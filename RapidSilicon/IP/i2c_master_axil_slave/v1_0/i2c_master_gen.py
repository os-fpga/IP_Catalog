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
    parser = argparse.ArgumentParser(description="I2C MASTER CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core Parameters")
    core_group.add_argument("--default_prescale",   default=1,        help="I2C Default Prescale 0 or 1")
    core_group.add_argument("--fixed_prescale",     default=0,        help="I2C Fixed Prescale 0 or 1")
    core_group.add_argument("--cmd_fifo",           default=1,        help="I2C FIFO Command Enable 0 or 1")
    core_group.add_argument("--cmd_addr_width",     default=5,        help="I2C FIFO Command Address Width (1-5)")
    core_group.add_argument("--write_fifo",         default=1,        help="I2C FIFO Write Enable 0 or 1")
    core_group.add_argument("--write_addr_width",   default=5,        help="I2C FIFO Write Address Width (1-5)")
    core_group.add_argument("--read_fifo",          default=1,        help="I2C FIFO Read Enable 0 or 1")
    core_group.add_argument("--read_addr_width",    default=5,        help="I2C FIFO Read Address Width (1-5)")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build Parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build_dir",     default="",                	    help="Build Directory")
    build_group.add_argument("--build_name",    default="i2c_master",   	    help="Build Folder Name")
    build_group.add_argument("--mod_name",      default="i2c_master_wrapper",   help="Module Name and File Name of the RTL")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json_template",  action="store_true",            help="Generate JSON Template")

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

# Build Project Directory ----------------------------------------------------------------------
    if args.build:
        # Build Path 
        build_path = os.path.join(args.build_dir, 'ip_build/rapidsilicon/ip/i2c_master/v1_0/' + (args.mod_name))
        gen_path = os.path.join("i2c_master_gen.py")
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
        # Add file extension
        tcl.append(f"add_library_ext .v .sv")
        # Add Sources.
#        for f, typ, lib in file_name:
        tcl.append(f"add_design_file {design_path}")
        # Set Top Module.
        tcl.append(f"set_top_module {args.mod_name}")
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
        
        # Generate .tcl File
        tcl_path = os.path.join(synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()

        # Generate RTL Wrapper
        if args.mod_name:
            wrapper_path = os.path.join(src_path, (args.mod_name + ".v"))
            with open(wrapper_path,'w') as f:

#-------------------------------------------------------------------------------
# ------------------------- RTL WRAPPER ----------------------------------------
#-------------------------------------------------------------------------------
                f.write ("""
////////////////////////////////////////////////////////////////////////////////////////////////
// For Reference: https://github.com/alexforencich/verilog-i2c/blob/master/rtl/i2c_master_axil.v      
////////////////////////////////////////////////////////////////////////////////////////////////
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
////////////////////////////////////////////////////////////////////////////////////////////////\n
""")
                f.write ("// Created on: {}\n// Language: Verilog 2001\n\n".format(datetime.now()))
                f.write ("`resetall \n`timescale 1ns/ 1ps \n`default_nettype none \n \n")
                f.write ("""module {} #(""".format(args.mod_name))

                f.write ("""
    // DEFAULT_PRESCALE
    parameter DEFAULT_PRESCALE = {}, """.format(args.default_prescale))

                f.write ("""
    // FIXED_PRESCALE
    parameter FIXED_PRESCALE = {},""".format(args.fixed_prescale))

                f.write ("""
    // CMD_FIFO
    parameter CMD_FIFO = {},""".format(args.cmd_fifo))

                f.write ("""
    // CMD_FIFO_ADDR_WIDTH
    parameter CMD_FIFO_ADDR_WIDTH = {},""".format(args.cmd_addr_width))

                f.write ("""
    // WRITE_FIFO
    parameter WRITE_FIFO = {},""".format(args.write_fifo))

                f.write ("""
    // WRITE_FIFO_ADDR_WIDTH
    parameter WRITE_FIFO_ADDR_WIDTH = {},""".format(args.write_addr_width))

                f.write ("""
    // READ_FIFO
    parameter READ_FIFO = {},""".format(args.read_fifo))

                f.write ("""
    // READ_FIFO_ADDR_WIDTH
    parameter READ_FIFO_ADDR_WIDTH = {}\n)""".format(args.read_addr_width))

                f.write("""
(
    input wire                    clk,
    input wire                    rst,

    /*
     * I2C interface
     */
    input  wire                   i2c_scl_i,
    output wire                   i2c_scl_o,
    output wire                   i2c_scl_t,
    input  wire                   i2c_sda_i,
    output wire                   i2c_sda_o,
    output wire                   i2c_sda_t,

    /*
     * Host Interface
     */
    input   wire [3:0]             s_axil_awaddr,
    input   wire [2:0]             s_axil_awprot,
    input   wire                   s_axil_awvalid,
    output  wire                   s_axil_awready,

    input   wire [31:0]            s_axil_wdata,
    input   wire [3:0]             s_axil_wstrb,
    input   wire                   s_axil_wvalid,
    output  wire                   s_axil_wready,

    output  wire [1:0]             s_axil_bresp,
    output  wire                   s_axil_bvalid,
    input   wire                   s_axil_bready,

    input   wire [3:0]             s_axil_araddr,
    input   wire [2:0]             s_axil_arprot,
    input   wire                   s_axil_arvalid,
    output  wire                   s_axil_arready,

    output  wire [31:0]            s_axil_rdata,
    output  wire [1:0]             s_axil_rresp,
    output  wire                   s_axil_rvalid,
    input   wire                   s_axil_rready
);

""")
                f.write("i2c_master_axil #(\n.DEFAULT_PRESCALE(DEFAULT_PRESCALE),\n.FIXED_PRESCALE(FIXED_PRESCALE),\n.CMD_FIFO(CMD_FIFO),\n.CMD_FIFO_ADDR_WIDTH(CMD_FIFO_ADDR_WIDTH),\n.WRITE_FIFO(WRITE_FIFO),\n.WRITE_FIFO_ADDR_WIDTH(WRITE_FIFO_ADDR_WIDTH),\n.READ_FIFO(READ_FIFO),\n.READ_FIFO_ADDR_WIDTH(READ_FIFO_ADDR_WIDTH))")

                f.write("""

i2c_master_axil_inst
(
.clk(clk),
.rst(rst),

// I2C Interface
.i2c_scl_i(i2c_scl_i),
.i2c_scl_o(i2c_scl_o),
.i2c_scl_t(i2c_scl_t),
.i2c_sda_i(i2c_sda_i),
.i2c_sda_o(i2c_sda_o),
.i2c_sda_t(i2c_sda_t),

// AXI-Lite Slave Interface
.s_axil_awaddr(s_axil_awaddr),
.s_axil_awprot(s_axil_awprot),
.s_axil_awvalid(s_axil_awvalid),
.s_axil_awready(s_axil_awready),

.s_axil_wdata(s_axil_wdata),
.s_axil_wstrb(s_axil_wstrb),
.s_axil_wvalid(s_axil_wvalid),
.s_axil_wready(s_axil_wready),

.s_axil_bresp(s_axil_bresp),
.s_axil_bvalid(s_axil_bvalid),
.s_axil_bready(s_axil_bready),

.s_axil_araddr(s_axil_araddr),
.s_axil_arprot(s_axil_arprot),
.s_axil_arvalid(s_axil_arvalid),
.s_axil_arready(s_axil_arready),

.s_axil_rdata(s_axil_rdata),
.s_axil_rresp(s_axil_rresp),
.s_axil_rvalid(s_axil_rvalid),
.s_axil_rready(s_axil_rready)
);

endmodule

`resetall
        """)
            f.close()

if __name__ == "__main__":
    main()
