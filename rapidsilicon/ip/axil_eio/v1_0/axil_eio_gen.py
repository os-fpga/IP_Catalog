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

from litex_wrapper.axil_eio_litex_wrapper import AXILEIO

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("S_AXI_ACLK",     0,  Pins(1)),
        ("OP_CLK",         0,  Pins(1)),
        ("IP_CLK",         0,  Pins(1)),
        ("S_AXI_ARESETN",  0,  Pins(1))
    ]

def input_output_probes(input_probe_width, output_probe_width):
    return [
        ("probe_in",   0, Pins(input_probe_width)),
        ("probe_out",  0, Pins(output_probe_width))
    ]

# AXIL_EIO Wrapper ----------------------------------------------------------------------------------
class AXILEIOWrapper(Module):
    def __init__(self, platform, data_width, addr_width, input_probe_width, output_probe_width, axi_input_clk_sync, axi_output_clk_sync):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        
        # AXI-LITE
        s_axi = AXILiteInterface(data_width = data_width, address_width = addr_width)
        platform.add_extension(s_axi.get_ios("s_axil"))
        self.comb += s_axi.connect_to_pads(platform.request("s_axil"), mode="slave")
            
        # AXIL_EIO
        self.submodules.axi_eio = axi_eio = AXILEIO(platform, 
                                                    s_axil              = s_axi,
                                                    input_probe_width   = input_probe_width, 
                                                    output_probe_width  = output_probe_width, 
                                                    axi_input_clk_sync  = axi_input_clk_sync, 
                                                    axi_output_clk_sync = axi_output_clk_sync
                                                    )

        self.comb += axi_eio.OP_CLK.eq(platform.request("OP_CLK"))
        self.comb += axi_eio.IP_CLK.eq(platform.request("IP_CLK"))
        self.comb += axi_eio.S_AXI_ACLK.eq(platform.request("S_AXI_ACLK"))
        self.comb += axi_eio.S_AXI_ARESETN.eq(platform.request("S_AXI_ARESETN"))

        platform.add_extension(input_output_probes(input_probe_width, output_probe_width))
        self.comb += axi_eio.probe_in.eq(platform.request("probe_in"))
        self.comb += platform.request("probe_out").eq(axi_eio.probe_out)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="EMULATE IO")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    dep_dict = {} 

    # IP Builder
    rs_builder = IP_Builder(device="gemini", ip_name="axil_eio", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fixed values parameters
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",    type=int,  default=32, choices=[32, 64],  help="AXI Data Width.")
    core_fix_param_group.add_argument("--addr_width",    type=int,  default=32, choices=[32],      help="AXI Address Width.")
    
    # Core Range Value Parameters
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--input_probe_width",   type=int,  default=8,  choices=range(1, 513),  help="No. of input probes.")
    core_range_param_group.add_argument("--output_probe_width",  type=int,  default=8,  choices=range(1, 513),  help="No. of output probes.")
    
    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--axi_input_clk_sync",   type=bool,  default=False,  help="AXI and input clock sync.")
    core_bool_param_group.add_argument("--axi_output_clk_sync",  type=bool,  default=False,  help="AXI and output clock sync.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axil_eio_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'EIO',
    'Version' : 'V1_0',
    'Interface' : 'AXI4-Lite ',
    'Description' : 'The Emulate-IO core is an AXI4-Lite compliant IP that offers input and output probes to sample and drive signals on FPGA fabric. The core provides an AXI4-slave interface that can be used to control the emulated IOs in real time.'}
    }
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")

    summary =  { 
    # "DATA WIDTH": args.data_width,
    "DATA WIDTH":args.data_width,
    "ADDR WIDTH": args.addr_width,
    "INPUT PROBE WIDTH": args.input_probe_width,
    "OUTPUT PROBE WIDTH": args.output_probe_width,


    # "PIPELINE OUTPUT": args.pip_out
    }

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)


    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXILEIOWrapper(platform,
                            data_width          = args.data_width,
                            addr_width          = args.addr_width,
                            input_probe_width   = args.input_probe_width, 
                            output_probe_width  = args.output_probe_width, 
                            axi_input_clk_sync  = args.axi_input_clk_sync, 
                            axi_output_clk_sync = args.axi_output_clk_sync
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
            version    = "v1_0"
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axil_eio", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"EIO\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
