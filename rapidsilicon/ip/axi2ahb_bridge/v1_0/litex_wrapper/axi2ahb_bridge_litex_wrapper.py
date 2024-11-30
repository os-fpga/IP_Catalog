#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around western digital's axi2ahb.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# AHB_2_AXI4_BRIDGE ---------------------------------------------------------------------------------------
class AXI2AHB(Module):
    def __init__(self, platform, m_axi):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("AHB_2_AXI4")
        
        self.logger.propagate = True

        # Clock Domain.
        # self.logger.info(f"CLOCK_DOMAIN     : {s_ahb.clock_domain}")
        self.logger.info(f"=================== PARAMETERS ====================")
        # Address width.
        address_width = len(m_axi.aw.addr)
        self.logger.info(f"C_AXI_ADDR_WIDTH : {address_width}")

        # Data width.
        data_width = len(m_axi.w.data)
        self.logger.info(f"C_AXI_DATA_WIDTH : {data_width}")

        # ID width.
        id_width = len(m_axi.aw.id)
        self.logger.info(f"C_AXI_ID_WIDTH   : {id_width}")
        
        self.logger.info(f"===================================================")
        
        self.ahb_haddr               = Signal(address_width)
        self.ahb_hburst              = Signal(3)
        self.ahb_hmastlock           = Signal(1)
        self.ahb_hprot               = Signal(4)
        self.ahb_hsize               = Signal(3)
        self.ahb_htrans              = Signal(2)
        self.ahb_hwrite              = Signal(1)
        self.ahb_hwdata              = Signal(data_width)
        self.ahb_hrdata              = Signal(data_width)
        self.ahb_hready           = Signal(1)
        self.ahb_hresp               = Signal(1)
        
        # Module instance.
        # ----------------
        self.specials += Instance("ahb_to_axi4",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE           = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID             = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION        = Instance.PreformattedParam("IP_VERSION"),
            # Global AXI
            p_data_width        = Instance.PreformattedParam(data_width),
            p_addr_width        = Instance.PreformattedParam(address_width),
            p_id_width          = Instance.PreformattedParam(id_width),  

            # Clk / Rst.
            i_clk               = ClockSignal(),
            i_rst_l             = ResetSignal(),

            # AHB Slave Interface.
            # --------------------
            
            o_ahb_haddr            		= self.ahb_haddr,
            o_ahb_hburst            	= self.ahb_hburst,
            o_ahb_hmastlock           = self.ahb_hmastlock,
            o_ahb_hprot            		= self.ahb_hprot,
            o_ahb_hsize            		= self.ahb_hsize,
            o_ahb_htrans           		= self.ahb_htrans,
            o_ahb_hwrite           		= self.ahb_hwrite,
            o_ahb_hwdata           		= self.ahb_hwdata, 
            i_ahb_hrdata           		= self.ahb_hrdata,
            i_ahb_hready              = self.ahb_hready,  
            i_ahb_hresp           		= self.ahb_hresp,

            
            
            # AXI master Interface.
            # --------------------
            # AW.
            i_axi_awid            = m_axi.aw.id,
            i_axi_awaddr          = m_axi.aw.addr,
            o_axi_awlen           = m_axi.aw.len,
            i_axi_awsize          = m_axi.aw.size,
            o_axi_awburst         = m_axi.aw.burst,
          #  o_S_AXI_AWLOCK          = m_axi.aw.lock,
          #  o_S_AXI_AWCACHE         = m_axi.aw.cache,
            i_axi_awprot          = m_axi.aw.prot,
          #  o_S_AXI_AWQOS           = m_axi.aw.qos,
            i_axi_awvalid         = m_axi.aw.valid,
            o_axi_awready         = m_axi.aw.ready,

            # W.
            i_axi_wdata           = m_axi.w.data,
            i_axi_wstrb           = m_axi.w.strb,
            i_axi_wlast           = m_axi.w.last,
            i_axi_wvalid          = m_axi.w.valid,
            o_axi_wready          = m_axi.w.ready,

            # B.
            o_axi_bid             = m_axi.b.id,
            o_axi_bresp           = m_axi.b.resp,
            o_axi_bvalid          = m_axi.b.valid,
            i_axi_bready          = m_axi.b.ready,

            # AR.
            i_axi_arid            = m_axi.ar.id,
            i_axi_araddr          = m_axi.ar.addr,
            i_axi_arlen           = m_axi.ar.len,
            i_axi_arsize          = m_axi.ar.size,
            i_axi_arburst         = m_axi.ar.burst,
          #  o_S_AXI_ARLOCK          = m_axi.ar.lock,
          #  o_S_AXI_ARCACHE         = m_axi.ar.cache,
            i_axi_arprot          = m_axi.ar.prot,
          #  o_S_AXI_ARQOS           = m_axi.ar.qos,
            i_axi_arvalid         = m_axi.ar.valid,
            o_axi_arready         = m_axi.ar.ready,

            # R.
            o_axi_rid             = m_axi.r.id,
            o_axi_rdata           = m_axi.r.data,
            o_axi_rresp           = m_axi.r.resp,
          #  o_S_AXI_RLAST           = m_axi.r.last,
            o_axi_rvalid          = m_axi.r.valid,
            i_axi_rready          = m_axi.r.ready,
         
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi2ahb.sv"))
