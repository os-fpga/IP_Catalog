#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse

from litex_wrapper.axi_spi_master_litex_wrapper import AXISPIMASTER

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios():
    return [
        ("s_axi_aclk",  0,    Pins(1)),
        ("s_axi_arst",  0,    Pins(1)),
    ]
    
def get_spi_ios():
    return [
        ("events_o",    0,    Pins(2)),
        ("spi",         0,
            Subsignal("clk",  Pins(1)),
            Subsignal("csn0", Pins(1)),
            Subsignal("csn1", Pins(1)),
            Subsignal("csn2", Pins(1)),
            Subsignal("csn3", Pins(1)),
            Subsignal("mode", Pins(2)),
            Subsignal("sdo0", Pins(1)),
            Subsignal("sdo1", Pins(1)),
            Subsignal("sdo2", Pins(1)),
            Subsignal("sdo3", Pins(1)),
            Subsignal("sdi0", Pins(1)),
            Subsignal("sdi1", Pins(1)),    
            Subsignal("sdi2", Pins(1)), 
            Subsignal("sdi3", Pins(1)), 
        )
    ]

# AXI SPI MASTER Wrapper ----------------------------------------------------------------------------------
class AXISPIMASTERWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, user_width, buffer_depth):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("s_axi_aclk"))
        self.comb += self.cd_sys.rst.eq(platform.request("s_axi_arst"))

        # AXI ----------------------------------------------------------------------------------
        axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            aw_user_width   = user_width,
            w_user_width    = user_width,
            b_user_width    = user_width,
            ar_user_width   = user_width,
            r_user_width    = user_width,
            id_width        = id_width
        )
        
        platform.add_extension(axi.get_ios("s_axi"))
        self.comb += axi.connect_to_pads(platform.request("s_axi"), mode="slave")

        # AXI SPI MASTER -----------------------------------------------------------------------
        self.submodules.spi_master = spi_master = AXISPIMASTER(platform, 
            s_axi           = axi,
            buffer_depth    = buffer_depth
            )
        
        # SPI IOS
        platform.add_extension(get_spi_ios())
        spi_pads = platform.request("spi")
        self.comb += [
            
            # Inputs
            spi_master.spi_sdi0.eq(spi_pads.sdi0),
            spi_master.spi_sdi1.eq(spi_pads.sdi1),
            spi_master.spi_sdi2.eq(spi_pads.sdi2),
            spi_master.spi_sdi3.eq(spi_pads.sdi3),
            
            # Outputs
            spi_pads.clk.eq(spi_master.spi_clk),
            spi_pads.csn0.eq(spi_master.spi_csn0),
            spi_pads.csn1.eq(spi_master.spi_csn1),
            spi_pads.csn2.eq(spi_master.spi_csn2),
            spi_pads.csn3.eq(spi_master.spi_csn3),
            spi_pads.mode.eq(spi_master.spi_mode),
            spi_pads.sdo0.eq(spi_master.spi_sdo0),
            spi_pads.sdo1.eq(spi_master.spi_sdo1),
            spi_pads.sdo2.eq(spi_master.spi_sdo2),
            spi_pads.sdo3.eq(spi_master.spi_sdo3),
        ]
        self.comb += platform.request("events_o").eq(spi_master.events_o)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI SPI MASTER CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(common_path)

    from rapidsilicon.lib.common import IP_Builder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--addr_width",   type=int, default=32, choices=[8, 16, 32],  help="AXI Address Width.")
    core_group.add_argument("--data_width",   type=int, default=32, choices=[8, 16, 32],  help="AXI Data Width.")
    core_group.add_argument("--user_width",   type=int, default=4,  choices=range(1,5),   help="AXI ID Width.")
    core_group.add_argument("--id_width",     type=int, default=16, choices=range(1,17),  help="AXI ID Width.")
    core_group.add_argument("--buffer_depth", type=int, default=8,  choices=[8, 16],      help="AXI Buffer Depth.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_spi_master_wrapper",       help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

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

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXISPIMASTERWrapper(platform,
        addr_width   = args.addr_width,
        data_width   = args.data_width,
        user_width   = args.user_width,
        id_width     = args.id_width,
        buffer_depth = args.buffer_depth,
    )
    
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = IP_Builder(device="gemini", ip_name="axi_spi_master", language="sverilog")
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
