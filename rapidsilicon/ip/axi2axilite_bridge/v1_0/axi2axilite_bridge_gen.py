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

from litex_sim.axi2axilite_bridge_litex_wrapper import AXI2AXILITE

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface, AXILiteInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("s_axi_aclk",      0, Pins(1)),
        ("s_axi_aresetn",   0, Pins(1))]

# AXI-2-AXILITE Wrapper --------------------------------------------------------------------------------
class AXI2AXILITEWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width):
        
        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("s_axi_aclk"))
        self.comb += self.cd_sys.rst.eq(platform.request("s_axi_aresetn"))

        # AXI SLAVE PORT
        s_axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width
        )
        
        # AXI MASTER PORT
        m_axi = AXILiteInterface(
            data_width      = data_width,
            address_width   = addr_width
        )

        platform.add_extension(s_axi.get_ios("s_axi"))
        self.comb += s_axi.connect_to_pads(platform.request("s_axi"), mode="slave")
        
        platform.add_extension(m_axi.get_ios("m_axi"))
        self.comb += m_axi.connect_to_pads(platform.request("m_axi"), mode="master")

        # AXI_2_AXILITE
        self.submodules.axi2axilite = AXI2AXILITE(platform, s_axi, m_axi)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI_2_AXILITE CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",         default=32,     type=int,    help="Data Width 8,16,32,64,128,256")
    core_group.add_argument("--addr_width",         default=6,      type=int,    help="Address Width 6 - 16")
    core_group.add_argument("--id_width",           default=2,      type=int,    help="ID Width from 1 - 32")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi2axilite_wrapper",  help="Build Folder Name, Build RTL File Name and Module Name")

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
    addr_range=range(6, 17)
    if args.addr_width not in addr_range:
        logger.error("\nEnter a valid 'addr_width' from 6 to 16")
        exit()

    # ID_Width
    id_range=range(1, 33)
    if args.id_width not in id_range:
        logger.error("\nEnter a valid 'id_width' from 1 to 32")
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

    import sys
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")  # FIXME
    sys.path.append(common_path)                                       # FIXME
    from common import RapidSiliconIPCatalogBuilder
    rs_builder = RapidSiliconIPCatalogBuilder(ip_name="axi2axilite_bridge")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))

        # Design Path
        design_path = os.path.join("../src", (args.build_name + ".v")) 
        
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
        tcl_path = os.path.join(rs_builder.synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module = AXI2AXILITEWrapper(platform,
        data_width          = args.data_width,
        addr_width          = args.addr_width,
        id_width            = args.id_width
        )
    
    # Build
    if args.build:
        rs_builder.build(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
