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

from litex_sim.axis_fifo_litex_wrapper import AXISTREAMFIFO

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIStreamInterface

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]

def get_status_ios():
    return [
        ("status", 0,
            Subsignal("overflow",   Pins(1)),
            Subsignal("bad_frame",  Pins(1)),
            Subsignal("good_frame", Pins(1)),
            Subsignal("full",       Pins(1)),
            Subsignal("empty",      Pins(1))    
        )
    ]

# AXI_STREAM_FIFO Wrapper ----------------------------------------------------------------------------------
class AXISTREAMFIFOWrapper(Module):
    def __init__(self, platform, depth, data_width, last_en, id_en, id_width, 
                dest_en, dest_width, user_en, user_width, pip_out, frame_fifo,
                drop_bad_frame, drop_when_full
                ):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI STREAM -------------------------------------------------------------------------------
        s_axis = AXIStreamInterface(
            data_width = data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width
        )
        
        m_axis = AXIStreamInterface(
            data_width = data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width
        )
        # Input AXI
        platform.add_extension(s_axis.get_ios("s_axis"))
        self.comb += s_axis.connect_to_pads(platform.request("s_axis"), mode="slave")
        
        # Output AXI
        platform.add_extension(m_axis.get_ios("m_axis"))
        self.comb += m_axis.connect_to_pads(platform.request("m_axis"), mode="master")
        
        # AXIS-FIFO ----------------------------------------------------------------------------------
        self.submodules.fifo = fifo = AXISTREAMFIFO(platform,
            m_axis          = m_axis,
            s_axis          = s_axis,
            depth           = depth, 
            last_en         = last_en,
            id_en           = id_en,
            dest_en         = dest_en,
            user_en         = user_en,
            pip_out         = pip_out,
            frame_fifo      = frame_fifo,
            drop_bad_frame  = drop_bad_frame,
            drop_when_full  = drop_when_full
            )
        
        # FIFO Status Signals ----------------------------------------------------------------------
        platform.add_extension(get_status_ios())
        fifo_pads = platform.request("status")
        self.comb += [
            fifo_pads.overflow.eq(fifo.status_overflow),
            fifo_pads.bad_frame.eq(fifo.status_bad_frame),
            fifo_pads.good_frame.eq(fifo.status_good_frame),
            fifo_pads.full.eq(fifo.status_full),
            fifo_pads.empty.eq(fifo.status_empty)
        ]

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS FIFO CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--depth",          default=4096,     type=int,         help="FIFO Depth 8,16,32,64,...,32768")
    core_group.add_argument("--data_width",     default=8,        type=int,         help="FIFO Data Width from 1 to 4096")
    core_group.add_argument("--last_en",        default=1,        type=int,         help="FIFO Last Enable 0 or 1")
    core_group.add_argument("--id_en",          default=0,        type=int,         help="FIFO ID Enable 0 or 1")
    core_group.add_argument("--id_width",       default=8,        type=int,         help="FIFO ID Width from 1 to 32")
    core_group.add_argument("--dest_en",        default=0,        type=int,         help="FIFO Destination Enable 0 or 1")
    core_group.add_argument("--dest_width",     default=8,        type=int,         help="FIFO Destination Width from 1 to 32")
    core_group.add_argument("--user_en",        default=1,        type=int,         help="FIFO User Enable 0 or 1")
    core_group.add_argument("--user_width",     default=1,        type=int,         help="FIFO User Width from 1 to 4096")
    core_group.add_argument("--pip_out",        default=2,        type=int,         help="FIFO Pipeline Output from 0 to 2")
    core_group.add_argument("--frame_fifo",     default=0,        type=int,         help="FIFO Frame 0 or 1")
    core_group.add_argument("--drop_bad_frame", default=0,        type=int,         help="FIFO Drop Bad Frame 0 or 1")
    core_group.add_argument("--drop_when_full", default=0,        type=int,         help="FIFO Drop Frame When Full 0 or 1")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_fifo_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Depth
    depth_param=[8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
    if args.depth not in depth_param:
        logger.error("\nEnter a valid 'depth'\n %s", depth_param)
        exit()

    # Data_Width
    data_width_range=range(1,4097)
    if args.data_width not in data_width_range:
        logger.error("\nEnter a valid 'data_width' from 1 to 4096")
        exit()
    
    # Last Enable
    last_en_range=range(2)
    if args.last_en not in last_en_range:
        logger.error("\nEnter a valid 'last_en' 0 or 1")
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
        
    # Pipeline_Output
    pip_range=range(3)
    if args.pip_out not in pip_range:
        logger.error("\nEnter a valid 'pip_out' from 0 to 2")
        exit()
        
    # Frame FIFO
    frame_fifo_range=range(2)
    if args.frame_fifo not in frame_fifo_range:
        logger.error("\nEnter a valid 'frame_fifo' 0 or 1")
        exit()
        
    # Drop Bad Frame
    drop_bad_frame_range=range(2)
    if args.drop_bad_frame not in drop_bad_frame_range:
        logger.error("\nEnter a valid 'drop_bad_frame' 0 or 1")
        exit()
        
    # Drop When Full
    drop_when_full_range=range(2)
    if args.drop_when_full not in drop_when_full_range:
        logger.error("\nEnter a valid 'drop_when_full' 0 or 1")
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
    rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="axis_fifo")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXISTREAMFIFOWrapper(platform,
        depth           = args.depth,
        data_width      = args.data_width,
        last_en         = args.last_en,
        id_en           = args.id_en,
        id_width        = args.id_width,
        dest_en         = args.dest_en,
        dest_width      = args.dest_width,
        user_en         = args.user_en,
        user_width      = args.user_width,
        pip_out         = args.pip_out,
        frame_fifo      = args.frame_fifo,
        drop_bad_frame  = args.drop_bad_frame,
        drop_when_full  = args.drop_when_full
    )

    # Build
    if args.build:
        rs_builder.generate_verilog(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
