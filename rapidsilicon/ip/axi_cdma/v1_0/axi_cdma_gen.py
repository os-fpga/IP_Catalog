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

from litex_wrapper.axi_cdma_litex_wrapper import AXICDMA

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1))]

def get_axis_ios(addr_width, len_width, tag_width):
    return [
        ("s_axis_desc", 0,
            Subsignal("read_addr",  Pins(addr_width)),
            Subsignal("write_addr", Pins(addr_width)),
            Subsignal("len",        Pins(len_width)),
            Subsignal("tag",        Pins(tag_width)),
            Subsignal("valid",      Pins(1)),
            Subsignal("ready",      Pins(1))
        ),
        
        ("m_axis_desc_status", 0,
            Subsignal("tag",        Pins(tag_width)),
            Subsignal("error",      Pins(4)),
            Subsignal("valid",      Pins(1))
        ),
        
        ("enable",  0, Pins(1))
    ]

# AXI-CDMA Wrapper --------------------------------------------------------------------------------
class AXICDMAWrapper(Module):
    def __init__(self, platform, data_width, addr_width, id_width, axi_max_burst_len, len_width, tag_width, enable_unaligned):
    
        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        # AXI
        axi = AXIInterface(
            data_width      = data_width,
            address_width   = addr_width,
            id_width        = id_width
        )

        platform.add_extension(axi.get_ios("m_axi"))
        self.comb += axi.connect_to_pads(platform.request("m_axi"), mode="master")

        # AXI_CDMA
        self.submodules.cdma = cdma = AXICDMA(platform, axi,
            axi_max_burst_len   =  axi_max_burst_len,
            len_width           =  len_width,
            tag_width           =  tag_width,
            enable_unaligned    =  enable_unaligned
            )

        # Descriptor IOs
        platform.add_extension(get_axis_ios(addr_width, len_width, tag_width))
        s_desc_pads = platform.request("s_axis_desc")
        self.comb += [
            cdma.s_axis_desc_read_addr.eq(s_desc_pads.read_addr),
            cdma.s_axis_desc_write_addr.eq(s_desc_pads.write_addr),
            cdma.s_axis_desc_len.eq(s_desc_pads.len),
            cdma.s_axis_desc_tag.eq(s_desc_pads.tag),
            cdma.s_axis_desc_valid.eq(s_desc_pads.valid),
            s_desc_pads.ready.eq(cdma.s_axis_desc_ready)
        ]
        
        m_desc_pads = platform.request("m_axis_desc_status")
        self.comb += [
            m_desc_pads.tag.eq(cdma.m_axis_desc_status_tag),
            m_desc_pads.error.eq(cdma.m_axis_desc_status_error),
            m_desc_pads.valid.eq(cdma.m_axis_desc_status_valid),
        ]
        
        self.comb += cdma.enable.eq(platform.request("enable"))

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI CDMA CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary

    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_cdma", language="verilog")
    
    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",        type=int,      default=32,     choices=[8, 16, 32, 64, 128, 256], help="DMA Data Width.")

     # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--addr_width",        type=int,    default=16,     choices=range(8, 17),    help="DMA Address Width.")
    core_range_param_group.add_argument("--id_width",          type=int,    default=8,      choices=range(1, 33),    help="DMA ID Width.")
    core_range_param_group.add_argument("--axi_max_burst_len", type=int,    default=16,     choices=range(1,257),    help="DMA AXI burst length.")
    core_range_param_group.add_argument("--len_width",         type=int,    default=20,     choices=range(1,21),     help="DMA AXI Width of length field.")
    core_range_param_group.add_argument("--tag_width",         type=int,    default=8,      choices=range(1,9),      help="DMA Width of tag field.")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--enable_unaligned",  type=bool,    default=True,    help="Support for unaligned transfers.")

   
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_cdma_wrapper",     help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'CDMA',
    'Version' : 'V1_0',
    'Interface' : 'AXI4 ',
    'Description' : 'Central DMA (CDMA) is a type of Direct Memory Access (DMA) that provides high-bandwidth Direct Memory Access (DMA) between a memory-mapped source address and a memory-mapped destination address using the AXI4 protocol'}
    }

    summary =  { 
    # "DATA WIDTH": args.data_width,
    "DATA WIDTH":args.data_width,
    "ADDR WIDTH": args.addr_width,
    "BURST LENGTH": args.axi_max_burst_len,
    "TAG WIDTH": args.tag_width,
    # "PIPELINE OUTPUT": args.pip_out
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")


    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXICDMAWrapper(platform,
        data_width        = args.data_width,
        addr_width        = args.addr_width,
        id_width          = args.id_width,
        axi_max_burst_len = args.axi_max_burst_len,
        len_width         = args.len_width,
        tag_width         = args.tag_width,
        enable_unaligned  = args.enable_unaligned
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axi_cdma", "v1_0", args.build_name, "src",args.build_name+".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"CDMA1\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
