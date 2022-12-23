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

from liteeth.gen import *
from liteeth import phy as liteeth_phys

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("sys_clock", 0, Pins(1)),
    ("sys_reset", 1, Pins(1)),

    # Interrupt
    ("interrupt", 0, Pins(1)),

    # MII PHY Pads
    ("mii_eth_clocks", 0,
        Subsignal("tx", Pins(1)),
        Subsignal("rx", Pins(1)),
    ),
    ("mii_eth", 0,
        Subsignal("rst_n",   Pins(1)),
        Subsignal("mdio",    Pins(1)),
        Subsignal("mdc",     Pins(1)),
        Subsignal("rx_dv",   Pins(1)),
        Subsignal("rx_er",   Pins(1)),
        Subsignal("rx_data", Pins(4)),
        Subsignal("tx_en",   Pins(1)),
        Subsignal("tx_data", Pins(4)),
        Subsignal("col",     Pins(1)),
        Subsignal("crs",     Pins(1))
    ),
]

# Core ---------------------------------------------------------------------------------------------

def LiteEthCore(platform, phy="mii", bus_endianness="big", ntxslots=2, nrxslots=2):
    core_config = {
        "phy"              : getattr(liteeth_phys, f"LiteEthPHY{phy.upper()}"),
        "ntxslots"         : 2,
        "nrxslots"         : 2,
        "clk_freq"         : 100e6,
        "core"             : "axi-lite",
        "endianness"       : bus_endianness,
    }
    core = MACCore(platform, core_config)
    return core

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteEth Core.")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", ".." ,".." , "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    # -----------------  Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axil_ethernet", language="verilog")
    
    # Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--core_phy",            type=str,  default="mii",        choices=["mii", "model"],  help="Type or PHY (mii or model (Sim)).")
    core_string_param_group.add_argument("--core_ntxslots",       type=str,  default="2",          choices=["1", "2", "4"],   help="Number of TX Slots.")
    core_string_param_group.add_argument("--core_nrxslots",       type=str,  default="2",          choices=["1", "2", "4"],   help="Number of RX Slots.")
    core_string_param_group.add_argument("--core_bus_endianness", type=str,  default="big",        choices=["big", "little"], help="Bus Endianness (big, little).")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",             action="store_true",     help="Build core.")
    build_group.add_argument("--build-dir",         default="./",            help="Build directory.")
    build_group.add_argument("--build-name",        default="axil_ethernet", help="Build Folder Name, Build RTL File Name and Module Name")

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

    # Create LiteEth Core --------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=_io, toolchain="raptor", device="gemini")

    import logging
    logging.basicConfig(level=logging.ERROR)

    module = LiteEthCore(platform,
        ntxslots       = int(args.core_ntxslots),
        nrxslots       = int(args.core_nrxslots),
        bus_endianness = args.core_bus_endianness,
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

if __name__ == "__main__":
    main()
