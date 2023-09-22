#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from litex_wrapper.boot_clock_litex_wrapper import BOOT_CLOCK

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1))
    ]

# IOs/Interfaces -----------------------------------------------------------------------------------

def get_other_ios():
    return [
        ("O",  0, Pins(1)),
    ]

# AXI RAM Wrapper ----------------------------------------------------------------------------------
class BOOTCLOCKWrapper(Module):
    def __init__(self, platform, period):
        self.clock_domains.cd_sys  = ClockDomain()


        # Boot Clock ----------------------------------------------------------------------------------
        self.submodules.boot_clock = boot_clock = BOOT_CLOCK(platform, period = period
            )
        
        # Ports ---------------------------------------------------------------------------------
        platform.add_extension(get_other_ios())
        self.comb += platform.request("O").eq(boot_clock.O)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Boot CLock")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {'period' :   'True'}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="boot_clock", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--period",     type=int,   default=25,     choices=range(1,1000),     help="Clock period in ns")
    
 
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="boot_clock_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()


    details =  {"IP details": {
    'Name' : 'Boot Clock',
    'Version' : 'V1_0',
    'Interface' : 'Native',
    'Description' : 'This is an oscillator IP.'}}


    summary =  { 
    "Frequency in MHz =": 40,
  }


    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict , summary=summary)
        rs_builder.import_ip_details_json(json_filename=args.json, build_dir=args.build_dir ,details=details)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = BOOTCLOCKWrapper(platform,
        period = args.period,
    )

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
