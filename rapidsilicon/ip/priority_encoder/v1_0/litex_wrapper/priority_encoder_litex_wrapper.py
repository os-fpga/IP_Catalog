#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich verilog-axi's priority_encoder.v

import os
import datetime
import math
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# PRIORITY_ENCODER  ---------------------------------------------------------------------------------------
class PRIORITYENCODER(Module):
    def __init__(self, platform, width, lsb_high_priority):
        
        # Logger
        self.logger = logging.getLogger("PRIORITY_ENCODER")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        self.logger.info(f"WIDTH             : {width}")
        
        self.logger.info(f"LSB_HIGH_PRIORITY : {lsb_high_priority}")
        
        self.logger.info(f"===================================================")
        
        self.input_unencoded    = Signal(width)
        self.output_valid       = Signal()
        self.output_encoded     = Signal(math.ceil(math.log2(width)))         
        self.output_unencoded   = Signal(width)         

        # Module instance.
        # ----------------
        self.specials += Instance("priority_encoder",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE           = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID             = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION        = Instance.PreformattedParam("IP_VERSION"),
            p_WIDTH             = Instance.PreformattedParam(width),
            p_LSB_HIGH_PRIORITY = lsb_high_priority,

            # Signals
            # -------
            i_input_unencoded   = self.input_unencoded,
            o_output_valid      = self.output_valid,
            o_output_encoded    = self.output_encoded,
            o_output_unencoded  = self.output_unencoded
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "priority_encoder.v"))
