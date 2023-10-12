#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Lite QUADSPI Core.")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", ".." ,".." , "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    # -----------------  Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axil_quadspi", language="verilog")
    
    # Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--core_module",         type=str,  default="S25FL128L",  choices=["S25FL128L"],     help="SPI Flash Module.")
    core_string_param_group.add_argument("--core_mode",           type=str,  default="x4",         choices=["x1", "x4"],      help="SPI Mode.")
    core_string_param_group.add_argument("--core_rate",           type=str,  default="1:1",        choices=["1:1", "1:2"],    help="SPI Flash Core rate.")
    core_string_param_group.add_argument("--core_bus_endianness", type=str,  default="big",        choices=["big", "little"], help="Bus Endianness (big, little).")
    core_string_param_group.add_argument("--core_phy",            type=str,  default="real",       choices=["real", "model"], help="Type or PHY (Real or Model (Sim)).")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--core_divisor",         type=int,  default=1,             choices=range(1, 256),     help="SPI Clk Divisor.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",             action="store_true",        help="Build core.")
    build_group.add_argument("--build-dir",         default="./",               help="Build directory.")
    build_group.add_argument("--build-name",        default="axil_quadspi",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON parameters")
    json_group.add_argument("--json",                                      help="Generate core from JSON file.")
    json_group.add_argument("--json-template",      action="store_true",   help="Generate JSON template.")

    args = parser.parse_args()


    #IP Details generation
    details =  {   "IP details": {
    'Name' : 'AXI Lite QuadSPI',
    'Version' : 'V1_0',
    'Interface' : 'AXI Lite',
    'Description' : ' QuadSPI is a high-speed and efficient serial communication protocol commonly used for flash memory and other storage devices. The QuadSPI IP core enables seamless communication between the host system and QuadSPI devices, allowing efficient data read, write, and erase operations.'}}

 
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

    summary =  { 
    "SPI Flash Module"                : args.core_module,
    "SPI Mode"                        : args.core_mode,
    "SPI Flash Core rate"             : args.core_rate,
    "Bus Endianness "                 : args.core_bus_endianness,
    "Type or PHY (Real or Model (Sim))"    : args.core_phy
  }
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
    # Create LiteSPI Core --------------------------------------------------------------------------
    from litespi_generator import LiteSPICore, _io
    platform = OSFPGAPlatform(io=_io, toolchain="raptor", device="gemini")

    import logging
    logging.basicConfig(level=logging.ERROR)

    module   = LiteSPICore(platform,
        module         = args.core_module,
        mode           = args.core_mode,
        rate           = args.core_rate,
        divisor        = args.core_divisor,
        bus_standard   = "axi-lite",
        bus_endianness = args.core_bus_endianness,
        with_master    = True,
        sim            = (args.core_phy == "model"),
    )
    # Equivalent to ./litespi_gen.py --with-master --bus-standard=axi-lite --module=S25FL128L --mode=x4

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axil_quadspi", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXILQSPI\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)
        
if __name__ == "__main__":
    main()
