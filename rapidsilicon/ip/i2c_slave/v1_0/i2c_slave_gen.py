#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse
from pathlib import Path

from datetime import datetime

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

    details =  {   "IP details": {
    'Name' : 'AXI-Lite I2C Slave',
    'Version' : 'V1_0',
    'Interface' : 'AXI-Lite, I2C',
    'Description' : 'An I2C slave device is a device that communicates with an I2C master device over an I2C bus. It recieves the clock and the start/stop conditions from the master and communicates with it for the exchange of data.'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")

        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.copy_images(file_path)
        
    summary =  {  
    "Data Width" : args.data_width,
    "Address Width" : args.addr_width,
    "Unaligned Writes" : "Supported with zero padding",
    "Control Parameter" : "Address of Slave Device"
    }

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)


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
        rs_builder.generate_tcl(version    = "v1_0")
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
            version = "v1_0"
        )
        
        # IP_ID Parameter
        now = datetime.now()
        my_year         = now.year - 2022
        year            = (bin(my_year)[2:]).zfill(7) # 7-bits  # Removing '0b' prefix = [2:]
        month           = (bin(now.month)[2:]).zfill(4) # 4-bits
        day             = (bin(now.day)[2:]).zfill(5) # 5-bits
        mod_hour        = now.hour % 12 # 12 hours Format
        hour            = (bin(mod_hour)[2:]).zfill(4) # 4-bits
        minute          = (bin(now.minute)[2:]).zfill(6) # 6-bits
        second          = (bin(now.second)[2:]).zfill(6) # 6-bits
        
        # Concatenation for IP_ID Parameter
        ip_id = ("{}{}{}{}{}{}").format(year, day, month, hour, minute, second)
        ip_id = ("32'h{}").format(hex(int(ip_id,2))[2:])
        
        # IP_VERSION parameter
        #               Base  _  Major _ Minor
        ip_version = "00000000_00000000_0000000000000001"
        ip_version = ("32'h{}").format(hex(int(ip_version, 2))[2:])
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "i2c_slave", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"I2CS\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)
        build_name = args.build_name.rsplit( ".", 1 )[ 0 ]
        file = os.path.join(args.build_dir, "rapidsilicon/ip/i2c_slave/v1_0", build_name, "sim/test_i2c_slave_axil_master.v")
        file = Path(file)
        text = file.read_text()
        text = text.replace("i2c_slave_wrapper", build_name)
        file.write_text(text)

if __name__ == "__main__":
    main()
