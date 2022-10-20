#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import json
import argparse
import shutil
import logging

from litex_sim.axi_register_litex_wrapper import AXIREGISTER

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
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",      default=32,   type=int,    help="Register Data Width 8,16,32,64,128,256,512,1024")
    core_group.add_argument("--addr_width",      default=32,   type=int,    help="Register Address Width 1 - 64")
    core_group.add_argument("--id_width",        default=32,   type=int,    help="Register ID Width from 1 - 32")

    core_group.add_argument("--aw_user_width",   default=1,    type=int,   help="Register AW-User Width from 1 - 1024")
    core_group.add_argument("--w_user_width",    default=1,    type=int,   help="Register W-User Width from 1 - 1024")
    core_group.add_argument("--b_user_width",    default=1,    type=int,   help="Register B-User Width from 1 - 1024")
    core_group.add_argument("--ar_user_width",   default=1,    type=int,   help="Register AR-User Width from 1 - 1024")
    core_group.add_argument("--r_user_width",    default=1,    type=int,   help="Register R-User Width from 1 - 1024")

    core_group.add_argument("--aw_reg_type",     default=1,    type=int,   help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--w_reg_type",      default=2,    type=int,   help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--b_reg_type",      default=1,    type=int,   help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--ar_reg_type",     default=1,    type=int,   help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--r_reg_type",      default=2,    type=int,   help="Register 0=bypass , 1=simple buffer , 2=skid buffer")

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

    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Data_Width
    data_width_param=[8, 16, 32, 64, 128, 256, 512, 1024]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n%s", data_width_param)
        exit()

    # Address_Width
    addr_range=range(1,65)
    if args.addr_width not in addr_range:
        logger.error("\nEnter a valid 'addr_width' from 1 to 64")
        exit()

    # ID_Width
    id_range=range(1, 33)
    if args.id_width not in id_range:
        logger.error("\nEnter a valid 'id_width' from 1 to 32")
        exit()

    # Write Address Channel User Width
    aw_user_range=range(1, 1025)
    if args.aw_user_width not in aw_user_range:
        logger.error("\nEnter a valid 'aw_user_width' from 1 to 1024")
        exit()

    # Write Data Channel User Width
    w_user_range=range(1, 1025)
    if args.w_user_width not in w_user_range:
        logger.error("\nEnter a valid 'w_user_width' from 1 to 1024")
        exit()

    # Write Response Channel User Width
    b_user_range=range(1, 1025)
    if args.b_user_width not in b_user_range:
        logger.error("\nEnter a valid 'b_user_width' from 1 to 1024")
        exit()

    # Read Address Channel User Width
    ar_user_range=range(1, 1025)
    if args.ar_user_width not in ar_user_range:
        logger.error("\nEnter a valid 'ar_user_width' from 1 to 1024")
        exit()

    # Read Data Channel User Width
    r_user_range=range(1, 1025)
    if args.r_user_width not in r_user_range:
        logger.error("\nEnter a valid 'r_user_width' from 1 to 1024")
        exit()

    # Write Address Channel Register Type
    aw_reg_range=range(3)
    if args.aw_reg_type not in aw_reg_range:
        logger.error("\nEnter a valid 'aw_reg_type' from 0 to 2")
        exit()

    # Write Data Channel Register Type
    w_reg_range=range(3)
    if args.w_reg_type not in w_reg_range:
        logger.error("\nEnter a valid 'w_reg_type' from 0 to 2")
        exit()

    # Write Response Channel Register Type
    b_reg_range=range(3)
    if args.b_reg_type not in b_reg_range:
        logger.error("\nEnter a valid 'b_reg_type' from 0 to 2")
        exit()

    # Read Address Channel Register Type
    ar_reg_range=range(3)
    if args.ar_reg_type not in ar_reg_range:
        logger.error("\nEnter a valid 'ar_reg_type' from 0 to 2")
        exit()

    # Read Data Channel Register Type
    r_reg_range=range(3)
    if args.r_reg_type not in r_reg_range:
        logger.error("\nEnter a valid 'r_reg_type' from 0 to 2")
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

    import sys
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")  # FIXME
    sys.path.append(common_path)                                       # FIXME
    from common import RapidSiliconIPCatalogBuilder
    rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="axi_register")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module = AXIREGISTERWrapper(platform,
        data_width          = args.data_width,
        addr_width          = args.addr_width,
        id_width            = args.id_width,
        aw_user_width       = args.aw_user_width,
        w_user_width        = args.w_user_width,
        b_user_width        = args.b_user_width,
        ar_user_width       = args.ar_user_width,
        r_user_width        = args.r_user_width,   
        aw_reg_type         = args.aw_reg_type,
        w_reg_type          = args.w_reg_type,
        b_reg_type          = args.b_reg_type,
        ar_reg_type         = args.ar_reg_type,
        r_reg_type          = args.r_reg_type                  
        )
    
    # Build
    if args.build:
        rs_builder.generate_verilog(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
