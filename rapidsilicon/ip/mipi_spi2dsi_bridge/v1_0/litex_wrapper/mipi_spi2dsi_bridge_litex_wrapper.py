#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Rapid Silicon's IP CATALOG mipi_spi2dsi_bridge.v

import os
import math
import datetime
import logging

from migen import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# RESET RELEASE  ---------------------------------------------------------------------------------------
class MIPISPI2DSIBRIDGE(Module):
    def __init__(self, platform):
        
        # Logger
        self.logger = logging.getLogger("MIPI_SPI2DSI_BRIDGE")
        
        self.logger.propagate = True
        
        
        self.logger.info(f"===================================================")
        
        self.rst               = Signal() 
        self.clk               = Signal()         
        self.spi_mosi_i        = Signal()     
        self.spi_csn_i         = Signal() 
        self.spi_clk_i         = Signal() 
        self.lcd_test_i        = Signal() 



        self.reg_1v8_en         = Signal()         
        self.reg_3v0_en         = Signal()
        self.lcd_rst            = Signal()   
        self.bl_en              = Signal()
        self.data_p             = Signal()
        self.data_n             = Signal()         
        self.clk_p              = Signal()
        self.clk_n              = Signal()   

        # Module instance.
        # ----------------
        self.specials += Instance("mipi_spi2dsi_bridge",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE               = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID                 = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION            = Instance.PreformattedParam("IP_VERSION"),


            # Signals
            # -------
            
            i_rst                    = self.rst,
            i_clk                    = self.clk,
            i_spi_mosi_i             = self.spi_mosi_i,
            i_spi_csn_i              = self.spi_csn_i,
            i_spi_clk_i              = self.spi_clk_i,
            i_lcd_test_i             = self.lcd_test_i,

            o_reg_1v8_en             = self.reg_1v8_en, 
            o_reg_3v0_en             = self.reg_3v0_en, 
            o_lcd_rst                = self.lcd_rst, 
            o_bl_en                  = self.bl_en, 
            o_data_p                 = self.data_p,
            o_data_n                 = self.data_n, 
            o_clk_p                  = self.clk_p, 
            o_clk_n                  = self.clk_n, 
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "mipi_spi2dsi_bridge.v"))
