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

from litex_wrapper.axil_crossbar_litex_wrapper import AXILITECROSSBAR

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("ACLK",  0, Pins(1)),
        ("ARESET",  0, Pins(1)),
    ]


def get_clkin_ios_s(i):
    return [
        ("s{}_axi_aclk".format(i),  0, Pins(1)),
        ("s{}_axi_areset".format(i),  0, Pins(1)),
    ]
def get_clkin_ios_m(j):
    return [
        ("m{}_axi_aclk".format(j),  0, Pins(1)),
        ("m{}_axi_areset".format(j),  0, Pins(1)),
    ]


# AXI LITE CROSSBAR ----------------------------------------------------------------------------------
class AXILITECROSSBARWrapper(Module):
    def __init__(self, platform, s_count, m_count, data_width, addr_width,bram):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("ACLK"))
        self.comb += self.cd_sys.rst.eq(platform.request("ARESET"))


        for i in range (s_count):
            platform.add_extension(get_clkin_ios_s(i))
            self.clock_domains.cd_sys  = ClockDomain("s{}_axi_aclk".format(i))
            self.comb += self.cd_sys.clk.eq(platform.request("s{}_axi_aclk".format(i)))
            self.clock_domains.cd_sys  = ClockDomain("s{}_axi_areset".format(i))
            self.comb += self.cd_sys.rst.eq(platform.request("s{}_axi_areset".format(i)))

        for j in range (m_count):
            platform.add_extension(get_clkin_ios_m(j))
            self.clock_domains.cd_sys  = ClockDomain("m{}_axi_aclk".format(j))
            self.comb += self.cd_sys.clk.eq(platform.request("m{}_axi_aclk".format(j)))
            self.clock_domains.cd_sys  = ClockDomain("m{}_axi_areset".format(j))
            self.comb += self.cd_sys.rst.eq(platform.request("m{}_axi_areset".format(j)))

        # Slave Interfaces
        s_axils = []
        for s_count in range(s_count):
            s_axil = AXILiteInterface(data_width = data_width , address_width = addr_width)
            if s_count>9:
                platform.add_extension(s_axil.get_ios("s{}_axil".format(s_count)))
                self.comb += s_axil.connect_to_pads(platform.request("s{}_axil".format(s_count)), mode="slave")
            else:
                platform.add_extension(s_axil.get_ios("s0{}_axil".format(s_count)))
                self.comb += s_axil.connect_to_pads(platform.request("s0{}_axil".format(s_count)), mode="slave")
                
            s_axils.append(s_axil)
        
        # Master Interfaces
        m_axils = []    
        for m_count in range(m_count):
            m_axil = AXILiteInterface(data_width = data_width , address_width = addr_width)
            if m_count>9:
                platform.add_extension(m_axil.get_ios("m{}_axil".format(m_count)))
                self.comb += m_axil.connect_to_pads(platform.request("m{}_axil".format(m_count)), mode="master")
            else:
                platform.add_extension(m_axil.get_ios("m0{}_axil".format(m_count)))
                self.comb += m_axil.connect_to_pads(platform.request("m0{}_axil".format(m_count)), mode="master")
            
            m_axils.append(m_axil)

        # AXIL-CROSSBAR ----------------------------------------------------------------------------------
        self.submodules += AXILITECROSSBAR (platform, 
            s_axil      = s_axils,
            m_axil      = m_axils,
            s_count     = s_count,
            m_count     = m_count,
            bram        = bram,
            )

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI_LITE_CROSSBAR_CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axil_crossbar", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters")
    core_fix_param_group.add_argument("--data_width",    type=int,      default=32,     choices=[32, 64],  help="Crossbar Data Width.")
    core_fix_param_group.add_argument("--addr_width",    type=int,      default=32,     choices=[32, 64, 128, 256],         help="Crossbar Address Width.")

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--m_count",     type=int,      default=4,       choices=range(1,5),               help="Crossbar Master Interfaces.")
    core_range_param_group.add_argument("--s_count",     type=int,      default=4,       choices=range(1,5),               help="Crossbar Slave Interfaces.")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--bram",     type=bool,     default=True,      help="Memory type")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="axil_crossbar_wrapper",        help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    details =  {   "IP details": {
    'Name' : 'AXI Crossbar Lite',
    'Version' : 'V2_0',
    'Interface' : 'AXI4 Lite ',
    'Description' : 'The AXI4 Lite Crossbar is AXI4 compliance IP core that connects one or more AXI memory mapped master devices to more memory mapped slave devices. It has multiple clock support for each interface. Supports all burst types.  Fully nonblocking with completely separate read and write paths; FIFO-based transaction ordering protection logic; and per-port address decode, and decode error handling'}
    }
    
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v2_0")
    summary =  { 
    # "DATA WIDTH": args.data_width,
    "MASTER COUNT":args.m_count,
    "SLAVE COUNT": args.s_count,
    # "PIPELINE OUTPUT": args.pip_out
    }

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)



    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module     = AXILITECROSSBARWrapper(platform,
        m_count     = args.m_count,
        s_count     = args.s_count,
        data_width  = args.data_width,
        addr_width  = args.addr_width,
        bram        = args.bram,
    )

    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v2_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl(version    = "v1_0")
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
            version = "v2_0"
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "axil_crossbar", "v2_0", args.build_name, "src",args.build_name + "_" + "v2_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"ALXB\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
