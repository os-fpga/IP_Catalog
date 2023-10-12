#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXI's axi_cdma.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')


# AXI CDMA ---------------------------------------------------------------------------------------
class AXICDMA(Module):
    def __init__(self, platform, m_axi, 
        axi_max_burst_len   = 16,
        len_width           = 20,
        tag_width           = 8,
        enable_unaligned    = 0
        ):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("AXI_CDMA")
        
        self.logger.propagate = True

        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Clock Domain.
        self.logger.info(f"Clock Domain     : {m_axi.clock_domain}")

        # Address width.
        address_width = len(m_axi.aw.addr)
        self.logger.info(f"AXI_ADDR_WIDTH   : {address_width}")

        # Data width.
        data_width = len(m_axi.w.data)
        self.logger.info(f"AXI_DATA_WIDTH   : {data_width}")

        # ID width.
        id_width = len(m_axi.aw.id)
        self.logger.info(f"AXI_ID_WIDTH     : {id_width}")
        
        # Other Parameters
        self.logger.info(f"AXI_MAX_BURST_LEN: {axi_max_burst_len}")
        self.logger.info(f"LEN_WIDTH        : {len_width}")
        self.logger.info(f"TAG_WIDTH        : {tag_width}")
        self.logger.info(f"ENABLE_UNALIGNED : {enable_unaligned}")

        self.logger.info(f"===================================================")
        
        # Non-Stnadard IOs
        self.s_axis_desc_read_addr      = Signal(address_width)
        self.s_axis_desc_write_addr     = Signal(address_width)
        self.s_axis_desc_tag            = Signal(tag_width)
        self.s_axis_desc_len            = Signal(len_width)
        self.s_axis_desc_valid          = Signal()
        self.s_axis_desc_ready          = Signal()
        self.m_axis_desc_status_tag     = Signal(tag_width)
        self.m_axis_desc_status_error   = Signal(4)
        self.m_axis_desc_status_valid   = Signal()
        self.enable                     = Signal()

        # Module instance.
        # ----------------
        self.specials += Instance("axi_cdma",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE                   = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID                     = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION                = Instance.PreformattedParam("IP_VERSION"),
            # Global AXI
            p_AXI_DATA_WIDTH            = Instance.PreformattedParam(data_width),
            p_AXI_ADDR_WIDTH            = Instance.PreformattedParam(address_width),
            p_AXI_ID_WIDTH              = Instance.PreformattedParam(id_width),

            # IP Params.
            p_AXI_MAX_BURST_LEN         = Instance.PreformattedParam(axi_max_burst_len),    
            p_LEN_WIDTH                 = Instance.PreformattedParam(len_width),
            p_TAG_WIDTH                 = Instance.PreformattedParam(tag_width),
            p_ENABLE_UNALIGNED          = enable_unaligned,    

            # Clk / Rst.
            i_clk                       = ClockSignal(m_axi.clock_domain),
            i_rst                       = ResetSignal(m_axi.clock_domain),

            # Configuration
            i_enable                    = self.enable,
            
            # AXI read descriptor input
            i_s_axis_desc_read_addr     = self.s_axis_desc_read_addr,
            i_s_axis_desc_write_addr    = self.s_axis_desc_write_addr,
            i_s_axis_desc_tag           = self.s_axis_desc_tag,
            i_s_axis_desc_len           = self.s_axis_desc_len,
            i_s_axis_desc_valid         = self.s_axis_desc_valid,
            o_s_axis_desc_ready         = self.s_axis_desc_ready,

            o_m_axis_desc_status_tag    = self.m_axis_desc_status_tag,
            o_m_axis_desc_status_error  = self.m_axis_desc_status_error,
            o_m_axis_desc_status_valid  = self.m_axis_desc_status_valid,

            # AXI master Interface.
            # --------------------
            # AW.
            o_m_axi_awid                = m_axi.aw.id,
            o_m_axi_awaddr              = m_axi.aw.addr,
            o_m_axi_awlen               = m_axi.aw.len,
            o_m_axi_awsize              = m_axi.aw.size,
            o_m_axi_awburst             = m_axi.aw.burst,
            o_m_axi_awlock              = m_axi.aw.lock,
            o_m_axi_awcache             = m_axi.aw.cache,
            o_m_axi_awprot              = m_axi.aw.prot,
            o_m_axi_awvalid             = m_axi.aw.valid,
            i_m_axi_awready             = m_axi.aw.ready,

            # W.
            o_m_axi_wdata               = m_axi.w.data,
            o_m_axi_wstrb               = m_axi.w.strb,
            o_m_axi_wlast               = m_axi.w.last,
            o_m_axi_wvalid              = m_axi.w.valid,
            i_m_axi_wready              = m_axi.w.ready,

            # B.
            i_m_axi_bid                 = m_axi.b.id,
            i_m_axi_bresp               = m_axi.b.resp,
            i_m_axi_bvalid              = m_axi.b.valid,
            o_m_axi_bready              = m_axi.b.ready,

            # AR.
            o_m_axi_arid                = m_axi.ar.id,
            o_m_axi_araddr              = m_axi.ar.addr,
            o_m_axi_arlen               = m_axi.ar.len,
            o_m_axi_arsize              = m_axi.ar.size,
            o_m_axi_arburst             = m_axi.ar.burst,
            o_m_axi_arlock              = m_axi.ar.lock,
            o_m_axi_arcache             = m_axi.ar.cache,
            o_m_axi_arprot              = m_axi.ar.prot,
            o_m_axi_arvalid             = m_axi.ar.valid,
            i_m_axi_arready             = m_axi.ar.ready,

            # R.
            i_m_axi_rid                 = m_axi.r.id,
            i_m_axi_rdata               = m_axi.r.data,
            i_m_axi_rresp               = m_axi.r.resp,
            i_m_axi_rlast               = m_axi.r.last,
            i_m_axi_rvalid              = m_axi.r.valid,
            o_m_axi_rready              = m_axi.r.ready,
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_cdma.v"))
