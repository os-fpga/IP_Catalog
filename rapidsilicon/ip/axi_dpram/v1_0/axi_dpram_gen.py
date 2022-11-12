#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse

from litex_wrapper.axi_dp_ram_litex_wrapper import AXIDPRAM

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_a_ios():
    return [
        ("a_clk", 0, Pins(1)),
        ("a_rst", 0, Pins(1))
    ]
    
def get_clkin_b_ios():
    return [
        ("b_clk", 0, Pins(1)),
        ("b_rst", 0, Pins(1))
    ]
    
# AXI-DPRAM Wrapper --------------------------------------------------------------------------------
class AXIDPRAMWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, a_pip_out, b_pip_out, a_interleave, b_interleave):

        # Clock Domain
        self.clock_domains.cd_sys = ClockDomain()
        
        # AXI
        s_axi_a = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
        )
        
        s_axi_b = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
        )
        
        platform.add_extension(s_axi_a.get_ios("s_axi_a"))
        self.comb += s_axi_a.connect_to_pads(platform.request("s_axi_a"), mode="slave")
        
        platform.add_extension(s_axi_b.get_ios("s_axi_b"))
        self.comb += s_axi_b.connect_to_pads(platform.request("s_axi_b"), mode="slave")
        
        # AXI-DPRAM -------------------------------------------------------------------------------
        self.submodules.dpram = dpram = AXIDPRAM(platform, s_axi_a, s_axi_b, 
            a_pipeline_output   =   a_pip_out, 
            b_pipeline_output   =   b_pip_out, 
            a_interleave        =   a_interleave, 
            b_interleave        =   b_interleave, 
            size                =   (2**addr_width)*(data_width/8)
            )
        
        platform.add_extension(get_clkin_a_ios())
        self.comb += dpram.a_clk.eq(platform.request("a_clk"))
        self.comb += dpram.a_rst.eq(platform.request("a_rst"))
        
        platform.add_extension(get_clkin_b_ios())
        self.comb += dpram.b_clk.eq(platform.request("b_clk"))
        self.comb += dpram.b_rst.eq(platform.request("b_rst"))

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI DPRAM CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from rapidsilicon.lib.common import IP_Builder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",   type=int, default=32, choices=[8, 16, 32, 64, 128, 256], help="DPRAM Data Width.")
    core_group.add_argument("--addr_width",   type=int, default=16, choices=range(8, 17),              help="DPRAM Address Width.")
    core_group.add_argument("--id_width",     type=int, default=8, choices=range(1, 33),              help="DPRAM ID Width.")
    core_group.add_argument("--a_pip_out",    type=int, default=0,  choices=range(2),                  help="DPRAM A Pipeline Output.")
    core_group.add_argument("--b_pip_out",    type=int, default=0,  choices=range(2),                  help="DPRAM B Pipeline Output.")
    core_group.add_argument("--a_interleave", type=int, default=0,  choices=range(2),                  help="DPRAM A Interleave.")
    core_group.add_argument("--b_interleave", type=int, default=0,  choices=range(2),                  help="DPRAM B Interleave.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_dpram_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = AXIDPRAMWrapper(platform,
        data_width   = args.data_width,
        addr_width   = args.addr_width,
        id_width     = args.id_width,
        a_pip_out    = args.a_pip_out,
        b_pip_out    = args.b_pip_out,
        a_interleave = args.a_interleave,
        b_interleave = args.b_interleave,
    )
    
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = IP_Builder(device="gemini", ip_name="axi_dpram", language="verilog")
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
