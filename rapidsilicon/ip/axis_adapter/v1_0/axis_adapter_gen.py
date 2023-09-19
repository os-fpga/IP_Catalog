#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from datetime import datetime

from litex_wrapper.axis_adapter_litex_wrapper import AXISADAPTER

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIStreamInterface

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]

# AXIS_ADAPTER Wrapper ----------------------------------------------------------------------------------
class AXISADAPTERWrapper(Module):
    def __init__(self, platform, s_data_width, m_data_width, id_en, id_width, 
                dest_en, dest_width, user_en, user_width):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI STREAM SLAVE -------------------------------------------------------------------------------
        s_axis = AXIStreamInterface(
            data_width = s_data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width,
            keep_width = int((s_data_width+7)/8)
        )
        
        # AXI STREAM MASTER -------------------------------------------------------------------------------
        m_axis = AXIStreamInterface(
            data_width = m_data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width,
            keep_width = int((m_data_width+7)/8)
        )
        
        # Input AXI
        platform.add_extension(s_axis.get_ios("s_axis"))
        self.comb += s_axis.connect_to_pads(platform.request("s_axis"), mode="slave")
        
        # Output AXI
        platform.add_extension(m_axis.get_ios("m_axis"))
        self.comb += m_axis.connect_to_pads(platform.request("m_axis"), mode="master")
        
        # AXIS-ADAPTER ----------------------------------------------------------------------------------
        self.submodules += AXISADAPTER(platform,
            m_axis          = m_axis,
            s_axis          = s_axis,
            id_en           = id_en,
            dest_en         = dest_en,
            user_en         = user_en
            )
        
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS ADAPTER CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axis_adapter", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--s_data_width",      type=int,     default=8,   choices=[8, 16, 32, 64, 128, 256, 512, 1024],   help="Slave Data Width.")
    core_fix_param_group.add_argument("--m_data_width",      type=int,     default=8,   choices=[8, 16, 32, 64, 128, 256, 512, 1024],   help="Master Data Width.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--id_width",       type=int,       default=8,      choices=range(1, 17),       help="ID Width.")
    core_range_param_group.add_argument("--dest_width",     type=int,       default=8,      choices=range(1, 9),       help="Destination Width.")
    core_range_param_group.add_argument("--user_width",     type=int,       default=1,      choices=range(1, 1025),     help="User Width.")
    
    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--id_en",        type=bool,     default=True,      help="ID Enable.")
    core_bool_param_group.add_argument("--dest_en",      type=bool,     default=True,      help="Destination Enable.")
    core_bool_param_group.add_argument("--user_en",      type=bool,     default=True,      help="User Enable.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                       help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_adapter_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

        if (args.id_en == False):
            dep_dict.update({
                'id_width' :   'True',
            })
        else:
            dep_dict.update({
                'id_width' :   'False',
            })
        if (args.dest_en == False):
            dep_dict.update({
                'dest_width' :   'True',
            })
        else:
            dep_dict.update({
                'dest_width' :   'False',
            })
        if (args.user_en == False):
            dep_dict.update({
                'user_width' :   'True',
            })
        else:
            dep_dict.update({
                'user_width' :   'False',
            })        

        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXISADAPTERWrapper(platform,
        s_data_width = args.s_data_width,
        m_data_width = args.m_data_width,
        id_en        = args.id_en,
        id_width     = args.id_width,
        dest_en      = args.dest_en,
        dest_width   = args.dest_width,
        user_en      = args.user_en,
        user_width   = args.user_width,
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
        
        # IP_ID Parameter
        now = datetime.now()
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axis_adapter", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXIS_ADP\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
