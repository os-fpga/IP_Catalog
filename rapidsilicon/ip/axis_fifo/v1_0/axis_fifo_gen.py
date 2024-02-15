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

from litex_wrapper.axis_fifo_litex_wrapper import AXISTREAMFIFO

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIStreamInterface

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]

def get_status_ios():
    return [
        ("status", 0,
            Subsignal("overflow",   Pins(1)),
            Subsignal("bad_frame",  Pins(1)),
            Subsignal("good_frame", Pins(1)),
            Subsignal("full",       Pins(1)),
            Subsignal("empty",      Pins(1))    
        )
    ]

# AXI_STREAM_FIFO Wrapper ----------------------------------------------------------------------------------
class AXISTREAMFIFOWrapper(Module):
    def __init__(self, platform, depth, data_width, last_en, id_en, id_width, 
                dest_en, dest_width, user_en, user_width, pip_out, frame_fifo,
                drop_bad_frame, drop_when_full):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI STREAM -------------------------------------------------------------------------------
        s_axis = AXIStreamInterface(
            data_width = data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width
        )
        
        m_axis = AXIStreamInterface(
            data_width = data_width,
            user_width = user_width,
            dest_width = dest_width,
            id_width   = id_width
        )
        # Input AXI
        platform.add_extension(s_axis.get_ios("s_axis"))
        self.comb += s_axis.connect_to_pads(platform.request("s_axis"), mode="slave")
        
        # Output AXI
        platform.add_extension(m_axis.get_ios("m_axis"))
        self.comb += m_axis.connect_to_pads(platform.request("m_axis"), mode="master")
        
        # AXIS-FIFO ----------------------------------------------------------------------------------
        self.submodules.fifo = fifo = AXISTREAMFIFO(platform,
            m_axis          = m_axis,
            s_axis          = s_axis,
            depth           = depth, 
            last_en         = last_en,
            id_en           = id_en,
            dest_en         = dest_en,
            user_en         = user_en,
            pip_out         = pip_out,
            frame_fifo      = frame_fifo,
            drop_bad_frame  = drop_bad_frame,
            drop_when_full  = drop_when_full
            )
        
        # FIFO Status Signals ----------------------------------------------------------------------
        platform.add_extension(get_status_ios())
        fifo_pads = platform.request("status")
        self.comb += [
            fifo_pads.overflow.eq(fifo.status_overflow),
            fifo_pads.bad_frame.eq(fifo.status_bad_frame),
            fifo_pads.good_frame.eq(fifo.status_good_frame),
            fifo_pads.full.eq(fifo.status_full),
            fifo_pads.empty.eq(fifo.status_empty)
        ]

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS FIFO CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports    :    Dependency
    dep_dict = {}   

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axis_fifo", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--depth",           type=int,     default=4096,   choices=[8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768],   help="FIFO Depth.")
    core_fix_param_group.add_argument("--data_width",      type=int,     default=8,      choices=[8, 16, 32, 64, 128, 256, 512, 1024],                                   help="FIFO Data Width.")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--last_en",         type=bool,       default=True,      help="FIFO Last Enable.")
    core_bool_param_group.add_argument("--id_en",           type=bool,       default=True,      help="FIFO ID Enable.")
    core_bool_param_group.add_argument("--dest_en",         type=bool,       default=True,      help="FIFO Destination Enable.")
    core_bool_param_group.add_argument("--user_en",         type=bool,       default=True,      help="FIFO User Enable.")
    core_bool_param_group.add_argument("--frame_fifo",      type=bool,       default=True,      help="FIFO Frame.")
    core_bool_param_group.add_argument("--drop_bad_frame",  type=bool,       default=True,      help="FIFO Drop Bad Frame.")
    core_bool_param_group.add_argument("--drop_when_full",  type=bool,       default=True,      help="FIFO Drop Frame When Full.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--id_width",       type=int,       default=8,      choices=range(1, 17),         help="FIFO ID Width.")
    core_range_param_group.add_argument("--dest_width",     type=int,       default=8,      choices=range(1, 9),         help="FIFO Destination Width.")
    core_range_param_group.add_argument("--user_width",     type=int,       default=1,      choices=range(1, 1025),       help="FIFO User Width.")
    core_range_param_group.add_argument("--pip_out",        type=int,       default=1,      choices=range(1, 33),       help="FIFO Pipeline Output registers.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_fifo_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

   #IP Details generation
    details =  {   "IP details": {
    'Name' : 'AXI Streaming FIFO',
    'Version' : 'V1_0',
    'Interface' : 'AXI Stream',
    'Description' : 'The AXIS FIFO is an AXI streaming compliant customize-able FIFO. It can be used to store and retrieve ordered data at different clock domains, while using optimal resources.'}}

 
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

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


    #IP Summary generation
    summary =  { 
    "AXI stream FIFO Depth selected": args.depth,
    "AXI stream Data width programmed": args.data_width,
    "AXI stream ID width programmed": args.id_width,
    }


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXISTREAMFIFOWrapper(platform,
        depth          = args.depth,
        data_width     = args.data_width,
        last_en        = args.last_en,
        id_en          = args.id_en,
        id_width       = args.id_width,
        dest_en        = args.dest_en,
        dest_width     = args.dest_width,
        user_en        = args.user_en,
        user_width     = args.user_width,
        pip_out        = args.pip_out,
        frame_fifo     = args.frame_fifo,
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
        rs_builder.generate_tcl(version    = "v1_0")
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axis_fifo", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXISFIFO\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
