#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
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

        axil_spi = AXILiteInterface(data_width=32, address_width=32)

        # Generate Core.
        os.system("cd .. && ./axil_spi_gen.py --core_module=S25FL128L --core_mode=x4 --core_phy=model --build")

        # Core Instance.
        self.specials += Instance("axil_spi",
            # Clk / Rst.
            # ----------
            i_clk         = ClockSignal("sys"),
            i_rst         = ResetSignal("sys"),

            # AXI-Lite.
            # ---------
            # AW.
            i_bus_awvalid = axil_spi.aw.valid,
            o_bus_awready = axil_spi.aw.ready,
            i_bus_awaddr  = axil_spi.aw.addr,
            i_bus_awprot  = axil_spi.aw.prot,
            # W.
            i_bus_wvalid  = axil_spi.w.valid,
            o_bus_wready  = axil_spi.w.ready,
            i_bus_wdata   = axil_spi.w.data,
            i_bus_wstrb   = axil_spi.w.strb,
            # B
            o_bus_bvalid  = axil_spi.b.valid,
            i_bus_bready  = axil_spi.b.ready,
            o_bus_bresp   = axil_spi.b.resp,
            # AR.
            i_bus_arvalid = axil_spi.ar.valid,
            o_bus_arready = axil_spi.ar.ready,
            i_bus_araddr  = axil_spi.ar.addr,
            i_bus_arprot  = axil_spi.ar.prot,
            # R.
            o_bus_rvalid  = axil_spi.r.valid,
            i_bus_rready  = axil_spi.r.ready,
            o_bus_rresp   = axil_spi.r.resp,
            o_bus_rdata   = axil_spi.r.data,

            # IOs.
            # ----
            # No IOs since using integrated model.
        )
        platform.add_source("../rapidsilicon/ip/axil_spi/v1_0/axil_spi/src/axil_spi.v")
        platform.add_source("axil_spi_mem.init", copy=True)
        self.bus.add_slave("axil_spi", axil_spi, region=SoCRegion(origin=0x3000_000, size=0x1000))

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AXIL_SPI  / LiteX simulation.")
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
