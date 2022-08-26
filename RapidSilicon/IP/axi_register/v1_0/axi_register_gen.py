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
    parser = argparse.ArgumentParser(description="AXI REGISTER CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",      default=32,      help="Register Data Width 8,16,32,64,128,256,512,1024")
    core_group.add_argument("--addr_width",      default=32,      help="Register Address Width 8,16,32,64")
    core_group.add_argument("--id_width",        default=32,      help="Register ID Width from 0 - 32")

    core_group.add_argument("--aw_user_width",   default=0,       help="Register AW-User Width from 0 - 1024")
    core_group.add_argument("--w_user_width",    default=0,       help="Register W-User Width from 0 - 1024")
    core_group.add_argument("--b_user_width",    default=0,       help="Register B-User Width from 0 - 1024")
    core_group.add_argument("--ar_user_width",   default=0,       help="Register AR-User Width from 0 - 1024")
    core_group.add_argument("--r_user_width",    default=0,       help="Register R-User Width from 0 - 1024")

    core_group.add_argument("--aw_reg_type",     default=1,       help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--w_reg_type",      default=2,       help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--b_reg_type",      default=1,       help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--ar_reg_type",     default=1,       help="Register 0=bypass , 1=simple buffer , 2=skid buffer")
    core_group.add_argument("--r_reg_type",      default=2,       help="Register 0=bypass , 1=simple buffer , 2=skid buffer")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                help="Build Core")
    build_group.add_argument("--build-dir",     default="",                         help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_register_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

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
        build_path = os.path.join(args.build_dir, 'ip_build/rapidsilicon/ip/axi_register/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "axi_register_gen.py"))
        
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
//////////////////////////////////////////////////////////////////////////////////////////////
// For Reference: https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_register.v
//////////////////////////////////////////////////////////////////////////////////////////////
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
//////////////////////////////////////////////////////////////////////////////////////////////\n\n
""")
                f.write ("// Created on: {}\n// Language: Verilog 2001\n\n".format(datetime.now()))
                f.write ("`resetall \n`timescale 1ns/ 1ps \n`default_nettype none \n\n")
                f.write ("""module {} #(""".format(args.build_name))

                f.write ("""
    // Width of data bus in bits 8, 16, 32, 64, 128, 256, 512, 1024
    localparam DATA_WIDTH = {}, """.format(args.data_width))

                f.write ("""
    // Width of address bus in bits from 1 - 64
    localparam ADDR_WIDTH = {}, """.format(args.addr_width))

                f.write ("""
    // Width of ID signal from 0 - 32
    localparam ID_WIDTH = {}, """.format(args.id_width))

                f.write ("""
    // Width of awuser signal from 0 - 1024
    localparam AWUSER_WIDTH = {}, """.format(args.aw_user_width))

                f.write ("""
    // Width of wuser signal from 0 - 1024
    localparam WUSER_WIDTH = {}, """.format(args.w_user_width))

                f.write ("""
    // Width of buser signal from 0 - 1024
    localparam BUSER_WIDTH = {}, """.format(args.b_user_width))

                f.write ("""
    // Width of aruser signal from 0 - 1024
    localparam ARUSER_WIDTH = {}, """.format(args.ar_user_width))

                f.write ("""
    // Width of ruser signal from 0 - 1024
    localparam RUSER_WIDTH = {}, """.format(args.r_user_width))

                f.write ("""
    // AW channel register type
    // 0 to bypass, 1 for simple buffer, 2 for skid buffer
    localparam AW_REG_TYPE = {}, """.format(args.aw_reg_type))

                f.write ("""
    // W channel register type
    // 0 to bypass, 1 for simple buffer, 2 for skid buffer
    localparam W_REG_TYPE = {}, """.format(args.w_reg_type))

                f.write ("""
    // B channel register type
    // 0 to bypass, 1 for simple buffer, 2 for skid buffer
    localparam B_REG_TYPE = {}, """.format(args.b_reg_type))

                f.write ("""
    // AR channel register type
    // 0 to bypass, 1 for simple buffer, 2 for skid buffer
    localparam AR_REG_TYPE = {}, """.format(args.ar_reg_type))

                f.write ("""
    // R channel register type
    // 0 to bypass, 1 for simple buffer, 2 for skid buffer
    localparam R_REG_TYPE = {}, """.format(args.r_reg_type))

                f.write("""
    // Width of wstrb (width of data bus in words)
    localparam STRB_WIDTH = (DATA_WIDTH/8)
)
(
    input  wire                     clk,
    input  wire                     rst,

    /*
     * AXI slave interface
     */
    input  wire [ID_WIDTH-1:0]      s_axi_awid,
    input  wire [ADDR_WIDTH-1:0]    s_axi_awaddr,
    input  wire [7:0]               s_axi_awlen,
    input  wire [2:0]               s_axi_awsize,
    input  wire [1:0]               s_axi_awburst,
    input  wire                     s_axi_awlock,
    input  wire [3:0]               s_axi_awcache,
    input  wire [2:0]               s_axi_awprot,
    input  wire [3:0]               s_axi_awqos,
    input  wire [3:0]               s_axi_awregion,
    input  wire [AWUSER_WIDTH-1:0]  s_axi_awuser,
    input  wire                     s_axi_awvalid,
    output wire                     s_axi_awready,
    input  wire [DATA_WIDTH-1:0]    s_axi_wdata,
    input  wire [STRB_WIDTH-1:0]    s_axi_wstrb,
    input  wire                     s_axi_wlast,
    input  wire [WUSER_WIDTH-1:0]   s_axi_wuser,
    input  wire                     s_axi_wvalid,
    output wire                     s_axi_wready,
    output wire [ID_WIDTH-1:0]      s_axi_bid,
    output wire [1:0]               s_axi_bresp,
    output wire [BUSER_WIDTH-1:0]   s_axi_buser,
    output wire                     s_axi_bvalid,
    input  wire                     s_axi_bready,
    input  wire [ID_WIDTH-1:0]      s_axi_arid,
    input  wire [ADDR_WIDTH-1:0]    s_axi_araddr,
    input  wire [7:0]               s_axi_arlen,
    input  wire [2:0]               s_axi_arsize,
    input  wire [1:0]               s_axi_arburst,
    input  wire                     s_axi_arlock,
    input  wire [3:0]               s_axi_arcache,
    input  wire [2:0]               s_axi_arprot,
    input  wire [3:0]               s_axi_arqos,
    input  wire [3:0]               s_axi_arregion,
    input  wire [ARUSER_WIDTH-1:0]  s_axi_aruser,
    input  wire                     s_axi_arvalid,
    output wire                     s_axi_arready,
    output wire [ID_WIDTH-1:0]      s_axi_rid,
    output wire [DATA_WIDTH-1:0]    s_axi_rdata,
    output wire [1:0]               s_axi_rresp,
    output wire                     s_axi_rlast,
    output wire [RUSER_WIDTH-1:0]   s_axi_ruser,
    output wire                     s_axi_rvalid,
    input  wire                     s_axi_rready,

    /*
     * AXI master interface
     */
    output wire [ID_WIDTH-1:0]      m_axi_awid,
    output wire [ADDR_WIDTH-1:0]    m_axi_awaddr,
    output wire [7:0]               m_axi_awlen,
    output wire [2:0]               m_axi_awsize,
    output wire [1:0]               m_axi_awburst,
    output wire                     m_axi_awlock,
    output wire [3:0]               m_axi_awcache,
    output wire [2:0]               m_axi_awprot,
    output wire [3:0]               m_axi_awqos,
    output wire [3:0]               m_axi_awregion,
    output wire [AWUSER_WIDTH-1:0]  m_axi_awuser,
    output wire                     m_axi_awvalid,
    input  wire                     m_axi_awready,
    output wire [DATA_WIDTH-1:0]    m_axi_wdata,
    output wire [STRB_WIDTH-1:0]    m_axi_wstrb,
    output wire                     m_axi_wlast,
    output wire [WUSER_WIDTH-1:0]   m_axi_wuser,
    output wire                     m_axi_wvalid,
    input  wire                     m_axi_wready,
    input  wire [ID_WIDTH-1:0]      m_axi_bid,
    input  wire [1:0]               m_axi_bresp,
    input  wire [BUSER_WIDTH-1:0]   m_axi_buser,
    input  wire                     m_axi_bvalid,
    output wire                     m_axi_bready,
    output wire [ID_WIDTH-1:0]      m_axi_arid,
    output wire [ADDR_WIDTH-1:0]    m_axi_araddr,
    output wire [7:0]               m_axi_arlen,
    output wire [2:0]               m_axi_arsize,
    output wire [1:0]               m_axi_arburst,
    output wire                     m_axi_arlock,
    output wire [3:0]               m_axi_arcache,
    output wire [2:0]               m_axi_arprot,
    output wire [3:0]               m_axi_arqos,
    output wire [3:0]               m_axi_arregion,
    output wire [ARUSER_WIDTH-1:0]  m_axi_aruser,
    output wire                     m_axi_arvalid,
    input  wire                     m_axi_arready,
    input  wire [ID_WIDTH-1:0]      m_axi_rid,
    input  wire [DATA_WIDTH-1:0]    m_axi_rdata,
    input  wire [1:0]               m_axi_rresp,
    input  wire                     m_axi_rlast,
    input  wire [RUSER_WIDTH-1:0]   m_axi_ruser,
    input  wire                     m_axi_rvalid,
    output wire                     m_axi_rready
);

""")
                f.write("axi_register #(\n.DATA_WIDTH(DATA_WIDTH),\n.ADDR_WIDTH(ADDR_WIDTH),\n.ID_WIDTH(ID_WIDTH),\n.AWUSER_WIDTH(AWUSER_WIDTH),\n.WUSER_WIDTH(WUSER_WIDTH),\n.BUSER_WIDTH(BUSER_WIDTH),\n.ARUSER_WIDTH(ARUSER_WIDTH),\n.RUSER_WIDTH(RUSER_WIDTH),\n.AW_REG_TYPE(AW_REG_TYPE),\n.W_REG_TYPE(W_REG_TYPE),\n.B_REG_TYPE(B_REG_TYPE),\n.AR_REG_TYPE(AR_REG_TYPE),\n.R_REG_TYPE(R_REG_TYPE)\n)")
                f.write("""

axi_register_inst
(
.clk(clk),
.rst(rst),

// slave
.s_axi_awid(s_axi_awid),
.s_axi_awaddr(s_axi_awaddr),
.s_axi_awlen(s_axi_awlen),
.s_axi_awsize(s_axi_awsize),
.s_axi_awburst(s_axi_awburst),
.s_axi_awlock(s_axi_awlock),
.s_axi_awcache(s_axi_awcache),
.s_axi_awprot(s_axi_awprot),
.s_axi_awqos(s_axi_awqos),
.s_axi_awregion(s_axi_awregion),
.s_axi_awuser(s_axi_awuser),
.s_axi_awvalid(s_axi_awvalid),
.s_axi_awready(s_axi_awready),

.s_axi_wdata(s_axi_wdata),
.s_axi_wstrb(s_axi_wstrb),
.s_axi_wlast(s_axi_wlast),
.s_axi_wuser(s_axi_wuser),
.s_axi_wvalid(s_axi_wvalid),
.s_axi_wready(s_axi_wready),

.s_axi_bid(s_axi_bid),
.s_axi_bresp(s_axi_bresp),
.s_axi_buser(s_axi_buser),
.s_axi_bvalid(s_axi_bvalid),
.s_axi_bready(s_axi_bready),

.s_axi_arid(s_axi_arid),
.s_axi_araddr(s_axi_araddr),
.s_axi_arlen(s_axi_arlen),
.s_axi_arsize(s_axi_arsize),
.s_axi_arburst(s_axi_arburst),
.s_axi_arlock(s_axi_arlock),
.s_axi_arcache(s_axi_arcache),
.s_axi_arprot(s_axi_arprot),
.s_axi_arqos(s_axi_arqos),
.s_axi_arregion(s_axi_arregion),
.s_axi_aruser(s_axi_aruser),
.s_axi_arvalid(s_axi_arvalid),
.s_axi_arready(s_axi_arready),

.s_axi_rid(s_axi_rid),
.s_axi_rdata(s_axi_rdata),
.s_axi_rresp(s_axi_rresp),
.s_axi_rlast(s_axi_rlast),
.s_axi_ruser(s_axi_ruser),
.s_axi_rvalid(s_axi_rvalid),
.s_axi_rready(s_axi_rready),

// master
.m_axi_awid(m_axi_awid),
.m_axi_awaddr(m_axi_awaddr),
.m_axi_awlen(m_axi_awlen),
.m_axi_awsize(m_axi_awsize),
.m_axi_awburst(m_axi_awburst),
.m_axi_awlock(m_axi_awlock),
.m_axi_awcache(m_axi_awcache),
.m_axi_awprot(m_axi_awprot),
.m_axi_awqos(m_axi_awqos),
.m_axi_awregion(m_axi_awregion),
.m_axi_awuser(m_axi_awuser),
.m_axi_awvalid(m_axi_awvalid),
.m_axi_awready(m_axi_awready),

.m_axi_wdata(m_axi_wdata),
.m_axi_wstrb(m_axi_wstrb),
.m_axi_wlast(m_axi_wlast),
.m_axi_wuser(m_axi_wuser),
.m_axi_wvalid(m_axi_wvalid),
.m_axi_wready(m_axi_wready),

.m_axi_bid(m_axi_bid),
.m_axi_bresp(m_axi_bresp),
.m_axi_buser(m_axi_buser),
.m_axi_bvalid(m_axi_bvalid),
.m_axi_bready(m_axi_bready),

.m_axi_arid(m_axi_arid),
.m_axi_araddr(m_axi_araddr),
.m_axi_arlen(m_axi_arlen),
.m_axi_arsize(m_axi_arsize),
.m_axi_arburst(m_axi_arburst),
.m_axi_arlock(m_axi_arlock),
.m_axi_arcache(m_axi_arcache),
.m_axi_arprot(m_axi_arprot),
.m_axi_arqos(m_axi_arqos),
.m_axi_arregion(m_axi_arregion),
.m_axi_aruser(m_axi_aruser),
.m_axi_arvalid(m_axi_arvalid),
.m_axi_arready(m_axi_arready),

.m_axi_rid(m_axi_rid),
.m_axi_rdata(m_axi_rdata),
.m_axi_rresp(m_axi_rresp),
.m_axi_rlast(m_axi_rlast),
.m_axi_ruser(m_axi_ruser),
.m_axi_rvalid(m_axi_rvalid),
.m_axi_rready(m_axi_rready)
);

endmodule

`resetall
             """)
                f.close()

if __name__ == "__main__":
    main()
