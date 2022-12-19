#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse
import math

from litex_wrapper.axi_crossbar_litex_wrapper import AXICROSSBAR

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("ACLK",    0, Pins(1)),
        ("ARESET",  0, Pins(1)),
    ]
# Slave interface clock/reset signals
def get_clkin_ios_s(i):
    return [
        ("s{}_axi_aclk".format(i),     0, Pins(1)),
        ("s{}_axi_areset".format(i),  0, Pins(1)),
    ]

# Master intrerface clock/reset signals
def get_clkin_ios_m(j):
    return [
        ("m{}_axi_aclk".format(j),     0, Pins(1)),
        ("m{}_axi_areset".format(j),  0, Pins(1)),
    ]

# AXI CROSSBAR Wrapper ----------------------------------------------------------------------------------
class AXICROSSBARWrapper(Module):
    def __init__(self, platform, m_count, s_count ,data_width, addr_width, s_id_width, aw_user_width, w_user_width, b_user_width, ar_user_width, r_user_width,
                aw_user_en, w_user_en, b_user_en, ar_user_en, r_user_en,sync_stages,fifo_depth,bram):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("ACLK"))
        self.comb += self.cd_sys.rst.eq(platform.request("ARESET"))

        # CLK for Slave Interfaces
        for i in range (s_count):
            platform.add_extension(get_clkin_ios_s(i))
            self.clock_domains.cd_sys  = ClockDomain("s{}_axi_aclk".format(i))
            self.comb += self.cd_sys.clk.eq(platform.request("s{}_axi_aclk".format(i)))
            self.clock_domains.cd_sys  = ClockDomain("s{}_axi_areset".format(i))
            self.comb += self.cd_sys.rst.eq(platform.request("s{}_axi_areset".format(i)))

        # CLK for Master Interfaces
        for j in range (m_count):
            platform.add_extension(get_clkin_ios_m(j))
            self.clock_domains.cd_sys  = ClockDomain("m{}_axi_aclk".format(j))
            self.comb += self.cd_sys.clk.eq(platform.request("m{}_axi_aclk".format(j)))
            self.clock_domains.cd_sys  = ClockDomain("m{}_axi_areset".format(j))
            self.comb += self.cd_sys.rst.eq(platform.request("m{}_axi_areset".format(j)))

        # Slave Interfaces
        s_axis = []
        for s_count in range(s_count):
            s_axi = AXIInterface(data_width = data_width , address_width = addr_width, id_width = s_id_width, aw_user_width = aw_user_width,
            w_user_width = w_user_width, b_user_width = b_user_width, ar_user_width = ar_user_width, r_user_width = r_user_width)
            if s_count>9:
                platform.add_extension(s_axi.get_ios("s{}_axi".format(s_count)))
                self.comb += s_axi.connect_to_pads(platform.request("s{}_axi".format(s_count)), mode="slave")
            else:
                platform.add_extension(s_axi.get_ios("s0{}_axi".format(s_count)))
                self.comb += s_axi.connect_to_pads(platform.request("s0{}_axi".format(s_count)), mode="slave")
                
            s_axis.append(s_axi)
        
        # Master Interfaces 
        if s_count<2:
            m_id_width = s_id_width
        else:
            m_id_width = (s_id_width+(math.ceil(math.log2(s_count)))) 
            
        m_axis = []  
        for m_count in range(m_count):
            m_axi = AXIInterface(data_width = data_width , address_width = addr_width, id_width = m_id_width, aw_user_width = aw_user_width,
            w_user_width = w_user_width, b_user_width = b_user_width, ar_user_width = ar_user_width, r_user_width = r_user_width)
            if m_count>9:
                platform.add_extension(m_axi.get_ios("m{}_axi".format(m_count)))
                self.comb += m_axi.connect_to_pads(platform.request("m{}_axi".format(m_count)), mode="master")
            else:
                platform.add_extension(m_axi.get_ios("m0{}_axi".format(m_count)))
                self.comb += m_axi.connect_to_pads(platform.request("m0{}_axi".format(m_count)), mode="master")
            
            m_axis.append(m_axi)
            
        # AXI CROSSBAR
        self.submodules.axi_crossbar = AXICROSSBAR(platform,
            s_axi               = s_axis,
            m_axi               = m_axis,
            s_count             = s_count,
            m_count             = m_count,
            aw_user_en          = aw_user_en,
            w_user_en           = w_user_en,
            b_user_en           = b_user_en,
            ar_user_en          = ar_user_en,
            r_user_en           = r_user_en,
            sync_stages         = sync_stages,
            fifo_depth          = fifo_depth,
            bram                = bram,
            )

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI_2_AXILITE CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    dep_dict = {
                'aw_user_width' :   'aw_user_en',
                'w_user_width'  :   'w_user_en',
                'b_user_width'  :   'b_user_en',
                'ar_user_width' :   'ar_user_en',
                'r_user_width'  :   'r_user_en',
    }            

   # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_crossbar", language="verilog")

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",    type=int,      default=32,     choices=[8, 16, 32, 64, 128, 256],  help="AXI Data Width.")
    core_fix_param_group.add_argument("--addr_width",    type=int,      default=32,     choices=[32, 64],                   help="AXI Address Width.")
    core_fix_param_group.add_argument("--sync_stages",   type=int,      default=2,      choices=[3, 4, 5, 6, 7, 8],         help="Number of Sync Stages")
    core_fix_param_group.add_argument("--fifo_depth",    type=int,      default=3,      choices=[4, 5, 6, 7, 8],            help="FIFO Depth")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--aw_user_en",    type=bool,    default=True,      help="AW-Channel User Enable.")
    core_bool_param_group.add_argument("--w_user_en",     type=bool,    default=False,     help="W-Channel User Enable.")
    core_bool_param_group.add_argument("--b_user_en",     type=bool,    default=False,     help="B-Channel User Enable.")
    core_bool_param_group.add_argument("--ar_user_en",    type=bool,    default=True,      help="AR-Channel User Enable.")
    core_bool_param_group.add_argument("--r_user_en",     type=bool,    default=False,     help="R-Channel User Enable.")  
    core_bool_param_group.add_argument("--bram",          type=bool,    default=False,     help="Memory type")       


    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--m_count",            type=int,       default=4,      choices=range(2,17),         help="Crossbar Master Interfaces.")
    core_range_param_group.add_argument("--s_count",            type=int,       default=4,      choices=range(1,17),         help="Crossbar SLAVE Interfaces.")
    core_range_param_group.add_argument("--s_id_width",         type=int,       default=8,      choices=range(1, 9),         help="AXI SLAVE ID Width.")
    core_range_param_group.add_argument("--aw_user_width",      type=int,       default=1,      choices=range(1, 1025),      help="AW-Channel User Width.")
    core_range_param_group.add_argument("--w_user_width",       type=int,       default=1,      choices=range(1, 1025),      help="W-Channel User Width.")
    core_range_param_group.add_argument("--b_user_width",       type=int,       default=1,      choices=range(1, 1025),      help="B-Channel User Width.")
    core_range_param_group.add_argument("--ar_user_width",      type=int,       default=1,      choices=range(1, 1025),      help="AR-Channel User Width.")
    core_range_param_group.add_argument("--r_user_width",       type=int,       default=1,      choices=range(1, 1025),      help="R-Channel User Width.")

  

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                       help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_crossbar_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = AXICROSSBARWrapper(platform,
        m_count       = args.m_count,
        s_count       = args.s_count,
        data_width    = args.data_width,
        addr_width    = args.addr_width,
        s_id_width    = args.s_id_width,
        aw_user_en    = args.aw_user_en,
        aw_user_width = args.aw_user_width,
        w_user_en     = args.w_user_en,
        w_user_width  = args.w_user_width,
        b_user_en     = args.b_user_en,
        b_user_width  = args.b_user_width,
        ar_user_en    = args.ar_user_en,
        ar_user_width = args.ar_user_width,
        r_user_en     = args.r_user_en,
        r_user_width  = args.r_user_width,
        sync_stages   = args.sync_stages,
        fifo_depth    = args.fifo_depth,
        bram          = args.bram,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
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