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

from litex_sim.i2c_slave_litex_wrapper import I2CSLAVE

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
        ),
        ("busy",             0, Pins(1)),
        ("bus_addressed",    0, Pins(1)), 
        ("bus_active",       0, Pins(1)),
        ("enable",           0, Pins(1)),
        ("device_address",   0, Pins(7))   
    ]
    
# I2C SLAVE Wrapper ---------------------------------------------------------------------------------
class I2CSLAVEWrapper(Module):
    def __init__(self, platform, data_width, addr_width, filter_len):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # AXI LITE ----------------------------------------------------------------------------------
        axil = AXILiteInterface(
            data_width      = data_width,
            address_width   = addr_width
        )
        platform.add_extension(axil.get_ios("m_axil"))
        self.comb += axil.connect_to_pads(platform.request("m_axil"), mode="master")

        # I2C_SLAVE ----------------------------------------------------------------------------------
        self.submodules.i2c_slave = i2c_slave = I2CSLAVE(platform, 
            m_axil        = axil,
            filter_len    = filter_len
            )
        
        # I2C Signals---------------------------------------------------------------------------------
        platform.add_extension(get_i2c_ios())
        i2c_pads = platform.request("i2c")
        self.comb += [
            i2c_slave.i2c_scl_i.eq(i2c_pads.scl_i),
            i2c_pads.scl_o.eq(i2c_slave.i2c_scl_o),
            i2c_pads.scl_t.eq(i2c_slave.i2c_scl_t),

            i2c_slave.i2c_sda_i.eq(i2c_pads.sda_i),
            i2c_pads.sda_o.eq(i2c_slave.i2c_sda_o),
            i2c_pads.sda_t.eq(i2c_slave.i2c_sda_t),
        ]
        
        # Configuration
        self.comb += i2c_slave.enable.eq(platform.request("enable"))
        self.comb += i2c_slave.device_address.eq(platform.request("device_address"))
        
        # Status
        self.comb += platform.request("busy").eq(i2c_slave.busy)
        self.comb += platform.request("bus_addressed").eq(i2c_slave.bus_addressed)
        self.comb += platform.request("bus_active").eq(i2c_slave.bus_active)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="I2C SLAVE CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core Parameters")
    core_group.add_argument("--data_width",     default=32,       type=int,            help="I2C_slave Data Width 8,16,32,64")
    core_group.add_argument("--addr_width",     default=16,       type=int,            help="I2C_slave Address Width 8,16,32")
    core_group.add_argument("--filter_len",     default=4,        type=int,            help="I2C_slave Filter Lenght from 1 to 4")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build Parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="i2c_slave_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Data Width
    data_width_param=[8, 16, 32, 64]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s", data_width_param)
        exit()
        
    # Address Width
    addr_width_param=[8, 16, 32]
    if args.addr_width not in addr_width_param:
        logger.error("\nEnter a valid 'addr_width'\n %s", addr_width_param)
        exit()

    # Filter Length
    filter_len_range=range(1,5)
    if args.filter_len not in filter_len_range:
        logger.error("\nEnter a valid 'filter_len' from 1 to 4")
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
    rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="i2c_slave")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()

    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform(io=[], device="gemini", toolchain="raptor")
    module     = I2CSLAVEWrapper(platform,
        data_width    = args.data_width,
        addr_width    = args.addr_width,
        filter_len    = args.filter_len
    )

    # Build
    if args.build:
        rs_builder.build(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
