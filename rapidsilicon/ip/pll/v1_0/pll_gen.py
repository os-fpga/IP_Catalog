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
        ("CLK_OUT0_EN",     0, Pins(1)),
        ("CLK_OUT1_EN",     0, Pins(1)),
        ("CLK_OUT2_EN",     0, Pins(1)),
        ("CLK_OUT3_EN",     0, Pins(1)),
        ("CLK_OUT0",        0, Pins(1)),
        ("CLK_OUT1",        0, Pins(1)),
        ("CLK_OUT2",        0, Pins(1)),
        ("CLK_OUT3",        0, Pins(1)),
        ("GEARBOX_FAST_CLK",0, Pins(1)),
        ("LOCK",            0, Pins(1)),
            ]

# AXI RAM Wrapper ----------------------------------------------------------------------------------
class PLLWrapper(Module):
    def __init__(self, platform, divide_clk_in_by_2, pll_mult, pll_div, clk_out0_div, clk_out1_div, clk_out2_div, clk_out3_div):

        self.clock_domains.cd_sys  = ClockDomain()

        # AXI-RAM ----------------------------------------------------------------------------------
        self.submodules.pll = pll = PLL(platform,
            divide_clk_in_by_2  =   divide_clk_in_by_2, 
            pll_mult            =   pll_mult,
            pll_div             =   pll_div,
            clk_out0_div        =   clk_out0_div,
            clk_out1_div        =   clk_out1_div,
            clk_out2_div        =   clk_out2_div,
            clk_out3_div        =   clk_out3_div,
            )

        platform.add_extension(get_clkin_ios())
        self.comb += pll.PLL_EN.eq(platform.request("PLL_EN"))
        self.comb += pll.CLK_IN.eq(platform.request("CLK_IN"))
        self.comb += pll.CLK_OUT0_EN.eq(platform.request("CLK_OUT0_EN"))
        self.comb += pll.CLK_OUT1_EN.eq(platform.request("CLK_OUT1_EN"))
        self.comb += pll.CLK_OUT2_EN.eq(platform.request("CLK_OUT2_EN"))
        self.comb += pll.CLK_OUT3_EN.eq(platform.request("CLK_OUT3_EN"))

        self.comb += platform.request("CLK_OUT0").eq(pll.CLK_OUT0)
        self.comb += platform.request("CLK_OUT1").eq(pll.CLK_OUT1)
        self.comb += platform.request("CLK_OUT2").eq(pll.CLK_OUT2)
        self.comb += platform.request("CLK_OUT3").eq(pll.CLK_OUT3)
        self.comb += platform.request("GEARBOX_FAST_CLK").eq(pll.GEARBOX_FAST_CLK)
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
    core_fix_param_group.add_argument("--clk_out0_div",   type=int,   default=2,     choices=[2,3,4,5,6,7,8,10,12,16,20.24,32,40,48,64],    help="CLK_OUT0 divider value")
    core_fix_param_group.add_argument("--clk_out1_div",   type=int,   default=2,     choices=[2,3,4,5,6,7,8,10,12,16,20.24,32,40,48,64],    help="CLK_OUT1 divider value")
    core_fix_param_group.add_argument("--clk_out2_div",   type=int,   default=2,     choices=[2,3,4,5,6,7,8,10,12,16,20.24,32,40,48,64],    help="CLK_OUT2 divider value")
    core_fix_param_group.add_argument("--clk_out3_div",   type=int,   default=2,     choices=[2,3,4,5,6,7,8,10,12,16,20.24,32,40,48,64],    help="CLK_OUT3 divider value")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--pll_mult",     type=int,   default=16,     choices=range(16,1000),     help="RAM Address Width")
    core_range_param_group.add_argument("--pll_div",       type=int,   default=1,      choices=range(1, 63),     help="RAM ID Width")
    
    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--divide_clk_in_by_2",    type=bool,   default=False,    help="RAM Pipelined Output")

    # Core file path parameters.
    # core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    # core_file_path_group.add_argument("--file_path", type=argparse.FileType('r'), help="File Path for memory initialization file")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="pll_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = PLLWrapper(platform,
              divide_clk_in_by_2=args.divide_clk_in_by_2,
              pll_mult=args.pll_mult,
              pll_div=args.pll_div,
              clk_out0_div=args.clk_out0_div,
              clk_out1_div=args.clk_out1_div,
              clk_out2_div=args.clk_out2_div,
              clk_out3_div=args.clk_out3_div)

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
