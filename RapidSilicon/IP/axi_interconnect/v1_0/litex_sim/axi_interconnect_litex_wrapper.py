#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

# LiteX wrapper around Alex Forencich Verilog-AXI's axi_interconnect.v

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXI Interconnect ---------------------------------------------------------------------------------
class AXIINTERCONNECT(Module):
    def __init__(self, platform, s_axi, m_axi, s_count, m_count, aw_user_en, w_user_en,
        b_user_en, ar_user_en, r_user_en):
        
        self.logger = logging.getLogger("AXI_INTERCONNECT")
        
        self.logger.propagate = False

        # AXI Inputs (slave interfaces).
        s_count = len(s_axi)
        self.logger.info(f"S_COUNT      : {s_count}")
        
        # AXI outputs (master interfaces).
        m_count = len(m_axi)
        self.logger.info(f"M_COUNT      : {m_count}")
        
        # Clock Domain.
        clock_domain = s_axi[0].clock_domain
        self.logger.info(f"CLOCK_DOMAIN : {clock_domain}")

        # Address width.
        address_width = len(s_axi[0].aw.addr)
        self.logger.info(f"ADDR_WIDTH   : {address_width}")

        # Data width.
        data_width = len(s_axi[0].w.data)
        self.logger.info(f"DATA_WIDTH   : {data_width}")

        # ID width.
        id_width = len(s_axi[0].aw.id)
        self.logger.info(f"ID_WIDTH     : {id_width}")

        # AW User width.
        aw_user_width = len(s_axi[0].aw.user)
        self.logger.info(f"AWUSER_WIDTH : {aw_user_width}")
        
        # W User width.
        w_user_width = len(s_axi[0].w.user)
        self.logger.info(f"WUSER_WIDTH  : {w_user_width}")
        
        # B User width.
        b_user_width = len(s_axi[0].b.user)
        self.logger.info(f"BUSER_WIDTH  : {b_user_width}")
        
        # AR User width.
        ar_user_width = len(s_axi[0].ar.user)
        self.logger.info(f"ARUSER_WIDTH : {ar_user_width}")
        
        # R User width.
        r_user_width = len(s_axi[0].r.user)
        self.logger.info(f"RUSER_WIDTH  : {r_user_width}")


        # Module instance.
        # ----------------
        self.specials += Instance("axi_interconnect",
            # Parameters.
            # -----------
            p_S_COUNT       = len(s_axi),
            p_M_COUNT       = len(m_axi),
            p_DATA_WIDTH    = data_width,
            p_ADDR_WIDTH    = address_width,
            p_ID_WIDTH      = id_width,

            p_AWUSER_ENABLE = aw_user_en,
            p_AWUSER_WIDTH  = aw_user_width,
            p_WUSER_ENABLE  = w_user_en,
            p_WUSER_WIDTH   = w_user_width,
            p_BUSER_ENABLE  = b_user_en,
            p_BUSER_WIDTH   = b_user_width,
            p_ARUSER_ENABLE = ar_user_en,
            p_ARUSER_WIDTH  = ar_user_width,
            p_RUSER_ENABLE  = r_user_en,
            p_RUSER_WIDTH   = r_user_width,

            # Clk / Rst.
            # ----------
            i_clk           = ClockSignal(),
            i_rst           = ResetSignal(),

            # AXI Slave Interfaces.
            # --------------------
            # AW.
            i_s_axi_awid     = Cat(*[s_axi.aw.id        for s_axi in s_axi]),
            i_s_axi_awaddr   = Cat(*[s_axi.aw.addr      for s_axi in s_axi]),
            i_s_axi_awlen    = Cat(*[s_axi.aw.len       for s_axi in s_axi]),
            i_s_axi_awsize   = Cat(*[s_axi.aw.size      for s_axi in s_axi]),
            i_s_axi_awburst  = Cat(*[s_axi.aw.burst     for s_axi in s_axi]),
            i_s_axi_awlock   = Cat(*[s_axi.aw.lock      for s_axi in s_axi]),
            i_s_axi_awcache  = Cat(*[s_axi.aw.cache     for s_axi in s_axi]),
            i_s_axi_awprot   = Cat(*[s_axi.aw.prot      for s_axi in s_axi]),
            i_s_axi_awqos    = Cat(*[s_axi.aw.qos       for s_axi in s_axi]),
            i_s_axi_awuser   = Cat(*[s_axi.aw.user      for s_axi in s_axi]),
            i_s_axi_awvalid  = Cat(*[s_axi.aw.valid     for s_axi in s_axi]),
            o_s_axi_awready  = Cat(*[s_axi.aw.ready     for s_axi in s_axi]),

            # W.
            i_s_axi_wdata    = Cat(*[s_axi.w.data       for s_axi in s_axi]),
            i_s_axi_wstrb    = Cat(*[s_axi.w.strb       for s_axi in s_axi]),
            i_s_axi_wlast    = Cat(*[s_axi.w.last       for s_axi in s_axi]),
            i_s_axi_wuser    = Cat(*[s_axi.w.user       for s_axi in s_axi]),
            i_s_axi_wvalid   = Cat(*[s_axi.w.valid      for s_axi in s_axi]),
            o_s_axi_wready   = Cat(*[s_axi.w.ready      for s_axi in s_axi]),

            # B.
            o_s_axi_bid      = Cat(*[s_axi.b.id         for s_axi in s_axi]),
            o_s_axi_bresp    = Cat(*[s_axi.b.resp       for s_axi in s_axi]),
            o_s_axi_buser    = Cat(*[s_axi.b.user       for s_axi in s_axi]),
            o_s_axi_bvalid   = Cat(*[s_axi.b.valid      for s_axi in s_axi]),
            i_s_axi_bready   = Cat(*[s_axi.b.ready      for s_axi in s_axi]),

            # AR.
            i_s_axi_arid     = Cat(*[s_axi.ar.id        for s_axi in s_axi]),
            i_s_axi_araddr   = Cat(*[s_axi.ar.addr      for s_axi in s_axi]),
            i_s_axi_arlen    = Cat(*[s_axi.ar.len       for s_axi in s_axi]),
            i_s_axi_arsize   = Cat(*[s_axi.ar.size      for s_axi in s_axi]),
            i_s_axi_arburst  = Cat(*[s_axi.ar.burst     for s_axi in s_axi]),
            i_s_axi_arlock   = Cat(*[s_axi.ar.lock      for s_axi in s_axi]),
            i_s_axi_arcache  = Cat(*[s_axi.ar.cache     for s_axi in s_axi]),
            i_s_axi_arprot   = Cat(*[s_axi.ar.prot      for s_axi in s_axi]),
            i_s_axi_arqos    = Cat(*[s_axi.ar.qos       for s_axi in s_axi]),
            i_s_axi_aruser   = Cat(*[s_axi.ar.user      for s_axi in s_axi]),
            i_s_axi_arvalid  = Cat(*[s_axi.ar.valid     for s_axi in s_axi]),
            o_s_axi_arready  = Cat(*[s_axi.ar.ready     for s_axi in s_axi]),

            # R.
            o_s_axi_rid      = Cat(*[s_axi.r.id         for s_axi in s_axi]),
            o_s_axi_rdata    = Cat(*[s_axi.r.data       for s_axi in s_axi]),
            o_s_axi_rresp    = Cat(*[s_axi.r.resp       for s_axi in s_axi]),
            o_s_axi_rlast    = Cat(*[s_axi.r.last       for s_axi in s_axi]),
            o_s_axi_ruser    = Cat(*[s_axi.r.user       for s_axi in s_axi]),
            o_s_axi_rvalid   = Cat(*[s_axi.r.valid      for s_axi in s_axi]),
            i_s_axi_rready   = Cat(*[s_axi.r.ready      for s_axi in s_axi]),

            # AXI Master Interfaces.
            # ----------------------
            # AW.
            o_m_axi_awid     = Cat(*[m_axi.aw.id        for m_axi in m_axi]),
            o_m_axi_awaddr   = Cat(*[m_axi.aw.addr      for m_axi in m_axi]),
            o_m_axi_awlen    = Cat(*[m_axi.aw.len       for m_axi in m_axi]),
            o_m_axi_awsize   = Cat(*[m_axi.aw.size      for m_axi in m_axi]),
            o_m_axi_awburst  = Cat(*[m_axi.aw.burst     for m_axi in m_axi]),
            o_m_axi_awlock   = Cat(*[m_axi.aw.lock      for m_axi in m_axi]),
            o_m_axi_awcache  = Cat(*[m_axi.aw.cache     for m_axi in m_axi]),
            o_m_axi_awprot   = Cat(*[m_axi.aw.prot      for m_axi in m_axi]),
            o_m_axi_awqos    = Cat(*[m_axi.aw.qos       for m_axi in m_axi]),
            o_m_axi_awregion = Cat(*[m_axi.aw.region    for m_axi in m_axi]),
            o_m_axi_awuser   = Cat(*[m_axi.aw.user      for m_axi in m_axi]),
            o_m_axi_awvalid  = Cat(*[m_axi.aw.valid     for m_axi in m_axi]),
            i_m_axi_awready  = Cat(*[m_axi.aw.ready     for m_axi in m_axi]),

            # W.
            o_m_axi_wdata    = Cat(*[m_axi.w.data       for m_axi in m_axi]),
            o_m_axi_wstrb    = Cat(*[m_axi.w.strb       for m_axi in m_axi]),
            o_m_axi_wlast    = Cat(*[m_axi.w.last       for m_axi in m_axi]),
            o_m_axi_wuser    = Cat(*[m_axi.w.user       for m_axi in m_axi]),
            o_m_axi_wvalid   = Cat(*[m_axi.w.valid      for m_axi in m_axi]),
            i_m_axi_wready   = Cat(*[m_axi.w.ready      for m_axi in m_axi]),

            # B.
            i_m_axi_bid      = Cat(*[m_axi.b.id         for m_axi in m_axi]),
            i_m_axi_bresp    = Cat(*[m_axi.b.resp       for m_axi in m_axi]),
            i_m_axi_buser    = Cat(*[m_axi.b.user       for m_axi in m_axi]),
            i_m_axi_bvalid   = Cat(*[m_axi.b.valid      for m_axi in m_axi]),
            o_m_axi_bready   = Cat(*[m_axi.b.ready      for m_axi in m_axi]),

            # AR.
            o_m_axi_arid     = Cat(*[m_axi.ar.id        for m_axi in m_axi]),
            o_m_axi_araddr   = Cat(*[m_axi.ar.addr      for m_axi in m_axi]),
            o_m_axi_arlen    = Cat(*[m_axi.ar.len       for m_axi in m_axi]),
            o_m_axi_arsize   = Cat(*[m_axi.ar.size      for m_axi in m_axi]),
            o_m_axi_arburst  = Cat(*[m_axi.ar.burst     for m_axi in m_axi]),
            o_m_axi_arlock   = Cat(*[m_axi.ar.lock      for m_axi in m_axi]),
            o_m_axi_arcache  = Cat(*[m_axi.ar.cache     for m_axi in m_axi]),
            o_m_axi_arprot   = Cat(*[m_axi.ar.prot      for m_axi in m_axi]),
            o_m_axi_arqos    = Cat(*[m_axi.ar.qos       for m_axi in m_axi]),
            o_m_axi_arregion = Cat(*[m_axi.ar.region    for m_axi in m_axi]),
            o_m_axi_aruser   = Cat(*[m_axi.ar.user      for m_axi in m_axi]),
            o_m_axi_arvalid  = Cat(*[m_axi.ar.valid     for m_axi in m_axi]),
            i_m_axi_arready  = Cat(*[m_axi.ar.ready     for m_axi in m_axi]),

            # R.
            i_m_axi_rid      = Cat(*[m_axi.r.id         for m_axi in m_axi]),
            i_m_axi_rdata    = Cat(*[m_axi.r.data       for m_axi in m_axi]),
            i_m_axi_rresp    = Cat(*[m_axi.r.resp       for m_axi in m_axi]),
            i_m_axi_rlast    = Cat(*[m_axi.r.last       for m_axi in m_axi]),
            i_m_axi_ruser    = Cat(*[m_axi.r.user       for m_axi in m_axi]),
            i_m_axi_rvalid   = Cat(*[m_axi.r.valid      for m_axi in m_axi]),
            o_m_axi_rready   = Cat(*[m_axi.r.ready      for m_axi in m_axi]),
        )
        
        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_interconnect.v"))
