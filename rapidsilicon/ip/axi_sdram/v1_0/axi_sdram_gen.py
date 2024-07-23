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

from litex_wrapper.axi_sdram_litex_wrapper import AXISDRAM

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]



def sdram_interface():
    return [    
        ("sdram_data_input_i",  0,  Pins(16)),
        ("sdram_clk_o",         0,  Pins(1)),
        ("sdram_cke_o",         0,  Pins(1)),
        ("sdram_cs_o",          0,  Pins(1)),
        ("sdram_ras_o",         0,  Pins(1)),
        ("sdram_cas_o",         0,  Pins(1)),
        ("sdram_we_o",          0,  Pins(1)),
        ("sdram_dqm_o",         0,  Pins(2)),
        ("sdram_addr_o",        0,  Pins(13)),
        ("sdram_ba_o",          0,  Pins(2)),
        ("sdram_data_output_o", 0,  Pins(16)),
        ("sdram_data_out_en_o", 0,  Pins(1)),
    ]

# SDRAM Wrapper ----------------------------------------------------------------------------------
class SDRAMWRAPPER(Module):
    def __init__(self, platform):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # AXI --------------------------------------------------------------------------------------
        axi = AXIInterface()

        platform.add_extension(axi.get_ios("s_axi"))
        self.comb += axi.connect_to_pads(platform.request("s_axi"), mode="slave")

        # AXI DDR ----------------------------------------------------------------------------------
        self.submodules.sdram = sdram = AXISDRAM(platform, axi)

        platform.add_extension(sdram_interface())

        #inputs
        self.comb += sdram.sdram_data_input_i.eq(platform.request("sdram_data_input_i"))
        
        # Outputs
        self.comb += platform.request("sdram_clk_o").eq(sdram.sdram_clk_o)
        self.comb += platform.request("sdram_cke_o").eq(sdram.sdram_cke_o)
        self.comb += platform.request("sdram_cs_o").eq(sdram.sdram_cs_o)
        self.comb += platform.request("sdram_ras_o").eq(sdram.sdram_ras_o)
        self.comb += platform.request("sdram_cas_o").eq(sdram.sdram_cas_o)
        self.comb += platform.request("sdram_we_o").eq(sdram.sdram_we_o)
        self.comb += platform.request("sdram_dqm_o").eq(sdram.sdram_dqm_o)
        self.comb += platform.request("sdram_addr_o").eq(sdram.sdram_addr_o)
        self.comb += platform.request("sdram_ba_o").eq(sdram.sdram_ba_o)
        self.comb += platform.request("sdram_data_output_o").eq(sdram.sdram_data_output_o)
        self.comb += platform.request("sdram_data_out_en_o").eq(sdram.sdram_data_out_en_o)




# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI SDRAM CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}
    

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_sdram", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.

    # Core range value parameters.
#    core_range_param_group = parser.add_argument_group(title="Core range parameters")
#    core_range_param_group.add_argument("--ba_bits",        type=int,   default=2,      choices=range(1, 5),     help="BANK ADDRESS WIDTH")
#    core_range_param_group.add_argument("--row_bits",       type=int,   default=13,      choices=range(1, 16),     help="RAM ID Width")
#    core_range_param_group.add_argument("--col_bits",       type=int,   default=11,      choices=range(1, 15),     help="RAM ID Width")
#    core_range_param_group.add_argument("--dq_level",       type=int,   default=2,      choices=range(1, 3),     help="RAM ID Width")
#    
#    # Core bool value parameters.
#    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
#    core_bool_param_group.add_argument("--read_buffer",    type=bool,   default=False,    help="Enable read buffer")
#
    # Core file path parameters.
    # core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    # core_file_path_group.add_argument("--file_path", type=argparse.FileType('r'), help="File Path for memory initialization file")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_sdram_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'DDR SDRAM',
    'Version' : 'V1_0',
    'Interface' : 'AXI',
    'Description' : ' DDR1-SDRAM controller with a AXI4 slave port.'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        
        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.copy_images(file_path)
        
    summary =  {  
    "AXI SDRAM controller"    }
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)


    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = SDRAMWRAPPER(platform)

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axi_sdram", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"DDR\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
