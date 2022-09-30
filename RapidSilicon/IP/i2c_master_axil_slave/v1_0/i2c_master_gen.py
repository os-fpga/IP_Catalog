#!/usr/bin/env python3

# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os
import json
import argparse
import shutil
import logging

from litex_sim.i2c_master_litex_wrapper import I2CMASTER

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
    
def get_i2c_ios():
    return [
        ("i2c", 0,
            Subsignal("scl_i", Pins(1)),
            Subsignal("scl_o", Pins(1)),
            Subsignal("scl_t", Pins(1)),
            Subsignal("sda_i", Pins(1)),
            Subsignal("sda_o", Pins(1)),
            Subsignal("sda_t", Pins(1)),    
        )
    ]

# I2C Master Wrapper ----------------------------------------------------------------------------------
class I2CMASTERWrapper(Module):
    def __init__(self, platform, default_prescale, fixed_prescale, cmd_fifo, cmd_addr_width, write_fifo, write_addr_width, read_fifo, read_addr_width):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # AXI LITE ----------------------------------------------------------------------------------
        axil = AXILiteInterface()
        platform.add_extension(axil.get_ios("s_axil"))
        self.comb += axil.connect_to_pads(platform.request("s_axil"), mode="slave")

        # I2C_MASTER ----------------------------------------------------------------------------------
        self.submodules.i2c_master = i2c_master = I2CMASTER(platform, axil,
            default_prescale    = default_prescale, 
            fixed_prescale      = fixed_prescale,
            cmd_fifo            = cmd_fifo,
            cmd_addr_width      = cmd_addr_width,
            write_fifo          = write_fifo,
            write_addr_width    = write_addr_width,
            read_fifo           = read_fifo,
            read_addr_width     = read_addr_width
            )
        
        # I2C Signals --------------------------------
        platform.add_extension(get_i2c_ios())
        i2c_pads = platform.request("i2c")
        self.comb += [
            i2c_master.i2c_scl_i.eq(i2c_pads.scl_i),
            i2c_pads.scl_o.eq(i2c_master.i2c_scl_o),
            i2c_pads.scl_t.eq(i2c_master.i2c_scl_t),

            i2c_master.i2c_sda_i.eq(i2c_pads.sda_i),
            i2c_pads.sda_o.eq(i2c_master.i2c_sda_o),
            i2c_pads.sda_t.eq(i2c_master.i2c_sda_t),
        ]

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="I2C MASTER CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core Parameters")
    core_group.add_argument("--default_prescale",   default=1,   type=int,     help="I2C Default Prescale 0 or 1")
    core_group.add_argument("--fixed_prescale",     default=0,   type=int,     help="I2C Fixed Prescale 0 or 1")
    core_group.add_argument("--cmd_fifo",           default=1,   type=int,     help="I2C FIFO Command Enable 0 or 1")
    core_group.add_argument("--cmd_addr_width",     default=5,   type=int,     help="I2C FIFO Command Address Width from 1 to 5)")
    core_group.add_argument("--write_fifo",         default=1,   type=int,     help="I2C FIFO Write Enable 0 or 1")
    core_group.add_argument("--write_addr_width",   default=5,   type=int,     help="I2C FIFO Write Address Width from 1 to 5)")
    core_group.add_argument("--read_fifo",          default=1,   type=int,     help="I2C FIFO Read Enable 0 or 1")
    core_group.add_argument("--read_addr_width",    default=5,   type=int,     help="I2C FIFO Read Address Width from 1 to 5)")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build Parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                	help="Build Directory")
    build_group.add_argument("--build-name",    default="i2c_master_wrapper",   help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Default Prescale
    default_prescale_range=range(2)
    if args.default_prescale not in default_prescale_range:
        logger.error("\nEnter a valid 'default_prescale' 0 or 1")
        exit()
        
    # Fixed Prescale
    fixed_prescale_range=range(2)
    if args.fixed_prescale not in fixed_prescale_range:
        logger.error("\nEnter a valid 'fixed_prescale' 0 or 1")
        exit()
        
    # CMD FIFO 
    cmd_fifo_range=range(2)
    if args.cmd_fifo not in cmd_fifo_range:
        logger.error("\nEnter a valid 'cmd_fifo' 0 or 1")
        exit()

    # CMD FIFO Address Width
    cmd_addr_width_range=range(1,6)
    if args.cmd_addr_width not in cmd_addr_width_range:
        logger.error("\nEnter a valid 'cmd_addr_width' from 1 to 5")
        exit()
        
    # Write FIFO 
    write_fifo_range=range(2)
    if args.write_fifo not in write_fifo_range:
        logger.error("\nEnter a valid 'write_fifo' 0 or 1")
        exit()
        
    # Write FIFO Address Width
    write_addr_width_range=range(1,6)
    if args.write_addr_width not in write_addr_width_range:
        logger.error("\nEnter a valid 'write_addr_width' from 1 to 5")
        exit()
        
    # Read FIFO 
    read_fifo_range=range(2)
    if args.read_fifo not in read_fifo_range:
        logger.error("\nEnter a valid 'read_fifo' 0 or 1")
        exit()
        
    # Read FIFO Address Width
    read_addr_width_range=range(1,6)
    if args.read_addr_width not in read_addr_width_range:
        logger.error("\nEnter a valid 'read_addr_width' from 1 to 5")
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
        build_path = os.path.join(args.build_dir, 'rapidsilicon/ip/i2c_master/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "i2c_master_gen.py"))
        
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
        # Add file extension
        tcl.append(f"add_library_ext .v .sv")
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
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = I2CMASTERWrapper(platform,
        default_prescale    = args.default_prescale,
        fixed_prescale      = args.fixed_prescale,
        cmd_fifo            = args.cmd_fifo,
        cmd_addr_width      = args.cmd_addr_width,
        write_fifo          = args.write_fifo,
        write_addr_width    = args.write_addr_width,
        read_fifo           = args.read_fifo,
        read_addr_width     = args.read_addr_width
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
