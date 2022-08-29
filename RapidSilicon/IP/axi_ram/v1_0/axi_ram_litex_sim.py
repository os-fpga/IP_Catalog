#!/usr/bin/env python3

#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

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

from axi_ram_litex_wrapper import AXIRAM

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

        # AXI Tests --------------------------------------------------------------------------------
        def axi_syntax_test():
            from verilog_axi.axi.axi_ram import AXIRAM
            s_axi = AXIInterface(data_width=32, address_width=32, id_width=8)
            self.submodules.axi_ram = AXIRAM(platform, s_axi, size=0x1000)

        def axi_integration_test():
            # AXI Test Mapping.
            # -----------------
            axi_map = {
                "axi_ram" : 0x010000,
            }

            # Add AXI RAM to SoC.
            # -------------------

            # Test from LiteX BIOS:
            # mem_list
            # mem_write <AXI_RAM_BASE> 0x5aa55aa5
            # mem_read  <AXI_RAM_BASE> 32

            # 1) Create AXI interface and connect it to SoC.
            s_axi = AXIInterface(data_width=32, address_width=32, id_width=1)
            self.bus.add_slave("axi_ram", s_axi, region=SoCRegion(origin=axi_map["axi_ram"], size=0x1000))
            # 2) Add AXIRAM.
            self.submodules += AXIRAM(platform, s_axi, size=0x1000)
            # 3) Debug.
            if 0:
                self.submodules += AXIAWDebug(s_axi, name="AXIRAM")
                self.submodules += AXIWDebug(s_axi,  name="AXIRAM")
                self.submodules += AXIARDebug(s_axi, name="AXIRAM")
                self.submodules += AXIRDebug(s_axi,  name="AXIRAM")

        axi_syntax_test()
        axi_integration_test()

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AXIRAM test simulation SoC ")
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
