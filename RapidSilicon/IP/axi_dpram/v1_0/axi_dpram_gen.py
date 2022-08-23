#!/usr/bin/env python3

# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os
import json
import argparse
import shutil
from datetime import datetime

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI DPRAM CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",     default=32,                   help="DPRAM Data Width 8,16,32,64")
    core_group.add_argument("--addr_width",     default=16,                   help="DPRAM Address Width 8,16")
    core_group.add_argument("--id_width",       default=8,                    help="DPRAM ID Width from 1 - 8")
    core_group.add_argument("--a_pip_out",      default=0,                    help="DPRAM A Pipeline Output 0 or 1")
    core_group.add_argument("--b_pip_out",      default=0,                    help="DPRAM B Pipeline Output 0 or 1")
    core_group.add_argument("--a_interleave",   default=0,                    help="DPRAM A Interleave 0 or 1")
    core_group.add_argument("--b_interleave",   default=0,                    help="DPRAM B Interleave 0 or 1")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="",                         help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_dpram_wrapper",        help="Build Folder Name, Build RTL File Name and Module Name")

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

    # Remove build extension when specified.
    args.build_name = os.path.splitext(args.build_name)[0]

    # Build Project Directory ----------------------------------------------------------------------
    if args.build:
        # Build Path
        build_path = os.path.join(args.build_dir, 'ip_build/rapidsilicon/ip/axi_dpram/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "axi_dpram_gen.py"))
        
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
        design_path = os.path.join("../src", (args.build_name + ".v")) 

        # Copy RTL from Source to Destination
        rtl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "src")        
        rtl_files = os.listdir(rtl_path)
        for file_name in rtl_files:
            full_file_path = os.path.join(rtl_path, file_name)
            if os.path.isfile(full_file_path):
                shutil.copy(full_file_path, src_path)

        # Copy litex_sim Data from Source to Destination  
        litex_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "litex_sim")      
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
        tcl.append(f"set_top_module {args.build_name}")
        # Add Timings Constraints.
#        tcl.append(f"add_constraint_file {args.build_name}.sdc")
        # Run.
        tcl.append("synthesize")
        tcl.append("packing")
        tcl.append("global_placement")
        tcl.append("place")
        tcl.append("route")
        tcl.append("sta")
        tcl.append("power")
        tcl.append("bitstream")

        # Generate .tcl file
        tcl_path = os.path.join(synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()

        # Generate RTL Wrapper
        if args.build_name:
            wrapper_path = os.path.join(src_path, (args.build_name + ".v"))
            with open(wrapper_path, "w") as f:

#-------------------------------------------------------------------------------
# ------------------------- RTL WRAPPER ----------------------------------------
#-------------------------------------------------------------------------------
                f.write ("""
////////////////////////////////////////////////////////////////////////////////////////////
// For Reference: https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_dp_ram.v
////////////////////////////////////////////////////////////////////////////////////////////
/*
Copyright (c) 2019 Alex Forencich

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
////////////////////////////////////////////////////////////////////////////////////////////\n\n
""")
                f.write ("// Created on: {}\n// Language: Verilog 2001\n\n".format(datetime.now()))
                f.write ("`resetall \n`timescale 1ns/ 1ps \n`default_nettype none \n\n")
                f.write ("""module {} #(""".format(args.build_name))

                f.write ("""
    // Width of data bus in bits
    localparam DATA_WIDTH = {}, """.format(args.data_width))

                f.write ("""
    // Width of address bus in bits
    localparam ADDR_WIDTH = {}, """.format(args.addr_width))

                f.write ("""
    // Width of ID signal
    localparam ID_WIDTH = {}, """.format(args.id_width))

                f.write ("""
    // Extra pipeline register on output port A
    localparam A_PIPELINE_OUTPUT = {}, """.format(args.a_pip_out))

                f.write ("""
    // Extra pipeline register on output port B
    localparam B_PIPELINE_OUTPUT = {}, """.format(args.b_pip_out))

                f.write ("""
    // Interleave read and write burst cycles on port A
    localparam A_INTERLEAVE = {}, """.format(args.a_interleave))

                f.write ("""
    // Interleave read and write burst cycles on port B
    localparam B_INTERLEAVE = {}, """.format(args.b_interleave))

                f.write("""
    // Width of wstrb (width of data bus in words)
    localparam STRB_WIDTH = (DATA_WIDTH/8)
)
(
    input  wire                   a_clk,
    input  wire                   a_rst,

    input  wire                   b_clk,
    input  wire                   b_rst,
    
    // Port A
    input  wire [ID_WIDTH-1:0]    s_axi_a_awid,
    input  wire [ADDR_WIDTH-1:0]  s_axi_a_awaddr,
    input  wire [7:0]             s_axi_a_awlen,
    input  wire [2:0]             s_axi_a_awsize,
    input  wire [1:0]             s_axi_a_awburst,
    input  wire                   s_axi_a_awlock,
    input  wire [3:0]             s_axi_a_awcache,
    input  wire [2:0]             s_axi_a_awprot,
    input  wire                   s_axi_a_awvalid,
    output wire                   s_axi_a_awready,
    input  wire [DATA_WIDTH-1:0]  s_axi_a_wdata,
    input  wire [STRB_WIDTH-1:0]  s_axi_a_wstrb,
    input  wire                   s_axi_a_wlast,
    input  wire                   s_axi_a_wvalid,
    output wire                   s_axi_a_wready,
    output wire [ID_WIDTH-1:0]    s_axi_a_bid,
    output wire [1:0]             s_axi_a_bresp,
    output wire                   s_axi_a_bvalid,
    input  wire                   s_axi_a_bready,
    input  wire [ID_WIDTH-1:0]    s_axi_a_arid,
    input  wire [ADDR_WIDTH-1:0]  s_axi_a_araddr,
    input  wire [7:0]             s_axi_a_arlen,
    input  wire [2:0]             s_axi_a_arsize,
    input  wire [1:0]             s_axi_a_arburst,
    input  wire                   s_axi_a_arlock,
    input  wire [3:0]             s_axi_a_arcache,
    input  wire [2:0]             s_axi_a_arprot,
    input  wire                   s_axi_a_arvalid,
    output wire                   s_axi_a_arready,
    output wire [ID_WIDTH-1:0]    s_axi_a_rid,
    output wire [DATA_WIDTH-1:0]  s_axi_a_rdata,
    output wire [1:0]             s_axi_a_rresp,
    output wire                   s_axi_a_rlast,
    output wire                   s_axi_a_rvalid,
    input  wire                   s_axi_a_rready,

    // Port B
    input  wire [ID_WIDTH-1:0]    s_axi_b_awid,
    input  wire [ADDR_WIDTH-1:0]  s_axi_b_awaddr,
    input  wire [7:0]             s_axi_b_awlen,
    input  wire [2:0]             s_axi_b_awsize,
    input  wire [1:0]             s_axi_b_awburst,
    input  wire                   s_axi_b_awlock,
    input  wire [3:0]             s_axi_b_awcache,
    input  wire [2:0]             s_axi_b_awprot,
    input  wire                   s_axi_b_awvalid,
    output wire                   s_axi_b_awready,
    input  wire [DATA_WIDTH-1:0]  s_axi_b_wdata,
    input  wire [STRB_WIDTH-1:0]  s_axi_b_wstrb,
    input  wire                   s_axi_b_wlast,
    input  wire                   s_axi_b_wvalid,
    output wire                   s_axi_b_wready,
    output wire [ID_WIDTH-1:0]    s_axi_b_bid,
    output wire [1:0]             s_axi_b_bresp,
    output wire                   s_axi_b_bvalid,
    input  wire                   s_axi_b_bready,
    input  wire [ID_WIDTH-1:0]    s_axi_b_arid,
    input  wire [ADDR_WIDTH-1:0]  s_axi_b_araddr,
    input  wire [7:0]             s_axi_b_arlen,
    input  wire [2:0]             s_axi_b_arsize,
    input  wire [1:0]             s_axi_b_arburst,
    input  wire                   s_axi_b_arlock,
    input  wire [3:0]             s_axi_b_arcache,
    input  wire [2:0]             s_axi_b_arprot,
    input  wire                   s_axi_b_arvalid,
    output wire                   s_axi_b_arready,
    output wire [ID_WIDTH-1:0]    s_axi_b_rid,
    output wire [DATA_WIDTH-1:0]  s_axi_b_rdata,
    output wire [1:0]             s_axi_b_rresp,
    output wire                   s_axi_b_rlast,
    output wire                   s_axi_b_rvalid,
    input  wire                   s_axi_b_rready
);

""")
                f.write("axi_dp_ram #(\n.DATA_WIDTH(DATA_WIDTH),\n.ADDR_WIDTH(ADDR_WIDTH),\n.ID_WIDTH(ID_WIDTH),\n.A_PIPELINE_OUTPUT(A_PIPELINE_OUTPUT),\n.B_PIPELINE_OUTPUT(B_PIPELINE_OUTPUT),\n.A_INTERLEAVE(A_INTERLEAVE),\n.B_INTERLEAVE(B_INTERLEAVE)\n)")
                f.write("""

axi_dp_ram_inst
(
.a_clk(a_clk),
.a_rst(a_rst),

.s_axi_a_awid(s_axi_a_awid),
.s_axi_a_awaddr(s_axi_a_awaddr),
.s_axi_a_awlen(s_axi_a_awlen),
.s_axi_a_awsize(s_axi_a_awsize),
.s_axi_a_awburst(s_axi_a_awburst),
.s_axi_a_awlock(s_axi_a_awlock),
.s_axi_a_awcache(s_axi_a_awcache),
.s_axi_a_awprot(s_axi_a_awprot),
.s_axi_a_awvalid(s_axi_a_awvalid),
.s_axi_a_awready(s_axi_a_awready),

.s_axi_a_wdata(s_axi_a_wdata),
.s_axi_a_wstrb(s_axi_a_wstrb),
.s_axi_a_wlast(s_axi_a_wlast),
.s_axi_a_wvalid(s_axi_a_wvalid),
.s_axi_a_wready(s_axi_a_wready),

.s_axi_a_bid(s_axi_a_bid),  
.s_axi_a_bresp(s_axi_a_bresp),
.s_axi_a_bvalid(s_axi_a_bvalid),
.s_axi_a_bready(s_axi_a_bready),

.s_axi_a_arid(s_axi_a_arid),
.s_axi_a_araddr(s_axi_a_araddr),
.s_axi_a_arlen(s_axi_a_arlen),
.s_axi_a_arsize(s_axi_a_arsize),
.s_axi_a_arburst(s_axi_a_arburst),
.s_axi_a_arlock(s_axi_a_arlock),
.s_axi_a_arcache(s_axi_a_arcache),
.s_axi_a_arprot(s_axi_a_arprot),
.s_axi_a_arvalid(s_axi_a_arvalid),
.s_axi_a_arready(s_axi_a_arready),

.s_axi_a_rid(s_axi_a_rid),
.s_axi_a_rdata(s_axi_a_rdata),
.s_axi_a_rresp(s_axi_a_rresp),
.s_axi_a_rlast(s_axi_a_rlast),
.s_axi_a_rvalid(s_axi_a_rvalid),
.s_axi_a_rready(s_axi_a_rready),


.b_clk(b_clk),
.b_rst(b_rst),

.s_axi_b_awid(s_axi_b_awid),
.s_axi_b_awaddr(s_axi_b_awaddr),
.s_axi_b_awlen(s_axi_b_awlen),
.s_axi_b_awsize(s_axi_b_awsize),
.s_axi_b_awburst(s_axi_b_awburst),
.s_axi_b_awlock(s_axi_b_awlock),
.s_axi_b_awcache(s_axi_b_awcache),
.s_axi_b_awprot(s_axi_b_awprot),
.s_axi_b_awvalid(s_axi_b_awvalid),
.s_axi_b_awready(s_axi_b_awready),

.s_axi_b_wdata(s_axi_b_wdata),
.s_axi_b_wstrb(s_axi_b_wstrb),
.s_axi_b_wlast(s_axi_b_wlast),
.s_axi_b_wvalid(s_axi_b_wvalid),
.s_axi_b_wready(s_axi_b_wready),

.s_axi_b_bid(s_axi_b_bid),  
.s_axi_b_bresp(s_axi_b_bresp),
.s_axi_b_bvalid(s_axi_b_bvalid),
.s_axi_b_bready(s_axi_b_bready),

.s_axi_b_arid(s_axi_b_arid),
.s_axi_b_araddr(s_axi_b_araddr),
.s_axi_b_arlen(s_axi_b_arlen),
.s_axi_b_arsize(s_axi_b_arsize),
.s_axi_b_arburst(s_axi_b_arburst),
.s_axi_b_arlock(s_axi_b_arlock),
.s_axi_b_arcache(s_axi_b_arcache),
.s_axi_b_arprot(s_axi_b_arprot),
.s_axi_b_arvalid(s_axi_b_arvalid),
.s_axi_b_arready(s_axi_b_arready),

.s_axi_b_rid(s_axi_b_rid),
.s_axi_b_rdata(s_axi_b_rdata),
.s_axi_b_rresp(s_axi_b_rresp),
.s_axi_b_rlast(s_axi_b_rlast),
.s_axi_b_rvalid(s_axi_b_rvalid),
.s_axi_b_rready(s_axi_b_rready)

);

endmodule

`resetall
             """)
                f.close()

if __name__ == "__main__":
    main()
