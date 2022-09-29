
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

# LiteX wrapper around RapidSilicon axi_spi_slave.sv

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXI_SPI_SLAVE ---------------------------------------------------------------------------------------
class AXISPISLAVE(Module):
    def __init__(self, platform, m_axi, dummy_cycles = 32 ):
        
        self.logger = logging.getLogger("AXI_SPI_SLAVE")
        
        # Clock Domain.
        clock_domain = m_axi.clock_domain
        self.logger.info(f"Clock Domain     : {clock_domain}")

        # Parameter Loggers
        addr_width = len(m_axi.aw.addr)
        self.logger.info(f"AXI_ADDR_WIDTH   : {addr_width}")
        
        data_width = len(m_axi.r.data)
        self.logger.info(f"AXI_DATA_WIDTH   : {data_width}")
        
        user_width = len(m_axi.aw.user)
        self.logger.info(f"AXI_USER_WIDTH   : {user_width}")
        
        id_width = len(m_axi.b.id)
        self.logger.info(f"AXI_ID_WIDTH     : {id_width}")
        
        self.logger.info(f"DUMMY_CYCLES     : {dummy_cycles}")
        
        self.test_mode     = Signal()
        self.spi_sclk      = Signal()
        self.spi_cs        = Signal()
        self.spi_mode      = Signal(2)
        self.spi_sdi0      = Signal()
        self.spi_sdi1      = Signal()
        self.spi_sdi2      = Signal()
        self.spi_sdi3      = Signal()
        self.spi_sdo0      = Signal()
        self.spi_sdo1      = Signal()
        self.spi_sdo2      = Signal()
        self.spi_sdo3      = Signal()
        

        # Module instance.
        # ----------------
        self.specials += Instance("axi_spi_slave",
            # Parameters.
            # -----------
            # Global.
            p_AXI_ADDR_WIDTH    = addr_width,
            p_AXI_DATA_WIDTH    = data_width,
            p_AXI_USER_WIDTH    = user_width,
            p_AXI_ID_WIDTH      = id_width,
            p_DUMMY_CYCLES      = dummy_cycles,

            # Clk / Rst.
            # ----------
            i_axi_aclk      = ClockSignal(),
            i_axi_aresetn   = ResetSignal(),

            # AXI Master Interface
            # --------------------
            # AW
            o_axi_master_aw_valid     = m_axi.aw.valid,
            o_axi_master_aw_addr      = m_axi.aw.addr,
            o_axi_master_aw_prot      = m_axi.aw.prot,
            o_axi_master_aw_region    = m_axi.aw.region,
            o_axi_master_aw_len       = m_axi.aw.len,
            o_axi_master_aw_size      = m_axi.aw.size,
            o_axi_master_aw_burst     = m_axi.aw.burst,
            o_axi_master_aw_lock      = m_axi.aw.lock,
            o_axi_master_aw_cache     = m_axi.aw.cache,
            o_axi_master_aw_qos       = m_axi.aw.qos,
            o_axi_master_aw_id        = m_axi.aw.id,
            o_axi_master_aw_user      = m_axi.aw.user,
            i_axi_master_aw_ready     = m_axi.aw.ready,
            
            # W    
            o_axi_master_w_valid      = m_axi.w.valid,
            o_axi_master_w_data       = m_axi.w.data,
            o_axi_master_w_strb       = m_axi.w.strb,
            o_axi_master_w_user       = m_axi.w.user,
            o_axi_master_w_last       = m_axi.w.last,
            i_axi_master_w_ready      = m_axi.w.ready,
            
            # B
            i_axi_master_b_valid      = m_axi.b.valid,
            i_axi_master_b_resp       = m_axi.b.resp,
            i_axi_master_b_id         = m_axi.b.id, 
            i_axi_master_b_user       = m_axi.b.user,
            o_axi_master_b_ready      = m_axi.b.ready,
            
            # AR
            o_axi_master_ar_valid     = m_axi.ar.valid,
            o_axi_master_ar_addr      = m_axi.ar.addr,
            o_axi_master_ar_prot      = m_axi.ar.prot,
            o_axi_master_ar_region    = m_axi.ar.region,
            o_axi_master_ar_len       = m_axi.ar.len,
            o_axi_master_ar_size      = m_axi.ar.size,
            o_axi_master_ar_burst     = m_axi.ar.burst,
            o_axi_master_ar_lock      = m_axi.ar.lock,
            o_axi_master_ar_cache     = m_axi.ar.cache,
            o_axi_master_ar_qos       = m_axi.ar.qos,
            o_axi_master_ar_id        = m_axi.ar.id,
            o_axi_master_ar_user      = m_axi.ar.user,
            i_axi_master_ar_ready     = m_axi.ar.ready,
            
            # R
            i_axi_master_r_valid      = m_axi.r.valid,
            i_axi_master_r_data       = m_axi.r.data,
            i_axi_master_r_resp       = m_axi.r.resp,
            i_axi_master_r_last       = m_axi.r.last,
            i_axi_master_r_id         = m_axi.r.id, 
            i_axi_master_r_user       = m_axi.r.user,
            o_axi_master_r_ready      = m_axi.r.ready,
            
            # SPI Interface
            # -------------
            i_test_mode         = self.test_mode,
            i_spi_sclk          = self.spi_sclk,
            i_spi_cs            = self.spi_cs,
            o_spi_mode          = self.spi_mode,
            i_spi_sdi0          = self.spi_sdi0,
            i_spi_sdi1          = self.spi_sdi1,
            i_spi_sdi2          = self.spi_sdi2,
            i_spi_sdi3          = self.spi_sdi3,
            o_spi_sdo0          = self.spi_sdo0,
            o_spi_sdo1          = self.spi_sdo1,
            o_spi_sdo2          = self.spi_sdo2,
            o_spi_sdo3          = self.spi_sdo3,
            
        )
        
        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_spi_slave.sv"))
