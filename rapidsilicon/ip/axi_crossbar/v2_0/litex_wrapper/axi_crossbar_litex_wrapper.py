#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXI's axi_crossbar.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')


# AXI CROSSBAR ---------------------------------------------------------------------------------
class AXICROSSBAR(Module):
    def __init__(self, platform, s_axi, m_axi, s_count, m_count, aw_user_en, w_user_en,
        b_user_en, ar_user_en, r_user_en,bram):

        self.s_awid_internal 	  = [Signal(len(s_axi[0].aw.id)) for s_count in range(s_count+1)]
        self.s_awaddr_internal   = [Signal(len(s_axi[0].aw.addr)) for s_count in range(s_count+1)]
        self.s_awlen_internal	  = [Signal(8) for s_count in range(s_count+1)]
        self.s_awsize_internal   = [Signal(3) for s_count in range(s_count+1)]
        self.s_awburst_internal  = [Signal(2) for s_count in range(s_count+1)]
        self.s_awlock_internal   = [Signal(2) for s_count in range(s_count+1)]
        self.s_awcache_internal  = [Signal(4) for s_count in range(s_count+1)]
        self.s_awprot_internal   = [Signal(3) for s_count in range(s_count+1)]
        self.s_awqos_internal    = [Signal(4) for s_count in range(s_count+1)]
        self.s_awuser_internal   = [Signal(1) for s_count in range(s_count+1)]
        self.s_awvalid_internal  = [Signal(1) for s_count in range(s_count+1)]
        self.s_awready_internal  = [Signal(1) for s_count in range(s_count+1)]
        
        self.s_wdata_internal    = [Signal(len(s_axi[0].w.data)) for s_count in range(s_count+1)]
        self.s_wstrb_internal    = [Signal(len(s_axi[0].w.strb)) for s_count in range(s_count+1)]
        self.s_wlast_internal    = [Signal(1) for s_count in range(s_count+1)]
        self.s_wuser_internal    = [Signal(1) for s_count in range(s_count+1)]
        self.s_wvalid_internal   = [Signal(1) for s_count in range(s_count+1)]
        self.s_wready_internal   = [Signal(1) for s_count in range(s_count+1)]
        
        self.s_bid_internal 	  = [Signal(len(s_axi[0].b.id)) for s_count in range(s_count+1)]
        self.s_bresp_internal    = [Signal(2) for s_count in range(s_count+1)]
        self.s_buser_internal    = [Signal(1) for s_count in range(s_count+1)]
        self.s_bvalid_internal   = [Signal(1) for s_count in range(s_count+1)]
        self.s_bready_internal   = [Signal(1) for s_count in range(s_count+1)]
        
        self.s_arid_internal 	  = [Signal(len(s_axi[0].ar.id)) for s_count in range(s_count+1)]
        self.s_araddr_internal   = [Signal(len(s_axi[0].ar.addr)) for s_count in range(s_count+1)]
        self.s_arlen_internal    = [Signal(8) for s_count in range(s_count+1)]
        self.s_arsize_internal   = [Signal(3) for s_count in range(s_count+1)]
        self.s_arburst_internal  = [Signal(2) for s_count in range(s_count+1)]
        self.s_arlock_internal   = [Signal(2) for s_count in range(s_count+1)]
        self.s_arcache_internal  = [Signal(4) for s_count in range(s_count+1)]
        self.s_arprot_internal   = [Signal(3) for s_count in range(s_count+1)]
        self.s_arqos_internal    = [Signal(4) for s_count in range(s_count+1)]
        self.s_aruser_internal   = [Signal(1) for s_count in range(s_count+1)]
        self.s_arvalid_internal  = [Signal(1) for s_count in range(s_count+1)]
        self.s_arready_internal  = [Signal(1) for s_count in range(s_count+1)]
        
        self.s_rid_internal 	  = [Signal(len(s_axi[0].r.id)) for s_count in range(s_count+1)]
        self.s_rdata_internal    = [Signal(len(s_axi[0].r.data)) for s_count in range(s_count+1)]
        self.s_rresp_internal    = [Signal(2) for s_count in range(s_count+1)]
        self.s_rlast_internal    = [Signal(1) for s_count in range(s_count+1)]
        self.s_ruser_internal    = [Signal(1) for s_count in range(s_count+1)]
        self.s_rvalid_internal   = [Signal(1) for s_count in range(s_count+1)]
        self.s_rready_internal   = [Signal(1) for s_count in range(s_count+1)]
        
        self.m_awid_internal 	  = [Signal(len(m_axi[0].aw.id)) for m_count in range(m_count+1)]
        self.m_awaddr_internal   = [Signal(len(m_axi[0].aw.addr)) for m_count in range(m_count+1)]
        self.m_awlen_internal    = [Signal(8) for m_count in range(m_count+1)]
        self.m_awsize_internal   = [Signal(3) for m_count in range(m_count+1)]
        self.m_awburst_internal  = [Signal(2) for m_count in range(m_count+1)]
        self.m_awlock_internal   = [Signal(2) for m_count in range(m_count+1)]
        self.m_awcache_internal  = [Signal(4) for m_count in range(m_count+1)]
        self.m_awprot_internal   = [Signal(3) for m_count in range(m_count+1)]
        self.m_awqos_internal    = [Signal(4) for m_count in range(m_count+1)]
        self.m_awregion_internal = [Signal(4) for m_count in range(m_count+1)]
        self.m_awuser_internal   = [Signal(1) for m_count in range(m_count+1)]
        self.m_awvalid_internal  = [Signal(1) for m_count in range(m_count+1)]
        self.m_awready_internal  = [Signal(1) for m_count in range(m_count+1)]
        
        self.m_wdata_internal    = [Signal(len(m_axi[0].w.data)) for m_count in range(m_count+1)]
        self.m_wstrb_internal    = [Signal(len(m_axi[0].w.strb)) for m_count in range(m_count+1)]
        self.m_wlast_internal    = [Signal(1) for m_count in range(m_count+1)]
        self.m_wuser_internal    = [Signal(1) for m_count in range(m_count+1)]
        self.m_wvalid_internal   = [Signal(1) for m_count in range(m_count+1)]
        self.m_wready_internal   = [Signal(1) for m_count in range(m_count+1)]
        
        self.m_bid_internal      = [Signal(len(m_axi[0].b.id)) for m_count in range(m_count+1)]
        self.m_bresp_internal    = [Signal(2) for m_count in range(m_count+1)]
        self.m_buser_internal    = [Signal(1) for m_count in range(m_count+1)]
        self.m_bvalid_internal   = [Signal(1) for m_count in range(m_count+1)]
        self.m_bready_internal   = [Signal(1) for m_count in range(m_count+1)]
        
        self.m_arid_internal     = [Signal(len(m_axi[0].ar.id)) for m_count in range(m_count+1)]
        self.m_araddr_internal   = [Signal(len(m_axi[0].ar.addr)) for m_count in range(m_count+1)]
        self.m_arlen_internal    = [Signal(8) for m_count in range(m_count+1)]
        self.m_arsize_internal   = [Signal(3) for m_count in range(m_count+1)]
        self.m_arburst_internal  = [Signal(2) for m_count in range(m_count+1)]
        self.m_arlock_internal   = [Signal(2) for m_count in range(m_count+1)]
        self.m_arcache_internal  = [Signal(4) for m_count in range(m_count+1)]
        self.m_arprot_internal   = [Signal(3) for m_count in range(m_count+1)]
        self.m_arqos_internal    = [Signal(4) for m_count in range(m_count+1)]
        self.m_arregion_internal = [Signal(4) for m_count in range(m_count+1)]
        self.m_aruser_internal   = [Signal(1) for m_count in range(m_count+1)]
        self.m_arvalid_internal  = [Signal(1) for m_count in range(m_count+1)]
        self.m_arready_internal  = [Signal(1) for m_count in range(m_count+1)]
        
        self.m_rid_internal      = [Signal(len(m_axi[0].r.id)) for m_count in range(m_count+1)]
        self.m_rdata_internal    = [Signal(len(m_axi[0].r.data)) for m_count in range(m_count+1)]
        self.m_rresp_internal    = [Signal(2) for m_count in range(m_count+1)]
        self.m_rlast_internal    = [Signal(1) for m_count in range(m_count+1)]
        self.m_ruser_internal    = [Signal(1) for m_count in range(m_count+1)]
        self.m_rvalid_internal   = [Signal(1) for m_count in range(m_count+1)]
        self.m_rready_internal   = [Signal(1) for m_count in range(m_count+1)]
        
        self.master_clk          = [Signal(1) for s_count in range(s_count+1)]
        
        self.logger = logging.getLogger("AXI_CROSSBAR")
        
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
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

        # Master ID width.
        m_id_width = len(m_axi[0].aw.id)
        self.logger.info(f"M_ID_WIDTH   : {m_id_width}")
        
        # Slave ID width.
        s_id_width = len(s_axi[0].aw.id)
        self.logger.info(f"S_ID_WIDTH   : {s_id_width}")

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
        self.logger.info(f"===================================================")
        # Module instance.
        # ----------------
        self.specials += Instance("axi_crossbar",
            # Parameters.
            # -----------
            p_S_COUNT       = Instance.PreformattedParam(len(s_axi)),
            p_M_COUNT       = Instance.PreformattedParam(len(m_axi)),
            p_DATA_WIDTH    = Instance.PreformattedParam(data_width),
            p_ADDR_WIDTH    = Instance.PreformattedParam(address_width),
            p_S_ID_WIDTH    = Instance.PreformattedParam(s_id_width),
            p_AWUSER_WIDTH  = Instance.PreformattedParam(aw_user_width),
            p_WUSER_WIDTH   = Instance.PreformattedParam(w_user_width),
            p_BUSER_WIDTH   = Instance.PreformattedParam(b_user_width),
            p_ARUSER_WIDTH  = Instance.PreformattedParam(ar_user_width),
            p_RUSER_WIDTH   = Instance.PreformattedParam(r_user_width),
            p_AWUSER_ENABLE = aw_user_en,
            p_WUSER_ENABLE  = w_user_en,
            p_BUSER_ENABLE  = b_user_en,
            p_ARUSER_ENABLE = ar_user_en,
            p_RUSER_ENABLE  = r_user_en,

            # Clk / Rst.
            # ----------
            i_clk           = ClockSignal(),
            i_rst           = ResetSignal(),

            # AXI Slave Interfaces.
            # --------------------
            # AW.
            i_s_axi_awid     = Cat(self.s_awid_internal),
            i_s_axi_awaddr   = Cat(self.s_awaddr_internal),
            i_s_axi_awlen    = Cat(self.s_awlen_internal),
            i_s_axi_awsize   = Cat(self.s_awsize_internal),
            i_s_axi_awburst  = Cat(self.s_awburst_internal),
            i_s_axi_awlock   = Cat(self.s_awlock_internal),
            i_s_axi_awcache  = Cat(self.s_awcache_internal),
            i_s_axi_awprot   = Cat(self.s_awprot_internal),
            i_s_axi_awqos    = Cat(self.s_awqos_internal),
            i_s_axi_awuser   = Cat(self.s_awuser_internal),
            i_s_axi_awvalid  = Cat(self.s_awvalid_internal),
            o_s_axi_awready  = Cat(self.s_awready_internal),

            # W.
            i_s_axi_wdata    = Cat(self.s_wdata_internal),
            i_s_axi_wstrb    = Cat(self.s_wstrb_internal),
            i_s_axi_wlast    = Cat(self.s_wlast_internal),
            i_s_axi_wuser    = Cat(self.s_wuser_internal),
            i_s_axi_wvalid   = Cat(self.s_wvalid_internal),
            o_s_axi_wready   = Cat(self.s_wready_internal),

            # B.
            o_s_axi_bid      = Cat(self.s_bid_internal),
            o_s_axi_bresp    = Cat(self.s_bresp_internal),
            o_s_axi_buser    = Cat(self.s_buser_internal),
            o_s_axi_bvalid   = Cat(self.s_bvalid_internal),
            i_s_axi_bready   = Cat(self.s_bready_internal),

            # AR.
            i_s_axi_arid     = Cat(self.s_arid_internal),
            i_s_axi_araddr   = Cat(self.s_araddr_internal),
            i_s_axi_arlen    = Cat(self.s_arlen_internal),
            i_s_axi_arsize   = Cat(self.s_arsize_internal),
            i_s_axi_arburst  = Cat(self.s_arburst_internal),
            i_s_axi_arlock   = Cat(self.s_arlock_internal),
            i_s_axi_arcache  = Cat(self.s_arcache_internal),
            i_s_axi_arprot   = Cat(self.s_arprot_internal),
            i_s_axi_arqos    = Cat(self.s_arqos_internal),
            i_s_axi_aruser   = Cat(self.s_aruser_internal),
            i_s_axi_arvalid  = Cat(self.s_arvalid_internal),
            o_s_axi_arready  = Cat(self.s_arready_internal),

            # R.
            o_s_axi_rid      = Cat(self.s_rid_internal),
            o_s_axi_rdata    = Cat(self.s_rdata_internal),
            o_s_axi_rresp    = Cat(self.s_rresp_internal),
            o_s_axi_rlast    = Cat(self.s_rlast_internal),
            o_s_axi_ruser    = Cat(self.s_ruser_internal),
            o_s_axi_rvalid   = Cat(self.s_rvalid_internal),
            i_s_axi_rready   = Cat(self.s_rready_internal),

            # AXI Master Interfaces.
            # ----------------------
            # AW.
            o_m_axi_awid     = Cat(self.m_awid_internal),
            o_m_axi_awaddr   = Cat(self.m_awaddr_internal),
            o_m_axi_awlen    = Cat(self.m_awlen_internal),
            o_m_axi_awsize   = Cat(self.m_awsize_internal),
            o_m_axi_awburst  = Cat(self.m_awburst_internal),
            o_m_axi_awlock   = Cat(self.m_awlock_internal),
            o_m_axi_awcache  = Cat(self.m_awcache_internal),
            o_m_axi_awprot   = Cat(self.m_awprot_internal),
            o_m_axi_awqos    = Cat(self.m_awqos_internal),
            o_m_axi_awregion = Cat(self.m_awregion_internal),
            o_m_axi_awuser   = Cat(self.m_awuser_internal),
            o_m_axi_awvalid  = Cat(self.m_awvalid_internal),
            i_m_axi_awready  = Cat(self.m_awready_internal),

            # W.
            o_m_axi_wdata    = Cat(self.m_wdata_internal),
            o_m_axi_wstrb    = Cat(self.m_wstrb_internal),
            o_m_axi_wlast    = Cat(self.m_wlast_internal),
            o_m_axi_wuser    = Cat(self.m_wuser_internal),
            o_m_axi_wvalid   = Cat(self.m_wvalid_internal),
            i_m_axi_wready   = Cat(self.m_wready_internal),

            # B.
            i_m_axi_bid      = Cat(self.m_bid_internal),
            i_m_axi_bresp    = Cat(self.m_bresp_internal),
            i_m_axi_buser    = Cat(self.m_buser_internal),
            i_m_axi_bvalid   = Cat(self.m_bvalid_internal),
            o_m_axi_bready   = Cat(self.m_bready_internal),

            # AR.
            o_m_axi_arid     = Cat(self.m_arid_internal),
            o_m_axi_araddr   = Cat(self.m_araddr_internal),
            o_m_axi_arlen    = Cat(self.m_arlen_internal),
            o_m_axi_arsize   = Cat(self.m_arsize_internal),
            o_m_axi_arburst  = Cat(self.m_arburst_internal),
            o_m_axi_arlock   = Cat(self.m_arlock_internal),
            o_m_axi_arcache  = Cat(self.m_arcache_internal),
            o_m_axi_arprot   = Cat(self.m_arprot_internal),
            o_m_axi_arqos    = Cat(self.m_arqos_internal),
            o_m_axi_arregion = Cat(self.m_arregion_internal),
            o_m_axi_aruser   = Cat(self.m_aruser_internal),
            o_m_axi_arvalid  = Cat(self.m_arvalid_internal),
            i_m_axi_arready  = Cat(self.m_arready_internal),

            # R.
            i_m_axi_rid      = Cat(self.m_rid_internal),
            i_m_axi_rdata    = Cat(self.m_rdata_internal),
            i_m_axi_rresp    = Cat(self.m_rresp_internal),
            i_m_axi_rlast    = Cat(self.m_rlast_internal),
            i_m_axi_ruser    = Cat(self.m_ruser_internal),
            i_m_axi_rvalid   = Cat(self.m_rvalid_internal),
            o_m_axi_rready   = Cat(self.m_rready_internal),
        )
        
        # Slave interface CDC blocks
        
        for s_count in range (s_count):
            self.specials += 	Instance("axi_cdc",
            p_AXI_ID_WIDTH     = 	Instance.PreformattedParam(s_id_width),
            p_AXI_DATA_WIDTH   = 	Instance.PreformattedParam(data_width),
            p_AXI_ADDR_WIDTH   = 	Instance.PreformattedParam(address_width),
            p_SYNC_STAGES      = 	2,
            p_FIFO_LOG         = 	3,
            p_MEM_TYPE		=       bram,
          
            i_S_AXI_ACLK 	= 	ClockSignal("s{}_axi_aclk".format(s_count)),
            i_S_AXI_ARESET	=	ResetSignal("s{}_axi_areset".format(s_count)),
            i_M_AXI_ACLK	= 	ClockSignal(),
            i_M_AXI_ARESET	=	ResetSignal(),
            
            i_S_AXI_AWID 	= 	s_axi[s_count].aw.id,
            i_S_AXI_AWADDR 	= 	s_axi[s_count].aw.addr,
            i_S_AXI_AWLEN 	= 	s_axi[s_count].aw.len,
            i_S_AXI_AWSIZE 	= 	s_axi[s_count].aw.size,
            i_S_AXI_AWBURST    = 	s_axi[s_count].aw.burst,
            i_S_AXI_AWLOCK 	= 	s_axi[s_count].aw.lock,
            i_S_AXI_AWCACHE    = 	s_axi[s_count].aw.cache,
            i_S_AXI_AWPROT 	= 	s_axi[s_count].aw.prot,
            i_S_AXI_AWQOS 	= 	s_axi[s_count].aw.qos,
            i_S_AXI_AWVALID    = 	s_axi[s_count].aw.valid,
            o_S_AXI_AWREADY    = 	s_axi[s_count].aw.ready,
            
            i_S_AXI_WDATA 	= 	s_axi[s_count].w.data,
            i_S_AXI_WSTRB 	= 	s_axi[s_count].w.strb,
            i_S_AXI_WLAST 	= 	s_axi[s_count].w.last,
            i_S_AXI_WVALID 	= 	s_axi[s_count].w.valid,
            o_S_AXI_WREADY 	= 	s_axi[s_count].w.ready,
            
            o_S_AXI_BID 	= 	s_axi[s_count].b.id,
            o_S_AXI_BRESP 	= 	s_axi[s_count].b.resp,
            o_S_AXI_BVALID 	= 	s_axi[s_count].b.valid,
            i_S_AXI_BREADY 	= 	s_axi[s_count].b.ready,

            i_S_AXI_ARID 	= 	s_axi[s_count].ar.id,
            i_S_AXI_ARADDR 	= 	s_axi[s_count].ar.addr,
            i_S_AXI_ARLEN 	= 	s_axi[s_count].ar.len,
            i_S_AXI_ARSIZE 	= 	s_axi[s_count].ar.size,
            i_S_AXI_ARBURST 	= 	s_axi[s_count].ar.burst,
            i_S_AXI_ARLOCK 	= 	s_axi[s_count].ar.lock,
            i_S_AXI_ARCACHE    = 	s_axi[s_count].ar.cache,   
            i_S_AXI_ARPROT 	= 	s_axi[s_count].ar.prot,
            i_S_AXI_ARQOS 	= 	s_axi[s_count].ar.qos,
            i_S_AXI_ARVALID	= 	s_axi[s_count].ar.valid, 
            o_S_AXI_ARREADY	= 	s_axi[s_count].ar.ready,
            
            o_S_AXI_RID 	= 	s_axi[s_count].r.id,
            o_S_AXI_RDATA 	= 	s_axi[s_count].r.data,
            o_S_AXI_RRESP 	= 	s_axi[s_count].r.resp,
            o_S_AXI_RLAST 	= 	s_axi[s_count].r.last,
            o_S_AXI_RVALID 	= 	s_axi[s_count].r.valid,
            i_S_AXI_RREADY 	= 	s_axi[s_count].r.ready,

            o_M_AXI_AWID 	= 	self.s_awid_internal[s_count],
            o_M_AXI_AWADDR 	= 	self.s_awaddr_internal[s_count],
            o_M_AXI_AWLEN 	= 	self.s_awlen_internal[s_count],
            o_M_AXI_AWSIZE 	= 	self.s_awsize_internal[s_count],
            o_M_AXI_AWBURST    = 	self.s_awburst_internal[s_count],
            o_M_AXI_AWLOCK 	= 	self.s_awlock_internal[s_count],
            o_M_AXI_AWCACHE    = 	self.s_awcache_internal[s_count],
            o_M_AXI_AWPROT 	= 	self.s_awprot_internal[s_count],
            o_M_AXI_AWQOS 	= 	self.s_awqos_internal[s_count],
            o_M_AXI_AWVALID    = 	self.s_awvalid_internal[s_count],
            i_M_AXI_AWREADY    = 	self.s_awready_internal[s_count],

            o_M_AXI_WDATA 	= 	self.s_wdata_internal[s_count],
            o_M_AXI_WSTRB 	= 	self.s_wstrb_internal[s_count],
            o_M_AXI_WLAST 	= 	self.s_wlast_internal[s_count],
            o_M_AXI_WVALID 	= 	self.s_wvalid_internal[s_count],
            i_M_AXI_WREADY 	= 	self.s_wready_internal[s_count],


            i_M_AXI_BID 	= 	self.s_bid_internal[s_count],
            i_M_AXI_BRESP 	= 	self.s_bresp_internal[s_count],
            i_M_AXI_BVALID 	= 	self.s_bvalid_internal[s_count],
            o_M_AXI_BREADY 	= 	self.s_bready_internal[s_count],


            o_M_AXI_ARID 	= 	self.s_arid_internal[s_count],
            o_M_AXI_ARADDR 	= 	self.s_araddr_internal[s_count],
            o_M_AXI_ARLEN 	= 	self.s_arlen_internal[s_count],
            o_M_AXI_ARSIZE 	= 	self.s_arsize_internal[s_count],
            o_M_AXI_ARBURST    = 	self.s_arburst_internal[s_count],
            o_M_AXI_ARLOCK 	= 	self.s_arlock_internal[s_count],
            o_M_AXI_ARCACHE 	= 	self.s_arcache_internal[s_count],
            o_M_AXI_ARPROT 	= 	self.s_arprot_internal[s_count],
            o_M_AXI_ARQOS 	= 	self.s_arqos_internal[s_count],
            o_M_AXI_ARVALID 	= 	self.s_arvalid_internal[s_count],
            i_M_AXI_ARREADY 	= 	self.s_arready_internal[s_count],

            i_M_AXI_RID 	= 	self.s_rid_internal[s_count],
            i_M_AXI_RDATA 	= 	self.s_rdata_internal[s_count],
            i_M_AXI_RRESP 	= 	self.s_rresp_internal[s_count],
            i_M_AXI_RLAST 	= 	self.s_rlast_internal[s_count],
            i_M_AXI_RVALID 	= 	self.s_rvalid_internal[s_count],
            o_M_AXI_RREADY 	= 	self.s_rready_internal[s_count],
        )   
        
        # Master interface CDC blocks
        for m_count in range (m_count):
            self.specials += Instance("axi_cdc",
            p_AXI_ID_WIDTH     = 	Instance.PreformattedParam(m_id_width),
            p_AXI_DATA_WIDTH   = 	Instance.PreformattedParam(data_width),
            p_AXI_ADDR_WIDTH   = 	Instance.PreformattedParam(address_width),
            p_SYNC_STAGES      = 	2,
            p_FIFO_LOG         = 	3,
            p_MEM_TYPE		=       bram,

            i_S_AXI_ACLK 	= 	ClockSignal(),
            i_S_AXI_ARESET	=	ResetSignal(),
            i_M_AXI_ACLK	= 	ClockSignal("m{}_axi_aclk".format(m_count)),
            i_M_AXI_ARESET	=	ResetSignal("m{}_axi_areset".format(m_count)),
            
            i_S_AXI_AWID 	= 	self.m_awid_internal[m_count],
            i_S_AXI_AWADDR 	= 	self.m_awaddr_internal[m_count],
            i_S_AXI_AWLEN 	= 	self.m_awlen_internal[m_count],
            i_S_AXI_AWSIZE 	= 	self.m_awsize_internal[m_count],	
            i_S_AXI_AWBURST 	= 	self.m_awburst_internal[m_count],
            i_S_AXI_AWLOCK 	= 	self.m_awlock_internal[m_count],
            i_S_AXI_AWCACHE 	= 	self.m_awcache_internal[m_count],		
            i_S_AXI_AWPROT 	= 	self.m_awprot_internal[m_count],	
            i_S_AXI_AWQOS 	= 	self.m_awqos_internal[m_count],
            i_S_AXI_AWVALID 	= 	self.m_awvalid_internal[m_count],
            o_S_AXI_AWREADY 	= 	self.m_awready_internal[m_count],
            
            i_S_AXI_WDATA 	= 	self.m_wdata_internal[m_count],
            i_S_AXI_WSTRB 	= 	self.m_wstrb_internal[m_count],
            i_S_AXI_WLAST 	= 	self.m_wlast_internal[m_count],
            i_S_AXI_WVALID 	= 	self.m_wvalid_internal[m_count],
            o_S_AXI_WREADY 	= 	self.m_wready_internal[m_count],
            
            o_S_AXI_BID 	= 	self.m_bid_internal[m_count],
            o_S_AXI_BRESP 	= 	self.m_bresp_internal[m_count],
            o_S_AXI_BVALID 	= 	self.m_bvalid_internal[m_count],
            i_S_AXI_BREADY 	= 	self.m_bready_internal[m_count],

            
            i_S_AXI_ARID 	= 	self.m_arid_internal[m_count],
            i_S_AXI_ARADDR 	= 	self.m_araddr_internal[m_count],
            i_S_AXI_ARLEN 	= 	self.m_arlen_internal[m_count],
            i_S_AXI_ARSIZE 	= 	self.m_arsize_internal[m_count],
            i_S_AXI_ARBURST 	= 	self.m_arburst_internal[m_count],
            i_S_AXI_ARLOCK 	= 	self.m_arlock_internal[m_count],
            i_S_AXI_ARCACHE 	= 	self.m_arcache_internal[m_count],    
            i_S_AXI_ARPROT 	= 	self.m_arprot_internal[m_count],
            i_S_AXI_ARQOS 	= 	self.m_arqos_internal[m_count],
            i_S_AXI_ARVALID 	= 	self.m_arvalid_internal[m_count],
            o_S_AXI_ARREADY 	= 	self.m_arready_internal[m_count],
            o_S_AXI_RID 	= 	self.m_rid_internal[m_count],
            o_S_AXI_RDATA 	= 	self.m_rdata_internal[m_count],
            o_S_AXI_RRESP 	= 	self.m_rresp_internal[m_count],
            o_S_AXI_RLAST 	= 	self.m_rlast_internal[m_count],  
            o_S_AXI_RVALID 	= 	self.m_rvalid_internal[m_count],
            i_S_AXI_RREADY 	= 	self.m_rready_internal[m_count],
   
            o_M_AXI_AWID 	= 	m_axi[m_count].aw.id,
            o_M_AXI_AWADDR 	= 	m_axi[m_count].aw.addr,
            o_M_AXI_AWLEN 	= 	m_axi[m_count].aw.len,
            o_M_AXI_AWSIZE 	=	m_axi[m_count].aw.size,
            o_M_AXI_AWBURST 	= 	m_axi[m_count].aw.burst,
            o_M_AXI_AWLOCK 	= 	m_axi[m_count].aw.lock,
            o_M_AXI_AWCACHE 	= 	m_axi[m_count].aw.cache,
            o_M_AXI_AWPROT 	= 	m_axi[m_count].aw.prot,
            o_M_AXI_AWQOS 	= 	m_axi[m_count].aw.qos,
            o_M_AXI_AWVALID 	= 	m_axi[m_count].aw.valid,			
            i_M_AXI_AWREADY 	= 	m_axi[m_count].aw.ready,

            o_M_AXI_WDATA 	= 	m_axi[m_count].w.data,
            o_M_AXI_WSTRB 	= 	m_axi[m_count].w.strb,
            o_M_AXI_WLAST 	= 	m_axi[m_count].w.last,
            o_M_AXI_WVALID 	= 	m_axi[m_count].w.valid,
            i_M_AXI_WREADY 	= 	m_axi[m_count].w.ready,


            i_M_AXI_BID 	= 	m_axi[m_count].b.id,
            i_M_AXI_BRESP 	= 	m_axi[m_count].b.resp,
            i_M_AXI_BVALID 	= 	m_axi[m_count].b.valid,
            o_M_AXI_BREADY 	= 	m_axi[m_count].b.ready,


            o_M_AXI_ARID 	= 	m_axi[m_count].ar.id,
            o_M_AXI_ARADDR 	= 	m_axi[m_count].ar.addr,
            o_M_AXI_ARLEN 	= 	m_axi[m_count].ar.len,
            o_M_AXI_ARSIZE 	= 	m_axi[m_count].ar.size,
            o_M_AXI_ARBURST 	= 	m_axi[m_count].ar.burst,
            o_M_AXI_ARLOCK 	= 	m_axi[m_count].ar.lock,
            o_M_AXI_ARCACHE 	= 	m_axi[m_count].ar.cache,
            o_M_AXI_ARPROT 	= 	m_axi[m_count].ar.prot,
            o_M_AXI_ARQOS 	= 	m_axi[m_count].ar.qos,
            o_M_AXI_ARVALID 	= 	m_axi[m_count].ar.valid,
            i_M_AXI_ARREADY 	= 	m_axi[m_count].ar.ready,

            i_M_AXI_RID 	= 	m_axi[m_count].r.id,
            i_M_AXI_RDATA 	= 	m_axi[m_count].r.data,
            i_M_AXI_RRESP 	= 	m_axi[m_count].r.resp,
            i_M_AXI_RLAST 	= 	m_axi[m_count].r.last,
            i_M_AXI_RVALID 	= 	m_axi[m_count].r.valid,
            o_M_AXI_RREADY 	= 	m_axi[m_count].r.ready,


        )
        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_crossbar.v"))
