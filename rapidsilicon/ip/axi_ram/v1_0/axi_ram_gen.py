#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse

from litex_wrapper.axi_ram_litex_wrapper import AXIRAM

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

# AXI RAM Wrapper ----------------------------------------------------------------------------------
class AXIRAMWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, pip_out):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # AXI --------------------------------------------------------------------------------------
        axi = AXIInterface(
            data_width    = data_width,
            address_width = addr_width,
            id_width      = id_width,
        )
        platform.add_extension(axi.get_ios("s_axi"))
        self.comb += axi.connect_to_pads(platform.request("s_axi"), mode="slave")

        # AXI-RAM ----------------------------------------------------------------------------------
        self.submodules += AXIRAM(platform, axi,
            pipeline_output   = pip_out, 
            size              = (2**addr_width)*data_width//8
            )

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI RAM CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

   # Parameter Dependency dictionary

    #                Ports     :    Dependency
    dep_dict = {}            


    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_ram", language="verilog")

    # Core fix value parameters.

    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width", type=int, default=32, choices=[8, 16, 32, 64], help="RAM Data Width.")
 

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--pip_out",    type=bool, default=False,        help="RAM Pipeline Output.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--addr_width", type=int, default=16, choices=range(8,17),     help="RAM Address Width.")
    core_range_param_group.add_argument("--id_width",   type=int, default=8,  choices=range(1, 9),     help="RAM ID Width.")

    # Core file path parameters.
    core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    core_file_path_group.add_argument("--file_path", type=str, default="./", help="File Path for memory initialization file")



    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_ram_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)


    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXIRAMWrapper(platform,
        data_width = args.data_width,
        addr_width = args.addr_width,
        id_width   = args.id_width,
        pip_out    = args.pip_out
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = IP_Builder(device="gemini", ip_name="axi_ram", language="verilog")
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
