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
        self.PLL_EN = Signal()
        self.CLK_IN = Signal()
        self.CLK_OUT0_EN = Signal()
        self.CLK_OUT1_EN = Signal()
        self.CLK_OUT2_EN = Signal()
        self.CLK_OUT3_EN = Signal()
        self.CLK_OUT0 = Signal()
        self.CLK_OUT1 = Signal()
        self.CLK_OUT2 = Signal()
        self.CLK_OUT3 = Signal()
        self.GEARBOX_FAST_CLK = Signal()
        self.LOCK = Signal()

        self.specials += Instance("PLL",
            **kwargs,

            p_DIVIDE_CLK_IN_BY_2    = Instance.PreformattedParam(divide_clk_in_by_2),
            p_PLL_MULT              = Instance.PreformattedParam(pll_mult),
            p_PLL_DIV               = Instance.PreformattedParam(pll_div),
            p_CLK_OUT0_DIV          = Instance.PreformattedParam(clk_out0_div),
            p_CLK_OUT1_DIV          = Instance.PreformattedParam(clk_out1_div),
            p_CLK_OUT2_DIV          = Instance.PreformattedParam(clk_out2_div),
            p_CLK_OUT3_DIV          = Instance.PreformattedParam(clk_out3_div),

            i_PLL_EN                = self.PLL_EN,
            i_CLK_IN                = self.CLK_IN,
            i_CLK_OUT0_EN           = self.CLK_OUT0_EN,
            i_CLK_OUT1_EN           = self.CLK_OUT1_EN,
            i_CLK_OUT2_EN           = self.CLK_OUT2_EN,
            i_CLK_OUT3_EN           = self.CLK_OUT3_EN,
            o_CLK_OUT0              = self.CLK_OUT0,
            o_CLK_OUT1              = self.CLK_OUT1,
            o_CLK_OUT2              = self.CLK_OUT2,
            o_CLK_OUT3              = self.CLK_OUT3,
            o_GEARBOX_FAST_CLK      = self.GEARBOX_FAST_CLK,
            o_LOCK                  = self.LOCK
        )

        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "PLL.v"))
