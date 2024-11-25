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

from litex_wrapper.ahb_sram_litex_wrapper import AHBSRAM

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform



# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("hclk",      0, Pins(1)),
        ("hresetn",   0, Pins(1))]
        
        
def ahb_interface():
    return [
        ("hburst",   	0, Pins(3)),
        ("haddr",   	0, Pins(32)),
        ("hsize",  	    0, Pins(3)),
        ("htrans",  	0, Pins(2)),
        ("hwrite",  	0, Pins(1)),
        ("hwdata",  	0, Pins(32)),
        ("hsel",  		0, Pins(1)),
        ("hready",  	0, Pins(1)),
        ("hrdata",  	0, Pins(32)),
        ("hready_resp",  	0, Pins(1)),
        ("hresp",  	    0, Pins(1)),
    ]

def sram_interface():
    return[
        ("sram_q0",      0, Pins(8)),
        ("sram_q1",      0, Pins(8)),
        ("sram_q2",      0, Pins(8)),
        ("sram_q3",      0, Pins(8)),
        ("sram_q4",      0, Pins(8)),
        ("sram_q5",      0, Pins(8)),
        ("sram_q6",      0, Pins(8)),
        ("sram_q7",      0, Pins(8)),
        ("sram_w_en",  	 0, Pins(1)),
        ("bank0_csn",  	 0, Pins(4)),
        ("bank1_csn",  	 0, Pins(4)),
        ("sram_addr_out",0, Pins(13)),
        ("sram_wdata",   0, Pins(32)),    ]

# AHB SRAM Wrapper --------------------------------------------------------------------------------
class AHBSRAMWrapper(Module):
    def __init__(self, platform, sram_data_width, sram_addr_width, addr_width, data_width):
        
        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("hclk"))
        self.comb += self.cd_sys.rst.eq(platform.request("hresetn"))

    
        # AHB_SRAM
        self.submodules.ahb_sram = ahb_sram = AHBSRAM(platform, sram_data_width, sram_addr_width, addr_width, data_width )
        
        platform.add_extension(ahb_interface())
        self.comb += ahb_sram.haddr.eq(platform.request("haddr"))
        self.comb += ahb_sram.hburst.eq(platform.request("hburst"))
        self.comb += ahb_sram.hsize.eq(platform.request("hsize"))
        self.comb += ahb_sram.htrans.eq(platform.request("htrans"))
        self.comb += ahb_sram.hwrite.eq(platform.request("hwrite"))
        self.comb += ahb_sram.hwdata.eq(platform.request("hwdata"))
        self.comb += ahb_sram.hsel.eq(platform.request("hsel"))
        self.comb += ahb_sram.hready.eq(platform.request("hready"))
        
        
        self.comb += platform.request("hrdata").eq(ahb_sram.hrdata)
        self.comb += platform.request("hready_resp").eq(ahb_sram.hready_resp)
        self.comb += platform.request("hresp").eq(ahb_sram.hresp)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AHB_SRAM CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="ahb_sram", language="System verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",       type=int,       default=32,         choices=[32, 64],      help="Data Width")

    # Core range value parameters. 
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--addr_width",     type=int,       default=32,      choices=range(6, 33),      help="Address Width")
    core_range_param_group.add_argument("--sram_data_width",       type=int,       default=8,      choices=range(1, 33),      help="ID Width")
    core_range_param_group.add_argument("--sram_addr_width",       type=int,       default=13,      choices=range(1, 15),      help="ID Width")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="ahb_sram_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()

   #IP Details generation
    details =  {   "IP details": {
    'Name' : 'AHB SRAM Controller',
    'Version' : 'V1_0',
    'Interface' : 'AHB',
    'Description' : 'This IP is a SRAM controller that implements an AHB slave interface, which acts as a bridge between an AHB bus and a SRAM memory unit. It manages data transfers between the two.'}}

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version  = "v1_0")

    #IP Summary generation
        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.copy_images(file_path)
        
    summary =  {  
    "Data width ": '32',

    }

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)


    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AHBSRAMWrapper(platform,
        sram_data_width = args.sram_data_width,
        sram_addr_width = args.sram_addr_width,
        addr_width      = args.addr_width,
        data_width      = args.data_width)

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "ahb_sram", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"A2HB\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
