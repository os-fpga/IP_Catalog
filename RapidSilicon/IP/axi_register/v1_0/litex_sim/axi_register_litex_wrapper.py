
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

# LiteX wrapper around RapidSilicon axi_register

import os
import logging
import math

from migen import *

from litex.soc.interconnect.axi import *


logging.basicConfig(level=logging.INFO)

# AXI DP RAM ---------------------------------------------------------------------------------------
class AXIREGISTER(Module):
    def __init__(self, platform, s_axi, size=1024,
        aw_user_width       = False,
        w_user_width        = False,
        b_user_width        = False,
        ar_user_width       = False,
        r_user_width        = False,
        
        aw_reg_type         = False,
        w_reg_type          = False,
        b_reg_type          = False,
        ar_reg_type         = False,
        r_reg_type          = False
    ):
        self.logger = logging.getLogger("AXI_REGISTER")

        # Get/Check Parameters.
        # ---------------------

        # Clock Domain.
        self.logger.info(f"Clock Domain: {s_axi.clock_domain}")

        # Address width.
        address_width = len(s_axi.aw.addr)
        self.logger.info(f"Address Width: {address_width}")

        # Data width.
        data_width = len(s_axi.w.data)
        self.logger.info(f"Data Width: {data_width}")
        
        # Size.
        self.logger.info(f"Size: {size}bytes")

        # ID width.
        id_width = len(s_axi.aw.id)
        self.logger.info(f"ID Width: {id_width}")

        # Channels Width
        self.logger.info(f"AWUSER_WIDTH : {aw_user_width}")
        self.logger.info(f"WUSER_WIDTH  : {w_user_width}")
        self.logger.info(f"BUSER_WIDTH  : {b_user_width}")
        self.logger.info(f"ARUSER_WIDTH : {ar_user_width}")
        self.logger.info(f"RUSER_WIDTH  : {r_user_width}")
        
        # Channel Reg Type
        self.logger.info(f"AW_REG_TYPE : {aw_reg_type}")
        self.logger.info(f"W_REG_TYPE  : {w_reg_type}")
        self.logger.info(f"B_REG_TYPE  : {b_reg_type}")
        self.logger.info(f"AR_REG_TYPE : {ar_reg_type}")
        self.logger.info(f"R_REG_TYPE  : {r_reg_type}")

        # Module instance.
        # ----------------

        self.specials += Instance("axi_register",
            # Parameters.
            # -----------
            # Global.
            p_DATA_WIDTH        = data_width,
            p_ADDR_WIDTH        = math.ceil(math.log2(size)),
            p_ID_WIDTH          = id_width,

            # Channels Width
            p_AWUSER_WIDTH      = aw_user_width,
            p_WUSER_WIDTH       = w_user_width,
            p_BUSER_WIDTH       = b_user_width,
            p_ARUSER_WIDTH      = ar_user_width,
            p_RUSER_WIDTH       = r_user_width,
            
            # Channel Reg Type
            p_AW_REG_TYPE      = aw_reg_type,
            p_W_REG_TYPE       = w_reg_type,
            p_B_REG_TYPE       = b_reg_type,
            p_AR_REG_TYPE      = ar_reg_type,
            p_R_REG_TYPE       = r_reg_type,

            # Clk / Rst.
            # ----------
            i_clk = ClockSignal(s_axi.clock_domain),
            i_rst = ResetSignal(s_axi.clock_domain),

            # AXI A Slave Interface.
            # --------------------
            # AW.
            i_s_axi_awid     = s_axi.aw.id,
            i_s_axi_awaddr   = s_axi.aw.addr,
            i_s_axi_awlen    = s_axi.aw.len,
            i_s_axi_awsize   = s_axi.aw.size,
            i_s_axi_awburst  = s_axi.aw.burst,
            i_s_axi_awlock   = s_axi.aw.lock,
            i_s_axi_awcache  = s_axi.aw.cache,
            i_s_axi_awprot   = s_axi.aw.prot,
            i_s_axi_awvalid  = s_axi.aw.valid,
            o_s_axi_awready  = s_axi.aw.ready,

            # W.
            i_s_axi_wdata    = s_axi.w.data,
            i_s_axi_wstrb    = s_axi.w.strb,
            i_s_axi_wlast    = s_axi.w.last,
            i_s_axi_wvalid   = s_axi.w.valid,
            o_s_axi_wready   = s_axi.w.ready,

            # B.
            o_s_axi_bid      = s_axi.b.id,
            o_s_axi_bresp    = s_axi.b.resp,
            o_s_axi_bvalid   = s_axi.b.valid,
            i_s_axi_bready   = s_axi.b.ready,

            # AR.
            i_s_axi_arid     = s_axi.ar.id,
            i_s_axi_araddr   = s_axi.ar.addr,
            i_s_axi_arlen    = s_axi.ar.len,
            i_s_axi_arsize   = s_axi.ar.size,
            i_s_axi_arburst  = s_axi.ar.burst,
            i_s_axi_arlock   = s_axi.ar.lock,
            i_s_axi_arcache  = s_axi.ar.cache,
            i_s_axi_arprot   = s_axi.ar.prot,
            i_s_axi_arvalid  = s_axi.ar.valid,
            o_s_axi_arready  = s_axi.ar.ready,

            # R.
            o_s_axi_rid      = s_axi.r.id,
            o_s_axi_rdata    = s_axi.r.data,
            o_s_axi_rresp    = s_axi.r.resp,
            o_s_axi_rlast    = s_axi.r.last,
            o_s_axi_rvalid   = s_axi.r.valid,
            i_s_axi_rready   = s_axi.r.ready,

        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_register.v"))
