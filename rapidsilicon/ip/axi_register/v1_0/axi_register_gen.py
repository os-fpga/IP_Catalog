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

from litex_wrapper.axi_register_litex_wrapper import AXIREGISTER

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface

# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1)),
    ]
    
# AXI-REGISTER Wrapper --------------------------------------------------------------------------------
class AXIREGISTERWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, aw_user_width, 
                w_user_width, b_user_width, ar_user_width, r_user_width, 
                aw_reg_type, w_reg_type, b_reg_type, ar_reg_type, r_reg_type):
        
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        reg_type = {
            "Bypass"        :   "0",
            "Simple_Buffer" :   "1",
            "Skid_Buffer"   :   "2"
        }

        # AXI-------------------------------------------------------------
        s_axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
            aw_user_width   = aw_user_width,
            w_user_width    = w_user_width,
            b_user_width    = b_user_width,
            ar_user_width   = ar_user_width,
            r_user_width    = r_user_width
        )
        
        m_axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
            aw_user_width   = aw_user_width,
            w_user_width    = w_user_width,
            b_user_width    = b_user_width,
            ar_user_width   = ar_user_width,
            r_user_width    = r_user_width
        )
        
        # AXI Slave
        platform.add_extension(s_axi.get_ios("s_axi"))
        self.comb += s_axi.connect_to_pads(platform.request("s_axi"), mode="slave")
        
        # AXI Master
        platform.add_extension(m_axi.get_ios("m_axi"))
        self.comb += m_axi.connect_to_pads(platform.request("m_axi"), mode="master")
        
        # AXI-REGISTER -----------------------------------------------------
        self.submodules += AXIREGISTER(platform, 
            s_axi               =   s_axi,
            m_axi               =   m_axi, 
            aw_reg_type         =   reg_type[aw_reg_type],
            w_reg_type          =   reg_type[w_reg_type],
            b_reg_type          =   reg_type[b_reg_type],
            ar_reg_type         =   reg_type[ar_reg_type],
            r_reg_type          =   reg_type[r_reg_type],
            size                =   (2**addr_width)*(data_width/8)
            )

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI REGISTER CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary

    dep_dict = {}         

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_register", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",    type=int,      default=32,     choices=[8, 16, 32, 64, 128, 256, 512, 1024],   help="Register Data Width.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--addr_width",         type=int,       default=32,     choices=range(1,65),        help="Register Address Width.")
    core_range_param_group.add_argument("--id_width",           type=int,       default=32,     choices=range(1,33),        help="Register ID Width from.")
    core_range_param_group.add_argument("--aw_user_width",      type=int,       default=1,      choices=range(1, 1025),     help="Register AW-User Width.")
    core_range_param_group.add_argument("--w_user_width",       type=int,       default=1,      choices=range(1, 1025),     help="Register W-User Width.")
    core_range_param_group.add_argument("--b_user_width",       type=int,       default=1,      choices=range(1, 1025),     help="Register B-User Width.")
    core_range_param_group.add_argument("--ar_user_width",      type=int,       default=1,      choices=range(1, 1025),     help="Register AR-User Width.")
    core_range_param_group.add_argument("--r_user_width",       type=int,       default=1,      choices=range(1, 1025),     help="Register R-User Width.")

# Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--aw_reg_type",   type=str,      default="Simple_Buffer",    choices=["Bypass", "Simple_Buffer", "Skid_Buffer"],   help="Type of Register")
    core_string_param_group.add_argument("--w_reg_type",    type=str,      default="Skid_Buffer",      choices=["Bypass", "Simple_Buffer", "Skid_Buffer"],   help="Type of Register")
    core_string_param_group.add_argument("--b_reg_type",    type=str,      default="Simple_Buffer",    choices=["Bypass", "Simple_Buffer", "Skid_Buffer"],   help="Type of Register")
    core_string_param_group.add_argument("--ar_reg_type",   type=str,      default="Simple_Buffer",    choices=["Bypass", "Simple_Buffer", "Skid_Buffer"],   help="Type of Register")
    core_string_param_group.add_argument("--r_reg_type",    type=str,      default="Skid_Buffer",      choices=["Bypass", "Simple_Buffer", "Skid_Buffer"],   help="Type of Register")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                       help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_register_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'AXI Register',
    'Version' : 'V1_0',
    'Interface' : 'AXI',
    'Description' : 'AXI Register is a AXI4 compliant IP Core. This IP Core enables designers to easily integrate customizable registers into their projects, allowing for efficient data storage, control, and configuration. Its adaptability and simplicity make it a valuable addition to FPGA and SoC designs, contributing to their flexibility and ease of customization.'}
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")

    summary =  { 
    "AXI Data Width": args.data_width,
    "AXI Address Width": args.addr_width,
    "AXI ID Width": args.id_width,
    "Register Size (BYTES)": int(args.data_width/(8))
    }
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXIREGISTERWrapper(platform,
        data_width    = args.data_width,
        addr_width    = args.addr_width,
        id_width      = args.id_width,
        aw_user_width = args.aw_user_width,
        w_user_width  = args.w_user_width,
        b_user_width  = args.b_user_width,
        ar_user_width = args.ar_user_width,
        r_user_width  = args.r_user_width,
        aw_reg_type   = args.aw_reg_type,
        w_reg_type    = args.w_reg_type,
        b_reg_type    = args.b_reg_type,
        ar_reg_type   = args.ar_reg_type,
        r_reg_type    = args.r_reg_type,
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axi_register", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXI_REG\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
