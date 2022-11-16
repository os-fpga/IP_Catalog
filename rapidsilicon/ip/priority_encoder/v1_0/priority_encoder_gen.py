#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse
import math

from litex_wrapper.priority_encoder_litex_wrapper import PRIORITYENCODER

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1))
    ]

def get_other_ios(width):
        return [
            ("input_unencoded",  0, Pins(width)), 
            ("output_valid",     0, Pins(1)), 
            ("output_encoded",   0, Pins(math.ceil(math.log2(width)))), 
            ("output_unencoded", 0, Pins(width)), 
        ]

# PRIORITY_ENCODER Wrapper ----------------------------------------------------------------------------------
class PRIORITYENCODERWrapper(Module):
    def __init__(self, platform, width, lsb_high_priority):
        
        self.clock_domains.cd_sys  = ClockDomain()
        
        # PRIORITY_ENCODER ----------------------------------------------------------------------------------
        self.submodules.priority_encoder = priority_encoder = PRIORITYENCODER(platform,
            width               = width,
            lsb_high_priority   = lsb_high_priority
            )
        
        # IOS 
        platform.add_extension(get_other_ios(width))
        self.comb += priority_encoder.input_unencoded.eq(platform.request("input_unencoded"))
        self.comb += platform.request("output_valid").eq(priority_encoder.output_valid)
        self.comb += platform.request("output_encoded").eq(priority_encoder.output_encoded)
        self.comb += platform.request("output_unencoded").eq(priority_encoder.output_unencoded)
        

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="PRIORITY_ENCODER")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

   # Parameter Dependency dictionary

    #                Ports     :    Dependency
    dep_dict = {}            


    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="priority_encoder", language="verilog")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--lsb_high_priority", type=bool, default=False,   help="LSB High Priority.")


    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--width",              type=int,  default=4, choices=range(2,9), help="Width.")\


    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="priority_encoder_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = PRIORITYENCODERWrapper(platform,
        width             = args.width,
        lsb_high_priority = args.lsb_high_priority,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = IP_Builder(device="gemini", ip_name="priority_encoder", language="verilog")
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
