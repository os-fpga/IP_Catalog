
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

# LiteX wrapper around RapidSilicon axi_spi_master.sv

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXI_SPI_MASTER ---------------------------------------------------------------------------------------
class AXISPIMASTER(Module):
    def __init__(self, platform, s_axi, buffer_depth = 8):
        
        self.logger = logging.getLogger("AXI_SPI_MASTER")
        
        # Clock Domain.
        clock_domain = s_axi.clock_domain
        self.logger.info(f"Clock Domain         : {clock_domain}")

        # Parameter Loggers
        addr_width = len(s_axi.aw.addr)
        self.logger.info(f"AXI4_ADDRESS_WIDTH   : {addr_width}")
        
        data_width = len(s_axi.r.data)
        self.logger.info(f"AXI4_RDATA_WIDTH     : {data_width}")
        
        data_width = len(s_axi.w.data)
        self.logger.info(f"AXI4_WDATA_WIDTH     : {data_width}")
        
        user_width = len(s_axi.aw.user)
        self.logger.info(f"AXI4_USER_WIDTH      : {user_width}")
        
        id_width = len(s_axi.b.id)
        self.logger.info(f"AXI4_ID_WIDTH        : {id_width}")
        
        self.logger.info(f"BUFFER_DEPTH         : {buffer_depth}")
        
        self.events_o      = Signal(2)
        self.spi_clk       = Signal()
        self.spi_csn0      = Signal()
        self.spi_csn1      = Signal()
        self.spi_csn2      = Signal()
        self.spi_csn3      = Signal()
        self.spi_mode      = Signal(2)
        self.spi_sdo0      = Signal()
        self.spi_sdo1      = Signal()
        self.spi_sdo2      = Signal()
        self.spi_sdo3      = Signal()
        self.spi_sdi0      = Signal()
        self.spi_sdi1      = Signal()
        self.spi_sdi2      = Signal()
        self.spi_sdi3      = Signal()
        

        # Module instance.
        # ----------------
        self.specials += Instance("axi_spi_master",
            # Parameters.
            # -----------
            # Global.
            p_AXI4_ADDRESS_WIDTH      = addr_width,
            p_AXI4_RDATA_WIDTH        = data_width,
            p_AXI4_WDATA_WIDTH        = data_width,
            p_AXI4_USER_WIDTH         = user_width,
            p_AXI4_ID_WIDTH           = id_width,
            p_BUFFER_DEPTH            = buffer_depth,

            # Clk / Rst.
            # ----------
            i_s_axi_aclk        = ClockSignal(),
            i_s_axi_aresetn     = ResetSignal(),

            # AXI Input
            # --------------------
            # AW
            i_s_axi_awid        = s_axi.aw.id,
            i_s_axi_awaddr      = s_axi.aw.addr,
            i_s_axi_awlen       = s_axi.aw.len,
            i_s_axi_awuser      = s_axi.aw.user,
            i_s_axi_awvalid     = s_axi.aw.valid,
            o_s_axi_awready     = s_axi.aw.ready,
            
            # W
            i_s_axi_wdata       = s_axi.w.data,
            i_s_axi_wstrb       = s_axi.w.strb,
            i_s_axi_wlast       = s_axi.w.last,
            i_s_axi_wuser       = s_axi.w.user,
            i_s_axi_wvalid      = s_axi.w.valid,
            o_s_axi_wready      = s_axi.w.ready,
            
            # B
            o_s_axi_bid         = s_axi.b.id,
            o_s_axi_bresp       = s_axi.b.resp,
            o_s_axi_buser       = s_axi.b.user,
            o_s_axi_bvalid      = s_axi.b.valid,
            i_s_axi_bready      = s_axi.b.ready,
            
            # AR
            i_s_axi_arid        = s_axi.ar.id,
            i_s_axi_araddr      = s_axi.ar.addr,
            i_s_axi_arlen       = s_axi.ar.len,
            i_s_axi_aruser      = s_axi.ar.user,
            i_s_axi_arvalid     = s_axi.ar.valid,
            o_s_axi_arready     = s_axi.ar.ready,
            
            # R
            o_s_axi_rid         = s_axi.r.id,
            o_s_axi_rdata       = s_axi.r.data,
            o_s_axi_rresp       = s_axi.r.resp,
            o_s_axi_rlast       = s_axi.r.last,
            o_s_axi_ruser       = s_axi.r.user,
            o_s_axi_rvalid      = s_axi.r.valid,
            i_s_axi_rready      = s_axi.r.ready,
            
            # SPI Interface
            # -------------
            o_events_o          = self.events_o,
            o_spi_clk           = self.spi_clk,
            o_spi_csn0          = self.spi_csn0,
            o_spi_csn1          = self.spi_csn1,
            o_spi_csn2          = self.spi_csn2,
            o_spi_csn3          = self.spi_csn3,
            o_spi_mode          = self.spi_mode,
            o_spi_sdo0          = self.spi_sdo0,
            o_spi_sdo1          = self.spi_sdo1,
            o_spi_sdo2          = self.spi_sdo2,
            o_spi_sdo3          = self.spi_sdo3,
            i_spi_sdi0          = self.spi_sdi0,
            i_spi_sdi1          = self.spi_sdi1,
            i_spi_sdi2          = self.spi_sdi2,
            i_spi_sdi3          = self.spi_sdi3,
            
        )
        
        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_spi_master.sv"))
