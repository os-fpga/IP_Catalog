#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Freecores uart16650's axi4lite_uart_top.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# AXI LITE UART -------------------------------------------------------------------------------------
class AXILITEUART(Module):
    def __init__(self, platform, s_axil, address_width, data_width):
        
        self.logger = logging.getLogger("AXI_LITE_UART")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Clock Domain
        clock_domain = s_axil.clock_domain
        self.logger.info(f"CLOCK_DOMAIN     : {clock_domain}")
        
        # Address width.
        address_width = len(s_axil.aw.addr)
        self.logger.info(f"ADDRESS_WIDTH    : {address_width}")
        
        # Read Data width.
        data_width = len(s_axil.r.data)
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        
        self.logger.info(f"===================================================")
        # UART Signals
        self.int_o           = Signal()
        self.srx_pad_i       = Signal()  
        self.stx_pad_o       = Signal()
        self.rts_pad_o       = Signal()
        self.cts_pad_i       = Signal()
        self.dtr_pad_o       = Signal()
        self.dsr_pad_i       = Signal()
        self.ri_pad_i        = Signal()
        self.dcd_pad_i       = Signal()
        
        # Module instance.
        # ----------------
        self.specials += Instance("axi4lite_uart_top",
        # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE        = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID          = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION     = Instance.PreformattedParam("IP_VERSION"),
            p_ADDRESS_WIDTH  = Instance.PreformattedParam(address_width),
            p_DATA_WIDTH     = Instance.PreformattedParam(data_width),

            # Clk / Rst.
            # ----------
            i_s_axi_aclk     = ClockSignal(clock_domain),
            i_s_axi_aresetn  = ResetSignal(clock_domain),
            
            # UART Signals
            o_int_o          = self.int_o,
            i_srx_pad_i      = self.srx_pad_i,
            o_stx_pad_o      = self.stx_pad_o,
            o_rts_pad_o      = self.rts_pad_o,
            i_cts_pad_i      = self.cts_pad_i,
            o_dtr_pad_o      = self.dtr_pad_o,
            i_dsr_pad_i      = self.dsr_pad_i,
            i_ri_pad_i       = self.ri_pad_i,
            i_dcd_pad_i      = self.dcd_pad_i,
            
            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_s_axi_awaddr   = s_axil.aw.addr,
            i_s_axi_awprot   = s_axil.aw.prot, 
            i_s_axi_awvalid  = s_axil.aw.valid,
            o_s_axi_awready  = s_axil.aw.ready,

            # W.
            i_s_axi_wdata    = s_axil.w.data,
            i_s_axi_wstrb    = s_axil.w.strb,
            i_s_axi_wvalid   = s_axil.w.valid,
            o_s_axi_wready   = s_axil.w.ready,

            # B.
            o_s_axi_bresp    = s_axil.b.resp,
            o_s_axi_bvalid   = s_axil.b.valid,
            i_s_axi_bready   = s_axil.b.ready,

            # AR.
            i_s_axi_araddr   = s_axil.ar.addr,
            i_s_axi_arprot   = s_axil.ar.prot,
            i_s_axi_arvalid  = s_axil.ar.valid,
            o_s_axi_arready  = s_axil.ar.ready,

            # R.
            o_s_axi_rdata    = s_axil.r.data,
            o_s_axi_rresp    = s_axil.r.resp,
            o_s_axi_rvalid   = s_axil.r.valid,
            i_s_axi_rready   = s_axil.r.ready,
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)
    
    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi4lite_uart_top.v"))