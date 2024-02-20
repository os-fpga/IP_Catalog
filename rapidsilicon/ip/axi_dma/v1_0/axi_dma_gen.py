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

from litex_wrapper.axi_dma_litex_wrapper import AXIDMA

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXIInterface

from litex.soc.interconnect.axi import AXIStreamInterface


# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk", 0, Pins(1)),
        ("rst", 0, Pins(1))
    ]

def get_axis_ios(axi_addr_width, len_width, axi_id_width, tag_width, axis_dest_width, axis_user_width):
    return [
        ("s_axis_read_desc", 0,
            Subsignal("addr",   Pins(axi_addr_width)), 
            Subsignal("len",    Pins(len_width)),
            Subsignal("tag",    Pins(tag_width)), 
            Subsignal("id",     Pins(axi_id_width)), 
            Subsignal("dest",   Pins(axis_dest_width)), 
            Subsignal("user",   Pins(axis_user_width)),
            Subsignal("valid",  Pins(1)),
            Subsignal("ready",  Pins(1))
        ),
        
        ("m_axis_read_desc_status", 0,
            Subsignal("tag",    Pins(tag_width)), 
            Subsignal("error",  Pins(4)),
            Subsignal("valid",  Pins(1))
        ),
        
        ("s_axis_write_desc", 0,
            Subsignal("addr",   Pins(axi_addr_width)), 
            Subsignal("len",    Pins(len_width)), 
            Subsignal("tag",    Pins(tag_width)), 
            Subsignal("valid",  Pins(1)),
            Subsignal("ready",  Pins(1))
        ),
        
        ("m_axis_write_desc_status", 0,
            Subsignal("len",    Pins(len_width)), 
            Subsignal("tag",    Pins(tag_width)), 
            Subsignal("id",     Pins(axi_id_width)), 
            Subsignal("dest",   Pins(axis_dest_width)), 
            Subsignal("user",   Pins(axis_user_width)), 
            Subsignal("error",  Pins(4)),
            Subsignal("valid",  Pins(1))
        ),
        
        ("read_enable",     0, Pins(1)),
        ("write_enable",    0, Pins(1)),
        ("write_abort",     0, Pins(1))
    ]
    
# AXI-DMA Wrapper --------------------------------------------------------------------------------
class AXIDMAWrapper(Module):
    def __init__(self, platform, axi_data_width, axi_addr_width, axi_id_width, axi_max_burst_len, 
                axis_last_enable, axis_id_enable, axis_id_width, axis_dest_enable, axis_dest_width,
                axis_user_enable, axis_user_width, len_width, tag_width, enable_sg, enable_unaligned):
        
        # Clocking
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        self.comb += self.cd_sys.rst.eq(platform.request("rst"))
        
        # AXI
        axi = AXIInterface(
            data_width      = axi_data_width,
            address_width   = axi_addr_width,
            id_width        = axi_id_width,
        )
        m_axis = AXIStreamInterface(
            data_width      = axi_data_width,
            user_width      = axis_user_width,
            dest_width      = axis_dest_width,
            id_width        = axis_id_width
        )
        
        s_axis = AXIStreamInterface(
            data_width      = axi_data_width,
            user_width      = axis_user_width,
            dest_width      = axis_dest_width,
            id_width        = axis_id_width
        )
        
        platform.add_extension(axi.get_ios("m_axi"))
        self.comb += axi.connect_to_pads(platform.request("m_axi"), mode="master")
        
        platform.add_extension(m_axis.get_ios("m_axis_read_data"))
        self.comb += m_axis.connect_to_pads(platform.request("m_axis_read_data"), mode="master")
        
        platform.add_extension(s_axis.get_ios("s_axis_write_data"))
        self.comb += s_axis.connect_to_pads(platform.request("s_axis_write_data"), mode="slave")
        
        # AXI_DMA
        self.submodules.dma = dma = AXIDMA(platform, 
            m_axi               = axi, 
            m_axis              = m_axis,
            s_axis              = s_axis, 
            axi_max_burst_len   = axi_max_burst_len,
            axis_last_enable    = axis_last_enable,
            axis_id_enable      = axis_id_enable,
            axis_dest_enable    = axis_dest_enable,
            axis_user_enable    = axis_user_enable,            
            len_width           = len_width,
            tag_width           = tag_width,
            enable_sg           = enable_sg,
            enable_unaligned    = enable_unaligned
            )
        
        # Descriptor IOs
        platform.add_extension(get_axis_ios(axi_addr_width, len_width, axi_id_width, tag_width, axis_dest_width, axis_user_width))
        s_desc_pads = platform.request("s_axis_read_desc")
        self.comb += [
            dma.s_axis_read_desc_addr.eq(s_desc_pads.addr),
            dma.s_axis_read_desc_len.eq(s_desc_pads.len),
            dma.s_axis_read_desc_tag.eq(s_desc_pads.tag),
            dma.s_axis_read_desc_id.eq(s_desc_pads.id),
            dma.s_axis_read_desc_dest.eq(s_desc_pads.dest),
            dma.s_axis_read_desc_user.eq(s_desc_pads.user),
            dma.s_axis_read_desc_valid.eq(s_desc_pads.valid),
            s_desc_pads.ready.eq(dma.s_axis_read_desc_ready)
        ]
        
        m_desc_pads = platform.request("m_axis_read_desc_status")
        self.comb += [
            m_desc_pads.tag.eq(dma.m_axis_read_desc_status_tag),
            m_desc_pads.error.eq(dma.m_axis_read_desc_status_error),
            m_desc_pads.valid.eq(dma.m_axis_read_desc_status_valid),
        ]
        
        s_desc_pads = platform.request("s_axis_write_desc")
        self.comb += [
            dma.s_axis_write_desc_addr.eq(s_desc_pads.addr),
            dma.s_axis_write_desc_len.eq(s_desc_pads.len),
            dma.s_axis_write_desc_tag.eq(s_desc_pads.tag),
            dma.s_axis_write_desc_valid.eq(s_desc_pads.valid),
            s_desc_pads.ready.eq(dma.s_axis_write_desc_ready)
        ]
        
        s_desc_pads = platform.request("m_axis_write_desc_status")
        self.comb += [
            s_desc_pads.len.eq(dma.m_axis_write_desc_status_len),
            s_desc_pads.tag.eq(dma.m_axis_write_desc_status_tag),
            s_desc_pads.id.eq(dma.m_axis_write_desc_status_id),
            s_desc_pads.dest.eq(dma.m_axis_write_desc_status_dest),
            s_desc_pads.user.eq(dma.m_axis_write_desc_status_user),
            s_desc_pads.error.eq(dma.m_axis_write_desc_status_error),
            s_desc_pads.valid.eq(dma.m_axis_write_desc_status_valid),
        ]
        
        self.comb += dma.read_enable.eq(platform.request("read_enable"))
        self.comb += dma.write_enable.eq(platform.request("write_enable"))
        self.comb += dma.write_abort.eq(platform.request("write_abort"))

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI DMA CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports         :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axi_dma", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--axi_data_width",    type=int,      default=32,     choices=[8, 16, 32, 64, 128, 256],      help="DMA Data Width.")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--axis_last_enable",    type=bool,      default=True,       help="DMA AXI stream tlast.")
    core_bool_param_group.add_argument("--axis_id_enable",      type=bool,      default=False,      help="DMA AXI stream tid.")
    core_bool_param_group.add_argument("--axis_dest_enable",    type=bool,      default=False,      help="DMA AXI stream tdest.")
    core_bool_param_group.add_argument("--axis_user_enable",    type=bool,      default=True,       help="DMA AXI stream tuser.")
    core_bool_param_group.add_argument("--enable_sg",           type=bool,      default=False,      help="Support for scatter/gather DMA.")
    core_bool_param_group.add_argument("--enable_unaligned",    type=bool,      default=False,      help="Support for unaligned transfers.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--axi_addr_width",     type=int,       default=16,     choices=range(8, 17),     help="DMA Address Width.")
    core_range_param_group.add_argument("--axi_id_width",       type=int,       default=8,      choices=range(1, 33),     help="DMA ID Width.")
    core_range_param_group.add_argument("--axi_max_burst_len",  type=int,       default=16,     choices=range(1, 257),    help="DMA AXI burst length.")
    core_range_param_group.add_argument("--axis_id_width",      type=int,       default=8,      choices=range(1, 33),     help="DMA AXI stream tid width.")
    core_range_param_group.add_argument("--axis_dest_width",    type=int,       default=8,      choices=range(1, 9),      help="DMA AXI stream tdest width.")
    core_range_param_group.add_argument("--axis_user_width",    type=int,       default=1,      choices=range(1, 9),      help="DMA AXIS User Width.")
    core_range_param_group.add_argument("--len_width",          type=int,       default=20,     choices=range(1, 21),     help="DMA AXI Width of length field.")
    core_range_param_group.add_argument("--tag_width",          type=int,       default=8,      choices=range(1, 9),      help="DMA Width of tag field.")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axi_dma_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'AXI Direct Memory Access',
    'Version' : 'V1_0',
    'Interface' : 'AXI4, AXI-Stream',
    'Description' : 'The AXI DMA soft IP facilitates seamless, high-speed data transfer between memory and peripherals bypassing any CPU, enhancing overall FPGA system efficiency and performance. This IP core simplifies complex data handling tasks, making it a valuable addition to various FPGA designs.'}
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version    = "v1_0")

        if (args.axis_id_enable == False):
            dep_dict.update({
                'axi_id_width' :   'True',
            })
        else:
            dep_dict.update({
                'axi_id_width' :   'False',
            })
        if (args.axis_dest_enable == False):
            dep_dict.update({
                'axis_dest_width' :   'True',
            })
        else:
            dep_dict.update({
                'axis_dest_width' :   'False',
            })
        if (args.axis_user_enable == False):
            dep_dict.update({
                'axis_user_width' :   'True',
            })
        else:
            dep_dict.update({
                'axis_user_width' :   'False',
            })        

        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
    
    summary =  { 
    "AXI Data Width" : args.axi_data_width,
    "AXI Address Width" : args.axi_addr_width,
    "Descriptor Interface" : "AXI-Stream",
    "Master Interface" : "AXI"
    }

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = AXIDMAWrapper(platform,
        axi_data_width    = args.axi_data_width,
        axi_addr_width    = args.axi_addr_width,
        axi_id_width      = args.axi_id_width,
        axi_max_burst_len = args.axi_max_burst_len,
        axis_last_enable  = args.axis_last_enable,
        axis_id_enable    = args.axis_id_enable,
        axis_id_width     = args.axis_id_width,
        axis_dest_enable  = args.axis_dest_enable,
        axis_dest_width   = args.axis_dest_width,
        axis_user_enable  = args.axis_user_enable,
        axis_user_width   = args.axis_user_width,
        len_width         = args.len_width,
        tag_width         = args.tag_width,
        enable_sg         = args.enable_sg,
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axi_dma", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"ADMA\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
