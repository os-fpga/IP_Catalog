#!/usr/bin/env python3

# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os
import json
import argparse
import shutil
import logging

from litex_sim.axil_crossbar_litex_wrapper import AXILITECROSSBAR

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]

# AXI LITE CROSSBAR ----------------------------------------------------------------------------------
class AXILITECROSSBARWrapper(Module):
    def __init__(self, platform, s_count, m_count, data_width, addr_width):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # Slave Interfaces
        s_axils = []
        for s_count in range(s_count):
            s_axil = AXILiteInterface(data_width = data_width , address_width = addr_width)
            if s_count>9:
                platform.add_extension(s_axil.get_ios("s{}_axil".format(s_count)))
                self.comb += s_axil.connect_to_pads(platform.request("s{}_axil".format(s_count)), mode="slave")
            else:
                platform.add_extension(s_axil.get_ios("s0{}_axil".format(s_count)))
                self.comb += s_axil.connect_to_pads(platform.request("s0{}_axil".format(s_count)), mode="slave")
                
            s_axils.append(s_axil)
        
        # Master Interfaces
        m_axils = []    
        for m_count in range(m_count):
            m_axil = AXILiteInterface(data_width = data_width , address_width = addr_width)
            if m_count>9:
                platform.add_extension(m_axil.get_ios("m{}_axil".format(m_count)))
                self.comb += m_axil.connect_to_pads(platform.request("m{}_axil".format(m_count)), mode="master")
            else:
                platform.add_extension(m_axil.get_ios("m0{}_axil".format(m_count)))
                self.comb += m_axil.connect_to_pads(platform.request("m0{}_axil".format(m_count)), mode="master")
            
            m_axils.append(m_axil)

        # AXIL-CROSSBAR ----------------------------------------------------------------------------------
        self.submodules += AXILITECROSSBAR (platform, 
            s_axil      = s_axils,
            m_axil      = m_axils,
            s_count     = s_count,
            m_count     = m_count
            )

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AXI_LITE_CROSSBAR_CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--m_count",        default=4,      type=int,         help="Crossbar Master Interfaces 2 to 16")
    core_group.add_argument("--s_count",        default=4,      type=int,         help="Crossbar SLAVE Interfaces 1 to 16")
    core_group.add_argument("--data_width",     default=32,     type=int,         help="Crossbar Data Width 8,16,32,64,128,256")
    core_group.add_argument("--addr_width",     default=32,     type=int,         help="Crossbar Address Width 32,64,128,256")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="axil_crossbar_wrapper",        help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # AXI Master Interfaces
    m_count_range=range(2,17)
    if args.m_count not in m_count_range:
        logger.error("\nEnter a valid 'm_count' from 2 to 16")
        exit()
        
    # AXI Slave Interfaces
    s_count_range=range(1,17)
    if args.s_count not in s_count_range:
        logger.error("\nEnter a valid 's_count' from 1 to 16")
        exit()

    # Data_Width
    data_width_param=[8, 16, 32, 64, 128, 256]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s", data_width_param)
        exit()
        
    # Address Width
    addr_width_param=[32, 64, 128, 256]
    if args.addr_width not in addr_width_param:
        logger.error("\nEnter a valid 'addr_width'\n %s", addr_width_param)
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
        build_path = os.path.join(args.build_dir, 'rapidsilicon/ip/axil_crossbar/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "axil_crossbar_gen.py"))

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
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXILITECROSSBARWrapper(platform,
        m_count         = args.m_count,
        s_count         = args.s_count,
        data_width      = args.data_width,
        addr_width      = args.addr_width
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
        
        # TimeScale Addition to Wrapper
        wrapper = os.path.join(src_path, f'{args.build_name}.v')
        f = open(wrapper, "r")
        content = f.readlines()
        content.insert(14, '`timescale 1ns / 1ps\n')
        f = open(wrapper, "w")
        content = "".join(content)
        f.write(str(content))
        f.close()

if __name__ == "__main__":
    main()
