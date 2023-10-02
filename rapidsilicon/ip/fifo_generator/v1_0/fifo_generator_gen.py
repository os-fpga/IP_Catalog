#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
import math

from litex_wrapper.fifo_litex_generator import *

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform


# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios(data_width):
    return [
        ("clk",        0,  Pins(1)),
        ("rst",        0,  Pins(1)),
		("wrt_clock",  0,  Pins(1)),
        ("rd_clock",   0,  Pins(1)),
        ("din",        0,  Pins(data_width)),
        ("dout",       0,  Pins(data_width)),
        ("wr_en",      0,  Pins(1)),
        ("rd_en",      0,  Pins(1)),
        ("full",       0,  Pins(1)),
        ("empty",      0,  Pins(1)),
        ("underflow",  0,  Pins(1)),
        ("overflow",   0,  Pins(1)),
        ("prog_full",  0,  Pins(1)),
        ("prog_empty", 0,  Pins(1))
    ]

# FIFO Generator ----------------------------------------------------------------------------------
class FIFOGenerator(Module):
    def __init__(self, platform, data_width, synchronous, full_threshold, empty_threshold, depth, first_word_fall_through, empty_value, full_value, BRAM):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios(data_width))
        self.clock_domains.cd_sys  = ClockDomain()
        self.clock_domains.cd_wrt	= ClockDomain()
        self.clock_domains.cd_rd	= ClockDomain()

        SYNCHRONOUS = {
            True    :   "SYNCHRONOUS",
            False   :   "ASYNCHRONOUS"
        }
	
        self.submodules.fifo = fifo = FIFO(data_width, SYNCHRONOUS[synchronous], full_threshold, empty_threshold, depth, first_word_fall_through, empty_value, full_value, BRAM)
    
        self.comb += fifo.din.eq(platform.request("din"))
        self.comb += platform.request("dout").eq(fifo.dout)
        if (full_threshold):
            self.comb += platform.request("prog_full").eq(fifo.prog_full)
        if (empty_threshold):
            self.comb += platform.request("prog_empty").eq(fifo.prog_empty)
        if(synchronous):
            self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        else:
            self.comb += self.cd_wrt.clk.eq(platform.request("wrt_clock"))
            self.comb += self.cd_rd.clk.eq(platform.request("rd_clock"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        self.comb += fifo.wren.eq(platform.request("wr_en"))
        self.comb += fifo.rden.eq(platform.request("rd_en"))   
        self.comb += platform.request("full").eq(fifo.full)
        self.comb += platform.request("empty").eq(fifo.empty)
        self.comb += platform.request("underflow").eq(fifo.underflow)
        self.comb += platform.request("overflow").eq(fifo.overflow)        
            
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="FIFO")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="fifo_generator", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--data_width",     type=int,   default=36,  	choices=range(1,129),   help="FIFO Write/Read Width")
    core_range_param_group.add_argument("--full_value",     type=int,   default=2,	    choices=range(2,4095),  help="Full Value")
    core_range_param_group.add_argument("--empty_value",    type=int,   default=1,  	choices=range(1,4095),  help="Empty Value")
    core_range_param_group.add_argument("--depth",          type=int,   default=1024,	choices=range(3,32769), help="FIFO Depth")

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--DEPTH",      type=int,     default=1024,   choices=[4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768],   help="FIFO Depth")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--synchronous",  			type=bool,   default=True,    help="Synchronous / Asynchronous Clock")
    core_bool_param_group.add_argument("--first_word_fall_through", type=bool,   default=False,    help="Fist Word Fall Through")
    core_bool_param_group.add_argument("--full_threshold",          type=bool,   default=False,	   help="Full Threshold")
    core_bool_param_group.add_argument("--empty_threshold",         type=bool,   default=False,    help="Empty Threshold")
    core_bool_param_group.add_argument("--BRAM",                    type=bool,   default=True,    help="Block or Distributed RAM")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",           help="Build Directory")
    build_group.add_argument("--build-name",    default="FIFO_generator", help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                   help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",    help="Generate JSON Template")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        if (args.full_threshold == False):
            dep_dict.update({
                'full_value'    :   'True'
            })
        if (args.empty_threshold == False):
            dep_dict.update({
                'empty_value'   :   'True'
            })
        if (args.BRAM == False and args.synchronous == False):
            option_strings_to_remove = ['--depth']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (math.ceil(math.log2(args.depth)) != math.floor(math.log2(args.depth))):
                parser._actions[4].default = 2 ** round(math.log2(args.depth))
            parser._actions[2].choices = range(2, args.DEPTH)
            parser._actions[3].choices = range(1, args.DEPTH)
            if (args.full_value >= args.DEPTH):
                parser._actions[2].default = args.DEPTH - 1
            if (args.empty_value >= args.DEPTH):    
                parser._actions[3].default = 1
        else:
            option_strings_to_remove = ['--DEPTH']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            parser._actions[2].choices = range(2, args.depth)
            parser._actions[3].choices = range(1, args.depth)
            if (args.full_value >= args.depth):
                parser._actions[2].default = args.depth - 1
            if (args.empty_value >= args.depth):    
                parser._actions[3].default = 1
        
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    if (args.BRAM == False and args.synchronous == False):
        depth = args.DEPTH
    else:
        depth = args.depth
    # Create Generator -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = FIFOGenerator(platform,
        data_width      				= args.data_width,
        synchronous     				= args.synchronous,
        full_threshold  				= args.full_threshold,
        empty_threshold 				= args.empty_threshold,
        depth           				= depth,
        full_value                      = args.full_value,
        empty_value                     = args.empty_value,
        first_word_fall_through         = args.first_word_fall_through,
        BRAM                            = args.BRAM
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
        now = datetime.datetime.now()
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "fifo_generator", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"FIFOGEN\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

        build_name = args.build_name.rsplit( ".", 1 )[ 0 ]
        file = os.path.join(args.build_dir, "rapidsilicon/ip/fifo_generator/v1_0", build_name, "sim/testbench.v")
        file = Path(file)
        text = file.read_text()
        text = text.replace("localparam DEPTH = 2048", "localparam DEPTH = %s" % depth)
        file.write_text(text)
        text = text.replace("FIFO_generator", "%s" % build_name)
        file.write_text(text)
        text = text.replace("localparam WIDTH = 36", "localparam WIDTH = %s" % args.data_width)
        file.write_text(text)
        if (not args.synchronous):
            if (args.BRAM):
                text = text.replace("== mem [i]", "== mem[i - 1]")
                file.write_text(text)
                text = text.replace("mem[i], dout, i", "mem[i - 1], dout, i - 1")
                file.write_text(text)
                text = text.replace("== 0", "<= 1")
                file.write_text(text)
            text = text.replace("forever #5 rd_clk = ~rd_clk;", "forever #2.5 rd_clk = ~rd_clk;")
            file.write_text(text)
        else:
            text = text.replace("wrt_clock(wrt_clk)", "clk(wrt_clk)")
            file.write_text(text)
            text = text.replace(".rd_clock(rd_clk), ", "")
            file.write_text(text)
        if (not args.BRAM and args.synchronous and not args.first_word_fall_through):
            text = text.replace("== mem [i]", "== mem[i - 1]")
            file.write_text(text)
            text = text.replace("mem[i], dout, i", "mem[i - 1], dout, i - 1")
            file.write_text(text)
            text = text.replace("== 0", "<= 1")
            file.write_text(text)

if __name__ == "__main__":
    main()
    