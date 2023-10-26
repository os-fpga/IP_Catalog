#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from datetime import datetime

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
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="i2c_master", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--default_prescale",    type=bool,        default=True,         help="I2C Default Prescale.")
    core_bool_param_group.add_argument("--fixed_prescale",      type=bool,        default=False,        help="I2C Fixed Prescale.")
    core_bool_param_group.add_argument("--cmd_fifo",            type=bool,        default=True,         help="I2C FIFO Command Enable.")
    core_bool_param_group.add_argument("--write_fifo",          type=bool,        default=True,         help="I2C FIFO Write Enable.")
    core_bool_param_group.add_argument("--read_fifo",           type=bool,        default=True,         help="I2C FIFO Read Enable.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--cmd_addr_width",         type=int,      default=5,     choices=range(1, 6),      help="I2C FIFO Command Address Width.")
    core_range_param_group.add_argument("--write_addr_width",       type=int,      default=5,     choices=range(1, 6),      help="I2C FIFO Write Address Width.")
    core_range_param_group.add_argument("--read_addr_width",        type=int,      default=5,     choices=range(1, 6),      help="I2C FIFO Read Address Width.")

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

    details =  {   "IP details": {
    'Name' : 'AXI-Lite I2C Master',
    'Version' : 'V1_0',
    'Interface' : 'AXI-Lite, I2C',
    'Description' : 'An I2C master is a device that initiates and controls the communication on the I2C bus. The master device generates the clock signal, initiates the start and stop conditions, and controls the flow of data on the bus.'}
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        

    summary =  { 
    "Write Address Width" : args.write_addr_width,
    "Read Address Width" : args.read_addr_width,
    "Status Register" : "0x00",
    "Command Register" : "0x04",
    "Data Register" : "0x08",
    "Prescale Register" : "0x0C"
    }

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "i2c_master", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"I2C_MSTR\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
