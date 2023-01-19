#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse
import math

from litex_wrapper.reset_release_litex_wrapper import RESETRELEASE

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1))
    ]

def get_other_ios(peripheral_aresetn, interconnects ,bus_reset,  peripheral_reset):
        return [    
            ("slow_clk",        0, Pins(1)), 
            ("ext_rst",         0, Pins(1)), 
            ("cpu_dbg_rst",     0, Pins(1)), 
            ("pll_lock",        0, Pins(1)), 

            ("cpu_rst",             0, Pins(1)), 
            ("periph_aresetn",      0, Pins(peripheral_aresetn)), 
            ("interconnect_aresetn",0, Pins(interconnects)), 
            ("bus_reset",           0, Pins(bus_reset)), 
            ("periph_reset",        0, Pins(peripheral_reset)), 
        ]

# RESET_RELEASE Wrapper ----------------------------------------------------------------------------------
class RESETRELEASEWrapper(Module):
    def __init__(self, platform, ext_reset_width, interconnects, bus_reset, peripheral_reset,peripheral_aresetn):
        
        self.clock_domains.cd_sys  = ClockDomain()
        
        # RESET_RELEASE ----------------------------------------------------------------------------------
        self.submodules.reset_release = reset_release = RESETRELEASE(platform,
            EXT_RESET_WIDTH     = ext_reset_width,
            INTERCONNECTS       = interconnects,
            BUS_RESET           = bus_reset,
            PERIPHERAL_RESET    = peripheral_reset,
            PERIPHERAL_ARESETN  = peripheral_aresetn,
            )
        
        # IOS 
        platform.add_extension(get_other_ios(peripheral_aresetn, interconnects ,bus_reset,  peripheral_reset))
        self.comb += reset_release.slow_clk.eq(platform.request("slow_clk"))
        self.comb += reset_release.ext_rst.eq(platform.request("ext_rst"))
        self.comb += reset_release.cpu_dbg_rst.eq(platform.request("cpu_dbg_rst"))
        self.comb += reset_release.pll_lock.eq(platform.request("pll_lock"))

        self.comb += platform.request("cpu_rst").eq(reset_release.cpu_rst)
        self.comb += platform.request("periph_aresetn").eq(reset_release.periph_aresetn)
        self.comb += platform.request("interconnect_aresetn").eq(reset_release.interconnect_aresetn)
        self.comb += platform.request("bus_reset").eq(reset_release.bus_reset)
        self.comb += platform.request("periph_reset").eq(reset_release.periph_reset)
        

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="RESET_RELEASE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="reset_release", language="verilog")

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--ext_reset_width",          type=int,    default=5,     choices=[4,5,6,7,8,9,10],           help="External reset window.")
    core_fix_param_group.add_argument("--peripheral_aresetn",       type=int,    default=1,     choices=[1,2,3,4,5,6,7,8,9,10],     help="Number of peripheral resets N.")
    core_fix_param_group.add_argument("--interconnects",            type=int,    default=1,     choices=[1,2,3,4,5,6,7,8,9,10],     help="Number of Interconnects.")
    core_fix_param_group.add_argument("--bus_reset",                type=int,    default=1,     choices=[1,2,3,4,5,6,7,8,9,10],     help="Number of bus reserts.")
    core_fix_param_group.add_argument("--peripheral_reset",         type=int,    default=1,     choices=[1,2,3,4,5,6,7,8,9,10],     help="Number of peripheral resets.")


    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="reset_release_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = RESETRELEASEWrapper(platform,
        ext_reset_width     = args.ext_reset_width,
        interconnects       = args.interconnects,
        bus_reset           = args.bus_reset,
        peripheral_reset    = args.peripheral_reset,
        peripheral_aresetn  = args.peripheral_aresetn,   )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v1_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
