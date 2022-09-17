#!/usr/bin/env python3

# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os
import json
import argparse
import shutil
import logging

from litex_sim.axi_dp_ram_litex_wrapper import AXIDPRAM

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("a_clk", 0, Pins(1)),
        ("a_rst", 0, Pins(1)),
        ("b_clk", 0, Pins(1)),
        ("b_rst", 0, Pins(1)),
    ]
    
# AXI-DPRAM Wrapper --------------------------------------------------------------------------------
class AXIDPRAMWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, a_pip_out, b_pip_out, a_interleave, b_interleave):
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("a_clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("a_rst"))
        self.comb += self.cd_sys.clk.eq(platform.request("b_clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("b_rst"))
        
        # AXI-------------------------------------------------------------
        s_axi_a = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
        )
        s_axi_b = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width,
        )
        platform.add_extension(s_axi_a.get_ios("s_axi_a"))
        platform.add_extension(s_axi_b.get_ios("s_axi_b"))
        self.comb += s_axi_a.connect_to_pads(platform.request("s_axi_a"), mode="slave")
        self.comb += s_axi_b.connect_to_pads(platform.request("s_axi_b"), mode="slave")
        
        # AXI-DPRAM -----------------------------------------------------
        self.submodules += AXIDPRAM(platform, s_axi_a, s_axi_b, 
                                    a_pipeline_output   =   a_pip_out, 
                                    b_pipeline_output   =   b_pip_out, 
                                    a_interleave        =   a_interleave, 
                                    b_interleave        =   b_interleave, 
                                    size                =   (2**addr_width)*(data_width/8)
                                    )


# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI DPRAM CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",     default=32,  type=int,    help="DPRAM Data Width 8,16,32,64")
    core_group.add_argument("--addr_width",     default=16,  type=int,    help="DPRAM Address Width 8 - 16")
    core_group.add_argument("--id_width",       default=32,  type=int,    help="DPRAM ID Width from 1 - 32")
    core_group.add_argument("--a_pip_out",      default=0,   type=int,    help="DPRAM A Pipeline Output 0 or 1")
    core_group.add_argument("--b_pip_out",      default=0,   type=int,    help="DPRAM B Pipeline Output 0 or 1")
    core_group.add_argument("--a_interleave",   default=0,   type=int,    help="DPRAM A Interleave 0 or 1")
    core_group.add_argument("--b_interleave",   default=0,   type=int,    help="DPRAM B Interleave 0 or 1")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_dpram_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")
    
    # Data_Width
    data_width_param=[8, 16, 32, 64, 128, 256]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s", data_width_param)
        exit()
    
    # Address Width
    addr_range=range(8, 17)
    if args.addr_width not in addr_range:
        logger.error("\nEnter a valid 'addr_width' from 8 to 16")
        exit()

    # ID_Width
    id_range=range(1, 33)
    if args.id_width not in id_range:
        logger.error("\nEnter a valid 'id_width' from 1 to 32")
        exit()
    
    # A_Pipeline_Output
    a_pip_range=range(2)
    if args.a_pip_out not in a_pip_range:
        logger.error("\nEnter a valid 'a_pip_out' 0 or 1")
        exit()

    # B_Pipeline_Output
    b_pip_range=range(2)
    if args.b_pip_out not in b_pip_range:
        logger.error("\nEnter a valid 'b_pip_out' 0 or 1")
        exit()

    # A_Interleave
    a_interleave_range=range(2)
    if args.a_interleave not in a_interleave_range:
        logger.error("\nEnter a valid 'a_interleave' 0 or 1")
        exit()

    # B_Interleave
    b_interleave_range=range(2)
    if args.b_interleave not in b_interleave_range:
        logger.error("\nEnter a valid 'b_interleave' 0 or 1")
        exit()

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
        build_path = os.path.join(args.build_dir, 'rapidsilicon/ip/axi_dpram/v1_0/' + (args.build_name))
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

        # Generate .tcl file
        tcl_path = os.path.join(synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module = AXIDPRAMWrapper(platform,
        data_width  = args.data_width,
        addr_width  = args.addr_width,
        id_width    = args.id_width,
        a_pip_out   = args.a_pip_out,
        b_pip_out   = args.b_pip_out,
        a_interleave= args.a_interleave,
        b_interleave= args.b_interleave                 
        )
    
    # Build
    if args.build:
        platform.build(module,
            build_dir    = "litex_build",
            build_name   = args.build_name,
            run          = False,
            regular_comb = False
        )
        shutil.copy(f"litex_build/{args.build_name}.v", src_path)
        shutil.rmtree("litex_build")

if __name__ == "__main__":
    main()
