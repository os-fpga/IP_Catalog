#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from litex_wrapper.soc_fpga_intf_irq_litex_wrapper import SOC_FPGA_INTF_IRQ

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs/Interfaces -----------------------------------------------------------------------------------

def get_other_ios():
        return [    
            ("irq_src",         0, Pins(16)), 
            ("irq_set",         0, Pins(16)), 
            ("irq_clk",         0, Pins(1)), 
            ("irq_rst_n",       0, Pins(1)), 
        ]
# SOC_FPGA_INTF_AHB_S Wrapper ----------------------------------------------------------------------------------
class IRQWrapper(Module):
    def __init__(self, platform):

        self.clock_domains.cd_sys  = ClockDomain()

        self.submodules.soc_fpga_intf_irq = soc_fpga_intf_irq = SOC_FPGA_INTF_IRQ(platform)

        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_other_ios())
        self.comb += soc_fpga_intf_irq.irq_src.eq(platform.request("irq_src"))
        self.comb += soc_fpga_intf_irq.irq_clk.eq(platform.request("irq_clk"))
        self.comb += soc_fpga_intf_irq.irq_rst_n.eq(platform.request("irq_rst_n"))

        self.comb += platform.request("irq_set").eq(soc_fpga_intf_irq.irq_set)

        # AXI-RAM ----------------------------------------------------------------------------------
        self.submodules += SOC_FPGA_INTF_IRQ(platform)

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SOC_FPGA_INTF_AHB_S CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="soc_fpga_intf_irq", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="soc_fpga_intf_irq_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

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
    module   = IRQWrapper(platform)

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
