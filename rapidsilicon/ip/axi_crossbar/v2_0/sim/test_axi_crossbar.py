"""

Copyright (c) 2020 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import itertools
import logging
import os
import random
import subprocess

import cocotb_test.simulator
import pytest

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.regression import TestFactory

from cocotbext.axi import AxiBus, AxiMaster, AxiRam

class TB(object):
    def __init__(self, dut):
        self.dut = dut
        
        s_count = 4
        m_count = 4

        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        cocotb.start_soon(Clock(dut.s0_axi_aclk, 5, units="ns").start())
        cocotb.start_soon(Clock(dut.s1_axi_aclk, 5, units="ns").start())
        cocotb.start_soon(Clock(dut.s2_axi_aclk, 5, units="ns").start())
        cocotb.start_soon(Clock(dut.s3_axi_aclk, 5, units="ns").start())
        cocotb.start_soon(Clock(dut.m0_axi_aclk, 9, units="ns").start())
        cocotb.start_soon(Clock(dut.m1_axi_aclk, 9, units="ns").start())
        cocotb.start_soon(Clock(dut.m2_axi_aclk, 9, units="ns").start())
        cocotb.start_soon(Clock(dut.m3_axi_aclk, 9, units="ns").start())
        cocotb.start_soon(Clock(dut.ACLK, 5, units="ns").start())

        self.axi_master = [AxiMaster(AxiBus.from_prefix(dut, f"s0{k}_axi"), dut.s0_axi_aclk, dut.s0_axi_areset) for k in range(s_count)]
        self.axi_ram = [AxiRam(AxiBus.from_prefix(dut, f"m0{k}_axi"), dut.m0_axi_aclk, dut.m0_axi_areset, size=2**16)for k in range(m_count)]
        
        #self.axi_master = [AxiMaster(AxiBus.from_prefix(dut, f"s0{k}_axi"), dut.clk, dut.rst) for k in range(s_count)]
        #self.axi_ram = [AxiRam(AxiBus.from_prefix(dut, f"m0{k}_axi"), dut.clk, dut.rst, size=2**16)for k in range(m_count)]
        
        for ram in self.axi_ram:
            # prevent X propagation from screwing things up - "anything but X!"
            # (X on bid and rid can propagate X to ready/valid)
            ram.write_if.b_channel.bus.bid.setimmediatevalue(0)
            ram.read_if.r_channel.bus.rid.setimmediatevalue(0)

    def set_idle_generator(self, generator=None):
        if generator:
            for master in self.axi_master:
                master.write_if.aw_channel.set_pause_generator(generator())
                master.write_if.w_channel.set_pause_generator(generator())
                master.read_if.ar_channel.set_pause_generator(generator())
            for ram in self.axi_ram:
                ram.write_if.b_channel.set_pause_generator(generator())
                ram.read_if.r_channel.set_pause_generator(generator())

    def set_backpressure_generator(self, generator=None):
        if generator:
            for master in self.axi_master:
                master.write_if.b_channel.set_pause_generator(generator())
                master.read_if.r_channel.set_pause_generator(generator())
            for ram in self.axi_ram:
                ram.write_if.aw_channel.set_pause_generator(generator())
                ram.write_if.w_channel.set_pause_generator(generator())
                ram.read_if.ar_channel.set_pause_generator(generator())

    async def cycle_reset(self):    
        self.dut.s0_axi_areset.value = 1
        self.dut.s1_axi_areset.value = 1
        self.dut.s2_axi_areset.value = 1
        self.dut.s3_axi_areset.value = 1
        self.dut.m0_axi_areset.value = 1
        self.dut.m1_axi_areset.value = 1
        self.dut.m2_axi_areset.value = 1
        self.dut.m3_axi_areset.value = 1
        self.dut.ARESET.value = 1
        await RisingEdge(self.dut.s0_axi_aclk)
        await RisingEdge(self.dut.s1_axi_aclk)
        await RisingEdge(self.dut.m0_axi_aclk)
        await RisingEdge(self.dut.m1_axi_aclk)

        self.dut.s0_axi_areset.value = 0
        self.dut.s1_axi_areset.value = 0
        self.dut.s2_axi_areset.value = 0
        self.dut.s3_axi_areset.value = 0
        self.dut.m0_axi_areset.value = 0
        self.dut.m1_axi_areset.value = 0
        self.dut.m2_axi_areset.value = 0
        self.dut.m3_axi_areset.value = 0
        self.dut.ARESET.value = 0
        await RisingEdge(self.dut.s0_axi_aclk)
        await RisingEdge(self.dut.s1_axi_aclk)
        await RisingEdge(self.dut.m0_axi_aclk)
        await RisingEdge(self.dut.m1_axi_aclk)
        
                                           
async def run_test_write(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None, s=0, m=0):

    tb = TB(dut)

    byte_lanes = tb.axi_master[s].write_if.byte_lanes
    max_burst_size = tb.axi_master[s].write_if.max_burst_size

    if size is None:
        size = max_burst_size

    await tb.cycle_reset()

    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    for length in list(range(1, byte_lanes*2))+[1024]:
        for offset in list(range(byte_lanes, byte_lanes*2))+list(range(4096-byte_lanes, 4096)):
            tb.log.info("length %d, offset %d, size %d", length, offset, size)
            ram_addr = offset+0x1000
            addr = ram_addr + m*0x1000000
            test_data = bytearray([x % 256 for x in range(length)])

            tb.axi_ram[m].write(ram_addr-128, b'\xaa'*(length+256))

            await tb.axi_master[s].write(addr, test_data, size=size)

            tb.log.debug("%s", tb.axi_ram[m].hexdump_str((ram_addr & ~0xf)-16, (((ram_addr & 0xf)+length-1) & ~0xf)+48))

            assert tb.axi_ram[m].read(ram_addr, length) == test_data
            assert tb.axi_ram[m].read(ram_addr-1, 1) == b'\xaa'
            assert tb.axi_ram[m].read(ram_addr+length, 1) == b'\xaa'

    await RisingEdge(dut.s0_axi_aclk)
    await RisingEdge(dut.s0_axi_aclk)

    
async def run_test_read(dut, data_in=None, idle_inserter=None, backpressure_inserter=None, size=None, s=0, m=0):

    tb = TB(dut)

    byte_lanes = tb.axi_master[s].write_if.byte_lanes
    max_burst_size = tb.axi_master[s].write_if.max_burst_size

    if size is None:
        size = max_burst_size

    await tb.cycle_reset()

    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    for length in list(range(1, byte_lanes*2))+[1024]:
        for offset in list(range(byte_lanes, byte_lanes*2))+list(range(4096-byte_lanes, 4096)):
            tb.log.info("length %d, offset %d, size %d", length, offset, size)
            ram_addr = offset+0x1000
            addr = ram_addr + m*0x1000000
            test_data = bytearray([x % 256 for x in range(length)])

            tb.axi_ram[m].write(ram_addr, test_data)

            data = await tb.axi_master[s].read(addr, length, size=size)

            assert data.data == test_data

    await RisingEdge(dut.s0_axi_aclk)
    await RisingEdge(dut.s0_axi_aclk) 

async def run_stress_test(dut, idle_inserter=None, backpressure_inserter=None):

    tb = TB(dut)

    await tb.cycle_reset()

    tb.set_idle_generator(idle_inserter)
    tb.set_backpressure_generator(backpressure_inserter)

    async def worker(master, offset, aperture, count=16):
        for k in range(count):
            m = random.randrange(len(tb.axi_ram))
            length = random.randint(1, min(512, aperture))
            addr = offset+random.randint(0, aperture-length) + m*0x1000000
            test_data = bytearray([x % 256 for x in range(length)])
            
            await Timer(random.randint(1, 100), 'ns')

            await master.write(addr, test_data)

            await Timer(random.randint(1, 100), 'ns')

            data = await master.read(addr, length)
            assert data.data == test_data

    workers = []



    for k in range(16):
        workers.append(cocotb.start_soon(worker(tb.axi_master[k % len(tb.axi_master)], k*0x1000, 0x1000, count=16)))

    while workers:
        await workers.pop(0).join()

    await RisingEdge(dut.s0_axi_aclk)
    await RisingEdge(dut.s0_axi_aclk)

def cycle_pause():
    return itertools.cycle([1, 1, 1, 0])


if cocotb.SIM_NAME:

    s_count = 4
    m_count = 4
 
    for test in [run_test_write, run_test_read]:

        factory = TestFactory(test)
        factory.add_option("idle_inserter", [None, cycle_pause])
        factory.add_option("backpressure_inserter", [None, cycle_pause])
        factory.add_option("s", range(min(s_count, 2)))
        factory.add_option("m", range(min(m_count, 2)))
        factory.generate_tests()

    factory = TestFactory(run_stress_test)
    factory.generate_tests()

