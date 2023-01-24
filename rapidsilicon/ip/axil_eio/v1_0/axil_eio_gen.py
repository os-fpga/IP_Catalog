#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

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

    # Core fixed values parameters
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",    type=int,  default=32, choices=[32, 64],  help="AXI Data Width.")
    core_fix_param_group.add_argument("--addr_width",    type=int,  default=32, choices=[32],      help="AXI Address Width.")
    
    # Core Range Value Parameters
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--inout_probe_width",   type=int,  default=8,  choices=range(1, 513),  help="No. of input probes.")
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

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXILEIOWrapper(platform,
                            data_width          = args.data_width,
                            addr_width          = args.addr_width,
                            input_probe_width   = args.inout_probe_width, 
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
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module
        )

if __name__ == "__main__":
    main()
