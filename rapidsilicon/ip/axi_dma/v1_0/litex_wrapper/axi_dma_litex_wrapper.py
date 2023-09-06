#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXI's axi_dma.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')


# AXI DMA ---------------------------------------------------------------------------------------
class AXIDMA(Module):
    def __init__(self, platform, m_axi, m_axis, s_axis,
        axi_max_burst_len   = 16,
        axis_last_enable    = 1,
        axis_id_enable      = 0,
        axis_dest_enable    = 0,
        axis_user_enable    = 1,
        len_width           = 20,
        tag_width           = 8,
        enable_sg           = 0,
        enable_unaligned    = 0,
    ):

        # Get Parameters.
        # ---------------------
        self.logger = logging.getLogger("AXI_DMA")
        
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        self.logger.info(f"Clock Domain         : {m_axi.clock_domain}")

        address_width = len(m_axi.aw.addr)
        self.logger.info(f"AXI_ADDR_WIDTH       : {address_width}")

        axi_data_width = len(m_axi.w.data)
        self.logger.info(f"AXI_DATA_WIDTH       : {axi_data_width}")
        
        axi_id_width = len(m_axi.ar.id)
        self.logger.info(f"AXI_ID_WIDTH         : {axi_id_width}")
        
        self.logger.info(f"AXIS_DATA_WIDTH      : {axi_data_width}")
        
        self.logger.info(f"AXI_MAX_BURST_LEN    : {axi_max_burst_len}")
        self.logger.info(f"AXIS_LAST_ENABLE     : {axis_last_enable}")
        
        self.logger.info(f"AXIS_ID_ENABLE       : {axis_id_enable}")
        axis_id_width = len(m_axis.id)
        self.logger.info(f"AXIS_ID_WIDTH        : {axis_id_width}")
        
        self.logger.info(f"AXIS_DEST_ENABLE     : {axis_dest_enable}")        
        axis_dest_width = len(m_axis.dest)
        self.logger.info(f"AXIS_DEST_WIDTH      : {axis_dest_width}")
        
        self.logger.info(f"AXIS_USER_ENABLE     : {axis_user_enable}")        
        axis_user_width = len(m_axis.user)
        self.logger.info(f"AXIS_USER_WIDTH      : {axis_user_width}")
        
        self.logger.info(f"LEN_WIDTH            : {len_width}")
        self.logger.info(f"TAG_WIDTH            : {tag_width}")
        self.logger.info(f"ENABLE_SG            : {enable_sg}")
        self.logger.info(f"ENABLE_UNALIGNED     : {enable_unaligned}")
        self.logger.info(f"===================================================")
        # Non-Stnadard IOs
        self.s_axis_read_desc_addr          = Signal(address_width)
        self.s_axis_read_desc_len           = Signal(len_width)
        self.s_axis_read_desc_tag           = Signal(tag_width)
        self.s_axis_read_desc_id            = Signal(axis_id_width)
        self.s_axis_read_desc_dest          = Signal(axis_dest_width)
        self.s_axis_read_desc_user          = Signal(axis_user_width)
        self.s_axis_read_desc_valid         = Signal()
        self.s_axis_read_desc_ready         = Signal()

        self.m_axis_read_desc_status_tag    = Signal(tag_width)
        self.m_axis_read_desc_status_error  = Signal(4)
        self.m_axis_read_desc_status_valid  = Signal()

        self.s_axis_write_desc_addr         = Signal(address_width)
        self.s_axis_write_desc_len          = Signal(len_width)
        self.s_axis_write_desc_tag          = Signal(tag_width)
        self.s_axis_write_desc_valid        = Signal()
        self.s_axis_write_desc_ready        = Signal()

        self.read_enable                    = Signal()
        self.write_enable                   = Signal()
        self.write_abort                    = Signal()

        self.m_axis_write_desc_status_len   = Signal(len_width)
        self.m_axis_write_desc_status_tag   = Signal(tag_width)
        self.m_axis_write_desc_status_id    = Signal(axis_id_width)
        self.m_axis_write_desc_status_dest  = Signal(axis_dest_width)
        self.m_axis_write_desc_status_user  = Signal(axis_user_width)
        self.m_axis_write_desc_status_error = Signal(4)
        self.m_axis_write_desc_status_valid = Signal()

        # Module instance.
        # ----------------
        self.specials += Instance("axi_dma",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE                           = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID                             = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION                        = Instance.PreformattedParam("IP_VERSION"),
            
            # Global AXI
            p_AXI_DATA_WIDTH                    = Instance.PreformattedParam(axi_data_width),
            p_AXI_ADDR_WIDTH                    = Instance.PreformattedParam(address_width),
            p_AXI_ID_WIDTH                      = Instance.PreformattedParam(axi_id_width),
            p_AXIS_DATA_WIDTH                   = Instance.PreformattedParam(axi_data_width),    
            
            # IP Params.
            p_AXI_MAX_BURST_LEN                 = Instance.PreformattedParam(axi_max_burst_len),    
            p_AXIS_ID_WIDTH                     = Instance.PreformattedParam(axis_id_width),
            p_AXIS_DEST_WIDTH                   = Instance.PreformattedParam(axis_dest_width),    
            p_AXIS_USER_WIDTH                   = Instance.PreformattedParam(axis_user_width),       
            p_LEN_WIDTH                         = Instance.PreformattedParam(len_width),
            p_TAG_WIDTH                         = Instance.PreformattedParam(tag_width),
            p_AXIS_LAST_ENABLE                  = axis_last_enable,
            p_AXIS_ID_ENABLE                    = axis_id_enable,
            p_AXIS_DEST_ENABLE                  = axis_dest_enable,
            p_AXIS_USER_ENABLE                  = axis_user_enable, 
            p_ENABLE_SG                         = enable_sg,
            p_ENABLE_UNALIGNED                  = enable_unaligned,    

            # Clk / Rst.
            i_clk                               = ClockSignal(m_axi.clock_domain),
            i_rst                               = ResetSignal(m_axi.clock_domain),

            # AXI read descriptor input
            i_s_axis_read_desc_addr             = self.s_axis_read_desc_addr, 
            i_s_axis_read_desc_len              = self.s_axis_read_desc_len, 
            i_s_axis_read_desc_tag              = self.s_axis_read_desc_tag, 
            i_s_axis_read_desc_id               = self.s_axis_read_desc_id, 
            i_s_axis_read_desc_dest             = self.s_axis_read_desc_dest, 
            i_s_axis_read_desc_user             = self.s_axis_read_desc_user, 
            i_s_axis_read_desc_valid            = self.s_axis_read_desc_valid,     
            o_s_axis_read_desc_ready            = self.s_axis_read_desc_ready,     

            # AXI read descriptor status output
            o_m_axis_read_desc_status_tag       = self.m_axis_read_desc_status_tag,
            o_m_axis_read_desc_status_error     = self.m_axis_read_desc_status_error,
            o_m_axis_read_desc_status_valid     = self.m_axis_read_desc_status_valid,

            # AXI write descriptor status input
            i_s_axis_write_desc_addr            = self.s_axis_write_desc_addr,   
            i_s_axis_write_desc_len             = self.s_axis_write_desc_len,
            i_s_axis_write_desc_tag             = self.s_axis_write_desc_tag,   
            i_s_axis_write_desc_valid           = self.s_axis_write_desc_valid,   
            o_s_axis_write_desc_ready           = self.s_axis_write_desc_ready,   

            # AXI write descriptor status output
            o_m_axis_write_desc_status_len      = self.m_axis_write_desc_status_len,
            o_m_axis_write_desc_status_tag      = self.m_axis_write_desc_status_tag,
            o_m_axis_write_desc_status_id       = self.m_axis_write_desc_status_id,
            o_m_axis_write_desc_status_dest     = self.m_axis_write_desc_status_dest,
            o_m_axis_write_desc_status_user     = self.m_axis_write_desc_status_user,
            o_m_axis_write_desc_status_error    = self.m_axis_write_desc_status_error,
            o_m_axis_write_desc_status_valid    = self.m_axis_write_desc_status_valid,

            # AXI stream read data output
            o_m_axis_read_data_tdata            = m_axis.data,
            o_m_axis_read_data_tkeep            = m_axis.keep,
            o_m_axis_read_data_tvalid           = m_axis.valid,
            i_m_axis_read_data_tready           = m_axis.ready,
            o_m_axis_read_data_tlast            = m_axis.last,
            o_m_axis_read_data_tid              = m_axis.id,
            o_m_axis_read_data_tdest            = m_axis.dest,
            o_m_axis_read_data_tuser            = m_axis.user,

            # AXI stream write data input
            i_s_axis_write_data_tdata            = s_axis.data,
            i_s_axis_write_data_tkeep            = s_axis.keep,
            i_s_axis_write_data_tvalid           = s_axis.valid,
            o_s_axis_write_data_tready           = s_axis.ready,
            i_s_axis_write_data_tlast            = s_axis.last,
            i_s_axis_write_data_tid              = s_axis.id,
            i_s_axis_write_data_tdest            = s_axis.dest,
            i_s_axis_write_data_tuser            = s_axis.user,

            # AXI Master Interface.
            # --------------------
            # AW.
            o_m_axi_awid                        = m_axi.aw.id,
            o_m_axi_awaddr                      = m_axi.aw.addr,
            o_m_axi_awlen                       = m_axi.aw.len,
            o_m_axi_awsize                      = m_axi.aw.size,
            o_m_axi_awburst                     = m_axi.aw.burst,
            o_m_axi_awlock                      = m_axi.aw.lock,
            o_m_axi_awcache                     = m_axi.aw.cache,
            o_m_axi_awprot                      = m_axi.aw.prot,
            o_m_axi_awvalid                     = m_axi.aw.valid,
            i_m_axi_awready                     = m_axi.aw.ready,

            # W.
            o_m_axi_wdata                       = m_axi.w.data,
            o_m_axi_wstrb                       = m_axi.w.strb,
            o_m_axi_wlast                       = m_axi.w.last,
            o_m_axi_wvalid                      = m_axi.w.valid,
            i_m_axi_wready                      = m_axi.w.ready,

            # B.
            i_m_axi_bid                         = m_axi.b.id,
            i_m_axi_bresp                       = m_axi.b.resp,
            i_m_axi_bvalid                      = m_axi.b.valid,
            o_m_axi_bready                      = m_axi.b.ready,

            # AR.
            o_m_axi_arid                        = m_axi.ar.id,
            o_m_axi_araddr                      = m_axi.ar.addr,
            o_m_axi_arlen                       = m_axi.ar.len,
            o_m_axi_arsize                      = m_axi.ar.size,
            o_m_axi_arburst                     = m_axi.ar.burst,
            o_m_axi_arlock                      = m_axi.ar.lock,
            o_m_axi_arcache                     = m_axi.ar.cache,
            o_m_axi_arprot                      = m_axi.ar.prot,
            o_m_axi_arvalid                     = m_axi.ar.valid,
            i_m_axi_arready                     = m_axi.ar.ready,

            # R.
            i_m_axi_rid                         = m_axi.r.id,
            i_m_axi_rdata                       = m_axi.r.data,
            i_m_axi_rresp                       = m_axi.r.resp,
            i_m_axi_rlast                       = m_axi.r.last,
            i_m_axi_rvalid                      = m_axi.r.valid,
            o_m_axi_rready                      = m_axi.r.ready,

            # Configuration
            i_read_enable                       = self.read_enable,
            i_write_enable                      = self.write_enable,
            i_write_abort                       = self.write_abort,
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_dma_wr.v"))
        platform.add_source(os.path.join(rtl_dir, "axi_dma_rd.v"))
        platform.add_source(os.path.join(rtl_dir, "axi_dma_desc_mux.v"))
        platform.add_source(os.path.join(rtl_dir, "axi_dma.v"))
