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

from litex_sim.axil_gpio_litex_wrapper import AXILITEGPIO

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios ():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1)),
    ]

def get_gpio_ios(data_width):
    return [
        ("gpin",    0, Pins(data_width)),
        ("gpout",   0, Pins(data_width)),
        ("int",     0, Pins(1)),
    ]
    
# AXI-LITE-GPIO Wrapper --------------------------------------------------------------------------------
class AXILITEGPIOWrapper(Module):
    def __init__(self, platform, data_width, addr_width):
        platform.add_extension(get_clkin_ios())
        
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI-LITE 
        axil = AXILiteInterface(
            data_width      = data_width,
            address_width   = addr_width
        )
        platform.add_extension(axil.get_ios("axil"))
        self.comb += axil.connect_to_pads(platform.request("axil"), mode="slave")

        # AXI-LITE-GPIO 
        self.submodules.gpio = gpio = AXILITEGPIO(platform, axil, 
            address_width   = addr_width, 
            data_width      = data_width
            )
        
        # GPIO 
        platform.add_extension(get_gpio_ios(data_width))
        self.comb += gpio.gpin.eq(platform.request("gpin"))
        self.comb += platform.request("gpout").eq(gpio.gpout)
        self.comb += platform.request("int").eq(gpio.int)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI LITE GPIO CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(common_path)

    from common import RapidSiliconIPCatalogBuilder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core Parameters")
    core_group.add_argument("--data_width",     default=32,     type=int,       help="GPIO Data Width 8,16,32")
    core_group.add_argument("--addr_width",     default=16,     type=int,       help="GPIO Address Width from 8 to 16")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build Parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axil_gpio_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Data_Width
    data_width_param=[8, 16, 32]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s", data_width_param)
        exit()
    
    # Address Width
    addr_range=range(8, 17)
    if args.addr_width not in addr_range:
        logger.error("\nEnter a valid 'addr_width' from 8 to 16")
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

    # Build Project Directory ----------------------------------------------------------------------

    rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="axil_gpio")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXILITEGPIOWrapper(platform,
        addr_width  = args.addr_width,
        data_width  = args.data_width
    )

    # Build
    if args.build:
        rs_builder.generate_verilog(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
