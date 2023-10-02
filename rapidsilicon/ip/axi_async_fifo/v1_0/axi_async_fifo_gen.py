#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse
import math

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


    details =  {   "IP details": {
    'Name' : 'axi_asynchronus_fifo',
    'Version' : 'V1_0',
    'Interface' : 'AXI',
    'Description' : 'The AXI Async FIFO is an AXI full compliant customize-able asynchronous FIFO. It can be used to store and retrieve ordered data at different clock domains, while using optimal resources.'}}


    summary =  { 
    "AXI Data width programmed": args.data_width,
    "AXI ID width programmed": args.id_width,
    "Memory Type selected": "Single Dual Port",
  }



    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

    # Export JSON Template (Optional) --------------------------------------------------------------

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
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict , summary=summary)
    #Exporting Details.json



if __name__ == "__main__":
    main()
