
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

# LiteX wrapper around RapidSilicon axis_uart

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *


logging.basicConfig(level=logging.INFO)

# AXIS-UART  ---------------------------------------------------------------------------------------
class AXISTREAMUART(Module):
    def __init__(self, platform, s_axis, m_axis):
        
        self.logger = logging.getLogger("AXI_STREAM_UART")
        
        # Data width.
        data_width = len(s_axis.data)
        self.logger.info(f"DATA_WIDTH : {data_width}")
        
        
        self.i_rxd              = Signal()
        self.o_txd              = Signal()
        self.o_tx_busy          = Signal()         
        self.o_rx_busy          = Signal()         
        self.o_rx_overrun_error = Signal()
        self.o_rx_frame_error   = Signal()
        self.i_prescale         = Signal()

        # Module instance.
        # ----------------
        self.specials += Instance("uart",
            # Parameters.
            # -----------
            # Global.
            p_DATA_WIDTH        = data_width,

            # Clk / Rst.
            # ----------
            i_clk               = ClockSignal(),
            i_rst               = ResetSignal(),

            # AXI Input
            # --------------------
            i_s_axis_tdata      = s_axis.data,
            i_s_axis_tvalid     = s_axis.valid,
            o_s_axis_tready     = s_axis.ready,

            # AXI Output
            o_m_axis_tdata      = m_axis.data,
            o_m_axis_tvalid     = m_axis.valid,
            i_m_axis_tready     = m_axis.ready,
            
            # UART interface
            i_rxd               = self.i_rxd,
            o_txd               = self.o_txd,
            
            # Status
            o_tx_busy           = self.o_tx_busy,
            o_rx_busy           = self.o_rx_busy,
            o_rx_overrun_error  = self.o_rx_overrun_error,
            o_rx_frame_error    = self.o_rx_frame_error,
            
            # Configuration
            i_prescale          = self.i_prescale
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "uart.v"))
