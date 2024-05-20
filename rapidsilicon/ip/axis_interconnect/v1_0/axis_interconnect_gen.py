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
from pathlib import Path

from datetime import datetime

from litex_wrapper.axis_interconnect_litex_wrapper import AXISTREAMINTERCONNECT

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

def get_control_ios(select_width, m_count):
    return [
        ("m{}_select".format(m_count), 0, Pins(select_width))
    ]
    
# AXIS_INTERCONNECT Wrapper ----------------------------------------------------------------------------------
class AXISTREAMINTERCONNECTWrapper(Module):
    def __init__(self, platform, m_count, s_count, data_width, last_en, id_en, id_width, 
                dest_en, dest_width, user_en, user_width):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # Keep Width, Select_width Calculation
        keep_width      = int((data_width+7)/8)
        select_width    = math.ceil(math.log2(s_count))
        
        # Slave Interfaces
        s_axiss = []
        for s_count in range(s_count):
            s_axis = AXIStreamInterface(data_width = data_width , user_width = user_width, id_width = id_width, dest_width = dest_width, keep_width = keep_width)
            if s_count>9:
                platform.add_extension(s_axis.get_ios("s{}_axis".format(s_count)))
                self.comb += s_axis.connect_to_pads(platform.request("s{}_axis".format(s_count)), mode="slave")
            else:
                platform.add_extension(s_axis.get_ios("s0{}_axis".format(s_count)))
                self.comb += s_axis.connect_to_pads(platform.request("s0{}_axis".format(s_count)), mode="slave")
                
            s_axiss.append(s_axis)
            
        # Master Interfaces
        m_axiss = []
        for m_count in range(m_count):
            m_axis = AXIStreamInterface(data_width = data_width , user_width = user_width, id_width = id_width, dest_width = dest_width, keep_width = keep_width)
            if m_count>9:
                platform.add_extension(m_axis.get_ios("m{}_axis".format(m_count)))
                self.comb += m_axis.connect_to_pads(platform.request("m{}_axis".format(m_count)), mode="master")
            else:
                platform.add_extension(m_axis.get_ios("m0{}_axis".format(m_count)))
                self.comb += m_axis.connect_to_pads(platform.request("m0{}_axis".format(m_count)), mode="master")
                
            m_axiss.append(m_axis)
        
        # AXIS-INTERCONNECT ----------------------------------------------------------------------------------
        self.submodules.interconnect = interconnect = AXISTREAMINTERCONNECT(platform,
            m_axis          = m_axiss,
            s_axis          = s_axiss,
            s_count         = s_count,
            m_count         = m_count, 
            last_en         = last_en,
            id_en           = id_en,
            dest_en         = dest_en,
            user_en         = user_en,
            select_width    = select_width
            )
        
        # Interconnect Control Signal ----------------------------------------------------------------------
        for m_count in range(m_count+1):
            platform.add_extension(get_control_ios(select_width, m_count))
            self.comb += interconnect.select[m_count].eq(platform.request("m{}_select".format(m_count)))

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS INTERCONNECT CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # ------------- Ports       : Dependency
    dep_dict = {
                "id_width"      : "id_en",
                "dest_width"    : "dest_en",
                "user_width"    : "user_en"
    }
    
    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axis_interconnect", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",      type=int,     default=8,   choices=[8, 16, 32, 64, 128, 256, 512, 1024],   help="Data Width.")

    # Core Range Value Parameters.
    core_range_param_group = parser.add_argument_group(title="Core Range Parameters")
    core_range_param_group.add_argument("--s_count",     type=int,   default=4,    choices=range(2,17),       help="Slave Interfaces.")
    core_range_param_group.add_argument("--m_count",     type=int,   default=4,    choices=range(1,17),       help="Master Interfaces.")
    core_range_param_group.add_argument("--id_width",    type=int,   default=8,    choices=range(1, 17),      help="ID Width.")
    core_range_param_group.add_argument("--dest_width",  type=int,   default=8,    choices=range(1, 9),       help="Destination Width.")
    core_range_param_group.add_argument("--user_width",  type=int,   default=1,    choices=range(1, 1025),    help="User Width.")
    
    # Core Bool value Parameters.
    core_bool_param_group = parser.add_argument_group(title="Core Bool Parameters")
    core_bool_param_group.add_argument("--last_en",    type=bool,    default=True,    help="Last Enable.")
    core_bool_param_group.add_argument("--id_en",      type=bool,    default=True,    help="ID Enable.")
    core_bool_param_group.add_argument("--dest_en",    type=bool,    default=True,    help="Destination Enable.")
    core_bool_param_group.add_argument("--user_en",    type=bool,    default=True,    help="User Enable.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_interconnect_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    details =  {   "IP details": {
    'Name' : 'AXI-Stream Interconnect',
    'Version' : 'V1_0',
    'Interface' : 'AXI-Stream',
    'Description' : 'AXI-Stream Interconnect is a AXI-Stream compliant IP Core. This IP Core is dedicated to facilitating efficient data streaming between various IP blocks and peripherals. Its primary function is to serve as a central hub that connects multiple AXI-Stream data sources and consumers, ensuring smooth and low-latency data flow.'}
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser , json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")

    summary =  { 
    "Number of Master Interfaces": args.m_count,
    "Number of Slave Interfaces": args.s_count,
    "AXIS Data Width": args.data_width,
    }
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

        
    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXISTREAMINTERCONNECTWrapper(platform,
        s_count        = args.s_count,
        m_count        = args.m_count,
        data_width     = args.data_width,
        last_en        = args.last_en,
        id_en          = args.id_en,
        id_width       = args.id_width,
        dest_en        = args.dest_en,
        dest_width     = args.dest_width,
        user_en        = args.user_en,
        user_width     = args.user_width
    )

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axis_interconnect", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"ASIN\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)
        build_name = args.build_name.rsplit( ".", 1 )[ 0 ]
        file = os.path.join(args.build_dir, "rapidsilicon/ip/axis_interconnect/v1_0", build_name, "sim/test_axis_crosspoint_4x4.v")
        file = Path(file)
        text = file.read_text()
        text = text.replace("axis_interconnect_wrapper", build_name)
        file.write_text(text)

if __name__ == "__main__":
    main()
