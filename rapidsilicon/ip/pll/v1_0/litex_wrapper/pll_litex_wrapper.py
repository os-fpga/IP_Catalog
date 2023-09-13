#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#


import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# Helpers ------------------------------------------------------------------------------------------
class Open(Signal): pass

def colorer(s, color="bright"):
    header  = {
        "bright": "\x1b[1m",
        "green":  "\x1b[32m",
        "cyan":   "\x1b[36m",
        "red":    "\x1b[31m",
        "yellow": "\x1b[33m",
        "underline": "\x1b[4m"}[color]
    trailer = "\x1b[0m"
    return header + str(s) + trailer

# PLL Wrapper ------------------------------------------------------------------------------------

class PLL(Module):
    def __init__(self, platform, divide_clk_in_by_2, pll_mult, pll_div, clk_out0_div, clk_out1_div, clk_out2_div, clk_out3_div, **kwargs):
        self.logger = logging.getLogger("PLL")
        self.logger.propagate = True

        
        # Logger
        self.logger = logging.getLogger("PLL")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        self.logger.info(f"DIVIDE_CLK_IN_BY_2   : {divide_clk_in_by_2}")
        self.logger.info(f"PLL_MULT             : {pll_mult}")
        self.logger.info(f"PLL_DIV              : {pll_div}")
        self.logger.info(f"CLK_OUT0_DIV         : {clk_out0_div}")
        self.logger.info(f"CLK_OUT1_DIV         : {clk_out1_div}")
        self.logger.info(f"CLK_OUT2_DIV         : {clk_out2_div}")
        self.logger.info(f"CLK_OUT3_DIV         : {clk_out3_div}")        
        self.logger.info(f"===================================================")
        
        # Create input/output signals
        self.pll_en = Signal()
        self.clk_in = Signal()
        self.clk_out0_en = Signal()
        self.clk_out1_en = Signal()
        self.clk_out2_en = Signal()
        self.clk_out3_en = Signal()
        self.clk_out0 = Signal()
        self.clk_out1 = Signal()
        self.clk_out2 = Signal()
        self.clk_out3 = Signal()
        self.gearbox_fast_clk = Signal()
        self.lock = Signal()

        self.specials += Instance("PLL",
            **kwargs,

            p_DIVIDE_CLK_IN_BY_2    = Instance.PreformattedParam(divide_clk_in_by_2),
            p_PLL_MULT              = Instance.PreformattedParam(pll_mult),
            p_PLL_DIV               = Instance.PreformattedParam(pll_div),
            p_CLK_OUT0_DIV          = Instance.PreformattedParam(clk_out0_div),
            p_CLK_OUT1_DIV          = Instance.PreformattedParam(clk_out1_div),
            p_CLK_OUT2_DIV          = Instance.PreformattedParam(clk_out2_div),
            p_CLK_OUT3_DIV          = Instance.PreformattedParam(clk_out3_div),

            i_PLL_EN                = self.pll_en,
            i_CLK_IN                = self.clk_in,
            i_CLK_OUT0_EN           = self.clk_out0_en,
            i_CLK_OUT1_EN           = self.clk_out1_en,
            i_CLK_OUT2_EN           = self.clk_out2_en,
            i_CLK_OUT3_EN           = self.clk_out3_en,
            o_CLK_OUT0              = self.clk_out0,
            o_CLK_OUT1              = self.clk_out1,
            o_CLK_OUT2              = self.clk_out2,
            o_CLK_OUT3              = self.clk_out3,
            o_GEARBOX_FAST_CLK      = self.gearbox_fast_clk,
            o_LOCK                  = self.lock
        )

        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "PLL.v"))
