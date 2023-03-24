#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from litex_wrapper.ahb2axi_bridge_litex_wrapper import AHB2AXI4

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface, AXILiteInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("s_ahb_aclk",      0, Pins(1)),
        ("s_ahb_aresetn",   0, Pins(1))]
        
        
def ahb_interface(addr_width,data_width):
    return [
    
        ("ahb_haddr",   	0, Pins(addr_width)),
        ("ahb_hburst",   	0, Pins(3)),
        ("ahb_hmastlock",   0, Pins(1)),
        ("ahb_hprot",   	0, Pins(4)),
        ("ahb_hsize",  	    0, Pins(3)),
        ("ahb_htrans",  	0, Pins(2)),
        ("ahb_hwrite",  	0, Pins(1)),
        ("ahb_hwdata",  	0, Pins(data_width)),
        ("ahb_hsel",  		0, Pins(1)),
        ("ahb_hreadyin",  	0, Pins(1)),
        ("ahb_hnonsec",  	0, Pins(1)),
        ("ahb_hrdata",  	0, Pins(data_width)),
        ("ahb_hreadyout",  	0, Pins(1)),
        ("ahb_hresp",  	    0, Pins(1)),
    ]

# AHB-2-AXI4 Wrapper --------------------------------------------------------------------------------
class AHB2AXI4Wrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width):
        
        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("s_ahb_aclk"))
        self.comb += self.cd_sys.rst.eq(platform.request("s_ahb_aresetn"))

        
        # AXI MASTER PORT
        m_axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width
        )
        
        
        platform.add_extension(m_axi.get_ios("m_axi"))
        self.comb += m_axi.connect_to_pads(platform.request("m_axi"), mode="master")

        # AHB_2_AXI4
        self.submodules.ahb2axi4 = ahb2axi4 = AHB2AXI4(platform, m_axi)
        
        platform.add_extension(ahb_interface(addr_width,data_width))
        self.comb += ahb2axi4.ahb_haddr.eq(platform.request("ahb_haddr"))
        self.comb += ahb2axi4.ahb_hburst.eq(platform.request("ahb_hburst"))
        self.comb += ahb2axi4.ahb_hmastlock.eq(platform.request("ahb_hmastlock"))
        self.comb += ahb2axi4.ahb_hprot.eq(platform.request("ahb_hprot"))
        self.comb += ahb2axi4.ahb_hsize.eq(platform.request("ahb_hsize"))
        self.comb += ahb2axi4.ahb_htrans.eq(platform.request("ahb_htrans"))
        self.comb += ahb2axi4.ahb_hwrite.eq(platform.request("ahb_hwrite"))
        self.comb += ahb2axi4.ahb_hwdata.eq(platform.request("ahb_hwdata"))
        self.comb += ahb2axi4.ahb_hsel.eq(platform.request("ahb_hsel"))
        self.comb += ahb2axi4.ahb_hreadyin.eq(platform.request("ahb_hreadyin"))
        self.comb += ahb2axi4.ahb_hnonsec.eq(platform.request("ahb_hnonsec"))
        
        
        self.comb += platform.request("ahb_hrdata").eq(ahb2axi4.ahb_hrdata)
        self.comb += platform.request("ahb_hreadyout").eq(ahb2axi4.ahb_hreadyout)
        self.comb += platform.request("ahb_hresp").eq(ahb2axi4.ahb_hresp)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AHB_2_AXI4 CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="ahb2axi_bridge", language="System verilog")

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",       type=int,       default=32,         choices=[32, 64],      help="Data Width")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--addr_width",     type=int,       default=33,      choices=range(6, 33),      help="Address Width")
    core_range_param_group.add_argument("--id_width",       type=int,       default=1,      choices=range(1, 33),      help="ID Width")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="ahb2axi4_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()
    
    
    ahb_interface(args.addr_width,args.data_width)

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AHB2AXI4Wrapper(platform,
        data_width = args.data_width,
        addr_width = args.addr_width,
        id_width   = args.id_width
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v1_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
