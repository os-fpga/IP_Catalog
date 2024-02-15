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

from liteeth_build import *
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
    core_string_param_group.add_argument("--core_phy",            type=str,  default="model",        choices=["mii", "model"],help="Type of PHY (mii or model (Sim)).")
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

    #IP Details generation
    details =  {   "IP details": {
    'Name' : 'AXI Lite Ethernet',
    'Version' : 'V1_0',
    'Interface' : 'AXI Lite',
    'Description' : 'This IP core provides a standardized interface for read and write operations between the host system and Ethernet devices. It enables efficient data exchange and control, allowing digital systems to connect to Ethernet networks for tasks such as data transmission, reception, and network management.'}}



    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

    #IP Summary generation
    summary =  { 
    "Type of PHY selected "      : args.core_phy,
    "Number of TX Slots selected": args.core_ntxslots,
    "Number of RX Slots selected": args.core_nrxslots,
    "Bus Endianness "            : args.core_bus_endianness,
    }


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
        

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axil_ethernet", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXILETH\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)
        
if __name__ == "__main__":
    main()
