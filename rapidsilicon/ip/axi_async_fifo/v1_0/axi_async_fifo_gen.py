#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import logging
import argparse
import math

from datetime import datetime

from litex_wrapper.axi_async_fifo_litex_wrapper import AXIASYNCFIFO

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_m_ios():
    return [
        ("m_clk", 0, Pins(1)),
        ("m_rst", 0, Pins(1))
    ]
    
def get_clkin_s_ios():
    return [
        ("s_clk", 0, Pins(1)),
        ("s_rst", 0, Pins(1))
    ]

class AXIASYNCFIFOWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, fifo_depth):
        
        platform.add_extension(get_clkin_s_ios())
        platform.add_extension(get_clkin_m_ios())
        self.clock_domains.cd_sys = ClockDomain()

        # AXI
        m_axi = AXIInterface(
            data_width      = data_width,
            address_width   = (math.ceil(math.log2(fifo_depth))),
            id_width        = id_width,
        )
        
        s_axi = AXIInterface(
            data_width      = data_width,
            address_width   = (math.ceil(math.log2(fifo_depth))),
            id_width        = id_width,
        )
        
        platform.add_extension(m_axi.get_ios("m_axi"))
        self.comb += m_axi.connect_to_pads(platform.request("m_axi"), mode="master")
        
        platform.add_extension(s_axi.get_ios("s_axi"))
        self.comb += s_axi.connect_to_pads(platform.request("s_axi"), mode="slave")
        
        # AXI-ASYNC-FIFO -------------------------------------------------------------------------------
        self.submodules.fifo=fifo = AXIASYNCFIFO(platform, m_axi=m_axi, s_axi=s_axi, 
            fifo_depth   =   fifo_depth,
            )

        self.comb += self.fifo.m_clk.eq(platform.request("m_clk"))
        self.comb += self.fifo.m_rst.eq(platform.request("m_rst"))
        self.comb += self.fifo.s_clk.eq(platform.request("s_clk"))
        self.comb += self.fifo.s_rst.eq(platform.request("s_rst"))
        


# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS ASYNC FIFO CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}   

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_async_fifo", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--fifo_depth",          type=int,     default=4096,   choices=[8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192,16384,32768],   help="FIFO Depth.")
    core_fix_param_group.add_argument("--data_width",          type=int,     default=32,   choices=[8, 16, 32, 64, 128],   help="Data width.")


    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--id_width",           type=int,       default=8,      choices=range(1, 33),        help="FIFO ID Width.")
    core_range_param_group.add_argument("--address_width",      type=int,       default=32,      choices=range(1,33),        help="FIFO Address Width.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                  help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                         help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_async_fifo_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    #IP Details generation
    details =  {   "IP details": {
    'Name' : 'AXI Async FIFO',
    'Version' : 'V1_0',
    'Interface' : 'AXI',
    'Description' : 'The AXI Async FIFO is an AXI full compliant customize-able asynchronous FIFO. It can be used to store and retrieve ordered data at different clock domains, while using optimal resources.'}}



    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

    #IP Summary generation
    summary =  { 
    "AXI FIFO Depth selected": args.fifo_depth,
    "AXI Data width programmed": args.data_width,
    "AXI Address width programmed": args.address_width,
    "AXI ID width programmed": args.id_width,
    }


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

        


    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXIASYNCFIFOWrapper(platform,
        data_width   = args.data_width,
        id_width     = args.id_width,
        fifo_depth   = args.fifo_depth,
        addr_width   = args.address_width,
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axi_async_fifo", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AAFF\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
