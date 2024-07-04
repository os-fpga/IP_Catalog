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

def freq_calc(self, fast_clk_freq, ref_clk_freq, c_range, d_range):
    self.product = Signal()
    self.ready = Signal()
    a = fast_clk_freq
    b = ref_clk_freq
    c_range = 1000
    d_range = 63
    # Nested loop for iterating over c and d
    for c in range(c_range):
        for d in range(d_range):
            # Calculate 2 * (a / b)
            product_candidate = (a/ b)
            # Check if the candidate product matches the formula with c and d
            if product_candidate == ((c+1) / (d+1)):
                # If a match is found, assign c, d, and the product to the respective signals
                pll_mult = c + 1
                pll_div  = d + 1
                return pll_mult, pll_div
        #break                    




def enum_post_div(self, pll_post_div):
    post_div = {
                "1"   : 17,            
                "2"   : 18,
                "3"   : 19,
                "4"   : 20,
                "5"   : 21,
                "6"   : 22,
                "7"   : 23,
                "4"   : 34,
                "6"   : 35,
                "8"   : 36,
                "10"  : 37,
                "12"  : 38,
                "14"  : 39,
                "9"   : 51,
                "12"  : 52,
                "15"  : 53,
                "18"  : 54,
                "21"  : 55,
                "16"  : 68,
                "20"  : 69,
                "24"  : 70,
                "28"  : 71,
                "25"  : 85,
                "30"  : 86,
                "35"  : 87,
                "36"  : 102,
                "42"  : 103,
                "49"  :119,
            }[pll_post_div]
    return post_div


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
    def __init__(self, platform, divide_clk_in_by_2, fast_clk_freq, ref_clk_freq, pll_post_div, **kwargs):
        self.logger = logging.getLogger("PLL")
        self.logger.propagate = True

        post_div = enum_post_div(self,pll_post_div)
        # Logger
        self.logger = logging.getLogger("PLL")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        self.logger.info(f"DIVIDE_CLK_IN_BY_2   : {divide_clk_in_by_2}")

        self.logger.info(f"===================================================")
        
        # Create input/output signals
        self.PLL_EN = Signal()
        self.CLK_IN = Signal()
        self.CLK_OUT = Signal()
        self.CLK_OUT_DIV2 = Signal()
        self.CLK_OUT_DIV3 = Signal()
        self.CLK_OUT_DIV4 = Signal()
        self.FAST_CLK = Signal()
        self.LOCK = Signal()

        pll_mult, pll_div = freq_calc(self, fast_clk_freq, ref_clk_freq, c_range=63, d_range=640)

        if (divide_clk_in_by_2 == 1):
            divide_by_2 = "TRUE"
        else:
            divide_by_2 = "FALSE"

        self.specials += Instance("PLL",
                    **kwargs,
                    p_DEV_FAMILY            = "VIRGO",
                    p_DIVIDE_CLK_IN_BY_2    = (divide_by_2),
                    p_PLL_MULT_FRAC         = 0,
                    p_PLL_MULT              = Instance.PreformattedParam(pll_mult),
                    p_PLL_DIV               = Instance.PreformattedParam(pll_div),
                    p_PLL_POST_DIV          = Instance.PreformattedParam(post_div),

                    i_PLL_EN                = 1,
                    i_CLK_IN                = self.CLK_IN,
                    o_CLK_OUT               = self.CLK_OUT,
                    o_CLK_OUT_DIV2          = self.CLK_OUT_DIV2,
                    o_CLK_OUT_DIV3          = self.CLK_OUT_DIV3,
                    o_CLK_OUT_DIV4          = self.CLK_OUT_DIV4,
                    o_FAST_CLK              = self.FAST_CLK,
                    o_LOCK                  = self.LOCK
                )
