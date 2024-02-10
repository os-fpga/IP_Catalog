#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

from litex_wrapper.mipi_spi2dsi_bridge_litex_wrapper import MIPISPI2DSIBRIDGE

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1))
    ]

def get_other_ios():
        return [    
            ("reg_1v8_en",      0, Pins(1)), 
            ("reg_3v0_en",      0, Pins(1)), 
            ("lcd_rst",         0, Pins(1)), 
            ("bl_en",           0, Pins(1)), 
            ("data_p",          0, Pins(1)), 
            ("data_n",          0, Pins(1)), 
            ("clk_p",           0, Pins(1)), 
            ("clk_n",           0, Pins(1)), 

            ("spi_mosi_i",      0, Pins(1)), 
            ("spi_csn_i",       0, Pins(1)), 
            ("spi_clk_i",       0, Pins(1)), 
            ("lcd_test_i",      0, Pins(1)), 
        ]

# mipi_spi2dsi_bridge Wrapper ----------------------------------------------------------------------------------
class MIPISPI2DSIBRIDGEWrapper(Module):
    def __init__(self, platform):
        
        self.clock_domains.cd_sys  = ClockDomain()
        
        # mipi_spi2dsi_bridge ----------------------------------------------------------------------------------
        self.submodules.mipi_spi2dsi_bridge = mipi_spi2dsi_bridge = MIPISPI2DSIBRIDGE(platform,

            )
        
        # IOS 
        platform.add_extension(get_other_ios())
        self.comb += mipi_spi2dsi_bridge.spi_mosi_i.eq(platform.request("spi_mosi_i"))
        self.comb += mipi_spi2dsi_bridge.spi_csn_i.eq(platform.request("spi_csn_i"))
        self.comb += mipi_spi2dsi_bridge.spi_clk_i.eq(platform.request("spi_clk_i"))
        self.comb += mipi_spi2dsi_bridge.lcd_test_i.eq(platform.request("lcd_test_i"))

        self.comb += platform.request("reg_1v8_en").eq(mipi_spi2dsi_bridge.reg_1v8_en)
        self.comb += platform.request("reg_3v0_en").eq(mipi_spi2dsi_bridge.reg_3v0_en)
        self.comb += platform.request("lcd_rst").eq(mipi_spi2dsi_bridge.lcd_rst)
        self.comb += platform.request("bl_en").eq(mipi_spi2dsi_bridge.bl_en)
        self.comb += platform.request("data_p").eq(mipi_spi2dsi_bridge.data_p)
        self.comb += platform.request("data_n").eq(mipi_spi2dsi_bridge.data_n)
        self.comb += platform.request("clk_p").eq(mipi_spi2dsi_bridge.clk_p)
        self.comb += platform.request("clk_n").eq(mipi_spi2dsi_bridge.clk_n)
        

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="mipi_spi2dsi_bridge")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="mipi_spi2dsi_bridge", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="mipi_spi2dsi_bridge_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    #IP Details generation
    details =  {   "IP details": {
    'Name' : 'MIPI SPI to DSI bridge IP',
    'Version' : 'V1_0',
    'Interface' : 'Native',
    'Description' : 'This IP core is a MIPI DSI Transmitter, SPI slave interface drives the data to be transmitted on the DSI transmitter.'}}


    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

    #IP Summary generation
    summary =  { 
    }


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
    
    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = MIPISPI2DSIBRIDGEWrapper(platform )

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "mipi_spi2dsi_bridge", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"MIPI SPI2DSI\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)
        
#        build_name = args.build_name.rsplit( ".", 1 )[ 0 ]
#        file = os.path.join(args.build_dir, "rapidsilicon/ip/mipi_spi2dsi_bridge/v1_0", build_name, "sim/testbench.v")
#        file = Path(file)
#        text = file.read_text()
#        text = text.replace("mipi_spi2dsi_bridge", "%s" % build_name)
#        file.write_text(text)

if __name__ == "__main__":
    main()
