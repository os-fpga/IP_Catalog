#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich verilog-uart's uart.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# AXIS-UART  ---------------------------------------------------------------------------------------
class AXISTREAMUART(Module):
    def __init__(self, platform, s_axis, m_axis, data_width=5):
        
        self.logger = logging.getLogger("AXI_STREAM_UART")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Data width.
        data_width = len(s_axis.data)
        self.logger.info(f"DATA_WIDTH : {data_width}")
        
        self.logger.info(f"===================================================")
        
        # Uart Signals
        self.rxd              = Signal(1)
        self.txd              = Signal(1)
        self.tx_busy          = Signal(1)         
        self.rx_busy          = Signal(1)         
        self.rx_overrun_error = Signal(1)
        self.rx_frame_error   = Signal(1)
        self.prescale         = Signal(16)

        # Module instance.
        # ----------------
        self.specials += Instance("uart",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE           = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID             = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION        = Instance.PreformattedParam("IP_VERSION"),
            # Global.
            p_DATA_WIDTH        = Instance.PreformattedParam(data_width),

            # Clk / Rst.
            # ----------
            i_clk               = ClockSignal(),
            i_rst               = ResetSignal(),

            # AXI Input
            i_s_axis_tdata      = s_axis.data,
            i_s_axis_tvalid     = s_axis.valid,
            o_s_axis_tready     = s_axis.ready,

            # AXI Output
            o_m_axis_tdata      = m_axis.data,
            o_m_axis_tvalid     = m_axis.valid,
            i_m_axis_tready     = m_axis.ready,
            
            # UART interface
            i_rxd               = self.rxd,
            o_txd               = self.txd,
            
            # Status
            o_tx_busy           = self.tx_busy,
            o_rx_busy           = self.rx_busy,
            o_rx_overrun_error  = self.rx_overrun_error,
            o_rx_frame_error    = self.rx_frame_error,
            
            # Configuration
            i_prescale          = self.prescale
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "uart.v"))
