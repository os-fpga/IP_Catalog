#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse
import math

from datetime import datetime

from datetime import datetime

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
    def __init__(self, platform, data_width, memory_type, common_clk, write_depth, bram, file_path, file_extension):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios(data_width, write_depth))
        self.clock_domains.cd_sys  = ClockDomain()
        self.clock_domains.cd_clk1  = ClockDomain()
        self.clock_domains.cd_clk2  = ClockDomain()
        self.submodules.sp = ram = OCM(platform, data_width, memory_type, common_clk, write_depth, bram, file_path, file_extension)
        
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
    
    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core string value parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--memory_type",    type=str,   default="Single_Port",   choices=["Single_Port", "Simple_Dual_Port", "True_Dual_Port"],   help="RAM Type")
    
    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--data_width",    type=int,   default=32,         choices=range(1,129),         help="RAM Write/Read Width")
    core_range_param_group.add_argument("--write_depth",   type=int,   default=1024,       choices=range(2,32769),       help="RAM Depth")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--bram",        type=bool,   default=False,     help="Block RAM vs Distributed Memory")
    core_bool_param_group.add_argument("--common_clk",  type=bool,   default=False,     help="Ports Common Clock")

    # Core file path parameters.
    core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    core_file_path_group.add_argument("--file_path",    type=str,   default="",   help="File Path for memory initialization file (.bin/.hex)")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                        help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                               help="Build Directory")
    build_group.add_argument("--build-name",    default="on_chip_memory",                   help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    details =  {   "IP details": {
    'Name' : 'On Chip Memory Generator',
    'Version' : 'V1_0',
    'Interface' : 'Native',
    'Description' : 'On Chip Memory Generator is an IP Core with native interface. This IP Core simplifies the integration of memory elements, allowing designers to generate customized on-chip memory instances that match their specific requirements. It include the ability to configure memory size, data width, organization (e.g., single-port, dual-port), and various memory types (e.g., single-ported RAM, simple dual-port RAM and true dual port RAM).'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        
        if (args.memory_type in ["Single_Port"]):
            option_strings_to_remove = ['--common_clk']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]

    if (args.memory_type == "Single_Port"):
        memory = "Single Port RAM"
    elif (args.memory_type == "Simple_Dual_Port"):
        memory = "Simple Dual Port RAM"
    else:
        memory = "True Dual Port RAM"
    
    m = math.ceil(args.data_width/36)
    n = math.ceil(args.write_depth/1024)
    
    if (args.bram == 1):
        memory_mapping = "Block RAM"
    else:
        memory_mapping = "Distributed RAM (LUTs)"
    
    summary =  { 
    "Type of Memory": memory,
    "Data Width": args.data_width,
    "Address Width": math.ceil(math.log2(args.write_depth)),
    "Mapping": memory_mapping,
    "Memory Init File Path": args.file_path
    }
    
    if (args.bram == 1):
        summary["Number of BRAMs"] = m*n
        
    if (args.memory_type in ["Simple_Dual_Port", "True_Dual_Port"]):
        if (args.common_clk == 1):
            summary["Common Clock"] = "Both Ports are synchronized"
            
    if (args.file_path == ""):
        summary["Memory Init File Path"] = "None"
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
    
    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = OCMWrapper(platform,
        memory_type     = args.memory_type,
        data_width      = args.data_width,
        write_depth     = args.write_depth,
        common_clk      = args.common_clk,
        bram            = args.bram,
        file_path       = args.file_path,
        file_extension  = os.path.splitext(args.file_path)[1]
        # wrapper         = os.path.join(args.build_dir, "rapidsilicon", "ip", "on_chip_memory", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
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
            version     = "v1_0"
        )
        
        # IP_ID Parameter
        now = datetime.datetime.now()
        my_year         = now.year - 2022
        year            = (bin(my_year)[2:]).zfill(7) # 7-bits  # Removing '0b' prefix = [2:]
        month           = (bin(now.month)[2:]).zfill(4) # 4-bits
        day             = (bin(now.day)[2:]).zfill(5) # 5-bits
        mod_hour        = now.hour % 12 # 12 hours Format
        hour            = (bin(mod_hour)[2:]).zfill(4) # 4-bits
        minute          = (bin(now.minute)[2:]).zfill(6) # 6-bits
        second          = (bin(now.second)[2:]).zfill(6) # 6-bits
        
        # Concatenation for IP_ID Parameter
        ip_id = ("{}{}{}{}{}{}").format(year, day, month, hour, minute, second)
        ip_id = ("32'h{}").format(hex(int(ip_id,2))[2:])
        
        # IP_VERSION parameter
        #               Base  _  Major _ Minor
        ip_version = "00000000_00000000_0000000000000001"
        ip_version = ("32'h{}").format(hex(int(ip_version, 2))[2:])
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "on_chip_memory", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"OCMGEN\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)
        
        # DRAM
        if (args.bram == 0):
            # wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "on_chip_memory", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
            with open (wrapper, "r") as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if "Port" in line:
                        lines.insert(i, "(* ram_style = \"logic\" *)\n\n")
                        break
                    
                file_extension  = os.path.splitext(args.file_path)[1]
                hex_path = "initial begin\n\t$readmemh(\"{}\", memory);\nend\n".format(args.file_path)
                bin_path = "initial begin\n\t$readmemb(\"{}\", memory);\nend\n".format(args.file_path)
                for i, line in enumerate(lines):
                    if "always" in line:
                        if (file_extension == ".hex"):
                            lines.insert(i, hex_path)
                        elif (file_extension == ".bin"):
                            lines.insert(i, bin_path)
                        break

            with open(os.path.join(wrapper), "w") as file:
                file.writelines(lines)

if __name__ == "__main__":
    main()
    
