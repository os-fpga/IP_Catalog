#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around jtag_to_axi_top.v

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# JTAG_AXILIT ---------------------------------------------------------------------------------
class JTAGAXI(Module):
    def __init__(self, platform, m_axi):
        
        self.logger = logging.getLogger("JTAG_TO_AXI")
        
        self.logger.propagate = False
        
        # Clock Domain.
        clock_domain = m_axi[0].clock_domain
        self.logger.info(f"CLOCK_DOMAIN : {clock_domain}")

        # Address width.
        address_width = len(m_axi[0].aw.addr)
        self.logger.info(f"ADDR_WIDTH   : {address_width}")

        # Data width.
        data_width = len(m_axi[0].w.data)
        self.logger.info(f"DATA_WIDTH   : {data_width}")

        # ID width.
        m_id_width = len(m_axi[0].aw.id)
        self.logger.info(f"M_ID_WIDTH   : {m_id_width}")

        # AW User width.
        aw_user_width = len(m_axi[0].aw.user)
        self.logger.info(f"AWUSER_WIDTH : {aw_user_width}")
        
        # W User width.
        w_user_width = len(m_axi[0].w.user)
        self.logger.info(f"WUSER_WIDTH  : {w_user_width}")
        
        # B User width.
        b_user_width = len(m_axi[0].b.user)
        self.logger.info(f"BUSER_WIDTH  : {b_user_width}")
        
        # AR User width.
        ar_user_width = len(m_axi[0].ar.user)
        self.logger.info(f"ARUSER_WIDTH : {ar_user_width}")
        
        # R User width.
        r_user_width = len(m_axi[0].r.user)
        self.logger.info(f"RUSER_WIDTH  : {r_user_width}")
        
        self.JTAG_TCK              = Signal(1)
        self.JTAG_TMS              = Signal(1)
        self.JTAG_TDI              = Signal(1)
        self.JTAG_TDO              = Signal(1)
        self.JTAG_TRST             = Signal(1)

        # Module instance.
        # ----------------
        self.specials += Instance("jtag_to_axi_top",
            # Parameters.
            # -----------
            p_C_S_AXI_ID_WIDTH      = Instance.PreformattedParam(m_id_width),
            p_C_S_AXI_DATA_WIDTH    = Instance.PreformattedParam(data_width),
            p_C_S_AXI_ADDR_WIDTH    = Instance.PreformattedParam(address_width),
            p_C_S_AXI_AWUSER_WIDTH  = Instance.PreformattedParam(aw_user_width),
            p_C_S_AXI_ARUSER_WIDTH  = Instance.PreformattedParam(ar_user_width),
            p_C_S_AXI_WUSER_WIDTH   = Instance.PreformattedParam(w_user_width),
            p_C_S_AXI_RUSER_WIDTH   = Instance.PreformattedParam(r_user_width),
            p_C_S_AXI_BUSER_WIDTH   = Instance.PreformattedParam(b_user_width),

            # Clk / Rst.
            # ----------
            i_ACLK              = ClockSignal(),
            i_ARESETN           = ResetSignal(),
            
            i_JTAG_TCK = self.JTAG_TCK,
            i_JTAG_TMS = self.JTAG_TMS,
            i_JTAG_TDI = self.JTAG_TDI,
            o_JTAG_TDO = self.JTAG_TDO,
            i_JTAG_TRST =self.JTAG_TRST,
            
            # AXI Master Interfaces.
            # ----------------------
            # AW.
            o_aw_id     = m_axi[0].aw.id,
            o_aw_addr   = m_axi[0].aw.addr,
            o_aw_len    = m_axi[0].aw.len,
            o_aw_size   = m_axi[0].aw.size,
            o_aw_burst  = m_axi[0].aw.burst,
            o_aw_lock   = m_axi[0].aw.lock,
            o_aw_cache  = m_axi[0].aw.cache,
            o_aw_prot   = m_axi[0].aw.prot,
            o_aw_qos    = m_axi[0].aw.qos,
            o_aw_region = m_axi[0].aw.region,
            o_aw_user   = m_axi[0].aw.user,
            o_aw_valid  = m_axi[0].aw.valid,
            i_aw_ready  = m_axi[0].aw.ready,

            # W.
            o_w_data    = m_axi[0].w.data,
            o_w_strb    = m_axi[0].w.strb,
            o_w_last    = m_axi[0].w.last,
            o_w_user    = m_axi[0].w.user,
            o_w_valid   = m_axi[0].w.valid,
            i_w_ready   = m_axi[0].w.ready,

            # B.
            i_b_id      = m_axi[0].b.id,
            i_b_resp    = m_axi[0].b.resp,
            i_b_user    = m_axi[0].b.user,
            i_b_valid   = m_axi[0].b.valid,
            o_b_ready   = m_axi[0].b.ready,

            # AR.
            o_ar_id     = m_axi[0].ar.id,
            o_ar_addr   = m_axi[0].ar.addr,
            o_ar_len    = m_axi[0].ar.len,
            o_ar_size   = m_axi[0].ar.size,
            o_ar_burst  = m_axi[0].ar.burst,
            o_ar_lock   = m_axi[0].ar.lock,
            o_ar_cache  = m_axi[0].ar.cache,
            o_ar_prot   = m_axi[0].ar.prot,
            o_ar_qos    = m_axi[0].ar.qos,
            o_ar_region = m_axi[0].ar.region,
            o_ar_user   = m_axi[0].ar.user,
            o_ar_valid  = m_axi[0].ar.valid,
            i_ar_ready  = m_axi[0].ar.ready,

            # R.
            i_r_id      = m_axi[0].r.id,
            i_r_data    = m_axi[0].r.data,
            i_r_resp    = m_axi[0].r.resp,
            i_r_last    = m_axi[0].r.last,
            i_r_user    = m_axi[0].r.user,
            i_r_valid   = m_axi[0].r.valid,
            o_r_ready   = m_axi[0].r.ready,
        )
        
        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "jtag_to_axi_top.v"))
