#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import argparse

from migen import *

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform
from litex.build.sim.config import SimConfig
from litex.build.sim.verilator import verilator_build_args, verilator_build_argdict

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.interconnect.axi import *

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("sys_clk", 0, Pins(1)),
    ("sys_rst", 0, Pins(1)),

    # Serial.
    ("serial", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),

        Subsignal("sink_valid", Pins(1)),
        Subsignal("sink_ready", Pins(1)),
        Subsignal("sink_data",  Pins(8)),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(SimPlatform):
    name = "sim"
    def __init__(self):
        SimPlatform.__init__(self, "SIM", _io)

# AXI Debug ----------------------------------------------------------------------------------------

class AXIAWDebug(Module):
    def __init__(self, axi, name=""):
        sync = getattr(self.sync, axi.clock_domain)
        sync += If(axi.aw.valid & axi.aw.ready,
            Display(f"AXI AW {name}: Addr: 0x%08x",
                axi.aw.addr
            ),
        )

class AXIWDebug(Module):
    def __init__(self, axi, name=""):
        sync = getattr(self.sync, axi.clock_domain)
        sync += If(axi.w.valid & axi.w.ready,
            Display(f"AXI W {name}: Data: 0x%x, Strb: %x",
                axi.w.data,
                axi.w.strb
            ),
        )

class AXIARDebug(Module):
    def __init__(self, axi, name=""):
        sync = getattr(self.sync, axi.clock_domain)
        sync += If(axi.ar.valid & axi.ar.ready,
            Display(f"AXI AR {name}: Addr: 0x%08x",
                axi.ar.addr,
            ),
        )

class AXIRDebug(Module):
    def __init__(self, axi, name=""):
        sync = getattr(self.sync, axi.clock_domain)
        sync += If(axi.r.valid & axi.r.ready,
            Display(f"AXI R {name}: Data: 0x%x",
                axi.r.data,
            ),
        )

# SimSoC -------------------------------------------------------------------------------------------

class SimSoC(SoCCore):
    def __init__(self, firmware=None, spi_debug=False, axil_quadspi_master_debug=False):
        # Parameters.
        sys_clk_freq = int(100e6)

        # Platform.
        platform = Platform()
        platform.add_debug(self, reset=1)
        #self.comb += platform.trace.eq(1)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request("sys_clk"))

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, uart_name="sim",
            integrated_rom_size      = 0x10000,
            integrated_main_ram_size = 0x10000,
            integrated_main_ram_init = get_mem_data(firmware, endianness="little")
        )
        #self.add_config("BIOS_NO_PROMPT")
        self.add_config("BIOS_NO_DELAYS")
        self.add_constant("ROM_BOOT_ADDRESS", self.bus.regions["main_ram"].origin)

        # AXIL-SPI Core generation/integration -----------------------------------------------------

        axil_quadspi_mmap   = AXILiteInterface(data_width=32, address_width=32)
        axil_quadspi_master = AXILiteInterface(data_width=32, address_width=32)

        # Generate Core.
        os.system("cd .. && ./axil_quadspi_gen.py --core_module=S25FL128L --core_mode=x4 --build")

        # Core Instance.
        spiflash4x_clk  = Signal()
        spiflash4x_cs_n = Signal()
        spiflash4x_dq   = Signal(4)

        self.specials += Instance("axil_quadspi",
            # Clk / Rst.
            # ----------
            i_clk         = ClockSignal("sys"),
            i_rst         = ResetSignal("sys"),

            # AXI-Lite Master.
            # ----------------
            # AW.
            i_m_axi_awvalid = axil_quadspi_master.aw.valid,
            o_m_axi_awready = axil_quadspi_master.aw.ready,
            i_m_axi_awaddr  = axil_quadspi_master.aw.addr[:28],
            i_m_axi_awprot  = axil_quadspi_master.aw.prot,
            # W.
            i_m_axi_wvalid  = axil_quadspi_master.w.valid,
            o_m_axi_wready  = axil_quadspi_master.w.ready,
            i_m_axi_wdata   = axil_quadspi_master.w.data,
            i_m_axi_wstrb   = axil_quadspi_master.w.strb,
            # B
            o_m_axi_bvalid  = axil_quadspi_master.b.valid,
            i_m_axi_bready  = axil_quadspi_master.b.ready,
            o_m_axi_bresp   = axil_quadspi_master.b.resp,
            # AR.
            i_m_axi_arvalid = axil_quadspi_master.ar.valid,
            o_m_axi_arready = axil_quadspi_master.ar.ready,
            i_m_axi_araddr  = axil_quadspi_master.ar.addr[:28],
            i_m_axi_arprot  = axil_quadspi_master.ar.prot,
            # R.
            o_m_axi_rvalid  = axil_quadspi_master.r.valid,
            i_m_axi_rready  = axil_quadspi_master.r.ready,
            o_m_axi_rresp   = axil_quadspi_master.r.resp,
            o_m_axi_rdata   = axil_quadspi_master.r.data,

            # AXI-Lite MMAP.
            # --------------
            # AW.
            i_s_axi_awvalid = axil_quadspi_mmap.aw.valid,
            o_s_axi_awready = axil_quadspi_mmap.aw.ready,
            i_s_axi_awaddr  = axil_quadspi_mmap.aw.addr[:28],
            i_s_axi_awprot  = axil_quadspi_mmap.aw.prot,
            # W.
            i_s_axi_wvalid  = axil_quadspi_mmap.w.valid,
            o_s_axi_wready  = axil_quadspi_mmap.w.ready,
            i_s_axi_wdata   = axil_quadspi_mmap.w.data,
            i_s_axi_wstrb   = axil_quadspi_mmap.w.strb,
            # B
            o_s_axi_bvalid  = axil_quadspi_mmap.b.valid,
            i_s_axi_bready  = axil_quadspi_mmap.b.ready,
            o_s_axi_bresp   = axil_quadspi_mmap.b.resp,
            # AR.
            i_s_axi_arvalid = axil_quadspi_mmap.ar.valid,
            o_s_axi_arready = axil_quadspi_mmap.ar.ready,
            i_s_axi_araddr  = axil_quadspi_mmap.ar.addr[:28],
            i_s_axi_arprot  = axil_quadspi_mmap.ar.prot,
            # R.
            o_s_axi_rvalid  = axil_quadspi_mmap.r.valid,
            i_s_axi_rready  = axil_quadspi_mmap.r.ready,
            o_s_axi_rresp   = axil_quadspi_mmap.r.resp,
            o_s_axi_rdata   = axil_quadspi_mmap.r.data,

            # IOs.
            # ----
            o_spiflash4x_clk  = spiflash4x_clk,
            o_spiflash4x_cs_n = spiflash4x_cs_n,
            o_spiflash4x_dq   = spiflash4x_dq,
        )
        platform.add_source("../rapidsilicon/ip/axil_quadspi/v1_0/axil_quadspi/src/axil_quadspi.v")
        self.bus.add_slave("axil_quadspi_master", axil_quadspi_master, region=SoCRegion(origin=0x8100_0000, size=0x10000, cached=False))
        self.bus.add_slave("axil_quadspi_mmap",   axil_quadspi_mmap,   region=SoCRegion(origin=0x3000_0000, size=0x10000))

        # Model Instance.
        platform.add_source("axil_quadspi_mem.init", copy=True)
        self.specials += Instance("N25Q_sim",
            i_csb    = spiflash4x_cs_n,
            i_sclk   = spiflash4x_clk,
            io_mosi  = spiflash4x_dq[0],
            io_miso  = spiflash4x_dq[1],
            io_wp    = spiflash4x_dq[2],
            io_holdb = spiflash4x_dq[3],
        )
        # From https://raw.githubusercontent.com/BrooksEE/N25Q/master/sim/N25Q_sim.v and modified
        platform.add_source("N25Q_sim.v")

        # Debug.
        if spi_debug:
            clk  = Signal()
            mosi = Signal()
            miso = Signal()
            wp   = Signal()
            hold = Signal()
            self.comb += [
                clk.eq(  spiflash4x_clk),
                mosi.eq( spiflash4x_dq[0]),
                miso.eq( spiflash4x_dq[1]),
                wp.eq(   spiflash4x_dq[2]),
                hold.eq( spiflash4x_dq[3]),
            ]
            self.sync += If(~spiflash4x_cs_n,
                Display("clk: %d; dq0(mosi): %d; dq1(miso): %d, dq2(wp): %d, dq3(hold): %d",
                    clk,
                    mosi,
                    miso,
                    wp,
                    hold,
                )
            )
        if axil_quadspi_master_debug:
            self.submodules += AXIAWDebug(axil_quadspi_master, name="AXIL_QUADSPI_MASTER")
            self.submodules += AXIWDebug(axil_quadspi_master,  name="AXIL_QUADSPI_MASTER")
            self.submodules += AXIARDebug(axil_quadspi_master, name="AXIL_QUADSPI_MASTER")
            self.submodules += AXIRDebug(axil_quadspi_master,  name="AXIL_QUADSPI_MASTER")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AXIL_QUADSPI  / LiteX simulation.")
    verilator_build_args(parser)
    args = parser.parse_args()
    verilator_build_kwargs = verilator_build_argdict(args)
    sim_config = SimConfig(default_clk="sys_clk")
    sim_config.add_module("serial2console", "serial")

    for n in range(2):
        # Create SoC.
        soc = SimSoC(firmware={
            0 : None,           # First loop with no firmware (to generate SoC's software headers).
            1 : "firmware/firmware.bin" # Second loop with compiled firmware.
        }[n])
        builder = Builder(soc)
        # Build/Run SoC (run only on second loop).
        builder.build(sim_config=sim_config, **verilator_build_kwargs, run=n > 0)

        # Compile firmware on first loop.
        if (n == 0):
            os.system("cd firmware && make clean all")

if __name__ == "__main__":
    main()
