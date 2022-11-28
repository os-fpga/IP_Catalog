#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Dan Gisselquist ZipCPU/wb2axip's axi2axilite.v

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXI_2_AXILITE_BRIDGE ---------------------------------------------------------------------------------------
class AXI2AXILITE(Module):
    def __init__(self, platform, s_axi, m_axi):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("AXI_2_AXILITE")
        
        self.logger.propagate = False

        # Clock Domain.
        self.logger.info(f"CLOCK_DOMAIN     : {s_axi.clock_domain}")

        # Address width.
        address_width = len(s_axi.aw.addr)
        self.logger.info(f"C_AXI_ADDR_WIDTH : {address_width}")

        # Data width.
        data_width = len(s_axi.w.data)
        self.logger.info(f"C_AXI_DATA_WIDTH : {data_width}")

        # ID width.
        id_width = len(s_axi.aw.id)
        self.logger.info(f"C_AXI_ID_WIDTH   : {id_width}")

        # Module instance.
        # ----------------
        self.specials += Instance("axi2axilite",
            # Parameters.
            # -----------
            # Global AXI
            p_C_AXI_DATA_WIDTH      = Instance.PreformattedParam(data_width),
            p_C_AXI_ADDR_WIDTH      = Instance.PreformattedParam(address_width),
            p_C_AXI_ID_WIDTH        = Instance.PreformattedParam(id_width),  

            # Clk / Rst.
            i_S_AXI_ACLK            = ClockSignal(),
            i_S_AXI_ARESETN         = ResetSignal(),

            # AXI Slave Interface.
            # --------------------
            # AW.
            i_S_AXI_AWID            = s_axi.aw.id,
            i_S_AXI_AWADDR          = s_axi.aw.addr,
            i_S_AXI_AWLEN           = s_axi.aw.len,
            i_S_AXI_AWSIZE          = s_axi.aw.size,
            i_S_AXI_AWBURST         = s_axi.aw.burst,
            i_S_AXI_AWLOCK          = s_axi.aw.lock,
            i_S_AXI_AWCACHE         = s_axi.aw.cache,
            i_S_AXI_AWPROT          = s_axi.aw.prot,
            i_S_AXI_AWQOS           = s_axi.aw.qos,
            i_S_AXI_AWVALID         = s_axi.aw.valid,
            o_S_AXI_AWREADY         = s_axi.aw.ready,

            # W.
            i_S_AXI_WDATA           = s_axi.w.data,
            i_S_AXI_WSTRB           = s_axi.w.strb,
            i_S_AXI_WLAST           = s_axi.w.last,
            i_S_AXI_WVALID          = s_axi.w.valid,
            o_S_AXI_WREADY          = s_axi.w.ready,

            # B.
            o_S_AXI_BID             = s_axi.b.id,
            o_S_AXI_BRESP           = s_axi.b.resp,
            o_S_AXI_BVALID          = s_axi.b.valid,
            i_S_AXI_BREADY          = s_axi.b.ready,

            # AR.
            i_S_AXI_ARID            = s_axi.ar.id,
            i_S_AXI_ARADDR          = s_axi.ar.addr,
            i_S_AXI_ARLEN           = s_axi.ar.len,
            i_S_AXI_ARSIZE          = s_axi.ar.size,
            i_S_AXI_ARBURST         = s_axi.ar.burst,
            i_S_AXI_ARLOCK          = s_axi.ar.lock,
            i_S_AXI_ARCACHE         = s_axi.ar.cache,
            i_S_AXI_ARPROT          = s_axi.ar.prot,
            i_S_AXI_ARQOS           = s_axi.ar.qos,
            i_S_AXI_ARVALID         = s_axi.ar.valid,
            o_S_AXI_ARREADY         = s_axi.ar.ready,

            # R.
            o_S_AXI_RID             = s_axi.r.id,
            o_S_AXI_RDATA           = s_axi.r.data,
            o_S_AXI_RRESP           = s_axi.r.resp,
            o_S_AXI_RLAST           = s_axi.r.last,
            o_S_AXI_RVALID          = s_axi.r.valid,
            i_S_AXI_RREADY          = s_axi.r.ready,
            
            
            # AXI LITE master Interface.
            # --------------------
            # AW.
            o_M_AXI_AWADDR          = m_axi.aw.addr,
            o_M_AXI_AWPROT          = m_axi.aw.prot,
            o_M_AXI_AWVALID         = m_axi.aw.valid,
            i_M_AXI_AWREADY         = m_axi.aw.ready,

            # W.
            o_M_AXI_WDATA           = m_axi.w.data,
            o_M_AXI_WSTRB           = m_axi.w.strb,
            o_M_AXI_WVALID          = m_axi.w.valid,
            i_M_AXI_WREADY          = m_axi.w.ready,

            # B.
            i_M_AXI_BRESP           = m_axi.b.resp,
            i_M_AXI_BVALID          = m_axi.b.valid,
            o_M_AXI_BREADY          = m_axi.b.ready,

            # AR.
            o_M_AXI_ARADDR          = m_axi.ar.addr,
            o_M_AXI_ARPROT          = m_axi.ar.prot,
            o_M_AXI_ARVALID         = m_axi.ar.valid,
            i_M_AXI_ARREADY         = m_axi.ar.ready,

            # R.
            i_M_AXI_RDATA           = m_axi.r.data,
            i_M_AXI_RRESP           = m_axi.r.resp,
            i_M_AXI_RVALID          = m_axi.r.valid,
            o_M_AXI_RREADY          = m_axi.r.ready,

        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi2axilite.v"))
