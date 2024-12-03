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

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform


# IOs/Interfaces -----------------------------------------------------------------------------------
def clock_ios():
    return [
        ("IOPAD_CLK",           0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",   0, Pins(1))
    ]
    
def dly_ios(num_dly):
    if (num_dly > 1):
        sel_dly = math.ceil(math.log2(num_dly))
    else:
        sel_dly = 1
    return [
        ("FABRIC_RST",          0, Pins(1)),
        ("SEL_DLY",             0, Pins(sel_dly)),
        ("FABRIC_DLY_LOAD",     0, Pins(num_dly)),
        ("FABRIC_DLY_ADJ",      0, Pins(num_dly)),
        ("FABRIC_DLY_INCDEC",   0, Pins(num_dly)),
    ] + [
        (f"FABRIC_DLY_TAP_VALUE_{i}", i, Pins(6)) for i in range(num_dly)
    ]

def get_ibuf_ios():
    return [
        ("IOPAD_I",     0, Pins(1)),
        ("FABRIC_EN",   0, Pins(1)),
        ("FABRIC_O",    0, Pins(1)),
        ("IOPAD_I_P",   0, Pins(1)),
        ("IOPAD_I_N",   0, Pins(1))
    ]

def get_obuf_ios():
    return [
        ("FABRIC_I",    0, Pins(1)),
        ("IOPAD_O",     0, Pins(1)),
        ("IOPAD_O_P",   0, Pins(1)),
        ("IOPAD_O_N",   0, Pins(1)),
        ("FABRIC_T",    0, Pins(1))
    ]

def get_idelay_ios(num_idly):
    if (num_idly > 1):
        sel_dly = math.ceil(math.log2(num_idly))
    else:
        sel_dly = 1
        
    return [
        ("FABRIC_RST",             0, Pins(1)),
        ("SEL_DLY",                0, Pins(sel_dly)),
        ("IOPAD_DATA_IN",          0, Pins(num_idly*1)),
        ("IOPAD_DATA_IN_P",        0, Pins(num_idly*1)),
        ("IOPAD_DATA_IN_N",        0, Pins(num_idly*1)),
        ("FABRIC_DLY_LOAD",        0, Pins(num_idly)),
        ("FABRIC_DLY_ADJ",         0, Pins(num_idly)),
        ("FABRIC_DLY_INCDEC",      0, Pins(num_idly)),
        ("FABRIC_DLY_TAP_VALUE",   0, Pins(6)),
        ("FABRIC_CLK_IN",          0, Pins(1)),
        ("FABRIC_DATA_OUT",        0, Pins(num_idly*1)),
        ("IOPAD_CLK",              0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",      0, Pins(1)),
    ] + [
        (f"FABRIC_DLY_TAP_VALUE_{i}", i, Pins(6)) for i in range(num_idly)
    ]

def get_clkbuf_ios():
    return [
        ("IOPAD_I",   0, Pins(1)),
        ("FABRIC_O",  0, Pins(1))
    ]
    
def get_iserdes_ios(width, num_idly):
    return [
        ("IOPAD_SDATA",                 0, Pins(num_idly)),
        ("IOPAD_SDATA_P",               0, Pins(num_idly)),
        ("IOPAD_SDATA_N",               0, Pins(num_idly)),
        ("IOPAD_CLK",                   0, Pins(1)),
        ("FABRIC_RX_RST",               0, Pins(1)),
        ("FABRIC_RST",                  0, Pins(1)),
        ("FABRIC_BITSLIP_ADJ",          0, Pins(num_idly)),
        ("FABRIC_EN",                   0, Pins(num_idly)),
        ("FABRIC_CLK_IN",               0, Pins(1)),
        ("FABRIC_CLK_OUT",              0, Pins(num_idly)),
        ("FABRIC_DATA_VALID",           0, Pins(num_idly)),
        ("FABRIC_DPA_LOCK",             0, Pins(num_idly)),
        ("FABRIC_DPA_ERROR",            0, Pins(num_idly)),
        ("IOPAD_PLL_REF_CLK",           0, Pins(1)),
        ("FABRIC_DLY_LOAD",             0, Pins(1)),
        ("FABRIC_DLY_ADJ",              0, Pins(1)),
        ("FABRIC_DLY_INCDEC",           0, Pins(1)),
        ("FABRIC_CLK_IN",               0, Pins(1)),
        ("FABRIC_DLY_TAP_VALUE",        0, Pins(6)),
        ("FABRIC_PDATA_OUT",            0, Pins(width))
    ] + [
        (f"FABRIC_PDATA_{i}", i, Pins(width)) for i in range(num_idly)
    ]

def get_oserdes_ios(num_odly, width):
    return [
        ("IOPAD_CLK",               0, Pins(1)),
        ("FABRIC_PDATA",            0, Pins(width)),
        ("FABRIC_RST",              0, Pins(1)),
        ("FABRIC_DATA_VALID",       0, Pins(num_odly)),
        ("FABRIC_CLK_IN",           0, Pins(1)),
        ("FABRIC_OE_IN",            0, Pins(num_odly)),
        # ("CHANNEL_BOND_SYNC_IN",    0, Pins(1)),
        # ("CHANNEL_BOND_SYNC_OUT",   0, Pins(1)),
        ("IOPAD_SDATA",             0, Pins(num_odly)),
        ("IOPAD_SDATA_P",           0, Pins(num_odly)),
        ("IOPAD_SDATA_N",           0, Pins(num_odly)),
        ("IOPAD_CLK_OUT",           0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",       0, Pins(1)),
        ("LO_CLK",                  0, Pins(1)),
        
        ("FABRIC_DLY_LOAD",        0, Pins(1)),
        ("FABRIC_DLY_ADJ",         0, Pins(1)),
        ("FABRIC_DLY_INCDEC",      0, Pins(1)),
        # ("FABRIC_DLY_TAP_VALUE",   0, Pins(6))
    ] + [
        (f"FABRIC_PDATA_{i}", i, Pins(width)) for i in range(num_odly)
    ]
    
def get_iddr_ios(num_idly):
    return [
        ("IOPAD_SDIN",          0, Pins(num_idly)),
        ("IOPAD_SDIN_P",        0, Pins(num_idly)),
        ("IOPAD_SDIN_N",        0, Pins(num_idly)),
        ("FABRIC_RST",          0, Pins(1)),
        ("FABRIC_EN",           0, Pins(num_idly)),
        ("FABRIC_DD_OUT",       0, Pins(2)),
        ("IOPAD_CLK",           0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",   0, Pins(1))
    ] + [
        (f"FABRIC_DD_OUT_{i}", i, Pins(2)) for i in range(num_idly)
    ]

def get_odelay_ios(num_odly):
    if (num_odly > 1):
        sel_dly = math.ceil(math.log2(num_odly))
    else:
        sel_dly = 1
    return [
        ("FABRIC_RST",             0, Pins(1)),
        ("SEL_DLY",                0, Pins(sel_dly)),
        # ("FABRIC_PDATA",           0, Pins(num_odly)),
        ("FABRIC_DLY_LOAD",        0, Pins(num_odly)),
        ("FABRIC_DLY_ADJ",         0, Pins(num_odly)),
        ("FABRIC_DLY_INCDEC",      0, Pins(num_odly)),
        ("FABRIC_DLY_TAP_VALUE",   0, Pins(6)),
        ("FABRIC_CLK_IN",          0, Pins(1)),
        ("FABRIC_DATA_IN",         0, Pins(num_odly)),
        ("IOPAD_DATA_OUT",         0, Pins(num_odly)),
        ("IOPAD_DATA_OUT_P",       0, Pins(num_odly)),
        ("IOPAD_DATA_OUT_N",       0, Pins(num_odly)),
        ("IOPAD_CLK",              0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",      0, Pins(1))
    ] + [
        (f"FABRIC_DLY_TAP_VALUE_{i}", i, Pins(6)) for i in range(num_odly)
    ]

def get_oddr_ios(num_odly):
    return [
        ("FABRIC_DD_IN",        0, Pins(2)),
        ("FABRIC_RST",          0, Pins(1)),
        ("FABRIC_EN",           0, Pins(num_odly)),
        ("IOPAD_SD_OUT",        0, Pins(num_odly)),
        ("IOPAD_SD_OUT_P",      0, Pins(num_odly)),
        ("IOPAD_SD_OUT_N",      0, Pins(num_odly)),
        ("IOPAD_CLK",           0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",   0, Pins(1))
    ] + [
        (f"FABRIC_DD_IN_{i}",i,  Pins(2)) for i in range(num_odly)
    ]

def bidirectional_ios(num_dly, width):
    return [
        # idelay
        ("IOPAD_DIN",           0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_DIN_P",         0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_DIN_N",         0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_DOUT",         0, Pins(math.ceil(num_dly/2))),
        #iserdes
        ("IOPAD_SDATA_IN",      0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SDATA_IN_P",    0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SDATA_IN_N",    0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_EN",           0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_BITSLIP_ADJ",  0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_DATA_VALID",   0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_DPA_LOCK",     0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_DPA_ERROR",    0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_CLK_OUT",      0, Pins(math.ceil(num_dly/2))),
        #iddr
        ("IOPAD_SD_IN",           0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SD_IN_P",         0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SD_IN_N",         0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_EN_IDDR",        0, Pins(math.ceil(num_dly/2))),
        # odelay
        ("FABRIC_DIN",          0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_DOUT",          0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_DOUT_P",        0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_DOUT_N",        0, Pins(math.ceil(num_dly/2))),
        # oserdes
        ("FABRIC_DATA_VALID",   0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_CLK_IN",       0, Pins(math.ceil(num_dly/2))),
        ("FABRIC_OE_IN",        0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SDATA_OUT",     0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SDATA_OUT_P",   0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SDATA_OUT_N",   0, Pins(math.ceil(num_dly/2))),
        #oddr
        ("FABRIC_EN_ODDR",      0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SD_OUT",        0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SD_OUT_P",      0, Pins(math.ceil(num_dly/2))),
        ("IOPAD_SD_OUT_N",      0, Pins(math.ceil(num_dly/2))),
    ] + [
        (f"FABRIC_PDATA_IN_{i}",    i, Pins(width)) for i in range(math.ceil(num_dly/2))
    ] + [
        (f"FABRIC_PDATA_OUT_{i}",   i, Pins(width)) for i in range(math.ceil(num_dly/2))
    ]+ [
        (f"FABRIC_DD_IN_{i}",       i, Pins(2)) for i in range(math.ceil(num_dly/2))
    ] + [
        (f"FABRIC_DD_OUT_{i}",      i, Pins(2)) for i in range(math.ceil(num_dly/2))
    ] 

def freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source):
    if clocking_source == "LOCAL_OSCILLATOR":
        b = 40
    else:
        b = ref_clk_freq
        
    a = out_clk_freq
    c_range = 1000
    d_range = 63
    # Nested loop for iterating over c and d
    for c in range(c_range):
        for d in range(d_range):
            # Calculate 2 * (a / b)
            product_candidate = (a / b)
            # Check if the candidate product matches the formula with c and d
            if product_candidate == ((c+1) / (d+1)):
                # If a match is found, assign c, d, and the product to the respective signals
                pll_mult = c + 1
                pll_div  = d + 1
                return pll_mult, pll_div

def ports_file_read(ports_file, bank_select, num_dly, io_type):
    if (ports_file == ""):
        return 0
    else:
        ports       = []
        bits_high   = 0
        
        if (io_type == "SINGLE_ENDED"):
            # Open the text file in read mode
            with open(ports_file, 'r') as file:
                for _ in range(num_dly):
                    line = file.readline()
                    if not line:
                        break
                    ports.append(line.strip())
            
            single_ended_ports = []
            single_ended_ports = [int(_.split("_")[2]) for _ in ports]
            single_ended_ports = sorted(single_ended_ports)
            for bit in single_ended_ports:
                bits_high |= (1 << bit) # making bits high depending upon bit number
            binary_dly_loc = bin(bits_high)[2:] # removing 0b from binary string
            
        elif (io_type == "DIFFERENTIAL"):
            # Open the text file in read mode
            with open(ports_file, 'r') as file:
                for _ in range(2*num_dly):
                    line = file.readline()
                    if not line:
                        break
                    ports.append(line.strip())
            # Loop through each port and extract the numeric part before the last letter
            for port in ports:
                last_part = port.split('_')[-1]  # Split by underscore and take the last part (e.g., "0P")
                number_part = int(last_part[:-1])      # Remove the last character (e.g., "P", "N") to get the number
                bits_high |= (1 << (2*number_part))  # Set the bit at position 'numx2' to 1
            binary_dly_loc =  bin(bits_high)[2:]
        
        bank_sel = [(bank[:4]) for bank in ports]
        for bank in bank_sel:
            if (bank != bank_select):
                print("Error: Invalid Bank Selected")
                return 0

        if (len(binary_dly_loc) < 40):
            binary_dly_loc = binary_dly_loc.zfill(40) # appending zeros to remaining bits on MSB
        else:
            binary_dly_loc = binary_dly_loc
            
        dly_loc = binary_dly_loc
        return dly_loc

#################################################################################
# I_BUF
#################################################################################
def I_BUF(self, platform, io_type, io_mode, voltage_standard, diff_termination):
    platform.add_extension(get_ibuf_ios())
    if (io_type == "SINGLE_ENDED"):
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF",
            # Parameters.
            # -----------
            p_WEAK_KEEPER = io_mode,
            p_IOSTANDARD  = voltage_standard,
            # Ports
            #------
            i_I     = platform.request("IOPAD_I"),
            i_EN    = platform.request("FABRIC_EN"),
            o_O     = platform.request("FABRIC_O")
        )
        
    elif (io_type == "DIFFERENTIAL"):
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF_DS",
            # Parameters.
            # -----------
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            # Ports
            #------
            i_I_P   = platform.request("IOPAD_I_P"),
            i_I_N   = platform.request("IOPAD_I_N"),
            i_EN    = platform.request("FABRIC_EN"),
            o_O     = platform.request("FABRIC_O")
        )

#################################################################################
# O_BUF
#################################################################################
def O_BUF(self, platform, io_type, io_mode, voltage_standard, diff_termination, slew_rate, drive_strength):
    platform.add_extension(get_obuf_ios())
    if (io_type == "SINGLE_ENDED"):
        # Module instance.
        # ----------------
        self.specials += Instance("O_BUF",
            # Parameters.
            # -----------
            p_IOSTANDARD                = voltage_standard,
            p_DRIVE_STRENGTH            = drive_strength,
            p_SLEW_RATE                 = slew_rate,
            # Ports
            #------
            i_I     = platform.request("FABRIC_I"),
            o_O     = platform.request("IOPAD_O")
        )
        
    elif (io_type == "DIFFERENTIAL"):
        # Module instance.
        # ----------------
        self.specials += Instance("O_BUF_DS",
            # Parameters.
            # -----------
            p_IOSTANDARD                = voltage_standard,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            # Ports
            #------
            i_I         = platform.request("FABRIC_I"),
            o_O_P       = platform.request("IOPAD_O_P"),
            o_O_N       = platform.request("IOPAD_O_N")
        )
        
    elif (io_type == "TRI_STATE"):
        # Module instance.
        # ----------------
        self.specials += Instance("O_BUFT",
            # Parameters.
            # -----------
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DRIVE_STRENGTH            = drive_strength,
            p_SLEW_RATE                 = slew_rate,
            # Ports
            #------
            i_I         = platform.request("FABRIC_I"),
            i_T         = platform.request("FABRIC_T"),
            o_O         = platform.request("IOPAD_O")
        )
        
    elif (io_type == "DIFF_TRI_STATE"):
        # Module instance.
        # ----------------
        self.specials += Instance("O_BUFT_DS",
            # Parameters.
            # -----------
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            # Ports
            #------
            i_I         = platform.request("FABRIC_I"),
            i_T         = platform.request("FABRIC_T"),
            o_O_P       = platform.request("IOPAD_O_P"),
            o_O_N       = platform.request("IOPAD_O_N")
        )

#################################################################################
# CLK_BUF
#################################################################################
def CLK_BUF(self, platform, io_mode):
    platform.add_extension(get_clkbuf_ios())
    self.i = Signal(1)
    # Module instance.
    # ----------------
    self.specials += Instance("I_BUF",
        # Parameters.
        # -----------
        p_WEAK_KEEPER = io_mode,
        # Ports
        #------
        i_I     = platform.request("IOPAD_I"),
        i_EN    = 1,
        o_O     = self.i
    )
    # Module instance.
    # ----------------
    self.specials += Instance("CLK_BUF",
        # Ports
        #------
        i_I     = self.i,
        o_O     = platform.request("FABRIC_O")
    )

#################################################################################
# I_DELAY
#################################################################################
def I_DELAY(self, platform, sel_dly, io_model, combination, io_mode, voltage_standard, op_mode, data_rate, delay, delay_type, clocking, clocking_source, ref_clk_freq, out_clk_freq, num_idly, ports_file, width, bank_select, io_type, diff_termination):
    platform.add_extension(get_idelay_ios(num_idly))
    ADDR_WIDTH  = 6
    
    if (clocking == "PLL"):
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
    else:
        pll_mult = 16
        pll_div  = 1
        
    if (io_type == "DIFFERENTIAL"):
        diff_termination = diff_termination
    else:
        diff_termination = "FALSE"
        
    if (combination == "I_DELAY"): 
        dly_loc = ports_file_read(ports_file, bank_select, num_idly, io_type)
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_DATA_IN")
            data_in     = iopad_i  
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p     = platform.request("IOPAD_DATA_IN_P")
            iopad_i_n     = platform.request("IOPAD_DATA_IN_N")
            data_in       = Cat(iopad_i_p, iopad_i_n)
            
        fabric_o    = platform.request("FABRIC_DATA_OUT")
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
                # Parameters.
                # -----------
                p_IO_MODEL                  = combination,
                p_DELAY                     = delay,
                p_WEAK_KEEPER               = io_mode,
                p_IOSTANDARD                = voltage_standard,
                p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
                p_NUM_DLY                   = num_idly,
                p_DELAY_TYPE                = delay_type,
                p_PLL_MULT                  = pll_mult,
                p_PLL_DIV                   = pll_div,
                p_DIFFERENTIAL_TERMINATION  = diff_termination,
                p_IO_TYPE                   = io_type,
                p_DLY_SEL_WIDTH             = sel_dly,
                # Ports
                #------
                i_DATA_IN                   = data_in,
                i_RESET                     = platform.request("FABRIC_RST"),
                i_SEL_DLY                   = platform.request("SEL_DLY"),
                i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
                i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
                i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
                o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_idly)]),
                o_DATA_OUT                  = fabric_o
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                  = combination,
            p_DELAY                     = delay,
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                   = num_idly,
            p_DELAY_TYPE                = delay_type,
            p_PLL_MULT                  = pll_mult,
            p_PLL_DIV                   = pll_div,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            p_IO_TYPE                   = io_type,
            p_DLY_SEL_WIDTH             = sel_dly,
            # Ports
            #------
            i_DATA_IN                   = data_in,
            i_CLK_IN                    = clk_in,
            i_RESET                     = platform.request("FABRIC_RST"),
            i_SEL_DLY                   = platform.request("SEL_DLY"),
            i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_idly)]),
            o_DATA_OUT                  = fabric_o
        )
        
    elif (combination == "I_DELAY_I_SERDES"):
        platform.add_extension(get_iserdes_ios(width, num_idly))
        dly_loc = ports_file_read(ports_file, bank_select, num_idly, io_type)
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_SDATA")
            sdata_in    = iopad_i
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_SDATA_P")
            iopad_i_n   = platform.request("IOPAD_SDATA_N")
            sdata_in    = Cat(iopad_i_p, iopad_i_n)
        
        # for i in range(num_idly):
        #     self.comb += platform.request(f"FABRIC_PDATA_{i}").eq(pdata_out[(i*width):(i*width)+width])
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
                # Parameters.
                # -----------
                p_IO_MODEL                  = combination,
                p_DELAY                     = delay,
                p_WEAK_KEEPER               = io_mode,
                p_IOSTANDARD                = voltage_standard,
                p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
                p_NUM_DLY                   = num_idly,
                p_DELAY_TYPE                = delay_type,
                p_WIDTH                     = width,
                p_DATA_RATE                 = data_rate,
                p_DPA_MODE                  = op_mode,
                p_PLL_MULT                  = pll_mult,
                p_PLL_DIV                   = pll_div,
                p_DIFFERENTIAL_TERMINATION  = diff_termination,
                p_IO_TYPE                   = io_type,
                p_DLY_SEL_WIDTH             = sel_dly,
                # Ports
                #------
                i_EN                        = platform.request("FABRIC_EN"),
                i_BITSLIP_ADJ               = platform.request("FABRIC_BITSLIP_ADJ"),
                o_CLK_OUT                   = platform.request("FABRIC_CLK_OUT"),
                o_DPA_LOCK                  = platform.request("FABRIC_DPA_LOCK"),
                o_DPA_ERROR                 = platform.request("FABRIC_DPA_ERROR"),
                o_DATA_VALID                = platform.request("FABRIC_DATA_VALID"),
                o_PDATA_OUT                 = Cat([platform.request(f"FABRIC_PDATA_{i}") for i in range(num_idly)]),
                i_SDATA_IN                  = sdata_in,
                i_RESET                     = platform.request("FABRIC_RST"),
                i_SEL_DLY                   = platform.request("SEL_DLY"),
                i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
                i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
                i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
                o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_idly)])
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                  = combination,
            p_DELAY                     = delay,
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                   = num_idly,
            p_DELAY_TYPE                = delay_type,
            p_WIDTH                     = width,
            p_DATA_RATE                 = data_rate,
            p_DPA_MODE                  = op_mode,
            p_PLL_MULT                  = pll_mult,
            p_PLL_DIV                   = pll_div,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            p_IO_TYPE                   = io_type,
            p_DLY_SEL_WIDTH             = sel_dly,
            # Ports
            #------
            i_EN                        = platform.request("FABRIC_EN"),
            i_BITSLIP_ADJ               = platform.request("FABRIC_BITSLIP_ADJ"),
            o_CLK_OUT                   = platform.request("FABRIC_CLK_OUT"),
            o_DPA_LOCK                  = platform.request("FABRIC_DPA_LOCK"),
            o_DPA_ERROR                 = platform.request("FABRIC_DPA_ERROR"),
            o_DATA_VALID                = platform.request("FABRIC_DATA_VALID"),
            o_PDATA_OUT                 = Cat([platform.request(f"FABRIC_PDATA_{i}") for i in range(num_idly)]),
            i_SDATA_IN                  = sdata_in,
            i_CLK_IN                    = clk_in,
            i_RESET                     = platform.request("FABRIC_RST"),
            i_SEL_DLY                   = platform.request("SEL_DLY"),
            i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_idly)])
        )
        
        
    elif (combination == "I_DELAY_I_DDR"):
        platform.add_extension(get_iddr_ios(num_idly))
        
        dly_loc = ports_file_read(ports_file, bank_select, num_idly, io_type)
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_SDIN")
            sdin        = iopad_i
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_SDIN_P")
            iopad_i_n   = platform.request("IOPAD_SDIN_N")
            sdin        = Cat(iopad_i_p, iopad_i_n)
            
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
                # Parameters.
                # -----------
                p_IO_MODEL                  = combination,
                p_DELAY                     = delay,
                p_WEAK_KEEPER               = io_mode,
                p_IOSTANDARD                = voltage_standard,
                p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
                p_NUM_DLY                   = num_idly,
                p_DELAY_TYPE                = delay_type,
                p_PLL_MULT                  = pll_mult,
                p_PLL_DIV                   = pll_div,
                p_DIFFERENTIAL_TERMINATION  = diff_termination,
                p_IO_TYPE                   = io_type,
                p_DLY_SEL_WIDTH             = sel_dly,
                # Ports
                #------
                i_EN                        = platform.request("FABRIC_EN"),
                o_DD_OUT                    = Cat([platform.request(f"FABRIC_DD_OUT_{i}") for i in range(num_idly)]),
                i_SD_IN                     = sdin,
                i_RESET                     = platform.request("FABRIC_RST"),
                i_SEL_DLY                   = platform.request("SEL_DLY"),
                i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
                i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
                i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
                o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_idly)])
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            p_IO_MODEL                  = combination,
            # -----------
            p_DELAY                     = delay,
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                   = num_idly,
            p_DELAY_TYPE                = delay_type,
            p_PLL_MULT                  = pll_mult,
            p_PLL_DIV                   = pll_div,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            p_IO_TYPE                   = io_type,
            p_DLY_SEL_WIDTH             = sel_dly,
            # Ports
            #------
            i_CLK_IN                    = clk_in,
            i_EN                        = platform.request("FABRIC_EN"),
            o_DD_OUT                    = Cat([platform.request(f"FABRIC_DD_OUT_{i}") for i in range(num_idly)]),
            i_SD_IN                     = sdin,
            i_RESET                     = platform.request("FABRIC_RST"),
            i_SEL_DLY                   = platform.request("SEL_DLY"),
            i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_idly)])
        )

#################################################################################
# I_DDR
#################################################################################
def I_DDR(self, platform, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq, num_idly):
    platform.add_extension(get_iddr_ios(num_idly))
    self.i      = Signal(1)
    self.clk    = Signal(1)
    self.clk_1  = Signal(1)
    self.clk_2  = Signal(1)
    
    if (clocking == "RX_CLOCK"):
        clock_out = self.clk_2
        clk = platform.request("IOPAD_CLK")
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF",
            # Parameters.
            # -----------
            p_WEAK_KEEPER = io_mode,
            # Ports
            #------
            i_I     = clk,
            i_EN    = 1,
            o_O     = self.clk_1
        )
        
        # Module instance.
        # ----------------
        self.specials += Instance("CLK_BUF",
            # Ports
            #------
            i_I     = self.clk_1,
            o_O     = clock_out
        )
        
    elif (clocking == "PLL"):
        self.lo_clk     = Signal(1)
        self.pll_clk    = Signal(1)
        self.pll_lock   = Signal(1)
        clock_out = self.pll_clk
        
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
        if (clocking_source == "LOCAL_OSCILLATOR"):
            
            # Module instance.
            # ----------------
            self.specials += Instance("BOOT_CLOCK",
                # Parameters.
                # -----------
                o_O     = self.lo_clk
            )
            # Module instance.
            # ----------------
            self.specials += Instance("PLL",
                # Parameters.
                # -----------
                p_DIVIDE_CLK_IN_BY_2    = "FALSE",
                p_PLL_MULT              = pll_mult,
                p_PLL_DIV               = pll_div,
                p_PLL_POST_DIV          = 17,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.lo_clk,
                o_CLK_OUT           = self.pll_clk,          
                o_LOCK              = self.pll_lock
            )
        
        elif (clocking_source == "RX_IO_CLOCK"):
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF", # For Clock
                # Parameters.
                # -----------
                p_WEAK_KEEPER = io_mode,
                # Ports
                #------
                i_I     = platform.request("IOPAD_PLL_REF_CLK"),
                i_EN    = 1,
                o_O     = self.clk
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("CLK_BUF",
                # Ports
                #------
                i_I     = self.clk,
                o_O     = self.clk_1
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("PLL",
                # Parameters.
                # -----------
                p_DIVIDE_CLK_IN_BY_2    = "FALSE",
                p_PLL_MULT              = pll_mult,
                p_PLL_DIV               = pll_div,
                p_PLL_POST_DIV          = 17,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.clk_1,
                o_CLK_OUT           = clock_out,           
                o_LOCK              = self.pll_lock
            )
            
    
    # Module instance.
    # ----------------
    self.specials += Instance("I_BUF",
        # Parameters.
        # -----------
        p_WEAK_KEEPER = io_mode,
        # Ports
        #------
        i_I     = platform.request("IOPAD_SDIN"),
        i_EN    = 1,
        o_O     = self.i
    )
    
    # Module instance.
    # ----------------
    self.specials += Instance("I_DDR",
        # Ports
        #------
        i_D = self.i,
        i_R = platform.request("FABRIC_RST"),
        i_E = platform.request("FABRIC_EN"),
        i_C = clock_out,
        o_Q = platform.request("FABRIC_DD_OUT")
    )

#################################################################################
# I_SERDES
#################################################################################
def I_SERDES(self, platform, data_rate, width, op_mode, io_type, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq, delay, delay_adjust, delay_type, num_idly):
    platform.add_extension(get_iserdes_ios(width, num_idly))
    self.d          = Signal(1)
    self.d_1        = Signal(1)
    self.clk        = Signal(1)
    self.clk_1      = Signal(1)
    self.pll_clk    = Signal(1)
    self.pll_lock   = Signal(1)
    self.lo_clk     = Signal(1)
    self.open       = Signal(6)
    self.open1      = Signal(1)
    self.open2      = Signal(1)
    
    if (op_mode == "DPA"):
        dpa_lock    = platform.request("FABRIC_DPA_LOCK")
        dpa_error   = platform.request("FABRIC_DPA_ERROR")
    else:
        dpa_lock    = self.open1
        dpa_error   = self.open2
    
    # self.comb += self.clk_in.eq("FABRIC_CLK_IN")
    
    # self.comb += self.clk_in.eq(platform.request("FABRIC_CLK_IN"))
    
    
    if (delay_adjust == "TRUE"):
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF", # For Data
            # Parameters.
            # -----------
            p_WEAK_KEEPER = io_mode,
            # Ports
            #------
            i_I     = platform.request("IOPAD_SDATA"),
            i_EN    = 1,
            o_O     = self.d
        )

        if (delay_type == "STATIC"):
            if (clocking == "RX_CLOCK"):
                # Module instance.
                # ----------------
                self.specials += Instance("I_DELAY",
                    # Parameters.
                    # -----------
                    p_DELAY             = delay,
                    # Ports
                    #------
                    i_I                 = self.d,
                    i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                    i_DLY_ADJ           = 0,
                    i_DLY_INCDEC        = 0,
                    i_CLK_IN            = self.clk_1,
                    o_DLY_TAP_VALUE     = self.open,
                    o_O                 = self.d_1
                )
            elif (clocking == "PLL"):
                # Module instance.
                # ----------------
                self.specials += Instance("I_DELAY",
                    # Parameters.
                    # -----------
                    p_DELAY             = delay,
                    # Ports
                    #------
                    i_I                 = self.d,
                    i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                    i_DLY_ADJ           = 0,
                    i_DLY_INCDEC        = 0,
                    i_CLK_IN            = self.pll_clk,
                    o_DLY_TAP_VALUE     = self.open,
                    o_O                 = self.d_1
                )

        elif (delay_type == "DYNAMIC"):
            if (clocking == "RX_CLOCK"):
                # Module instance.
                # ----------------
                self.specials += Instance("I_DELAY",
                    # Parameters.
                    # -----------
                    p_DELAY             = delay,
                    # Ports
                    #------
                    i_I                 = self.d,
                    i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                    i_DLY_ADJ           = platform.request("FABRIC_DLY_ADJ"),
                    i_DLY_INCDEC        = platform.request("FABRIC_DLY_INCDEC"),
                    i_CLK_IN            = self.clk_1,
                    o_DLY_TAP_VALUE     = platform.request("FABRIC_DLY_TAP_VALUE"),
                    o_O                 = self.d_1
                )
            elif (clocking == "PLL"):
                # Module instance.
                # ----------------
                self.specials += Instance("I_DELAY",
                    # Parameters.
                    # -----------
                    p_DELAY             = delay,
                    # Ports
                    #------
                    i_I                 = self.d,
                    i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                    i_DLY_ADJ           = platform.request("FABRIC_DLY_ADJ"),
                    i_DLY_INCDEC        = platform.request("FABRIC_DLY_INCDEC"),
                    i_CLK_IN            = self.pll_clk,
                    o_DLY_TAP_VALUE     = platform.request("FABRIC_DLY_TAP_VALUE"),
                    o_O                 = self.d_1
                )
            
    elif (delay_adjust == "FALSE"):
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF", # For Data
            # Parameters.
            # -----------
            p_WEAK_KEEPER = io_mode,
            # Ports
            #------
            i_I     = platform.request("IOPAD_SDATA"),
            i_EN    = 1,
            o_O     = self.d_1
        )
    
    if clocking == "RX_CLOCK":
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF", # For Clock
            # Parameters.
            # -----------
            p_WEAK_KEEPER = io_mode,
            # Ports
            #------
            i_I     = platform.request("IOPAD_CLK"),
            i_EN    = 1,
            o_O     = self.clk
        )

        # Module instance.
        # ----------------
        self.specials += Instance("CLK_BUF",
            # Ports
            #------
            i_I     = self.clk,
            o_O     = self.clk_1
        )
        # Module instance.
        # ----------------
        self.specials += Instance("I_SERDES",
            # Parameters.
            # -----------
            p_DATA_RATE     = data_rate,
            p_WIDTH         = width,
            p_DPA_MODE      = op_mode,
            # Ports
            #------
            i_D               = self.d_1,
            i_RX_RST          = platform.request("FABRIC_RX_RST"),
            i_BITSLIP_ADJ     = platform.request("FABRIC_BITSLIP_ADJ"),
            i_EN              = platform.request("FABRIC_EN"),
            i_CLK_IN          = platform.request("FABRIC_CLK_IN"),
            o_CLK_OUT         = platform.request("FABRIC_CLK_OUT"),
            o_Q               = platform.request("FABRIC_PDATA_OUT"),
            o_DATA_VALID      = platform.request("FABRIC_DATA_VALID"),
            o_DPA_LOCK        = dpa_lock,
            o_DPA_ERROR       = dpa_error,
            i_PLL_LOCK        = 1,
            i_PLL_CLK         = self.clk_1
        )
    
    elif clocking == "PLL":
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
        if clocking_source == "RX_IO_CLOCK":
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF", # For Clock
                # Parameters.
                # -----------
                p_WEAK_KEEPER = io_mode,
                # Ports
                #------
                i_I     = platform.request("IOPAD_PLL_REF_CLK"),
                i_EN    = 1,
                o_O     = self.clk
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("CLK_BUF",
                # Ports
                #------
                i_I     = self.clk,
                o_O     = self.clk_1
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("PLL",
                # Parameters.
                # -----------
                p_DIVIDE_CLK_IN_BY_2    = "FALSE",
                p_PLL_MULT              = pll_mult,
                p_PLL_DIV               = pll_div,
                p_PLL_POST_DIV          = 17,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.clk_1,
                o_CLK_OUT           = self.pll_clk,           
                o_LOCK              = self.pll_lock
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("I_SERDES",
                # Parameters.
                # -----------
                p_DATA_RATE       = data_rate,
                p_WIDTH           = width,
                p_DPA_MODE        = op_mode,
                # Ports
                #------
                i_D               = self.d_1,
                i_RX_RST          = platform.request("FABRIC_RX_RST"),
                i_BITSLIP_ADJ     = platform.request("FABRIC_BITSLIP_ADJ"),
                i_EN              = platform.request("FABRIC_EN"),
                i_CLK_IN          = platform.request("FABRIC_CLK_IN"),
                o_CLK_OUT         = platform.request("FABRIC_CLK_OUT"),
                o_Q               = platform.request("FABRIC_PDATA_OUT"),
                o_DATA_VALID      = platform.request("FABRIC_DATA_VALID"),
                o_DPA_LOCK        = dpa_lock,
                o_DPA_ERROR       = dpa_error,
                i_PLL_LOCK        = self.pll_lock,
                i_PLL_CLK         = self.pll_clk
            )
            
        elif clocking_source == "LOCAL_OSCILLATOR":
            # Module instance.
            # ----------------
            self.specials += Instance("BOOT_CLOCK",
                # Parameters.
                # -----------
                o_O     = self.lo_clk
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("PLL",
                # Parameters.
                # -----------
                p_DIVIDE_CLK_IN_BY_2    = "FALSE",
                p_PLL_MULT              = pll_mult,
                p_PLL_DIV               = pll_div,
                p_PLL_POST_DIV          = 17,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.lo_clk,
                o_CLK_OUT           = self.pll_clk,          
                o_LOCK              = self.pll_lock
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("I_SERDES",
                # Parameters.
                # -----------
                p_DATA_RATE       = data_rate,
                p_WIDTH           = width,
                p_DPA_MODE        = op_mode,
                # Ports
                #------
                i_D               = self.d_1,
                i_RX_RST          = platform.request("FABRIC_RX_RST"),
                i_BITSLIP_ADJ     = platform.request("FABRIC_BITSLIP_ADJ"),
                i_EN              = platform.request("FABRIC_EN"),
                i_CLK_IN          = platform.request("FABRIC_CLK_IN"),
                o_CLK_OUT         = platform.request("FABRIC_CLK_OUT"),
                o_Q               = platform.request("FABRIC_PDATA_OUT"),
                o_DATA_VALID      = platform.request("FABRIC_DATA_VALID"),
                o_DPA_LOCK        = dpa_lock,
                o_DPA_ERROR       = dpa_error,
                i_PLL_LOCK        = self.pll_lock,
                i_PLL_CLK         = self.pll_clk
            )

#################################################################################
# O_SERDES
#################################################################################
def O_SERDES(self, platform, data_rate, width, clocking, clock_forwarding, clocking_source, ref_clk_freq, out_clk_freq, op_mode, io_mode, voltage_standard, drive_strength, slew_rate, delay, delay_adjust, delay_type, clock_phase, num_odly):
    platform.add_extension(get_oserdes_ios(num_odly, width))
    
    self.q          = Signal(1)
    self.q_1        = Signal(1)
    self.oe_out     = Signal(1)
    self.clk        = Signal(1)
    self.clk_1      = Signal(1)
    self.clk_out    = Signal(1)
    self.pll_clk    = Signal(1)
    self.pll_lock   = Signal(1)
    self.lo_clk     = Signal(1)
    self.open       = Signal(6)
    self.open1      = Signal(1)
    
    if clocking == "RX_CLOCK":
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF", # For Clock
            # Parameters.
            # -----------
            p_WEAK_KEEPER = io_mode,
            # Ports
            #------
            i_I     = platform.request("IOPAD_CLK"),
            i_EN    = 1,
            o_O     = self.clk
        )
        
        # Module instance.
        # ----------------
        self.specials += Instance("CLK_BUF",
            # Ports
            #------
            i_I     = self.clk,
            o_O     = self.clk_1
        )
        if (delay_adjust == "FALSE"):
            # Module instance.
            # ----------------
            self.specials += Instance("O_SERDES",
                # Parameters.
                # -----------
                p_DATA_RATE             = data_rate,
                p_WIDTH                 = width,
                # Ports
                #------
                i_D                     = platform.request("FABRIC_PDATA"),   
                i_RST                   = platform.request("FABRIC_RST"),   
                i_DATA_VALID            = platform.request("FABRIC_DATA_VALID"),         
                i_CLK_IN                = platform.request("FABRIC_CLK_IN"),    
                i_OE_IN                 = platform.request("FABRIC_OE_IN"),
                o_OE_OUT                = self.oe_out,     
                o_Q                     = self.q,
                i_CHANNEL_BOND_SYNC_IN  = 0,        
                o_CHANNEL_BOND_SYNC_OUT = self.open1,
                i_PLL_LOCK              = 1,
                i_PLL_CLK               = self.clk_1
            )
            if (clock_forwarding == "FALSE"):
                # Module instance.
                # ----------------
                self.specials += Instance("O_BUFT",
                    # Ports
                    #------
                    i_I     = self.q,
                    i_T     = self.oe_out,
                    o_O     = platform.request("IOPAD_SDATA")
                )

            elif (clock_forwarding == "TRUE"):
                # Module instance.
                # ----------------
                self.specials += Instance("O_SERDES_CLK",
                    # Parameters
                    #-----------
                    p_DATA_RATE    = data_rate,
                    p_CLOCK_PHASE  = int(clock_phase),
                    # Ports
                    #------
                    i_CLK_EN        = self.oe_out,
                    i_PLL_LOCK      = 1,
                    i_PLL_CLK       = self.clk_1,
                    o_OUTPUT_CLK    = self.clk_out
                )
                # Module instance.
                # ----------------
                self.specials += Instance("O_BUF",
                    # Parameters.
                    # -----------
                    p_IOSTANDARD                = voltage_standard,
                    p_DRIVE_STRENGTH            = drive_strength,
                    p_SLEW_RATE                 = slew_rate,
                    # Ports
                    #------
                    i_I     = self.clk_out,
                    o_O     = platform.request("IOPAD_CLK_OUT")
                )
        
        elif (delay_adjust == "TRUE"):
            
            # self.clk_in = Signal(1)
            # self.comb += self.clk_in.eq(platform.request("FABRIC_CLK_IN"))
            
            # Module instance.
            # ----------------
            self.specials += Instance("O_SERDES",
                # Parameters.
                # -----------
                p_DATA_RATE             = data_rate,
                p_WIDTH                 = width,
                # Ports
                #------
                i_D                     = platform.request("FABRIC_PDATA"),   
                i_RST                   = platform.request("FABRIC_RST"),   
                i_DATA_VALID            = platform.request("FABRIC_DATA_VALID"),         
                i_CLK_IN                = platform.request("FABRIC_CLK_IN"),    
                i_OE_IN                 = platform.request("FABRIC_OE_IN"),
                o_OE_OUT                = self.oe_out,     
                o_Q                     = self.q_1,
                i_CHANNEL_BOND_SYNC_IN  = 0,        
                o_CHANNEL_BOND_SYNC_OUT = self.open1,
                i_PLL_LOCK              = 1,
                i_PLL_CLK               = self.clk_1
            )
            
            if (clock_forwarding == "FALSE"):
                if (delay_type == "STATIC"):
                # Module instance.
                    # ----------------
                    self.specials += Instance("O_DELAY",
                        # Parameters.
                        # -----------
                        p_DELAY             = delay,
                        # Ports
                        #------
                        i_I                 = self.q_1,
                        i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                        i_DLY_ADJ           = 0,
                        i_DLY_INCDEC        = 0,
                        i_CLK_IN            = self.clk_1,
                        o_DLY_TAP_VALUE     = self.open,
                        o_O                 = self.q
                    )
                elif (delay_type == "DYNAMIC"):
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_DELAY",
                        # Parameters.
                        # -----------
                        p_DELAY             = delay,
                        # Ports
                        #------
                        i_I                 = self.q_1,
                        i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                        i_DLY_ADJ           = platform.request("FABRIC_DLY_ADJ"),
                        i_DLY_INCDEC        = platform.request("FABRIC_DLY_INCDEC"),
                        i_CLK_IN            = self.clk_1,
                        o_DLY_TAP_VALUE     = platform.request("FABRIC_DLY_TAP_VALUE"),
                        o_O                 = self.q
                    )
                    
                # Module instance.
                # ----------------
                self.specials += Instance("O_BUFT",
                    # Ports
                    #------
                    i_I     = self.q,
                    i_T     = self.oe_out,
                    o_O     = platform.request("IOPAD_SDATA")
                )

            elif (clock_forwarding == "TRUE"):
                # Module instance.
                # ----------------
                self.specials += Instance("O_SERDES_CLK",
                    # Parameters
                    #-----------
                    p_DATA_RATE    = data_rate,
                    p_CLOCK_PHASE  = int(clock_phase),
                    # Ports
                    #------
                    i_CLK_EN        = self.oe_out,
                    i_PLL_LOCK      = 1,
                    i_PLL_CLK       = self.clk_1,
                    o_OUTPUT_CLK    = self.clk_out
                )
                # Module instance.
                # ----------------
                self.specials += Instance("O_BUF",
                    # Parameters.
                    # -----------
                    p_IOSTANDARD                = voltage_standard,
                    p_DRIVE_STRENGTH            = drive_strength,
                    p_SLEW_RATE                 = slew_rate,
                    # Ports
                    #------
                    i_I     = self.clk_out,
                    o_O     = platform.request("IOPAD_CLK_OUT")
                )
    
    elif clocking == "PLL":
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
        if clocking_source == "RX_IO_CLOCK":
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF", # For Clock
                # Parameters.
                # -----------
                p_WEAK_KEEPER = io_mode,
                # Ports
                #------
                i_I     = platform.request("IOPAD_PLL_REF_CLK"),
                i_EN    = 1,
                o_O     = self.clk
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("CLK_BUF",
                # Ports
                #------
                i_I     = self.clk,
                o_O     = self.clk_1
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("PLL",
                # Parameters.
                # -----------
                p_DIVIDE_CLK_IN_BY_2    = "FALSE",
                p_PLL_MULT              = pll_mult,
                p_PLL_DIV               = pll_div,
                p_PLL_POST_DIV          = 17,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.clk_1,
                o_CLK_OUT           = self.pll_clk,           
                o_LOCK              = self.pll_lock
            )
            
            if (delay_adjust == "FALSE"):
                # Module instance.
                # ----------------
                self.specials += Instance("O_SERDES",
                    # Parameters.
                    # -----------
                    p_DATA_RATE             = data_rate,
                    p_WIDTH                 = width,
                    # Ports
                    #------
                    i_D                     = platform.request("FABRIC_PDATA"),   
                    i_RST                   = platform.request("FABRIC_RST"),   
                    i_DATA_VALID            = platform.request("FABRIC_DATA_VALID"),         
                    i_CLK_IN                = platform.request("FABRIC_CLK_IN"),    
                    i_OE_IN                 = platform.request("FABRIC_OE_IN"),
                    o_OE_OUT                = self.oe_out,     
                    o_Q                     = self.q,
                    i_CHANNEL_BOND_SYNC_IN  = 0,        
                    o_CHANNEL_BOND_SYNC_OUT = self.open1,
                    i_PLL_LOCK              = self.pll_lock,
                    i_PLL_CLK               = self.pll_clk
                )
            
                if (clock_forwarding == "FALSE"):
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_BUFT",
                        # Ports
                        #------
                        i_I     = self.q,
                        i_T     = self.oe_out,
                        o_O     = platform.request("IOPAD_SDATA")
                    )
                elif (clock_forwarding == "TRUE"):
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_SERDES_CLK",
                        # Parameters
                        #-----------
                        p_DATA_RATE    = data_rate,
                        p_CLOCK_PHASE  = int(clock_phase),
                        # Ports
                        #------
                        i_CLK_EN        = self.oe_out,
                        i_PLL_LOCK      = self.pll_lock,
                        i_PLL_CLK       = self.pll_clk,
                        o_OUTPUT_CLK    = self.clk_out
                    )
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_BUF",
                        # Parameters.
                        # -----------
                        p_IOSTANDARD                = voltage_standard,
                        p_DRIVE_STRENGTH            = drive_strength,
                        p_SLEW_RATE                 = slew_rate,
                        # Ports
                        #------
                        i_I     = self.clk_out,
                        o_O     = platform.request("IOPAD_CLK_OUT")
                    )
            
            elif (delay_adjust == "TRUE"):
                # Module instance.
                # ----------------
                self.specials += Instance("O_SERDES",
                    # Parameters.
                    # -----------
                    p_DATA_RATE             = data_rate,
                    p_WIDTH                 = width,
                    # Ports
                    #------
                    i_D                     = platform.request("FABRIC_PDATA"),   
                    i_RST                   = platform.request("FABRIC_RST"),   
                    i_DATA_VALID            = platform.request("FABRIC_DATA_VALID"),         
                    i_CLK_IN                = platform.request("FABRIC_CLK_IN"),    
                    i_OE_IN                 = platform.request("FABRIC_OE_IN"),
                    o_OE_OUT                = self.oe_out,     
                    o_Q                     = self.q_1,
                    i_CHANNEL_BOND_SYNC_IN  = 0,        
                    o_CHANNEL_BOND_SYNC_OUT = self.open1,
                    i_PLL_LOCK              = self.pll_lock,
                    i_PLL_CLK               = self.pll_clk
                )
                
                if (clock_forwarding == "FALSE"):
                    if (delay_type == "STATIC"):
                        # Module instance.
                        # ----------------
                        self.specials += Instance("O_DELAY",
                            # Parameters.
                            # -----------
                            p_DELAY             = delay,
                            # Ports
                            #------
                            i_I                 = self.q_1,
                            i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                            i_DLY_ADJ           = 0,
                            i_DLY_INCDEC        = 0,
                            i_CLK_IN            = self.pll_clk,
                            o_DLY_TAP_VALUE     = self.open,
                            o_O                 = self.q
                        )
                        
                    elif (delay_type == "DYNAMIC"):
                        # Module instance.
                        # ----------------
                        self.specials += Instance("O_DELAY",
                            # Parameters.
                            # -----------
                            p_DELAY             = delay,
                            # Ports
                            #------
                            i_I                 = self.q_1,
                            i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                            i_DLY_ADJ           = platform.request("FABRIC_DLY_ADJ"),
                            i_DLY_INCDEC        = platform.request("FABRIC_DLY_INCDEC"),
                            i_CLK_IN            = self.pll_clk,
                            o_DLY_TAP_VALUE     = platform.request("FABRIC_DLY_TAP_VALUE"),
                            o_O                 = self.q
                        )
                    
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_BUFT",
                        # Ports
                        #------
                        i_I     = self.q,
                        i_T     = self.oe_out,
                        o_O     = platform.request("IOPAD_SDATA")
                    )
                elif (clock_forwarding == "TRUE"):
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_SERDES_CLK",
                        # Parameters
                        #-----------
                        p_DATA_RATE    = data_rate,
                        p_CLOCK_PHASE  = int(clock_phase),
                        # Ports
                        #------
                        i_CLK_EN        = self.oe_out,
                        i_PLL_LOCK      = self.pll_lock,
                        i_PLL_CLK       = self.pll_clk,
                        o_OUTPUT_CLK    = self.clk_out
                    )
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_BUF",
                        # Parameters.
                        # -----------
                        p_IOSTANDARD                = voltage_standard,
                        p_DRIVE_STRENGTH            = drive_strength,
                        p_SLEW_RATE                 = slew_rate,
                        # Ports
                        #------
                        i_I     = self.clk_out,
                        o_O     = platform.request("IOPAD_CLK_OUT")
                    )
            
        elif clocking_source == "LOCAL_OSCILLATOR":
            # Module instance.
            # ----------------
            self.specials += Instance("BOOT_CLOCK",
                # Parameters.
                # -----------
                o_O     = self.lo_clk
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("PLL",
                # Parameters.
                # -----------
                p_DIVIDE_CLK_IN_BY_2    = "FALSE",
                p_PLL_MULT              = pll_mult,
                p_PLL_DIV               = pll_div,
                p_PLL_POST_DIV          = 17,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.lo_clk,
                o_CLK_OUT           = self.pll_clk,           
                o_LOCK              = self.pll_lock
            )
            if (delay_adjust == "FALSE"):
                # Module instance.
                # ----------------
                self.specials += Instance("O_SERDES",
                    # Parameters.
                    # -----------
                    p_DATA_RATE             = data_rate,
                    p_WIDTH                 = width,
                    # Ports
                    #------
                    i_D                     = platform.request("FABRIC_PDATA"),   
                    i_RST                   = platform.request("FABRIC_RST"),   
                    i_DATA_VALID            = platform.request("FABRIC_DATA_VALID"),         
                    i_CLK_IN                = platform.request("FABRIC_CLK_IN"),    
                    i_OE_IN                 = platform.request("FABRIC_OE_IN"),
                    o_OE_OUT                = self.oe_out,     
                    o_Q                     = self.q,
                    i_CHANNEL_BOND_SYNC_IN  = 0,        
                    o_CHANNEL_BOND_SYNC_OUT = self.open1,
                    i_PLL_LOCK              = self.pll_lock,
                    i_PLL_CLK               = self.pll_clk
                )

                if (clock_forwarding == "FALSE"):
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_BUFT",
                        # Ports
                        #------
                        i_I     = self.q,
                        i_T     = self.oe_out,
                        o_O     = platform.request("IOPAD_SDATA")
                    )
                elif (clock_forwarding == "TRUE"):
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_SERDES_CLK",
                        # Parameters
                        #-----------
                        p_DATA_RATE    = data_rate,
                        p_CLOCK_PHASE  = int(clock_phase),
                        # Ports
                        #------
                        i_CLK_EN        = self.oe_out,
                        i_PLL_LOCK      = self.pll_lock,
                        i_PLL_CLK       = self.pll_clk,
                        o_OUTPUT_CLK    = self.clk_out
                    )
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_BUF",
                        # Parameters.
                        # -----------
                        p_IOSTANDARD                = voltage_standard,
                        p_DRIVE_STRENGTH            = drive_strength,
                        p_SLEW_RATE                 = slew_rate,
                        # Ports
                        #------
                        i_I     = self.clk_out,
                        o_O     = platform.request("IOPAD_CLK_OUT")
                    )
                    
            elif (delay_adjust == "TRUE"):
                # Module instance.
                # ----------------
                self.specials += Instance("O_SERDES",
                    # Parameters.
                    # -----------
                    p_DATA_RATE             = data_rate,
                    p_WIDTH                 = width,
                    # Ports
                    #------
                    i_D                     = platform.request("FABRIC_PDATA"),   
                    i_RST                   = platform.request("FABRIC_RST"),   
                    i_DATA_VALID            = platform.request("FABRIC_DATA_VALID"),         
                    i_CLK_IN                = platform.request("FABRIC_CLK_IN"),    
                    i_OE_IN                 = platform.request("FABRIC_OE_IN"),
                    o_OE_OUT                = self.oe_out,     
                    o_Q                     = self.q_1,
                    i_CHANNEL_BOND_SYNC_IN  = 0,        
                    o_CHANNEL_BOND_SYNC_OUT = self.open1,
                    i_PLL_LOCK              = self.pll_lock,
                    i_PLL_CLK               = self.pll_clk
                )
                if (clock_forwarding == "FALSE"):
                    if (delay_type == "STATIC"):
                    # Module instance.
                        # ----------------
                        self.specials += Instance("O_DELAY",
                            # Parameters.
                            # -----------
                            p_DELAY             = delay,
                            # Ports
                            #------
                            i_I                 = self.q_1,
                            i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                            i_DLY_ADJ           = 0,
                            i_DLY_INCDEC        = 0,
                            i_CLK_IN            = self.pll_clk,
                            o_DLY_TAP_VALUE     = self.open,
                            o_O                 = self.q
                        )
                    elif (delay_type == "DYNAMIC"):
                        # Module instance.
                        # ----------------
                        self.specials += Instance("O_DELAY",
                            # Parameters.
                            # -----------
                            p_DELAY             = delay,
                            # Ports
                            #------
                            i_I                 = self.q_1,
                            i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
                            i_DLY_ADJ           = platform.request("FABRIC_DLY_ADJ"),
                            i_DLY_INCDEC        = platform.request("FABRIC_DLY_INCDEC"),
                            i_CLK_IN            = self.pll_clk,
                            o_DLY_TAP_VALUE     = platform.request("FABRIC_DLY_TAP_VALUE"),
                            o_O                 = self.q
                        )
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_BUFT",
                        # Ports
                        #------
                        i_I     = self.q,
                        i_T     = self.oe_out,
                        o_O     = platform.request("IOPAD_SDATA")
                    )
                elif (clock_forwarding == "TRUE"):
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_SERDES_CLK",
                        # Parameters
                        #-----------
                        p_DATA_RATE    = data_rate,
                        p_CLOCK_PHASE  = int(clock_phase),
                        # Ports
                        #------
                        i_CLK_EN        = self.oe_out,
                        i_PLL_LOCK      = self.pll_lock,
                        i_PLL_CLK       = self.pll_clk,
                        o_OUTPUT_CLK    = self.clk_out
                    )
                    # Module instance.
                    # ----------------
                    self.specials += Instance("O_BUF",
                        # Parameters.
                        # -----------
                        p_IOSTANDARD                = voltage_standard,
                        p_DRIVE_STRENGTH            = drive_strength,
                        p_SLEW_RATE                 = slew_rate,
                        # Ports
                        #------
                        i_I     = self.clk_out,
                        o_O     = platform.request("IOPAD_CLK_OUT")
                    )

#################################################################################
# O_DDR
#################################################################################
def O_DDR(self, platform, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq, num_odly):
    platform.add_extension(get_oddr_ios(num_odly))
    self.q      = Signal(1)
    self.clk    = Signal(1)
    self.clk_1  = Signal(1)
    self.clk_2  = Signal(1)
    
    if (clocking == "RX_CLOCK"):
        clock_out = self.clk_2
        # clk = platform.request("IOPAD_CLK")
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF",
            # Parameters.
            # -----------
            p_WEAK_KEEPER = io_mode,
            # Ports
            #------
            i_I     = platform.request("IOPAD_CLK"),
            i_EN    = 1,
            o_O     = self.clk_1
        )
        
        # Module instance.
        # ----------------
        self.specials += Instance("CLK_BUF",
            # Ports
            #------
            i_I     = self.clk_1,
            o_O     = clock_out
        )
        
    elif (clocking == "PLL"):
        self.lo_clk     = Signal(1)
        self.pll_clk    = Signal(1)
        self.pll_lock   = Signal(1)
        clock_out = self.pll_clk
        
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
        if (clocking_source == "LOCAL_OSCILLATOR"):
            
            # Module instance.
            # ----------------
            self.specials += Instance("BOOT_CLOCK",
                # Parameters.
                # -----------
                o_O     = self.lo_clk
            )
            # Module instance.
            # ----------------
            self.specials += Instance("PLL",
                # Parameters.
                # -----------
                p_DIVIDE_CLK_IN_BY_2    = "FALSE",
                p_PLL_MULT              = pll_mult,
                p_PLL_DIV               = pll_div,
                p_PLL_POST_DIV          = 17,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.lo_clk,
                o_CLK_OUT           = self.pll_clk,          
                o_LOCK              = self.pll_lock
            )
        elif (clocking_source == "RX_IO_CLOCK"):
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF", # For Clock
                # Parameters.
                # -----------
                p_WEAK_KEEPER = io_mode,
                # Ports
                #------
                i_I     = platform.request("IOPAD_PLL_REF_CLK"),
                i_EN    = 1,
                o_O     = self.clk
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("CLK_BUF",
                # Ports
                #------
                i_I     = self.clk,
                o_O     = self.clk_1
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("PLL",
                # Parameters.
                # -----------
                p_DIVIDE_CLK_IN_BY_2    = "FALSE",
                p_PLL_MULT              = pll_mult,
                p_PLL_DIV               = pll_div,
                p_PLL_POST_DIV          = 17,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.clk_1,
                o_CLK_OUT           = clock_out,           
                o_LOCK              = self.pll_lock
            )
    
    # Module instance.
    # ----------------
    self.specials += Instance("O_DDR",
        # Ports
        #------
        i_D = platform.request("FABRIC_DD_IN"),
        i_R = platform.request("FABRIC_RST"),
        i_E = platform.request("FABRIC_EN"),
        i_C = clock_out,
        o_Q = self.q
    )
    # Module instance.
    # ----------------
    self.specials += Instance("O_BUF",
        # Ports
        #------
        i_I     = self.q,
        o_O     = platform.request("IOPAD_SD_OUT")
    )

#################################################################################
# O_DELAY
#################################################################################
def O_DELAY(self, platform, sel_dly, io_model, combination, io_mode, voltage_standard, slew_rate, drive_strength, delay, delay_type, clocking, clocking_source, ref_clk_freq, out_clk_freq, num_odly, width, data_rate, ports_file, bank_select, io_type, diff_termination):
    
    platform.add_extension(get_odelay_ios(num_odly))
    ADDR_WIDTH = 6
    
    if (clocking == "PLL"):
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
    else:
        pll_mult = 16
        pll_div  = 1
    
    if (io_type == "DIFFERENTIAL"):
        diff_termination = diff_termination
    else:
        diff_termination = "FALSE"
    
    if (combination == "O_DELAY"):
        dly_loc = ports_file_read(ports_file, bank_select, num_odly, io_type)
        fabric_i     = platform.request("FABRIC_DATA_IN")
        
        if (io_type == "SINGLE_ENDED"):
            iopad_o     = platform.request("IOPAD_DATA_OUT")
            data_out    = iopad_o
        elif (io_type == "DIFFERENTIAL"):
            iopad_o_p   = platform.request("IOPAD_DATA_OUT_P")
            iopad_o_n   = platform.request("IOPAD_DATA_OUT_N")
            data_out    = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
                # Parameters.
                # -----------
                p_IO_MODEL                  = combination,
                p_DELAY                     = delay,
                p_WEAK_KEEPER               = io_mode,
                p_IOSTANDARD                = voltage_standard,
                p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
                p_NUM_DLY                   = num_odly,
                p_DELAY_TYPE                = delay_type,
                p_PLL_MULT                  = pll_mult,
                p_PLL_DIV                   = pll_div,
                p_DIFFERENTIAL_TERMINATION  = diff_termination,
                p_IO_TYPE                   = io_type,
                p_DLY_SEL_WIDTH             = sel_dly,
                # Ports
                #------
                i_DATA_IN                   = fabric_i,
                i_RESET                     = platform.request("FABRIC_RST"),
                i_SEL_DLY                   = platform.request("SEL_DLY"),
                i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
                i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
                i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
                o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_odly)]),
                o_DATA_OUT                  = data_out
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                  = combination,
            p_DELAY                     = delay,
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                   = num_odly,
            p_DELAY_TYPE                = delay_type,
            p_PLL_MULT                  = pll_mult,
            p_PLL_DIV                   = pll_div,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            p_IO_TYPE                   = io_type,
            p_DLY_SEL_WIDTH             = sel_dly,
            # Ports
            #------
            i_DATA_IN                   = fabric_i,
            i_CLK_IN                    = clk_in,
            i_RESET                     = platform.request("FABRIC_RST"),
            i_SEL_DLY                   = platform.request("SEL_DLY"),
            i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_odly)]),
            o_DATA_OUT                  = data_out
        )
        
        
    elif (combination == "O_DELAY_O_SERDES"):
        
        platform.add_extension(get_oserdes_ios(num_odly, width))
        
        dly_loc = ports_file_read(ports_file, bank_select, num_odly, io_type)
        
        if (io_type == "SINGLE_ENDED"):
            iopad_o     = platform.request("IOPAD_SDATA")
            sdata_out   = iopad_o
        elif (io_type == "DIFFERENTIAL"):
            iopad_o_p   = platform.request("IOPAD_SDATA_P")
            iopad_o_n   = platform.request("IOPAD_SDATA_N")
            sdata_out   = Cat(iopad_o_p, iopad_o_n)
            
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
                # Parameters.
                # -----------
                p_IO_MODEL                  = combination,
                p_DELAY                     = delay,
                p_WEAK_KEEPER               = io_mode,
                p_IOSTANDARD                = voltage_standard,
                p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
                p_NUM_DLY                   = num_odly,
                p_DELAY_TYPE                = delay_type,
                p_WIDTH                     = width,
                p_DRIVE_STRENGTH            = drive_strength,
                p_SLEW_RATE                 = slew_rate,
                p_DATA_RATE                 = data_rate,
                p_PLL_MULT                  = pll_mult,
                p_PLL_DIV                   = pll_div,
                p_DIFFERENTIAL_TERMINATION  = diff_termination,
                p_IO_TYPE                   = io_type,
                p_DLY_SEL_WIDTH             = sel_dly,
                # Ports
                #------
                i_PDATA_IN                  = Cat([platform.request(f"FABRIC_PDATA_{i}") for i in range(num_odly)]),
                i_FAB_CLK_IN                = platform.request("FABRIC_CLK_IN"),
                i_DATA_VALID                = platform.request("FABRIC_DATA_VALID"),
                i_OE_IN                     = platform.request("FABRIC_OE_IN"),
                i_RESET                     = platform.request("FABRIC_RST"),
                i_SEL_DLY                   = platform.request("SEL_DLY"),
                i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
                i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
                i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
                o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_odly)]),
                o_SDATA_OUT                 = sdata_out
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                  = combination,
            p_DELAY                     = delay,
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                   = num_odly,
            p_DELAY_TYPE                = delay_type,
            p_WIDTH                     = width,
            p_DRIVE_STRENGTH            = drive_strength,
            p_SLEW_RATE                 = slew_rate,
            p_DATA_RATE                 = data_rate,
            p_PLL_MULT                  = pll_mult,
            p_PLL_DIV                   = pll_div,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            p_IO_TYPE                   = io_type,
            p_DLY_SEL_WIDTH             = sel_dly,
            # Ports
            #------
            i_CLK_IN                    = clk_in,
            i_PDATA_IN                  = Cat([platform.request(f"FABRIC_PDATA_{i}") for i in range(num_odly)]),
            i_FAB_CLK_IN                = platform.request("FABRIC_CLK_IN"),
            i_DATA_VALID                = platform.request("FABRIC_DATA_VALID"),
            i_OE_IN                     = platform.request("FABRIC_OE_IN"),
            i_RESET                     = platform.request("FABRIC_RST"),
            i_SEL_DLY                   = platform.request("SEL_DLY"),
            i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_odly)]),
            o_SDATA_OUT                 = sdata_out
        )
        
    
    elif (combination == "O_DELAY_O_DDR"):
        
        platform.add_extension(get_oddr_ios(num_odly))
        
        dly_loc = ports_file_read(ports_file, bank_select, num_odly, io_type)
        
        if (io_type == "SINGLE_ENDED"):
            iopad_o   = platform.request("IOPAD_SD_OUT")
            sd_out    = iopad_o
        elif (io_type == "DIFFERENTIAL"):
            iopad_o_p = platform.request("IOPAD_SD_OUT_P")
            iopad_o_n = platform.request("IOPAD_SD_OUT_N")
            sd_out    = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
                # Parameters.
                # -----------
                p_IO_MODEL                  = combination,
                p_DELAY                     = delay,
                p_WEAK_KEEPER               = io_mode,
                p_IOSTANDARD                = voltage_standard,
                p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
                p_NUM_DLY                   = num_odly,
                p_DELAY_TYPE                = delay_type,
                p_DRIVE_STRENGTH            = drive_strength,
                p_SLEW_RATE                 = slew_rate,
                p_PLL_MULT                  = pll_mult,
                p_PLL_DIV                   = pll_div,
                p_DIFFERENTIAL_TERMINATION  = diff_termination,
                p_IO_TYPE                   = io_type,
                p_DLY_SEL_WIDTH             = sel_dly,
                # Ports
                #------
                i_DD_IN                     = Cat([platform.request(f"FABRIC_DD_IN_{i}") for i in range(num_odly)]),
                i_EN                        = platform.request("FABRIC_EN"),
                i_RESET                     = platform.request("FABRIC_RST"),
                i_SEL_DLY                   = platform.request("SEL_DLY"),
                i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
                i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
                i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
                o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_odly)]),
                o_SD_OUT                    = sd_out
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                  = combination,
            p_DELAY                     = delay,
            p_WEAK_KEEPER               = io_mode,
            p_IOSTANDARD                = voltage_standard,
            p_DLY_LOC                   = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                   = num_odly,
            p_DELAY_TYPE                = delay_type,
            p_DRIVE_STRENGTH            = drive_strength,
            p_SLEW_RATE                 = slew_rate,
            p_PLL_MULT                  = pll_mult,
            p_PLL_DIV                   = pll_div,
            p_DIFFERENTIAL_TERMINATION  = diff_termination,
            p_IO_TYPE                   = io_type,
            p_DLY_SEL_WIDTH             = sel_dly,
            # Ports
            #------
            i_CLK_IN                    = clk_in,
            i_DD_IN                     = Cat([platform.request(f"FABRIC_DD_IN_{i}") for i in range(num_odly)]),
            i_EN                        = platform.request("FABRIC_EN"),
            i_RESET                     = platform.request("FABRIC_RST"),
            i_SEL_DLY                   = platform.request("SEL_DLY"),
            i_DLY_LOAD                  = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                   = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE           = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_odly)]),
            o_SD_OUT                    = sd_out
        )

#################################################################################
# Bidirectional Delays
#################################################################################
def Bidirectional_Delays(self, platform, sel_dly, combination, num_dly, io_type, io_mode, voltage_standard, diff_termination, slew_rate, drive_strength,
                        delay, delay_type, ports_file, bank_select, clocking, out_clk_freq, ref_clk_freq, clocking_source, width, data_rate, op_mode):
    
    platform.add_extension(clock_ios())
    platform.add_extension(dly_ios(num_dly))
    platform.add_extension(bidirectional_ios(num_dly, width))
    dly_loc = ports_file_read(ports_file, bank_select, num_dly, io_type)

    if (clocking == "PLL"):
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
    else:
        pll_mult = 16
        pll_div  = 1
    
    ### I_DELAY+O_DELAY ###
    if (combination == "I_DELAY+O_DELAY"):
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_DIN")
            iopad_o     = platform.request("IOPAD_DOUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_DIN_P")
            iopad_i_n   = platform.request("IOPAD_DIN_N")
            iopad_o_p   = platform.request("IOPAD_DOUT_P")
            iopad_o_n   = platform.request("IOPAD_DOUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_DIN_IDLY                      = iopad_i,
            i_DIN_ODLY                      = platform.request("FABRIC_DIN"),
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)]),
            o_DOUT_IDLY                     = platform.request("FABRIC_DOUT"),
            o_DOUT_ODLY                     = iopad_o
            )
        
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_DIN_IDLY                      = iopad_i,
            i_DIN_ODLY                      = platform.request("FABRIC_DIN"),
            i_CLK_IN                        = clk_in,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)]),
            o_DOUT_IDLY                     = platform.request("FABRIC_DOUT"),
            o_DOUT_ODLY                     = iopad_o
            )
    
    ### I_DELAY+O_SERDES_O_DELAY ###
    elif (combination == "I_DELAY+O_SERDES_O_DELAY"):
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_DIN")
            iopad_o     = platform.request("IOPAD_SDATA_OUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_DIN_P")
            iopad_i_n   = platform.request("IOPAD_DIN_N")
            iopad_o_p   = platform.request("IOPAD_SDATA_OUT_P")
            iopad_o_n   = platform.request("IOPAD_SDATA_OUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
            
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_WIDTH                         = width,
            p_DATA_RATE                     = data_rate,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_DIN_IDLY                      = iopad_i,
            i_PDATA_IN_OSERDES              = Cat([platform.request(f"FABRIC_PDATA_IN_{i}") for i in range(math.ceil(num_dly/2))]),
            i_DATA_VALID_OSERDES            = platform.request("FABRIC_DATA_VALID"),
            i_FAB_CLK_IN                    = platform.request("FABRIC_CLK_IN"),
            i_OE_IN                         = platform.request("FABRIC_OE_IN"),
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)]),
            o_DOUT_IDLY                     = platform.request("FABRIC_DOUT"),
            o_SDATA_OUT_ODLY                = iopad_o
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
                
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_WIDTH                         = width,
            p_DATA_RATE                     = data_rate,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_DIN_IDLY                      = iopad_i,
            i_CLK_IN                        = clk_in,
            i_PDATA_IN_OSERDES              = Cat([platform.request(f"FABRIC_PDATA_IN_{i}") for i in range(math.ceil(num_dly/2))]),
            i_DATA_VALID_OSERDES            = platform.request("FABRIC_DATA_VALID"),
            i_FAB_CLK_IN                    = platform.request("FABRIC_CLK_IN"),
            i_OE_IN                         = platform.request("FABRIC_OE_IN"),
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)]),
            o_DOUT_IDLY                     = platform.request("FABRIC_DOUT"),
            o_SDATA_OUT_ODLY                = iopad_o
            )
    
    ### I_DELAY+O_DDR_O_DELAY ###
    elif (combination == "I_DELAY+O_DDR_O_DELAY"):
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_DIN")
            iopad_o     = platform.request("IOPAD_SD_OUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_DIN_P")
            iopad_i_n   = platform.request("IOPAD_DIN_N")
            iopad_o_p   = platform.request("IOPAD_SD_OUT_P")
            iopad_o_n   = platform.request("IOPAD_SD_OUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
            
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_DIN_IDLY                      = iopad_i,
            i_DD_IN_ODDR                    = Cat([platform.request(f"FABRIC_DD_IN_{i}") for i in range(math.ceil(num_dly/2))]),
            i_EN_ODDR                       = platform.request("FABRIC_EN_ODDR"),
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)]),
            o_DOUT_IDLY                     = platform.request("FABRIC_DOUT"),
            o_SD_OUT_ODDR                   = iopad_o
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
                
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_CLK_IN                        = clk_in,
            i_DIN_IDLY                      = iopad_i,
            i_DD_IN_ODDR                    = Cat([platform.request(f"FABRIC_DD_IN_{i}") for i in range(math.ceil(num_dly/2))]),
            i_EN_ODDR                       = platform.request("FABRIC_EN_ODDR"),
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)]),
            o_DOUT_IDLY                     = platform.request("FABRIC_DOUT"),
            o_SD_OUT_ODDR                   = iopad_o
            )
            
    ### I_DELAY_I_SERDES+O_DELAY ###
    elif (combination == "I_DELAY_I_SERDES+O_DELAY"):
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_SDATA_IN")
            iopad_o     = platform.request("IOPAD_DOUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_SDATA_IN_P")
            iopad_i_n   = platform.request("IOPAD_SDATA_IN_N")
            iopad_o_p   = platform.request("IOPAD_DOUT_P")
            iopad_o_n   = platform.request("IOPAD_DOUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_SDATA_IN_IDLY                 = iopad_i,
            i_EN_ISERDES                    = platform.request("FABRIC_EN"),
            i_BITSLIP_ADJ                   = platform.request("FABRIC_BITSLIP_ADJ"),
            o_DATA_VALID_ISERDES            = platform.request("FABRIC_DATA_VALID"),            
            o_DPA_LOCK                      = platform.request("FABRIC_DPA_LOCK"),
            o_DPA_ERROR                     = platform.request("FABRIC_DPA_ERROR"),
            o_CLK_OUT                       = platform.request("FABRIC_CLK_OUT"),
            o_PDATA_OUT_ISERDES             = Cat([platform.request(f"FABRIC_PDATA_OUT_{i}") for i in range(math.ceil(num_dly/2))]),   
            i_DIN_ODLY                      = platform.request("FABRIC_DIN"),
            o_DOUT_ODLY                     = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_CLK_IN                        = clk_in,
            i_SDATA_IN_IDLY                 = iopad_i,
            i_EN_ISERDES                    = platform.request("FABRIC_EN"),
            i_BITSLIP_ADJ                   = platform.request("FABRIC_BITSLIP_ADJ"),
            o_DATA_VALID_ISERDES            = platform.request("FABRIC_DATA_VALID"),            
            o_DPA_LOCK                      = platform.request("FABRIC_DPA_LOCK"),
            o_DPA_ERROR                     = platform.request("FABRIC_DPA_ERROR"),
            o_CLK_OUT                       = platform.request("FABRIC_CLK_OUT"),
            o_PDATA_OUT_ISERDES             = Cat([platform.request(f"FABRIC_PDATA_OUT_{i}") for i in range(math.ceil(num_dly/2))]),   
            i_DIN_ODLY                      = platform.request("FABRIC_DIN"),
            o_DOUT_ODLY                     = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])
            )
            
    ### I_DELAY_I_SERDES+O_SERDES_O_DELAY ###
    elif (combination == "I_DELAY_I_SERDES+O_SERDES_O_DELAY"):
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_SDATA_IN")
            iopad_o     = platform.request("IOPAD_SDATA_OUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_SDATA_IN_P")
            iopad_i_n   = platform.request("IOPAD_SDATA_IN_N")
            iopad_o_p   = platform.request("IOPAD_SDATA_OUT_P")
            iopad_o_n   = platform.request("IOPAD_SDATA_OUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_WIDTH                         = width,
            p_DATA_RATE                     = data_rate,
            p_DPA_MODE                      = op_mode,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_SDATA_IN_IDLY                 = iopad_i,
            i_PDATA_IN_OSERDES              = Cat([platform.request(f"FABRIC_PDATA_IN_{i}") for i in range(math.ceil(num_dly/2))]),   
            i_DATA_VALID_OSERDES            = platform.request("FABRIC_DATA_VALID"),                
            i_FAB_CLK_IN                    = platform.request("FABRIC_CLK_IN"),        
            i_OE_IN                         = platform.request("FABRIC_OE_IN"),
            i_EN                            = platform.request("FABRIC_EN"),
            i_BITSLIP_ADJ                   = platform.request("FABRIC_BITSLIP_ADJ"),     
            o_CLK_OUT                       = platform.request("FABRIC_CLK_OUT"),
            o_DPA_LOCK                      = platform.request("FABRIC_DPA_LOCK"),
            o_DPA_ERROR                     = platform.request("FABRIC_DPA_ERROR"),
            o_DATA_VALID_ISERDES            = platform.request("FABRIC_DATA_VALID"),            
            o_PDATA_OUT_ISERDES             = Cat([platform.request(f"FABRIC_PDATA_OUT_{i}") for i in range(math.ceil(num_dly/2))]),           
            o_SDATA_OUT_ODLY                = iopad_o, 
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])          
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_WIDTH                         = width,
            p_DATA_RATE                     = data_rate,
            p_DPA_MODE                      = op_mode,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_CLK_IN                        = clk_in,
            i_SDATA_IN_IDLY                 = iopad_i,
            i_PDATA_IN_OSERDES              = Cat([platform.request(f"FABRIC_PDATA_IN_{i}") for i in range(math.ceil(num_dly/2))]),   
            i_DATA_VALID_OSERDES            = platform.request("FABRIC_DATA_VALID"),                
            i_FAB_CLK_IN                    = platform.request("FABRIC_CLK_IN"),        
            i_OE_IN                         = platform.request("FABRIC_OE_IN"),
            i_EN                            = platform.request("FABRIC_EN"),
            i_BITSLIP_ADJ                   = platform.request("FABRIC_BITSLIP_ADJ"),     
            o_CLK_OUT                       = platform.request("FABRIC_CLK_OUT"),
            o_DPA_LOCK                      = platform.request("FABRIC_DPA_LOCK"),
            o_DPA_ERROR                     = platform.request("FABRIC_DPA_ERROR"),
            o_DATA_VALID_ISERDES            = platform.request("FABRIC_DATA_VALID"),            
            o_PDATA_OUT_ISERDES             = Cat([platform.request(f"FABRIC_PDATA_OUT_{i}") for i in range(math.ceil(num_dly/2))]),           
            o_SDATA_OUT_ODLY                = iopad_o, 
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])          
            )
    
    ### I_DELAY_I_SERDES+O_DDR_O_DELAY ###
    elif (combination == "I_DELAY_I_SERDES+O_DDR_O_DELAY"):
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_SDATA_IN")
            iopad_o     = platform.request("IOPAD_SD_OUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_SDATA_IN_P")
            iopad_i_n   = platform.request("IOPAD_SDATA_IN_N")
            iopad_o_p   = platform.request("IOPAD_SD_OUT_P")
            iopad_o_n   = platform.request("IOPAD_SD_OUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_WIDTH                         = width,
            p_DATA_RATE                     = data_rate,
            p_DPA_MODE                      = op_mode,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_SDATA_IN_IDLY                 = iopad_i,
            i_EN_ISERDES                    = platform.request("FABRIC_EN"),
            i_BITSLIP_ADJ                   = platform.request("FABRIC_BITSLIP_ADJ"),
            o_DATA_VALID_ISERDES            = platform.request("FABRIC_DATA_VALID"),
            o_DPA_LOCK                      = platform.request("FABRIC_DPA_LOCK"),
            o_DPA_ERROR                     = platform.request("FABRIC_DPA_ERROR"),
            o_CLK_OUT                       = platform.request("FABRIC_CLK_OUT"),
            o_PDATA_OUT_ISERDES             = Cat([platform.request(f"FABRIC_PDATA_OUT_{i}") for i in range(math.ceil(num_dly/2))]),
            i_DD_IN_ODDR                    = Cat([platform.request(f"FABRIC_DD_IN_{i}") for i in range(math.ceil(num_dly/2))]),
            i_EN_ODDR                       = platform.request("FABRIC_EN_ODDR"),
            o_SD_OUT_ODDR                   = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])          
            )
        
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_WIDTH                         = width,
            p_DATA_RATE                     = data_rate,
            p_DPA_MODE                      = op_mode,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_CLK_IN                        = clk_in,
            i_SDATA_IN_IDLY                 = iopad_i,
            i_EN_ISERDES                    = platform.request("FABRIC_EN"),
            i_BITSLIP_ADJ                   = platform.request("FABRIC_BITSLIP_ADJ"),
            o_DATA_VALID_ISERDES            = platform.request("FABRIC_DATA_VALID"),
            o_DPA_LOCK                      = platform.request("FABRIC_DPA_LOCK"),
            o_DPA_ERROR                     = platform.request("FABRIC_DPA_ERROR"),
            o_CLK_OUT                       = platform.request("FABRIC_CLK_OUT"),
            o_PDATA_OUT_ISERDES             = Cat([platform.request(f"FABRIC_PDATA_OUT_{i}") for i in range(math.ceil(num_dly/2))]),
            i_DD_IN_ODDR                    = Cat([platform.request(f"FABRIC_DD_IN_{i}") for i in range(math.ceil(num_dly/2))]),
            i_EN_ODDR                       = platform.request("FABRIC_EN_ODDR"),
            o_SD_OUT_ODDR                   = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])          
            )
            
    ### I_DELAY_I_DDR+O_DELAY ###
    elif (combination == "I_DELAY_I_DDR+O_DELAY"):
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_SD_IN")
            iopad_o     = platform.request("IOPAD_DOUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_SD_IN_P")
            iopad_i_n   = platform.request("IOPAD_SD_IN_N")
            iopad_o_p   = platform.request("IOPAD_DOUT_P")
            iopad_o_n   = platform.request("IOPAD_DOUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_SD_IN_IDDR                    = iopad_i,    
            i_EN_IDDR                       = platform.request("FABRIC_EN_IDDR"),
            i_DIN_ODLY                      = platform.request("FABRIC_DIN"),
            o_DD_OUT_IDDR                   = Cat([platform.request(f"FABRIC_DD_OUT_{i}") for i in range(math.ceil(num_dly/2))]),
            o_DOUT_ODLY                     = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])          
            )
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_CLK_IN                        = clk_in,
            i_SD_IN_IDDR                    = iopad_i,    
            i_EN_IDDR                       = platform.request("FABRIC_EN_IDDR"),
            i_DIN_ODLY                      = platform.request("FABRIC_DIN"),
            o_DD_OUT_IDDR                   = Cat([platform.request(f"FABRIC_DD_OUT_{i}") for i in range(math.ceil(num_dly/2))]),
            o_DOUT_ODLY                     = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])          
            )
        
    ### I_DELAY_I_DDR+O_SERDES_O_DELAY ###
    elif (combination == "I_DELAY_I_DDR+O_SERDES_O_DELAY"):
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_SD_IN")
            iopad_o     = platform.request("IOPAD_SDATA_OUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_SD_IN_P")
            iopad_i_n   = platform.request("IOPAD_SD_IN_N")
            iopad_o_p   = platform.request("IOPAD_SDATA_OUT_P")
            iopad_o_n   = platform.request("IOPAD_SDATA_OUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_WIDTH                         = width,
            p_DATA_RATE                     = data_rate,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_SD_IN_IDDR                    = iopad_i,    
            i_EN_IDDR                       = platform.request("FABRIC_EN_IDDR"),
            o_DD_OUT_IDDR                   = Cat([platform.request(f"FABRIC_DD_OUT_{i}") for i in range(math.ceil(num_dly/2))]),
            i_PDATA_IN_OSERDES              = Cat([platform.request(f"FABRIC_PDATA_IN_{i}") for i in range(math.ceil(num_dly/2))]),           
            i_DATA_VALID_OSERDES            = platform.request("FABRIC_DATA_VALID"),                
            i_FAB_CLK_IN                    = platform.request("FABRIC_CLK_IN"),        
            i_OE_IN                         = platform.request("FABRIC_OE_IN"),
            o_SDATA_OUT_ODLY                = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])
            )
        
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
            
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_WIDTH                         = width,
            p_DATA_RATE                     = data_rate,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_CLK_IN                        = clk_in,
            i_SD_IN_IDDR                    = iopad_i,    
            i_EN_IDDR                       = platform.request("FABRIC_EN_IDDR"),
            o_DD_OUT_IDDR                   = Cat([platform.request(f"FABRIC_DD_OUT_{i}") for i in range(math.ceil(num_dly/2))]),
            i_PDATA_IN_OSERDES              = Cat([platform.request(f"FABRIC_PDATA_IN_{i}") for i in range(math.ceil(num_dly/2))]),           
            i_DATA_VALID_OSERDES            = platform.request("FABRIC_DATA_VALID"),                
            i_FAB_CLK_IN                    = platform.request("FABRIC_CLK_IN"),        
            i_OE_IN                         = platform.request("FABRIC_OE_IN"),
            o_SDATA_OUT_ODLY                = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])
            )
        
    ### I_DELAY_I_DDR+O_DDR_O_DELAY ###
    elif (combination == "I_DELAY_I_DDR+O_DDR_O_DELAY"):
        
        if (io_type == "SINGLE_ENDED"):
            iopad_i     = platform.request("IOPAD_SD_IN")
            iopad_o     = platform.request("IOPAD_SD_OUT")
            
        elif (io_type == "DIFFERENTIAL"):
            iopad_i_p   = platform.request("IOPAD_SD_IN_P")
            iopad_i_n   = platform.request("IOPAD_SD_IN_N")
            iopad_o_p   = platform.request("IOPAD_SD_OUT_P")
            iopad_o_n   = platform.request("IOPAD_SD_OUT_N")
            iopad_i     = Cat(iopad_i_p, iopad_i_n)
            iopad_o     = Cat(iopad_o_p, iopad_o_n)
        
        if (clocking_source == "LOCAL_OSCILLATOR"):
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_SD_IN_IDDR                    = iopad_i,     
            i_DD_IN_ODDR                    = Cat([platform.request(f"FABRIC_DD_IN_{i}") for i in range(math.ceil(num_dly/2))]),     
            i_EN_IDDR                       = platform.request("FABRIC_EN_IDDR"), 
            i_EN_ODDR                       = platform.request("FABRIC_EN_ODDR"), 
            o_DD_OUT_IDDR                   = Cat([platform.request(f"FABRIC_DD_OUT_{i}") for i in range(math.ceil(num_dly/2))]),
            o_SD_OUT_ODDR                   = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])
            )
        
        else:
            if (clocking == "RX_CLOCK"):
                clk_in = platform.request("IOPAD_CLK")
            elif (clocking == "PLL"):
                clk_in = platform.request("IOPAD_PLL_REF_CLK")
                
            # Module instance.
            # ----------------
            self.specials += Instance("DLY_CONFIG",
            # Parameters.
            # -----------
            p_IO_MODEL                      = combination,
            p_DELAY                         = delay,
            p_DLY_LOC                       = Instance.PreformattedParam("40'b{}".format(dly_loc)),
            p_NUM_DLY                       = num_dly,
            p_WEAK_KEEPER                   = io_mode,
            p_IOSTANDARD                    = voltage_standard,
            p_DRIVE_STRENGTH                = drive_strength,
            p_SLEW_RATE                     = slew_rate,
            p_DIFFERENTIAL_TERMINATION      = diff_termination,
            p_DLY_SEL_WIDTH                 = sel_dly,
            p_IO_TYPE                       = io_type,
            p_DELAY_TYPE                    = delay_type,
            p_PLL_MULT                      = pll_mult,
            p_PLL_DIV                       = pll_div,
            # Ports.
            # -----------
            i_CLK_IN                        = clk_in,
            i_SD_IN_IDDR                    = iopad_i,     
            i_DD_IN_ODDR                    = Cat([platform.request(f"FABRIC_DD_IN_{i}") for i in range(math.ceil(num_dly/2))]),     
            i_EN_IDDR                       = platform.request("FABRIC_EN_IDDR"), 
            i_EN_ODDR                       = platform.request("FABRIC_EN_ODDR"), 
            o_DD_OUT_IDDR                   = Cat([platform.request(f"FABRIC_DD_OUT_{i}") for i in range(math.ceil(num_dly/2))]),
            o_SD_OUT_ODDR                   = iopad_o,
            i_RESET                         = platform.request("FABRIC_RST"),
            i_SEL_DLY                       = platform.request("SEL_DLY"),
            i_DLY_LOAD                      = platform.request("FABRIC_DLY_LOAD"),
            i_DLY_ADJ                       = platform.request("FABRIC_DLY_ADJ"),
            i_DLY_INCDEC                    = platform.request("FABRIC_DLY_INCDEC"),
            o_DELAY_TAP_VALUE               = Cat([platform.request(f"FABRIC_DLY_TAP_VALUE_{i}") for i in range(num_dly)])
            )

# IO Configurator Wrapper ----------------------------------------------------------------------------------
class IO_CONFIG_Wrapper(Module):
    def __init__(self, platform, io_model, combination, io_type, io_mode, voltage_standard, delay, data_rate, op_mode, width, 
                clocking, clocking_source, out_clk_freq, ref_clk_freq, diff_termination, slew_rate, drive_strength, 
                clock_forwarding, delay_adjust, delay_type, clock_phase, num_idly, num_odly, num_dly, ports_file, bank_select):
        # Clocking ---------------------------------------------------------------------------------
        self.clock_domains.cd_sys  = ClockDomain()
        
        if (io_model == "I_BUF"):
            I_BUF(self, platform, io_type, io_mode, voltage_standard, diff_termination)
            
        elif (io_model == "O_BUF"):
            O_BUF(self, platform, io_type, io_mode, voltage_standard, diff_termination, slew_rate, drive_strength)
            
        elif (io_model in ["IO_DELAY"]):
            if (combination in ["I_DELAY", "I_DELAY_I_SERDES", "I_DELAY_I_DDR"]):
                if (num_idly > 1):
                    sel_dly = math.ceil(math.log2(num_idly))
                else:
                    sel_dly = 1
                I_DELAY(self, platform, sel_dly, io_model, combination, io_mode, voltage_standard, op_mode, data_rate, delay, delay_type, clocking, clocking_source, ref_clk_freq, out_clk_freq, num_idly, ports_file, width, bank_select, io_type, diff_termination)
            
            elif (combination in ["O_DELAY", "O_DELAY_O_SERDES", "O_DELAY_O_DDR"]):
                if (num_odly > 1):
                    sel_dly = math.ceil(math.log2(num_odly))
                else:
                    sel_dly = 1
                O_DELAY(self, platform, sel_dly, io_model, combination, io_mode, voltage_standard, slew_rate, drive_strength, delay, delay_type, clocking, clocking_source, ref_clk_freq, out_clk_freq, num_odly, width, data_rate, ports_file, bank_select, io_type, diff_termination)
            
            elif (combination in ["I_DELAY+O_DELAY", "I_DELAY+O_SERDES_O_DELAY", "I_DELAY+O_DDR_O_DELAY", 
                                "I_DELAY_I_SERDES+O_DELAY", "I_DELAY_I_SERDES+O_SERDES_O_DELAY", "I_DELAY_I_SERDES+O_DDR_O_DELAY",
                                "I_DELAY_I_DDR+O_DELAY", "I_DELAY_I_DDR+O_SERDES_O_DELAY", "I_DELAY_I_DDR+O_DDR_O_DELAY"]):
                sel_dly = sel_dly = math.ceil(math.log2(num_dly))
                Bidirectional_Delays(self, platform, sel_dly, combination, num_dly, io_type, io_mode, voltage_standard, diff_termination, slew_rate, drive_strength,
                                    delay, delay_type, ports_file, bank_select, clocking, out_clk_freq, ref_clk_freq, clocking_source, width, data_rate, op_mode)
            
        elif (io_model == "CLK_BUF"):
            CLK_BUF(self, platform, io_mode)
        
        elif (io_model == "I_DDR"):
            I_DDR(self, platform, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq, num_idly)
            
        elif (io_model == "I_SERDES"):
            I_SERDES(self, platform, data_rate, width, op_mode, io_type, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq, delay, delay_adjust, delay_type, num_idly)
        
        elif (io_model == "O_SERDES"):
            O_SERDES(self, platform, data_rate, width, clocking, clock_forwarding, clocking_source, ref_clk_freq, out_clk_freq, op_mode, io_mode, voltage_standard, drive_strength, slew_rate, delay, delay_adjust, delay_type, clock_phase, num_odly)
        
        elif (io_model == "O_DDR"):
            O_DDR(self, platform, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq, num_odly)
            
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
    rs_builder = IP_Builder(device="virgo", ip_name="io_configurator", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    core_string_param_group     = parser.add_argument_group(title="Core string parameters") # Core string value parameters.
    core_range_param_group      = parser.add_argument_group(title="Core range parameters")  # Core range value parameters.
    core_fix_param_group        = parser.add_argument_group(title="Core fix parameters")    # Core fix value parameters.
    
    core_string_param_group.add_argument("--io_model",                  type=str,   default="CLK_BUF",              choices=["CLK_BUF", "I_BUF", "IO_DELAY", "I_DDR", "I_SERDES", "O_BUF", "O_DDR", "O_SERDES"],                            help="Type of Model")
    core_string_param_group.add_argument("--direction",                 type=str,   default="UNIDIRECTIONAL",       choices=["UNIDIRECTIONAL", "BIDIRECTIONAL"],                                                                            help="Direction of Port")
    core_string_param_group.add_argument("--combination",               type=str,   default="I_DELAY",              choices=["I_DELAY", "I_DELAY_I_SERDES", "I_DELAY_I_DDR", "O_DELAY", "O_DELAY_O_SERDES", "O_DELAY_O_DDR",
                                                                                                                            "I_DELAY+O_DELAY", "I_DELAY+O_SERDES_O_DELAY", "I_DELAY+O_DDR_O_DELAY", 
                                                                                                                            "I_DELAY_I_SERDES+O_DELAY", "I_DELAY_I_SERDES+O_SERDES_O_DELAY", "I_DELAY_I_SERDES+O_DDR_O_DELAY",
                                                                                                                            "I_DELAY_I_DDR+O_DELAY", "I_DELAY_I_DDR+O_SERDES_O_DELAY", "I_DELAY_I_DDR+O_DDR_O_DELAY"],                      help="Multiple IO_DELAY Combinations")
    core_string_param_group.add_argument("--io_type",                   type=str,   default="SINGLE_ENDED",         choices=["SINGLE_ENDED", "DIFFERENTIAL", "TRI_STATE", "DIFF_TRI_STATE"],                                                help="Type of IO")
    core_string_param_group.add_argument("--io_mode",                   type=str,   default="NONE",                 choices=["NONE", "PULLUP", "PULLDOWN"],                                                                                 help="Input Configuration")
    core_string_param_group.add_argument("--voltage_standard",          type=str,   default="DEFAULT",              choices=["DEFAULT", "LVCMOS_12", "LVCMOS_15", "LVCMOS_18_HP", "LVCMOS_18_HR", "LVCMOS_25", "LVCMOS_33",
                                                                                                                            "LVTTL", "HSTL_I_12", "HSTL_II_12", "HSTL_I_15", "HSTL_II_15", "HSUL_12", "PCI66", "PCIX133", "POD_12",
                                                                                                                            "SSTL_I_15", "SSTL_II_15", "SSTL_I_18_HP", "SSTL_II_18_HP", "SSTL_I_18_HR", "SSTL_II_18_HR", "SSTL_I_25",
                                                                                                                            "SSTL_II_25", "SSTL_I_33", "SSTL_II_33"],                                                                       help="IO Voltage Standards")
    core_string_param_group.add_argument("--diff_termination",          type=str,   default="TRUE",                 choices=["TRUE", "FALSE"],                                                                                              help="Enable differential termination")
    core_string_param_group.add_argument("--slew_rate",                 type=str,   default="SLOW",                 choices=["SLOW", "FAST"],                                                                                               help="Transition rate for LVCMOS standards")
    core_fix_param_group.add_argument("--drive_strength",               type=int,   default=2,                      choices=[2, 4, 6, 8, 12, 16],                                                                                           help="Drive strength in mA for LVCMOS standards")
    core_string_param_group.add_argument("--bank_select",               type=str,   default="HR_1",                 choices=["HR_1", "HR_2", "HR_3", "HR_5", "HP_1", "HP_2"],                                                               help="Bank Selection for DELAY")
    core_range_param_group.add_argument ("--num_idly",                  type=int,   default=1,                      choices=range(1,41),                                                                                                    help="Number of input delays")
    core_range_param_group.add_argument ("--num_odly",                  type=int,   default=1,                      choices=range(1,41),                                                                                                    help="Number of output delays")
    core_fix_param_group.add_argument("--num_dly",                      type=int,   default=2,                      choices=[2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40],                                   help="Number of Bidirectional IO_DELAYs")
    core_string_param_group.add_argument("--data_rate",                 type=str,   default="SDR",                  choices=["SDR"],                                                                                                        help="Data Rate")
    core_string_param_group.add_argument("--op_mode",                   type=str,   default="NONE",                 choices=["NONE", "DPA", "CDR"],                                                                                         help="Dynamic Phase Alignment or Clock Data Recovery")
    core_string_param_group.add_argument("--clocking",                  type=str,   default="RX_CLOCK",             choices=["RX_CLOCK", "PLL"],                                                                                            help="Clocking option for I_SERDES")
    core_string_param_group.add_argument("--clocking_source",           type=str,   default="RX_IO_CLOCK",          choices=["RX_IO_CLOCK", "LOCAL_OSCILLATOR"],                                                                            help="Clocking Source for PLL")
    core_string_param_group.add_argument("--clock_forwarding",          type=str,   default="FALSE",                choices=["TRUE", "FALSE"],                                                                                              help="Clock forwarding for O_SERDES")
    core_string_param_group.add_argument("--delay_adjust",              type=str,   default="TRUE",                 choices=["TRUE", "FALSE"],                                                                                              help="Data delay adjustment for SERDES")
    core_string_param_group.add_argument("--delay_type",                type=str,   default="STATIC",               choices=["STATIC", "DYNAMIC"],                                                                                          help="Delay type static/dynamic")
    core_string_param_group.add_argument("--clock_phase",               type=str,   default="0",                    choices=["0", "90", "180", "270"],                                                                                      help="Clock Phase 0,90,180,270")
    core_range_param_group.add_argument("--delay",                      type=int,   default=0,                      choices=range(0,64),                                                                                                    help="Tap Delay Value")
    core_range_param_group.add_argument("--width",                      type=int,   default=4,                      choices=range(3,11),                                                                                                    help="Width of Serialization/Deserialization")
    core_range_param_group.add_argument("--out_clk_freq",               type=int,   default=1600,                   choices=range(800,3201),                                                                                                help="Output clock frequency in MHz")
    core_range_param_group.add_argument("--ref_clk_freq",               type=int,   default=50,                     choices=range(5, 1201),                                                                                                 help="Reference clock frequency in MHz")
    
    # Core file path parameters.
    core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    core_file_path_group.add_argument("--ports_file",                   type=str,    default="",                    help="Path to Ports file(.txt)")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",                    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                           help="Build Directory")
    build_group.add_argument("--build-name",    default="io_configurator",              help="Build Folder Name, Build RTL File Name and Module Name")
    build_group.add_argument("--device",        default="",                             help="Device")
    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name'          : 'IO_CONFIGURATOR',
    'Version'       : 'V1_0',
    'Interface'     : 'Native',
    'Description'   : 'IO_Configurator is a native interface IP. It allows user to generate IO Primitives with configurable parameters.'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.img_name(args.io_model, file_path)  

        device = args.device
        parser._actions[30].default = [str(args.device)]
        
        if (args.io_type == "DIFFERENTIAL"):
            parser._actions[11].choices = range(1,21)
            parser._actions[12].choices = range(1,21)
            parser._actions[13].choices = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        
        if (device not in ["1VG28"]):
            parser._actions[1].choices = ["CLK_BUF", "I_BUF", "I_DDR", "I_SERDES", "O_BUF", "O_DDR", "O_SERDES"]
        
        if (args.direction != "BIDIRECTIONAL"):
            option_strings_to_remove = ["--num_dly"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        else:
            option_strings_to_remove = ["--num_idly", "--num_odly"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        # if (args.io_type not in ["DIFFERENTIAL"]):
        #     option_strings_to_remove = ["--diff_termination"]
        #     parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.voltage_standard not in ["LVCMOS_12", "LVCMOS_15", "LVCMOS_18_HP", "LVCMOS_18_HR", "LVCMOS_25", "LVCMOS_33"]):
            option_strings_to_remove = ["--slew_rate", "--drive_strength"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.clock_forwarding == "TRUE"):
            option_strings_to_remove = ["--delay_adjust", "--delay", "--delay_type"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.delay_adjust == "FALSE"):
            option_strings_to_remove = ["--delay", "--delay_type"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.io_type in ["DIFFERENTIAL", "DIFF_TRI_STATE"]):
            parser._actions[6].choices = ["DEFAULT", "BLVDS_DIFF", "LVDS_HP_DIFF", "LVDS_HR_DIFF", "LVPECL_25_DIFF", "LVPECL_33_DIFF", 
                                        "HSTL_12_DIFF", "HSTL_15_DIFF", "HSUL_12_DIFF", "MIPI_DIFF", "POD_12_DIFF", "RSDS_DIFF", "SLVS_DIFF", 
                                        "SSTL_15_DIFF", "SSTL_18_HP_DIFF", "SSTL_18_HR_DIFF"]
        
        if (args.io_type not in ["DIFFERENTIAL", "DIFF_TRI_STATE"]):
                option_strings_to_remove = ["--diff_termination"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.io_model == "I_BUF"):
            option_strings_to_remove = ["--ports_file", "--direction", "--combination", "--num_idly", "--num_odly", "--delay_type", "--bank_select",
                                        "--clock_phase", "--delay_adjust", "--delay_type", "--clock_forwarding", "--slew_rate", "--drive_strength", 
                                        "--data_rate", "--op_mode", "--delay", "--width", "--clocking", "--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            parser._actions[2].choices = ["SINGLE_ENDED", "DIFFERENTIAL"]
        
        elif (args.io_model == "O_BUF"):
            option_strings_to_remove = ["--ports_file", "--direction", "--combination", "--num_idly", "--num_odly", "--delay_type", "--bank_select", "--clock_phase",
                                        "--delay_adjust", "--delay_type", "--clock_forwarding", "--data_rate", "--op_mode", "--delay", "--width", "--clocking", 
                                        "--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.io_type in ["SINGLE_ENDED", "DIFFERENTIAL"]):
                option_strings_to_remove = ['--io_mode']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        elif (args.io_model in ["IO_DELAY"]):
            option_strings_to_remove = ["--clock_phase", "--delay_adjust", "--clock_forwarding"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            parser._actions[4].choices = ["SINGLE_ENDED", "DIFFERENTIAL"]
            
            if (args.direction == "UNIDIRECTIONAL"):
                parser._actions[3].choices = ["I_DELAY", "I_DELAY_I_SERDES", "I_DELAY_I_DDR", "O_DELAY", "O_DELAY_O_SERDES", "O_DELAY_O_DDR"]
            elif (args.direction == "BIDIRECTIONAL"):
                parser._actions[3].default = "I_DELAY+O_DELAY"
                parser._actions[3].choices = ["I_DELAY+O_DELAY", "I_DELAY+O_SERDES_O_DELAY", "I_DELAY+O_DDR_O_DELAY", 
                                            "I_DELAY_I_SERDES+O_DELAY", "I_DELAY_I_SERDES+O_SERDES_O_DELAY", "I_DELAY_I_SERDES+O_DDR_O_DELAY",
                                            "I_DELAY_I_DDR+O_DELAY", "I_DELAY_I_DDR+O_SERDES_O_DELAY", "I_DELAY_I_DDR+O_DDR_O_DELAY"]
            
            if (args.combination not in ["O_DELAY", "O_DELAY_O_SERDES", "O_DELAY_O_DDR", "I_DELAY+O_DELAY", "I_DELAY+O_SERDES_O_DELAY", "I_DELAY+O_DDR_O_DELAY", 
                                        "I_DELAY_I_SERDES+O_DELAY", "I_DELAY_I_SERDES+O_SERDES_O_DELAY", "I_DELAY_I_SERDES+O_DDR_O_DELAY",
                                        "I_DELAY_I_DDR+O_DELAY", "I_DELAY_I_DDR+O_SERDES_O_DELAY", "I_DELAY_I_DDR+O_DDR_O_DELAY"]):
                option_strings_to_remove = ["--drive_strength", "--slew_rate"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]

            if (args.clocking == "RX_CLOCK"):
                option_strings_to_remove = ["--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking_source == "LOCAL_OSCILLATOR"):
                option_strings_to_remove = ["--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.combination not in ["I_DELAY_I_SERDES"]):
                option_strings_to_remove = ["--op_mode"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.combination not in ["I_DELAY_I_SERDES", "O_DELAY_O_SERDES"]):
                option_strings_to_remove = ["--data_rate", "--width"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                
            if (args.combination in ["I_DELAY", "I_DELAY_I_SERDES", "I_DELAY_I_DDR"]):
                option_strings_to_remove = ["--num_odly"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            elif (args.combination in ["O_DELAY", "O_DELAY_O_SERDES", "O_DELAY_O_DDR"]):
                option_strings_to_remove = ["--num_idly"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                
        elif (args.io_model in ["I_DDR", "O_DDR"]):
            option_strings_to_remove = ["--ports_file", "--direction", "--combination", "--num_idly", "--num_odly", "--delay_type", "--bank_select", "--clock_phase",
                                        "--delay_adjust", "--delay_type","--clock_forwarding", "--slew_rate", "--drive_strength", "--diff_termination", "--delay", 
                                        "--io_type", "--voltage_standard", "--data_rate", "--op_mode", "--width"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking == "RX_CLOCK"):
                option_strings_to_remove = ["--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking_source == "LOCAL_OSCILLATOR"):
                option_strings_to_remove = ["--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        elif (args.io_model in ["CLK_BUF"]):
            option_strings_to_remove = ["--ports_file", "--direction", "--combination", "--num_idly", "--num_odly", "--delay_type", "--bank_select", "--clock_phase",
                                        "--delay_adjust", "--delay_type","--clock_forwarding", "--slew_rate", "--drive_strength", "--diff_termination", "--delay",
                                        "--io_type", "--voltage_standard", "--data_rate", "--op_mode", "--width", "--clocking", "--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        elif (args.io_model in ["I_SERDES", "O_SERDES"]):
            
            option_strings_to_remove = ["--ports_file", "--direction", "--combination", "--num_idly", "--num_odly", "--delay_type", "--bank_select", "--voltage_standard", "--slew_rate"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.clock_forwarding == "FALSE"):
                option_strings_to_remove = ["--clock_phase"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.io_model == "O_SERDES"):
                option_strings_to_remove = ["--op_mode"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.io_model == "I_SERDES"):
                option_strings_to_remove = ["--clock_forwarding"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.voltage_standard not in ["LVCMOS_12", "LVCMOS_15", "LVCMOS_18_HP", "LVCMOS_18_HR", "LVCMOS_25", "LVCMOS_33"]):
                option_strings_to_remove = ["--slew_rate", "--drive_strength"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.clock_forwarding == "FALSE"):
                option_strings_to_remove = ["--voltage_standard"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                
            option_strings_to_remove = ["--diff_termination", "--io_type"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking == "RX_CLOCK"):
                option_strings_to_remove = ["--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking_source == "LOCAL_OSCILLATOR"):
                option_strings_to_remove = ["--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
    summary =  {  
    "IO_MODEL": args.io_model
    }
    
    # IO_TYPE: NONE/PULLUP/PULLDOWN
    if (args.io_model != "O_BUF"):
        if (args.io_mode == "NONE"):
            summary["IO_MODE"] = "No internal pull-up or pull-down resistor enabled"
        elif (args.io_mode == "PULLUP"):
            summary["IO_MODE"] = "Logic high in the absence of an external connection"
        elif (args.io_mode == "PULLDOWN"):
            summary["IO_MODE"] = "Logic low in the absence of an external connection"
    
    if (args.io_model in ["I_SERDES", "O_SERDES", "I_DDR", "O_DDR", "I_DELAY", "O_DELAY"]):
    # CLOCK
        if (args.clocking == "RX_CLOCK"):
            summary["CLOCK"] = "IOPAD provides the clock signal"
        elif (args.clocking == "PLL"):
            if (args.clocking_source == "LOCAL_OSCILLATOR"):
                summary["LOCAL_OSCILLATOR"] = "40 MHz"
                summary["OUTPUT_CLOCK_FREQUENCY"] = str(args.out_clk_freq) + " MHz"
                summary["CLOCK"] = "Local Oscillator clock feeds into a PLL"
            elif (args.clocking_source == "RX_IO_CLOCK"):
                summary["INPUT_CLOCK_FREQUENCY"] = str(args.ref_clk_freq) + " MHz"
                summary["OUTPUT_CLOCK_FREQUENCY"] = str(args.out_clk_freq) + " Mhz"
                summary["CLOCK"] = "User-defined IOPAD clock feeds a PLL"
    
    if (args.io_model in ["I_BUF", "O_BUF"]):
        if (args.io_type == "SINGLE_ENDED"):
            summary["IO_TYPE"] = "Unidirectional data flow"
        elif (args.io_type == "DIFFERENTIAL"):
            summary["IO_TYPE"] = "Noise-resistant data transfer"
        elif (args.io_type == "TRI_STATE"):
            summary["IO_TYPE"] = "Extended control for high-impedance state"
        elif (args.io_type == "DIFF_TRI_STATE"):
            summary["IO_TYPE"] = "Differential signaling and extended control for high-impedance state"
    
    if (args.io_model in ["I_BUF", "O_BUF"]):
        summary["VOLTAGE_STANDARD"] = args.voltage_standard
    
    elif (args.io_model in ["I_SERDES", "O_SERDES"]):
        # DATA_RATE
        if (args.data_rate == "SDR"):
            summary["DATA_RATE"] = "Transfering data on one clock cycle"
        elif (args.data_rate == "DDR"):
            summary["DATA_RATE"] = "Transfering data on both rising and falling edges of the clock cycle"
        
        # OP_MODE
        if (args.op_mode == "DPA"):
            summary["OPERATION"] = "Dynamic Phase Alignment"
        elif (args.op_mode == "CDR"):
            summary["OPERATION"] = "Clock Data Recovery"
        elif (args.op_mode == "MIPI"):
            summary["OPERATION"] = "Mobile Industry Processor Interface"
        
        # CLOCK_FORWARDING
        if (args.io_model == "O_SERDES"):
            summary["CLOCK_FORWARDING"] = args.clock_forwarding
        
    elif (args.io_model in ["I_DELAY", "I_DELAY_I_SERDES", "I_DELAY_I_DDR", "O_DELAY", "O_DELAY_O_SERDES", "O_DELAY_O_DDR"]):
        summary["TAP_DELAY_VALUE"] = args.delay
    
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
        
    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device=args.device) # device needs to be fixed
    module   = IO_CONFIG_Wrapper(platform,
        io_model                        = args.io_model,
        combination                     = args.combination,
        io_type                         = args.io_type,
        io_mode                         = args.io_mode,
        voltage_standard                = args.voltage_standard,
        delay                           = args.delay,
        data_rate                       = args.data_rate,
        op_mode                         = args.op_mode,
        width                           = args.width,
        clocking                        = args.clocking,
        clocking_source                 = args.clocking_source,
        out_clk_freq                    = args.out_clk_freq,
        ref_clk_freq                    = args.ref_clk_freq,
        diff_termination                = args.diff_termination,
        slew_rate                       = args.slew_rate,
        drive_strength                  = args.drive_strength,
        clock_forwarding                = args.clock_forwarding,
        delay_adjust                    = args.delay_adjust,
        delay_type                      = args.delay_type,
        clock_phase                     = args.clock_phase,
        num_idly                        = args.num_idly,
        num_odly                        = args.num_odly,
        num_dly                         = args.num_dly,
        ports_file                      = args.ports_file,
        bank_select                     = args.bank_select
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
        
        header_path = os.path.join(args.build_dir, "rapidsilicon", "ip", "io_configurator", "v1_0", args.build_name, "src", "header.vh")
        defines     = []
        # clocking options defines
        if (args.clocking == "RX_CLOCK"):
            defines.append("`define RX_CLOCK\n")
        elif(args.clocking == "PLL"):
            defines.append("`define PLL\n")
            if (args.clocking_source == "LOCAL_OSCILLATOR"):
                defines.append("`define LOCAL_OSCILLATOR\n")
            elif (args.clocking_source == "RX_IO_CLOCK"):
                defines.append("`define RX_IO_CLOCK\n")
        
        # io models defines
        if (args.direction == "UNIDIRECTIONAL"):
            defines.append("`define unidirectional\n")
            if (args.combination == "I_DELAY"):
                defines.append("`define I_DELAY\n")
                
            elif (args.combination == "I_DELAY_I_SERDES"):
                defines.append("`define I_DELAY_I_SERDES\n")
                
            elif (args.combination == "I_DELAY_I_DDR"):
                defines.append("`define I_DELAY_I_DDR\n")
                
            elif (args.combination == "O_DELAY"):
                defines.append("`define O_DELAY\n")
                
            elif (args.combination == "O_DELAY_O_SERDES"):
                defines.append("`define O_SERDES_O_DELAY\n")
                
            elif (args.combination == "O_DELAY_O_DDR"):
                defines.append("`define O_DDR_O_DELAY\n")
                
        elif (args.direction == "BIDIRECTIONAL"):
            defines.append("`define bidirectional\n")
            if (args.combination == "I_DELAY+O_DELAY"):
                defines.append("`define I_DELAY_O_DELAY\n")
            
            elif (args.combination == "I_DELAY+O_SERDES_O_DELAY"):
                defines.append("`define I_DELAY_O_DELAY_O_SERDES\n")
                
            elif (args.combination == "I_DELAY+O_DDR_O_DELAY"):
                defines.append("`define I_DELAY_O_DELAY_O_DDR\n")
                
            elif (args.combination == "I_DELAY_I_SERDES+O_DELAY"):
                defines.append("`define I_DELAY_I_SERDES_O_DELAY\n")
                
            elif (args.combination == "I_DELAY_I_SERDES+O_SERDES_O_DELAY"):
                defines.append("`define I_DELAY_I_SERDES_O_DELAY_O_SERDES\n")
                
            elif (args.combination == "I_DELAY_I_SERDES+O_DDR_O_DELAY"):
                defines.append("`define I_DELAY_I_SERDES_O_DELAY_O_DDR\n")
                
            elif (args.combination == "I_DELAY_I_DDR+O_DELAY"):
                defines.append("`define I_DELAY_I_DDR_O_DELAY\n")
                
            elif (args.combination == "I_DELAY_I_DDR+O_SERDES_O_DELAY"):
                defines.append("`define I_DELAY_I_DDR_O_DELAY_O_SERDES\n")
                
            elif (args.combination == "I_DELAY_I_DDR+O_DDR_O_DELAY"):
                defines.append("`define I_DELAY_I_DDR_O_DELAY_O_DDR\n")
        
        # io type defines
        if (args.io_type == "SINGLE_ENDED"):
            defines.append("`define SINGLE_ENDED")
        elif (args.io_type == "DIFFERENTIAL"):
            defines.append("`define DIFFERENTIAL")
        
        with open(os.path.join(header_path), "w") as file:
            file.writelines(defines)

        wrapper     = os.path.join(args.build_dir, "rapidsilicon", "ip", "io_configurator", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines   = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    # IP Parameters
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"IO\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(\n".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    main()