
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

# LiteX wrapper around RapidSilicon axil_gpio

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

class AXILITEGPIO(Module):
    def __init__(self, platform, s_axil, data_width, address_width):
        self.logger = logging.getLogger("AXI_LITE_GPIO")

        # Clock Domain.
        clock_domain = s_axil.clock_domain
        self.logger.info(f"Clock Domain     : {clock_domain}")
        
        # GPIO
        self.gpin  = Signal(data_width)
        self.gpout = Signal(data_width)
        self.int   = Signal()
        
        # Data width.
        data_width = len(s_axil.w.data)
        self.logger.info(f"Data Width       : {data_width}")

        # Address width.
        address_width = len(s_axil.aw.addr)
        self.logger.info(f"Address Width    : {address_width}")
        
        # Module instance.
        # ----------------

        self.specials += Instance("axi4lite_gpio",
            # Parameters.
            # -----------
            p_DATA_WIDTH      = data_width,
            p_ADDR_WIDTH      = address_width,
            
            # Clk / Rst.
            # ----------
            i_CLK      = ClockSignal(clock_domain),
            i_RSTN     = ResetSignal(clock_domain),
            
            # GPIOS
            i_GPIN     = self.gpin,
            o_GPOUT    = self.gpout,
            o_INT      = self.int,

            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_AWADDR   = s_axil.aw.addr,
            i_AWPROT   = s_axil.aw.prot,
            i_AWVALID  = s_axil.aw.valid,
            o_AWREADY  = s_axil.aw.ready,

            # W.
            i_WDATA    = s_axil.w.data,
            i_WSTRB    = s_axil.w.strb,
            i_WVALID   = s_axil.w.valid,
            o_WREADY   = s_axil.w.ready,

            # B.
            o_BRESP    = s_axil.b.resp,
            o_BVALID   = s_axil.b.valid,
            i_BREADY   = s_axil.b.ready,

            # AR.
            i_ARADDR   = s_axil.ar.addr,
            i_ARPROT   = s_axil.ar.prot,
            i_ARVALID  = s_axil.ar.valid,
            o_ARREADY  = s_axil.ar.ready,

            # R.
            o_RDATA    = s_axil.r.data,
            o_RRESP    = s_axil.r.resp,
            o_RVALID   = s_axil.r.valid,
            i_RREADY   = s_axil.r.ready,
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi4lite_gpio.sv"))


