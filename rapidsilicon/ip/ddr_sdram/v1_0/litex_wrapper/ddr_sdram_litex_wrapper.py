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

# DDR SDRAM ------------------------------------------------------------------------------------------

class AXIDDR(Module):
    def __init__(self, platform, s_axil, ba_bits, row_bits, col_bits, dq_level, read_buffer):

        # Get/Check Parameters.
        # ---------------------
        self.logger = logging.getLogger("ddr_sdram")

        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # Clock Domain.
        clock_domain = s_axil.clock_domain
        self.logger.info(f"Clock Domain     : {colorer(clock_domain)}")


        # Pipeline Output

        self.logger.info(f"===================================================")
        # Module instance.
        # ----------------
        

        self.ddr_ck_p   = Signal()    
        self.ddr_ck_n   = Signal()    
        self.ddr_cke    = Signal()    
        self.ddr_cs_n   = Signal()    
        self.ddr_ras_n  = Signal()    
        self.ddr_cas_n  = Signal()    
        self.ddr_we_n   = Signal()    
        self.ddr_ba     = Signal()
        self.ddr_a      = Signal()
        self.ddr_dm     = Signal()
        # self.ddr_dqs    = Signal()    
        # self.ddr_dq     = Signal()


        self.specials += Instance("ddr_sdram_ctrl",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE         = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID           = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION      = Instance.PreformattedParam("IP_VERSION"),
            p_BA_BITS         = Instance.PreformattedParam(ba_bits),
            p_ROW_BITS        = Instance.PreformattedParam(row_bits),
            p_COL_BITS        = Instance.PreformattedParam(col_bits),
            p_DQ_LEVEL        = Instance.PreformattedParam(dq_level),
            p_READ_BUFFER     = Instance.PreformattedParam(read_buffer),
            # ----------
#            io_clk             = Instance.InOut, #ClockSignal(clock_domain),
#            io_rst             = Instance.InOut, #ResetSignal(clock_domain),


            
            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_awaddr   = s_axil.aw.addr,
            i_awprot   = s_axil.aw.prot, 
            i_awvalid  = s_axil.aw.valid,
            o_awready  = s_axil.aw.ready,

            # W.
            i_wdata    = s_axil.w.data,
            i_wstrb    = s_axil.w.strb,
            i_wvalid   = s_axil.w.valid,
            o_wready   = s_axil.w.ready,

            # B.
            o_bresp    = s_axil.b.resp,
            o_bvalid   = s_axil.b.valid,
            i_bready   = s_axil.b.ready,

            # AR.
            i_araddr   = s_axil.ar.addr,
            i_arprot   = s_axil.ar.prot,
            i_arvalid  = s_axil.ar.valid,
            o_arready  = s_axil.ar.ready,

            # R.
            o_rdata    = s_axil.r.data,
            o_rresp    = s_axil.r.resp,
            o_rvalid   = s_axil.r.valid,
            i_rready   = s_axil.r.ready,


            # DDR Signals

                    
            o_ddr_ck_p         = self.ddr_ck_p,     
            o_ddr_ck_n         = self.ddr_ck_n,     
            o_ddr_cke          = self.ddr_cke, 
            o_ddr_cs_n         = self.ddr_cs_n,     
            o_ddr_ras_n        = self.ddr_ras_n,     
            o_ddr_cas_n        = self.ddr_cas_n,     
            o_ddr_we_n         = self.ddr_we_n,     
            o_ddr_ba           = self.ddr_ba, 
            o_ddr_a            = self.ddr_a, 
            o_ddr_dm           = self.ddr_dm, 
            io_ddr_dqs         = platform.request("ddr_dqs"), #self.ddr_dqs, 
            io_ddr_dq          = platform.request("ddr_dq") #self.ddr_dq
            
            
                            )

        # Add Sources.
        # ------------
        self.add_sources(platform)
    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "ddr_sdram_ctrl.v"))
