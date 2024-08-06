#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse
import math

from datetime import datetime

from litex_wrapper.ddr_sdram_litex_wrapper import AXIDDR

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios():
    return [
        ("clk",  0, Pins(1)),
        ("rst",  0, Pins(1)),
    ]

def ddr_interface(ba_bits, row_bits, dq_level):
    x = ((1 << dq_level) + 1) // 2 - 1
    y = ((4 << dq_level) + 1) // 2 - 1
    return [    
        ("ddr_ck_p",     0,  Pins(1)),
        ("ddr_ck_n",     0,  Pins(1)),
        ("ddr_cke",      0,  Pins(1)),
        ("ddr_cs_n",     0,  Pins(1)),
        ("ddr_ras_n",    0,  Pins(1)),
        ("ddr_cas_n",    0,  Pins(1)),
        ("ddr_we_n",     0,  Pins(1)),
        ("ddr_ba",       0,  Pins(ba_bits)),
        ("ddr_a",        0,  Pins(row_bits)),
        ("ddr_dm",       0,  Pins(x)),
        ("ddr_dqs",      0,  Pins(x)),
        ("ddr_dq",       0,  Pins(y)),
    ]

def ddr_inst(self, platform, ba_bits, row_bits, col_bits, dq_level, read_buffer):

        platform.add_extension(ddr_interface(ba_bits, row_bits, dq_level))

        platform.add_extension(get_clkin_ios())

        s_axil = AXILiteInterface()

        platform.add_extension(s_axil.get_ios("s_axil"))
        self.comb += s_axil.connect_to_pads(platform.request("s_axil"), mode="slave")

        self.specials += Instance("ddr_sdram_ctrl",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE         = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID           = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION      = Instance.PreformattedParam("IP_VERSION"),
            p_BA_BITS         = Instance.PreformattedParam(ba_bits),
            p_ROW_BITS        = Instance.PreformattedParam(row_bits),
            p_COL_BITS        = Instance.PreformattedParam(col_bits),
            p_DQ_LEVEL        = Instance.PreformattedParam(dq_level),
            p_READ_BUFFER     = Instance.PreformattedParam(read_buffer),
           # ----------
            i_clk             = platform.request("clk"),
            i_rstn_async             = platform.request("rst"),


            
            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
           i_awaddr   = s_axil.aw.addr,
           i_awvalid  = s_axil.aw.valid,
           o_awready  = s_axil.aw.ready,

           # W.
           i_wdata    = s_axil.w.data,
#           i_wstrb    = s_axil.w.strb,
           i_wvalid   = s_axil.w.valid,
           o_wready   = s_axil.w.ready,

           # B.
#           o_bresp    = s_axil.b.resp,
           o_bvalid   = s_axil.b.valid,
           i_bready   = s_axil.b.ready,

           # AR.
           i_araddr   = s_axil.ar.addr,
           i_arvalid  = s_axil.ar.valid,
           o_arready  = s_axil.ar.ready,

           # R.
           o_rdata    = s_axil.r.data,
#           o_rresp    = s_axil.r.resp,
           o_rvalid   = s_axil.r.valid,
           i_rready   = s_axil.r.ready,
#
#
#            # DDR Signals
#
#                    
           o_ddr_ck_p         = platform.request("ddr_ck_p"),     
           o_ddr_ck_n         = platform.request("ddr_ck_n"),     
           o_ddr_cke          = platform.request("ddr_cke"), 
           o_ddr_cs_n         = platform.request("ddr_cs_n"),     
           o_ddr_ras_n        = platform.request("ddr_ras_n"),     
           o_ddr_cas_n        = platform.request("ddr_cas_n"),     
           o_ddr_we_n         = platform.request("ddr_we_n"),     
           o_ddr_ba           = platform.request("ddr_ba"), 
           o_ddr_a            = platform.request("ddr_a"), 
           o_ddr_dm           = platform.request("ddr_dm"), 
            io_ddr_dqs         = platform.request("ddr_dqs"), #self.ddr_dqs, 
            io_ddr_dq          = platform.request("ddr_dq") #self.ddr_dq
            
        )

# DDR SDRAM Wrapper ----------------------------------------------------------------------------------
class DDRWRAPPER(Module):
    def __init__(self, platform, ba_bits, row_bits, col_bits, dq_level, read_buffer):
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_clkin_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        # self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        # self.comb += self.cd_sys.rst.eq(platform.request("rst"))

        ddr_inst(self, platform, ba_bits, row_bits, col_bits, dq_level, read_buffer)

        # AXI --------------------------------------------------------------------------------------





# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI DDR SDRAM CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}
    

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="ddr_sdram", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.

    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--ba_bits",        type=int,   default=2,      choices=range(1, 5),     help="BANK ADDRESS WIDTH")
    core_range_param_group.add_argument("--row_bits",       type=int,   default=13,      choices=range(1, 16),     help="Row address Width")
    core_range_param_group.add_argument("--col_bits",       type=int,   default=11,      choices=range(1, 15),     help="Column Address Width")
    core_range_param_group.add_argument("--dq_level",       type=int,   default=2,      choices=range(1, 3),     help="DQ level")
    core_range_param_group.add_argument("--read_buffer",    type=int,   default=0,   choices=range(1, 2),    help="Enable read buffer")



    # Core file path parameters.
    # core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    # core_file_path_group.add_argument("--file_path", type=argparse.FileType('r'), help="File Path for memory initialization file")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="ddr_sdram_wrapper",      help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'DDR SDRAM',
    'Version' : 'V1_0',
    'Interface' : 'AXI',
    'Description' : ' DDR1-SDRAM controller with a AXI4 slave port.'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        
        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.copy_images(file_path)
        
    summary =  {  
    "Row address width": args.row_bits,
    "Column address Width": args.col_bits,
    "Data bit width based on DQ Level": 2**args.dq_level,
    # "PIPELINE OUTPUT": args.pip_out
    }
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)


    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = DDRWRAPPER(platform, 
        ba_bits         = args.ba_bits,
        row_bits        = args.row_bits, 
        col_bits        = args.col_bits, 
        dq_level        = args.dq_level, 
        read_buffer     = args.read_buffer    )

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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "ddr_sdram", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"DDR\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
