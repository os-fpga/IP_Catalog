#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import json
import argparse
import shutil
import logging

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform 

from litex.soc.interconnect import stream

from litex.soc.interconnect.axi import *

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("axis_clk",  0, Pins(1)),
        ("axis_rst",  0, Pins(1)),
    ]

# AXI Stream Converter -----------------------------------------------------------------------------
class AXISConverter(Module):
    def __init__(self, platform, in_width=64, out_width=64, user_width=0, reverse=False):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("axis_clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("axis_rst"))

        # Input AXI --------------------------------------------------------------------------------
        axis_in = AXIStreamInterface(data_width=in_width, user_width=user_width)
        platform.add_extension(axis_in.get_ios("s_axis"))
        self.comb += axis_in.connect_to_pads(platform.request("s_axis"), mode="slave")

        # Output AXI -------------------------------------------------------------------------------
        axis_out = AXIStreamInterface(data_width=out_width, user_width=user_width)
        platform.add_extension(axis_out.get_ios("m_axis"))
        self.comb += axis_out.connect_to_pads(platform.request("m_axis"), mode="master")

        # Converter --------------------------------------------------------------------------------
        converter = stream.StrideConverter(axis_in.description, axis_out.description, reverse=reverse)
        self.submodules += converter
        self.comb += axis_in.connect(converter.sink)
        self.comb += converter.source.connect(axis_out)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI STREAM CONVERTER CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )
    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--core_in_width",      default=128,       type=int,            help="AXI-ST Input Data-width.")
    core_group.add_argument("--core_out_width",     default=64,        type=int,            help="AXI-ST Output Data-width.")
    core_group.add_argument("--core_user_width",    default=1,         type=int,            help="AXI-ST User width.")
    core_group.add_argument("--core_reverse",       default=0,         type=int,            help="Reverse Converter Ordering.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",             action="store_true",                    help="Build core.")
    build_group.add_argument("--build-dir",         default="./",                           help="Build directory.")
    build_group.add_argument("--build-name",        default="axis_width_converter",         help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON parameters")
    json_group.add_argument("--json",                                               help="Generate core from JSON file.")
    json_group.add_argument("--json-template",      action="store_true",            help="Generate JSON template.")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")
    
    # Data IN/OUT Check
    data_param = [8, 16, 32, 64, 128, 256, 512, 1024]
    if args.core_in_width not in data_param:
        logger.error("\nEnter a valid 'core_in_width'\n %s", data_param)
        exit()
        
    if args.core_out_width not in data_param:
        logger.error("\nEnter a valid 'core_out_width'\n %s", data_param)
        exit()
        
    # User Width
    if args.core_user_width not in range(1,4097):
        logger.error("\nEnter a valid 'core_user_width' from 1 to 4096\n")
        exit()
        
    # Reverse Condition
    if args.core_reverse not in range(2):
        logger.error("\nEnter a valid 'core_reverse' 0 or 1\n")
        exit()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        with open(args.json, 'rt') as f:
            t_args = argparse.Namespace()
            t_args.__dict__.update(json.load(f))
            args = parser.parse_args(namespace=t_args)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        print(json.dumps(vars(args), indent=4))
        
    # Remove build extension when specified.
    args.build_name = os.path.splitext(args.build_name)[0]

    # Create LiteX Core ----------------------------------------------------------------------------
    core_in_width   = int(args.core_in_width)
    core_out_width  = int(args.core_out_width)
    core_user_width = int(args.core_user_width)
    platform   = OSFPGAPlatform( io=[], device='gemini', toolchain="raptor")
    module     = AXISConverter(platform,
        in_width   = core_in_width,
        out_width  = core_out_width,
        user_width = core_user_width,
    )
    
    # Build Project Directory ----------------------------------------------------------------------

    import sys
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")  # FIXME
    sys.path.append(common_path)                                       # FIXME
    from common import RapidSiliconIPCatalogBuilder
    rs_builder = RapidSiliconIPCatalogBuilder(ip_name="axis_width_converter")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))

        # Design Path
        design_path = os.path.join("../src", (args.build_name + ".v")) 
        
        # TCL File Content        
        tcl = []
        # Create Design.
        tcl.append(f"create_design {args.build_name}")
        # Set Device.
        tcl.append(f"target_device {'GEMINI'}")
        # Add Include Path.
        tcl.append(f"add_library_path {'../src'}")
        # Add Sources.
#        for f, typ, lib in file_name:
        tcl.append(f"add_design_file {design_path}")
        # Set Top Module.
        tcl.append(f"set_top_module {args.build_name}")
        # Add Timings Constraints.
#        tcl.append(f"add_constraint_file {args.build_name}.sdc")
        # Run.
        tcl.append("synthesize")

        # Generate .tcl file
        tcl_path = os.path.join(rs_builder.synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()

    # Build
    if args.build:
        rs_builder.build(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
