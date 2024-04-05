#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import datetime
import logging

from migen import *

logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# IO_CONFIGURATOR ------------------------------------------------------------------------------------------
class IO_CONFIG(Module):
    
    #################################################################################
    # I_BUF
    #################################################################################
    def I_BUF(self, io_type, config):
        if (io_type == "Single_Ended"):
            self.i      = Signal(1)
            self.en     = Signal(1)
            self.o      = Signal(1)
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF",
                # Parameters.
                # -----------
                p_WEAK_KEEPER = config,
                # Ports
                #------
                i_I     = self.i,
                i_EN    = self.en,
                o_O     = self.o
            )
        
        elif (io_type == "Differential"):
            self.i_p    = Signal(1)
            self.i_n    = Signal(1)
            self.en     = Signal(1)
            self.o      = Signal(1)
            # Module instance.
            # ----------------
            self.specials += Instance("I_BUF_DS",
                # Parameters.
                # -----------
                p_WEAK_KEEPER = config,
                # Ports
                #------
                i_I_P   = self.i_p,
                i_I_N   = self.i_n,
                i_EN    = self.en,
                o_O     = self.o
            )
    
    #################################################################################
    # O_BUF
    #################################################################################
    def O_BUF(self, io_type, config):
        if (io_type == "Single_Ended"):
            self.i      = Signal(1)
            self.o      = Signal(1)
            # Module instance.
            # ----------------
            self.specials += Instance("O_BUF",
                # Ports
                #------
                i_I     = self.i,
                o_O     = self.o
            )
        
        elif (io_type == "Differential"):
            self.i        = Signal(1)
            self.o_p      = Signal(1)
            self.o_n      = Signal(1)
            # Module instance.
            # ----------------
            self.specials += Instance("O_BUF_DS",
                # Ports
                #------
                i_I         = self.i,
                o_O_P       = self.o_p,
                o_O_N       = self.o_n
            )
            
        elif (io_type == "Tri-State"):
            self.i          = Signal(1)
            self.t          = Signal(1)
            self.o          = Signal(1)
            # Module instance.
            # ----------------
            self.specials += Instance("O_BUFT",
                # Parameters.
                # -----------
                p_WEAK_KEEPER = config,
                # Ports
                #------
                i_I         = self.i,
                o_T         = self.t,
                o_O         = self.o
            )
            
        elif (io_type == "Differential-Tri-State"):
            self.i          = Signal(1)
            self.t          = Signal(1)
            self.o_p        = Signal(1)
            self.o_n        = Signal(1)
            # Module instance.
            # ----------------
            self.specials += Instance("O_BUFT_DS",
                # Parameters.
                # -----------
                p_WEAK_KEEPER = config,
                # Ports
                #------
                i_I         = self.i,
                o_T         = self.t,
                o_O_P       = self.o_p,
                o_O_N       = self.o_n
            )
    
    #################################################################################
    # I_DELAY
    #################################################################################
    def I_DELAY(self, config, delay):
        self.i              = Signal(1)
        self.i_1            = Signal(1)
        self.dly_load       = Signal(1)
        self.dly_adj        = Signal(1)
        self.dly_incdec     = Signal(1)
        self.dly_tap_value  = Signal(6)
        self.clk_in         = Signal(1)
        self.o              = Signal(1)
        
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF",
            # Parameters.
            # -----------
            p_WEAK_KEEPER = config,
            # Ports
            #------
            i_I     = self.i,
            i_EN    = 1,
            o_O     = self.i_1
        )
        
        # Module instance.
        # ----------------
        self.specials += Instance("I_DELAY",
            # Parameters.
            # -----------
            p_DELAY             = delay,
            # Ports
            #------
            i_I                 = self.i_1,
            i_DLY_LOAD          = self.dly_load,
            i_DLY_ADJ           = self.dly_adj,
            i_DLY_INCDEC        = self.dly_incdec,
            i_CLK_IN            = self.clk_in,
            o_DLY_TAP_VALUE     = self.dly_tap_value,
            o_O                 = self.o
        )
    
    #################################################################################
    # CLK_BUF
    #################################################################################
    def CLK_BUF(self, config):
        self.i      = Signal(1)
        self.i_1    = Signal(1)
        self.o      = Signal(1)
        # Module instance.
        # ----------------
        self.specials += Instance("I_BUF",
            # Parameters.
            # -----------
            p_WEAK_KEEPER = config,
            # Ports
            #------
            i_I     = self.i,
            i_EN    = 1,
            o_O     = self.i_1
        )
        
        # Module instance.
        # ----------------
        self.specials += Instance("CLK_BUF",
            # Ports
            #------
            i_I     = self.i_1,
            o_O     = self.o
        )
    
    #################################################################################
    # I_SERDES
    #################################################################################
    def I_SERDES(self, data_rate, width, dpa_mode):
        self.d              = Signal(1)
        self.rx_rst         = Signal(1)
        self.bitslip_adj    = Signal(1)
        self.en             = Signal(1)
        self.clk_in         = Signal(1)
        self.clk_out        = Signal(1)
        self.q              = Signal(width)
        self.data_valid     = Signal(1)
        self.dpa_lock       = Signal(1)
        self.dpa_error      = Signal(1)
        self.pll_lock       = Signal(1)
        self.pll_clk        = Signal(1)
        # Module instance.
        # ----------------
        self.specials += Instance("I_SERDES",
            # Parameters.
            # -----------
            p_DATA_RATE     = data_rate,
            p_WIDTH         = width,
            p_DPA_MODE      = dpa_mode,
            # Ports
            #------
            i_D               = self.d,
            i_RX_RST          = self.rx_rst,
            i_BITSLIP_ADJ     = self.bitslip_adj,
            i_EN              = self.en,
            i_CLK_IN          = self.clk_in,
            o_CLK_OUT         = self.clk_out,
            o_Q               = self.q,
            o_DATA_VALID      = self.data_valid,
            o_DPA_LOCK        = self.dpa_lock,
            o_DPA_ERROR       = self.dpa_error,
            i_PLL_LOCK        = self.pll_lock,
            i_PLL_CLK         = self.pll_clk
        )
    
    #################################################################################
    # O_SERDES
    #################################################################################
    def O_SERDES(self, data_rate, width):
        self.d                      = Signal(width)
        self.rst                    = Signal(1)
        self.load_word              = Signal(1)
        self.clk_in                 = Signal(1)
        self.oe_in                  = Signal(1)
        self.oe_out                 = Signal(1)
        self.q                      = Signal(1)
        self.channel_bond_sync_in   = Signal(1)
        self.channel_bond_sync_out  = Signal(1)
        self.pll_lock               = Signal(1)
        self.pll_clk                = Signal(1)
        # Module instance.
        # ----------------
        self.specials += Instance("O_SERDES",
            # Parameters.
            # -----------
            p_DATA_RATE     = data_rate,
            p_WIDTH         = width,
            # Ports
            #------
            i_D                     = self.d,   
            i_RST                   = self.rst,   
            i_LOAD_WORD             = self.load_word,         
            i_CLK_IN                = self.clk_in,    
            i_OE_IN                 = self.oe_in,
            o_OE_OUT                = self.oe_out,     
            o_Q                     = self.q,
            i_CHANNEL_BOND_SYNC_IN  = self.channel_bond_sync_in,        
            o_CHANNEL_BOND_SYNC_OUT = self.channel_bond_sync_out,
            i_PLL_LOCK              = self.pll_lock,
            i_PLL_CLK               = self.pll_clk
            
        )
    
    #################################################################################
    # I_DDR
    #################################################################################
    def I_DDR(self, config):
        self.d      = Signal(1)
        self.r      = Signal(1)
        self.e      = Signal(1)
        self.q      = Signal(2)
        self.CLK_BUF(config)
        
        # Module instance.
        # ----------------
        self.specials += Instance("I_DDR",
            # Ports
            #------
            i_D = self.d,
            i_R = self.r,
            i_E = self.e,
            i_C = self.o,
            o_Q = self.q
        )
    
    #################################################################################
    # I_DELAY
    #################################################################################
    def O_DELAY(self, delay):
        self.i              = Signal(1)
        self.i_1            = Signal(1)
        self.dly_load       = Signal(1)
        self.dly_adj        = Signal(1)
        self.dly_incdec     = Signal(1)
        self.dly_tap_value  = Signal(6)
        self.clk_in         = Signal(1)
        self.o              = Signal(1)
        
        # Module instance.
        # ----------------
        self.specials += Instance("O_DELAY",
            # Parameters.
            # -----------
            p_DELAY             = delay,
            # Ports
            #------
            i_I                 = self.i,
            i_DLY_LOAD          = self.dly_load,
            i_DLY_ADJ           = self.dly_adj,
            i_DLY_INCDEC        = self.dly_incdec,
            i_CLK_IN            = self.clk_in,
            o_DLY_TAP_VALUE     = self.dly_tap_value,
            o_O                 = self.i_1
        )
        # Module instance.
        # ----------------
        self.specials += Instance("O_BUF",
            # Ports
            #------
            i_I     = self.i_1,
            o_O     = self.o
        )
        
    def __init__(self, platform, io_model, io_type, config, delay, data_rate, dpa_mode, width):
        # Get/Check Parameters.
        # ---------------------
        self.logger = logging.getLogger("IO_CONFIGURATOR")

        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # IO Model
        self.logger.info(f"IO_MODEL             : {io_model}")

        # IO_TYPE
        self.logger.info(f"IO_TYPE              : {io_type}")

        # IO_CONFIGURATION
        self.logger.info(f"IO_CONFIGURATION     : {config}")

        self.logger.info(f"===================================================")
        
        if (io_model == "I_BUF"):
            self.I_BUF(io_type, config)
        
        elif (io_model == "O_BUF"):
            self.O_BUF(io_type, config)
        
        elif (io_model == "I_DELAY"):
            self.I_DELAY(config, delay)
        
        elif (io_model == "CLK_BUF"):
            self.CLK_BUF(config)
            
        elif (io_model == "I_SERDES"):
            self.I_SERDES(data_rate, width, dpa_mode)
        
        elif (io_model == "I_DDR"):
            self.I_DDR(config)
        
        elif (io_model == "O_SERDES"):
            self.O_SERDES(data_rate, width)
        
        elif (io_model == "O_DELAY"):
            self.O_DELAY(delay)