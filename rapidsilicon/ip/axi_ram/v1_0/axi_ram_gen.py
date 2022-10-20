#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse
import shutil
import logging

from litex_sim.axi_ram_litex_wrapper import AXIRAM

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
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(common_path)

    from common import RapidSiliconIPCatalogBuilder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",     default=32,     type=int,       help="RAM Data Width 8,16,32,64")
    core_group.add_argument("--addr_width",     default=16,     type=int,       help="RAM Address Width from 8 to 16")
    core_group.add_argument("--id_width",       default=8,      type=int,       help="RAM ID Width from 1 to 8")
    core_group.add_argument("--pip_out",        default=0,      type=int,       help="RAM Pipeline Output 0 or 1")

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

    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Data_Width
    data_width_param=[8, 16, 32, 64]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s", data_width_param)
        exit()

    # Address_Width
    addr_range=range(8,17)
    if args.addr_width not in addr_range:
        logger.error("\nEnter a valid 'addr_width' from 8 to 16")
        exit()

    # ID_Width
    id_range=range(1, 9)
    if args.id_width not in id_range:
        logger.error("\nEnter a valid 'id_width' from 1 to 8")
        exit()

    # Pipeline_Output
    pip_range=range(2)
    if args.pip_out not in pip_range:
        logger.error("\nEnter a valid 'pip_out' 0 or 1")
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
        rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="axi_ram")
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_verilog(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
