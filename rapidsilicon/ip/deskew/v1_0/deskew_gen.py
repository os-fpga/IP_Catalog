#!/usr/bin/env python3
#
# This file is Copyright (c) 2024 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from datetime import datetime

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

def ios(num_dly, gearing_ratio):
    return [
        ("CLK_IN",          0, Pins(1)),
        ("RST",             0, Pins(1)),
        ("DATA_IN",         0, Pins(gearing_ratio*num_dly)),
        ("DLY_LOAD",        0, Pins(num_dly)),
        ("DLY_ADJ",         0, Pins(num_dly)),
        ("DLY_INCDEC",      0, Pins(num_dly)),
        ("DLY_TAP_VALUE",   0, Pins(6*num_dly)),
        ("CALIB_DONE",      0, Pins(num_dly)),
        ("CALIB_ERROR",     0, Pins(num_dly)),
        ("DLY_SEL",         0, Pins(1)),

    ]
    
def deskew(self, platform, num_dly, frequency, num_samples, gearing_ratio):
    platform.add_extension(ios(num_dly, gearing_ratio))
    # Module instance.
    # ----------------
    self.specials += Instance("deskew_cntrl_wrap",
    # Parameters.
    # -----------
    p_NUM_DLY               = num_dly,
    p_FREQ                  = frequency,
    p_WIDTH                 = gearing_ratio,
    p_SAMPLES_NO            = num_samples,
    # Ports.
    # -----------
    i_clk                   = platform.request("CLK_IN"),
    i_rst                   = platform.request("RST"),
    i_datain                = platform.request("DATA_IN"),    
    i_dly_tap_value_in      = platform.request("DLY_TAP_VALUE"),    
    o_dly_ld                = platform.request("DLY_LOAD"),
    o_dly_adj               = platform.request("DLY_ADJ"),
    o_dly_incdec            = platform.request("DLY_INCDEC"),
    o_dly_sel               = platform.request("DLY_SEL"),
    o_calib_done            = platform.request("CALIB_DONE"),
    o_calib_error           = platform.request("CALIB_ERROR")

    )
    
# DESKEW Wrapper ----------------------------------------------------------------------------------
class DeskewWrapper(Module):
    def __init__(self, platform, num_dly, frequency, num_samples, gearing_ratio):
        self.clock_domains.cd_sys  = ClockDomain()
        deskew(self, platform, num_dly, frequency, num_samples, gearing_ratio)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="DESKEW")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="virgo", ip_name="deskew", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core Parameters.
    core_range_param_group  = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--num_dly",                type=int,   default=4,     choices=range(1,5),              help="Number of IO_DELAYs")
    core_range_param_group.add_argument("--input_frequency",        type=int,   default=300,   choices=range(300, 2500001),     help="Input clock frequency")
    core_range_param_group.add_argument("--num_samples",            type=int,   default=10,    choices=range(10,301),           help="Number of IO_DELAYs")
    core_range_param_group.add_argument("--gearing_ratio",          type=int,   default=4,     choices=range(3,11),             help="Gearing Ratio for SERDES")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="deskew_wrapper",       help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'Deskew',
    'Version' : 'V1_0',
    'Interface' : 'Native',
    'Description' : 'Deskew is a Native interface IP Core'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        
        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.copy_images(file_path)
        
    summary =  {  
    "Gearing Ratio"         : args.gearing_ratio,
    "Clock Frequency (MHz)" : args.input_frequency    
    }
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="virgo")
    module   = DeskewWrapper(platform,
        num_dly         = args.num_dly,
        frequency       = args.input_frequency,
        num_samples     = args.num_samples,
        gearing_ratio   = args.gearing_ratio
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "deskew", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"DSKW\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(\n".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
