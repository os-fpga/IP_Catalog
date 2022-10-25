#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse

from litex_wrapper.i2c_master_litex_wrapper import I2CMASTER

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

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..")
    sys.path.append(common_path)

    from common import IP_Builder

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core Parameters")
    core_group.add_argument("--default_prescale",  type=int, default=1, choices=range(2),     help="I2C Default Prescale.")
    core_group.add_argument("--fixed_prescale",    type=int, default=0, choices=range(2),     help="I2C Fixed Prescale.")
    core_group.add_argument("--cmd_fifo",          type=int, default=1, choices=range(2),     help="I2C FIFO Command Enable.")
    core_group.add_argument("--cmd_addr_width",    type=int, default=5, choices=range(1, 6),  help="I2C FIFO Command Address Width.")
    core_group.add_argument("--write_fifo",        type=int, default=1, choices=range(2),     help="I2C FIFO Write Enable.")
    core_group.add_argument("--write_addr_width",  type=int, default=5, choices=range(1, 6),  help="I2C FIFO Write Address Width.")
    core_group.add_argument("--read_fifo",         type=int, default=1, choices=range(2),     help="I2C FIFO Read Enable.")
    core_group.add_argument("--read_addr_width",   type=int, default=5, choices=range(1, 6),  help="I2C FIFO Read Address Width.")

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

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        with open(args.json, 'rt') as f:
            t_args = argparse.Namespace()
            t_args.__dict__.update(json.load(f))
            args = parser.parse_args(namespace=t_args)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        print(json.dumps(vars(args), indent=4))
        
    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = I2CMASTERWrapper(platform,
        default_prescale = args.default_prescale,
        fixed_prescale   = args.fixed_prescale,
        cmd_fifo         = args.cmd_fifo,
        cmd_addr_width   = args.cmd_addr_width,
        write_fifo       = args.write_fifo,
        write_addr_width = args.write_addr_width,
        read_fifo        = args.read_fifo,
        read_addr_width  = args.read_addr_width,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder = IP_Builder(device="gemini", ip_name="i2c_master", language="verilog")
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
