#!/usr/bin/env python3

# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os
import json
import argparse
import shutil
import logging

from litex_sim.axi_dma_litex_wrapper import AXIDMA

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface

from litex.soc.interconnect.axi import AXIStreamInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1))
    ]

def get_axis_ios(axi_addr_width, len_width, axi_id_width, tag_width, axis_dest_width, axis_user_width):
    return [
        ("s_axis_read_desc", 0,
            Subsignal("addr",   Pins(axi_addr_width)), 
            Subsignal("len",    Pins(len_width)),
            Subsignal("tag",    Pins(tag_width)), 
            Subsignal("id",     Pins(axi_id_width)), 
            Subsignal("dest",   Pins(axis_dest_width)), 
            Subsignal("user",   Pins(axis_user_width)),
            Subsignal("valid",  Pins(1)),
            Subsignal("ready",  Pins(1))
        ),
        
        ("m_axis_read_desc_status", 0,
            Subsignal("tag",    Pins(tag_width)), 
            Subsignal("error",  Pins(4)),
            Subsignal("valid",  Pins(1))
        ),
        
        ("s_axis_write_desc", 0,
            Subsignal("addr",   Pins(axi_addr_width)), 
            Subsignal("len",    Pins(len_width)), 
            Subsignal("tag",    Pins(tag_width)), 
            Subsignal("valid",  Pins(1)),
            Subsignal("ready",  Pins(1))
        ),
        
        ("m_axis_write_desc_status", 0,
            Subsignal("len",    Pins(len_width)), 
            Subsignal("tag",    Pins(tag_width)), 
            Subsignal("id",     Pins(axi_id_width)), 
            Subsignal("dest",   Pins(axis_dest_width)), 
            Subsignal("user",   Pins(axis_user_width)), 
            Subsignal("error",  Pins(4)),
            Subsignal("valid",  Pins(1))
        ),
        
        ("read_enable",     0, Pins(1)),
        ("write_enable",    0, Pins(1)),
        ("write_abort",     0, Pins(1))
    ]
    
# AXI-DMA Wrapper --------------------------------------------------------------------------------
class AXIDMAWrapper(Module):
    def __init__(self, platform, axi_data_width, axi_addr_width, axi_id_width, axi_max_burst_len, 
                axis_last_enable, axis_id_enable, axis_id_width, axis_dest_enable, axis_dest_width,
                axis_user_enable, axis_user_width, len_width, tag_width, enable_sg, enable_unaligned):
        
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI
        axi = AXIInterface(
            data_width      = axi_data_width,
            address_width   = axi_addr_width,
            id_width        = axi_id_width,
        )
        axis = AXIStreamInterface(
            data_width      = axi_data_width,
            user_width      = axis_user_width,
            dest_width      = axis_dest_width,
            id_width        = axis_id_width
        )
        
        platform.add_extension(axi.get_ios("m_axi"))
        self.comb += axi.connect_to_pads(platform.request("m_axi"), mode="master")
        
        platform.add_extension(axis.get_ios("m_axis"))
        self.comb += axis.connect_to_pads(platform.request("m_axis"), mode="master")
        
        platform.add_extension(axis.get_ios("s_axis"))
        self.comb += axis.connect_to_pads(platform.request("s_axis"), mode="slave")
        
        # AXI_DMA
        self.submodules.dma = dma = AXIDMA(platform, 
            m_axi               = axi, 
            m_axis              = axis,
            s_axis              = axis, 
            axi_max_burst_len   = axi_max_burst_len,
            axis_last_enable    = axis_last_enable,
            axis_id_enable      = axis_id_enable,
            axis_dest_enable    = axis_dest_enable,
            axis_user_enable    = axis_user_enable,            
            len_width           = len_width,
            tag_width           = tag_width,
            enable_sg           = enable_sg,
            enable_unaligned    = enable_unaligned
            )
        
        # Descriptor IOs
        platform.add_extension(get_axis_ios(axi_addr_width, len_width, axi_id_width, tag_width, axis_dest_width, axis_user_width))
        s_desc_pads = platform.request("s_axis_read_desc")
        self.comb += [
            dma.s_axis_read_desc_addr.eq(s_desc_pads.addr),
            dma.s_axis_read_desc_len.eq(s_desc_pads.len),
            dma.s_axis_read_desc_tag.eq(s_desc_pads.tag),
            dma.s_axis_read_desc_id.eq(s_desc_pads.id),
            dma.s_axis_read_desc_dest.eq(s_desc_pads.dest),
            dma.s_axis_read_desc_user.eq(s_desc_pads.user),
            dma.s_axis_read_desc_valid.eq(s_desc_pads.valid),
            s_desc_pads.ready.eq(dma.s_axis_read_desc_ready)
        ]
        
        m_desc_pads = platform.request("m_axis_read_desc_status")
        self.comb += [
            m_desc_pads.tag.eq(dma.m_axis_read_desc_status_tag),
            m_desc_pads.error.eq(dma.m_axis_read_desc_status_error),
            m_desc_pads.valid.eq(dma.m_axis_read_desc_status_valid),
        ]
        
        s_desc_pads = platform.request("s_axis_write_desc")
        self.comb += [
            dma.s_axis_write_desc_addr.eq(s_desc_pads.addr),
            dma.s_axis_write_desc_len.eq(s_desc_pads.len),
            dma.s_axis_write_desc_tag.eq(s_desc_pads.tag),
            dma.s_axis_write_desc_valid.eq(s_desc_pads.valid),
            s_desc_pads.ready.eq(dma.s_axis_write_desc_ready)
        ]
        
        s_desc_pads = platform.request("m_axis_write_desc_status")
        self.comb += [
            s_desc_pads.len.eq(dma.m_axis_write_desc_status_len),
            s_desc_pads.tag.eq(dma.m_axis_write_desc_status_tag),
            s_desc_pads.id.eq(dma.m_axis_write_desc_status_id),
            s_desc_pads.dest.eq(dma.m_axis_write_desc_status_dest),
            s_desc_pads.user.eq(dma.m_axis_write_desc_status_user),
            s_desc_pads.error.eq(dma.m_axis_write_desc_status_error),
            s_desc_pads.valid.eq(dma.m_axis_write_desc_status_valid),
        ]
        
        self.comb += dma.read_enable.eq(platform.request("read_enable"))
        self.comb += dma.write_enable.eq(platform.request("write_enable"))
        self.comb += dma.write_abort.eq(platform.request("write_abort"))


# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI DMA CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--axi_data_width",         default=32,     type=int,    help="DMA Data Width 8,16,32,64,128,256")
    core_group.add_argument("--axi_addr_width",         default=16,     type=int,    help="DMA Address Width from 8 to 16")
    core_group.add_argument("--axi_id_width",           default=8,      type=int,    help="DMA ID Width from 1 to 32")
    core_group.add_argument("--axi_max_burst_len",      default=16,     type=int,    help="DMA AXI burst length from 1 to 256")
    core_group.add_argument("--axis_last_enable",       default=1,      type=int,    help="DMA AXI stream tlast 0 or 1")    
    core_group.add_argument("--axis_id_enable",         default=0,      type=int,    help="DMA AXI stream tid 0 or 1")    
    core_group.add_argument("--axis_id_width",          default=8,      type=int,    help="DMA AXI stream tid width from 1 to 32")    
    core_group.add_argument("--axis_dest_enable",       default=0,      type=int,    help="DMA AXI stream tdest 0 or 1")
    core_group.add_argument("--axis_dest_width",        default=8,      type=int,    help="DMA AXI stream tdest width  from 1 to 8")
    core_group.add_argument("--axis_user_enable",       default=1,      type=int,    help="DMA AXI stream tuser 0 or 1")
    core_group.add_argument("--axis_user_width",        default=1,      type=int,    help="DMA AXIS User Width from 1 to 8")    
    core_group.add_argument("--len_width",              default=20,     type=int,    help="DMA AXI Width of length field from 1 to 20")
    core_group.add_argument("--tag_width",              default=8,      type=int,    help="DMA Width of tag field from 1 to 8")
    core_group.add_argument("--enable_sg",              default=0,      type=int,    help="Support for scatter/gather DMA 0 or 1")    
    core_group.add_argument("--enable_unaligned",       default=0,      type=int,    help="Support for unaligned transfers 0 or 1")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_dma_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()

    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Data_Width
    data_width_param=[8, 16, 32, 64, 128, 256]
    if args.axi_data_width not in data_width_param:
        logger.error("\nEnter a valid 'axi_data_width'\n %s", data_width_param)
        exit()
    
    # Address Width
    addr_range=range(8, 17)
    if args.axi_addr_width not in addr_range:
        logger.error("\nEnter a valid 'axi_addr_width' from 8 to 16")
        exit()

    # ID_Width
    id_range=range(1, 33)
    if args.axi_id_width not in id_range:
        logger.error("\nEnter a valid 'axi_id_width' from 1 to 32")
        exit()
    
    # axis_user_width_range
    axis_user_width_range=range(1,9)
    if args.axis_user_width not in axis_user_width_range:
        logger.error("\nEnter a valid 'axis_user_width' from 1 to 8")
        exit()

    # axis_id_width_range
    axis_id_width_range=range(1,33)
    if args.axis_id_width not in axis_id_width_range:
        logger.error("\nEnter a valid 'axis_id_width' from 1 to 32")
        exit()

    # axi_max_burst_len_range
    axi_max_burst_len_range=range(1,257)
    if args.axi_max_burst_len not in axi_max_burst_len_range:
        logger.error("\nEnter a valid 'a_intaxi_max_burst_lenerleave' from 1 to 256")
        exit()

    # axis_last_enable_range
    axis_last_enable_range=range(2)
    if args.axis_last_enable not in axis_last_enable_range:
        logger.error("\nEnter a valid 'axis_last_enable' 0 or 1")
        exit()

    # AXIS_ID_ENABLE
    axis_id_enable_range=range(2)
    if args.axis_id_enable not in axis_id_enable_range:
        logger.error("\nEnter a valid 'axis_id_enable' 0 or 1")
        exit()

    # AXIS_DEST_ENABLE
    axis_dest_enable_range=range(2)
    if args.axis_dest_enable not in axis_dest_enable_range:
        logger.error("\nEnter a valid 'axis_dest_enable' 0 or 1")
        exit()

    # AXIS_DEST_WIDTH
    axis_dest_width_range=range(1,9)
    if args.axis_dest_width not in axis_dest_width_range:
        logger.error("\nEnter a valid 'axis_dest_width' from 1 to 8")
        exit()

    # len_width
    len_width_range=range(1,21)
    if args.len_width not in len_width_range:
        logger.error("\nEnter a valid 'len_width' from 1 to 20")
        exit()

    # AXIS_USER_ENABLE
    axis_user_enable_range=range(2)
    if args.axis_user_enable not in axis_user_enable_range:
        logger.error("\nEnter a valid 'axis_user_enable' 0 or 1")
        exit()

    # ENABLE_SG
    enable_sg_range=range(2)
    if args.enable_sg not in enable_sg_range:
        logger.error("\nEnter a valid 'enable_sg' 0 or 1")
        exit()

    # TAG_WIDTH
    tag_width_range=range(1,9)
    if args.tag_width not in tag_width_range:
        logger.error("\nEnter a valid 'tag_width' from 1 to 8")
        exit()

    # ENABLE_UNALIGNED
    enable_unaligned_range=range(2)
    if args.enable_unaligned not in enable_unaligned_range:
        logger.error("\nEnter a valid 'enable_unaligned' 0 or 1")
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
    if args.build:
        # Build Path
        build_path = os.path.join(args.build_dir, 'rapidsilicon/ip/axi_dma/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "axi_dma_gen.py"))
        
        if not os.path.exists(build_path):
            os.makedirs(build_path)
            shutil.copy(gen_path, build_path)

        # Litex_sim Path
        litex_sim_path = os.path.join(build_path, "litex_sim")
        if not os.path.exists(litex_sim_path):    
            os.makedirs(litex_sim_path)

        # Simulation Path
        sim_path = os.path.join(build_path, "sim")
        if not os.path.exists(sim_path):    
            os.makedirs(sim_path)

        # Source Path
        src_path = os.path.join(build_path, "src")
        if not os.path.exists(src_path):    
            os.makedirs(src_path) 

        # Synthesis Path
        synth_path = os.path.join(build_path, "synth")
        if not os.path.exists(synth_path):    
            os.makedirs(synth_path) 

        # Design Path
        design_path = os.path.join("../src", (args.build_name + ".v")) 

        # Copy RTL from Source to Destination
        rtl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "src")        
        rtl_files = os.listdir(rtl_path)
        for file_name in rtl_files:
            full_file_path = os.path.join(rtl_path, file_name)
            if os.path.isfile(full_file_path):
                shutil.copy(full_file_path, src_path)

        # Copy litex_sim Data from Source to Destination  
        litex_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "litex_sim")      
        litex_files = os.listdir(litex_path)
        for file_name in litex_files:
            full_file_path = os.path.join(litex_path, file_name)
            if os.path.isfile(full_file_path):
                shutil.copy(full_file_path, litex_sim_path)

        
        # TCL File Content        
        tcl = []
        # Create Design.
        tcl.append(f"create_design {args.build_name}")
        # Set Device.
        tcl.append(f"target_device {'GEMINI'}")
        # Add Include Path.
        tcl.append(f"add_library_path {'../src'}")
        # Add Sources.
#        for f, typ, lib in file_name:
        tcl.append(f"add_design_file {design_path}")
        # Set Top Module.
        tcl.append(f"set_top_module {args.build_name}")
        # Add Timings Constraints.
#        tcl.append(f"add_constraint_file {args.build_name}.sdc")
        # Run.
        tcl.append("synthesize")

        # Generate .tcl file
        tcl_path = os.path.join(synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module = AXIDMAWrapper(platform,
        axi_data_width      = args.axi_data_width,
        axi_addr_width      = args.axi_addr_width,
        axi_id_width        = args.axi_id_width,
        axi_max_burst_len   = args.axi_max_burst_len,
        axis_last_enable    = args.axis_last_enable,
        axis_id_enable      = args.axis_id_enable,
        axis_id_width       = args.axis_id_width,
        axis_dest_enable    = args.axis_dest_enable,
        axis_dest_width     = args.axis_dest_width,
        axis_user_enable    = args.axis_user_enable,
        axis_user_width     = args.axis_user_width,
        len_width           = args.len_width,
        tag_width           = args.tag_width,
        enable_sg           = args.enable_sg,
        enable_unaligned    = args.enable_unaligned
        )
    
    # Build
    if args.build:
        platform.build(module,
            build_dir    = "litex_build",
            build_name   = args.build_name,
            run          = False,
            regular_comb = False
        )
        shutil.copy(f"litex_build/{args.build_name}.v", src_path)
        shutil.rmtree("litex_build")
        
        # TimeScale Addition to Wrapper
        wrapper = os.path.join(src_path, f'{args.build_name}.v')
        f = open(wrapper, "r")
        content = f.readlines()
        content.insert(14, '`timescale 1ns / 1ps\n')
        f = open(wrapper, "w")
        content = "".join(content)
        f.write(str(content))
        f.close()

if __name__ == "__main__":
    main()
