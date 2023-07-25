#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from litex_wrapper.jtag_to_axi_litex_wrapper import JTAGAXI

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("ACLK",    0, Pins(1)),
        ("ARESET",  0, Pins(1))
    ]

def jtag_interface():
    return [
    
        ("JTAG_TCK",   0, Pins(1)),
        ("JTAG_TMS",   0, Pins(1)),
        ("JTAG_TDI",   0, Pins(1)),
        ("JTAG_TDO",   0, Pins(1)),
        ("JTAG_TRST",  0, Pins(1)),
    ]

# JTAG to AXI Wrapper ----------------------------------------------------------------------------------
class JTAG2AXIWrapper(Module):
    def __init__(self, platform, data_width, addr_width, s_id_width, aw_user_width, w_user_width, b_user_width, ar_user_width, r_user_width):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("ACLK"))
        self.comb += self.cd_sys.rst.eq(platform.request("ARESET"))
    
        m_id_width = s_id_width
        m_axis = []  

        m_axi = AXIInterface(data_width = data_width , address_width = addr_width, id_width = m_id_width, aw_user_width = aw_user_width,
        w_user_width = w_user_width, b_user_width = b_user_width, ar_user_width = ar_user_width, r_user_width = r_user_width)

        platform.add_extension(m_axi.get_ios("m_axi"))
        self.comb += m_axi.connect_to_pads(platform.request("m_axi"), mode="master")
            
        m_axis.append(m_axi)
            
        # JTAG2AXI
        self.submodules.jtag_axi =jtag_axi = JTAGAXI(platform,
            m_axi               = m_axis
            )
        platform.add_extension(jtag_interface())
        self.comb += jtag_axi.JTAG_TCK.eq(platform.request("JTAG_TCK"))
        self.comb += jtag_axi.JTAG_TMS.eq(platform.request("JTAG_TMS"))
        self.comb += jtag_axi.JTAG_TDI.eq(platform.request("JTAG_TDI"))
        self.comb += platform.request("JTAG_TDO").eq(jtag_axi.JTAG_TDO)
        self.comb += jtag_axi.JTAG_TRST.eq(platform.request("JTAG_TRST"))

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="JTAG TO AXI")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    dep_dict = {} 

    # IP Builder
    rs_builder = IP_Builder(device="gemini", ip_name="jtag_to_axi", language="sverilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fixed values parameters
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",    type=int,  default=32, choices=[32, 64],                  help="AXI Data Width.")
    core_fix_param_group.add_argument("--addr_width",    type=int,  default=32, choices=[32],                      help="AXI Address Width.")
    
    # Core Range Value Parameters
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--m_id_width",    type=int,  default=4,  choices=range(1, 9),             help="AXI SLAVE ID Width.")
    core_range_param_group.add_argument("--aw_user_width", type=int,  default=1,  choices=range(1, 33),            help="AW-Channel User Width.")
    core_range_param_group.add_argument("--w_user_width",  type=int,  default=1,  choices=range(1, 33),            help="W-Channel User Width.")
    core_range_param_group.add_argument("--b_user_width",  type=int,  default=1,  choices=range(1, 33),            help="B-Channel User Width.")
    core_range_param_group.add_argument("--ar_user_width", type=int,  default=1,  choices=range(1, 33),            help="AR-Channel User Width.")
    core_range_param_group.add_argument("--r_user_width",  type=int,  default=1,  choices=range(1, 33),            help="R-Channel User Width.")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                       help="Build Directory")
    build_group.add_argument("--build-name",    default="jtag_to_axi_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = JTAG2AXIWrapper(platform,
        data_width    = args.data_width,
        addr_width    = args.addr_width,
        s_id_width    = args.m_id_width,
        aw_user_width = args.aw_user_width,
        w_user_width  = args.w_user_width,
        b_user_width  = args.b_user_width,
        ar_user_width = args.ar_user_width,
        r_user_width  = args.r_user_width
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
            module     = module
        )

if __name__ == "__main__":
    main()
