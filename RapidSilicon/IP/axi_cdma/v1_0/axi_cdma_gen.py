#!/usr/bin/env python3

# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os
import json
import argparse
import shutil
import logging

from litex_sim.axi_cdma_litex_wrapper import AXICDMA

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1))]

def get_axis_ios(addr_width, len_width, tag_width):
    return [
        ("s_axis_desc", 0,
            Subsignal("read_addr",  Pins(addr_width)),
            Subsignal("write_addr", Pins(addr_width)),
            Subsignal("len",        Pins(len_width)),
            Subsignal("tag",        Pins(tag_width)),
            Subsignal("valid",      Pins(1)),
            Subsignal("ready",      Pins(1))
        ),
        
        ("m_axis_desc_status", 0,
            Subsignal("tag",        Pins(tag_width)),
            Subsignal("error",      Pins(4)),
            Subsignal("valid",      Pins(1))
        ),
        
        ("enable",  0, Pins(1))
    ]

# AXI-CDMA Wrapper --------------------------------------------------------------------------------
class AXICDMAWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, axi_max_burst_len, len_width, tag_width, enable_unaligned):
    
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # AXI
        axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width
        )

        platform.add_extension(axi.get_ios("m_axi"))
        self.comb += axi.connect_to_pads(platform.request("m_axi"), mode="master")

        # AXI_CDMA
        self.submodules.cdma = cdma = AXICDMA(platform, axi,
            axi_max_burst_len   =  axi_max_burst_len,
            len_width           =  len_width,
            tag_width           =  tag_width,
            enable_unaligned    =  enable_unaligned
            )

        # Descriptor IOs
        platform.add_extension(get_axis_ios(addr_width, len_width, tag_width))
        s_desc_pads = platform.request("s_axis_desc")
        self.comb += [
            cdma.s_axis_desc_read_addr.eq(s_desc_pads.read_addr),
            cdma.s_axis_desc_write_addr.eq(s_desc_pads.write_addr),
            cdma.s_axis_desc_len.eq(s_desc_pads.len),
            cdma.s_axis_desc_tag.eq(s_desc_pads.tag),
            cdma.s_axis_desc_valid.eq(s_desc_pads.valid),
            s_desc_pads.ready.eq(cdma.s_axis_desc_ready)
        ]
        
        m_desc_pads = platform.request("m_axis_desc_status")
        self.comb += [
            m_desc_pads.tag.eq(cdma.m_axis_desc_status_tag),
            m_desc_pads.error.eq(cdma.m_axis_desc_status_error),
            m_desc_pads.valid.eq(cdma.m_axis_desc_status_valid),
        ]
        
        self.comb += cdma.enable.eq(platform.request("enable"))

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI CDMA CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",         default=32,     type=int,    help="DMA Data Width 8,16,32,64,128,256")
    core_group.add_argument("--addr_width",         default=16,     type=int,    help="DMA Address Width 8 - 16")
    core_group.add_argument("--id_width",           default=8,      type=int,    help="DMA ID Width from 1 - 32")
    core_group.add_argument("--axi_max_burst_len",  default=16,     type=int,    help="DMA AXI burst length from 1 to 256 ")
    core_group.add_argument("--len_width",          default=20,     type=int,    help="DMA AXI Width of length field from 1 to 20")
    core_group.add_argument("--tag_width",          default=8,      type=int,    help="DMA Width of tag field from 1 to 8")
    core_group.add_argument("--enable_unaligned",   default=0,      type=int,    help="Support for unaligned transfers 0 or 1")

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

    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Data_Width
    data_width_param=[8, 16, 32, 64, 128, 256]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s", data_width_param)
        exit()
    
    # Address Width
    addr_range=range(8, 17)
    if args.addr_width not in addr_range:
        logger.error("\nEnter a valid 'addr_width' from 8 to 16")
        exit()

    # ID_Width
    id_range=range(1, 33)
    if args.id_width not in id_range:
        logger.error("\nEnter a valid 'id_width' from 1 to 32")
        exit()
    
    # axi_max_burst_len_range
    axi_max_burst_len_range=range(1,257)
    if args.axi_max_burst_len not in axi_max_burst_len_range:
        logger.error("\nEnter a valid 'a_intaxi_max_burst_lenerleave' from 0 to 256")
        exit()

    # len_width
    len_width_range=range(1,21)
    if args.len_width not in len_width_range:
        logger.error("\nEnter a valid 'len_width' from 1 to 20")
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


    jsonlogger = logging.getLogger("JSON")
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        jsonlogger.info(json.dumps(vars(args), indent=4))

    # Remove build extension when specified.
    args.build_name = os.path.splitext(args.build_name)[0]

    # Build Project Directory ----------------------------------------------------------------------
    if args.build:
        # Build Path
        build_path = os.path.join(args.build_dir, 'rapidsilicon/ip/axi_cdma/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "axi_cdma_gen.py"))
        
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
    module = AXICDMAWrapper(platform,
        data_width          = args.data_width,
        addr_width          = args.addr_width,
        id_width            = args.id_width,
        axi_max_burst_len   = args.axi_max_burst_len,
        len_width           = args.len_width,
        tag_width           = args.tag_width,
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
