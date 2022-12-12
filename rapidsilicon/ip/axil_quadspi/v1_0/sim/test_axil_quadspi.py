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

# AXISimSoC ----------------------------------------------------------------------------------------

class AXISimSoC(SoCCore):
    def __init__(self):
        # Parameters.
        sys_clk_freq = int(100e6)

        # Platform.
        platform     = Platform()
        self.comb += platform.trace.eq(1)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request("sys_clk"))

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, bus_standard="axi-lite", uart_name="sim", integrated_rom_size=0x10000)
        self.add_config("BIOS_NO_BOOT")

        # AXIL-SPI Core generation/integration -----------------------------------------------------

        axil_quadspi = AXILiteInterface(data_width=32, address_width=32)

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

            # AXI-Lite.
            # ---------
            # AW.
            i_bus_awvalid = axil_quadspi.aw.valid,
            o_bus_awready = axil_quadspi.aw.ready,
            i_bus_awaddr  = axil_quadspi.aw.addr,
            i_bus_awprot  = axil_quadspi.aw.prot,
            # W.
            i_bus_wvalid  = axil_quadspi.w.valid,
            o_bus_wready  = axil_quadspi.w.ready,
            i_bus_wdata   = axil_quadspi.w.data,
            i_bus_wstrb   = axil_quadspi.w.strb,
            # B
            o_bus_bvalid  = axil_quadspi.b.valid,
            i_bus_bready  = axil_quadspi.b.ready,
            o_bus_bresp   = axil_quadspi.b.resp,
            # AR.
            i_bus_arvalid = axil_quadspi.ar.valid,
            o_bus_arready = axil_quadspi.ar.ready,
            i_bus_araddr  = axil_quadspi.ar.addr,
            i_bus_arprot  = axil_quadspi.ar.prot,
            # R.
            o_bus_rvalid  = axil_quadspi.r.valid,
            i_bus_rready  = axil_quadspi.r.ready,
            o_bus_rresp   = axil_quadspi.r.resp,
            o_bus_rdata   = axil_quadspi.r.data,

            # IOs.
            # ----
            o_spiflash4x_clk  = spiflash4x_clk,
            o_spiflash4x_cs_n = spiflash4x_cs_n,
            o_spiflash4x_dq   = spiflash4x_dq,
        )
        platform.add_source("../rapidsilicon/ip/axil_quadspi/v1_0/axil_quadspi/src/axil_quadspi.v")
        self.bus.add_slave("axil_quadspi", axil_quadspi, region=SoCRegion(origin=0x3000_000, size=0x1000))

        # Model Instance.
        platform.add_source("axil_quadspi_mem.init", copy=True)
        self.specials += Instance("spiflash",
            i_csb  = spiflash4x_cs_n,
            i_clk  = spiflash4x_clk,
            io_io0 = spiflash4x_dq[0],
            io_io1 = spiflash4x_dq[1],
            io_io2 = spiflash4x_dq[2],
            io_io3 = spiflash4x_dq[3],
        )
        platform.add_source("spiflash.v")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AXIL_QUADSPI  / LiteX simulation.")
    verilator_build_args(parser)
    args = parser.parse_args()
    verilator_build_kwargs = verilator_build_argdict(args)
    sim_config = SimConfig(default_clk="sys_clk")
    sim_config.add_module("serial2console", "serial")

    soc = AXISimSoC()
    builder = Builder(soc)
    builder.build(sim_config=sim_config, **verilator_build_kwargs)

if __name__ == "__main__":
    main()
