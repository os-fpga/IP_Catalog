#!/usr/bin/env python3
#
# This file is Copyright (c) 2024 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse

from datetime import datetime

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform


# IOs/Interfaces -----------------------------------------------------------------------------------
def Clocking():
    return [
        # GMII/ GMII_FIFO/ RGMII
        ("gtx_clk",         0, Pins(1)),
        ("gtx_rst",         0, Pins(1)),
        
        # GMII/ RGMII
        ("rx_clk",          0, Pins(1)),
        ("rx_rst",          0, Pins(1)),
        ("tx_clk",          0, Pins(1)),
        ("tx_rst",          0, Pins(1)),
        
        # GMII_FIFO/ RGMII_FIFO
        ("logic_clk",       0, Pins(1)),
        ("logic_rst",       0, Pins(1)),
        
        # RGMII/ RGMII_FIFO
        ("gtx_clk90",       0, Pins(1)),
    ]

def AXI_Stream():
    return [
        # AXI input
        ("tx_axis_tdata",           0, Pins(8)),
        ("tx_axis_tvalid",          0, Pins(1)),
        ("tx_axis_tready",          0, Pins(1)),
        ("tx_axis_tlast",           0, Pins(1)),
        ("tx_axis_tuser",           0, Pins(1)),
        ("tx_axis_tkeep",           0, Pins(1)),
        
        # AXI Output
        ("rx_axis_tdata",           0, Pins(8)),
        ("rx_axis_tvalid",          0, Pins(1)),
        ("rx_axis_tready",          0, Pins(1)),
        ("rx_axis_tlast",           0, Pins(1)),
        ("rx_axis_tuser",           0, Pins(1)),
        ("rx_axis_tkeep",           0, Pins(1))
    ]

def GMII_Interface():
    return [
        # GMII/ GMII_FIFO
        ("gmii_rx_clk",             0, Pins(1)),
        ("gmii_rxd",                0, Pins(8)),
        ("gmii_rx_dv",              0, Pins(1)),
        ("gmii_rx_er",              0, Pins(1)),
        ("mii_tx_clk",              0, Pins(1)),
        ("gmii_tx_clk",             0, Pins(1)),
        ("gmii_txd",                0, Pins(8)),
        ("gmii_tx_en",              0, Pins(1)),
        ("gmii_tx_er",              0, Pins(1))
    ]
    
def RGMII_Interface():
    return [
        # RGMII/ RGMII_FIFO
        ("rgmii_rx_clk",             0, Pins(1)),
        ("rgmii_rxd",                0, Pins(4)),
        ("rgmii_rx_ctl",             0, Pins(1)),
        ("rgmii_tx_clk",             0, Pins(1)),
        ("rgmii_txd",                0, Pins(4)),
        ("rgmii_tx_ctl",             0, Pins(1))
    ]
    
def Status():
    return [
        # GMII/ GMII_FIFO/ RGMII/ RGMII_FIFO
        ("tx_error_underflow",      0, Pins(1)),
        ("rx_error_bad_frame",      0, Pins(1)),
        ("rx_error_bad_fcs",        0, Pins(1)),
        ("speed",                   0, Pins(2)),
        
        # GMII_FIFO/ RGMII_FIFO
        ("tx_fifo_overflow",        0, Pins(1)),
        ("tx_fifo_bad_frame",       0, Pins(1)),
        ("tx_fifo_good_frame",      0, Pins(1)),
        ("rx_fifo_overflow",        0, Pins(2)),
        ("rx_fifo_bad_frame",       0, Pins(1)),
        ("rx_fifo_good_frame",      0, Pins(1))
    ]
    
def Configuration():
    return [
        # GMII/ GMII_FIFO/ RGMII
        ("cfg_ifg",                 0, Pins(8)),
        ("cfg_tx_enable",           0, Pins(1)),
        ("cfg_rx_enable",           0, Pins(1))
    ]

#################################################################################
# 1G_GMII_FIFO
#################################################################################
def _1G_GMII_FIFO(self, platform):
    platform.add_extension(Clocking())
    platform.add_extension(GMII_Interface())
    platform.add_extension(AXI_Stream())
    platform.add_extension(Configuration())
    platform.add_extension(Status())
    
    self.specials += Instance("eth_mac_1g_gmii_fifo", 
                        name= "eth_mac_1g_gmii_fifo_inst",
        # Ports
        # -----
        # Clocking
        i_gtx_clk                   = platform.request("gtx_clk"),
        i_gtx_rst                   = platform.request("gtx_rst"),
        i_logic_clk                 = platform.request("logic_clk"),
        i_logic_rst                 = platform.request("logic_rst"),
        
        # AXI input
        i_tx_axis_tdata             = platform.request("tx_axis_tdata"),
        i_tx_axis_tkeep             = platform.request("tx_axis_tkeep"),
        i_tx_axis_tvalid            = platform.request("tx_axis_tvalid"),    
        o_tx_axis_tready            = platform.request("tx_axis_tready"),    
        i_tx_axis_tlast             = platform.request("tx_axis_tlast"),
        i_tx_axis_tuser             = platform.request("tx_axis_tuser"),
        
        # AXI output
        o_rx_axis_tdata             = platform.request("rx_axis_tdata"),
        o_rx_axis_tkeep             = platform.request("rx_axis_tkeep"),
        o_rx_axis_tvalid            = platform.request("rx_axis_tvalid"),    
        i_rx_axis_tready            = platform.request("rx_axis_tready"),    
        o_rx_axis_tlast             = platform.request("rx_axis_tlast"),
        o_rx_axis_tuser             = platform.request("rx_axis_tuser"),
        
        # GMII interface
        i_gmii_rx_clk               = platform.request("gmii_rx_clk"),    
        i_gmii_rxd                  = platform.request("gmii_rxd"),
        i_gmii_rx_dv                = platform.request("gmii_rx_dv"),    
        i_gmii_rx_er                = platform.request("gmii_rx_er"),    
        i_mii_tx_clk                = platform.request("mii_tx_clk"),    
        o_gmii_tx_clk               = platform.request("gmii_tx_clk"),    
        o_gmii_txd                  = platform.request("gmii_txd"),
        o_gmii_tx_en                = platform.request("gmii_tx_en"),    
        o_gmii_tx_er                = platform.request("gmii_tx_er"),
        
        # Status
        o_tx_error_underflow        = platform.request("tx_error_underflow"),                 
        o_tx_fifo_overflow          = platform.request("tx_fifo_overflow"),             
        o_tx_fifo_bad_frame         = platform.request("tx_fifo_bad_frame"),             
        o_tx_fifo_good_frame        = platform.request("tx_fifo_good_frame"),                 
        o_rx_error_bad_frame        = platform.request("rx_error_bad_frame"),                 
        o_rx_error_bad_fcs          = platform.request("rx_error_bad_fcs"),             
        o_rx_fifo_overflow          = platform.request("rx_fifo_overflow"),             
        o_rx_fifo_bad_frame         = platform.request("rx_fifo_bad_frame"),             
        o_rx_fifo_good_frame        = platform.request("rx_fifo_good_frame"),                 
        o_speed                     = platform.request("speed"), 
        
        # Configuration
        i_cfg_ifg                   = platform.request("cfg_ifg"), 
        i_cfg_tx_enable             = platform.request("cfg_tx_enable"),     
        i_cfg_rx_enable             = platform.request("cfg_rx_enable")  
    )
    
#################################################################################
# 1G_GMII
#################################################################################
def _1G_GMII(self, platform):
    platform.add_extension(Clocking())
    platform.add_extension(GMII_Interface())
    platform.add_extension(AXI_Stream())
    platform.add_extension(Configuration())
    platform.add_extension(Status())
    
    self.specials += Instance("eth_mac_1g_gmii", 
                        name= "eth_mac_1g_gmii_inst",
        # Ports
        # -----
        # Clocking
        i_gtx_clk               = platform.request("gtx_clk"),
        i_gtx_rst               = platform.request("gtx_rst"),
        o_rx_clk                = platform.request("rx_clk"),
        o_rx_rst                = platform.request("rx_rst"),
        o_tx_clk                = platform.request("tx_clk"),
        o_tx_rst                = platform.request("tx_rst"),
        
        # AXI Input
        i_tx_axis_tdata         = platform.request("tx_axis_tdata"), 
        i_tx_axis_tvalid        = platform.request("tx_axis_tvalid"),     
        o_tx_axis_tready        = platform.request("tx_axis_tready"),     
        i_tx_axis_tlast         = platform.request("tx_axis_tlast"), 
        i_tx_axis_tuser         = platform.request("tx_axis_tuser"), 
        
        # AXI Output
        o_rx_axis_tdata         = platform.request("rx_axis_tdata"),
        o_rx_axis_tvalid        = platform.request("rx_axis_tvalid"),
        o_rx_axis_tlast         = platform.request("rx_axis_tlast"),
        o_rx_axis_tuser         = platform.request("rx_axis_tuser"),
        
        # GMII interface
        i_gmii_rx_clk           = platform.request("gmii_rx_clk"),
        i_gmii_rxd              = platform.request("gmii_rxd"),
        i_gmii_rx_dv            = platform.request("gmii_rx_dv"),
        i_gmii_rx_er            = platform.request("gmii_rx_er"),
        i_mii_tx_clk            = platform.request("mii_tx_clk"),
        o_gmii_tx_clk           = platform.request("gmii_tx_clk"),
        o_gmii_txd              = platform.request("gmii_txd"),
        o_gmii_tx_en            = platform.request("gmii_tx_en"),
        o_gmii_tx_er            = platform.request("gmii_tx_er"),
        
        # Status
        o_tx_error_underflow    = platform.request("tx_error_underflow"),
        o_rx_error_bad_frame    = platform.request("rx_error_bad_frame"),
        o_rx_error_bad_fcs      = platform.request("rx_error_bad_fcs"),
        o_speed                 = platform.request("speed"),
        
        # Configuration
        i_cfg_ifg               = platform.request("cfg_ifg"),
        i_cfg_tx_enable         = platform.request("cfg_tx_enable"),
        i_cfg_rx_enable         = platform.request("cfg_rx_enable")
    )

#################################################################################
# 1G_RGMII_FIFO
#################################################################################
def _1G_RGMII_FIFO(self, platform):
    platform.add_extension(Clocking())
    platform.add_extension(RGMII_Interface())
    platform.add_extension(AXI_Stream())
    platform.add_extension(Configuration())
    platform.add_extension(Status())
    self.specials += Instance("eth_mac_1g_rgmii_fifo", 
                        name= "eth_mac_1g_rgmii_fifo_inst",
        # Ports
        # -----
        # Clocking
        i_gtx_clk                   = platform.request("gtx_clk"),
        i_gtx_clk90                 = platform.request("gtx_clk90"),
        i_gtx_rst                   = platform.request("gtx_rst"),
        i_logic_clk                 = platform.request("logic_clk"),
        i_logic_rst                 = platform.request("logic_rst"),
        
        # AXI input
        i_tx_axis_tdata             = platform.request("tx_axis_tdata"),
        i_tx_axis_tkeep             = platform.request("tx_axis_tkeep"),
        i_tx_axis_tvalid            = platform.request("tx_axis_tvalid"),    
        o_tx_axis_tready            = platform.request("tx_axis_tready"),    
        i_tx_axis_tlast             = platform.request("tx_axis_tlast"),
        i_tx_axis_tuser             = platform.request("tx_axis_tuser"),
        
        # AXI output
        o_rx_axis_tdata             = platform.request("rx_axis_tdata"),
        o_rx_axis_tkeep             = platform.request("rx_axis_tkeep"),
        o_rx_axis_tvalid            = platform.request("rx_axis_tvalid"),    
        i_rx_axis_tready            = platform.request("rx_axis_tready"),    
        o_rx_axis_tlast             = platform.request("rx_axis_tlast"),
        o_rx_axis_tuser             = platform.request("rx_axis_tuser"),
        
        # RGMII Interface
        i_rgmii_rx_clk              = platform.request("rgmii_rx_clk"),
        i_rgmii_rxd                 = platform.request("rgmii_rxd"),
        i_rgmii_rx_ctl              = platform.request("rgmii_rx_ctl"),
        o_rgmii_tx_clk              = platform.request("rgmii_tx_clk"),
        o_rgmii_txd                 = platform.request("rgmii_txd"),
        o_rgmii_tx_ctl              = platform.request("rgmii_tx_ctl"),
        
        # Status
        o_tx_error_underflow        = platform.request("tx_error_underflow"),                 
        o_tx_fifo_overflow          = platform.request("tx_fifo_overflow"),             
        o_tx_fifo_bad_frame         = platform.request("tx_fifo_bad_frame"),             
        o_tx_fifo_good_frame        = platform.request("tx_fifo_good_frame"),                 
        o_rx_error_bad_frame        = platform.request("rx_error_bad_frame"),                 
        o_rx_error_bad_fcs          = platform.request("rx_error_bad_fcs"),             
        o_rx_fifo_overflow          = platform.request("rx_fifo_overflow"),             
        o_rx_fifo_bad_frame         = platform.request("rx_fifo_bad_frame"),             
        o_rx_fifo_good_frame        = platform.request("rx_fifo_good_frame"),                 
        o_speed                     = platform.request("speed"), 
        
        # Configuration
        i_cfg_ifg                   = platform.request("cfg_ifg"),
        i_cfg_tx_enable             = platform.request("cfg_tx_enable"),
        i_cfg_rx_enable             = platform.request("cfg_rx_enable")
    )

#################################################################################
# 1G_RGMII
#################################################################################
def _1G_RGMII(self, platform):
    platform.add_extension(Clocking())
    platform.add_extension(RGMII_Interface())
    platform.add_extension(AXI_Stream())
    platform.add_extension(Configuration())
    platform.add_extension(Status())
    self.specials += Instance("eth_mac_1g_rgmii", 
                        name= "eth_mac_1g_rgmii_inst",
        # Ports
        # -----
        # Clocking
        i_gtx_clk               = platform.request("gtx_clk"),
        i_gtx_clk90             = platform.request("gtx_clk90"),
        i_gtx_rst               = platform.request("gtx_rst"),
        o_rx_clk                = platform.request("rx_clk"),
        o_rx_rst                = platform.request("rx_rst"),
        o_tx_clk                = platform.request("tx_clk"),
        o_tx_rst                = platform.request("tx_rst"),
        
        # AXI Input
        i_tx_axis_tdata         = platform.request("tx_axis_tdata"), 
        i_tx_axis_tvalid        = platform.request("tx_axis_tvalid"),     
        o_tx_axis_tready        = platform.request("tx_axis_tready"),     
        i_tx_axis_tlast         = platform.request("tx_axis_tlast"), 
        i_tx_axis_tuser         = platform.request("tx_axis_tuser"), 
        
        # AXI Output
        o_rx_axis_tdata         = platform.request("rx_axis_tdata"),
        o_rx_axis_tvalid        = platform.request("rx_axis_tvalid"),
        o_rx_axis_tlast         = platform.request("rx_axis_tlast"),
        o_rx_axis_tuser         = platform.request("rx_axis_tuser"),
        
        # RGMII Interface
        i_rgmii_rx_clk          = platform.request("rgmii_rx_clk"),
        i_rgmii_rxd             = platform.request("rgmii_rxd"),
        i_rgmii_rx_ctl          = platform.request("rgmii_rx_ctl"),
        o_rgmii_tx_clk          = platform.request("rgmii_tx_clk"),
        o_rgmii_txd             = platform.request("rgmii_txd"),
        o_rgmii_tx_ctl          = platform.request("rgmii_tx_ctl"),
        
        # Status
        o_tx_error_underflow    = platform.request("tx_error_underflow"),
        o_rx_error_bad_frame    = platform.request("rx_error_bad_frame"),
        o_rx_error_bad_fcs      = platform.request("rx_error_bad_fcs"),
        o_speed                 = platform.request("speed"),
        
        # Configuration
        i_cfg_ifg               = platform.request("cfg_ifg"),
        i_cfg_tx_enable         = platform.request("cfg_tx_enable"),
        i_cfg_rx_enable         = platform.request("cfg_rx_enable")
    )

# Ethernet_MAC ----------------------------------------------------------------------------------
class Ethernet_MAC(Module):
    def __init__(self, platform, interface, data_rate, fifo):
        # Clocking ---------------------------------------------------------------------------------
        self.clock_domains.cd_sys  = ClockDomain()
        
        # 1G GMII ---------------------------------------------------------------------------------
        if (interface == "GMII" and data_rate == "1G"):
            if (fifo == True):
                _1G_GMII_FIFO(self, platform)
            elif (fifo == False):
                _1G_GMII(self, platform)
        
        # 10G GMII ---------------------------------------------------------------------------------
        # elif (interface == "GMII" and data_rate == "10G"):
        #     if (fifo == True):
        #         _10G_GMII_FIFO(self, platform)
        #     elif (fifo == False):
        #         _10G_GMII(self, platform)
        
        # 1G RGMII ---------------------------------------------------------------------------------
        elif (interface == "RGMII" and data_rate == "1G"):
            if (fifo == True):
                _1G_RGMII_FIFO(self, platform)
            elif (fifo == False):
                _1G_RGMII(self, platform)
            
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="ETHERNET_MAC")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="virgo", ip_name="ethernet_mac", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core string value parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--interface",     type=str,   default="GMII",      choices=["GMII", "RGMII"],           help="Physical Interface of Ethernet Mac")
    core_string_param_group.add_argument("--data_rate",     type=str,   default="1G",        choices=["1G", "10G"],               help="Data Rate of Ethernet")
    # core_string_param_group.add_argument("--fifo",          type=str,   default="FALSE",     choices=["TRUE", "FALSE"],           help="Ethernet Mac with/without FIFO")
    
    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--fifo",        type=bool,     default=False,      help="Ethernet Mac with/without FIFO")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",       help="Build Core")
    build_group.add_argument("--build-dir",     default="./",              help="Build Directory")
    build_group.add_argument("--build-name",    default="ethernet_mac",    help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                      help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",       help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name'          : 'ETHERNET_MAC',
    'Version'       : 'V1_0',
    'Interface'     : 'AXI-Stream',
    'Description'   : 'ETHERNET_MAC.'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        
    summary =  { 
    "Physical Interface": args.interface
    }
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="virgo")
    module   = Ethernet_MAC(platform,
        interface       = args.interface,
        data_rate       = args.data_rate,
        fifo            = args.fifo
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "ethernet_mac", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"EMAC\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(\n".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
