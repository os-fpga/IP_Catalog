#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXI's axil_crossbar.v.

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)


# AXI LITE CROSSBAR ------------------------------------------------------------------------------------------
class AXILITECROSSBAR(Module):
    def __init__(self, platform, s_axil, m_axil, s_count, m_count,bram):

        self.s_awaddr_internal  = [Signal(len(s_axil[0].aw.addr)) for s_count in range(s_count+1)]
        self.s_awprot_internal  = [Signal(3) for s_count in range(s_count+1)]
        self.s_awvalid_internal = [Signal(1) for s_count in range(s_count+1)]
        self.s_awready_internal = [Signal(1) for s_count in range(s_count+1)]
        
        self.s_wdata_internal   = [Signal(len(s_axil[0].w.data)) for s_count in range(s_count+1)]
        self.s_wstrb_internal   = [Signal(len(s_axil[0].w.strb)) for s_count in range(s_count+1)]
        self.s_wvalid_internal  = [Signal(1) for s_count in range(s_count+1)]
        self.s_wready_internal  = [Signal(1) for s_count in range(s_count+1)]
        
        self.s_bresp_internal   = [Signal(2) for s_count in range(s_count+1)]
        self.s_bvalid_internal  = [Signal(1) for s_count in range(s_count+1)]
        self.s_bready_internal  = [Signal(1) for s_count in range(s_count+1)]
        
        self.s_araddr_internal  = [Signal(len(s_axil[0].ar.addr)) for s_count in range(s_count+1)]
        self.s_arprot_internal  = [Signal(3) for s_count in range(s_count+1)]
        self.s_arvalid_internal = [Signal(1) for s_count in range(s_count+1)]
        self.s_arready_internal = [Signal(1) for s_count in range(s_count+1)]
        
        self.s_rdata_internal   = [Signal(len(s_axil[0].r.data)) for s_count in range(s_count+1)]
        self.s_rresp_internal   = [Signal(2) for s_count in range(s_count+1)]
        self.s_rvalid_internal  = [Signal(1) for s_count in range(s_count+1)]
        self.s_rready_internal  = [Signal(1) for s_count in range(s_count+1)]
        
        
        self.m_awaddr_internal  = [Signal(len(m_axil[0].aw.addr)) for m_count in range(m_count+1)]
        self.m_awprot_internal  = [Signal(3) for m_count in range(m_count+1)]
        self.m_awvalid_internal = [Signal(1) for m_count in range(m_count+1)]
        self.m_awready_internal = [Signal(1) for m_count in range(m_count+1)]
        
        self.m_wdata_internal   = [Signal(len(m_axil[0].w.data)) for m_count in range(m_count+1)]
        self.m_wstrb_internal   = [Signal(len(m_axil[0].w.strb)) for m_count in range(m_count+1)]
        self.m_wvalid_internal  = [Signal(1) for m_count in range(m_count+1)]
        self.m_wready_internal  = [Signal(1) for m_count in range(m_count+1)]
         
        self.m_bresp_internal   = [Signal(2) for m_count in range(m_count+1)]
        self.m_bvalid_internal  = [Signal(1) for m_count in range(m_count+1)]
        self.m_bready_internal  = [Signal(1) for m_count in range(m_count+1)]
         
        self.m_araddr_internal  = [Signal(len(m_axil[0].ar.addr)) for m_count in range(m_count+1)]
        self.m_arprot_internal  = [Signal(3) for m_count in range(m_count+1)]
        self.m_arvalid_internal = [Signal(1) for m_count in range(m_count+1)]
        self.m_arready_internal = [Signal(1) for m_count in range(m_count+1)]
         
        self.m_rdata_internal   = [Signal(len(m_axil[0].r.data)) for m_count in range(m_count+1)]
        self.m_rresp_internal   = [Signal(2) for m_count in range(m_count+1)]
        self.m_rvalid_internal  = [Signal(1) for m_count in range(m_count+1)]
        self.m_rready_internal  = [Signal(1) for m_count in range(m_count+1)]
        
        self.master_clk         = [Signal(1) for s_count in range(s_count+1)]
        
        self.logger = logging.getLogger("AXI_LITE_CROSSBAR")
        
        self.logger.propagate = False

        # Clock Domain.
        clock_domain = s_axil[0].clock_domain
        self.logger.info(f"CLOCK_DOMAIN : {clock_domain}")
        
        # AXI Inputs (slave interfaces).
        s_count = len(s_axil)
        self.logger.info(f"S_COUNT      : {s_count}")
        
        # AXI outputs (master interfaces).
        m_count = len(m_axil)
        self.logger.info(f"M_COUNT      : {m_count}")
        
        # Data width.
        data_width = len(s_axil[0].w.data)
        self.logger.info(f"DATA_WIDTH   : {data_width}")

        # Address width.
        addr_width = len(s_axil[0].aw.addr)
        self.logger.info(f"ADDR_WIDTH   : {addr_width}")


        # Module instance.
        # ----------------

        self.specials += Instance("axil_crossbar",
            # Parameters.
            # -----------
            p_S_COUNT           = Instance.PreformattedParam(len(s_axil)),
            p_M_COUNT           = Instance.PreformattedParam(len(m_axil)),
            p_DATA_WIDTH        = Instance.PreformattedParam(data_width),
            p_ADDR_WIDTH        = Instance.PreformattedParam(addr_width),

            # Clk / Rst.
            # ----------
            i_clk               = ClockSignal(clock_domain),
            i_rst               = ResetSignal(clock_domain),

            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_s_axil_awaddr     =    Cat(self.s_awaddr_internal),
            i_s_axil_awprot     =    Cat(self.s_awprot_internal),
            i_s_axil_awvalid    =    Cat(self.s_awvalid_internal),
            o_s_axil_awready    =    Cat(self.s_awready_internal),

            # W.   
            i_s_axil_wdata      =    Cat(self.s_wdata_internal),
            i_s_axil_wstrb      =    Cat(self.s_wstrb_internal),
            i_s_axil_wvalid     =    Cat(self.s_wvalid_internal),
            o_s_axil_wready     =    Cat(self.s_wready_internal),

            # B.   
            o_s_axil_bresp      =    Cat(self.s_bresp_internal),
            o_s_axil_bvalid     =    Cat(self.s_bvalid_internal),
            i_s_axil_bready     =    Cat(self.s_bready_internal),

            # AR.   
            i_s_axil_araddr     =    Cat(self.s_araddr_internal),
            i_s_axil_arprot     =    Cat(self.s_arprot_internal),
            i_s_axil_arvalid    =    Cat(self.s_arvalid_internal),
            o_s_axil_arready    =    Cat(self.s_arready_internal),

            # R.   
            o_s_axil_rdata      =    Cat(self.s_rdata_internal),
            o_s_axil_rresp      =    Cat(self.s_rresp_internal),
            o_s_axil_rvalid     =    Cat(self.s_rvalid_internal),
            i_s_axil_rready     =    Cat(self.s_rready_internal),
            
            
            # AXI-Lite Master Interface.
            # -------------------------
            # AW.
            o_m_axil_awaddr     =    Cat(self.m_awaddr_internal),
            o_m_axil_awprot     =    Cat(self.m_awprot_internal),
            o_m_axil_awvalid    =    Cat(self.m_awvalid_internal),
            i_m_axil_awready    =    Cat(self.m_awready_internal),

            # W.
            o_m_axil_wdata      =    Cat(self.m_wdata_internal),
            o_m_axil_wstrb      =    Cat(self.m_wstrb_internal),
            o_m_axil_wvalid     =    Cat(self.m_wvalid_internal),
            o_m_axil_wready     =    Cat(self.m_wready_internal),
   
            # B.   
            i_m_axil_bresp      =    Cat(self.m_bresp_internal),
            i_m_axil_bvalid     =    Cat(self.m_bvalid_internal),
            o_m_axil_bready     =    Cat(self.m_bready_internal),
   
            # AR.   
            o_m_axil_araddr     =    Cat(self.m_araddr_internal),
            o_m_axil_arprot     =    Cat(self.m_arprot_internal),
            o_m_axil_arvalid    =    Cat(self.m_arvalid_internal),
            i_m_axil_arready    =    Cat(self.m_arready_internal),
   
            # R.   
            i_m_axil_rdata      =    Cat(self.m_rdata_internal),
            i_m_axil_rresp      =    Cat(self.m_rresp_internal),
            i_m_axil_rvalid     =    Cat(self.m_rvalid_internal),
            o_m_axil_rready     =    Cat(self.m_rready_internal),
        )
        
        # Slave interface CDC blocks
        for s_count in range (s_count):
            self.specials += Instance("axi_cdc",
            p_AXI_ID_WIDTH      =   0,
            p_AXI_DATA_WIDTH    =   Instance.PreformattedParam(data_width),
            p_AXI_ADDR_WIDTH    =   Instance.PreformattedParam(addr_width),
            p_SYNC_STAGES       =   2,
            p_FIFO_LOG          =   3,
            p_MEM_TYPE		 =   bram,

            i_S_AXI_ACLK        =   ClockSignal("s{}_axi_aclk".format(s_count)),
            i_S_AXI_ARESET      =   ResetSignal("s{}_axi_areset".format(s_count)),
            i_M_AXI_ACLK        =   ClockSignal(),
            i_M_AXI_ARESET      =   ResetSignal(),   
            i_S_AXI_ARADDR      =   s_axil[s_count].ar.addr,
            i_S_AXI_ARPROT      =   s_axil[s_count].ar.prot,
            o_S_AXI_ARREADY     =   s_axil[s_count].ar.ready,
            i_S_AXI_ARVALID     =   s_axil[s_count].ar.valid,
    
    
            i_S_AXI_AWADDR      =   s_axil[s_count].aw.addr,
            i_S_AXI_AWPROT      =   s_axil[s_count].aw.prot,
            o_S_AXI_AWREADY     =   s_axil[s_count].aw.ready,
            i_S_AXI_AWVALID     =   s_axil[s_count].aw.valid,   
            i_S_AXI_BREADY      =   s_axil[s_count].b.ready,
            o_S_AXI_BRESP       =   s_axil[s_count].b.resp,
            o_S_AXI_BVALID      =   s_axil[s_count].b.valid,   
            o_S_AXI_RDATA       =   s_axil[s_count].r.data,
            i_S_AXI_RREADY      =   s_axil[s_count].r.ready,
            o_S_AXI_RRESP       =   s_axil[s_count].r.resp,
            o_S_AXI_RVALID      =   s_axil[s_count].r.valid,   
            i_S_AXI_WDATA       =   s_axil[s_count].w.data,
            o_S_AXI_WREADY      =   s_axil[s_count].w.ready,
            i_S_AXI_WSTRB       =   s_axil[s_count].w.strb,
            i_S_AXI_WVALID      =   s_axil[s_count].w.valid,   
    
            o_M_AXI_AWADDR      =   self.s_awaddr_internal[s_count],
            o_M_AXI_AWPROT      =   self.s_awprot_internal[s_count],
            o_M_AXI_AWVALID     =   self.s_awvalid_internal[s_count],
            i_M_AXI_AWREADY     =   self.s_awready_internal[s_count],   
            o_M_AXI_WDATA       =   self.s_wdata_internal[s_count],
            o_M_AXI_WSTRB       =   self.s_wstrb_internal[s_count],
            o_M_AXI_WVALID      =   self.s_wvalid_internal[s_count],
            i_M_AXI_WREADY      =   self.s_wready_internal[s_count],   
            i_M_AXI_BRESP       =   self.s_bresp_internal[s_count],
            i_M_AXI_BVALID      =   self.s_bvalid_internal[s_count],
            o_M_AXI_BREADY      =   self.s_bready_internal[s_count],   
            o_M_AXI_ARADDR      =   self.s_araddr_internal[s_count],
            o_M_AXI_ARPROT      =   self.s_arprot_internal[s_count],
            o_M_AXI_ARVALID     =   self.s_arvalid_internal[s_count],
            i_M_AXI_ARREADY     =   self.s_arready_internal[s_count],   
            i_M_AXI_RDATA       =   self.s_rdata_internal[s_count],
            i_M_AXI_RRESP       =   self.s_rresp_internal[s_count],
            i_M_AXI_RVALID      =   self.s_rvalid_internal[s_count],
            o_M_AXI_RREADY      =   self.s_rready_internal[s_count],
    
    
        )       
        # Master interface CDC blocks
        for m_count in range     (m_count):
            self.specials += Instance("axi_cdc",
            p_AXI_ID_WIDTH      =   0,
            p_AXI_DATA_WIDTH    =   Instance.PreformattedParam(data_width),
            p_AXI_ADDR_WIDTH    =   Instance.PreformattedParam(addr_width),
            p_SYNC_STAGES       =   2,
            p_FIFO_LOG          =   3,
            p_MEM_TYPE		 =   bram,

            i_S_AXI_ACLK        =   ClockSignal(),
            i_S_AXI_ARESET      =   ResetSignal(),
            i_M_AXI_ACLK        =   ClockSignal("m{}_axi_aclk".format(m_count)),
            i_M_AXI_ARESET      =   ResetSignal("m{}_axi_areset".format(m_count)),   
            i_S_AXI_ARADDR      =   self.m_araddr_internal[m_count],
            i_S_AXI_ARPROT      =   self.m_arprot_internal[m_count],
            o_S_AXI_ARREADY     =   self.m_arready_internal[m_count],
            i_S_AXI_ARVALID     =   self.m_arvalid_internal[m_count],   
            i_S_AXI_AWADDR      =   self.m_awaddr_internal[m_count],	
            i_S_AXI_AWPROT      =   self.m_awprot_internal[m_count],	
            o_S_AXI_AWREADY     =   self.m_awready_internal[m_count],
            i_S_AXI_AWVALID     =   self.m_awvalid_internal[m_count],   
            i_S_AXI_BREADY      =   self.m_bready_internal[m_count],
            o_S_AXI_BRESP       =   self.m_bresp_internal[m_count],
            o_S_AXI_BVALID      =   self.m_bvalid_internal[m_count],   
            o_S_AXI_RDATA       =   self.m_rdata_internal[m_count],
            i_S_AXI_RREADY      =   self.m_rready_internal[m_count],
            o_S_AXI_RRESP       =   self.m_rresp_internal[m_count],
            o_S_AXI_RVALID      =   self.m_rvalid_internal[m_count],   
            i_S_AXI_WDATA       =   self.m_wdata_internal[m_count],
            o_S_AXI_WREADY      =   self.m_wready_internal[m_count],
            i_S_AXI_WSTRB       =   self.m_wstrb_internal[m_count],
            i_S_AXI_WVALID      =   self.m_wvalid_internal[m_count],   
    
            o_M_AXI_AWADDR      =   m_axil[m_count].aw.addr,
            o_M_AXI_AWPROT      =   m_axil[m_count].aw.prot,
            o_M_AXI_AWVALID     =   m_axil[m_count].aw.valid,			
            i_M_AXI_AWREADY     =   m_axil[m_count].aw.ready,

            o_M_AXI_WDATA       =   m_axil[m_count].w.data,
            o_M_AXI_WSTRB       =   m_axil[m_count].w.strb,
            o_M_AXI_WVALID      =   m_axil[m_count].w.valid,
            i_M_AXI_WREADY      =   m_axil[m_count].w.ready,


            i_M_AXI_BRESP       =   m_axil[m_count].b.resp,
            i_M_AXI_BVALID      =   m_axil[m_count].b.valid,
            o_M_AXI_BREADY      =   m_axil[m_count].b.ready,  
            o_M_AXI_ARADDR      =   m_axil[m_count].ar.addr,
            o_M_AXI_ARPROT      =   m_axil[m_count].ar.prot,
            o_M_AXI_ARVALID     =   m_axil[m_count].ar.valid,
            i_M_AXI_ARREADY     =   m_axil[m_count].ar.ready,

            i_M_AXI_RDATA       =   m_axil[m_count].r.data,
            i_M_AXI_RRESP       =   m_axil[m_count].r.resp,
            i_M_AXI_RVALID      =   m_axil[m_count].r.valid,
            o_M_AXI_RREADY      =   m_axil[m_count].r.ready,
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axil_crossbar.v"))
