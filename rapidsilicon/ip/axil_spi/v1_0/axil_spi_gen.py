#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteSPI Core.")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", ".." ,".." , "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    # -----------------  Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axil_spi", language="verilog")
    
    # Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--core_module",         type=str,  default="S25FL128L",  choices=["S25FL128L"],     help="SPI Flash Module.")
    core_string_param_group.add_argument("--core_mode",           type=str,  default="x1",         choices=["x1", "x4"],      help="SPI Mode.")
    core_string_param_group.add_argument("--core_rate",           type=str,  default="1:1",        choices=["1:1", "1:2"],    help="SPI Flash Core rate.")
    core_string_param_group.add_argument("--core_bus_endianness", type=str,  default="big",        choices=["big", "little"], help="Bus Endianness (big, little).")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--core_divisor",         type=int,  default=1,             choices=range(1, 256),     help="SPI Clk Divisor.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",             action="store_true",   help="Build core.")
    build_group.add_argument("--build-dir",         default="./",          help="Build directory.")
    build_group.add_argument("--build-name",        default="axil_spi",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON parameters")
    json_group.add_argument("--json",                                      help="Generate core from JSON file.")
    json_group.add_argument("--json-template",      action="store_true",   help="Generate JSON template.")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create LiteSPI Core --------------------------------------------------------------------------
    from litespi.gen import LiteSPICore, _io
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
        sim            = False,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
