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

from litex_sim.axis_uart_litex_wrapper import AXISTREAMUART

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIStreamInterface

# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1))
    ]
    
def get_uart_ios():
    return [
        ("rxd",             0, Pins(1)),
        ("txd",             0, Pins(1)), 
        ("tx_busy",         0, Pins(1)),
        ("rx_busy",         0, Pins(1)),
        ("rx_overrun_error",0, Pins(1)),
        ("rx_frame_error",  0, Pins(1)),
        ("prescale",        0, Pins(16))       
    ]
    
# AXI_STREAM_UART Wrapper ----------------------------------------------------------------------------------
class AXISTREAMUARTWrapper(Module):
    def __init__(self, platform, data_width):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())  
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI STREAM -------------------------------------------------------------------------------
        s_axis = AXIStreamInterface(
            data_width = data_width
        )
        
        m_axis = AXIStreamInterface(
            data_width = data_width
        )
        
        # Input AXI
        platform.add_extension(s_axis.get_ios("s_axis"))
        self.comb += s_axis.connect_to_pads(platform.request("s_axis"), mode="slave")
        
        # Output AXI
        platform.add_extension(m_axis.get_ios("m_axis"))
        self.comb += m_axis.connect_to_pads(platform.request("m_axis"), mode="master")
        
        # AXIS-UART ----------------------------------------------------------------------------------
        self.submodules.uart = uart = AXISTREAMUART(platform, 
            m_axis  = m_axis,
            s_axis  = s_axis
            )
        
        # UART Signals--------------------------------------------------------------------------------
        platform.add_extension(get_uart_ios())
        
        # Inputs
        self.comb += uart.rxd.eq(platform.request("rxd"))
        self.comb += uart.prescale.eq(platform.request("prescale"))
        
        # Outputs
        self.comb += platform.request("txd").eq(uart.txd)
        self.comb += platform.request("tx_busy").eq(uart.tx_busy)
        self.comb += platform.request("rx_busy").eq(uart.rx_busy)
        self.comb += platform.request("rx_overrun_error").eq(uart.rx_overrun_error)
        self.comb += platform.request("rx_frame_error").eq(uart.rx_frame_error)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXIS UART CORE")
    parser.formatter_class = lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog,
        max_help_position = 10,
        width             = 120
    )

    # Core Parameters.
    core_group = parser.add_argument_group(title="Core parameters")
    core_group.add_argument("--data_width",     default=5,     type=int,        help="UART Data Width from 5 to 8")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axis_uart_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    # Parameter Check -------------------------------------------------------------------------------
    logger = logging.getLogger("Invalid Parameter Value")

    # Data Width
    data_width_range=range(5,9)
    if args.data_width not in data_width_range:
        logger.error("\nEnter a valid 'data_width' from 5 to 8")
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
    sys.path.append("../../") # FIXME
    from common import RapidSiliconIPCatalogBuilder
    rs_builder = RapidSiliconIPCatalogBuilder(ip_name="axis_uart")

    if args.build:
        rs_builder.prepare(build_dir=args.build_dir, build_name=args.build_name)
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))

        # Design Path
        design_path = os.path.join("../src", (args.build_name + ".v")) 
        
        # TCL File Content        
        tcl = []
        # Create Design.
        tcl.append(f"create_design {args.build_name}")
        # Set Device.
        tcl.append(f"target_device {'GEMINI'}")
        # Add Include Path.
        tcl.append(f"add_library_path {'../src'}")
        # Add Sources.
#        for f, typ, lib in file_name:
        tcl.append(f"add_design_file {design_path}")
        # Set Top Module.
        tcl.append(f"set_top_module {args.build_name}")
        # Add Timings Constraints.
#        tcl.append(f"add_constraint_file {args.build_name}.sdc")
        # Run.
        tcl.append("synthesize")

        # Generate .tcl file
        tcl_path = os.path.join(rs_builder.synth_path, "raptor.tcl")
        with open(tcl_path, "w") as f:
            f.write("\n".join(tcl))
        f.close()

    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXISTREAMUARTWrapper(platform,
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
