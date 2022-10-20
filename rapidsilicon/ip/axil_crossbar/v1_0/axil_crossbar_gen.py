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

from litex_sim.axil_crossbar_litex_wrapper import AXILITECROSSBAR

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]

# AXI LITE CROSSBAR ----------------------------------------------------------------------------------
class AXILITECROSSBARWrapper(Module):
    def __init__(self, platform, s_count, m_count, data_width, addr_width):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # Slave Interfaces
        s_axils = []
        for s_count in range(s_count):
            s_axil = AXILiteInterface(data_width = data_width , address_width = addr_width)
            if s_count>9:
                platform.add_extension(s_axil.get_ios("s{}_axil".format(s_count)))
                self.comb += s_axil.connect_to_pads(platform.request("s{}_axil".format(s_count)), mode="slave")
            else:
                platform.add_extension(s_axil.get_ios("s0{}_axil".format(s_count)))
                self.comb += s_axil.connect_to_pads(platform.request("s0{}_axil".format(s_count)), mode="slave")
                
            s_axils.append(s_axil)
        
        # Master Interfaces
        m_axils = []    
        for m_count in range(m_count):
            m_axil = AXILiteInterface(data_width = data_width , address_width = addr_width)
            if m_count>9:
                platform.add_extension(m_axil.get_ios("m{}_axil".format(m_count)))
                self.comb += m_axil.connect_to_pads(platform.request("m{}_axil".format(m_count)), mode="master")
            else:
                platform.add_extension(m_axil.get_ios("m0{}_axil".format(m_count)))
                self.comb += m_axil.connect_to_pads(platform.request("m0{}_axil".format(m_count)), mode="master")
            
            m_axils.append(m_axil)

        # AXIL-CROSSBAR ----------------------------------------------------------------------------------
        self.submodules += AXILITECROSSBAR (platform, 
            s_axil      = s_axils,
            m_axil      = m_axils,
            s_count     = s_count,
            m_count     = m_count
            )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AXI_LITE_CROSSBAR_CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(common_path)

    from common import RapidSiliconIPCatalogBuilder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--m_count",        default=4,      type=int,         help="Crossbar Master Interfaces 2 to 16")
    core_group.add_argument("--s_count",        default=4,      type=int,         help="Crossbar SLAVE Interfaces 1 to 16")
    core_group.add_argument("--data_width",     default=32,     type=int,         help="Crossbar Data Width 8,16,32,64,128,256")
    core_group.add_argument("--addr_width",     default=32,     type=int,         help="Crossbar Address Width 32,64,128,256")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="axil_crossbar_wrapper",        help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # AXI Master Interfaces
    m_count_range=range(2,17)
    if args.m_count not in m_count_range:
        logger.error("\nEnter a valid 'm_count' from 2 to 16")
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
    module     = AXILITECROSSBARWrapper(platform,
        m_count    = args.m_count,
        s_count    = args.s_count,
        data_width = args.data_width,
        addr_width = args.addr_width,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="axil_crossbar")
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_verilog(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
