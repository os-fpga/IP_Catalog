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

from litex_wrapper.reset_release_litex_wrapper import RESETRELEASE

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1))
    ]

def get_other_ios(peripheral_aresetn, interconnects ,bus_reset,  peripheral_reset):
        return [    
            ("slow_clk",        0, Pins(1)), 
            ("ext_rst",         0, Pins(1)), 
            ("cpu_dbg_rst",     0, Pins(1)), 
            ("pll_lock",        0, Pins(1)), 

            ("cpu_rst",             0, Pins(1)), 
            ("periph_aresetn",      0, Pins(peripheral_aresetn)), 
            ("interconnect_aresetn",0, Pins(interconnects)), 
            ("bus_reset",           0, Pins(bus_reset)), 
            ("periph_reset",        0, Pins(peripheral_reset)), 
        ]

# RESET_RELEASE Wrapper ----------------------------------------------------------------------------------
class RESETRELEASEWrapper(Module):
    def __init__(self, platform, ext_reset_width, interconnects, bus_reset, peripheral_reset,peripheral_aresetn):
        
        self.clock_domains.cd_sys  = ClockDomain()
        
        # RESET_RELEASE ----------------------------------------------------------------------------------
        self.submodules.reset_release = reset_release = RESETRELEASE(platform,
            EXT_RESET_WIDTH     = ext_reset_width,
            INTERCONNECTS       = interconnects,
            BUS_RESET           = bus_reset,
            PERIPHERAL_RESET    = peripheral_reset,
            PERIPHERAL_ARESETN  = peripheral_aresetn,
            )
        
        # IOS 
        platform.add_extension(get_other_ios(peripheral_aresetn, interconnects ,bus_reset,  peripheral_reset))
        self.comb += reset_release.slow_clk.eq(platform.request("slow_clk"))
        self.comb += reset_release.ext_rst.eq(platform.request("ext_rst"))
        self.comb += reset_release.cpu_dbg_rst.eq(platform.request("cpu_dbg_rst"))
        self.comb += reset_release.pll_lock.eq(platform.request("pll_lock"))

        self.comb += platform.request("cpu_rst").eq(reset_release.cpu_rst)
        self.comb += platform.request("periph_aresetn").eq(reset_release.periph_aresetn)
        self.comb += platform.request("interconnect_aresetn").eq(reset_release.interconnect_aresetn)
        self.comb += platform.request("bus_reset").eq(reset_release.bus_reset)
        self.comb += platform.request("periph_reset").eq(reset_release.periph_reset)
        

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="RESET_RELEASE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="reset_release", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--ext_reset_width",          type=int,    default=5,     choices=[4,5,6,7,8,9,10],           help="External reset window.")
    core_fix_param_group.add_argument("--peripheral_aresetn",       type=int,    default=1,     choices=[1,2,3,4,5,6,7,8,9,10],     help="Number of peripheral resets N.")
    core_fix_param_group.add_argument("--interconnects",            type=int,    default=1,     choices=[1,2,3,4,5,6,7,8,9,10],     help="Number of Interconnects.")
    core_fix_param_group.add_argument("--bus_reset",                type=int,    default=1,     choices=[1,2,3,4,5,6,7,8,9,10],     help="Number of bus reserts.")
    core_fix_param_group.add_argument("--peripheral_reset",         type=int,    default=1,     choices=[1,2,3,4,5,6,7,8,9,10],     help="Number of peripheral resets.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="reset_release_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    #IP Details generation
    details =  {   "IP details": {
    'Name' : 'Reset Release IP',
    'Version' : 'V1_0',
    'Interface' : 'Native',
    'Description' : 'This IP core provides a reliable mechanism for releasing reset signals to various modules and subsystems in a coordinated manner, preventing glitches and ensuring a smooth start-up sequence.'}}


    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

    #IP Summary generation
    summary =  { 
    "External reset window": args.ext_reset_width,
    "Number of peripheral resets N": args.peripheral_aresetn,
    "Number of Interconnects": args.interconnects,
    "Number of bus reserts": args.bus_reset,
    "Number of peripheral resets": args.peripheral_reset,
    }


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
    
    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = RESETRELEASEWrapper(platform,
        ext_reset_width     = args.ext_reset_width,
        interconnects       = args.interconnects,
        bus_reset           = args.bus_reset,
        peripheral_reset    = args.peripheral_reset,
        peripheral_aresetn  = args.peripheral_aresetn,   )

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "reset_release", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"RST_RLSE\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
