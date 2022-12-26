#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from litex_wrapper.axil_uart16550_litex_wrapper import AXILITEUART

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("s_axil_aclk",      0, Pins(1)),
        ("s_axil_aresetn",   0, Pins(1)),
    ]
    
def get_uart_ios():
    return [
        ("int_o",       0, Pins(1)),
        ("srx_pad_i",   0, Pins(1)), 
        ("stx_pad_o",   0, Pins(1)),
        ("rts_pad_o",   0, Pins(1)),
        ("cts_pad_i",   0, Pins(1)),
        ("dtr_pad_o",   0, Pins(1)),
        ("dsr_pad_i",   0, Pins(1)),   
        ("ri_pad_i",    0, Pins(1)), 
        ("dcd_pad_i",   0, Pins(1))  
    ]

# AXI LITE UART Wrapper ----------------------------------------------------------------------------------
class AXILITEUARTWrapper(Module):
    def __init__(self, platform, addr_width, data_width):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("s_axil_aclk"))
        self.comb += self.cd_sys.rst.eq(platform.request("s_axil_aresetn"))

        # AXI LITE --------------------------------------------------------------------------------------
        axil = AXILiteInterface(
            address_width       = addr_width,
            data_width          = data_width
        )
        platform.add_extension(axil.get_ios("s_axil"))
        self.comb += axil.connect_to_pads(platform.request("s_axil"), mode="slave")

        # AXI-LITE-UART ----------------------------------------------------------------------------------
        self.submodules.uart = uart = AXILITEUART(platform, axil,  
            address_width       = addr_width, 
            data_width          = data_width
            )
        
        # UART Signals --------------------------------------------------------------------------------
        platform.add_extension(get_uart_ios())
        
        # Inputs
        self.comb += uart.srx_pad_i.eq(platform.request("srx_pad_i"))
        self.comb += uart.cts_pad_i.eq(platform.request("cts_pad_i"))
        self.comb += uart.dsr_pad_i.eq(platform.request("dsr_pad_i"))
        self.comb += uart.ri_pad_i.eq(platform.request("ri_pad_i"))
        self.comb += uart.dcd_pad_i.eq(platform.request("dcd_pad_i"))
        
        # Outputs
        self.comb += platform.request("int_o").eq(uart.int_o)
        self.comb += platform.request("stx_pad_o").eq(uart.stx_pad_o)
        self.comb += platform.request("rts_pad_o").eq(uart.rts_pad_o)
        self.comb += platform.request("dtr_pad_o").eq(uart.dtr_pad_o)


# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI LITE UART CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder
    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axil_uart16550", language="verilog")

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--addr_width",       type=int,       default=16,     choices=[8, 16, 32],        help="UART Address Width.")
    core_fix_param_group.add_argument("--data_width",       type=int,       default=32,     choices=[8, 16, 32, 64],    help="UART Data Width.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                 help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                        help="Build Directory")
    build_group.add_argument("--build-name",    default="axil_uart16550_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

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

    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXILITEUARTWrapper(platform,
        addr_width = args.addr_width,
        data_width = args.data_width,
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
