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
    parser = argparse.ArgumentParser(description="AXI LITE UART CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--addr_width",          default=5,                    help="UART Address Width")
    core_group.add_argument("--rdata_width",         default=32,                   help="UART Read Data Width")
    core_group.add_argument("--wdata_width",         default=32,                   help="UART Write Data Width")
    core_group.add_argument("--prot_width",          default=3,                    help="UART Protection Width")
 
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build_dir",     default="",                     help="Build Directory")
    build_group.add_argument("--build_name",    default="axil_uart",            help="Build Folder Name")
    build_group.add_argument("--mod_name",      default="axil_uart_wrapper",    help="Module Name and File Name of the RTL")

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

    litex_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "litex_sim")

    gen_path = os.path.join("axil_uart_gen.py")

    # Remove build extension when specified --------------------------------------------------------
    args.build_name = os.path.splitext(args.build_name)[0]

    # Build Project Directory ----------------------------------------------------------------------
    if args.build:
        # Build Path
        build_path = os.path.join(args.build_dir, 'ip_build/rapidsilicon/ip/axil_uart/v1_0/' + (args.mod_name))
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
        # Add Include Path
        tcl.append(f"add_include_path {'../src'}")
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
    if args.mod_name:
        wrapper_path = os.path.join(src_path, (args.mod_name + ".v"))
        with open(wrapper_path, "w") as f:

#-------------------------------------------------------------------------------
# ------------------------- RTL WRAPPER ----------------------------------------
#-------------------------------------------------------------------------------
            f.write ("""
//////////////////////////////////////////////////////////////////////////////////////////
/*
Copyright (c) 2022 Rapid Silicon
*/
//////////////////////////////////////////////////////////////////////////////////////////\n\n
""")
            f.write ("// Created on: {}\n// Language: Verilog 2001\n\n".format(datetime.now()))
            f.write ("`resetall \n`timescale 1ns/ 1ps \n`default_nettype none \n\n")
            f.write ("""module {} #(""".format(args.mod_name))

            f.write ("""
        // Width of Addresses in bits
        localparam AXI4_ADDRESS_WIDTH = {}, """.format(args.addr_width))

            f.write ("""
        // Width of Read Data in bits
        localparam AXI4_RDATA_WIDTH = {}, """.format(args.rdata_width))

            f.write ("""
        // Width of Write Data in bits
        localparam AXI4_WDATA_WIDTH = {}, """.format(args.wdata_width))

            f.write ("""
        // Width of Protection in bits
        localparam AXI4_PROT_WIDTH = {}""".format(args.prot_width))

            f.write("""
)
(
    // Global signals
    input  wire                          s_axi_aclk,
    input  wire                          s_axi_aresetn,

    // write address channel
    input  wire                          s_axi_awvalid,
    input  wire [AXI4_ADDRESS_WIDTH-1:0] s_axi_awaddr,
    input  wire [AXI4_PROT_WIDTH-1:0]    s_axi_awprot,
    output wire                          s_axi_awready,

    // write data channel
    input  wire                          s_axi_wvalid,
    input  wire [AXI4_WDATA_WIDTH-1:0]   s_axi_wdata,
    input  wire [AXI4_WDATA_WIDTH/8-1:0] s_axi_wstrb,
    output wire                          s_axi_wready,

    // write response channel
    output wire                          s_axi_bvalid,
    output wire [1:0]                    s_axi_bresp,
    input  wire                          s_axi_bready,

    // read address channel
    input  wire                          s_axi_arvalid,
    input  wire [AXI4_ADDRESS_WIDTH-1:0] s_axi_araddr,
    input  wire [AXI4_PROT_WIDTH-1:0]    s_axi_arprot,
    output wire                          s_axi_arready,

    // read data channel
    output wire                          s_axi_rvalid,
    output wire [AXI4_RDATA_WIDTH-1:0]   s_axi_rdata,
    output wire [1:0]                    s_axi_rresp,
    input  wire                          s_axi_rready,

    // UART Signals
    output  wire                         int_o,
    input 	wire						 srx_pad_i,
    output 	wire						 stx_pad_o,
    output 	wire						 rts_pad_o,
    input 	wire						 cts_pad_i,
    output 	wire						 dtr_pad_o,
    input 	wire						 dsr_pad_i,
    input 	wire						 ri_pad_i,
    input 	wire						 dcd_pad_i
);

""")
            f.write("axi4lite_uart_top #(\n.AXI4_ADDRESS_WIDTH(AXI4_ADDRESS_WIDTH),\n.AXI4_RDATA_WIDTH(AXI4_RDATA_WIDTH),\n.AXI4_WDATA_WIDTH(AXI4_WDATA_WIDTH),\n.AXI4_PROT_WIDTH(AXI4_PROT_WIDTH)\n)")
            f.write("""
axi4lite_uart_top_inst
(
.s_axi_aclk(s_axi_aclk),
.s_axi_aresetn(s_axi_aresetn),

.s_axi_awvalid(s_axi_awvalid),
.s_axi_awaddr(s_axi_awaddr),
.s_axi_awprot(s_axi_awprot),
.s_axi_awready(s_axi_awready),

.s_axi_wvalid(s_axi_wvalid),
.s_axi_wdata(s_axi_wdata),
.s_axi_wstrb(s_axi_wstrb),
.s_axi_wready(s_axi_wready),

.s_axi_bvalid(s_axi_bvalid),
.s_axi_bresp(s_axi_bresp),
.s_axi_bready(s_axi_bready),

.s_axi_arvalid(s_axi_arvalid),
.s_axi_araddr(s_axi_araddr),
.s_axi_arprot(s_axi_arprot),
.s_axi_arready(s_axi_arready),

.s_axi_rvalid(s_axi_rvalid),
.s_axi_rdata(s_axi_rdata),
.s_axi_rresp(s_axi_rresp),
.s_axi_rready(s_axi_rready),

.int_o(int_o),
.srx_pad_i(srx_pad_i),
.stx_pad_o(stx_pad_o),
.rts_pad_o(rts_pad_o),
.cts_pad_i(cts_pad_i),
.dtr_pad_o(dtr_pad_o),
.dsr_pad_i(dsr_pad_i),
.ri_pad_i(ri_pad_i),
.dcd_pad_i(dcd_pad_i)
);

endmodule

`resetall
             """)
            f.close()

if __name__ == "__main__":
    main()
