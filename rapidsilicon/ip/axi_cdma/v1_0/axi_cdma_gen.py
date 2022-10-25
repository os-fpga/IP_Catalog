#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse

from litex_wrapper.axi_cdma_litex_wrapper import AXICDMA

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

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(common_path)

    from common import IP_Builder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",        type=int, default=32, choices=[8, 16, 32, 64, 128, 256], help="DMA Data Width.")
    core_group.add_argument("--addr_width",        type=int, default=16, choices=range(8, 17),              help="DMA Address Width.")
    core_group.add_argument("--id_width",          type=int, default=8,  choices=range(1, 33),              help="DMA ID Width.")
    core_group.add_argument("--axi_max_burst_len", type=int, default=16, choices=range(1,257),              help="DMA AXI burst length.")
    core_group.add_argument("--len_width",         type=int, default=20, choices=range(1,21),               help="DMA AXI Width of length field.")
    core_group.add_argument("--tag_width",         type=int, default=8,  choices=range(1,9),                help="DMA Width of tag field.")
    core_group.add_argument("--enable_unaligned",  type=int, default=0,  choices=range(2),                  help="Support for unaligned transfers.")

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
    module   = AXICDMAWrapper(platform,
        data_width        = args.data_width,
        addr_width        = args.addr_width,
        id_width          = args.id_width,
        axi_max_burst_len = args.axi_max_burst_len,
        len_width         = args.len_width,
        tag_width         = args.tag_width,
        enable_unaligned  = args.enable_unaligned
    )
    
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = IP_Builder(device="gemini", ip_name="axi_cdma", language="verilog")
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
