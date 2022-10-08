#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXI's axil_crossbar.v.

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)


# AXI LITE CROSSBAR ------------------------------------------------------------------------------------------
class AXILITECROSSBAR(Module):
    def __init__(self, platform, s_axil, m_axil, s_count, m_count):
        
        self.logger = logging.getLogger("AXI_LITE_CROSSBAR")
        
        self.logger.propagate = False

        # Clock Domain.
        clock_domain = s_axil[0].clock_domain
        self.logger.info(f"CLOCK_DOMAIN : {clock_domain}")
        
        # AXI Inputs (slave interfaces).
        s_count = len(s_axil)
        self.logger.info(f"S_COUNT      : {s_count}")
        
        # AXI outputs (master interfaces).
        m_count = len(m_axil)
        self.logger.info(f"M_COUNT      : {m_count}")
        
        # Data width.
        data_width = len(s_axil[0].w.data)
        self.logger.info(f"DATA_WIDTH   : {data_width}")

        # Address width.
        addr_width = len(s_axil[0].aw.addr)
        self.logger.info(f"ADDR_WIDTH   : {addr_width}")


        # Module instance.
        # ----------------

        self.specials += Instance("axil_crossbar",
            # Parameters.
            # -----------
            p_S_COUNT           = len(s_axil),
            p_M_COUNT           = len(m_axil),
            p_DATA_WIDTH        = data_width,
            p_ADDR_WIDTH        = addr_width,

            # Clk / Rst.
            # ----------
            i_clk               = ClockSignal(clock_domain),
            i_rst               = ResetSignal(clock_domain),

            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_s_axil_awaddr     = Cat(*[s_axi.aw.addr      for s_axi in s_axil]),
            i_s_axil_awprot     = Cat(*[s_axi.aw.prot      for s_axi in s_axil]),
            i_s_axil_awvalid    = Cat(*[s_axi.aw.valid     for s_axi in s_axil]),
            o_s_axil_awready    = Cat(*[s_axi.aw.ready     for s_axi in s_axil]),

            # W.
            i_s_axil_wdata      = Cat(*[s_axi.w.data      for s_axi in s_axil]),
            i_s_axil_wstrb      = Cat(*[s_axi.w.strb      for s_axi in s_axil]),
            i_s_axil_wvalid     = Cat(*[s_axi.w.valid     for s_axi in s_axil]),
            o_s_axil_wready     = Cat(*[s_axi.w.ready     for s_axi in s_axil]),

            # B.
            o_s_axil_bresp      = Cat(*[s_axi.b.resp      for s_axi in s_axil]),
            o_s_axil_bvalid     = Cat(*[s_axi.b.valid     for s_axi in s_axil]),
            i_s_axil_bready     = Cat(*[s_axi.b.ready     for s_axi in s_axil]),

            # AR.
            i_s_axil_araddr     = Cat(*[s_axi.ar.addr      for s_axi in s_axil]),
            i_s_axil_arprot     = Cat(*[s_axi.ar.prot      for s_axi in s_axil]),
            i_s_axil_arvalid    = Cat(*[s_axi.ar.valid     for s_axi in s_axil]),
            o_s_axil_arready    = Cat(*[s_axi.ar.ready     for s_axi in s_axil]),

            # R.
            o_s_axil_rdata      = Cat(*[s_axi.r.data      for s_axi in s_axil]),
            o_s_axil_rresp      = Cat(*[s_axi.r.resp      for s_axi in s_axil]),
            o_s_axil_rvalid     = Cat(*[s_axi.r.valid     for s_axi in s_axil]),
            i_s_axil_rready     = Cat(*[s_axi.r.ready     for s_axi in s_axil]),
            
            
            # AXI-Lite Master Interface.
            # -------------------------
            # AW.
            o_m_axil_awaddr     = Cat(*[m_axi.aw.addr      for m_axi in m_axil]),
            o_m_axil_awprot     = Cat(*[m_axi.aw.prot      for m_axi in m_axil]),
            o_m_axil_awvalid    = Cat(*[m_axi.aw.valid     for m_axi in m_axil]),
            i_m_axil_awready    = Cat(*[m_axi.aw.ready     for m_axi in m_axil]),

            # W.
            o_m_axil_wdata      = Cat(*[m_axi.w.data      for m_axi in m_axil]),
            o_m_axil_wstrb      = Cat(*[m_axi.w.strb      for m_axi in m_axil]),
            o_m_axil_wvalid     = Cat(*[m_axi.w.valid     for m_axi in m_axil]),
            o_m_axil_wready     = Cat(*[m_axi.w.ready     for m_axi in m_axil]),

            # B.
            i_m_axil_bresp      = Cat(*[m_axi.b.resp      for m_axi in m_axil]),
            i_m_axil_bvalid     = Cat(*[m_axi.b.valid     for m_axi in m_axil]),
            o_m_axil_bready     = Cat(*[m_axi.b.ready     for m_axi in m_axil]),

            # AR.
            o_m_axil_araddr     = Cat(*[m_axi.ar.addr      for m_axi in m_axil]),
            o_m_axil_arprot     = Cat(*[m_axi.ar.prot      for m_axi in m_axil]),
            o_m_axil_arvalid    = Cat(*[m_axi.ar.valid     for m_axi in m_axil]),
            i_m_axil_arready    = Cat(*[m_axi.ar.ready     for m_axi in m_axil]),

            # R.
            i_m_axil_rdata      = Cat(*[m_axi.r.data      for m_axi in m_axil]),
            i_m_axil_rresp      = Cat(*[m_axi.r.resp      for m_axi in m_axil]),
            i_m_axil_rvalid     = Cat(*[m_axi.r.valid     for m_axi in m_axil]),
            o_m_axil_rready     = Cat(*[m_axi.r.ready     for m_axi in m_axil])
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axil_crossbar.v"))
