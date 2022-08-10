#!/usr/bin/env python3

# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os
import json
import argparse
import shutil
from datetime import datetime

from migen import *

from litex.build.generic_platform import *
from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect import stream
from litex.soc.interconnect.axi import *


# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS FIFO CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--depth",          default=1024,                 help="FIFO Depth")
    core_group.add_argument("--data_width",     default=8,                    help="FIFO Data Width")
    core_group.add_argument("--last_en",        default=1,                    help="FIFO Last Enable 0 or 1")
    core_group.add_argument("--id_en",          default=0,                    help="FIFO ID Enable 0 or 1")
    core_group.add_argument("--id_width",       default=8,                    help="FIFO ID Width")
    core_group.add_argument("--dest_en",        default=0,                    help="FIFO Destination Enable 0 or 1")
    core_group.add_argument("--dest_width",     default=8,                    help="FIFO Destination Width")
    core_group.add_argument("--user_en",        default=1,                    help="FIFO User Enable 0 or 1")
    core_group.add_argument("--user_width",     default=1,                    help="FIFO User Width")
    core_group.add_argument("--pip_out",        default=2,                    help="FIFO Pipeline Output from 0 to 2")
    core_group.add_argument("--frame_fifo",     default=0,                    help="FIFO Frame 0 or 1")
    core_group.add_argument("--drop_bad_frame", default=0,                    help="FIFO Drop Bad Frame 0 or 1")
    core_group.add_argument("--drop_when_full", default=0,                    help="FIFO Drop Frame when FIFO is Full")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build_dir",     default="",                     help="Build Directory")
    build_group.add_argument("--build_name",    default="axis_fifo",            help="Build Folder Name")
    build_group.add_argument("--mod_name",      default="axis_fifo_wrapper",    help="Module Name and File Name of the RTL")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        with open(args.json, 'rt') as f:
            t_args = argparse.Namespace()
            t_args.__dict__.update(json.load(f))
            args = parser.parse_args(namespace=t_args)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        print(json.dumps(vars(args), indent=4))

    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform("", io=[], toolchain="raptor")

    rtl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "src")

    litex_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "litex_sim")

    gen_path = os.path.join("axis_fifo_gen.py")

    # Remove build extension when specified --------------------------------------------------------
    args.build_name = os.path.splitext(args.build_name)[0]

    # Build Project Directory ----------------------------------------------------------------------
    if args.build:
        # Build Path
        build_path = os.path.join(args.build_dir, 'ip_build/rapidsilicon/ip/axis_fifo/v1_0/' + (args.mod_name))
        if not os.path.exists(build_path):
            os.makedirs(build_path)
            shutil.copy(gen_path, build_path)

        # Litex_sim Path
        litex_sim_path = os.path.join(build_path, "litex_sim")
        if not os.path.exists(litex_sim_path):    
            os.makedirs(litex_sim_path)

        # Simulation Path
        sim_path = os.path.join(build_path, "sim")
        if not os.path.exists(sim_path):    
            os.makedirs(sim_path)

        # Source Path
        src_path = os.path.join(build_path, "src")
        if not os.path.exists(src_path):    
            os.makedirs(src_path) 

        # Synthesis Path
        synth_path = os.path.join(build_path, "synth")
        if not os.path.exists(synth_path):    
            os.makedirs(synth_path) 
        # Design Path
        design_path = os.path.join("../src", (args.mod_name + ".v")) 

        # Copy RTL from Source to Destination        
        rtl_files = os.listdir(rtl_path)
        for file_name in rtl_files:
            full_file_path = os.path.join(rtl_path, file_name)
            if os.path.isfile(full_file_path):
                shutil.copy(full_file_path, src_path)

        # Copy litex_sim Data from Source to Destination        
        litex_files = os.listdir(litex_path)
        for file_name in litex_files:
            full_file_path = os.path.join(litex_path, file_name)
            if os.path.isfile(full_file_path):
                shutil.copy(full_file_path, litex_sim_path)
                

        # TCL File Content        
        tcl = []
        # Create Design.
        tcl.append(f"create_design {args.build_name}")
        # Set Device.
        tcl.append(f"target_device {'GEMINI'}")
        # Add Include Path.
        tcl.append(f"add_library_path {'../src'}")
        # Add Sources.
#        for f, typ, lib in file_name:
        tcl.append(f"add_design_file {design_path}")
        # Set Top Module.
        tcl.append(f"set_top_module {args.mod_name}")
        # Add Timings Constraints.
#        tcl.append(f"add_constraint_file {args.build_name}.sdc")
        # Run.
        tcl.append("synthesize")

        # Generate .tcl file
        tcl_path = os.path.join(synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()

    # Generate RTL Wrapper
    if args.mod_name:
        wrapper_path = os.path.join(src_path, (args.mod_name + ".v"))
        with open(wrapper_path, "w") as f:

#-------------------------------------------------------------------------------
# ------------------------- RTL WRAPPER ----------------------------------------
#-------------------------------------------------------------------------------
            f.write ("""
//////////////////////////////////////////////////////////////////////////////////////////
// For Reference: https://github.com/alexforencich/verilog-i2c/blob/master/rtl/axis_fifo.v
//////////////////////////////////////////////////////////////////////////////////////////
/*
Copyright (c) 2013 - 2018 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
//////////////////////////////////////////////////////////////////////////////////////////\n\n
""")
            f.write ("// Created on: {}\n// Language: Verilog 2001\n\n".format(datetime.now()))
            f.write ("`resetall \n`timescale 1ns/ 1ps \n`default_nettype none \n\n")
            f.write ("""module {} #(""".format(args.mod_name))

            f.write ("""
        // FIFO depth in words
        // KEEP_WIDTH words per cycle if KEEP_ENABLE set
        // Rounded up to nearest power of 2 cycles
        localparam DEPTH = {}, """.format(args.depth))

            f.write ("""
        // Width of AXI stream interfaces in bits
        localparam DATA_WIDTH = {}, """.format(args.data_width))

            f.write ("""
        // Propagate tkeep signal
        // If disabled, tkeep assumed to be 1'b1
        parameter KEEP_ENABLE = (DATA_WIDTH>8),
        // tkeep signal width (words per cycle)
        parameter KEEP_WIDTH = (DATA_WIDTH/8),""")                

            f.write ("""
        // Propagate tlast signal
        localparam LAST_ENABLE = {}, """.format(args.last_en))

            f.write ("""
        // Propagate tid signal
        localparam ID_ENABLE = {}, """.format(args.id_en))

            f.write ("""
        // tid signal width
        localparam ID_WIDTH = {}, """.format(args.id_width))

            f.write ("""
        // Propagate tdest signal
        localparam DEST_ENABLE = {}, """.format(args.dest_en))

            f.write ("""
        // tdest signal width
        localparam DEST_WIDTH = {}, """.format(args.dest_width))

            f.write ("""
        // Propagate tuser signal
        localparam USER_ENABLE = {}, """.format(args.user_en))

            f.write ("""
        // tuser signal width
        localparam USER_WIDTH = {}, """.format(args.user_width))

            f.write ("""
        // number of output pipeline registers
        localparam PIPELINE_OUTPUT = {}, """.format(args.pip_out))

            f.write ("""
        // Frame FIFO mode - operate on frames instead of cycles
        // When set, m_axis_tvalid will not be deasserted within a frame
        // Requires LAST_ENABLE set
        localparam FRAME_FIFO = {}, """.format(args.frame_fifo))

            f.write ("""
        // Drop frames marked bad
        // Requires FRAME_FIFO set
        localparam DROP_BAD_FRAME = {}, """.format(args.drop_bad_frame))

            f.write ("""
        // Drop incoming frames when full
        // When set, s_axis_tready is always asserted
        // Requires FRAME_FIFO set
        localparam DROP_WHEN_FULL = {}, """.format(args.drop_when_full))    

            f.write("""
        // tuser value for bad frame marker
        localparam USER_BAD_FRAME_VALUE = 1'b1,
        // tuser mask for bad frame marker
        parameter USER_BAD_FRAME_MASK = 1'b1
)
(
    input  wire                   clk,
    input  wire                   rst,

    /*
     * AXI input
     */
    input  wire [DATA_WIDTH-1:0]  s_axis_tdata,
    input  wire [KEEP_WIDTH-1:0]  s_axis_tkeep,
    input  wire                   s_axis_tvalid,
    output wire                   s_axis_tready,
    input  wire                   s_axis_tlast,
    input  wire [ID_WIDTH-1:0]    s_axis_tid,
    input  wire [DEST_WIDTH-1:0]  s_axis_tdest,
    input  wire [USER_WIDTH-1:0]  s_axis_tuser,

    /*
     * AXI output
     */
    output wire [DATA_WIDTH-1:0]  m_axis_tdata,
    output wire [KEEP_WIDTH-1:0]  m_axis_tkeep,
    output wire                   m_axis_tvalid,
    input  wire                   m_axis_tready,
    output wire                   m_axis_tlast,
    output wire [ID_WIDTH-1:0]    m_axis_tid,
    output wire [DEST_WIDTH-1:0]  m_axis_tdest,
    output wire [USER_WIDTH-1:0]  m_axis_tuser,

    /*
     * Status
     */
    output wire                   status_overflow,
    output wire                   status_bad_frame,
    output wire                   status_good_frame,
    output wire                   status_full,
    output wire                   status_empty
);

""")
            f.write("axis_fifo #(\n.DEPTH(DEPTH),\n.DATA_WIDTH(DATA_WIDTH),\n.LAST_ENABLE(LAST_ENABLE),\n.ID_ENABLE(ID_ENABLE),\n.ID_WIDTH(ID_WIDTH),\n.DEST_ENABLE(DEST_ENABLE),\n.DEST_WIDTH(DEST_WIDTH),\n.USER_ENABLE(USER_ENABLE),\n.USER_WIDTH(USER_WIDTH),\n.PIPELINE_OUTPUT(PIPELINE_OUTPUT),\n.FRAME_FIFO(FRAME_FIFO),\n.DROP_BAD_FRAME(DROP_BAD_FRAME),\n.DROP_WHEN_FULL(DROP_WHEN_FULL)\n)")
            f.write("""

axis_fifo_inst
(
.clk(clk),
.rst(rst),

/*
 * AXI input
 */
.s_axis_tdata(s_axis_tdata),
.s_axis_tkeep(s_axis_tkeep),
.s_axis_tvalid(s_axis_tvalid),
.s_axis_tready(s_axis_tready),
.s_axis_tlast(s_axis_tlast),
.s_axis_tid(s_axis_tid),
.s_axis_tdest(s_axis_tdest),
.s_axis_tuser(s_axis_tuser),


/*
 * AXI output
 */
.m_axis_tdata(m_axis_tdata),
.m_axis_tkeep(m_axis_tkeep),
.m_axis_tvalid(m_axis_tvalid),
.m_axis_tready(m_axis_tready),
.m_axis_tlast(m_axis_tlast),
.m_axis_tid(m_axis_tid),
.m_axis_tdest(m_axis_tdest),
.m_axis_tuser(m_axis_tuser),


/*
 * Status
 */
.status_overflow(status_overflow),
.status_bad_frame(status_bad_frame),
.status_good_frame(status_good_frame),
.status_full(status_full),
.status_empty(status_empty)
);

endmodule

`resetall
             """)
            f.close()

if __name__ == "__main__":
    main()
