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
    def __init__(self, platform, divided_clks, divide_clk_in_by_2, fast_clk_freq, ref_clk_freq, clk_out0_div, clk_out1_div, clk_out2_div, clk_out3_div):

        self.clock_domains.cd_sys  = ClockDomain()

        # AXI-RAM ----------------------------------------------------------------------------------
        self.submodules.pll = pll = PLL(platform,
            divided_clks        =   divided_clks,
            divide_clk_in_by_2  =   divide_clk_in_by_2, 
            fast_clk_freq       =   fast_clk_freq,
            ref_clk_freq        =   ref_clk_freq,
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
    core_fix_param_group.add_argument("--divided_clks",   type=int,   default=4,     choices=[1,2,3,4],                                     help="Divided clocks to be generated from fast clock")
    core_fix_param_group.add_argument("--clk_out0_div",   type=int,   default=2,     choices=[2,3,4,5,6,7,8,10,12,16,20,24,32,40,48,64],    help="CLK_OUT0 divider value")
    core_fix_param_group.add_argument("--clk_out1_div",   type=int,   default=2,     choices=[2,3,4,5,6,7,8,10,12,16,20,24,32,40,48,64],    help="CLK_OUT1 divider value")
    core_fix_param_group.add_argument("--clk_out2_div",   type=int,   default=2,     choices=[2,3,4,5,6,7,8,10,12,16,20,24,32,40,48,64],    help="CLK_OUT2 divider value")
    core_fix_param_group.add_argument("--clk_out3_div",   type=int,   default=2,     choices=[2,3,4,5,6,7,8,10,12,16,20,24,32,40,48,64],    help="CLK_OUT3 divider value")

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
    'Version' : 'V1_0',
    'Interface' : 'Native',
    'Description' : "PLL IP core is a key component in chip design, used to generate stable clock signals from an input reference clock. Its essential for precise synchronization and clock management in modern integrated circuits, ensuring reliable performance across various applications."}}


    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        


    if (args.divided_clks == 3):
        option_strings_to_remove = ['--clk_out3_div']
        parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
    elif(args.divided_clks == 2):
        option_strings_to_remove = ['--clk_out3_div']
        parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        option_strings_to_remove = ['--clk_out2_div']
        parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
    elif(args.divided_clks == 1):
        option_strings_to_remove = ['--clk_out3_div']
        parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        option_strings_to_remove = ['--clk_out2_div']
        parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        option_strings_to_remove = ['--clk_out1_div']
        parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]



    summary =  { 
    "Number of divided clocks ": args.divided_clks,
    "Fast clock frequency selected": args.fast_clk_freq,
    "Input reference clock frequency": args.ref_clk_freq,
  }
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")


    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = PLLWrapper(platform,
              divide_clk_in_by_2=args.divide_clk_in_by_2,
              divided_clks=args.divided_clks,
              fast_clk_freq=args.fast_clk_freq,
              ref_clk_freq=args.ref_clk_freq,
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
