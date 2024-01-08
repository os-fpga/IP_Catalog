#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from datetime import datetime

from litex_wrapper.axis_async_fifo_litex_wrapper import AXISASYNCFIFO

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIStreamInterface

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_m_ios():
    return [
        ("m_clk", 0, Pins(1)),
        ("m_rst", 0, Pins(1))
    ]
    
def get_clkin_s_ios():
    return [
        ("s_clk", 0, Pins(1)),
        ("s_rst", 0, Pins(1))
    ]
    
def get_slave_status_ios():
    return [
        ("s_status", 0,
            Subsignal("overflow",   Pins(1)),
            Subsignal("bad_frame",  Pins(1)),
            Subsignal("good_frame", Pins(1)),
        )]
    
def get_master_status_ios():
    return [
        ("m_status", 0,
            Subsignal("overflow",   Pins(1)),
            Subsignal("bad_frame",       Pins(1)),
            Subsignal("good_frame",      Pins(1))    
        )
    ]

# AXI_STREAM_FIFO Wrapper ----------------------------------------------------------------------------------
class AXISASYNCFIFOWrapper(Module):
    def __init__(self, platform, depth, data_width, last_en, id_en, id_width, 
                dest_en, dest_width, user_en, user_width, ram_pipeline, out_fifo_en, frame_fifo, bad_frame_value, 
                drop_bad_frame, drop_when_full):

        # Clock Domain
        self.clock_domains.cd_sys = ClockDomain()
        
        # AXI STREAM -------------------------------------------------------------------------------
        s_axis = AXIStreamInterface(
            data_width = data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width,
            keep_width = int((data_width+7)/8)
        )
        
        m_axis = AXIStreamInterface(
            data_width = data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width,
            keep_width = int((data_width+7)/8)
        )
        # Input AXI
        platform.add_extension(s_axis.get_ios("s_axis"))
        self.comb += s_axis.connect_to_pads(platform.request("s_axis"), mode="slave")
        
        # Output AXI
        platform.add_extension(m_axis.get_ios("m_axis"))
        self.comb += m_axis.connect_to_pads(platform.request("m_axis"), mode="master")

        # AXIS-ASYNC-FIFO ----------------------------------------------------------------------------------
        self.submodules.fifo = fifo = AXISASYNCFIFO(platform,
            m_axis          = m_axis,
            s_axis          = s_axis,
            depth           = depth, 
            last_en         = last_en,
            id_en           = id_en,
            dest_en         = dest_en,
            user_en         = user_en,
            ram_pipeline         = ram_pipeline,
            frame_fifo      = frame_fifo,
            out_fifo_en     = out_fifo_en,
            bad_frame_value = bad_frame_value,
            drop_bad_frame  = drop_bad_frame,
            drop_when_full  = drop_when_full
            )
        
        # FIFO Status Signals ----------------------------------------------------------------------
        platform.add_extension(get_slave_status_ios())
        fifo_pads = platform.request("s_status")
        self.comb += [
            fifo_pads.overflow.eq(fifo.s_status_overflow),
            fifo_pads.bad_frame.eq(fifo.s_status_bad_frame),
            fifo_pads.good_frame.eq(fifo.s_status_good_frame),
        ]

        platform.add_extension(get_master_status_ios())
        fifo_pads = platform.request("m_status")
        self.comb += [
            fifo_pads.overflow.eq(fifo.m_status_overflow),
            fifo_pads.bad_frame.eq(fifo.m_status_bad_frame),
            fifo_pads.good_frame.eq(fifo.m_status_good_frame),
        ]

        platform.add_extension(get_clkin_m_ios())
        self.comb += fifo.m_clk.eq(platform.request("m_clk"))
        self.comb += fifo.m_rst.eq(platform.request("m_rst"))
        
        platform.add_extension(get_clkin_s_ios())
        self.comb += fifo.s_clk.eq(platform.request("s_clk"))
        self.comb += fifo.s_rst.eq(platform.request("s_rst"))

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS ASYNC FIFO CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}   

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axis_async_fifo", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--depth",          type=int,     default=4096,   choices=[8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768],   help="FIFO Depth.")
    core_fix_param_group.add_argument("--data_width",      type=int,     default=8,   choices=[8, 16, 32, 64, 128, 256, 512, 1024],   help="FIFO Data Width.")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--last_en",         type=bool,      default=True,       help="FIFO Last Enable.")
    core_bool_param_group.add_argument("--id_en",           type=bool,      default=True,       help="FIFO ID Enable.")
    core_bool_param_group.add_argument("--dest_en",         type=bool,      default=True,       help="FIFO Destination Enable.")
    core_bool_param_group.add_argument("--user_en",         type=bool,      default=True,       help="FIFO User Enable.")
    core_bool_param_group.add_argument("--frame_fifo",      type=bool,      default=True,       help="FIFO Frame.")
    core_bool_param_group.add_argument("--out_fifo_en",     type=bool,      default=True,       help="OUTPUT FIFO ENABLE.")
    core_bool_param_group.add_argument("--drop_bad_frame",  type=bool,      default=True,       help="FIFO Drop Bad Frame.")
    core_bool_param_group.add_argument("--drop_when_full",  type=bool,      default=True,       help="FIFO Drop Frame When Full.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--id_width",       type=int,       default=8,      choices=range(1, 17),        help="FIFO ID Width.")
    core_range_param_group.add_argument("--dest_width",     type=int,       default=8,      choices=range(1, 9),        help="FIFO Destination Width.")
    core_range_param_group.add_argument("--user_width",     type=int,       default=1,      choices=range(1, 1024),      help="FIFO User Width.")
    core_range_param_group.add_argument("--bad_frame_value",type=int,       default=1,      choices=range(1,100),       help="FIFO USER BAD FRAME VALUE")
    core_range_param_group.add_argument("--ram_pipeline",   type=int,       default=1,      choices=range(1, 10),      help="FIFO Number of Pipeline registers.")
    core_range_param_group.add_argument("--bad_frame_mask", type=int,   default=1,  choices=range(1,100),    help="FIFO Mask for bad frame marker")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                  help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                         help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_async_fifo_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    #IP Details generation
    details =  {   "IP details": {
    'Name' : 'AXIS Async FIFO',
    'Version' : 'V1_0',
    'Interface' : 'AXI',
    'Description' : 'The AXI Streaming Async FIFO is a customize-able asynchronous FIFO. It can be used to store and retrieve ordered data at different clock domains, while using optimal resources.'}}



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

        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

    #IP Summary generation
    summary =  { 
    "AXI STreaming FIFO Depth programmed": args.depth,
    "AXI Streaming Data width programmed": args.data_width,
    "AXI Streaming ID width programmed": args.id_width,
    "AXI Streaming destination width programmed": args.dest_width,
    }


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXISASYNCFIFOWrapper(platform,
        depth          = args.depth,
        data_width     = args.data_width,
        last_en        = args.last_en,
        id_en          = args.id_en,
        id_width       = args.id_width,
        dest_en        = args.dest_en,
        dest_width     = args.dest_width,
        user_en        = args.user_en,
        user_width     = args.user_width,
        ram_pipeline        = args.ram_pipeline,
        frame_fifo     = args.frame_fifo,
        out_fifo_en    = args.out_fifo_en,
        bad_frame_value= args.bad_frame_value,
        drop_bad_frame = args.drop_bad_frame,
        drop_when_full = args.drop_when_full,
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
            version = "v1_0"
        )
        
        # IP_ID Parameter
        now = datetime.now()
        my_year         = now.year - 2022
        year            = (bin(my_year)[2:]).zfill(7) # 7-bits  # Removing '0b' prefix = [2:]
        month           = (bin(now.month)[2:]).zfill(4) # 4-bits
        day             = (bin(now.day)[2:]).zfill(5) # 5-bits
        mod_hour        = now.hour % 12 # 12 hours Format
        hour            = (bin(mod_hour)[2:]).zfill(4) # 4-bits
        minute          = (bin(now.minute)[2:]).zfill(6) # 6-bits
        second          = (bin(now.second)[2:]).zfill(6) # 6-bits
        
        # Concatenation for IP_ID Parameter
        ip_id = ("{}{}{}{}{}{}").format(year, day, month, hour, minute, second)
        ip_id = ("32'h{}").format(hex(int(ip_id,2))[2:])
        
        # IP_VERSION parameter
        #               Base  _  Major _ Minor
        ip_version = "00000000_00000000_0000000000000001"
        ip_version = ("32'h{}").format(hex(int(ip_version, 2))[2:])
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axis_async_fifo", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"ASYNFIFO\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
