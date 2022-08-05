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
    parser = argparse.ArgumentParser(description="AXI GPIO CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core Parameters")
    core_group.add_argument("--data_width",     default=32,                   help="GPIO Data Width 8,16,32")
    core_group.add_argument("--addr_width",     default=16,                   help="GPIO Address Width 8,16")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build Parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build_dir",     default="",                     help="Build Directory")
    build_group.add_argument("--build_name",    default="axi_gpio",             help="Build Folder Name")
    build_group.add_argument("--mod_name",      default="axi_gpio_wrapper",     help="Module Name and File Name of the RTL")

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

    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform("", io=[], toolchain="raptor")
    rtl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "src")

    # Remove build extension when specified --------------------------------------------------------
    args.build_name = os.path.splitext(args.build_name)[0]

    # Build Project Directory ----------------------------------------------------------------------
    if args.build:
        # Build Path 
        build_path = os.path.join(args.build_dir, (args.build_name) + '/rapidsilicon/ip/axi_gpio/v1_0/')
        if not os.path.exists(build_path):
            os.makedirs(build_path)

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
        design_path = os.path.join("../src", (args.mod_name + ".sv"))  

        # Copy RTL from Source to Destination
        src_files = os.listdir(rtl_path)
        for file_name in src_files:
            full_file_name = os.path.join(rtl_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, src_path)        

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
        
        # Generate .tcl File
        tcl_path = os.path.join(synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()

    # Generate RTL Wrapper
    if args.mod_name:
        wrapper_path = os.path.join(src_path, (args.mod_name + ".sv"))
        with open(wrapper_path,'w') as f:

#-------------------------------------------------------------------------------
# ------------------------- RTL WRAPPER ----------------------------------------
#-------------------------------------------------------------------------------
            f.write ("""
////////////////////////////////////////////////////////////////////////////////
/*
Copyright (c) 2018 Alex Forencich

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
////////////////////////////////////////////////////////////////////////////////\n
""")
            f.write ("// Created on: {}\n// Language: Verilog 2001\n\n".format(datetime.now()))
            f.write ("`resetall \n`timescale 1ns/ 1ps \n`default_nettype none \n \n")
            f.write ("""module {} #(""".format(args.mod_name))

            f.write ("""
    // Width of data bus in bits
    localparam DATA_WIDTH = {}, """.format(args.data_width))

            f.write ("""
    // Width of address bus in bits
    localparam ADDR_WIDTH = {},""".format(args.addr_width))

            f.write("""
    // Width of wstrb (width of data bus in words)
    localparam STRB_WIDTH = (DATA_WIDTH/8)
)
(
  input  wire                           CLK, 
  input  wire			                RSTN, 
  input  wire  [DATA_WIDTH-1:0]    		GPIN,                 
  output wire  [DATA_WIDTH-1:0]    		GPOUT,                 
  output wire		                    INT,
  
  // write address channel
  input  wire  [ADDR_WIDTH-1:0]    		AWADDR,
  input  wire  [2:0]     		        AWPROT,
  input  wire			                AWVALID,
  output wire           		        AWREADY,
  
  // write data channel
  input  wire  [DATA_WIDTH-1:0]		    WDATA,
  input  wire  [STRB_WIDTH-1:0]		    WSTRB,
  input  wire			                WVALID,
  output wire 		                    WREADY,
  
  // write response channel
  output wire  [1:0]		            BRESP,
  output wire		                    BVALID,
  input  wire			                BREADY,

  // read address channel
  input  wire  [ADDR_WIDTH-1:0]		    ARADDR,
  input  wire  [2:0]		            ARPROT,
  input  wire                    		ARVALID,
  output wire		                    ARREADY,

  // read data channel
  output wire  [DATA_WIDTH-1:0]		    RDATA,
  output wire  [1:0]		            RRESP,
  output wire		                    RVALID,
  input  wire                    		RREADY
);

""")
            f.write("axi4lite_gpio #(\n.DATA_WIDTH(DATA_WIDTH),\n.ADDR_WIDTH(ADDR_WIDTH)\n)")
            f.write("""
gpio_inst(
.WDATA(WDATA),
.WSTRB(WSTRB),
.WVALID(WVALID),
.WREADY(WREADY),

.BRESP(BRESP),
.BVALID(BVALID),
.BREADY(BREADY),

.ARADDR(ARADDR),
.ARPROT(ARPROT),
.ARVALID(ARVALID),
.ARREADY(ARREADY),

.RDATA(RDATA),
.RRESP(RRESP),
.RVALID(RVALID),
.RREADY(RREADY)
);

endmodule

`resetall
        """)
        f.close()

if __name__ == "__main__":
    main()
