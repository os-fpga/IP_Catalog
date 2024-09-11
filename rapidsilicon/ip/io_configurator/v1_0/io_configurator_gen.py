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
        ("IOPAD_CLK",                   0, Pins(1)),
        ("FABRIC_RX_RST",               0, Pins(num_idly)),
        ("FABRIC_BITSLIP_ADJ",          0, Pins(num_idly)),
        ("FABRIC_EN",                   0, Pins(num_idly)),
        ("FABRIC_CLK_IN",               0, Pins(1)),
        ("FABRIC_CLK_OUT",              0, Pins(num_idly)),
        # ("FABRIC_Q",                    0, Pins(width*num_idly)),
        ("FABRIC_DATA_VALID",           0, Pins(num_idly)),
        ("FABRIC_DPA_LOCK",             0, Pins(num_idly)),
        ("FABRIC_DPA_ERROR",            0, Pins(num_idly)),
        ("IOPAD_PLL_REF_CLK",           0, Pins(1)),
        ("FABRIC_DLY_LOAD",             0, Pins(1)),
        ("FABRIC_DLY_ADJ",              0, Pins(1)),
        ("FABRIC_DLY_INCDEC",           0, Pins(1)),
        ("FABRIC_CLK_IN",               0, Pins(1)),
        ("FABRIC_DLY_TAP_VALUE",        0, Pins(6)),
        ("FABRIC_PDATA",                0, Pins(width))
    ] + [
        (f"FABRIC_PDATA_{i}", i, Pins(width)) for i in range(num_idly)
    ]

def get_oserdes_ios(width):
    return [
        ("IOPAD_CLK",               0, Pins(1)),
        ("FABRIC_D",                0, Pins(width)),
        ("FABRIC_RST",              0, Pins(1)),
        ("FABRIC_LOAD_WORD",        0, Pins(1)),
        ("FABRIC_CLK_IN",           0, Pins(1)),
        ("FABRIC_OE_IN",            0, Pins(1)),
        # ("CHANNEL_BOND_SYNC_IN",    0, Pins(1)),
        # ("CHANNEL_BOND_SYNC_OUT",   0, Pins(1)),
        ("IOPAD_Q",                 0, Pins(1)),
        ("IOPAD_CLK_OUT",           0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",       0, Pins(1)),
        ("LO_CLK",                  0, Pins(1)),
        
        ("FABRIC_DLY_LOAD",        0, Pins(1)),
        ("FABRIC_DLY_ADJ",         0, Pins(1)),
        ("FABRIC_DLY_INCDEC",      0, Pins(1)),
        ("FABRIC_DLY_TAP_VALUE",   0, Pins(6))
    ]
    
def get_iddr_ios(num_idly):
    return [
        ("IOPAD_D",             0, Pins(1)),
        ("FABRIC_RST",          0, Pins(1)),
        ("FABRIC_EN",           0, Pins(num_idly)),
        ("FABRIC_Q",            0, Pins(num_idly)),
        ("IOPAD_CLK",           0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",   0, Pins(1))
    ]

def get_odelay_ios():
    return [
        ("FABRIC_I",               0, Pins(1)),
        ("FABRIC_DLY_LOAD",        0, Pins(1)),
        ("FABRIC_DLY_ADJ",         0, Pins(1)),
        ("FABRIC_DLY_INCDEC",      0, Pins(1)),
        ("FABRIC_DLY_TAP_VALUE",   0, Pins(6)),
        ("FABRIC_CLK_IN",          0, Pins(1)),
        ("IOPAD_O",                0, Pins(1)),
        ("IOPAD_CLK",              0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",      0, Pins(1))
    ]

def get_oddr_ios():
    return [
        ("FABRIC_D",            0, Pins(2)),
        ("FABRIC_R",            0, Pins(1)),
        ("FABRIC_E",            0, Pins(1)),
        ("IOPAD_Q",             0, Pins(1)),
        ("IOPAD_CLK",           0, Pins(1)),
        ("IOPAD_PLL_REF_CLK",   0, Pins(1))
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
            product_candidate = 2 * (a / b)
            # Check if the candidate product matches the formula with c and d
            if product_candidate == ((c+1) / (d+1)):
                # If a match is found, assign c, d, and the product to the respective signals
                pll_mult = c + 1
                pll_div  = d + 1
                return pll_mult, pll_div

def ports_file(ports_file_path):
    if (ports_file_path == ""):
        return 0
    else:
        ports = []
        # Open the text file in read mode
        with open(ports_file_path, 'r') as file:
            # Read each line in the file
            for line in file:
                # Strip any leading/trailing whitespace (like newline characters) and append to the list
                ports.append(line.strip())
        
        ports = [int(name.split("_")[2]) for name in ports]
        
        bits_high = 0
        for bit in ports:
            bits_high |= (1 << bit) # making bits high depending upon bit number
            
        binary_dly_loc = bin(bits_high)[2:] # removing 0b from binary string
        
        if (len(binary_dly_loc) < 40):
            binary_dly_loc = binary_dly_loc.zfill(40) # appending zeros to remaining bits on MSB
        else:
            binary_dly_loc = binary_dly_loc
            
        dly_loc = binary_dly_loc[20:] + binary_dly_loc[:20] # swapped bits
        
        # for name in ports:
        #     # Extract the number from the name (e.g., 'signal_5' -> 5)
        #     num = int(name.split("_")[-1])
        # print(extracted_numbers)
            # rotated_ports = ports[::-1] # rotated whole list
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
            # p_IOSTANDARD  = voltage_standard,
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
            # p_IOSTANDARD                = voltage_standard,
            # p_DIFFERENTIAL_TERMINATION  = diff_termination,
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
            # p_IOSTANDARD                = voltage_standard,
            # p_DRIVE_STRENGTH            = drive_strength,
            # p_SLEW_RATE                 = slew_rate,
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
            # p_IOSTANDARD                = voltage_standard,
            # p_DIFFERENTIAL_TERMINATION  = diff_termination,
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
            # p_IOSTANDARD                = voltage_standard,
            # p_DRIVE_STRENGTH            = drive_strength,
            # p_SLEW_RATE                 = slew_rate,
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
            # p_IOSTANDARD                = voltage_standard,
            # p_DIFFERENTIAL_TERMINATION  = diff_termination,
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
def I_DELAY(self, platform, io_model, io_mode, op_mode, data_rate, delay, delay_type, clocking, clocking_source, ref_clk_freq, out_clk_freq, num_idly, cntrl, ports_file_path, width):
    platform.add_extension(get_idelay_ios(num_idly))
    
    
    self.i          = Signal(num_idly*1)
    self.clk        = Signal(1)
    self.clk_1      = Signal(1)
    self.open       = Signal(6)
    self.lo_clk     = Signal(1)
    self.pll_clk    = Signal(1)
    self.pll_lock   = Signal(1)
    
    if (clocking == "RX_CLOCK"):
        clock_out   = self.clk_1
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
            o_O     = self.clk
        )
        # Module instance.
        # ----------------
        self.specials += Instance("CLK_BUF",
            # Ports
            #------
            i_I     = self.clk,
            o_O     = clock_out
        )
    
    elif (clocking == "PLL"):
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
        clock_out = self.pll_clk
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
                p_PLL_POST_DIV          = 2,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.lo_clk,
                o_CLK_OUT           = clock_out,          
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
                p_PLL_POST_DIV          = 2,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.clk_1,
                o_CLK_OUT           = clock_out,           
                o_LOCK              = self.pll_lock
            )
    
    # Parameter
    ADDR_WIDTH          = 5
    DLY_TAP_WIDTH       = 6
    
    # user selection signals
    usr_dly_ld             = Signal(num_idly)
    usr_dly_adj            = Signal(num_idly)
    usr_dly_incdec         = Signal(num_idly)
    usr_dly_tap_value_out  = Signal(DLY_TAP_WIDTH*num_idly)
    
    idly_out       = Signal(num_idly)
    f2g_dly_addr   = Signal(ADDR_WIDTH*cntrl)
    g2f_rx_dly_tap = Signal(DLY_TAP_WIDTH*cntrl)
    dly_tap_value  = Signal(DLY_TAP_WIDTH*num_idly)
    
    # controller output signals
    cntrl_dly_ld       = Signal(cntrl)
    cntrl_dly_adj      = Signal(cntrl)
    cntrl_dly_incdec   = Signal(cntrl)   
    
    # wires for controller to delays
    delay_ld        = Signal(num_idly) 
    delay_adj       = Signal(num_idly) 
    delay_incdec    = Signal(num_idly) 
    dly_ld          = platform.request("FABRIC_DLY_LOAD")
    
    if (delay_type == "STATIC"):
        dly_adj            = 0
        dly_incdec         = 0
    
    elif (delay_type == "DYNAMIC"):
        dly_adj            = platform.request("FABRIC_DLY_ADJ")
        dly_incdec         = platform.request("FABRIC_DLY_INCDEC")
    
    
    # mux_dly_tap   = {}
    if (num_idly > 1):
        rst         = platform.request("FABRIC_RST")
        sel_dly     = platform.request("SEL_DLY")
        for i in range(num_idly):
            dly_tap_val       = platform.request(f"FABRIC_DLY_TAP_VALUE_{i}")
            self.comb        += dly_tap_val.eq(usr_dly_tap_value_out[(i*6):(i*6)+6])
    else:
        dly_tap_val       = platform.request("FABRIC_DLY_TAP_VALUE")
        # self.comb        += dly_tap_val.eq(dly_tap_value)
    
    if (num_idly > 1):
        # MUX generation
        if (delay_type == "STATIC"):
            # Module instance.
            # ----------------
            self.specials += Instance("muxp", name="dly_load_mux",
                # Parameters.
                # -----------
                p_DWIDTH        = num_idly,
                p_NUM_OF_BUS    = num_idly,
                # Ports
                #------
                i_d             = dly_ld,
                i_sel           = sel_dly,
                o_dout          = usr_dly_ld
            )
            #     mux_ld[i]         = usr_dly_ld[i].eq(dly_ld[i])
            # self.comb += Case(sel_dly, mux_ld)

        elif (delay_type == "DYNAMIC"):
            # Module instance.
            # ----------------
            self.specials += Instance("muxp", name="dly_load_mux",
                # Parameters.
                # -----------
                p_DWIDTH        = num_idly,
                p_NUM_OF_BUS    = num_idly,
                # Ports
                #------
                i_d             = dly_ld,
                i_sel           = sel_dly,
                o_dout          = usr_dly_ld
            )

            # Module instance.
            # ----------------
            self.specials += Instance("muxp", name="dly_adj_mux",
                # Parameters.
                # -----------
                p_DWIDTH        = num_idly,
                p_NUM_OF_BUS    = num_idly,
                # Ports
                #------
                i_d             = dly_adj,
                i_sel           = sel_dly,
                o_dout          = usr_dly_adj
            )
        
            # Module instance.
            # ----------------
            self.specials += Instance("muxp", name="dly_incdec_mux",
                # Parameters.
                # -----------
                p_DWIDTH        = num_idly,
                p_NUM_OF_BUS    = num_idly,
                # Ports
                #------
                i_d             = dly_incdec,
                i_sel           = sel_dly,
                o_dout          = usr_dly_incdec
            )
            
        # print()
        # for i in range(num_idly):
        #     mux_ld[i]         = usr_dly_ld[i].eq(dly_ld[i])
        #     mux_adj[i]        = usr_dly_adj[i].eq(dly_adj[i])
        #     mux_incdec[i]     = usr_dly_incdec[i].eq(dly_incdec[i])
        # self.comb += Case(sel_dly, mux_ld)
        # self.comb += Case(sel_dly, mux_adj)
        # self.comb += Case(sel_dly, mux_incdec)
    
    
    
    dly_loc = ports_file(ports_file_path)
    
    if (num_idly > 1):
        
        
        cntrl_num_dly = num_idly
        for j in range(cntrl):

            # this will work for max 20 delays
            if (cntrl_num_dly > 20):
                cntrl_num_dly = 20
            else:
                cntrl_num_dly = num_idly - 20 * (j)

            # Module instance.
            # ----------------
            self.specials += Instance("muxp",
                # Parameters.
                # -----------
                p_DWIDTH        = DLY_TAP_WIDTH,
                p_NUM_OF_BUS    = cntrl_num_dly,
                # Ports
                #------
                i_d             = dly_tap_value[(j*120):(j*120)+120],
                i_sel           = f2g_dly_addr[(j*6):(j*6)+6],
                o_dout          = g2f_rx_dly_tap[(j*6):(j*6)+6]
            )

            # Module instance.
            # ----------------
            self.specials += Instance("one2x_decoder", name = "load_decoder",
                # Parameters.
                # -----------
                p_DWIDTH        = 1,
                p_NUM_OF_OBUS   = cntrl_num_dly,
                # Ports
                #------
                i_din           = cntrl_dly_ld[j],
                i_sel           = f2g_dly_addr[(j*6):(j*6)+6],
                o_dout          = delay_ld[(j*20):(j*20)+20]
            )

            # Module instance.
            # ----------------
            self.specials += Instance("one2x_decoder", name = "adj_decoder",
                # Parameters.
                # -----------
                p_DWIDTH        = 1,
                p_NUM_OF_OBUS   = cntrl_num_dly,
                # Ports
                #------
                i_din           = cntrl_dly_adj[j],
                i_sel           = f2g_dly_addr[(j*6):(j*6)+6],
                o_dout          = delay_adj[(j*20):(j*20)+20]
            )

            # Module instance.
            # ----------------
            self.specials += Instance("one2x_decoder", name = "incdec_decoder",
                # Parameters.
                # -----------
                p_DWIDTH        = 1,
                p_NUM_OF_OBUS   = cntrl_num_dly,
                # Ports
                #------
                i_din           = cntrl_dly_incdec[j],
                i_sel           = f2g_dly_addr[(j*6):(j*6)+6],
                o_dout          = delay_incdec[(j*20):(j*20)+20]
            )

            # Module instance.
            # ----------------
            self.specials += Instance("DLY_ADDR_CNTRL",
                # Parameters.
                # -----------
                p_DLY_LOC               = Instance.PreformattedParam("20'b{}".format(dly_loc[(j*20):(j*20)+20])),
                p_NUM_DLY               = cntrl_num_dly,
                p_DLY_TAP_WIDTH         = DLY_TAP_WIDTH ,
                p_ADDR_WIDTH            = ADDR_WIDTH,
                # Ports
                #------
                i_rst                   = rst,
                i_cntrl_dly_tap_value   = g2f_rx_dly_tap[(j*6):(j*6)+6],            
                i_usr_dly_incdec        = usr_dly_incdec[(j*20):(j*20)+20],        
                i_usr_dly_ld            = usr_dly_ld[(j*20):(j*20)+20],    
                i_usr_dly_adj           = usr_dly_adj[(j*20):(j*20)+20],    
                i_usr_rd_dly_value      = 0,        
                o_f2g_dly_addr          = f2g_dly_addr[(j*6):(j*6)+6],  
                o_cntrl_dly_incdec      = cntrl_dly_incdec[j],    
                o_cntrl_dly_ld          = cntrl_dly_ld[j],
                o_cntrl_dly_adj         = cntrl_dly_adj[j],  
                o_usr_dly_tap_value_out = usr_dly_tap_value_out[(j*120):(j*120)+120]
            )
        
    if (io_model == "I_DELAY"): 
        iopad_i     = platform.request("IOPAD_DATA_IN")
        fabric_o    = platform.request("FABRIC_DATA_OUT")
        
        if (num_idly > 1):
            for i in range(num_idly):
                # Module instance.
                # ----------------
                self.specials += Instance("I_BUF",
                    # Parameters.
                    # -----------
                    p_WEAK_KEEPER = io_mode,
                    # Ports
                    #------
                    i_I     = iopad_i[i],
                    i_EN    = 1,
                    o_O     = self.i[i]
                )
                # Module instance.
                # ----------------
                self.specials += Instance("I_DELAY",
                    # Parameters.
                    # -----------
                    p_DELAY             = delay,
                    # Ports
                    #------
                    i_I                 = self.i[i],
                    i_DLY_LOAD          = delay_ld[i],
                    i_DLY_ADJ           = delay_adj[i],
                    i_DLY_INCDEC        = delay_incdec[i],
                    i_CLK_IN            = clock_out,
                    o_DLY_TAP_VALUE     = dly_tap_value[(i*6):(i*6)+6],
                    o_O                 = fabric_o[i]
                )
        else:
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF",
                # Parameters.
                # -----------
                p_WEAK_KEEPER = io_mode,
                # Ports
                #------
                i_I     = iopad_i,
                i_EN    = 1,
                o_O     = self.i
            )
            # Module instance.
            # ----------------
            self.specials += Instance("I_DELAY",
                # Parameters.
                # -----------
                p_DELAY             = delay,
                # Ports
                #------
                i_I                 = self.i,
                i_DLY_LOAD          = dly_ld,
                i_DLY_ADJ           = dly_adj,
                i_DLY_INCDEC        = dly_incdec,
                i_CLK_IN            = clock_out,
                o_DLY_TAP_VALUE     = dly_tap_val,
                o_O                 = fabric_o
            )
            
            
    elif (io_model == "I_DELAY+I_SERDES"):
        platform.add_extension(get_iserdes_ios(width, num_idly))
        iopad_i         = platform.request("IOPAD_SDATA")
        en              = platform.request("FABRIC_EN")
        bitslip         = platform.request("FABRIC_BITSLIP_ADJ")
        data_valid      = platform.request("FABRIC_DATA_VALID")
        rst             = platform.request("FABRIC_RX_RST")
        
        serdes_out      = Signal(width*num_idly)
        clk_serdes_out  = Signal(num_idly)
        self.open1      = Signal(num_idly)
        self.open2      = Signal(num_idly)
        
        if (op_mode == "DPA"):
            dpa_lock    = platform.request("FABRIC_DPA_LOCK")
            dpa_error   = platform.request("FABRIC_DPA_ERROR")
        else:
            dpa_lock    = self.open1
            dpa_error   = self.open2
        
        if (num_idly > 1):
            for i in range(num_idly):

                fabric_q    = platform.request(f"FABRIC_PDATA_{i}")
                self.comb   += fabric_q.eq(serdes_out[(i*width):(i*width)+width])

                # Module instance.
                # ----------------
                self.specials += Instance("I_BUF",
                    # Parameters.
                    # -----------
                    p_WEAK_KEEPER = io_mode,
                    # Ports
                    #------
                    i_I     = iopad_i[i],
                    i_EN    = 1,
                    o_O     = self.i[i]
                )
                # Module instance.
                # ----------------
                self.specials += Instance("I_DELAY",
                    # Parameters.
                    # -----------
                    p_DELAY             = delay,
                    # Ports
                    #------
                    i_I                 = self.i[i],
                    i_DLY_LOAD          = delay_ld[i],
                    i_DLY_ADJ           = delay_adj[i],
                    i_DLY_INCDEC        = delay_incdec[i],
                    i_CLK_IN            = clock_out,
                    o_DLY_TAP_VALUE     = dly_tap_value[(i*6):(i*6)+6],
                    o_O                 = idly_out[i]
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
                    i_D               = idly_out[i],
                    i_RX_RST          = ~rst,
                    i_BITSLIP_ADJ     = bitslip[i],
                    i_EN              = en[i],
                    i_CLK_IN          = clk_serdes_out[i],
                    o_CLK_OUT         = clk_serdes_out[i],
                    o_Q               = serdes_out[(i*width):(i*width)+width],
                    o_DATA_VALID      = data_valid[i],
                    o_DPA_LOCK        = dpa_lock[i],
                    o_DPA_ERROR       = dpa_error[i],
                    i_PLL_LOCK        = self.pll_lock,
                    i_PLL_CLK         = clock_out
                )
        else:
            fabric_q    = platform.request("FABRIC_PDATA")
            # self.comb   += fabric_q.eq(serdes_out[(i*width):(i*width)+width])
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF",
                # Parameters.
                # -----------
                p_WEAK_KEEPER = io_mode,
                # Ports
                #------
                i_I     = iopad_i,
                i_EN    = 1,
                o_O     = self.i
            )
            # Module instance.
            # ----------------
            self.specials += Instance("I_DELAY",
                # Parameters.
                # -----------
                p_DELAY             = delay,
                # Ports
                #------
                i_I                 = self.i,
                i_DLY_LOAD          = dly_ld,
                i_DLY_ADJ           = dly_adj,
                i_DLY_INCDEC        = dly_incdec,
                i_CLK_IN            = clock_out,
                o_DLY_TAP_VALUE     = dly_tap_val,
                o_O                 = idly_out
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
                i_D               = idly_out,
                i_RX_RST          = ~rst,
                i_BITSLIP_ADJ     = bitslip,
                i_EN              = en,
                i_CLK_IN          = clk_serdes_out,
                o_CLK_OUT         = clk_serdes_out,
                o_Q               = fabric_q,
                o_DATA_VALID      = data_valid,
                o_DPA_LOCK        = dpa_lock,
                o_DPA_ERROR       = dpa_error,
                i_PLL_LOCK        = self.pll_lock,
                i_PLL_CLK         = clock_out
            )
            
    elif (io_model == "I_DELAY+I_DDR"):
        platform.add_extension(get_iddr_ios(num_idly))
        iopad_i     = platform.request("IOPAD_DATA_IN")
        en          = platform.request("FABRIC_EN")
        fabric_q    = platform.request("FABRIC_DATA_OUT")
        # rst         = platform.request("FABRIC_RST")
        
        if (num_idly > 1):
            for i in range(num_idly):

                # Module instance.
                # ----------------
                self.specials += Instance("I_BUF",
                    # Parameters.
                    # -----------
                    p_WEAK_KEEPER = io_mode,
                    # Ports
                    #------
                    i_I     = iopad_i[i],
                    i_EN    = 1,
                    o_O     = self.i[i]
                )
                # Module instance.
                # ----------------
                self.specials += Instance("I_DELAY",
                    # Parameters.
                    # -----------
                    p_DELAY             = delay,
                    # Ports
                    #------
                    i_I                 = self.i[i],
                    i_DLY_LOAD          = delay_ld[i],
                    i_DLY_ADJ           = delay_adj[i],
                    i_DLY_INCDEC        = delay_incdec[i],
                    i_CLK_IN            = clock_out,
                    o_DLY_TAP_VALUE     = dly_tap_value[(i*6):(i*6)+6],
                    o_O                 = idly_out[i]
                )

                # Module instance.
                # ----------------
                self.specials += Instance("I_DDR",
                    # Ports
                    #------
                    i_D = idly_out[i],
                    i_R = rst,
                    i_E = en[i],
                    i_C = clock_out,
                    o_Q = fabric_q[i]
                )
        else:
            rst     = platform.request("FABRIC_RST")
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF",
                # Parameters.
                # -----------
                p_WEAK_KEEPER = io_mode,
                # Ports
                #------
                i_I     = iopad_i,
                i_EN    = 1,
                o_O     = self.i
            )
            # Module instance.
            # ----------------
            self.specials += Instance("I_DELAY",
                # Parameters.
                # -----------
                p_DELAY             = delay,
                # Ports
                #------
                i_I                 = self.i,
                i_DLY_LOAD          = dly_ld,
                i_DLY_ADJ           = dly_adj,
                i_DLY_INCDEC        = dly_incdec,
                i_CLK_IN            = clock_out,
                o_DLY_TAP_VALUE     = dly_tap_val,
                o_O                 = idly_out
            )
            # Module instance.
            # ----------------
            self.specials += Instance("I_DDR",
                # Ports
                #------
                i_D = idly_out,
                i_R = rst,
                i_E = en,
                i_C = clock_out,
                o_Q = fabric_q
            )
            

#################################################################################
# I_DDR
#################################################################################
def I_DDR(self, platform, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq):
    platform.add_extension(get_iddr_ios())
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
                p_PLL_POST_DIV          = 2,
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
                p_PLL_POST_DIV          = 2,
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
        i_I     = platform.request("IOPAD_D"),
        i_EN    = 1,
        o_O     = self.i
    )
    
    # Module instance.
    # ----------------
    self.specials += Instance("I_DDR",
        # Ports
        #------
        i_D = self.i,
        i_R = platform.request("FABRIC_R"),
        i_E = platform.request("FABRIC_E"),
        i_C = clock_out,
        o_Q = platform.request("FABRIC_Q")
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
            i_I     = platform.request("IOPAD_D"),
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
            i_I     = platform.request("IOPAD_D"),
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
            o_Q               = platform.request("FABRIC_Q"),
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
                p_PLL_POST_DIV          = 2,
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
                o_Q               = platform.request("FABRIC_Q"),
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
                p_PLL_POST_DIV          = 2,
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
                o_Q               = platform.request("FABRIC_Q"),
                o_DATA_VALID      = platform.request("FABRIC_DATA_VALID"),
                o_DPA_LOCK        = dpa_lock,
                o_DPA_ERROR       = dpa_error,
                i_PLL_LOCK        = self.pll_lock,
                i_PLL_CLK         = self.pll_clk
            )

#################################################################################
# O_SERDES
#################################################################################
def O_SERDES(self, platform, data_rate, width, clocking, clock_forwarding, clocking_source, ref_clk_freq, out_clk_freq, op_mode, io_mode, voltage_standard, drive_strength, slew_rate, delay, delay_adjust, delay_type, clock_phase):
    platform.add_extension(get_oserdes_ios(width))
    
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
                i_D                     = platform.request("FABRIC_D"),   
                i_RST                   = platform.request("FABRIC_RST"),   
                i_LOAD_WORD             = platform.request("FABRIC_LOAD_WORD"),         
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
                    o_O     = platform.request("IOPAD_Q")
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
                    # p_IOSTANDARD                = voltage_standard,
                    # p_DRIVE_STRENGTH            = drive_strength,
                    # p_SLEW_RATE                 = slew_rate,
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
                i_D                     = platform.request("FABRIC_D"),   
                i_RST                   = platform.request("FABRIC_RST"),   
                i_LOAD_WORD             = platform.request("FABRIC_LOAD_WORD"),         
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
                    o_O     = platform.request("IOPAD_Q")
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
                    # p_IOSTANDARD                = voltage_standard,
                    # p_DRIVE_STRENGTH            = drive_strength,
                    # p_SLEW_RATE                 = slew_rate,
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
                p_PLL_POST_DIV          = 2,
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
                    i_D                     = platform.request("FABRIC_D"),   
                    i_RST                   = platform.request("FABRIC_RST"),   
                    i_LOAD_WORD             = platform.request("FABRIC_LOAD_WORD"),         
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
                        o_O     = platform.request("IOPAD_Q")
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
                        # p_IOSTANDARD                = voltage_standard,
                        # p_DRIVE_STRENGTH            = drive_strength,
                        # p_SLEW_RATE                 = slew_rate,
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
                    i_D                     = platform.request("FABRIC_D"),   
                    i_RST                   = platform.request("FABRIC_RST"),   
                    i_LOAD_WORD             = platform.request("FABRIC_LOAD_WORD"),         
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
                        o_O     = platform.request("IOPAD_Q")
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
                        # p_IOSTANDARD                = voltage_standard,
                        # p_DRIVE_STRENGTH            = drive_strength,
                        # p_SLEW_RATE                 = slew_rate,
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
                p_PLL_POST_DIV          = 2,
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
                    i_D                     = platform.request("FABRIC_D"),   
                    i_RST                   = platform.request("FABRIC_RST"),   
                    i_LOAD_WORD             = platform.request("FABRIC_LOAD_WORD"),         
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
                        o_O     = platform.request("IOPAD_Q")
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
                        # p_IOSTANDARD                = voltage_standard,
                        # p_DRIVE_STRENGTH            = drive_strength,
                        # p_SLEW_RATE                 = slew_rate,
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
                    i_D                     = platform.request("FABRIC_D"),   
                    i_RST                   = platform.request("FABRIC_RST"),   
                    i_LOAD_WORD             = platform.request("FABRIC_LOAD_WORD"),         
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
                        o_O     = platform.request("IOPAD_Q")
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
                        # p_IOSTANDARD                = voltage_standard,
                        # p_DRIVE_STRENGTH            = drive_strength,
                        # p_SLEW_RATE                 = slew_rate,
                        # Ports
                        #------
                        i_I     = self.clk_out,
                        o_O     = platform.request("IOPAD_CLK_OUT")
                    )

#################################################################################
# O_DDR
#################################################################################
def O_DDR(self, platform, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq):
    platform.add_extension(get_oddr_ios())
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
                p_PLL_POST_DIV          = 2,
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
                p_PLL_POST_DIV          = 2,
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
        i_D = platform.request("FABRIC_D"),
        i_R = platform.request("FABRIC_R"),
        i_E = platform.request("FABRIC_E"),
        i_C = clock_out,
        o_Q = self.q
    )
    # Module instance.
    # ----------------
    self.specials += Instance("O_BUF",
        # Ports
        #------
        i_I     = self.q,
        o_O     = platform.request("IOPAD_Q")
    )

#################################################################################
# O_DELAY
#################################################################################
def O_DELAY(self, platform, io_mode, delay, delay_type, clocking, clocking_source, ref_clk_freq, out_clk_freq):
    platform.add_extension(get_odelay_ios())
    self.o          = Signal(1)
    self.open       = Signal(1)
    self.clk        = Signal(1)
    self.clk_1      = Signal(1)
    self.lo_clk     = Signal(1)
    self.pll_clk    = Signal(1)
    self.pll_lock   = Signal(1)
    
    if (delay_type == "STATIC"):
        dly_adj         = 0
        dly_incdec      = 0
        dly_tap_value   = self.open
    
    elif (delay_type == "DYNAMIC"):
        dly_adj         = platform.request("FABRIC_DLY_ADJ")
        dly_incdec      = platform.request("FABRIC_DLY_INCDEC")
        dly_tap_value   = platform.request("FABRIC_DLY_TAP_VALUE")
        
    if (clocking == "RX_CLOCK"):
        clock_out   = self.clk_1
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
            o_O     = self.clk
        )
        # Module instance.
        # ----------------
        self.specials += Instance("CLK_BUF",
            # Ports
            #------
            i_I     = self.clk,
            o_O     = clock_out
        )
    
    elif (clocking == "PLL"):
        pll_mult, pll_div = freq_calc(self, out_clk_freq, ref_clk_freq, clocking_source)
        clock_out = self.pll_clk
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
                p_PLL_POST_DIV          = 2,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.lo_clk,
                o_CLK_OUT           = clock_out,          
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
                p_PLL_POST_DIV          = 2,
                # Ports
                #------
                i_PLL_EN            = 1,
                i_CLK_IN            = self.clk_1,
                o_CLK_OUT           = clock_out,           
                o_LOCK              = self.pll_lock
            )
    
    
    # Module instance.
    # ----------------
    self.specials += Instance("O_DELAY",
        # Parameters.
        # -----------
        p_DELAY             = delay,
        # Ports
        #------
        i_I                 = platform.request("FABRIC_I"),
        i_DLY_LOAD          = platform.request("FABRIC_DLY_LOAD"),
        i_DLY_ADJ           = dly_adj,
        i_DLY_INCDEC        = dly_incdec,
        i_CLK_IN            = clock_out,
        o_DLY_TAP_VALUE     = dly_tap_value,
        o_O                 = self.o
    )
    # Module instance.
    # ----------------
    self.specials += Instance("O_BUF",
        # Ports
        #------
        i_I     = self.o,
        o_O     = platform.request("IOPAD_O")
    )

# IO Configurator Wrapper ----------------------------------------------------------------------------------
class IO_CONFIG_Wrapper(Module):
    def __init__(self, platform, io_model, io_type, io_mode, voltage_standard, delay, data_rate, op_mode, width, 
                 clocking, clocking_source, out_clk_freq, ref_clk_freq, diff_termination, slew_rate, drive_strength, 
                 clock_forwarding, delay_adjust, delay_type, clock_phase, num_idly, num_odly, ports_file_path):
        # Clocking ---------------------------------------------------------------------------------
        self.clock_domains.cd_sys  = ClockDomain()
        
        if (io_model == "I_BUF"):
            I_BUF(self, platform, io_type, io_mode, voltage_standard, diff_termination)
            
        elif (io_model == "O_BUF"):
            O_BUF(self, platform, io_type, io_mode, voltage_standard, diff_termination, slew_rate, drive_strength)
            
        elif (io_model in ["I_DELAY", "I_DELAY+I_SERDES", "I_DELAY+I_DDR"]):
            if (num_idly > 20):
                cntrl = 2
            else:
                cntrl = 1
            I_DELAY(self, platform, io_model, io_mode, op_mode, data_rate, delay, delay_type, clocking, clocking_source, ref_clk_freq, out_clk_freq, num_idly, cntrl, ports_file_path, width)
            
        elif (io_model == "CLK_BUF"):
            CLK_BUF(self, platform, io_mode)
        
        elif (io_model == "I_DDR"):
            I_DDR(self, platform, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq)
            
        elif (io_model == "I_SERDES"):
            I_SERDES(self, platform, data_rate, width, op_mode, io_type, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq, delay, delay_adjust, delay_type, num_idly)
        
        elif (io_model == "O_SERDES"):
            O_SERDES(self, platform, data_rate, width, clocking, clock_forwarding, clocking_source, ref_clk_freq, out_clk_freq, op_mode, io_mode, voltage_standard, drive_strength, slew_rate, delay, delay_adjust, delay_type, clock_phase)
        
        elif (io_model == "O_DDR"):
            O_DDR(self, platform, io_mode, clocking, clocking_source, out_clk_freq, ref_clk_freq)
            
        elif (io_model == "O_DELAY"):
            O_DELAY(self, platform, io_mode, delay, delay_type, clocking, clocking_source, ref_clk_freq, out_clk_freq, num_odly, comb, width)

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
    
    
    core_string_param_group = parser.add_argument_group(title="Core string parameters") # Core string value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters") # Core range value parameters.
    core_fix_param_group = parser.add_argument_group(title="Core fix parameters") # Core fix value parameters.
    
    core_string_param_group.add_argument("--io_model",                  type=str,   default="CLK_BUF",              choices=["CLK_BUF", "I_BUF", "I_DELAY", "I_DELAY+I_SERDES", "I_DELAY+I_DDR", "I_DDR", "I_SERDES", "O_BUF", "O_DELAY", "O_DDR", "O_SERDES"],                              help="Type of Model")
    core_string_param_group.add_argument("--io_type",                   type=str,   default="SINGLE_ENDED",         choices=["SINGLE_ENDED", "DIFFERENTIAL", "TRI_STATE", "DIFF_TRI_STATE"],                                                help="Type of IO")
    core_string_param_group.add_argument("--io_mode",                   type=str,   default="NONE",                 choices=["NONE", "PULLUP", "PULLDOWN"],                                                                                 help="Input Configuration")
    core_string_param_group.add_argument("--bank_select",               type=str,   default="HP0",                  choices=["HP0", "HP1", "HV0", "HV1", "HV2", "HV3"],                                                                     help="Bank Selection for DELAY")
    # core_range_param_group.add_argument ("--num_of_delays",             type=int,   default=1,                      choices=range(1,41),                                                                                                    help="Number of DELAYs")
    # core_string_param_group.add_argument("--io_delay",                  type=str,   default="I_DELAY",              choices=["I_DELAY", "O_DELAY"],                                                                                         help="Type of DELAY")
    core_range_param_group.add_argument ("--num_of_i_delays",           type=int,   default=1,                      choices=range(1,41),                                                                                                    help="Number of input delays")
    core_range_param_group.add_argument ("--num_of_o_delays",           type=int,   default=1,                      choices=range(1,41),                                                                                                    help="Number of output delays")

    # core_string_param_group.add_argument("--combination",               type=str,   default="I_DELAY",              choices=["I_DELAY", "I_DELAY+I_SERDES", "I_DELAY+I_DDR", "O_DELAY", "O_DELAY+O_SERDES", "O_DELAY+O_DDR"],               help="Combination of Models in a design")
    core_string_param_group.add_argument("--data_rate",                 type=str,   default="SDR",                  choices=["SDR"],                                                                                                        help="Data Rate")
    core_string_param_group.add_argument("--op_mode",                   type=str,   default="NONE",                 choices=["NONE", "DPA", "CDR"],                                                                                         help="Dynamic Phase Alignment or Clock Data Recovery")
    core_string_param_group.add_argument("--clocking",                  type=str,   default="RX_CLOCK",             choices=["RX_CLOCK", "PLL"],                                                                                            help="Clocking option for I_SERDES")
    core_string_param_group.add_argument("--clocking_source",           type=str,   default="LOCAL_OSCILLATOR",     choices=["LOCAL_OSCILLATOR", "RX_IO_CLOCK"],                                                                            help="Clocking Source for PLL")
    core_string_param_group.add_argument("--clock_forwarding",          type=str,   default="FALSE",                choices=["TRUE", "FALSE"],                                                                                              help="Clock forwarding for O_SERDES")
    core_string_param_group.add_argument("--voltage_standard",          type=str,   default="DEFAULT",              choices=["DEFAULT", "LVCMOS_12", "LVCMOS_15", "LVCMOS_18_HP", "LVCMOS_18_HR", "LVCMOS_25", "LVCMOS_33",
                                                                                                                            "LVTTL", "HSTL_I_12", "HSTL_II_12", "HSTL_I_15", "HSTL_II_15", "HSUL_12", "PCI66", "PCIX133", "POD_12",
                                                                                                                            "SSTL_I_15", "SSTL_II_15", "SSTL_I_18_HP", "SSTL_II_18_HP", "SSTL_I_18_HR", "SSTL_II_18_HR", "SSTL_I_25",
                                                                                                                            "SSTL_II_25", "SSTL_I_33", "SSTL_II_33"],                                                                       help="IO Voltage Standards")
    core_string_param_group.add_argument("--diff_termination",          type=str,   default="TRUE",                 choices=["TRUE", "FALSE"],                                                                                              help="Enable differential termination")
    core_string_param_group.add_argument("--slew_rate",                 type=str,   default="SLOW",                 choices=["SLOW", "FAST"],                                                                                               help="Transition rate for LVCMOS standards")
    core_string_param_group.add_argument("--delay_adjust",              type=str,   default="TRUE",                 choices=["TRUE", "FALSE"],                                                                                              help="Data delay adjustment for SERDES")
    core_string_param_group.add_argument("--delay_type",                type=str,   default="STATIC",               choices=["STATIC", "DYNAMIC"],                                                                                          help="Delay type static/dynamic for SERDES")
    core_string_param_group.add_argument("--clock_phase",               type=str,   default="0",                    choices=["0", "90", "180", "270"],                                                                                      help="Clock Phase 0,90,180,270")

    core_fix_param_group.add_argument("--drive_strength",    type=int,   default=2,         choices=[2, 4, 6, 8, 12, 16],         help="Drive strength in mA for LVCMOS standards")
    
    core_range_param_group.add_argument("--delay",                      type=int,   default=0,         choices=range(0,64),         help="Tap Delay Value")
    core_range_param_group.add_argument("--width",                      type=int,   default=4,         choices=range(3,11),         help="Width of Serialization/Deserialization")
    core_range_param_group.add_argument("--out_clk_freq",               type=int,   default=1600,      choices=range(800,3201),     help="Output clock frequency in MHz")
    core_range_param_group.add_argument("--ref_clk_freq",               type=int,   default=50,        choices=range(5, 1201),      help="Reference clock frequency in MHz")
    
    # Core file path parameters.
    core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    core_file_path_group.add_argument("--ports_file_path",    type=str,    default="",       help="Path to port list")
    
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
    'Description'   : 'IO_Configurator is a native interface IP. It allows user to generate IO Primitives with configurable parameters.'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.img_name(args.io_model, file_path)   
        
        
        if (args.clock_forwarding == "TRUE"):
            option_strings_to_remove = ["--delay_adjust", "--delay", "--delay_type"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.delay_adjust == "FALSE"):
            option_strings_to_remove = ["--delay", "--delay_type"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.io_type in ["DIFFERENTIAL", "DIFF_TRI_STATE"]):
            parser._actions[9].choices = ["DEFAULT", "BLVDS_DIFF", "LVDS_HP_DIFF", "LVDS_HR_DIFF", "LVPECL_25_DIFF", "LVPECL_33_DIFF", "HSTL_12_DIFF", "HSTL_15_DIFF", "HSUL_12_DIFF", "MIPI_DIFF", "POD_12_DIFF", "RSDS_DIFF", "SLVS_DIFF", "SSTL_15_DIFF", "SSTL_18_HP_DIFF", "SSTL_18_HR_DIFF"]
        
        if (args.io_type not in ["DIFFERENTIAL", "DIFF_TRI_STATE"]):
                option_strings_to_remove = ["--diff_termination"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        if (args.io_model == "I_BUF"):
            option_strings_to_remove = ["--combination", "--num_of_i_delays", "--num_of_o_delays", "--delay_type", "--bank_select", "--clock_phase", "--voltage_standard", "--diff_termination", "--delay_adjust", "--delay_type", "--clock_forwarding", "--slew_rate", "--drive_strength", "--data_rate", "--op_mode", "--delay", "--width", "--clocking", "--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            parser._actions[2].choices = ["SINGLE_ENDED", "DIFFERENTIAL"]
        
        elif (args.io_model == "O_BUF"):
            option_strings_to_remove = ["--combination", "--num_of_i_delays", "--num_of_o_delays", "--delay_type", "--bank_select", "--clock_phase", "--diff_termination", "--voltage_standard", "--delay_adjust", "--delay_type", "--clock_forwarding", "--data_rate", "--op_mode", "--delay", "--width", "--clocking", "--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.voltage_standard not in ["LVCMOS_12", "LVCMOS_15", "LVCMOS_18_HP", "LVCMOS_18_HR", "LVCMOS_25", "LVCMOS_33"]):
                option_strings_to_remove = ["--slew_rate", "--drive_strength"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.io_type in ["SINGLE_ENDED", "DIFFERENTIAL"]):
                option_strings_to_remove = ['--io_mode']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        elif (args.io_model in ["I_DELAY", "O_DELAY"]):
            option_strings_to_remove = ["--clock_phase", "--delay_adjust", "--clock_forwarding", "--slew_rate", "--drive_strength", "--diff_termination", "--io_type", "--voltage_standard", "--data_rate", "--op_mode", "--width"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking == "RX_CLOCK"):
                option_strings_to_remove = ["--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking_source == "LOCAL_OSCILLATOR"):
                option_strings_to_remove = ["--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            
            if (args.io_model == "I_DELAY"):
                parser._actions[6].choices = ["I_DELAY", "I_DELAY+I_SERDES", "I_DELAY+I_DDR"]
                option_strings_to_remove = ["--num_of_o_delays"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            else:
                parser._actions[6].choices = ["O_DELAY", "O_DELAY+O_SERDES", "O_DELAY+O_DDR"]
                option_strings_to_remove = ["--num_of_i_delays"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        elif (args.io_model in ["I_DDR", "O_DDR"]):
            option_strings_to_remove = ["--combination", "--num_of_i_delays", "--num_of_o_delays", "--delay_type", "--bank_select", "--clock_phase", "--delay_adjust", "--delay_type","--clock_forwarding", "--slew_rate", "--drive_strength", "--diff_termination", "--delay", "--io_type", "--voltage_standard", "--data_rate", "--op_mode", "--width"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking == "RX_CLOCK"):
                option_strings_to_remove = ["--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            if (args.clocking_source == "LOCAL_OSCILLATOR"):
                option_strings_to_remove = ["--ref_clk_freq"]
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        elif (args.io_model in ["CLK_BUF"]):
            option_strings_to_remove = ["--combination", "--num_of_i_delays", "--num_of_o_delays", "--delay_type", "--bank_select", "--clock_phase", "--delay_adjust", "--delay_type","--clock_forwarding", "--slew_rate", "--drive_strength", "--diff_termination", "--delay", "--io_type", "--voltage_standard", "--data_rate", "--op_mode", "--width", "--clocking", "--clocking_source", "--out_clk_freq", "--ref_clk_freq"]
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        
        elif (args.io_model in ["I_SERDES", "O_SERDES"]):
            
            option_strings_to_remove = ["--combination", "--num_of_i_delays", "--num_of_o_delays", "--delay_type", "--bank_select", "--voltage_standard", "--slew_rate"]
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
    
    # if (args.io_model in ["I_BUF", "O_BUF"]):
    #    summary["VOLTAGE_STANDARD"] = args.voltage_standard
    
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
        
    elif (args.io_model in ["I_DELAY", "O_DELAY"]):
        summary["TAP_DELAY_VALUE"] = args.delay
    

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    device = "1VG28"

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device=device)
    module   = IO_CONFIG_Wrapper(platform,
        io_model                        = args.io_model,
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
        num_idly                        = args.num_of_i_delays,
        num_odly                        = args.num_of_o_delays,
        # comb                            = args.combination,
        ports_file_path                 = args.ports_file_path
        
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
