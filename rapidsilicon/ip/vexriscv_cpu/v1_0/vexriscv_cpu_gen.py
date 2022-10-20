#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT.

import os
import json
import argparse
import shutil

from litex_sim.vexriscv_cpu_litex_wrapper import VexRiscv

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1))]

def get_jtag_ios():
    return [
                
            ("jtag_tms",    0,  Pins(1)),
            ("jtag_tdi",    0,  Pins(1)),
            ("jtag_tdo",    0,  Pins(1)),
            ("jtag_tck",    0,  Pins(1)),    
            ]

def get_other_ios():
    return [
            ("timerInterrupt",      0,  Pins(1)),
            ("externalInterrupt",   0,  Pins(1)),    
            ("softwareInterrupt",   0,  Pins(1)),    
            ("debugReset",          0,  Pins(1)),
            ("debug_resetOut",      0,  Pins(1)),
        ]

# AXI-VEXRISCV Wrapper --------------------------------------------------------------------------------
class VexriscvWrapper(Module):
    def __init__(self, platform):
        
        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        #IBUS
        ibus_axi = AXIInterface(data_width = 32, address_width = 32, id_width = 8)
        platform.add_extension(ibus_axi.get_ios("ibus_axi"))
        self.comb += ibus_axi.connect_to_pads(platform.request("ibus_axi"), mode="master")

        #IBUS
        dbus_axi = AXIInterface(data_width = 32, address_width = 32, id_width = 8)
        platform.add_extension(dbus_axi.get_ios("dbus_axi"))
        self.comb += dbus_axi.connect_to_pads(platform.request("dbus_axi"), mode="master")

        # VEXRISCV
        self.submodules.vexriscv = vexriscv = VexRiscv(platform,
            ibus        = ibus_axi,
            dbus        = dbus_axi
            )

        platform.add_extension(get_jtag_ios())
        # Inputs
        self.comb += vexriscv.jtag_tms.eq(platform.request("jtag_tms"))
        self.comb += vexriscv.jtag_tdi.eq(platform.request("jtag_tdi"))
        self.comb += vexriscv.jtag_tck.eq(platform.request("jtag_tck"))

        # Outputs
        self.comb += platform.request("jtag_tdo").eq(vexriscv.jtag_tdo)

        platform.add_extension(get_other_ios())
        # Inputs
        self.comb += vexriscv.timerInterrupt.eq(platform.request("timerInterrupt"))
        self.comb += vexriscv.externalInterrupt.eq(platform.request("externalInterrupt"))
        self.comb += vexriscv.softwareInterrupt.eq(platform.request("softwareInterrupt"))
        self.comb += vexriscv.debugReset.eq(platform.request("debugReset"))

        # Outputs
        self.comb += platform.request("debug_resetOut").eq(vexriscv.debug_resetOut)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Vexriscv CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="vexriscv_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        with open(args.json, 'rt') as f:
            t_args = argparse.Namespace()
            t_args.__dict__.update(json.load(f))
            args = parser.parse_args(namespace=t_args)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        print(json.dumps(vars(args), indent=4))

    # Remove build extension when specified.
    args.build_name = os.path.splitext(args.build_name)[0]

    # Build Project Directory ----------------------------------------------------------------------

    import sys
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")  # FIXME
    sys.path.append(common_path)                                       # FIXME
    from common import RapidSiliconIPCatalogBuilder
    rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="vexriscv_cpu")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module = VexriscvWrapper(platform)
    
    # Build
    if args.build:
        rs_builder.generate_verilog(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
