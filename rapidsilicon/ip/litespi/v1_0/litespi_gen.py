#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteSPI Core.")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(common_path)

    from common import IP_Builder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",             action="store_true",   help="Build core.")
    build_group.add_argument("--build-dir",         default="./",          help="Build directory.")
    build_group.add_argument("--build-name",        default="litespi",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON parameters")
    json_group.add_argument("--json",                                    help="Generate core from JSON file.")
    json_group.add_argument("--json-template",      action="store_true", help="Generate JSON template.")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        with open(args.json, 'rt') as f:
            t_args = argparse.Namespace()
            t_args.__dict__.update(json.load(f))
            args = parser.parse_args(namespace=t_args)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        print(json.dumps(vars(args), indent=4))

    # Create LiteSPI Core --------------------------------------------------------------------------
    from litespi.gen import LiteSPICore, _io
    platform = OSFPGAPlatform(io=_io, toolchain="raptor", device="gemini")
    module   = LiteSPICore(platform,
        module         = "S25FL128L",
        mode           = "x4",
        rate           = "1:1",
        divisor        = "1",
        bus_standard   = "axi-lite",
        bus_endianness = "big",
        sim            = False,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = IP_Builder(device="gemini", ip_name="litespi", language="verilog")
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
