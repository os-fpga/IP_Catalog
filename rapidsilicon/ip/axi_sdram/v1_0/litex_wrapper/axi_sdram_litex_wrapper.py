#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXI's ddr_sdram.v.

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# Helpers ------------------------------------------------------------------------------------------
class Open(Signal): pass

def colorer(s, color="bright"):
    header  = {
        "bright": "\x1b[1m",
        "green":  "\x1b[32m",
        "cyan":   "\x1b[36m",
        "red":    "\x1b[31m",
        "yellow": "\x1b[33m",
        "underline": "\x1b[4m"}[color]
    trailer = "\x1b[0m"
    return header + str(s) + trailer

# AXI RAM ------------------------------------------------------------------------------------------

class AXISDRAM(Module):
    def __init__(self, platform, s_axi ):

        # Get/Check Parameters.
        # ---------------------
        self.logger = logging.getLogger("ddr_sdram")

        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # Clock Domain.
        clock_domain = s_axi.clock_domain
        self.logger.info(f"Clock Domain     : {colorer(clock_domain)}")


        # Pipeline Output

        self.logger.info(f"===================================================")
        # Module instance.
        # ----------------
        

        self.sdram_data_input_i     = Signal(16)    
        self.sdram_clk_o            = Signal(1)    
        self.sdram_cke_o            = Signal(1)    
        self.sdram_cs_o             = Signal(1)    
        self.sdram_ras_o            = Signal(1)    
        self.sdram_cas_o            = Signal(1)    
        self.sdram_we_o             = Signal(1)    
        self.sdram_dqm_o            = Signal(2)
        self.sdram_addr_o           = Signal(13)
        self.sdram_ba_o             = Signal(2)
        self.sdram_data_output_o    = Signal(16)    
        self.sdram_data_out_en_o    = Signal(1)


        self.specials += Instance("ddr_sdram",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE         = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID           = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION      = Instance.PreformattedParam("IP_VERSION"),
            # ----------
            i_clk             = ClockSignal(clock_domain),
            i_rst             = ResetSignal(clock_domain),


            
            # AXI Slave Interface.
            # --------------------
            # AW.
            i_inport_awid_i      = s_axi.aw.id,
            i_inport_awaddr_i    = s_axi.aw.addr,
            i_inport_awlen_i     = s_axi.aw.len,
            i_inport_awburst_i   = s_axi.aw.burst,
            i_inport_awvalid_i   = s_axi.aw.valid,
            o_inport_awready_o   = s_axi.aw.ready,

            # W.
            i_inport_wdata_i     = s_axi.w.data,
            i_inport_wstrb_i     = s_axi.w.strb,
            i_inport_wlast_i     = s_axi.w.last,
            i_inport_wvalid_i    = s_axi.w.valid,
            o_inport_wready_o    = s_axi.w.ready,

            # B.
            o_inport_axi_bid_o       = s_axi.b.id,
            o_inport_axi_bresp_o     = s_axi.b.resp,
            o_inport_axi_bvalid_o    = s_axi.b.valid,
            i_inport_axi_bready_i    = s_axi.b.ready,

            # AR.
            i_inport_axi_arid_i      = s_axi.ar.id,
            i_inport_axi_araddr_i    = s_axi.ar.addr,
            i_inport_axi_arlen_i     = s_axi.ar.len,
            i_inport_axi_arburst_i   = s_axi.ar.burst,
            i_inport_axi_arvalid_i   = s_axi.ar.valid,
            o_inport_axi_arready_o   = s_axi.ar.ready,

            # R.
            o_inport_axi_rid_o       = s_axi.r.id,
            o_inport_axi_rdata_o     = s_axi.r.data,
            o_inport_axi_rresp_o     = s_axi.r.resp,
            o_inport_axi_rlast_o     = s_axi.r.last,
            o_inport_axi_rvalid_o    = s_axi.r.valid,
            i_inport_axi_rready_i    = s_axi.r.ready,

            i_sdram_data_input_i     = self.sdram_data_input_i,           
            o_sdram_clk_o            = self.sdram_clk_o,   
            o_sdram_cke_o            = self.sdram_cke_o,   
            o_sdram_cs_o             = self.sdram_cs_o,   
            o_sdram_ras_o            = self.sdram_ras_o,   
            o_sdram_cas_o            = self.sdram_cas_o,   
            o_sdram_we_o             = self.sdram_we_o,   
            o_sdram_dqm_o            = self.sdram_dqm_o,   
            o_sdram_addr_o           = self.sdram_addr_o,   
            o_sdram_ba_o             = self.sdram_ba_o,   
            o_sdram_data_output_o    = self.sdram_data_output_o,           
            o_sdram_data_out_en_o    = self.sdram_data_out_en_o,           

        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "sdram_axi.v"))
        platform.add_source(os.path.join(rtl_dir, "sdram_axi_pmem.v"))
        platform.add_source(os.path.join(rtl_dir, "sdram_axi_core.v"))
