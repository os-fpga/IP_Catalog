#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around RS OCLA IP CORE ocla.v

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXI LITE OCLA -------------------------------------------------------------------------------------
class AXILITEOCLA(Module):
    def __init__(self, platform, 
                 s_axil, 
                 nprobes, 
                 trigger_inputs, 
                 probe_widht,
                 mem_depth, 
                 trigger_inputs_en):
        
        #self.logger = logging.getLogger("AXI_LITE_OCLA")
        
        #self.logger.propagate = True
        
        # Clock Domain
        clock_domain = s_axil.clock_domain
        #self.logger.info(f"CLOCK_DOMAIN     : {clock_domain}")
        
        # Address width.
        address_width = len(s_axil.aw.addr)
        #self.logger.info(f"ADDRESS_WIDTH    : {address_width}")
        
        # Read Data width.
        data_width = len(s_axil.r.data)
        #self.logger.info(f"DATA_WIDTH       : {data_width}")
        
        # OCLA features.
        #self.logger.info(f"NO_OF_PROBES          : {nprobes}")
        #self.logger.info(f"NO_OF_TRIGGER_INPUTS  : {trigger_inputs}")
        #self.logger.info(f"PROBE_WIDHT           : {probe_widht}")
        #self.logger.info(f"MEM_DEPTH             : {mem_depth}")

        
        # OCLA Signals
        if(trigger_inputs_en == True):
            self.trigger_input_i    = Signal(trigger_inputs)
        self.probes_i           = Signal(nprobes)  

        
        if(trigger_inputs_en == True):
        # Module instance.
        # ----------------
            self.specials += Instance("ocla",
                                                    
        # Parameters.
            # -----------            
            p_NO_OF_PROBES            = Instance.PreformattedParam(nprobes),
            p_NO_OF_TRIGGER_INPUTS    = Instance.PreformattedParam(trigger_inputs),
            p_PROBE_WIDHT             = Instance.PreformattedParam(probe_widht),
            p_MEM_DEPTH               = Instance.PreformattedParam(mem_depth),
            p_AXI_DATA_WIDTH          = Instance.PreformattedParam(data_width),
            p_AXI_ADDR_WIDTH          = Instance.PreformattedParam(address_width),

            # sampling Clk / Rst.
            # ----------
            i_sample_clk       = ClockSignal("i_sample_clk"),
            i_rstn             = ResetSignal("i_rstn"),
            
            # AXI Clk / Rst.
            # ----------
            i_S_AXI_ACLK       = ClockSignal(),
            i_S_AXI_ARESETN    = ResetSignal(),
            
            # OCLA Signals
            i_trigger_input    = self.trigger_input_i,
            i_probes           = self.probes_i,

            
            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_S_AXI_AWADDR   = s_axil.aw.addr,
            i_S_AXI_AWPROT   = s_axil.aw.prot, 
            i_S_AXI_AWVALID  = s_axil.aw.valid,
            o_S_AXI_AWREADY  = s_axil.aw.ready,

            # W.
            i_S_AXI_WDATA    = s_axil.w.data,
            i_S_AXI_WSTRB    = s_axil.w.strb,
            i_S_AXI_WVALID   = s_axil.w.valid,
            o_S_AXI_WREADY   = s_axil.w.ready,

            # B.
            o_S_AXI_BRESP    = s_axil.b.resp,
            o_S_AXI_BVALID   = s_axil.b.valid,
            i_S_AXI_BREADY   = s_axil.b.ready,

            # AR.
            i_S_AXI_ARADDR   = s_axil.ar.addr,
            i_S_AXI_ARPROT   = s_axil.ar.prot,
            i_S_AXI_ARVALID  = s_axil.ar.valid,
            o_S_AXI_ARREADY  = s_axil.ar.ready,

            # R.
            o_S_AXI_RDATA    = s_axil.r.data,
            o_S_AXI_RRESP    = s_axil.r.resp,
            o_S_AXI_RVALID   = s_axil.r.valid,
            i_S_AXI_RREADY   = s_axil.r.ready,
        )
            
        else:
            self.specials += Instance("ocla",
                                                    
        # Parameters.
            # -----------            
            p_NO_OF_PROBES            = Instance.PreformattedParam(nprobes),
            p_NO_OF_TRIGGER_INPUTS    = Instance.PreformattedParam(trigger_inputs),
            p_PROBE_WIDHT             = Instance.PreformattedParam(probe_widht),
            p_MEM_DEPTH               = Instance.PreformattedParam(mem_depth),
            p_AXI_DATA_WIDTH          = Instance.PreformattedParam(data_width),
            p_AXI_ADDR_WIDTH          = Instance.PreformattedParam(address_width),

            # sampling Clk / Rst.
            # ----------
            i_sample_clk       = ClockSignal("i_sample_clk"),
            i_rstn             = ResetSignal("i_rstn"),
            
            
            # AXI Clk / Rst.
            # ----------
            i_S_AXI_ACLK       = ClockSignal(),
            i_S_AXI_ARESETN    = ResetSignal(),
            
            # OCLA Signals
            i_probes           = self.probes_i,

            
            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_S_AXI_AWADDR   = s_axil.aw.addr,
            i_S_AXI_AWPROT   = s_axil.aw.prot, 
            i_S_AXI_AWVALID  = s_axil.aw.valid,
            o_S_AXI_AWREADY  = s_axil.aw.ready,

            # W.
            i_S_AXI_WDATA    = s_axil.w.data,
            i_S_AXI_WSTRB    = s_axil.w.strb,
            i_S_AXI_WVALID   = s_axil.w.valid,
            o_S_AXI_WREADY   = s_axil.w.ready,

            # B.
            o_S_AXI_BRESP    = s_axil.b.resp,
            o_S_AXI_BVALID   = s_axil.b.valid,
            i_S_AXI_BREADY   = s_axil.b.ready,

            # AR.
            i_S_AXI_ARADDR   = s_axil.ar.addr,
            i_S_AXI_ARPROT   = s_axil.ar.prot,
            i_S_AXI_ARVALID  = s_axil.ar.valid,
            o_S_AXI_ARREADY  = s_axil.ar.ready,

            # R.
            o_S_AXI_RDATA    = s_axil.r.data,
            o_S_AXI_RRESP    = s_axil.r.resp,
            o_S_AXI_RVALID   = s_axil.r.valid,
            i_S_AXI_RREADY   = s_axil.r.ready,
        )
        # Add Sources.
        # ------------
        self.add_sources(platform)
    
    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "ocla.sv"))
