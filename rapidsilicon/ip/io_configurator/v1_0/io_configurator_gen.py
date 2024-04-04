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

from litex_wrapper.io_configurator_litex_wrapper import IO_CONFIG

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_ibuf_ios():
    return [
        ("I",    0, Pins(1)),
        ("EN",   0, Pins(1)),
        ("O",    0, Pins(1)),
        ("I_P",  0, Pins(1)),
        ("I_N",  0, Pins(1))
    ]

def get_obuf_ios():
    return [
        ("I",    0, Pins(1)),
        ("O",    0, Pins(1)),
        ("O_P",  0, Pins(1)),
        ("O_N",  0, Pins(1)),
        ("T",    0, Pins(1))
    ]

def get_idelay_ios():
    return [
        ("I",               0, Pins(1)),
        ("DLY_LOAD",        0, Pins(1)),
        ("DLY_ADJ",         0, Pins(1)),
        ("DLY_INCDEC",      0, Pins(1)),
        ("DLY_TAP_VALUE",   0, Pins(6)),
        ("CLK_IN",          0, Pins(1)),
        ("O",               0, Pins(1)),
    ]

def get_clkbuf_ios():
    return [
        ("I",   0, Pins(1)),
        ("O",   0, Pins(1))
    ]
    
def get_iserdes_ios(width):
    return [
        ("D",           0, Pins(1)),
        ("RX_RST",      0, Pins(1)),
        ("BITSLIP_ADJ", 0, Pins(1)),
        ("EN",          0, Pins(1)),
        ("CLK_IN",      0, Pins(1)),
        ("CLK_OUT",     0, Pins(1)),
        ("Q",           0, Pins(width)),
        ("DATA_VALID",  0, Pins(1)),
        ("DPA_LOCK",    0, Pins(1)),
        ("DPA_ERROR",   0, Pins(1)),
        ("PLL_LOCK",    0, Pins(1)),
        ("PLL_CLK",     0, Pins(1))
    ]

def get_oserdes_ios(width):
    return [
        ("D",                       0, Pins(width)),
        ("RST",                     0, Pins(1)),
        ("LOAD_WORD",               0, Pins(1)),
        ("CLK_IN",                  0, Pins(1)),
        ("OE_IN",                   0, Pins(1)),
        ("OE_OUT",                  0, Pins(1)),
        ("Q",                       0, Pins(1)),
        ("CHANNEL_BOND_SYNC_IN",    0, Pins(1)),
        ("CHANNEL_BOND_SYNC_OUT",   0, Pins(1)),
        ("PLL_LOCK",                0, Pins(1)),
        ("PLL_CLK",                 0, Pins(1))
    ]

# IO Configurator Wrapper ----------------------------------------------------------------------------------
class IO_CONFIG_Wrapper(Module):
    def __init__(self, platform, io_model, io_type, config, voltage_standard, delay, data_rate, dpa_mode, width):
        # Clocking ---------------------------------------------------------------------------------
        self.clock_domains.cd_sys  = ClockDomain()
        
        self.submodules.io = io_config = IO_CONFIG(platform, io_model, io_type, config, delay, data_rate, dpa_mode, width)
        
        #################################################################################
        # I_BUF
        #################################################################################
        if (io_model == "I_BUF"):
            platform.add_extension(get_ibuf_ios())
            if (io_type == "Single_Ended"):
                self.comb += io_config.i.eq(platform.request("I"))
                self.comb += io_config.en.eq(platform.request("EN"))
                self.comb += platform.request("O").eq(io_config.o)
            elif (io_type == "Differential"):
                self.comb += io_config.i_p.eq(platform.request("I_P"))
                self.comb += io_config.i_n.eq(platform.request("I_N"))
                self.comb += io_config.en.eq(platform.request("EN"))
                self.comb += platform.request("O").eq(io_config.o)
        
        #################################################################################
        # O_BUF
        #################################################################################
        elif (io_model == "O_BUF"):
            platform.add_extension(get_obuf_ios())
            if (io_type == "Single_Ended"):
                self.comb += io_config.i.eq(platform.request("I"))
                self.comb += platform.request("O").eq(io_config.o)
            elif (io_type == "Differential"):
                self.comb += io_config.i.eq(platform.request("I"))
                self.comb += platform.request("O_P").eq(io_config.o_p)
                self.comb += platform.request("O_N").eq(io_config.o_n)
            elif (io_type == "Tri-State"):
                self.comb += io_config.i.eq(platform.request("I"))
                self.comb += io_config.t.eq(platform.request("T"))
                self.comb += platform.request("O").eq(io_config.o)
            elif (io_type == "Differential-Tri-State"):
                self.comb += io_config.i.eq(platform.request("I"))
                self.comb += io_config.t.eq(platform.request("T"))
                self.comb += platform.request("O_P").eq(io_config.o_p)
                self.comb += platform.request("O_N").eq(io_config.o_n)
            
        #################################################################################
        # I_DELAY
        #################################################################################
        elif (io_model == "I_DELAY"):
            platform.add_extension(get_idelay_ios())
            self.comb += io_config.i.eq(platform.request("I"))
            self.comb += io_config.dly_load.eq(platform.request("DLY_LOAD"))
            self.comb += io_config.dly_adj.eq(platform.request("DLY_ADJ"))
            self.comb += io_config.dly_incdec.eq(platform.request("DLY_INCDEC"))
            self.comb += io_config.clk_in.eq(platform.request("CLK_IN"))
            self.comb += platform.request("DLY_TAP_VALUE").eq(io_config.dly_tap_value)
            self.comb += platform.request("O").eq(io_config.o)
        
        #################################################################################
        # CLK_BUF
        #################################################################################
        elif (io_model == "CLK_BUF"):
            platform.add_extension(get_clkbuf_ios())
            self.comb += io_config.i.eq(platform.request("I"))
            self.comb += platform.request("O").eq(io_config.o)
            
        #################################################################################
        # I_SERDES
        #################################################################################
        elif (io_model == "I_SERDES"):
            platform.add_extension(get_iserdes_ios(width))
            self.comb += io_config.d.eq(platform.request("D"))
            self.comb += io_config.rx_rst.eq(platform.request("RX_RST"))
            self.comb += io_config.bitslip_adj.eq(platform.request("BITSLIP_ADJ"))
            self.comb += io_config.en.eq(platform.request("EN"))
            self.comb += io_config.clk_in.eq(platform.request("CLK_IN"))
            self.comb += io_config.pll_lock.eq(platform.request("PLL_LOCK"))
            self.comb += io_config.pll_clk.eq(platform.request("PLL_CLK"))
            self.comb += platform.request("CLK_OUT").eq(io_config.clk_out)
            self.comb += platform.request("Q").eq(io_config.q)
            self.comb += platform.request("DATA_VALID").eq(io_config.data_valid)
            self.comb += platform.request("DPA_LOCK").eq(io_config.dpa_lock)
            self.comb += platform.request("DPA_ERROR").eq(io_config.dpa_error)
        
        #################################################################################
        # O_SERDES
        #################################################################################
        elif (io_model == "O_SERDES"):
            platform.add_extension(get_oserdes_ios(width))
            self.comb += io_config.d.eq(platform.request("D"))
            self.comb += io_config.rst.eq(platform.request("RST"))
            self.comb += io_config.load_word.eq(platform.request("LOAD_WORD"))
            self.comb += io_config.clk_in.eq(platform.request("CLK_IN"))
            self.comb += io_config.oe_in.eq(platform.request("OE_IN"))
            self.comb += io_config.channel_bond_sync_in.eq(platform.request("CHANNEL_BOND_SYNC_IN"))
            self.comb += io_config.pll_lock.eq(platform.request("PLL_LOCK"))
            self.comb += io_config.pll_clk.eq(platform.request("PLL_CLK"))
            self.comb += platform.request("OE_OUT").eq(io_config.oe_out)
            self.comb += platform.request("Q").eq(io_config.q)
            self.comb += platform.request("CHANNEL_BOND_SYNC_OUT").eq(io_config.channel_bond_sync_out)
            

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="IO_CONFIGURATOR")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="io_configurator", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core string value parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--io_model",          type=str,   default="I_BUF",        choices=["I_BUF", "O_BUF", "CLK_BUF", "I_DELAY", "I_SERDES", "O_SERDES"],           help="Type of Model")
    core_string_param_group.add_argument("--io_type",           type=str,   default="Single_Ended", choices=["Single_Ended", "Differential", "Tri-State", "Differential-Tri-State"],    help="Type of IO")
    core_string_param_group.add_argument("--config",            type=str,   default="NONE",         choices=["NONE", "PULLUP", "PULLDOWN"],                                             help="Configuration of Resistor")
    core_string_param_group.add_argument("--voltage_standard",  type=str,   default="LVCMOS",       choices=["LVCMOS", "LVTTL"],                                                        help="IO Voltage Standards")
    core_string_param_group.add_argument("--data_rate",         type=str,   default="SDR",          choices=["SDR", "DDR"],                                                             help="Single or Double Data Rate (SDR/DDR)")
    core_string_param_group.add_argument("--dpa_mode",          type=str,   default="NONE",         choices=["NONE", "DPA", "CDR"],                                                     help="Dynamic Phase Alignment or Clock Data Recovery")
    
    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--delay",    type=int,   default=0,         choices=range(0,64),         help="Tap Delay Value")
    core_range_param_group.add_argument("--width",    type=int,   default=4,         choices=range(3,11),         help="Width of Serialization/Deserialization")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="io_configurator",              help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name'          : 'IO_CONFIGURATOR',
    'Version'       : 'V1_0',
    'Interface'     : 'Native',
    'Description'   : 'IO_Config'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        
        if (args.io_model == "I_BUF"):
            parser._actions[2].choices = ["Single_Ended", "Differential"]
            
        if (args.io_type in ["Single_Ended", "Differential"]):
            option_strings_to_remove = ['--config']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        # if (args.io_model == "O_BUF"):
            
        #     parser._actions[2].choices = ["Single_Ended", "Differential", "Tri-State", "Differential-Tri-State"]
            
        #     if (args.io_type == "Single_Ended", "Differential"):
        #         option_strings_to_remove = ['--config']
        #         parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
    summary =  { 
    "IO_MODEL": args.io_model,
    "IO_TYPE": args.io_type
    }
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = IO_CONFIG_Wrapper(platform,
        io_model            = args.io_model,
        io_type             = args.io_type,
        config              = args.config,
        voltage_standard    = args.voltage_standard,
        delay               = args.delay,
        data_rate           = args.data_rate,
        dpa_mode            = args.dpa_mode,
        width               = args.width
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "io_configurator", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"IO\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(\n".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()
