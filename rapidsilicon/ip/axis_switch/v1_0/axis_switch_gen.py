#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse
import math

from datetime import datetime

from litex_wrapper.axis_switch_litex_wrapper import AXISTREAMSWITCH

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

# AXI_STREAM_SWITCH Wrapper ----------------------------------------------------------------------------------
class AXISTREAMSWITCHWrapper(Module):
    def __init__(self, platform, s_count, m_count, data_width, 
                id_enable, m_dest_width, user_enable, user_width, 
                s_reg_type, m_reg_type, arb_type_round_robin, m_top,
                arb_lsb_high_priority, update_tid, s_id_width, m_base
                ):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        reg_type = {
            "Bypass"        :   "0",
            "Simple_Buffer" :   "1",
            "Skid_Buffer"   :   "2"
        }
        
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
        keep_enable     = int(data_width>8)
        keep_width      = int((data_width+7)/8)
        
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
                data_width = data_width,
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
                data_width = data_width,
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
        self.submodules.switch = AXISTREAMSWITCH(platform,
            m_axis                  = m_axiss,
            s_axis                  = s_axiss,
            s_count                 = s_count,
            m_count                 = m_count,
            keep_enable             = keep_enable,
            keep_width              = keep_width,
            id_enable               = id_enable,
            user_enable             = user_enable,
            s_id_width              = s_id_width,
            m_id_width              = m_id_width,
            m_dest_width            = m_dest_width,
            s_dest_width            = s_dest_width,
            m_reg_type              = reg_type[m_reg_type],
            s_reg_type              = reg_type[s_reg_type],
            arb_type_round_robin    = arb_type_round_robin,
            arb_lsb_high_priority   = arb_lsb_high_priority,
            update_tid              = update_tid,
            m_connect               = m_connect,
            m_base                  = m_base,
            m_top                   = m_top,
            user_width              = user_width
            )
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS SWITCH CORE")

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
    rs_builder = IP_Builder(device="gemini", ip_name="axis_switch", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",      type=int,     default=8,   choices=[8, 16, 32, 64, 128, 256, 512, 1024],   help="SWITCH Data Width.")

    # Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--m_reg_type",    type=str,      default="Skid_Buffer",   choices=["Bypass", "Simple_Buffer", "Skid_Buffer"],   help="Type of Register")
    core_string_param_group.add_argument("--s_reg_type",    type=str,      default="Bypass",        choices=["Bypass", "Simple_Buffer", "Skid_Buffer"],   help="Type of Register")

    # Core bool value parameters
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--id_en",                   type=bool,  default=True,  help="SWITCH ID Enable.")
    core_bool_param_group.add_argument("--user_en",                 type=bool,  default=True,   help="SWITCH User Enable.")
    core_bool_param_group.add_argument("--lsb_high_priority",       type=bool,  default=True,   help="SWITCH LSB Priority Selection")
    core_bool_param_group.add_argument("--type_round_robin",        type=bool,  default=True,   help="SWITCH Round Robin Arbitration")
    core_bool_param_group.add_argument("--tid",                     type=bool,  default=True,  help="SWITCH Update TID")

    # Core range value parameters
    core_range_param_group = parser.add_argument_group(title="Core range parameters")

    core_range_param_group.add_argument("--user_width",     type=int,   default=1,  choices=range(1,1025),  help="SWITCH User Width")
    core_range_param_group.add_argument("--s_id_width",     type=int,   default=16,  choices=range(1,17),    help="SWITCH S_ID Width")
    core_range_param_group.add_argument("--m_dest_width",   type=int,   default=8,  choices=range(1,9),    help="SWITCH M_Destination Width")

    core_range_param_group.add_argument("--s_count",        type=int,   default=4,  choices=range(1,17),    help="SWITCH Slave Interfaces")
    core_range_param_group.add_argument("--m_count",        type=int,   default=4,  choices=range(1,17),    help="SWITCH Master Interfaces")
    core_range_param_group.add_argument("--m_base",         type=int,   default=0,  choices=range(0,16),    help="SWITCH Output interface routing base")
    core_range_param_group.add_argument("--m_top",          type=int,   default=0,  choices=range(0,16),    help="SWITCH Output interface routing top")

    # Build Parameters
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_switch_wrapper",  help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'AXI-Stream Switch',
    'Version' : 'V1_0',
    'Interface' : 'AXI-Streaming',
    'Description' : 'The AXIS Switch core is an AXI4-Streaming compliant customizable switch that is designed to be used in applications that require configurable routing between masters and slaves with multiple arbitration options.'}
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        if(args.m_count):
            if (args.m_count == 1):
                parser._actions[12].choices = range(1, 17)
            else:
                parser._actions[12].choices = range(1, math.floor(31/args.m_count) + 1)
            parser._actions[15].choices = range(0, args.m_count)
            parser._actions[14].choices = range(0, args.m_count)
        if(args.s_count):
            if (args.s_count == 1):
                parser._actions[13].choices = range(1, 17)
            else:
                parser._actions[13].choices = range(1, math.floor(31/args.s_count) + 1)
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    summary =  { 
    "Data Width" : args.data_width,
    "Master Register Type" : args.m_reg_type,
    "Slave Register Type" : args.s_reg_type,
    "Number of Masters" : args.m_count,
    "Number of Slaves" : args.s_count,
    "Masters base address offset" : args.m_base,
    "Masters top address offset" : args.m_top
    }

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    
    m_base = args.m_base
    m_top = args.m_top
    if (m_base >= args.m_count):
        m_base = 0
    if (m_top >= args.m_count):
        m_top = 0

    module   = AXISTREAMSWITCHWrapper(platform,
        s_count                 = args.s_count, 
        m_count                 = args.m_count, 
        data_width              = args.data_width, 
        id_enable               = args.id_en,
        s_id_width              = args.s_id_width,
        m_dest_width            = args.m_dest_width,
        user_enable             = args.user_en,
        user_width              = args.user_width,
        m_base                  = m_base,
        m_top                   = m_top,
        update_tid              = args.tid,
        s_reg_type              = args.s_reg_type,
        m_reg_type              = args.m_reg_type,
        arb_type_round_robin    = args.type_round_robin,
        arb_lsb_high_priority   = args.lsb_high_priority
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axis_switch", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXISSWTH\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
