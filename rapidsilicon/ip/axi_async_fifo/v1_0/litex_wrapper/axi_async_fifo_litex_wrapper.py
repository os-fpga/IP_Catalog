#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXI's axi_fifo.v

import os
import datetime
import logging
import math

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')


# AXI_FIFO ---------------------------------------------------------------------------------------
class AXIASYNCFIFO(Module):
    def __init__(self, platform, s_axi, m_axi, fifo_depth):
        
        # Get Parameters.
        # --------------
        self.logger = logging.getLogger("AXI_FIFO")
        
        self.logger.propagate = True

        self.logger.info(f"=================== PARAMETERS ====================")
        
        data_width = len(s_axi.w.data)
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        
        addr_width = len(s_axi.aw.addr)
        self.logger.info(f"ADDR_WIDTH       : {addr_width}")
        
        id_width = len(s_axi.ar.id)
        self.logger.info(f"ID_WIDTH         : {id_width}")
        
        self.logger.info(f"WRITE_FIFO_DELAY : {fifo_depth}")
        
        self.logger.info(f"===================================================")

        # Clock/Reset Signals
        self.m_clk                 = Signal()
        self.m_rst                 = Signal()
        self.s_clk                 = Signal()
        self.s_rst                 = Signal()
        

        # Module instance.
        # ----------------
        self.specials += Instance("axi_async_fifo",
            # Parameters.
            # -----------
            # Global.
            p_AXI_DATA_WIDTH        = data_width,
            p_AXI_ADDR_WIDTH        = addr_width,
            p_AXI_ID_WIDTH          = id_width,
            p_FIFO_LOG          = (math.ceil(math.log2(fifo_depth))),


            # Clk / Rst.
            # ----------
            i_M_AXI_ACLK             = self.m_clk,
            i_M_AXI_ARESETN         = self.m_rst,
            i_S_AXI_ACLK             = self.s_clk,
            i_S_AXI_ARESETN         = self.s_rst,

            # AXI Input
            # --------------------
            i_S_AXI_AWID        = s_axi.aw.id,
            i_S_AXI_AWADDR      = s_axi.aw.addr,
            i_S_AXI_AWLEN       = s_axi.aw.len,
            i_S_AXI_AWSIZE      = s_axi.aw.size,
            i_S_AXI_AWBURST     = s_axi.aw.burst,
            i_S_AXI_AWLOCK      = s_axi.aw.lock,
            i_S_AXI_AWCACHE     = s_axi.aw.cache,
            i_S_AXI_AWPROT      = s_axi.aw.prot,
            i_S_AXI_AWQOS       = s_axi.aw.qos,
#            i_S_AXI_AWREGION    = s_axi.aw.region,
#            i_S_AXI_AWUSER      = s_axi.aw.user,
            i_S_AXI_AWVALID     = s_axi.aw.valid,
            o_S_AXI_AWREADY     = s_axi.aw.ready,
            
            i_S_AXI_WDATA       = s_axi.w.data,
            i_S_AXI_WSTRB       = s_axi.w.strb,
            i_S_AXI_WLAST       = s_axi.w.last,
#            i_S_AXI_WUSER       = s_axi.w.user,
            i_S_AXI_WVALID      = s_axi.w.valid,
            o_S_AXI_WREADY      = s_axi.w.ready,
            
            o_S_AXI_BID         = s_axi.b.id,
            o_S_AXI_BRESP       = s_axi.b.resp,
#            o_S_AXI_BUSER       = s_axi.b.user,
            o_S_AXI_BVALID      = s_axi.b.valid,
            i_S_AXI_BREADY      = s_axi.b.ready,
            
            i_S_AXI_ARID        = s_axi.ar.id,
            i_S_AXI_ARADDR      = s_axi.ar.addr,
            i_S_AXI_ARLEN       = s_axi.ar.len,
            i_S_AXI_ARSIZE      = s_axi.ar.size,
            i_S_AXI_ARBURST     = s_axi.ar.burst,
            i_S_AXI_ARLOCK      = s_axi.ar.lock,
            i_S_AXI_ARCACHE     = s_axi.ar.cache,
            i_S_AXI_ARPROT      = s_axi.ar.prot,
            i_S_AXI_ARQOS       = s_axi.ar.qos,
#            i_S_AXI_ARREGION    = s_axi.ar.region,
#            i_S_AXI_ARUSER      = s_axi.ar.user,
            i_S_AXI_ARVALID     = s_axi.ar.valid,
            o_S_AXI_ARREADY     = s_axi.ar.ready,
            
            o_S_AXI_RID         = s_axi.r.id,
            o_S_AXI_RDATA       = s_axi.r.data,
            o_S_AXI_RRESP       = s_axi.r.resp,
            o_S_AXI_RLAST       = s_axi.r.last,
#            o_S_AXI_RUSER       = s_axi.r.user,
            o_S_AXI_RVALID      = s_axi.r.valid,
            i_S_AXI_RREADY      = s_axi.r.ready,
            
        
            # AXI Output
            # --------------------
            o_M_AXI_AWID        = m_axi.aw.id,
            o_M_AXI_AWADDR      = m_axi.aw.addr,
            o_M_AXI_AWLEN       = m_axi.aw.len,
            o_M_AXI_AWSIZE      = m_axi.aw.size,
            o_M_AXI_AWBURST     = m_axi.aw.burst,
            o_M_AXI_AWLOCK      = m_axi.aw.lock,
            o_M_AXI_AWCACHE     = m_axi.aw.cache,
            o_M_AXI_AWPROT      = m_axi.aw.prot,
            o_M_AXI_AWQOS       = m_axi.aw.qos,
#            o_M_AXI_AWREGION    = m_axi.aw.region,
#            o_M_AXI_AWUSER      = m_axi.aw.user,
            o_M_AXI_AWVALID     = m_axi.aw.valid,
            i_M_AXI_AWREADY     = m_axi.aw.ready,
            
            o_M_AXI_WDATA       = m_axi.w.data,
            o_M_AXI_WSTRB       = m_axi.w.strb,
            o_M_AXI_WLAST       = m_axi.w.last,
#            o_M_AXI_WUSER       = m_axi.w.user,
            o_M_AXI_WVALID      = m_axi.w.valid,
            i_M_AXI_WREADY      = m_axi.w.ready,
            
            i_M_AXI_BID         = m_axi.b.id,
            i_M_AXI_BRESP       = m_axi.b.resp,
#            i_M_AXI_BUSER       = m_axi.b.user,
            i_M_AXI_BVALID      = m_axi.b.valid,
            o_M_AXI_BREADY      = m_axi.b.ready,
            
            o_M_AXI_ARID        = m_axi.ar.id,
            o_M_AXI_ARADDR      = m_axi.ar.addr,
            o_M_AXI_ARLEN       = m_axi.ar.len,
            o_M_AXI_ARSIZE      = m_axi.ar.size,
            o_M_AXI_ARBURST     = m_axi.ar.burst,
            o_M_AXI_ARLOCK      = m_axi.ar.lock,
            o_M_AXI_ARCACHE     = m_axi.ar.cache,
            o_M_AXI_ARPROT      = m_axi.ar.prot,
            o_M_AXI_ARQOS       = m_axi.ar.qos,
#            o_M_AXI_ARREGION    = m_axi.ar.region,
#            o_M_AXI_ARUSER      = m_axi.ar.user,
            o_M_AXI_ARVALID     = m_axi.ar.valid,
            i_M_AXI_ARREADY     = m_axi.ar.ready,
            
            i_M_AXI_RID         = m_axi.r.id,
            i_M_AXI_RDATA       = m_axi.r.data,
            i_M_AXI_RRESP       = m_axi.r.resp,
            i_M_AXI_RLAST       = m_axi.r.last,
#            i_M_AXI_RUSER       = m_axi.r.user,
            i_M_AXI_RVALID      = m_axi.r.valid,
            o_M_AXI_RREADY      = m_axi.r.ready            
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_async_fifo.v"))
