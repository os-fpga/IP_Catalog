#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import json
import argparse
import shutil
import logging

from litex_sim.axi_spi_master_litex_wrapper import AXISPIMASTER

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios():
    return [
        ("s_axi_aclk",  0,    Pins(1)),
        ("s_axi_arst",  0,    Pins(1)),
    ]
    
def get_spi_ios():
    return [
        ("events_o",    0,    Pins(2)),
        ("spi",         0,
            Subsignal("clk",  Pins(1)),
            Subsignal("csn0", Pins(1)),
            Subsignal("csn1", Pins(1)),
            Subsignal("csn2", Pins(1)),
            Subsignal("csn3", Pins(1)),
            Subsignal("mode", Pins(2)),
            Subsignal("sdo0", Pins(1)),
            Subsignal("sdo1", Pins(1)),
            Subsignal("sdo2", Pins(1)),
            Subsignal("sdo3", Pins(1)),
            Subsignal("sdi0", Pins(1)),
            Subsignal("sdi1", Pins(1)),    
            Subsignal("sdi2", Pins(1)), 
            Subsignal("sdi3", Pins(1)), 
        )
    ]

# AXI SPI MASTER Wrapper ----------------------------------------------------------------------------------
class AXISPIMASTERWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, user_width, buffer_depth):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("s_axi_aclk"))
        self.comb += self.cd_sys.rst.eq(platform.request("s_axi_arst"))

        # AXI ----------------------------------------------------------------------------------
        axil = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            aw_user_width   = user_width,
            w_user_width    = user_width,
            b_user_width    = user_width,
            ar_user_width   = user_width,
            r_user_width    = user_width,
            id_width        = id_width
        )
        
        platform.add_extension(axil.get_ios("s_axi"))
        self.comb += axil.connect_to_pads(platform.request("s_axi"), mode="slave")

        # AXI SPI MASTER -----------------------------------------------------------------------
        self.submodules.spi_master = spi_master = AXISPIMASTER(platform, 
            s_axi           = axil,
            buffer_depth    = buffer_depth
            )
        
        # SPI IOS
        platform.add_extension(get_spi_ios())
        spi_pads = platform.request("spi")
        self.comb += [
            # Inputs
            spi_master.spi_clk.eq(spi_pads.clk),
            spi_master.spi_csn0.eq(spi_pads.csn0),
            spi_master.spi_csn1.eq(spi_pads.csn1),
            spi_master.spi_csn2.eq(spi_pads.csn2),
            spi_master.spi_csn3.eq(spi_pads.csn3),
            spi_master.spi_mode.eq(spi_pads.mode),
            spi_master.spi_sdo0.eq(spi_pads.sdo0),
            spi_master.spi_sdo1.eq(spi_pads.sdo1),
            spi_master.spi_sdo2.eq(spi_pads.sdo2),
            spi_master.spi_sdo3.eq(spi_pads.sdo3),
            # Outputs
            spi_pads.sdi0.eq(spi_master.spi_sdi0),
            spi_pads.sdi1.eq(spi_master.spi_sdi1),
            spi_pads.sdi2.eq(spi_master.spi_sdi2),
            spi_pads.sdi3.eq(spi_master.spi_sdi3),
        ]
        self.comb += platform.request("events_o").eq(spi_master.events_o)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI SPI MASTER CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--addr_width",        default=32,    type=int,       help="AXI Address Width 8,16,32")
    core_group.add_argument("--data_width",        default=32,    type=int,       help="AXI Data Width 8,16,32")
    core_group.add_argument("--user_width",        default=4,     type=int,       help="AXI ID Width from 1 to 4")
    core_group.add_argument("--id_width",          default=16,    type=int,       help="AXI ID Width from 1 to 16")
    core_group.add_argument("--buffer_depth",      default=8,     type=int,       help="AXI Buffer Depth 8,16")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_spi_master_wrapper",       help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")
    
    # Data Width
    data_width_param=[8, 16, 32]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s" , data_width_param)
        exit()
        
    # Address Width
    addr_width_param=[8, 16, 32]
    if args.addr_width not in addr_width_param:
        logger.error("\nEnter a valid 'addr_width'\n %s" , addr_width_param)
        exit()

    # User Width
    user_width_range=range(1,5)
    if args.user_width not in user_width_range:
        logger.error("\nEnter a valid 'user_width' from 1 to 4")
        exit()
        
    # ID Width
    id_width_range=range(1,17)
    if args.id_width not in id_width_range:
        logger.error("\nEnter a valid 'id_width' from 1 to 16")
        exit()
        
    # Buffer Depth
    buffer_param=[8, 16]
    if args.buffer_depth not in buffer_param:
        logger.error("\nEnter a valid 'buffer_depth'\n %s" , buffer_param)
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
        build_path = os.path.join(args.build_dir, 'rapidsilicon/ip/axi_spi_master/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "axi_spi_master_gen.py"))
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
        design_path = os.path.join("../src", (args.build_name + ".sv")) 

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

        # Generate .tcl file
        tcl_path = os.path.join(synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()

    # Create LiteX Core ----------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module = AXISPIMASTERWrapper(platform,
        addr_width          = args.addr_width,
        data_width          = args.data_width,
        user_width          = args.user_width,
        id_width            = args.id_width, 
        buffer_depth        = args.buffer_depth
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
        
        # Changing File Extension from .v to .sv
        old_wrapper = os.path.join(src_path, f'{args.build_name}.v')
        new_wrapper = old_wrapper.replace('.v','.sv')
        os.rename(old_wrapper, new_wrapper)
        
        # TimeScale Addition to Wrapper
        f = open(new_wrapper, "r")
        content = f.readlines()
        content.insert(14, '`timescale 1ns / 1ps\n')
        f = open(new_wrapper, "w")
        content = "".join(content)
        f.write(str(content))
        f.close()

if __name__ == "__main__":
    main()
