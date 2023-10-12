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
import math

from litex_wrapper.fifo_litex_generator import *

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform
# Define a custom function to generate choices in multiples of 9
def multiples_of_9(value):
    if value % 9 != 0:
        raise argparse.ArgumentTypeError("Value must be a multiple of 9")
    return value

# Making the read and write data widths into their own buses
def divide_n_bit_number(number):
    # Convert the number to a binary string
    binary_string = '0' * number
    buses = []

    for i in range(0, len(binary_string), 36):
        bus = binary_string[i:i+36]
        buses.append(bus)
    if (len(buses[-1]) < 36 and len(buses[-1]) > 18):
        for i in range(len(binary_string) - len(buses[-1]), len(binary_string), 18):
            bus = binary_string[i:i+18]
            buses.append(bus)
        buses.pop(-3)
    
    return buses

# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios(data_width_write, data_width_read):
    return [
        ("clk",        0,  Pins(1)),
        ("rst",        0,  Pins(1)),
		("wrt_clock",  0,  Pins(1)),
        ("rd_clock",   0,  Pins(1)),
        ("din",        0,  Pins(data_width_write)),
        ("dout",       0,  Pins(data_width_read)),
        ("wr_en",      0,  Pins(1)),
        ("rd_en",      0,  Pins(1)),
        ("full",       0,  Pins(1)),
        ("empty",      0,  Pins(1)),
        ("underflow",  0,  Pins(1)),
        ("overflow",   0,  Pins(1)),
        ("prog_full",  0,  Pins(1)),
        ("prog_empty", 0,  Pins(1))
    ]

# Data Width Read Limitations ---------------------------------------------------------------------

def factors_multiples(number):
    factors = []
    for i in range(2, number + 1):
        if number % i == 0:
            factors.append(i)
    sequence = []
    while (number not in sequence):
        sequence = [min(factors)]
        while sequence[-1] * 2 <= 1024:
            next_number = sequence[-1] * 2
            sequence.append(next_number)
        if number in sequence:
            break
        else:
            factors.pop(0)
    return sequence

# FIFO Generator ----------------------------------------------------------------------------------
class FIFOGenerator(Module):
    def __init__(self, platform, data_width_write, data_width_read, synchronous, full_threshold, empty_threshold, depth, first_word_fall_through, empty_value, full_value, BRAM):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios(data_width_write, data_width_read))
        self.clock_domains.cd_sys  = ClockDomain()
        self.clock_domains.cd_wrt	= ClockDomain()
        self.clock_domains.cd_rd	= ClockDomain()

        SYNCHRONOUS = {
            True    :   "SYNCHRONOUS",
            False   :   "ASYNCHRONOUS"
        }
	
        self.submodules.fifo = fifo = FIFO(data_width_write, data_width_read, SYNCHRONOUS[synchronous], full_threshold, empty_threshold, depth, first_word_fall_through, empty_value, full_value, BRAM)
    
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
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_range_param_group.add_argument("--data_width",         type=int,   default=36,  	choices=range(1,1025),   help="FIFO Write/Read Width")
    core_fix_param_group.add_argument("--data_width_write",   type=int,   default=36,  	choices=[i*9 for i in range(1, 114)],   help="FIFO Write Width")
    core_range_param_group.add_argument("--full_value",         type=int,   default=2,      choices=range(2,4095),  help="Full Value")
    core_range_param_group.add_argument("--empty_value",        type=int,   default=1,      choices=range(1,4095),  help="Empty Value")
    core_range_param_group.add_argument("--depth",              type=int,   default=1024,	choices=range(3,32769), help="FIFO Depth")

    # Core fix value parameters.
    core_fix_param_group.add_argument("--data_width_read",  type=int,   default=36,  	choices=[i for i in range(1, 1025)],   help="FIFO Read Width")
    core_fix_param_group.add_argument("--DEPTH",            type=int,   default=1024,   choices=[4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768],   help="FIFO Depth")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--synchronous",             type=bool,   default=True,    help="Synchronous / Asynchronous Clock")
    core_bool_param_group.add_argument("--first_word_fall_through", type=bool,   default=False,   help="Fist Word Fall Through")
    core_bool_param_group.add_argument("--full_threshold",          type=bool,   default=False,	  help="Full Threshold")
    core_bool_param_group.add_argument("--empty_threshold",         type=bool,   default=False,   help="Empty Threshold")
    core_bool_param_group.add_argument("--BRAM",                    type=bool,   default=True,    help="Block or Distributed RAM")
    core_bool_param_group.add_argument("--asymmetric",              type=bool,   default=True,   help="Asymmetric Data Widths for Read and Write ports.")

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

    if (args.BRAM == False and args.synchronous == False):
        depth = args.DEPTH
    else:
        depth = args.depth
    if (args.asymmetric):
        data_width_read  = args.data_width_read
        data_width_write = args.data_width_write
    else:
        data_width_read  = args.data_width
        data_width_write = args.data_width
        
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        buses_write = divide_n_bit_number(data_width_write)
        remaining_memory = 0
        num_9K = 0
        num_18K = 0
        total_mem = 0
        while total_mem < 128:
            for i, bus in enumerate(buses_write):
                if (total_mem < 128):
                    if (len(bus) <= 9):
                        memory = 1024
                        remaining_memory = remaining_memory + (len(bus) * memory)
                        num_9K = num_9K + 1
                        if (num_9K == 4):
                            total_mem = total_mem + 1
                            num_9K = 0
                    elif (len(bus) <= 18):
                        memory = 1024
                        num_18K = num_18K + 1
                        remaining_memory = remaining_memory + (len(bus) * memory)
                        if (num_18K == 2):
                            total_mem = total_mem + 1
                            num_18K = 0
                    elif (len(bus) <= 36):
                        memory = 1024
                        remaining_memory = remaining_memory + (len(bus) * memory)
                        total_mem = total_mem + 1
        if (args.BRAM == False):
            dep_dict.update({
                'asymmetric'    :   'True'
            })
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
            if (args.asymmetric):
                option_strings_to_remove = ['--data_width']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                if (math.ceil(math.log2(args.depth)) != math.floor(math.log2(args.depth))):
                    parser._actions[5].default = 2 ** round(math.log2(args.depth))
                parser._actions[2].choices = range(2, args.DEPTH)
                parser._actions[3].choices = range(1, args.DEPTH)
                if (args.full_value >= args.DEPTH):
                    parser._actions[2].default = args.DEPTH - 1
                if (args.empty_value >= args.DEPTH):    
                    parser._actions[3].default = 1
                parser._actions[4].choices = factors_multiples(args.data_width_write)
                parser._actions[4].default = args.data_width_write
            else:
                option_strings_to_remove = ['--data_width_read']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                option_strings_to_remove = ['--data_width_write']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                if (math.ceil(math.log2(args.depth)) != math.floor(math.log2(args.depth))):
                    parser._actions[4].default = 2 ** round(math.log2(args.depth))
                parser._actions[2].choices = range(2, args.DEPTH)
                parser._actions[3].choices = range(1, args.DEPTH)
                if (args.full_value >= args.DEPTH):
                    parser._actions[2].default = args.DEPTH - 1
                if (args.empty_value >= args.DEPTH):    
                    parser._actions[3].default = 1
                parser._actions[4].choices = [4 * (2 ** i) for i in range(int(math.log2(remaining_memory/args.data_width) - 1))]
        else:
            option_strings_to_remove = ['--DEPTH']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            parser._actions[4].choices = range(2, int(remaining_memory/data_width_write) + 1)
            if (args.asymmetric):
                option_strings_to_remove = ['--data_width']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                parser._actions[2].choices = range(2, args.depth)
                parser._actions[3].choices = range(1, args.depth)
                if (args.full_value >= args.depth):
                    parser._actions[2].default = args.depth - 1
                if (args.empty_value >= args.depth):    
                    parser._actions[3].default = 1
                parser._actions[5].choices = factors_multiples(args.data_width_write)
                parser._actions[5].default = args.data_width_write
            else:
                option_strings_to_remove = ['--data_width_read']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                option_strings_to_remove = ['--data_width_write']
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

    # Create Generator -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = FIFOGenerator(platform,
        data_width_read   				= data_width_read,
        data_width_write                = data_width_write,
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
        build_name = args.build_name.rsplit( ".", 1 )[ 0 ]
        file = os.path.join(args.build_dir, "rapidsilicon/ip/fifo_generator/v1_0", build_name, "sim/testbench.v")
        file = Path(file)
        text = file.read_text()
        text = text.replace("localparam DEPTH = 2048", "localparam DEPTH = %s" % depth)
        file.write_text(text)
        text = text.replace("FIFO_generator", "%s" % build_name)
        file.write_text(text)
        text = text.replace("localparam WRITE_WIDTH = 36", "localparam WRITE_WIDTH = %s" % data_width_write)
        file.write_text(text)
        text = text.replace("localparam READ_WIDTH = 36", "localparam READ_WIDTH = %s" % data_width_read)
        file.write_text(text)
        if (not args.synchronous):
            if (args.BRAM):
                text = text.replace("== mem [i]", "== mem[i - 2]")
                file.write_text(text)
                text = text.replace("mem[i], dout, i", "mem[i - 2], dout, i - 2")
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
    
