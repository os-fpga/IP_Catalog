#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse
import math

from litex_wrapper.axis_ram_switch_litex_wrapper import AXISTREAMRAMSWITCH

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIStreamInterface


# Function to convert Binary to Decimal ---------------------------------------
def bin2dec(n):
    return int (n,2)

# Function to convert Decimal to Binary ---------------------------------------
def dec2bin(n):
    return bin(n).replace("0b", "")

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]

def get_status_ios(n):
    return [
        ("status", 0,
            Subsignal("overflow",   Pins(n)),
            Subsignal("bad_frame",  Pins(n)),
            Subsignal("good_frame", Pins(n)) 
        )
    ]
# AXI_STREAM_RAM_SWITCH Wrapper ----------------------------------------------------------------------------------
class AXISTREAMRAMSWITCHWrapper(Module):
    def __init__(self, platform, fifo_depth, cmd_fifo_depth, speedup, s_count,
                m_count, s_data_width, m_data_width, id_enable, s_id_width, arb_lsb_high_priority,
                m_dest_width, user_enable, user_width, user_bad_frame_value, 
                user_bad_frame_mask, drop_bad_frame, drop_when_full, ram_pipeline,
                m_base, m_top, update_tid, arb_type_round_robin
                ):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        s_dest_width    = m_dest_width + (math.ceil(math.log2(m_count)))
        m_id_width      = s_id_width + (math.ceil(math.log2(s_count)))

        # Computing bus width for M_CONNECT ----------------------------------
        s_connect       = ''
        for i in range (s_count):
            s_connect += str(1)
        m_connect = ''
        for i in range (m_count):
            m_connect += str(s_connect)
        m_connect = bin2dec(m_connect)

        # Computing KEEP_ENABLE and KEEP_WIDTH --------------------------------
        s_keep_enable     = int(s_data_width>8)
        s_keep_width      = int((s_data_width+7)/8)

        m_keep_enable     = int(m_data_width>8)
        m_keep_width      = int((m_data_width+7)/8)

        # Computing addresses for M_BASE --------------------------------------
        temp = ''
        for i in range (m_base, m_count):
            zeroes = ''
            for j in range (s_dest_width - len(dec2bin(i))):
                zeroes += '0'
            temp = zeroes + str(dec2bin(i)) + temp
        m_base = bin2dec(temp)

        # Computing addresses for M_TOP ----------------------------------------
        temp = ''
        for i in range (m_top, m_count):
            zeroes = ''
            for j in range (s_dest_width - len(dec2bin(i))):
                zeroes += '0'
            temp = zeroes + str(dec2bin(i)) + temp
        m_top = bin2dec(temp)

        # AXI STREAM -------------------------------------------------------------------------------
        # Slave Interface ----------------
        
        s_axiss = []
        for i in range(s_count):
            s_axis = AXIStreamInterface(
                data_width = s_data_width,
                user_width = user_width,
                id_width   = s_id_width,
                dest_width = s_dest_width
            )            
            if i>9:
                platform.add_extension(s_axis.get_ios("s{}_axis".format(i)))
                self.comb += s_axis.connect_to_pads(platform.request("s{}_axis".format(i)), mode="slave")
            else:
                platform.add_extension(s_axis.get_ios("s0{}_axis".format(i)))
                self.comb += s_axis.connect_to_pads(platform.request("s0{}_axis".format(i)), mode="slave")
            s_axiss.append(s_axis)

        # Master Interface ---------------
        m_axiss = []
        for i in range(m_count):
            m_axis = AXIStreamInterface(
                data_width = m_data_width,
                user_width = user_width,
                id_width   = m_id_width,
                dest_width = m_dest_width
            )
            if i>9:
                platform.add_extension(m_axis.get_ios("m{}_axis".format(i)))
                self.comb += m_axis.connect_to_pads(platform.request("m{}_axis".format(i)), mode="master")
            else:
                platform.add_extension(m_axis.get_ios("m0{}_axis".format(i)))
                self.comb += m_axis.connect_to_pads(platform.request("m0{}_axis".format(i)), mode="master")
            m_axiss.append(m_axis)

        # AXIS-SWITCH -------------------------------------------------------------------------------
        self.submodules.ram_switch =  ram_switch = AXISTREAMRAMSWITCH(platform,
            fifo_depth              = fifo_depth,
            cmd_fifo_depth          = cmd_fifo_depth,
            speedup                 = speedup,
            m_axis                  = m_axiss,
            s_axis                  = s_axiss,
            s_count                 = s_count,
            m_count                 = m_count,
            s_keep_enable           = s_keep_enable,
            s_keep_width            = s_keep_width,
            id_enable               = id_enable,
            user_enable             = user_enable,
            s_id_width              = s_id_width,
            m_id_width              = m_id_width,
            m_dest_width            = m_dest_width,
            s_dest_width            = s_dest_width,
            arb_type_round_robin    = arb_type_round_robin,
            arb_lsb_high_priority   = arb_lsb_high_priority,
            update_tid              = update_tid,
            m_connect               = m_connect,
            m_base                  = m_base,
            m_top                   = m_top,
            user_bad_frame_value    = user_bad_frame_value,
            user_bad_frame_mask     = user_bad_frame_mask,
            drop_bad_frame          = drop_bad_frame,
            drop_when_full          = drop_when_full,
            s_data_width            = s_data_width,
            m_data_width            = m_data_width,
            m_keep_enable           = m_keep_enable,
            m_keep_width            = m_keep_width,
            ram_pipeline            = ram_pipeline,
            user_width              = user_width
            )
        
        # RAM SWITCH Status Signals -----------------------------------------------------------------
        
        platform.add_extension(get_status_ios(s_count))        
        ram_switch_pads = platform.request("status")
        self.comb += [
            ram_switch_pads.overflow.eq(ram_switch.status_overflow),
            ram_switch_pads.bad_frame.eq(ram_switch.status_bad_frame),
            ram_switch_pads.good_frame.eq(ram_switch.status_good_frame)
        ]
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS RAM SWITCH CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)
    
    from common import IP_Builder

    # Parameter Dependency dictionary
    #       Ports       :   Dependency
    dep_dict = {
        'user_width'    :   'user_enable'
    }

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axis_ram_switch", language="verilog")
    
    # Core fix value parameters
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--fifo_depth",       type=int,   default=4096,   choices=[8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768], help="RAM_SWITCH FIFO Depth.")
    core_fix_param_group.add_argument("--cmd_fifo_depth",   type=int,   default=32,     choices=[8, 16, 32, 64, 128, 256, 512, 1024],                                 help="RAM_SWITCH CMD_FIFO Depth")
    core_fix_param_group.add_argument("--s_data_width",     type=int,       default=8,  choices=[8, 16, 32, 64, 128, 256, 512, 1024],      help="RAM_SWITCH Slave Data Width.")
    core_fix_param_group.add_argument("--m_data_width",     type=int,       default=8,  choices=[8, 16, 32, 64, 128, 256, 512, 1024],      help="RAM_SWITCH Master Data Width.")
    
    # Core bool value parameters
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--id_en",                   type=bool,  default=False,  help="RAM_SWITCH ID Enable.")
    core_bool_param_group.add_argument("--user_en",                 type=bool,  default=True,   help="RAM_SWITCH User Enable.")
    core_bool_param_group.add_argument("--lsb_high_priority",       type=bool,  default=True,   help="RAM_SWITCH LSB Priority Selection")
    core_bool_param_group.add_argument("--type_round_robin",        type=bool,  default=True,   help="RAM_SWITCH Round Robin Arbitration")
    core_bool_param_group.add_argument("--tid",                     type=bool,  default=False,  help="RAM_SWITCH Update TID")
    core_bool_param_group.add_argument("--drop_bad_frame",          type=bool,  default=False,  help="RAM SWITCH Drop frames marked bad")
    core_bool_param_group.add_argument("--drop_when_full",          type=bool,  default=False,  help="RAM_SWITCH Drop incoming frames when full")

    # Core range value parameters
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--user_width",     type=int,   default=1,  choices=range(1,1025),  help="RAM_SWITCH User Width")
    core_range_param_group.add_argument("--s_id_width",     type=int,   default=8,  choices=range(1,17),    help="RAM_SWITCH S_ID Width")
    core_range_param_group.add_argument("--m_dest_width",   type=int,   default=1,  choices=range(1,9),    help="RAM_SWITCH M_Destination Width")
    core_range_param_group.add_argument("--speedup",        type=int,   default=0,  choices=range(0,101),   help="RAM_SWITCH Speedup factor")
    core_range_param_group.add_argument("--ram_pipeline",   type=int,   default=2,  choices=range(0,33),    help="RAM_SWITCH RAM Pipeline Stages")
    core_range_param_group.add_argument("--s_count",        type=int,   default=4,  choices=range(1,17),    help="RAM_SWITCH Slave Interfaces")
    core_range_param_group.add_argument("--m_count",        type=int,   default=4,  choices=range(1,17),    help="RAM_SWITCH Master Interfaces")
    core_range_param_group.add_argument("--m_base",         type=int,   default=0,  choices=range(0,16),    help="RAM_SWITCH Output interface routing base")
    core_range_param_group.add_argument("--m_top",          type=int,   default=0,  choices=range(0,16),    help="RAM_SWITCH Output interface routing top")
    core_range_param_group.add_argument("--bad_frame_value",type=int,   default=1,  choices=range(1,100),    help="RAM_SWITCH Value for bad frame marker")
    core_range_param_group.add_argument("--bad_frame_mask", type=int,   default=1,  choices=range(1,100),    help="RAM_SWITCH Mask for bad frame marker")
    
    # Build Parameters
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                  help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                         help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_ram_switch_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = AXISTREAMRAMSWITCHWrapper(platform,
        fifo_depth              = args.fifo_depth,
        cmd_fifo_depth          = args.cmd_fifo_depth,
        speedup                 = args.speedup,
        s_count                 = args.s_count, 
        m_count                 = args.m_count, 
        s_data_width            = args.s_data_width,
        m_data_width            = args.m_data_width,
        id_enable               = args.id_en,
        s_id_width              = args.s_id_width,
        m_dest_width            = args.m_dest_width,
        user_enable             = args.user_en,
        user_width              = args.user_width,
        user_bad_frame_value    = args.bad_frame_value,
        user_bad_frame_mask     = args.bad_frame_mask,
        drop_bad_frame          = args.drop_bad_frame,
        drop_when_full          = args.drop_when_full,
        m_base                  = args.m_base,
        m_top                   = args.m_top,
        update_tid              = args.tid,
        arb_type_round_robin    = args.type_round_robin,
        arb_lsb_high_priority   = args.lsb_high_priority,
        ram_pipeline            = args.ram_pipeline
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
            module     = module
        )

if __name__ == "__main__":
    main()
