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

from litex_wrapper.jtag_to_axi_litex_wrapper import JTAGAXI

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("ACLK",    0, Pins(1)),
        ("ARESET",  0, Pins(1))
    ]

def jtag_interface():
    return [
    
        ("JTAG_TCK",   0, Pins(1)),
        ("JTAG_TMS",   0, Pins(1)),
        ("JTAG_TDI",   0, Pins(1)),
        ("JTAG_TDO",   0, Pins(1)),
        ("JTAG_TRST",  0, Pins(1)),
    ]

# JTAG to AXI Wrapper ----------------------------------------------------------------------------------
class JTAG2AXIWrapper(Module):
    def __init__(self, platform, data_width, addr_width, s_id_width, aw_user_width, w_user_width, b_user_width, ar_user_width, r_user_width):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("ACLK"))
        self.comb += self.cd_sys.rst.eq(platform.request("ARESET"))
    
        m_id_width = s_id_width
        m_axis = []  

        m_axi = AXIInterface(data_width = data_width , address_width = addr_width, id_width = m_id_width, aw_user_width = aw_user_width,
        w_user_width = w_user_width, b_user_width = b_user_width, ar_user_width = ar_user_width, r_user_width = r_user_width)

        platform.add_extension(m_axi.get_ios("m_axi"))
        self.comb += m_axi.connect_to_pads(platform.request("m_axi"), mode="master")
            
        m_axis.append(m_axi)
            
        # JTAG2AXI
        self.submodules.jtag_axi =jtag_axi = JTAGAXI(platform,
            m_axi               = m_axis
            )
        platform.add_extension(jtag_interface())
        self.comb += jtag_axi.JTAG_TCK.eq(platform.request("JTAG_TCK"))
        self.comb += jtag_axi.JTAG_TMS.eq(platform.request("JTAG_TMS"))
        self.comb += jtag_axi.JTAG_TDI.eq(platform.request("JTAG_TDI"))
        self.comb += platform.request("JTAG_TDO").eq(jtag_axi.JTAG_TDO)
        self.comb += jtag_axi.JTAG_TRST.eq(platform.request("JTAG_TRST"))

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="JTAG TO AXI")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    dep_dict = {} 

    # IP Builder
    rs_builder = IP_Builder(device="gemini", ip_name="jtag_to_axi", language="sverilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fixed values parameters
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",    type=int,  default=32, choices=[32, 64],                  help="AXI Data Width.")
    core_fix_param_group.add_argument("--addr_width",    type=int,  default=32, choices=[32],                      help="AXI Address Width.")
    
    # Core Range Value Parameters
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--m_id_width",    type=int,  default=4,  choices=range(1, 9),             help="AXI SLAVE ID Width.")
    core_range_param_group.add_argument("--aw_user_width", type=int,  default=1,  choices=range(1, 33),            help="AW-Channel User Width.")
    core_range_param_group.add_argument("--w_user_width",  type=int,  default=1,  choices=range(1, 33),            help="W-Channel User Width.")
    core_range_param_group.add_argument("--b_user_width",  type=int,  default=1,  choices=range(1, 33),            help="B-Channel User Width.")
    core_range_param_group.add_argument("--ar_user_width", type=int,  default=1,  choices=range(1, 33),            help="AR-Channel User Width.")
    core_range_param_group.add_argument("--r_user_width",  type=int,  default=1,  choices=range(1, 33),            help="R-Channel User Width.")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                       help="Build Directory")
    build_group.add_argument("--build-name",    default="jtag_to_axi_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'JTAG to AXI',
    'Version' : 'V1_0',
    'Interface' : 'JTAG/AXI4 ',
    'Description' : 'The JTAG-to-AXI IP is an AXI4 compliant IP that can be used to initiate AXI4 transactions inside the FPGA. The IP provides an AXI4 master interface on one side and a JTAG interface on the other side.'}
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")

    summary =  { 
    # "DATA WIDTH": args.data_width,
    "DATA WIDTH":args.data_width,
    "ADDR WIDTH": args.addr_width,
    # "PIPELINE OUTPUT": args.pip_out
    }
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini",summary=summary)
    module   = JTAG2AXIWrapper(platform,
        data_width    = args.data_width,
        addr_width    = args.addr_width,
        s_id_width    = args.m_id_width,
        aw_user_width = args.aw_user_width,
        w_user_width  = args.w_user_width,
        b_user_width  = args.b_user_width,
        ar_user_width = args.ar_user_width,
        r_user_width  = args.r_user_width
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "jtag_to_axi", "v1_0", args.build_name, "src",args.build_name+".sv")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"JTAG2AXI\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
