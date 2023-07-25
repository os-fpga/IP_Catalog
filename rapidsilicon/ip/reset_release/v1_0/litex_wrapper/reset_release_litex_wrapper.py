#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Rapid Silicon's IP CATALOG reset_release.v

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
class RESETRELEASE(Module):
    def __init__(self, platform, EXT_RESET_WIDTH, INTERCONNECTS, BUS_RESET, PERIPHERAL_RESET, PERIPHERAL_ARESETN):
        
        # Logger
        self.logger = logging.getLogger("RESET_RELEASE")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        self.logger.info(f"EXTERNAL RESET WINDOW    : {EXT_RESET_WIDTH}")
        self.logger.info(f"INTERCONNECTS            : {INTERCONNECTS}")
        self.logger.info(f"BUS_RESET                : {BUS_RESET}")
        self.logger.info(f"PERIPHERAL_RESET         : {PERIPHERAL_RESET}")
        self.logger.info(f"PERIPHERAL_ARESETN       : {PERIPHERAL_ARESETN}")
        
        self.logger.info(f"===================================================")
        
        self.slow_clk               = Signal() 
        self.ext_rst                = Signal()         
        self.cpu_dbg_rst            = Signal()     
        self.pll_lock               = Signal() 

        self.cpu_rst                = Signal()         
        self.periph_aresetn         = Signal(PERIPHERAL_ARESETN)
        self.interconnect_aresetn   = Signal(INTERCONNECTS)   
        self.bus_reset              = Signal(BUS_RESET)
        self.periph_reset           = Signal(PERIPHERAL_RESET)

        # Module instance.
        # ----------------
        self.specials += Instance("reset_release",
            # Parameters.
            # -----------
            p_EXT_RESET_WIDTH       = Instance.PreformattedParam(EXT_RESET_WIDTH),
            p_INTERCONNECTS         = Instance.PreformattedParam(INTERCONNECTS),
            p_BUS_RESET             = Instance.PreformattedParam(BUS_RESET),
            p_PERIPHERAL_RESET      = Instance.PreformattedParam(PERIPHERAL_RESET),
            p_PERIPHERAL_ARESETN    = Instance.PreformattedParam(PERIPHERAL_ARESETN),    


            # Signals
            # -------
            
            i_slow_clk              = self.slow_clk,
            i_ext_rst               = self.ext_rst,
            i_cpu_dbg_rst           = self.cpu_dbg_rst,
            i_pll_lock              = self.pll_lock,

            o_cpu_rst               = self.cpu_rst, 
            o_periph_aresetn        = self.periph_aresetn, 
            o_interconnect_aresetn  = self.interconnect_aresetn, 
            o_bus_reset             = self.bus_reset, 
            o_periph_reset          = self.periph_reset
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "reset_release.v"))
