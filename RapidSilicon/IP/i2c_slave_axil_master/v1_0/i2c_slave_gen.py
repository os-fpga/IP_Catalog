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
    parser = argparse.ArgumentParser(description="I2C SLAVE CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core Parameters")
    core_group.add_argument("--data_width",     default=32,                   help="I2C_slave Data Width 8,16,32")
    core_group.add_argument("--addr_width",     default=16,                   help="I2C_slave Address Width 8,16")
    core_group.add_argument("--filter_len",     default=4,                    help="I2C_slave Filter Lenght from 0 - 4")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build Parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="",                     help="Build Directory")
    build_group.add_argument("--build-name",    default="i2c_slave_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

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
        build_path = os.path.join(args.build_dir, 'ip_build/rapidsilicon/ip/i2c_slave/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "i2c_slave_gen.py"))
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

        
        # Generate .tcl File
        tcl_path = os.path.join(synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()

        # Generate RTL Wrapper
        if args.build_name:
            wrapper_path = os.path.join(src_path, (args.build_name + ".v"))
            with open(wrapper_path,'w') as f:

#-------------------------------------------------------------------------------
# ------------------------- RTL WRAPPER ----------------------------------------
#-------------------------------------------------------------------------------
                f.write ("""
///////////////////////////////////////////////////////////////////////////////////////////////////////
// For Reference: https://github.com/alexforencich/verilog-i2c/blob/master/rtl/i2c_slave_axil_master.v      
///////////////////////////////////////////////////////////////////////////////////////////////////////
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
///////////////////////////////////////////////////////////////////////////////////////////////////////\n
""")
                f.write ("// Created on: {}\n// Language: Verilog 2001\n\n".format(datetime.now()))
                f.write ("`resetall \n`timescale 1ns/ 1ps \n`default_nettype none \n \n")
                f.write ("""module {} #(""".format(args.build_name))

                f.write ("""
    // Width of data bus in bits
    localparam DATA_WIDTH = {}, """.format(args.data_width))

                f.write ("""
    // Width of address bus in bits
    localparam ADDR_WIDTH = {},""".format(args.addr_width))

                f.write ("""
    // Length of filter
    localparam FILTER_LEN = {},""".format(args.filter_len))

                f.write("""
    // Width of wstrb (width of data bus in words)
    localparam STRB_WIDTH = (DATA_WIDTH/8)
)
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
     * AXI lite master interface
     */
    output wire [ADDR_WIDTH-1:0]  m_axil_awaddr,
    output wire [2:0]             m_axil_awprot,
    output wire                   m_axil_awvalid,
    input  wire                   m_axil_awready,
    output wire [DATA_WIDTH-1:0]  m_axil_wdata,
    output wire [STRB_WIDTH-1:0]  m_axil_wstrb,
    output wire                   m_axil_wvalid,
    input  wire                   m_axil_wready,
    input  wire [1:0]             m_axil_bresp,
    input  wire                   m_axil_bvalid,
    output wire                   m_axil_bready,
    output wire [ADDR_WIDTH-1:0]  m_axil_araddr,
    output wire [2:0]             m_axil_arprot,
    output wire                   m_axil_arvalid,
    input  wire                   m_axil_arready,
    input  wire [DATA_WIDTH-1:0]  m_axil_rdata,
    input  wire [1:0]             m_axil_rresp,
    input  wire                   m_axil_rvalid,
    output wire                   m_axil_rready,

    /*
     * Status
     */
    output wire                   busy,
    output wire                   bus_addressed,
    output wire                   bus_active,

    /*
     * Configuration
     */
    input  wire                   enable,
    input  wire [6:0]             device_address
);

""")
                f.write("i2c_slave_axil_master #(\n.DATA_WIDTH(DATA_WIDTH),\n.ADDR_WIDTH(ADDR_WIDTH),\n.FILTER_LEN(FILTER_LEN)\n)")

                f.write("""
            
i2c_inst
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

// AXI-Lite Master Interface
.m_axil_awaddr(m_axil_awaddr),
.m_axil_awprot(m_axil_awprot),
.m_axil_awvalid(m_axil_awvalid),
.m_axil_awready(m_axil_awready),

.m_axil_wdata(m_axil_wdata),
.m_axil_wstrb(m_axil_wstrb),
.m_axil_wvalid(m_axil_wvalid),
.m_axil_wready(m_axil_wready),

.m_axil_bresp(m_axil_bresp),
.m_axil_bvalid(m_axil_bvalid),
.m_axil_bready(m_axil_bready),

.m_axil_araddr(m_axil_araddr),
.m_axil_arprot(m_axil_arprot),
.m_axil_arvalid(m_axil_arvalid),
.m_axil_arready(m_axil_arready),

.m_axil_rdata(m_axil_rdata),
.m_axil_rresp(m_axil_rresp),
.m_axil_rvalid(m_axil_rvalid),
.m_axil_rready(m_axil_rready),

.busy(busy),
.bus_addressed(bus_addressed),
.bus_active(bus_active),

.enable(enable),
.device_address(device_address)
);

endmodule

`resetall
        """)
            f.close()

if __name__ == "__main__":
    main()
