#!/usr/bin/env python3

import argparse

from migen import *

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform
from litex.build.sim.config import SimConfig
from litex.build.sim.verilator import verilator_build_args, verilator_build_argdict

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from dsp_gen import RS_DSP

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("sys_clk", 0, Pins(1)),
    ("sys_rst", 0, Pins(1)),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(SimPlatform):
    name = "sim"
    def __init__(self):
        SimPlatform.__init__(self, "SIM", _io)

# DSPSimSoC ----------------------------------------------------------------------------------------

class DSPSimSoC(SoCMini):
    def __init__(self, firmware=None):
        # Parameters.
        sys_clk_freq = int(100e6)

        # Platform.
        platform = Platform()
        self.comb += platform.trace.eq(1)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request("sys_clk"))

        # SoCMini ----------------------------------------------------------------------------------
        SoCMini.__init__(self, platform, clk_freq=sys_clk_freq)

        # DSP --------------------------------------------------------------------------------------
        self.dsp = RS_DSP(config="RS_DSP_MULT", a_width=20, b_width=18, z_width=38)
        self.sync += self.dsp.a.eq(self.dsp.a + 1)
        self.sync += self.dsp.b.eq(2)
        self.sync += Display("Z: %x", self.dsp.z)

        platform.add_source("models/dsp_sim.v")

        # Finish -----------------------------------------------------------------------------------
        cycles = Signal(32)
        self.sync += cycles.eq(cycles + 1)
        self.sync += If(cycles == 100,
            Display("-"*80),
            Display("Cycles: %d", cycles),
            Finish(),
        )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="DSP Generator simulation.")
    verilator_build_args(parser)
    args = parser.parse_args()
    verilator_build_kwargs = verilator_build_argdict(args)
    sim_config = SimConfig(default_clk="sys_clk")

    mod = DSPSimSoC()
    builder = Builder(mod)
    builder.build(sim_config=sim_config, **verilator_build_kwargs)

if __name__ == "__main__":
    main()
