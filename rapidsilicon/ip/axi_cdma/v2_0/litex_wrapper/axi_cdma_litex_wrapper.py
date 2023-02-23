#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around ZipCPU Verilog-AXI's axicdma.v

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXI CDMA ---------------------------------------------------------------------------------------
class AXICDMA(Module):
    def __init__(self, platform, axi, axil):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("AXI_CDMA")
        
        self.logger.propagate = False

        # Clock Domain.
        self.logger.info(f"Clock Domain     : {axi.clock_domain}")

        # Address width.
        m_address_width = len(axi.aw.addr)
        s_address_width = len(axil.aw.addr)
        self.logger.info(f"AXI_ADDR_WIDTH   : {m_address_width}")

        # Data width.
        m_data_width = len(axi.w.data)
        s_data_width = len(axil.w.data)
        self.logger.info(f"AXI_DATA_WIDTH   : {m_data_width}")

        # ID width.
        id_width = len(axi.aw.id)
        self.logger.info(f"AXI_ID_WIDTH     : {id_width}")
        
       
        self.o_int   = Signal()
    

        # Module instance.
        # ----------------
        self.specials += Instance("axi_cdma",
            # Parameters.
            # -----------
            # Global AXI
            p_C_AXI_DATA_WIDTH          = (m_data_width),
            p_C_AXI_ADDR_WIDTH          = (m_address_width),
            p_C_AXI_ID_WIDTH            = (id_width),
            
            # Global AXILite
            p_C_AXIL_DATA_WIDTH         = (s_data_width),
            p_C_AXIL_ADDR_WIDTH         = (s_address_width),
           


            # Clk / Rst.
            i_S_AXI_ACLK                = ClockSignal(axi.clock_domain),
            i_S_AXI_ARESETN              = ResetSignal(axi.clock_domain),


            # AXI master Interface.
            # --------------------
            # AW.
            o_M_AXI_AWID                = axi.aw.id,
            o_M_AXI_AWADDR              = axi.aw.addr,
            o_M_AXI_AWLEN               = axi.aw.len,
            o_M_AXI_AWSIZE              = axi.aw.size,
            o_M_AXI_AWBURST             = axi.aw.burst,
            o_M_AXI_AWLOCK              = axi.aw.lock,
            o_M_AXI_AWCACHE             = axi.aw.cache,
            o_M_AXI_AWPROT              = axi.aw.prot,
            o_M_AXI_AWQOS               = axi.aw.qos,
            o_M_AXI_AWVALID             = axi.aw.valid,
            i_M_AXI_AWREADY             = axi.aw.ready,

            # W.
            o_M_AXI_WDATA               = axi.w.data,
            o_M_AXI_WSTRB               = axi.w.strb,
            o_M_AXI_WLAST               = axi.w.last,
            o_M_AXI_WVALID              = axi.w.valid,
            i_M_AXI_WREADY              = axi.w.ready,

            # B.
            i_M_AXI_BID                 = axi.b.id,
            i_M_AXI_BRESP              = axi.b.resp,
            i_M_AXI_BVALID              = axi.b.valid,
            o_M_AXI_BREADY              = axi.b.ready,

            # AR.
            o_M_AXI_ARID               = axi.ar.id,
            o_M_AXI_ARADDR             = axi.ar.addr,
            o_M_AXI_ARLEN              = axi.ar.len,
            o_M_AXI_ARSIZE             = axi.ar.size,
            o_M_AXI_ARBURST            = axi.ar.burst,
            o_M_AXI_ARLOCK            = axi.ar.lock,
            o_M_AXI_ARCACHE            = axi.ar.cache,
            o_M_AXI_ARPROT             = axi.ar.prot,
            o_M_AXI_ARQOS              = axi.ar.qos,

            o_M_AXI_ARVALID            = axi.ar.valid,
            i_M_AXI_ARREADY            = axi.ar.ready,

            # R.
            i_M_AXI_RID                = axi.r.id,
            i_M_AXI_RDATA              = axi.r.data,
            i_M_AXI_RRESP              = axi.r.resp,
            i_M_AXI_RLAST              = axi.r.last,
            i_M_AXI_RVALID             = axi.r.valid,
            o_M_AXI_RREADY             = axi.r.ready,




            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_S_AXIL_AWADDR           = axil.aw.addr,
            i_S_AXIL_AWPROT           = axil.aw.prot,
            i_S_AXIL_AWVALID          = axil.aw.valid,
            o_S_AXIL_AWREADY          = axil.aw.ready,

            # W.
            i_S_AXIL_WDATA            = axil.w.data,
            i_S_AXIL_WSTRB            = axil.w.strb,
            i_S_AXIL_WVALID           = axil.w.valid,
            o_S_AXIL_WREADY           = axil.w.ready,

            # B.
            o_S_AXIL_BRESP            = axil.b.resp,
            o_S_AXIL_BVALID           = axil.b.valid,
            i_S_AXIL_BREADY           = axil.b.ready,

            # AR.
            i_S_AXIL_ARADDR           = axil.ar.addr,
            i_S_AXIL_ARPROT           = axil.ar.prot,
            i_S_AXIL_ARVALID          = axil.ar.valid,
            o_S_AXIL_ARREADY          = axil.ar.ready,

            # R.
            o_S_AXIL_RDATA            = axil.r.data,
            o_S_AXIL_RRESP            = axil.r.resp,
            o_S_AXIL_RVALID           = axil.r.valid,
            i_S_AXIL_RREADY           = axil.r.ready,
            o_o_int                   =  self.o_int, 

        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axicdma.v"))
