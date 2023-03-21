from typing import List, Tuple

import cocotb # type: ignore
from cocotb.clock import Clock # type: ignore
from cocotb.regression import TestFactory # type: ignore
from cocotb.handle import SimHandle # type: ignore
from cocotb.log import SimLog # type: ignore
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly, ReadWrite, Timer # type: ignore
from cocotb_AHB.AHB_common.AHB_types import *
from cocotb_AHB.AHB_common.SubordinateInterface import SubordinateInterface
from cocotb_AHB.AHB_common.MonitorInterface import MonitorInterface
from cocotb_AHB.drivers.SimDefaultSubordinate import SimDefaultSubordinate

from cocotb_AHB.monitors.AHBSignalMonitor import AHBSignalMonitor
from cocotb_AHB.monitors.AHBPacketMonitor import AHBPacketMonitor

CLK_PERIOD = (10, "ns")

async def setup_dut(dut: SimHandle) -> None:
    cocotb.fork(Clock(dut.s_ahb_aclk, *CLK_PERIOD).start())
    dut.s_ahb_aresetn.value = 1
    await ClockCycles(dut.s_ahb_aclk, 10)
    await RisingEdge(dut.s_ahb_aclk)
    await Timer(1, units='ns')
    dut.s_ahb_aresetn.value = 0
    await ClockCycles(dut.s_ahb_aclk, 1)


# async def reset_AHB(dut: SimHandle,
#                     subordinates: List[SubordinateInterface]) -> None:
#     for subordinate in subordinates:
#         subordinate.set_ready(HREADY.WaitState)
#         subordinate.put_cmd(ICMD())
#     await ReadOnly()
#     while dut.rstn.value == 0:
#         await RisingEdge(dut.clk)
#         await ReadWrite()
#         for subordinate in subordinates:
#             subordinate.put_cmd(ICMD())


# async def test_incorrect_args(dut: SimHandle, length: int, bus_width: int) -> None:
#     if length > 0 and length % 1024 == 0 and bus_width in [8*2**i for i in range(8)]:
#         return
#     log = SimLog("cocotb.test_incorrect")
#     try:
#         subordinate = SimDefaultSubordinate(length, bus_width)
#     except Exception as e:
#         log.info(e)
#         return
#     print(locals())
#     assert False


# async def test_incorrect(dut: SimHandle, length: int, bus_width: int, sel: HSEL,
#                          commands: List[Tuple[int, HSIZE, HTRANS]]) -> None:
#     log = SimLog("cocotb.test_incorrect")
#     try:
#         subordinate = SimDefaultSubordinate(length, bus_width)
#     except Exception as e:
#         log.info(e)
#         return
#     try:
#         subordinate.register_clock(dut.clk)
#         subordinate.register_reset(dut.rstn, True)
#         subordinate.set_ready(HREADY.Working)
#         cocotb.fork(setup_dut(dut))
#         cocotb.fork(subordinate.start())

#         await reset_AHB(dut, [subordinate])
#         risingedge = RisingEdge(dut.clk)
#         for command in commands:
#             subordinate.set_ready(HREADY.Working)
#             subordinate.put_cmd(ICMD(command[0], HBURST.Single, HMASTLOCK.Locked, HPROT(0),
#                                      command[1], HNONSEC.Secure, HEXCL.NonExcl, 0, command[2],
#                                      0xf, HWRITE.Write, sel))
#             await risingedge
#             subordinate.put_data(IDATA(0x12345678))
#             rdata, readyout, resp, exokay = subordinate.get_rsp()
#             while readyout == HREADYOUT.NotReady:
#                 subordinate.set_ready(HREADY.WaitState)
#                 subordinate.put_cmd(ICMD(0x0, HBURST.Single, HMASTLOCK.Locked, HPROT(0),
#                                          HSIZE.Word, HNONSEC.Secure, HEXCL.NonExcl, 0, HTRANS.Idle,
#                                          0xf, HWRITE.Write, sel))
#                 await risingedge
#                 rdata, readyout, resp, exokay = subordinate.get_rsp()
#     except Exception as e:
#         await RisingEdge(dut.clk)
#         log.info(e)
#         return
#     assert False


# async def test_answer(dut: SimHandle, length: int,
#                       bus_width: int, instruction_sequences: List[Tuple[(int, HTRANS)]]) -> None:
#     subordinate = SimDefaultSubordinate(length, bus_width)
#     subordinate.register_clock(dut.clk)
#     subordinate.register_reset(dut.rstn, True)
#     subordinate.set_ready(HREADY.Working)
#     cocotb.fork(setup_dut(dut))
#     cocotb.fork(subordinate.start())
#     await reset_AHB(dut, [subordinate])
#     risingedge = RisingEdge(dut.clk)
#     for addr, i in instruction_sequences:
#         subordinate.set_ready(HREADY.Working)
#         subordinate.put_cmd(ICMD(addr, HBURST.Single, HMASTLOCK.Locked, HPROT(0),
#                                  HSIZE.Byte, HNONSEC.Secure, HEXCL.NonExcl, 0, i,
#                                  0x0, HWRITE.Write, HSEL.Sel))
#         await risingedge
#         subordinate.put_data(IDATA(0x0))
#         rsp = subordinate.get_rsp()
#         if i in [HTRANS.Idle, HTRANS.Busy]:
#             assert rsp.hResp == HRESP.Successful
#         else:
#             assert rsp.hResp == HRESP.Failed
#             subordinate.set_ready(HREADY.WaitState)
#             subordinate.put_cmd(ICMD(0x0, HBURST.Single, HMASTLOCK.Locked, HPROT(0),
#                                      HSIZE.Word, HNONSEC.Secure, HEXCL.NonExcl, 0, HTRANS.Idle,
#                                      0xf, HWRITE.Write, HSEL.Sel))
#             await risingedge
#             subordinate.put_data(IDATA(0x12345678))
#             rsp = subordinate.get_rsp()
#             assert rsp.hReadyOut == HREADYOUT.Ready
#             assert rsp.hResp == HRESP.Failed
#     subordinate.set_ready(HREADY.Working)
#     await risingedge


# should_fail = TestFactory(test_incorrect_args)
# should_fail.add_option('length', (0, 4095, 1023, 1024, 4096))
# should_fail.add_option('bus_width', (1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128))
# should_fail.generate_tests()


# should_fail = TestFactory(test_incorrect)
# should_fail.add_option('length', (1024,))
# should_fail.add_option('bus_width', (32,))
# should_fail.add_option('sel', (HSEL.Sel, ))
# should_fail.add_option('commands', ([(0x201, HSIZE.Halfword, HTRANS.Idle)],
#                                     [(0x201, HSIZE.Halfword, HTRANS.Busy)],
#                                     [(0x201, HSIZE.Halfword, HTRANS.Seq)],
#                                     [(0x201, HSIZE.Halfword, HTRANS.NonSeq)],
#                                     [(0x201, HSIZE.Word, HTRANS.Idle)],
#                                     [(0x201, HSIZE.Word, HTRANS.Busy)],
#                                     [(0x201, HSIZE.Word, HTRANS.Seq)],
#                                     [(0x201, HSIZE.Word, HTRANS.NonSeq)],
#                                     [(0x200, HSIZE.Doubleword, HTRANS.Idle)],
#                                     [(0x200, HSIZE.Doubleword, HTRANS.Busy)],
#                                     [(0x200, HSIZE.Doubleword, HTRANS.Seq)],
#                                     [(0x200, HSIZE.Doubleword, HTRANS.NonSeq)],

# ))
# should_fail.generate_tests()

# check_resp = TestFactory(test_answer)
# check_resp.add_option('length', (0x400,))
# check_resp.add_option('bus_width', (32,))
# # Simple Subordinate must treat IDLE and BUSY as IDLE and NonSeq and Seq as NonSeq
# check_resp.add_option('instruction_sequences', ([(0x200, HTRANS.Idle)],
#                                                 [(0x200, HTRANS.Busy)],
#                                                 [(0x200, HTRANS.NonSeq)],
#                                                 [(0x200, HTRANS.Seq)],
#                                                 [(0x200, HTRANS.NonSeq), (0x200, HTRANS.Seq)],
#                                                 [(0x200, HTRANS.NonSeq), (0x200, HTRANS.Busy)],
#                                                 [(0x200, HTRANS.NonSeq), (0x200, HTRANS.Busy), (0x200, HTRANS.NonSeq)],
#                                                 [(0x200, HTRANS.NonSeq), (0x200, HTRANS.Busy), (0x200, HTRANS.Seq)],
#                                                 [(0x200, HTRANS.NonSeq), (0x200, HTRANS.Busy), (0x200, HTRANS.Idle)],
#                                                 [(0x200, HTRANS.NonSeq), (0x200, HTRANS.NonSeq)],
#                                                 [(0x200, HTRANS.NonSeq), (0x200, HTRANS.NonSeq)],
#                                                 [(0x200, HTRANS.NonSeq), (0x200, HTRANS.Idle), (0x200, HTRANS.NonSeq)]))
# check_resp.generate_tests()
