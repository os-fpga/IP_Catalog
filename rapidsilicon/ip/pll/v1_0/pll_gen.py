#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from litex_wrapper.pll_litex_wrapper import PLL

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform



# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios():
    return [
        ("PLL_EN",          0, Pins(1)),
        ("CLK_IN",          0, Pins(1)),
        ("CLK_OUT",         0, Pins(1)),
        ("CLK_OUT_DIV2",    0, Pins(1)),
        ("CLK_OUT_DIV3",    0, Pins(1)),
        ("CLK_OUT_DIV4",    0, Pins(1)),
        ("SERDES_FAST_CLK", 0, Pins(1)),
        ("LOCK",            0, Pins(1)),
            ]

# AXI RAM Wrapper ----------------------------------------------------------------------------------
class PLLWrapper(Module):
    def __init__(self, platform, divide_clk_in_by_2, fast_clk_freq, ref_clk_freq, pll_post_div):

        self.clock_domains.cd_sys  = ClockDomain()

        # AXI-RAM ----------------------------------------------------------------------------------
        self.submodules.pll = pll = PLL(platform,
            divide_clk_in_by_2  =   divide_clk_in_by_2, 
            fast_clk_freq       =   fast_clk_freq,
            ref_clk_freq        =   ref_clk_freq,
            pll_post_div        =   pll_post_div,
            )

        platform.add_extension(get_clkin_ios())
        self.comb += pll.PLL_EN.eq(platform.request("PLL_EN"))
        self.comb += pll.CLK_IN.eq(platform.request("CLK_IN"))

        self.comb += platform.request("CLK_OUT").eq(pll.CLK_OUT)
        self.comb += platform.request("CLK_OUT_DIV2").eq(pll.CLK_OUT_DIV2)
        self.comb += platform.request("CLK_OUT_DIV3").eq(pll.CLK_OUT_DIV3)
        self.comb += platform.request("CLK_OUT_DIV4").eq(pll.CLK_OUT_DIV4)
        self.comb += platform.request("SERDES_FAST_CLK").eq(pll.SERDES_FAST_CLK)
        self.comb += platform.request("LOCK").eq(pll.LOCK)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="PLL CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="pll", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    

    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--pll_post_div",    type=int,   default= 2,     choices=[2,4,6,8,10,12,14,16,18,20,24,28,30,32,36,40,42,48,50,56,60,70,72,84,98],   help="CLock divided by 1")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--fast_clk_freq",     type=int,   default=1600,     choices=range(800,3201),     help="Freq in MHz")
    core_range_param_group.add_argument("--ref_clk_freq",       type=int,   default=50,      choices=range(5, 1201),     help="Freq in MHz")
    
    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--divide_clk_in_by_2",    type=bool,   default=False,    help="Divide input clock by 2")


    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="pll_wrapper",          help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {"IP details": {
    'Name' : 'PLL',
    'Version' : 'v1_0',
    'Interface' : 'Native',
    'Description' : "PLL IP core is a key component in chip design, used to generate stable clock signals from an input reference clock. Its essential for precise synchronization and clock management in modern integrated circuits, ensuring reliable performance across various applications."}}


    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")


#    if (args.id_en == False):
#        dep_dict.update({
#            'id_width' :   'True',
#        })
#    else:
#        dep_dict.update({
#            'id_width' :   'False',
#        })
#    if (args.dest_en == False):
#        dep_dict.update({
#            'dest_width' :   'True',
#        })
#    else:
#        dep_dict.update({
#            'dest_width' :   'False',
#        })
#    if (args.user_en == False):
#        dep_dict.update({
#            'user_width' :   'True',
#        })
#    else:
#        dep_dict.update({
#            'user_width' :   'False',
#        })        
#

    summary =  { 
    "Fast clock frequency selected": args.fast_clk_freq,
    "Input reference clock frequency": args.ref_clk_freq,
  }
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)


    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = PLLWrapper(platform,
              divide_clk_in_by_2=args.divide_clk_in_by_2,
              fast_clk_freq=args.fast_clk_freq,
              ref_clk_freq=args.ref_clk_freq,
              pll_post_div =args.pll_post_div)

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v1_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl(version    = "v1_0")
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
            version = "v1_0"
        )

if __name__ == "__main__":
    main()
