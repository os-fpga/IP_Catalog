#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from litex_wrapper.soc_fpga_intf_axi_m0_litex_wrapper import SOC_FPGA_INTF_AHB_S

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface

from litex.soc.interconnect.ahb import Interface

# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios():
    return [
        ("M0_ACLK",  0, Pins(1)),
        ("M0_ARESETN_I",  0, Pins(1)),
    ]

# AXI RAM Wrapper ----------------------------------------------------------------------------------
class AHBSLAVEWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("M0_ACLK"))
        self.comb += self.cd_sys.rst.eq(platform.request("M0_ARESETN_I"))

        # AXI --------------------------------------------------------------------------------------

        ahb = Interface(
            adr_width = addr_width,
            data_width = data_width
        )

        platform.add_extension(ahb.get_ios("s_ahb"))
        self.comb += ahb.connect_to_pads(platform.request("s_ahb"), mode="master")

        # AXI-RAM ----------------------------------------------------------------------------------
        self.submodules += SOC_FPGA_INTF_AHB_S(platform, axi)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SOC FPGA AXI M0 INTF")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="soc_fpga_intf_axi_m0", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",   type=int,   default=32,     choices=[8, 16, 32, 64],    help="RAM Data Width")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--addr_width",     type=int,   default=16,     choices=range(8,17),     help="RAM Address Width")
    core_range_param_group.add_argument("--id_width",       type=int,   default=8,      choices=range(1, 9),     help="RAM ID Width")
    
    # Core file path parameters.
    # core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    # core_file_path_group.add_argument("--file_path", type=argparse.FileType('r'), help="File Path for memory initialization file")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="soc_fpga_intf_axi_m0_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = AHBSLAVEWrapper(platform,
        data_width = args.data_width,
        addr_width = args.addr_width,
        id_width   = args.id_width
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
