#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from litex_wrapper.bram_litex_wrapper import *

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

# BRAM Wrapper ----------------------------------------------------------------------------------
class BRAMWrapper(Module):
    def __init__(self, platform, data_width, memory_type, common_clk, write_depth):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios(data_width, write_depth))
        self.clock_domains.cd_sys  = ClockDomain()
        self.submodules.sp = ram = BRAM(platform, data_width, memory_type, common_clk, write_depth)
        
        # Single Port RAM
        if (memory_type == "SP"):
            self.comb += ram.addr_A.eq(platform.request("addr_A"))
            self.comb += ram.din_A.eq(platform.request("din_A"))
            self.comb += platform.request("dout_A").eq(ram.dout_A)
            self.comb += self.cd_sys.clk.eq(platform.request("clk_A"))
            self.comb += ram.wen_A.eq(platform.request("wen_A"))
            self.comb += ram.ren_A.eq(platform.request("ren_A"))
        
        # Simple Dual Port RAM
        elif (memory_type == "SDP"):
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
                self.comb += ram.clk_A.eq(platform.request("clk_A"))
                self.comb += ram.clk_B.eq(platform.request("clk_B"))
                
        # True Dual Port
        elif (memory_type == "TDP"):
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
                self.comb += ram.clk_A.eq(platform.request("clk_A"))
                self.comb += ram.clk_B.eq(platform.request("clk_B"))
            
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="BRAM CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="bram", language="verilog")

    # Core string value parameters.
    core_string_param_group = parser.add_argument_group(title="Core fix parameters")
    core_string_param_group.add_argument("--memory_type",    type=str,   default="SP",   choices=["SP", "SDP", "TDP"],   help="RAM Type.")
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",   type=int,       default=32,      choices=[32, 64, 96, 128],      help="RAM Write/Read Width")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--common_clk",  type=bool,   default=False,    help="Ports Common Clock.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--write_depth",   type=int,   default=1024,       choices=range(2,32769),       help="RAM Depth.")

    # Core file path parameters.
    core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    core_file_path_group.add_argument("--file_path",   type=argparse.FileType('r'),   help="File Path for memory initialization file")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="bram_wrapper",         help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = BRAMWrapper(platform,
        memory_type     = args.memory_type,
        data_width      = args.data_width,
        write_depth     = args.write_depth,
        common_clk      = args.common_clk
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

if __name__ == "__main__":
    main()
