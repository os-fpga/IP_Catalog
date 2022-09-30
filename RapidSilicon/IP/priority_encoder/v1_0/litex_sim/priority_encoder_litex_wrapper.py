
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

# LiteX wrapper around RapidSilicon priority_encoder

import os
import math
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# PRIORITY_ENCODER  ---------------------------------------------------------------------------------------
class PRIORITYENCODER(Module):
    def __init__(self, platform, width, lsb_high_priority):
        
        # Logger
        self.logger = logging.getLogger("PRIORITY_ENCODER")
        
        self.logger.propagate = False
        
        self.logger.info(f"WIDTH             : {width}")
        
        self.logger.info(f"LSB_HIGH_PRIORITY : {lsb_high_priority}")
        
        self.input_unencoded    = Signal(width)
        self.output_valid       = Signal()
        self.output_encoded     = Signal(math.ceil(math.log2(width)))         
        self.output_unencoded   = Signal(width)         

        # Module instance.
        # ----------------
        self.specials += Instance("priority_encoder",
            # Parameters.
            # -----------
            p_WIDTH             = width,
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
