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

from litex_wrapper.on_chip_memory_litex_wrapper_symmetric import *

from litex_wrapper.on_chip_memory_litex_wrapper_asymmetric import *

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform


# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios(port_type, data_width, write_depth, memory_type, write_width_A, write_width_B, read_width_A, read_width_B, write_depth_A, write_depth_B, read_depth_A, read_depth_B):    
    
    # read_depth_A depends upon Port A
    if (memory_type == "Single_Port"):
        if (write_depth_A > read_depth_A): # assigning greater value to addr_A port
            write_depth_A = write_depth_A
        else:
            write_depth_A = read_depth_A
    
    # read_depth_B depends upon Port A
    elif (memory_type == "Simple_Dual_Port"):
        write_depth_B   = read_depth_B # assigning greater value to addr_A port
    
    # read_depth_B depends upon Port B only
    elif (memory_type == "True_Dual_Port"):
        if (write_depth_A > read_depth_A): # assigning greater value to addr_A port
            write_depth_A = write_depth_A
        else:
            write_depth_A = read_depth_A
        
        if (write_depth_B > read_depth_B): # assigning greater value to addr_B port
            write_depth_B = write_depth_B
        else:
            write_depth_B = read_depth_B
    
    if port_type == "Asymmetric":
        write_width_A = write_width_A
        write_width_B = write_width_B
        read_width_A  = read_width_A
        read_width_B  = read_width_B
        write_depth_A = write_depth_A
        write_depth_B = write_depth_B
        
    else:
        write_width_A   = data_width
        write_width_B   = data_width
        read_width_A    = data_width
        read_width_B    = data_width
        write_depth_A   = write_depth
        write_depth_B   = write_depth
    
    return [
        ("clk",     0, Pins(1)),
        ("clk_A",   0, Pins(1)),
        ("clk_B",   0, Pins(1)),
        ("rst",     0, Pins(1)),
        
        ("addr_A",  0, Pins(math.ceil(math.log2(write_depth_A)))),
        ("addr_B",  0, Pins(math.ceil(math.log2(write_depth_B)))),
        
        ("din_A",   0, Pins(write_width_A)),
        ("din_B",   0, Pins(write_width_B)),
        
        ("dout_A",  0, Pins(read_width_A)),
        ("dout_B",  0, Pins(read_width_B)),
        
        ("wen_A",   0, Pins(1)),
        ("ren_A",   0, Pins(1)),
        
        ("wen_B",   0, Pins(1)),
        ("ren_B",   0, Pins(1)),
        
        ("be_A",    0, Pins(math.ceil(write_width_A/9))),
        ("be_B",    0, Pins(math.ceil(write_width_B/9)))
    ]

# on_chip_memory Wrapper ----------------------------------------------------------------------------------
class OCMWrapper(Module):
    def __init__(self, platform, write_width_A, write_width_B, read_width_A, read_width_B, memory_type, write_depth, data_width, common_clk, port_type, write_depth_A, read_depth_A, write_depth_B, read_depth_B, memory_mapping, file_path_hex, file_extension, byte_write_enable, op_mode):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios(port_type, data_width, write_depth, memory_type, write_width_A, write_width_B, read_width_A, read_width_B, write_depth_A, write_depth_B, read_depth_A, read_depth_B))
        self.clock_domains.cd_sys   = ClockDomain(reset_less = True)
        self.clock_domains.A        = ClockDomain(reset_less = True)
        self.clock_domains.B        = ClockDomain(reset_less = True)
        
        if port_type == "Asymmetric":
            self.submodules.sp = ram = OCM_ASYM(write_width_A, write_width_B, read_width_A, read_width_B, memory_type, common_clk, write_depth_A, read_depth_A, write_depth_B, read_depth_B, memory_mapping, file_path_hex, file_extension, byte_write_enable, op_mode)
        else:
            self.submodules.sp = ram = OCM_SYM(data_width, memory_type, common_clk, write_depth, memory_mapping, file_path_hex, file_extension, byte_write_enable, op_mode)
            
        self.M = ram.m
        self.N = ram.n    
        
        # Single Port RAM
        if (memory_type == "Single_Port"):
            self.comb += ram.addr_A.eq(platform.request("addr_A"))
            self.comb += ram.din_A.eq(platform.request("din_A"))
            self.comb += self.A.clk.eq(platform.request("clk_A"))
            self.comb += ram.wen_A.eq(platform.request("wen_A"))
            self.comb += ram.ren_A.eq(platform.request("ren_A"))
            if (memory_mapping == "Distributed_RAM"):
                self.comb += platform.request("dout_A").eq(ram.dout_A)
            else:
                if (byte_write_enable):
                    self.comb += ram.be_A.eq(platform.request("be_A"))
                self.comb += platform.request("dout_A").eq(ram.dout_A_)
        
        # Simple Dual Port RAM
        elif (memory_type == "Simple_Dual_Port"):
            self.comb += ram.addr_A.eq(platform.request("addr_A"))
            self.comb += ram.din_A.eq(platform.request("din_A"))
            self.comb += ram.addr_B.eq(platform.request("addr_B"))
            self.comb += ram.wen_A.eq(platform.request("wen_A"))
            self.comb += ram.ren_B.eq(platform.request("ren_B"))
            if (memory_mapping == "Distributed_RAM"):
                self.comb += platform.request("dout_B").eq(ram.dout_B)
            else:
                if (byte_write_enable):
                    self.comb += ram.be_A.eq(platform.request("be_A"))
                self.comb += platform.request("dout_B").eq(ram.dout_B_)
            # Common Clock
            if (common_clk == 1):
                self.comb += self.cd_sys.clk.eq(platform.request("clk"))
            else:
                self.comb += self.A.clk.eq(platform.request("clk_A"))
                self.comb += self.B.clk.eq(platform.request("clk_B"))
                
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
            if (memory_mapping == "Distributed_RAM"):
                self.comb += platform.request("dout_A").eq(ram.dout_A)
                self.comb += platform.request("dout_B").eq(ram.dout_B)
            else:
                if (byte_write_enable):
                    self.comb += ram.be_A.eq(platform.request("be_A"))
                    self.comb += ram.be_B.eq(platform.request("be_B"))
                self.comb += platform.request("dout_A").eq(ram.dout_A_)
                self.comb += platform.request("dout_B").eq(ram.dout_B_)
            # Common Clock
            if (common_clk == 1):
                self.comb += self.cd_sys.clk.eq(platform.request("clk"))
            else:
                self.comb += self.A.clk.eq(platform.request("clk_A"))
                self.comb += self.B.clk.eq(platform.request("clk_B"))
            
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
    core_string_param_group.add_argument("--memory_type",       type=str,   default="Single_Port",   choices=["Single_Port", "Simple_Dual_Port", "True_Dual_Port"],   help="RAM Type")
    core_string_param_group.add_argument("--port_type",         type=str,   default="Symmetric",     choices=["Symmetric", "Asymmetric"],                             help="Ports Type")
    core_string_param_group.add_argument("--memory_mapping",    type=str,   default="Block_RAM",     choices=["Block_RAM", "Distributed_RAM"],                        help="Memory mapping on Block RAM and Distributed RAM (LUTs)")
    core_string_param_group.add_argument("--op_mode",           type=str,   default="Read_First",    choices=["No_Change", "Write_First", "Read_First"],              help="Operation Mode of Memory")
    
    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--common_clk",          type=bool,   default=False,    help="Read/Write Synchronization")
    core_bool_param_group.add_argument("--byte_write_enable",   type=bool,   default=False,    help="Byte Wide Write Enable")
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--DATA_WIDTH",       type=int,   default=16,         choices=[8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128],         help="RAM Write/Read Width")
    core_fix_param_group.add_argument("--write_width_A",    type=int,   default=36,         choices=[9, 18, 36, 72, 144, 288, 576],                                              help="RAM Write Width for Port A")
    core_fix_param_group.add_argument("--write_width_B",    type=int,   default=36,         choices=[9, 18, 36, 72, 144, 288, 576],                                              help="RAM Write Width for Port B")
    core_fix_param_group.add_argument("--read_width_A",     type=int,   default=36,         choices=[9, 18, 36, 72, 144, 288, 576],                                              help="RAM Read Width for Port A")
    core_fix_param_group.add_argument("--read_width_B",     type=int,   default=36,         choices=[9, 18, 36, 72, 144, 288, 576],                                              help="RAM Read Width for Port B")
    core_fix_param_group.add_argument("--write_depth_A",    type=int,   default=1024,       choices=[1024, 2048, 4096, 8192,16384, 32768],                                       help="RAM Depth for Port A")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--data_width",    type=int,   default=32,         choices=range(1,129),         help="RAM Write/Read Width")
    core_range_param_group.add_argument("--write_depth",   type=int,   default=1024,       choices=range(2,32769),       help="RAM Depth")

    # Core file path parameters.
    core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    core_file_path_group.add_argument("--file_path",    type=str,    default="",       help="Path to memory initialization file (.bin/.hex)")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",              help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                     help="Build Directory")
    build_group.add_argument("--build-name",    default="on_chip_memory",         help="Build Folder Name, Build RTL File Name and Module Name")

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
        
        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.copy_images(file_path)
        
        if (args.byte_write_enable == True):
            option_strings_to_remove = ['--data_width']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        else:
            option_strings_to_remove = ['--DATA_WIDTH']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.memory_mapping == "Distributed_RAM"):
            option_strings_to_remove = ['--byte_write_enable']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.write_width_A >= 288 or args.read_width_A >= 288 or args.write_width_B >= 288 or args.read_width_B >= 288):
            parser._actions[11].choices = [1024, 2048, 4096, 8192]
            
        if (args.port_type == "Symmetric"):
            option_strings_to_remove = ['--write_width_A', '--write_width_B', '--read_width_A', '--read_width_B', '--write_depth_A']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        else:
            option_strings_to_remove = ['--DATA_WIDTH', '--data_width','--write_depth']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.memory_type in ["Single_Port"]):
            dep_dict.update({
                        'common_clk':     'True'
                    })
            option_strings_to_remove = ['--write_width_B', '--read_width_B']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.write_width_A != args.read_width_A):
                parser._actions[3].choices = ["Block_RAM"]
                
        elif (args.memory_type in ["Simple_Dual_Port"]):
            option_strings_to_remove = ['--write_width_B', '--read_width_A']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.write_width_A != args.read_width_B):
                parser._actions[3].choices = ["Block_RAM"]

        elif (args.memory_type in ["True_Dual_Port"]):
            if (args.write_width_A != args.read_width_A or args.write_width_A != args.write_width_B or args.write_width_B != args.read_width_B):
                parser._actions[3].choices = ["Block_RAM"]

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    file_extension  = os.path.splitext(args.file_path)[1]
    
    if (args.memory_type == "Single_Port"):
        read_depth_A = int((args.write_depth_A * args.write_width_A) / args.read_width_A)
        read_depth_B = 0
        write_depth_B = read_depth_A
    elif (args.memory_type == "Simple_Dual_Port"):
        read_depth_A = 0
        read_depth_B = int((args.write_depth_A * args.write_width_A) / args.read_width_B)
        write_depth_B =read_depth_B
    elif (args.memory_type == "True_Dual_Port"):
        write_depth_B   = int((args.write_depth_A * args.write_width_A) / args.write_width_B)
        read_depth_A    = int((args.write_depth_A * args.write_width_A) / args.read_width_A)
        read_depth_B    = int((write_depth_B * args.write_width_B) / args.read_width_B)
        
    if (args.memory_type == "Single_Port"):
        memory = "Single Port RAM"
    elif (args.memory_type == "Simple_Dual_Port"):
        memory = "Simple Dual Port RAM"
    else:
        memory = "True Dual Port RAM"
    
    if (args.memory_mapping == "Block_RAM"):
        memory_mapping = "Block RAM"
    else:
        memory_mapping = "Distributed RAM(LUTs)"
        
    summary =  {  
    "Type of Memory": memory,
    "Mapping": memory_mapping,
    }
    
    if args.port_type == "Asymmetric":
        if (args.memory_type == "Single_Port"):
            summary["Address A"] = math.ceil(math.log2(args.write_depth_A))
        elif args.memory_type == "Simple_Dual_Port":
            summary["Address A"] = math.ceil(math.log2(args.write_depth_A))
            summary["Address B"] = math.ceil(math.log2(read_depth_B))
        elif args.memory_type == "True_Dual_Port":
            if (args.write_depth_A > read_depth_A): # assigning greater value to addr_A port
                write_depthA = args.write_depth_A
            else:
                write_depthA = read_depth_A
            if (write_depth_B > read_depth_B): # assigning greater value to addr_B port
                write_depthB = write_depth_B
            else:
                write_depthB = read_depth_B
            summary["Address A"] = math.ceil(math.log2(write_depthA))
            summary["Address B"] = math.ceil(math.log2(write_depthB))
    else:
        summary["Address"] = math.ceil(math.log2(args.write_depth))
    
    if (args.memory_type in ["Simple_Dual_Port", "True_Dual_Port"]):
        if (args.common_clk == 1):
            summary["Synchronization"] = "True"
        else:
            summary["Synchronization"] = "False"
            
    if (args.byte_write_enable == True):
        data = args.DATA_WIDTH
    else:
        data = args.data_width
    
    module   = OCMWrapper(platform,
        memory_type         = args.memory_type,
        data_width          = data,
        write_depth         = args.write_depth,
        write_width_A       = args.write_width_A,
        write_width_B       = args.write_width_B,
        read_width_A        = args.read_width_A,
        read_width_B        = args.read_width_B,
        write_depth_A       = args.write_depth_A,
        write_depth_B       = write_depth_B,
        read_depth_A        = read_depth_A,
        read_depth_B        = read_depth_B,
        common_clk          = args.common_clk,
        memory_mapping      = args.memory_mapping,
        port_type           = args.port_type,
        file_path_hex       = args.file_path,
        file_extension      = file_extension,
        byte_write_enable   = args.byte_write_enable,
        op_mode             = args.op_mode
    )
    
    if (args.memory_mapping == "Block_RAM"):
        summary["Number of BRAMs"] = module.M * module.N
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    
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
            version    = "v1_0"
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
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"OCM\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(\n".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)
        
        # DRAM
        if (args.memory_mapping == "Distributed_RAM"):
            wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "on_chip_memory", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
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