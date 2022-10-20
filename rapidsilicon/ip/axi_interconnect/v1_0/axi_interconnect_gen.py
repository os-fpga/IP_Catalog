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

from litex_sim.axi_interconnect_litex_wrapper import AXIINTERCONNECT

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1))
    ]

# AXI INTERCONNECT Wrapper -------------------------------------------------------------------------
class AXIINTERCONNECTWrapper(Module):
    def __init__(self, platform, m_count, s_count ,data_width, addr_width, id_width, aw_user_width, w_user_width, b_user_width,
                ar_user_width, r_user_width, aw_user_en, w_user_en, b_user_en, ar_user_en, r_user_en):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # Slave Interfaces
        s_axis = []
        for s_count in range(s_count):
            s_axi = AXIInterface(data_width = data_width , address_width = addr_width, id_width = id_width, aw_user_width = aw_user_width,
            w_user_width = w_user_width, b_user_width = b_user_width, ar_user_width = ar_user_width, r_user_width = r_user_width)
            if s_count>9:
                platform.add_extension(s_axi.get_ios("s{}_axi".format(s_count)))
                self.comb += s_axi.connect_to_pads(platform.request("s{}_axi".format(s_count)), mode="slave")
            else:
                platform.add_extension(s_axi.get_ios("s0{}_axi".format(s_count)))
                self.comb += s_axi.connect_to_pads(platform.request("s0{}_axi".format(s_count)), mode="slave")
                
            s_axis.append(s_axi)
        
        # Master Interfaces
        m_axis = []    
        for m_count in range(m_count):
            m_axi = AXIInterface(data_width = data_width , address_width = addr_width, id_width = id_width, aw_user_width = aw_user_width,
            w_user_width = w_user_width, b_user_width = b_user_width, ar_user_width = ar_user_width, r_user_width = r_user_width)
            if m_count>9:
                platform.add_extension(m_axi.get_ios("m{}_axi".format(m_count)))
                self.comb += m_axi.connect_to_pads(platform.request("m{}_axi".format(m_count)), mode="master")
            else:
                platform.add_extension(m_axi.get_ios("m0{}_axi".format(m_count)))
                self.comb += m_axi.connect_to_pads(platform.request("m0{}_axi".format(m_count)), mode="master")
            
            m_axis.append(m_axi)

        # AXI-INTERCONNECT ----------------------------------------------------------------------------------
        self.submodules.axi_interconnect = AXIINTERCONNECT(platform,
            s_axi               = s_axis,
            m_axi               = m_axis,
            s_count             = s_count,
            m_count             = m_count,
            aw_user_en          = aw_user_en,
            w_user_en           = w_user_en,
            b_user_en           = b_user_en,
            ar_user_en          = ar_user_en,
            r_user_en           = r_user_en
            )

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI Interconnect CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--m_count",        default=4,      type=int,         help="Interconnect Master Interfaces 2 to 16")
    core_group.add_argument("--s_count",        default=4,      type=int,         help="Interconnect SLAVE Interfaces 2 to 16")
    core_group.add_argument("--data_width",     default=32,     type=int,         help="AXI Data Width 8,16,32,64,128,256")
    core_group.add_argument("--addr_width",     default=32,     type=int,         help="AXI Address Width 32,64,128,256")
    core_group.add_argument("--id_width",       default=8,      type=int,         help="AXI ID Width from 1 to 8")
    core_group.add_argument("--aw_user_en",     default=0,      type=int,         help="AW-Channel User Enable 0 or 1")
    core_group.add_argument("--aw_user_width",  default=1,      type=int,         help="AW-Channel User Width from 1 to 1024")
    core_group.add_argument("--w_user_en",      default=0,      type=int,         help="W-Channel User Enable 0 or 1")
    core_group.add_argument("--w_user_width",   default=1,      type=int,         help="W-Channel User Width from 1 to 1024")
    core_group.add_argument("--b_user_en",      default=0,      type=int,         help="B-Channel User Enable 0 or 1")
    core_group.add_argument("--b_user_width",   default=1,      type=int,         help="B-Channel User Width from 1 t0 1024")
    core_group.add_argument("--ar_user_en",     default=0,      type=int,         help="AR-Channel User Enable 0 or 1")
    core_group.add_argument("--ar_user_width",  default=1,      type=int,         help="AR-Channel User Width from 1 to 1024")
    core_group.add_argument("--r_user_en",      default=0,      type=int,         help="R-Channel User Enable 0 or 1")
    core_group.add_argument("--r_user_width",   default=1,      type=int,         help="R-Channel User Width from 1 to 1024")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                     help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                            help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_interconnect_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # AXI Master Interfaces
    m_count_range=range(1,17)
    if args.m_count not in m_count_range:
        logger.error("\nEnter a valid 'm_count' from 1 to 16")
        exit()
        
    # AXI Slave Interfaces
    s_count_range=range(1,17)
    if args.s_count not in s_count_range:
        logger.error("\nEnter a valid 's_count' from 1 to 16")
        exit()

    # Data_Width
    data_width_param=[8, 16, 32, 64, 128, 256]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s", data_width_param)
        exit()
        
    # Address Width
    addr_width_param=[32, 64, 128, 256]
    if args.addr_width not in addr_width_param:
        logger.error("\nEnter a valid 'addr_width'\n %s", addr_width_param)
        exit()
        
    # ID_Width
    id_range=range(1, 9)
    if args.id_width not in id_range:
        logger.error("\nEnter a valid 'id_width' from 1 to 8")
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
        
    # AW_USER_ENABLE
    aw_user_en_range=range(2)
    if args.aw_user_en not in aw_user_en_range:
        logger.error("\nEnter a valid 'aw_user_en' 0 or 1")
        exit()
        
    # W_USER_ENABLE
    w_user_en_range=range(2)
    if args.w_user_en not in w_user_en_range:
        logger.error("\nEnter a valid 'w_user_en' 0 or 1")
        exit()
        
    # B_USER_ENABLE
    b_user_en_range=range(2)
    if args.b_user_en not in b_user_en_range:
        logger.error("\nEnter a valid 'b_user_en' 0 or 1")
        exit()
        
    # AR_USER_ENABLE
    ar_user_en_range=range(2)
    if args.ar_user_en not in ar_user_en_range:
        logger.error("\nEnter a valid 'ar_user_en' 0 or 1")
        exit()
        
    # R_USER_ENABLE
    r_user_en_range=range(2)
    if args.r_user_en not in r_user_en_range:
        logger.error("\nEnter a valid 'r_user_en' 0 or 1")
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
    rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="axi_interconnect")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()

    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXIINTERCONNECTWrapper(platform,
        m_count             = args.m_count,
        s_count             = args.s_count,
        data_width          = args.data_width,
        addr_width          = args.addr_width,
        id_width            = args.id_width,
        aw_user_en          = args.aw_user_en,
        aw_user_width       = args.aw_user_width,
        w_user_en           = args.w_user_en,
        w_user_width        = args.w_user_width, 
        b_user_en           = args.b_user_en,
        b_user_width        = args.b_user_width,
        ar_user_en          = args.ar_user_en,
        ar_user_width       = args.ar_user_width,
        r_user_en           = args.r_user_en,
        r_user_width        = args.r_user_width
        )
    
    # Build
    if args.build:
        rs_builder.build(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
