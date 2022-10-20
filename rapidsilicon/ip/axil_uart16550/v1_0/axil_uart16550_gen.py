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

from litex_sim.axil_uart16550_litex_wrapper import AXILITEUART

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("s_axi_aclk",      0, Pins(1)),
        ("s_axi_aresetn",   0, Pins(1)),
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
        self.comb += self.cd_sys.clk.eq(platform.request("s_axi_aclk"))
        self.comb += self.cd_sys.rst.eq(platform.request("s_axi_aresetn"))

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
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--addr_width",      default=16,       type=int,       help="UART Address Width 8,16,32")
    core_group.add_argument("--data_width",      default=32,       type=int,       help="UART Data Width 8,16,32,64")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axil_uart16550_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Address Width
    addr_width_param=[8, 16, 32]
    if args.addr_width not in addr_width_param:
        logger.error("\nEnter a valid 'addr_width'\n %s", addr_width_param)
        exit()
    
    # Data_Width
    data_width_param=[8, 16, 32, 64]
    if args.data_width not in data_width_param:
        logger.error("\nEnter a valid 'data_width'\n %s", data_width_param)
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
    rs_builder = RapidSiliconIPCatalogBuilder(device="gemini", ip_name="axil_uart16550")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()

    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXILITEUARTWrapper(platform,
        addr_width      = args.addr_width,
        data_width      = args.data_width
    )

    # Build
    if args.build:
        rs_builder.build(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
