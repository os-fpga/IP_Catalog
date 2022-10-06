#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT.

import os
import json
import argparse
import shutil
import logging

from litex_sim.axi_vexriscv_litex_wrapper import VexRiscv

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1))]

def get_jtag_ios():
    return [
                
            ("jtag_tms",    0,  Pins(1)),
            ("jtag_tdi",    0,  Pins(1)),
            ("jtag_tdo",    0,  Pins(1)),
            ("jtag_tck",    0,  Pins(1)),    
            ]


def get_other_ios():
    return [
            ("timerInterrupt",      0,  Pins(1)),
            ("externalInterrupt",   0,  Pins(1)),    
            ("softwareInterrupt",   0,  Pins(1)),    
            ("debugReset",          0,  Pins(1)),
            ("debug_resetOut",      0,  Pins(1)),
        ]

# AXI-VEXRISCV Wrapper --------------------------------------------------------------------------------
class VexriscvWrapper(Module):
    def __init__(self, platform):
    
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        #IBUS
        ibus_axi = AXIInterface(data_width = 32, address_width = 32, id_width = 8)
        platform.add_extension(ibus_axi.get_ios("ibus_axi"))
        self.comb += ibus_axi.connect_to_pads(platform.request("ibus_axi"), mode="master")

        #IBUS
        dbus_axi = AXIInterface(data_width = 32, address_width = 32, id_width = 8)
        platform.add_extension(dbus_axi.get_ios("dbus_axi"))
        self.comb += dbus_axi.connect_to_pads(platform.request("dbus_axi"), mode="master")

        # VEXRISCV
        self.submodules.vexriscv = vexriscv = VexRiscv(platform,
            ibus        = ibus_axi,
            dbus        = dbus_axi
            )

        platform.add_extension(get_jtag_ios())
        # Inputs
        self.comb += vexriscv.jtag_tms.eq(platform.request("jtag_tms"))
        self.comb += vexriscv.jtag_tdi.eq(platform.request("jtag_tdi"))
        self.comb += vexriscv.jtag_tck.eq(platform.request("jtag_tck"))

        # Outputs
        self.comb += platform.request("jtag_tdo").eq(vexriscv.jtag_tdo)

        platform.add_extension(get_other_ios())
        # Inputs
        self.comb += vexriscv.timerInterrupt.eq(platform.request("timerInterrupt"))
        self.comb += vexriscv.externalInterrupt.eq(platform.request("externalInterrupt"))
        self.comb += vexriscv.softwareInterrupt.eq(platform.request("softwareInterrupt"))
        self.comb += vexriscv.debugReset.eq(platform.request("debugReset"))

        # Outputs
        self.comb += platform.request("debug_resetOut").eq(vexriscv.debug_resetOut)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Vexriscv CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="vexriscv_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

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
        build_path = os.path.join(args.build_dir, 'rapidsilicon/ip/vexriscv/v1_0/' + (args.build_name))
        gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "axi_vexriscv_gen.py"))
        
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
    module = VexriscvWrapper(platform)
    #    data_width          = args.data_width,
    #    addr_width          = args.addr_width,
    #    id_width            = args.id_width,
    #    )
    
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
        content.insert(13, '// This file is Copyright (c) 2022 RapidSilicon\n//------------------------------------------------------------------------------')
        content.insert(15, '\n`timescale 1ns / 1ps\n')
        f = open(wrapper, "w")
        content = "".join(content)
        f.write(str(content))
        f.close()

if __name__ == "__main__":
    main()
