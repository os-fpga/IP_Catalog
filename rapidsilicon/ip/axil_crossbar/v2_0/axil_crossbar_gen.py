#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from litex_wrapper.axil_crossbar_litex_wrapper import AXILITECROSSBAR

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("ACLK",  0, Pins(1)),
        ("ARESET",  0, Pins(1)),
    ]


def get_clkin_ios_s(i):
    return [
        ("s{}_axi_aclk".format(i),  0, Pins(1)),
        ("s{}_axi_areset".format(i),  0, Pins(1)),
    ]
def get_clkin_ios_m(j):
    return [
        ("m{}_axi_aclk".format(j),  0, Pins(1)),
        ("m{}_axi_areset".format(j),  0, Pins(1)),
    ]


# AXI LITE CROSSBAR ----------------------------------------------------------------------------------
class AXILITECROSSBARWrapper(Module):
    def __init__(self, platform, s_count, m_count, data_width, addr_width,bram):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("ACLK"))
        self.comb += self.cd_sys.rst.eq(platform.request("ARESET"))


        for i in range (s_count):
            platform.add_extension(get_clkin_ios_s(i))
            self.clock_domains.cd_sys  = ClockDomain("s{}_axi_aclk".format(i))
            self.comb += self.cd_sys.clk.eq(platform.request("s{}_axi_aclk".format(i)))
            self.clock_domains.cd_sys  = ClockDomain("s{}_axi_areset".format(i))
            self.comb += self.cd_sys.rst.eq(platform.request("s{}_axi_areset".format(i)))

        for j in range (m_count):
            platform.add_extension(get_clkin_ios_m(j))
            self.clock_domains.cd_sys  = ClockDomain("m{}_axi_aclk".format(j))
            self.comb += self.cd_sys.clk.eq(platform.request("m{}_axi_aclk".format(j)))
            self.clock_domains.cd_sys  = ClockDomain("m{}_axi_areset".format(j))
            self.comb += self.cd_sys.rst.eq(platform.request("m{}_axi_areset".format(j)))

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
            m_count     = m_count,
            bram        = bram,
            )

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI_LITE_CROSSBAR_CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axil_crossbar", language="verilog")

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",    type=int,      default=32,     choices=[8, 16, 32, 64, 128, 256],  help="Crossbar Data Width.")
    core_fix_param_group.add_argument("--addr_width",    type=int,      default=32,     choices=[32, 64, 128, 256],         help="Crossbar Address Width.")


    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--bram",     type=bool,     default=True,      help="Memory type")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--m_count",     type=int,      default=4,       choices=range(1,5),               help="Crossbar Master Interfaces.")
    core_range_param_group.add_argument("--s_count",     type=int,      default=4,       choices=range(1,5),               help="Crossbar Slave Interfaces.")
    
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
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module     = AXILITECROSSBARWrapper(platform,
        m_count     = args.m_count,
        s_count     = args.s_count,
        data_width  = args.data_width,
        addr_width  = args.addr_width,
        bram        = args.bram,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v2_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
