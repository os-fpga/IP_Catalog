#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from litex_wrapper.i2c_slave_litex_wrapper import I2CSLAVE

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

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="i2c_slave", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",       type=int,       default=32,         choices=[32, 64],    help="I2C_slave Data Width.")
    core_fix_param_group.add_argument("--addr_width",       type=int,       default=16,         choices=[8, 16, 32],        help="I2C_slave Address Width.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--filter_len",     type=int,       default=4,          choices=range(1,5),      help="I2C_slave Filter Length.")

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
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = I2CSLAVEWrapper(platform,
        data_width = args.data_width,
        addr_width = args.addr_width,
        filter_len = args.filter_len,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v1_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
