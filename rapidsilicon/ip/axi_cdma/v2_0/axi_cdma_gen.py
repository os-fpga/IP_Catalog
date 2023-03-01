#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from litex_wrapper.axi_cdma_litex_wrapper import AXICDMA

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface, AXILiteInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",   0, Pins(1)),
        ("rst",   0, Pins(1)),
        ("o_int", 0, Pins(1))
        ]



# AXI-CDMA Wrapper --------------------------------------------------------------------------------
class AXICDMAWrapper(Module):
    def __init__(self, platform, id_width, axi_addr_width, axi_data_width, axil_addr_width, axil_data_width):
    
        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # AXI
        axi = AXIInterface(
            id_width           = id_width,
            data_width         = axi_data_width,
            address_width      = axi_addr_width
        )

        

        platform.add_extension(axi.get_ios("m_axi"))
        self.comb += axi.connect_to_pads(platform.request("m_axi"), mode="master")


        # AXI-LITE 
        axil = AXILiteInterface(
            address_width      = axil_addr_width,
            data_width         = axil_data_width
        )
        platform.add_extension(axil.get_ios("s_axil"))
        self.comb += axil.connect_to_pads(platform.request("s_axil"), mode="slave")
        
        
        # AXI_CDMA
        self.submodules.cdma = cdma = AXICDMA(platform, axi,axil)

        self.comb += platform.request("o_int").eq(cdma.o_int)

        
      

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI CDMA CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary

    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_cdma", language="verilog")

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--axi_data_width",        type=int,      default=32,     choices=[8, 16, 32, 64, 128, 256], help="CDMA AXI4 full Data Width.")
    core_fix_param_group.add_argument("--axi_addr_width",        type=int,      default=32,     choices=[8, 16, 32, 64, 128, 256], help="CDMA AXI4 full addr Width.")
    core_fix_param_group.add_argument("--axil_data_width",       type=int,      default=32,     choices=[32],                      help="CDMA AXI4 lite Data Width.")
    core_fix_param_group.add_argument("--axil_addr_width",       type=int,      default=5,      choices=range(1, 65),              help="CDMA AXI4 lite addr Width.")


    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--id_width",          type=int,    default=8,      choices=range(1, 33),    help="CDMA ID Width.")
    
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_cdma_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXICDMAWrapper(platform,
        axi_data_width         = args.axi_data_width,
        axi_addr_width         = args.axi_addr_width,
        id_width               = args.id_width,
        axil_data_width        = args.axil_data_width,
        axil_addr_width        = args.axil_addr_width,
        
    )
    
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v2_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
