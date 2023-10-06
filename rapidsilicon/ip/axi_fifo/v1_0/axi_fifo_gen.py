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

from litex_wrapper.axi_fifo_litex_wrapper import AXIFIFO

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]
    
# AXI FIFO Wrapper ----------------------------------------------------------------------------------
class AXIFIFOWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, aw_user_en, aw_user_width,
                w_user_en, w_user_width, b_user_en, b_user_width, ar_user_en, ar_user_width,
                r_user_en, r_user_width, write_fifo_depth, read_fifo_depth, write_fifo_delay, 
                read_fifo_delay):
        
        # Clocking 
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # AXI 
        s_axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
            aw_user_width   = aw_user_width,
            w_user_width    = w_user_width,
            b_user_width    = b_user_width,
            ar_user_width   = ar_user_width,
            r_user_width    = r_user_width
        )
        
        m_axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
            aw_user_width   = aw_user_width,
            w_user_width    = w_user_width,
            b_user_width    = b_user_width,
            ar_user_width   = ar_user_width,
            r_user_width    = r_user_width
        )
        
        platform.add_extension(s_axi.get_ios("s_axi"))
        self.comb += s_axi.connect_to_pads(platform.request("s_axi"), mode="slave")
        
        platform.add_extension(m_axi.get_ios("m_axi"))
        self.comb += m_axi.connect_to_pads(platform.request("m_axi"), mode="master")

        # AXI FIFO 
        self.submodules += AXIFIFO(platform, 
            s_axi               = s_axi,
            m_axi               = m_axi,
            aw_user_en          = aw_user_en,
            w_user_en           = w_user_en,
            b_user_en           = b_user_en,
            ar_user_en          = ar_user_en,
            r_user_en           = r_user_en,
            write_fifo_depth    = write_fifo_depth,
            read_fifo_depth     = read_fifo_depth,
            write_fifo_delay    = write_fifo_delay,
            read_fifo_delay     = read_fifo_delay
            )

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI FIFO CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_fifo", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",           type=int,    default=32,    choices=[32, 64, 128, 256, 512, 1024],  help="FIFO Data Width.")
    core_fix_param_group.add_argument("--write_fifo_depth",     type=int,    default=32,     choices=[32, 512],                     help="FIFO Write Depth.")
    core_fix_param_group.add_argument("--read_fifo_depth",      type=int,    default=32,     choices=[32, 512],                     help="FIFO Read Depth.")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--aw_user_en",           type=bool,     default=True,      help="FIFO AW-Channel User Enable.")
    core_bool_param_group.add_argument("--w_user_en",            type=bool,     default=True,      help="FIFO W-Channel User Enable.")
    core_bool_param_group.add_argument("--b_user_en",            type=bool,     default=True,      help="FIFO B-Channel User Enable.")
    core_bool_param_group.add_argument("--ar_user_en",           type=bool,     default=True,      help="FIFO AR-Channel User Enable.")
    core_bool_param_group.add_argument("--r_user_en",            type=bool,     default=True,      help="FIFO R-Channel User Enable.")
    core_bool_param_group.add_argument("--write_fifo_delay",     type=bool,     default=True,      help="FIFO Write Delay.")
    core_bool_param_group.add_argument("--read_fifo_delay",      type=bool,     default=True,      help="FIFO Read Delay.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--addr_width",          type=int,       default=32,    choices=range(1,65),         help="FIFO Address Width.")
    core_range_param_group.add_argument("--id_width",            type=int,       default=8,     choices=range(1,33),         help="FIFO ID Width.")
    core_range_param_group.add_argument("--aw_user_width",       type=int,       default=1,     choices=range(1, 1025),      help="FIFO AW-Channel User Width.")
    core_range_param_group.add_argument("--w_user_width",        type=int,       default=1,     choices=range(1, 1025),      help="FIFO W-Channel User Width.")
    core_range_param_group.add_argument("--b_user_width",        type=int,       default=1,     choices=range(1, 1025),      help="FIFO B-Channel User Width.")
    core_range_param_group.add_argument("--ar_user_width",       type=int,       default=1,     choices=range(1, 1025),      help="FIFO AR-Channel User Width.")
    core_range_param_group.add_argument("--r_user_width",        type=int,       default=1,     choices=range(1, 1025),      help="FIFO R-Channel User Width.")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_fifo_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()


    #IP Details generation
    details =  {   "IP details": {
    'Name' : 'AXI Sync FIFO',
    'Version' : 'V1_0',
    'Interface' : 'AXI',
    'Description' : 'The AXI FIFO is an AXI full compliant customize-able synchronus FIFO. It can be used to store and retrieve ordered data, while using optimal resources.'}}

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

        if (args.aw_user_en == False):
            dep_dict.update({
                'aw_user_width' :   'True',
            })
        else:
            dep_dict.update({
                'aw_user_width' :   'False',
            })
        if (args.w_user_en == False):
            dep_dict.update({
                'w_user_width' :   'True',
            })
        else:
            dep_dict.update({
                'w_user_width' :   'False',
            })
        if (args.b_user_en == False):
            dep_dict.update({
                'b_user_width' :   'True',
            })
        else:
            dep_dict.update({
                'b_user_width' :   'False',
            })        
        if (args.ar_user_en == False):
            dep_dict.update({
                'ar_user_width' :   'True',
            })
        else:
            dep_dict.update({
                'ar_user_width' :   'False',
            })
        if (args.r_user_en == False):
            dep_dict.update({
                'r_user_width' :   'True',
            })
        else:
            dep_dict.update({
                'r_user_width' :   'False',
            })

        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")



    #IP Summary generation
    summary =  { 
    "AXI FIFO Write Depth selected": args.write_fifo_depth,
    "AXI FIFO Read Depth selected": args.read_fifo_depth,
    "AXI FIFO Data width selected": args.data_width,
#    "AXI Address width programmed": args.addr_width,
    "AXI ID width selected": args.id_width,
    }


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
        

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXIFIFOWrapper(platform,
        data_width       = args.data_width,
        addr_width       = args.addr_width,
        id_width         = args.id_width,
        aw_user_en       = args.aw_user_en,
        aw_user_width    = args.aw_user_width,
        w_user_en        = args.w_user_en,
        w_user_width     = args.w_user_width,
        b_user_en        = args.b_user_en,
        b_user_width     = args.b_user_width,
        ar_user_en       = args.ar_user_en,
        ar_user_width    = args.ar_user_width,
        r_user_en        = args.r_user_en,
        r_user_width     = args.r_user_width,
        write_fifo_depth = args.write_fifo_depth,
        read_fifo_depth  = args.read_fifo_depth,
        write_fifo_delay = args.write_fifo_delay,
        read_fifo_delay  = args.read_fifo_delay,
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axi_fifo", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXI_FIFO\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
