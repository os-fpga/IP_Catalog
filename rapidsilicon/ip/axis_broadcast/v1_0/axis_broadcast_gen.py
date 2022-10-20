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

from litex_sim.axis_broadcast_litex_wrapper import AXISBROADCAST

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIStreamInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1)),]

# AXIS-BROADCAST Wrapper --------------------------------------------------------------------------------
class AXIBROADCASTWrapper(Module):
    def __init__(self, platform, m_count, data_width, last_en, id_en, id_width, dest_en, dest_width, user_en, user_width):

        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # Master Interfaces
        m_axiss = []    
        for m_count in range(m_count):
            m_axis = AXIStreamInterface(data_width = data_width , id_width = id_width, user_width = user_width, dest_width = dest_width)
            if m_count>9:
                platform.add_extension(m_axis.get_ios("m{}_axis".format(m_count)))
                self.comb += m_axis.connect_to_pads(platform.request("m{}_axis".format(m_count)), mode="master")
            else:
                platform.add_extension(m_axis.get_ios("m0{}_axis".format(m_count)))
                self.comb += m_axis.connect_to_pads(platform.request("m0{}_axis".format(m_count)), mode="master")
            
            m_axiss.append(m_axis)
            
        # AXI STREAM SLAVE -------------------------------------------------------------------------------
        s_axis = AXIStreamInterface(
            data_width      = data_width,
            id_width        = id_width,
            user_width      = user_width,
            dest_width      = dest_width
        )

        # Input AXI
        platform.add_extension(s_axis.get_ios("s_axis"))
        self.comb += s_axis.connect_to_pads(platform.request("s_axis"), mode="slave")
        
        # AXIS-BROADCAST ----------------------------------------------------------------------------------
        self.submodules += AXISBROADCAST(platform,
            m_axis          = m_axiss,
            s_axis          = s_axis,
            m_count         = m_count,
            last_en         = last_en,
            id_en           = id_en,
            dest_en         = dest_en,
            user_en         = user_en
            )

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS BROADCAST CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    
    core_group.add_argument("--m_count",       default=4,      type=int,    help="BROADCAST AXIS Master Interfaces from 2 to 16")
    core_group.add_argument("--data_width",    default=32,     type=int,    help="BROADCAST AXIS interface Data Width from 1 to 4096")
    core_group.add_argument("--last_en",       default=1,      type=int,    help="BROADCAST AXIS tlast signal 0 or 1")
    core_group.add_argument("--id_en",         default=0,      type=int,    help="BROADCAST AXIS tid signal 0 or 1")
    core_group.add_argument("--id_width",      default=8,      type=int,    help="BROADCAST AXIS tid signal width from 1 to 32")
    core_group.add_argument("--dest_en",       default=0,      type=int,    help="BROADCAST AXIS tdest signal 0 or 1")
    core_group.add_argument("--dest_width",    default=8,      type=int,    help="BROADCAST AXIS tdest signal width from 1 to 32")
    core_group.add_argument("--user_en",       default=1,      type=int,    help="BROADCAST AXIS tuser signal 0 or 1")
    core_group.add_argument("--user_width",    default=1,      type=int,    help="BROADCAST AXIS interface User Width from 1 to 4096")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                       help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_broadcast_wrapper",   help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()

    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # AXI Master Interfaces
    m_count_range=range(2,17)
    if args.m_count not in m_count_range:
        logger.error("\nEnter a valid 'm_count' from 2 to 16")
        exit()

    # Data_Width
    data_width_range=range(1,4097)
    if args.data_width not in data_width_range:
        logger.error("\nEnter a valid 'data_width' from 1 to 4096")
        exit()

    # ID Enable
    id_en_range=range(2)
    if args.id_en not in id_en_range:
        logger.error("\nEnter a valid 'id_en' 0 or 1")
        exit()

    # ID Width
    id_width_range=range(1,33)
    if args.id_width not in id_width_range:
        logger.error("\nEnter a valid 'id_width' from 1 to 32")
        exit()

    # Destination Enable
    dest_en_range=range(2)
    if args.dest_en not in dest_en_range:
        logger.error("\nEnter a valid 'dest_en' 0 or 1")
        exit()
        
    # Destination Width
    dest_width_range=range(1,33)
    if args.dest_width not in dest_width_range:
        logger.error("\nEnter a valid 'dest_width' from 1 to 32")
        exit()
        
    # User Enable
    user_en_range=range(2)
    if args.user_en not in user_en_range:
        logger.error("\nEnter a valid 'user_en' 0 or 1")
        exit()
        
    # User Width
    user_width_range=range(1,4097)
    if args.user_width not in user_width_range:
        logger.error("\nEnter a valid 'user_width' from 1 to 4096")
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
    rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="axis_broadcast")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module = AXIBROADCASTWrapper(platform,
        m_count         = args.m_count,
        data_width      = args.data_width,
        last_en         = args.last_en,
        id_en           = args.id_en,
        id_width        = args.id_width,
        dest_en         = args.dest_en,
        dest_width      = args.dest_width,
        user_en         = args.user_en,
        user_width      = args.user_width
        )
    
    # Build
    if args.build:
        rs_builder.generate_verilog(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
