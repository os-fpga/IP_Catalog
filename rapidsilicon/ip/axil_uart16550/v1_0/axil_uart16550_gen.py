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

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--addr_width",       type=int,       default=16,     choices=[8, 16, 32],        help="UART Address Width.")
    core_fix_param_group.add_argument("--data_width",       type=int,       default=32,     choices=[32, 64],    help="UART Data Width.")

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

    details =  {   "IP details": {
    'Name' : 'AXILite UART 16550',
    'Version' : 'V1_0',
    'Interface' : 'AXI-Lite',
    'Description' : 'AXI Lite UART is a type of Universal Asynchronous Receiver-Transmitter (UART) that uses the AXI Lite protocol to interface with other devices in an embedded system. UARTs are commonly used to transmit and receive data between a microcontroller or processor and other devices.'}
    }

    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

    summary =  { 
    "AXILite Data Width": args.data_width,
    "AXILite Address Width": args.addr_width,
    "Operation Mode" : "FIFO Mode",
    "Word Width" : "8 Bits"
    }
    if (args.data_width == 32):
        summary["Debug Interface"] = "Yes"
    else:
        summary["Debug Interface"] = "No"

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
        
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axil_uart16550", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"AXIL_URT\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
