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

from litex_wrapper.axis_pipeline_register_litex_wrapper import AXISPIPELINEREGISTER

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

# AXIS_PIPELINE_REGISTER Wrapper ----------------------------------------------------------------------------------
class AXISPIPELINEREGISTERWrapper(Module):
    def __init__(self, platform, data_width, last_en, id_en, id_width, 
                dest_en, dest_width, user_en, user_width, reg_type, length
                ):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI STREAM -------------------------------------------------------------------------------
        s_axis = AXIStreamInterface(
            data_width = data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width,
            keep_width = int((data_width+7)/8)
        )
        
        m_axis = AXIStreamInterface(
            data_width = data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width,
            keep_width = int((data_width+7)/8)
        )
        
        register_type = {
            "Bypass"        :   "0",
            "Simple_Buffer" :   "1",
            "Skid_Buffer"   :   "2"
        }
        
        # Input AXI
        platform.add_extension(s_axis.get_ios("s_axis"))
        self.comb += s_axis.connect_to_pads(platform.request("s_axis"), mode="slave")
        
        # Output AXI
        platform.add_extension(m_axis.get_ios("m_axis"))
        self.comb += m_axis.connect_to_pads(platform.request("m_axis"), mode="master")
        
        # AXIS-PIPELINE-REGISTER ----------------------------------------------------------------------------------
        self.submodules += AXISPIPELINEREGISTER(platform,
            m_axis          = m_axis,
            s_axis          = s_axis,
            last_en         = last_en,
            id_en           = id_en,
            dest_en         = dest_en,
            user_en         = user_en,
            reg_type        = register_type[reg_type],
            length          = length
            )
        
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS PIPELINE REGISTER CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports    :    Dependency
    dep_dict = {}   

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axis_pipeline_register", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core string value parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--reg_type",    type=str,        default="Bypass",    choices=["Bypass", "Simple_Buffer", "Skid_Buffer"],      help="Register Type; bypass, simple buffer, skid buffer")

    # Core fixed value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",      type=int,     default=8,   choices=[8, 16, 32, 64, 128, 256, 512, 1024],   help="Data Width.")
    
    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--id_width",       type=int,       default=8,      choices=range(1, 17),       help="ID Width.")
    core_range_param_group.add_argument("--dest_width",     type=int,       default=8,      choices=range(1, 9),       help="Destination Width.")
    core_range_param_group.add_argument("--user_width",     type=int,       default=1,      choices=range(1, 1025),    help="User Width.")
    core_range_param_group.add_argument("--length",         type=int,       default=2,      choices=range(1,17),       help="Number of registers in pipeline.")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--last_en",    type=bool,       default=True,       help="Last Enable.")
    core_bool_param_group.add_argument("--id_en",      type=bool,       default=True,       help="ID Enable.")
    core_bool_param_group.add_argument("--dest_en",    type=bool,       default=True,       help="Destination Enable.")
    core_bool_param_group.add_argument("--user_en",    type=bool,       default=True,       help="User Enable.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                        help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                               help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_pipeline_register_wrapper",   help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    details =  {   "IP details": {
    'Name' : 'AXI-Stream Pipeline Register',
    'Version' : 'V1_0',
    'Interface' : 'AXI-STREAM',
    'Description' : 'AXI-Stream Pipeline Register is a AXI-Stream compliant IP Core. This IP Core is designed to optimize the flow and processing of data streams using the AXI-Stream protocol. This IP core provides a valuable mechanism for inserting pipeline registers into a data stream, which can help enhance data throughput, reduce latency, and improve system performance. It has ability to add pipeline stages to the data stream, effectively breaking down data processing tasks into smaller, more manageable segments.'}
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")

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

    summary =  { 
    "AXI-Stream Data Width": args.data_width,
    "Register Type in Pipelining": args.reg_type,
    "Number of Registers in Pipelining": args.length
    }
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXISPIPELINEREGISTERWrapper(platform,
        data_width = args.data_width,
        last_en    = args.last_en,
        id_en      = args.id_en,
        id_width   = args.id_width,
        dest_en    = args.dest_en,
        dest_width = args.dest_width,
        user_en    = args.user_en,
        user_width = args.user_width,
        reg_type   = args.reg_type,
        length     = args.length,
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axis_pipeline_register", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXIS_PREG\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
