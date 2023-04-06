#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from litex_wrapper.on_chip_memory_litex_wrapper import *

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform


# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios(data_width, write_depth):
    return [
        ("clk",     0, Pins(1)),
        ("clk_A",   0, Pins(1)),
        ("clk_B",   0, Pins(1)),
        ("rst",     0, Pins(1)),
        
        ("addr_A",  0, Pins(math.ceil(math.log2(write_depth)))),
        ("addr_B",  0, Pins(math.ceil(math.log2(write_depth)))),
        
        ("din_A",   0, Pins(data_width)),
        ("din_B",   0, Pins(data_width)),
        
        ("dout_A",  0, Pins(data_width)),
        ("dout_B",  0, Pins(data_width)),
        
        ("wen_A",   0, Pins(1)),
        ("ren_A",   0, Pins(1)),
        
        ("wen_B",   0, Pins(1)),
        ("ren_B",   0, Pins(1))
    ]

# on_chip_memory Wrapper ----------------------------------------------------------------------------------
class OCMWrapper(Module):
    def __init__(self, platform, data_width, memory_type, common_clk, write_depth, bram):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios(data_width, write_depth))
        self.clock_domains.cd_sys  = ClockDomain()
        self.clock_domains.cd_clk1  = ClockDomain()
        self.clock_domains.cd_clk2  = ClockDomain()
        self.submodules.sp = ram = OCM(platform, data_width, memory_type, common_clk, write_depth, bram)
        
        # Single Port RAM
        if (memory_type == "Single_Port"):
            self.comb += ram.addr_A.eq(platform.request("addr_A"))
            self.comb += ram.din_A.eq(platform.request("din_A"))
            self.comb += platform.request("dout_A").eq(ram.dout_A)
            self.comb += self.cd_sys.clk.eq(platform.request("clk_A"))
            self.comb += ram.wen_A.eq(platform.request("wen_A"))
            self.comb += ram.ren_A.eq(platform.request("ren_A"))
        
        # Simple Dual Port RAM
        elif (memory_type == "Simple_Dual_Port"):
            self.comb += ram.addr_A.eq(platform.request("addr_A"))
            self.comb += ram.din_A.eq(platform.request("din_A"))
            self.comb += ram.addr_B.eq(platform.request("addr_B"))
            self.comb += ram.wen_A.eq(platform.request("wen_A"))
            self.comb += ram.ren_B.eq(platform.request("ren_B"))
            self.comb += platform.request("dout_B").eq(ram.dout_B)
            # Common Clock
            if (common_clk == 1):
                self.comb += self.cd_sys.clk.eq(platform.request("clk"))
            else:
                self.comb += self.cd_clk1.clk.eq(platform.request("clk_A"))
                self.comb += self.cd_clk2.clk.eq(platform.request("clk_B"))
                
        # True Dual Port
        elif (memory_type == "True_Dual_Port"):
            self.comb += ram.addr_A.eq(platform.request("addr_A"))
            self.comb += ram.din_A.eq(platform.request("din_A"))
            self.comb += ram.addr_B.eq(platform.request("addr_B"))
            self.comb += ram.din_B.eq(platform.request("din_B"))
            self.comb += ram.wen_A.eq(platform.request("wen_A"))
            self.comb += ram.ren_A.eq(platform.request("ren_A"))
            self.comb += ram.wen_B.eq(platform.request("wen_B"))
            self.comb += ram.ren_B.eq(platform.request("ren_B"))
            self.comb += platform.request("dout_A").eq(ram.dout_A)
            self.comb += platform.request("dout_B").eq(ram.dout_B)
            # Common Clock
            if (common_clk == 1):
                self.comb += self.cd_sys.clk.eq(platform.request("clk"))
            else:
                self.comb += self.cd_clk1.clk.eq(platform.request("clk_A"))
                self.comb += self.cd_clk2.clk.eq(platform.request("clk_B"))
            
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="ON CHIP MEMORY")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="on_chip_memory", language="verilog")

    # Core string value parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--memory_type",    type=str,   default="Single_Port",   choices=["Single_Port", "Simple_Dual_Port", "True_Dual_Port"],   help="RAM Type")
    
    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--data_width",    type=int,   default=32,         choices=range(1,129),         help="RAM Write/Read Width")
    core_range_param_group.add_argument("--write_depth",   type=int,   default=1024,       choices=range(2,32769),       help="RAM Depth")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--common_clk",  type=bool,   default=False,    help="Ports Common Clock")
    core_bool_param_group.add_argument("--bram",        type=bool,   default=False,     help="BRAM vs Distributed Memory")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                        help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                               help="Build Directory")
    build_group.add_argument("--build-name",    default="on_chip_memory_wrapper",           help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    fabric_mem = 4194432
    if args.json:
        args_1 = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        for key, value in vars(args).items():
            if args_1.data_width <= 128 and args_1.data_width > 64 :
                parser._actions[3].choices = [2,int(fabric_mem/128)]
                parser._actions[3].default = int(fabric_mem/128)
            elif args_1.data_width <= 64 and args_1.data_width > 32:
                parser._actions[3].choices = [2,int(fabric_mem/64)]
                parser._actions[3].default = int(fabric_mem/64)
            elif args_1.data_width <= 32 and args_1.data_width > 16:
                parser._actions[3].choices = [2,int(fabric_mem/32)]
                parser._actions[3].default = int(fabric_mem/32)
            elif args_1.data_width <= 16 and args_1.data_width > 8 :
                parser._actions[3].choices = [2,int(fabric_mem/16)]
                parser._actions[3].default = int(fabric_mem/16)
            elif args_1.data_width <= 8 and args_1.data_width > 4 :
                parser._actions[3].choices = [2,int(fabric_mem/8)]
                parser._actions[3].default = int(fabric_mem/8)
            elif args_1.data_width <= 4 and args_1.data_width > 2 :
                parser._actions[3].choices = [2,int(fabric_mem/4)]
                parser._actions[3].default = int(fabric_mem/4)
            elif args_1.data_width <= 2 and args_1.data_width > 1 :
                parser._actions[3].choices = [2,int(fabric_mem/2)]
                parser._actions[3].default = int(fabric_mem/2)
            if args_1.data_width == 32:
                parser._actions[3].default = 1024
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = OCMWrapper(platform,
        memory_type     = args.memory_type,
        data_width      = args.data_width,
        write_depth     = args.write_depth,
        common_clk      = args.common_clk,
        bram            = args.bram
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
            module     = module
        )
        
        # DRAM
        if (args.bram == 0):
            wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "on_chip_memory", "v1_0", args.build_name, "src",args.build_name+".v")
            with open (wrapper, "r") as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if "Port" in line:
                        lines.insert(i, "(* ram_style = \"logic\" *)\n\n")
                        break

            with open(os.path.join(wrapper), "w") as file:
                file.writelines(lines)

if __name__ == "__main__":
    main()
    
