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

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')


# AXI_FIFO ---------------------------------------------------------------------------------------
class AXIFIFO(Module):
    def __init__(self, platform, s_axi, m_axi, 
        aw_user_en          = 0,
        w_user_en           = 0,
        b_user_en           = 0,
        ar_user_en          = 0,
        r_user_en           = 0, 
        write_fifo_depth    = 0,
        read_fifo_depth     = 0,
        write_fifo_delay    = 0,
        read_fifo_delay     = 0  
    ):
        
        # Get Parameters.
        # --------------
        self.logger = logging.getLogger("AXI_FIFO")
        
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        clock_domain = s_axi.clock_domain
        self.logger.info(f"Clock Domain     : {clock_domain}")

        data_width = len(s_axi.w.data)
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        
        addr_width = len(s_axi.aw.addr)
        self.logger.info(f"ADDR_WIDTH       : {addr_width}")
        
        id_width = len(s_axi.ar.id)
        self.logger.info(f"ID_WIDTH         : {id_width}")
        
        self.logger.info(f"AWUSER_ENABLE    : {aw_user_en}")
        aw_user_width = len(s_axi.aw.user)
        self.logger.info(f"AWUSER_WIDTH     : {aw_user_width}")
        
        self.logger.info(f"WUSER_ENABLE     : {w_user_en}")
        w_user_width = len(s_axi.w.user)
        self.logger.info(f"WUSER_WIDTH      : {w_user_width}")
        
        self.logger.info(f"BUSER_ENABLE     : {b_user_en}")
        b_user_width = len(s_axi.b.user)
        self.logger.info(f"BUSER_WIDTH      : {b_user_width}")
        
        self.logger.info(f"ARUSER_ENABLE    : {ar_user_en}")
        ar_user_width = len(s_axi.ar.user)
        self.logger.info(f"ARUSER_WIDTH     : {ar_user_width}")
        
        self.logger.info(f"RUSER_ENABLE     : {r_user_en}")
        r_user_width = len(s_axi.r.user)
        self.logger.info(f"RUSER_WIDTH      : {r_user_width}")
        
        self.logger.info(f"WRITE_FIFO_DEPTH : {write_fifo_depth}")
        self.logger.info(f"READ_FIFO_DEPTH  : {read_fifo_depth}")
        self.logger.info(f"WRITE_FIFO_DELAY : {write_fifo_delay}")
        self.logger.info(f"READ_FIFO_DELAY  : {read_fifo_delay}")
        
        self.logger.info(f"===================================================")
        
        # Module instance.
        # ----------------
        self.specials += Instance("axi_fifo",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE           = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID             = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION        = Instance.PreformattedParam("IP_VERSION"),
            # Global.
            p_DATA_WIDTH        =  Instance.PreformattedParam(data_width),
            p_ADDR_WIDTH        =  Instance.PreformattedParam(addr_width),
            p_ID_WIDTH          =  Instance.PreformattedParam(id_width),
            p_AWUSER_WIDTH      =  Instance.PreformattedParam(aw_user_width),
            p_WUSER_WIDTH       =  Instance.PreformattedParam(w_user_width),
            p_BUSER_WIDTH       =  Instance.PreformattedParam(b_user_width),
            p_ARUSER_WIDTH      =  Instance.PreformattedParam(ar_user_width),
            p_RUSER_WIDTH       =  Instance.PreformattedParam(r_user_width),
            p_WRITE_FIFO_DEPTH  =  Instance.PreformattedParam(write_fifo_depth),
            p_READ_FIFO_DEPTH   =  Instance.PreformattedParam(read_fifo_depth),
            p_AWUSER_ENABLE     =  aw_user_en,
            p_WUSER_ENABLE      =  w_user_en,
            p_BUSER_ENABLE      =  b_user_en,
            p_ARUSER_ENABLE     =  ar_user_en,
            p_RUSER_ENABLE      =  r_user_en,
            p_WRITE_FIFO_DELAY  =  write_fifo_delay,
            p_READ_FIFO_DELAY   =  read_fifo_delay,

            # Clk / Rst.
            i_clk               = ClockSignal(),
            i_rst               = ResetSignal(),

            # AXI Input
            # --------------------
            i_s_axi_awid        = s_axi.aw.id,
            i_s_axi_awaddr      = s_axi.aw.addr,
            i_s_axi_awlen       = s_axi.aw.len,
            i_s_axi_awsize      = s_axi.aw.size,
            i_s_axi_awburst     = s_axi.aw.burst,
            i_s_axi_awlock      = s_axi.aw.lock,
            i_s_axi_awcache     = s_axi.aw.cache,
            i_s_axi_awprot      = s_axi.aw.prot,
            i_s_axi_awqos       = s_axi.aw.qos,
            i_s_axi_awregion    = s_axi.aw.region,
            i_s_axi_awuser      = s_axi.aw.user,
            i_s_axi_awvalid     = s_axi.aw.valid,
            o_s_axi_awready     = s_axi.aw.ready,
            
            i_s_axi_wdata       = s_axi.w.data,
            i_s_axi_wstrb       = s_axi.w.strb,
            i_s_axi_wlast       = s_axi.w.last,
            i_s_axi_wuser       = s_axi.w.user,
            i_s_axi_wvalid      = s_axi.w.valid,
            o_s_axi_wready      = s_axi.w.ready,
            
            o_s_axi_bid         = s_axi.b.id,
            o_s_axi_bresp       = s_axi.b.resp,
            o_s_axi_buser       = s_axi.b.user,
            o_s_axi_bvalid      = s_axi.b.valid,
            i_s_axi_bready      = s_axi.b.ready,
            
            i_s_axi_arid        = s_axi.ar.id,
            i_s_axi_araddr      = s_axi.ar.addr,
            i_s_axi_arlen       = s_axi.ar.len,
            i_s_axi_arsize      = s_axi.ar.size,
            i_s_axi_arburst     = s_axi.ar.burst,
            i_s_axi_arlock      = s_axi.ar.lock,
            i_s_axi_arcache     = s_axi.ar.cache,
            i_s_axi_arprot      = s_axi.ar.prot,
            i_s_axi_arqos       = s_axi.ar.qos,
            i_s_axi_arregion    = s_axi.ar.region,
            i_s_axi_aruser      = s_axi.ar.user,
            i_s_axi_arvalid     = s_axi.ar.valid,
            o_s_axi_arready     = s_axi.ar.ready,
            
            o_s_axi_rid         = s_axi.r.id,
            o_s_axi_rdata       = s_axi.r.data,
            o_s_axi_rresp       = s_axi.r.resp,
            o_s_axi_rlast       = s_axi.r.last,
            o_s_axi_ruser       = s_axi.r.user,
            o_s_axi_rvalid      = s_axi.r.valid,
            i_s_axi_rready      = s_axi.r.ready,
            
        
            # AXI Output
            # --------------------
            o_m_axi_awid        = m_axi.aw.id,
            o_m_axi_awaddr      = m_axi.aw.addr,
            o_m_axi_awlen       = m_axi.aw.len,
            o_m_axi_awsize      = m_axi.aw.size,
            o_m_axi_awburst     = m_axi.aw.burst,
            o_m_axi_awlock      = m_axi.aw.lock,
            o_m_axi_awcache     = m_axi.aw.cache,
            o_m_axi_awprot      = m_axi.aw.prot,
            o_m_axi_awqos       = m_axi.aw.qos,
            o_m_axi_awregion    = m_axi.aw.region,
            o_m_axi_awuser      = m_axi.aw.user,
            o_m_axi_awvalid     = m_axi.aw.valid,
            i_m_axi_awready     = m_axi.aw.ready,
            
            o_m_axi_wdata       = m_axi.w.data,
            o_m_axi_wstrb       = m_axi.w.strb,
            o_m_axi_wlast       = m_axi.w.last,
            o_m_axi_wuser       = m_axi.w.user,
            o_m_axi_wvalid      = m_axi.w.valid,
            i_m_axi_wready      = m_axi.w.ready,
            
            i_m_axi_bid         = m_axi.b.id,
            i_m_axi_bresp       = m_axi.b.resp,
            i_m_axi_buser       = m_axi.b.user,
            i_m_axi_bvalid      = m_axi.b.valid,
            o_m_axi_bready      = m_axi.b.ready,
            
            o_m_axi_arid        = m_axi.ar.id,
            o_m_axi_araddr      = m_axi.ar.addr,
            o_m_axi_arlen       = m_axi.ar.len,
            o_m_axi_arsize      = m_axi.ar.size,
            o_m_axi_arburst     = m_axi.ar.burst,
            o_m_axi_arlock      = m_axi.ar.lock,
            o_m_axi_arcache     = m_axi.ar.cache,
            o_m_axi_arprot      = m_axi.ar.prot,
            o_m_axi_arqos       = m_axi.ar.qos,
            o_m_axi_arregion    = m_axi.ar.region,
            o_m_axi_aruser      = m_axi.ar.user,
            o_m_axi_arvalid     = m_axi.ar.valid,
            i_m_axi_arready     = m_axi.ar.ready,
            
            i_m_axi_rid         = m_axi.r.id,
            i_m_axi_rdata       = m_axi.r.data,
            i_m_axi_rresp       = m_axi.r.resp,
            i_m_axi_rlast       = m_axi.r.last,
            i_m_axi_ruser       = m_axi.r.user,
            i_m_axi_rvalid      = m_axi.r.valid,
            o_m_axi_rready      = m_axi.r.ready            
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_fifo.v"))
