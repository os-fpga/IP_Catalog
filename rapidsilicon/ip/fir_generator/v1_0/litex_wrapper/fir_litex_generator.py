#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2023 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#

import datetime
import logging
import math
from migen import *


# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# FIR Generator ---------------------------------------------------------------------------------------
class FIR(Module):
    def __init__(self):
        self.logger = logging.getLogger("FIR")
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Data Width
        self.logger.info(f"DATA_WIDTH_IN       : {18}")
        self.logger.info(f"DATA_WIDTH_OUT       : {38}")

        self.logger.info(f"===================================================")

        coefficients = 4
        self.data_in = Signal(18)
        self.data_out = Signal(38)

        self.z = Array(Signal() for _ in range (coefficients))
        self.delay_b = Array(Signal() for _ in range (coefficients))

        for i in range (coefficients):
            self.delay_b[i] = Signal(18, name=f"delay_b_{i}")
            self.z[i] = Signal(38, name=f"z_{i}")

        for i in range(coefficients):
            if (i == 0):
                self.specials += Instance("DSP38",

                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP
                    p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                    p_OUTPUT_REG_EN = "TRUE",
                    p_INPUT_REG_EN = "TRUE",
                    p_COEFF_0       = 2,

                    # Reset
                    i_CLK           = ClockSignal(),
                    i_RESET        = ResetSignal(),

                    # IOs
                    i_A             = C(0, 20),
                    i_B             = self.data_in,
                    o_Z             = self.z[i],  
                    i_FEEDBACK      = C(4, 3),
                    i_UNSIGNED_A    = 1,
                    i_UNSIGNED_B    = 1,
                    o_DLY_B         = self.delay_b[i],
                    i_LOAD_ACC      = 1,
                    i_ACC_FIR       = C(0, 6),
                    i_ROUND         = 0,
                    i_SATURATE      = 0,
                    i_SHIFT_RIGHT   = C(0, 6),
                    i_SUBTRACT      = 0
                )
            elif (i == coefficients - 1):
                self.specials += Instance("DSP38",

                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP
                    p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                    p_OUTPUT_REG_EN = "FALSE",
                    p_INPUT_REG_EN = "TRUE",
                    p_COEFF_0       = 2,

                    # Reset
                    i_CLK           = ClockSignal(),
                    i_RESET        = ResetSignal(),

                    # IOs
                    i_A             = self.z[i - 1],
                    i_B             = self.delay_b[i - 1],
                    o_Z             = self.data_out,  
                    i_FEEDBACK      = C(4, 3),
                    i_UNSIGNED_A    = 1,
                    i_UNSIGNED_B    = 1,
                    i_LOAD_ACC      = 1,
                    i_ACC_FIR       = C(0, 6),
                    i_ROUND         = 0,
                    i_SATURATE      = 0,
                    i_SHIFT_RIGHT   = C(0, 6),
                    i_SUBTRACT      = 0
                )
            else:
                self.specials += Instance("DSP38",

                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP
                    p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                    p_OUTPUT_REG_EN = "TRUE",
                    p_INPUT_REG_EN = "TRUE",
                    p_COEFF_0       = 4,

                    # Reset
                    i_CLK           = ClockSignal(),
                    i_RESET        = ResetSignal(),

                    # IOs
                    i_A             = self.z[i - 1],
                    i_B             = self.delay_b[i - 1],
                    o_Z             = self.z[i],  
                    i_FEEDBACK      = C(4, 3),
                    i_UNSIGNED_A    = 1,
                    i_UNSIGNED_B    = 1,
                    o_DLY_B         = self.delay_b[i],
                    i_LOAD_ACC      = 1,
                    i_ACC_FIR       = C(0, 6),
                    i_ROUND         = 0,
                    i_SATURATE      = 0,
                    i_SHIFT_RIGHT   = C(0, 6),
                    i_SUBTRACT      = 0
                )


