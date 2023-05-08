#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from litex_wrapper.axis_broadcast_litex_wrapper import AXISBROADCAST

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
            dest_width      = dest_width,
            keep_width      = int((data_width+7)/8)
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

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports    :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axis_broadcast", language="verilog")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--last_en",    type=bool,       default=True,       help="BROADCAST AXIS tlast signal width.")
    core_bool_param_group.add_argument("--id_en",      type=bool,       default=True,       help="BROADCAST AXIS tid signal width.")
    core_bool_param_group.add_argument("--dest_en",    type=bool,       default=True,       help="BROADCAST AXIS tdest signal width.")
    core_bool_param_group.add_argument("--user_en",    type=bool,       default=True,       help="BROADCAST AXIS tuser signal width.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--m_count",        type=int,       default=4,      choices=range(2,17),        help="BROADCAST AXIS Master Interfaces.")
    core_range_param_group.add_argument("--data_width",     type=int,       default=32,     choices=range(1,1025),      help="BROADCAST AXIS interface Data Width.")
    core_range_param_group.add_argument("--id_width",       type=int,       default=8,      choices=range(1, 33),       help="BROADCAST AXIS tid signal width.")
    core_range_param_group.add_argument("--dest_width",     type=int,       default=8,      choices=range(1, 33),       help="BROADCAST AXIS tdest signal width.")
    core_range_param_group.add_argument("--user_width",     type=int,       default=1,      choices=range(1, 4097),     help="BROADCAST AXIS interface User Width.")

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

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

        if (args.id_en == False):
            dep_dict.update({
                'id_width' :   'True',
            })
        else:
            dep_dict.update({
                'id_width' :   'False',
            })
        if (args.dest_en == False):
            dep_dict.update({
                'dest_width' :   'True',
            })
        else:
            dep_dict.update({
                'dest_width' :   'False',
            })
        if (args.user_en == False):
            dep_dict.update({
                'user_width' :   'True',
            })
        else:
            dep_dict.update({
                'user_width' :   'False',
            })        

        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXIBROADCASTWrapper(platform,
        m_count    = args.m_count,
        data_width = args.data_width,
        last_en    = args.last_en,
        id_en      = args.id_en,
        id_width   = args.id_width,
        dest_en    = args.dest_en,
        dest_width = args.dest_width,
        user_en    = args.user_en,
        user_width = args.user_width,
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
