#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse

from litex_wrapper.axi_register_litex_wrapper import AXIREGISTER

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface

# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1)),
    ]
    
# AXI-REGISTER Wrapper --------------------------------------------------------------------------------
class AXIREGISTERWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, aw_user_width, 
                w_user_width, b_user_width, ar_user_width, r_user_width, 
                aw_reg_type, w_reg_type, b_reg_type, ar_reg_type, r_reg_type):
        
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI-------------------------------------------------------------
        s_axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
            aw_user_width   = aw_user_width,
            w_user_width    = w_user_width,
            b_user_width    = b_user_width,
            ar_user_width   = ar_user_width,
            r_user_width    = r_user_width
        )
        
        m_axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
            aw_user_width   = aw_user_width,
            w_user_width    = w_user_width,
            b_user_width    = b_user_width,
            ar_user_width   = ar_user_width,
            r_user_width    = r_user_width
        )
        
        # AXI Slave
        platform.add_extension(s_axi.get_ios("s_axi"))
        self.comb += s_axi.connect_to_pads(platform.request("s_axi"), mode="slave")
        
        # AXI Master
        platform.add_extension(m_axi.get_ios("m_axi"))
        self.comb += m_axi.connect_to_pads(platform.request("m_axi"), mode="master")
        
        # AXI-REGISTER -----------------------------------------------------
        self.submodules += AXIREGISTER(platform, 
            s_axi               =   s_axi,
            m_axi               =   m_axi, 
            aw_reg_type         =   aw_reg_type,
            w_reg_type          =   w_reg_type,
            b_reg_type          =   b_reg_type,
            ar_reg_type         =   ar_reg_type,
            r_reg_type          =   r_reg_type,
            size                =   (2**addr_width)*(data_width/8)
            )


# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI REGISTER CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(common_path)

    from common import IP_Builder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",    type=int, default=32, choices=[8, 16, 32, 64, 128, 256, 512, 1024], help="Register Data Width.")
    core_group.add_argument("--addr_width",    type=int, default=32, choices=range(1,65),                          help="Register Address Width.")
    core_group.add_argument("--id_width",      type=int, default=8,  choices=range(1,33),                          help="Register ID Width.")

    core_group.add_argument("--aw_user_width", type=int, default=1,  choices=range(1, 1025),  help="Register AW-User Width.")
    core_group.add_argument("--w_user_width",  type=int, default=1,  choices=range(1, 1025),  help="Register W-User Width.")
    core_group.add_argument("--b_user_width",  type=int, default=1,  choices=range(1, 1025),  help="Register B-User Width.")
    core_group.add_argument("--ar_user_width", type=int, default=1,  choices=range(1, 1025),  help="Register AR-User Width.")
    core_group.add_argument("--r_user_width",  type=int, default=1,  choices=range(1, 1025),  help="Register R-User Width.")

    core_group.add_argument("--aw_reg_type",   type=int, default=1,  choices=range(3), help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--w_reg_type",    type=int, default=2,  choices=range(3), help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--b_reg_type",    type=int, default=1,  choices=range(3), help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--ar_reg_type",   type=int, default=1,  choices=range(3), help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--r_reg_type",    type=int, default=2,  choices=range(3), help="Register 0=bypass , 1=simple buffer , 2=skid buffer")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                       help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_register_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = AXIREGISTERWrapper(platform,
        data_width    = args.data_width,
        addr_width    = args.addr_width,
        id_width      = args.id_width,
        aw_user_width = args.aw_user_width,
        w_user_width  = args.w_user_width,
        b_user_width  = args.b_user_width,
        ar_user_width = args.ar_user_width,
        r_user_width  = args.r_user_width,
        aw_reg_type   = args.aw_reg_type,
        w_reg_type    = args.w_reg_type,
        b_reg_type    = args.b_reg_type,
        ar_reg_type   = args.ar_reg_type,
        r_reg_type    = args.r_reg_type,
    )
    
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = IP_Builder(device="gemini", ip_name="axi_register", language="verilog")
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
