#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around eio_top.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# AXIL_EIO ---------------------------------------------------------------------------------
class AXILEIO(Module):
    def __init__(self, 
                platform, 
                s_axil, 
                input_probe_width, 
                output_probe_width, 
                axi_input_clk_sync, 
                axi_output_clk_sync
                ):
        
        self.logger = logging.getLogger("AXIL_EIO")
        
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # Clock Domain.
        clock_domain = s_axil.clock_domain
        self.logger.info(f"CLOCK_DOMAIN : {clock_domain}")

        # Address width.
        address_width = len(s_axil.aw.addr)
        self.logger.info(f"ADDR_WIDTH   : {address_width}")

        # Data width.
        data_width = len(s_axil.w.data)
        self.logger.info(f"DATA_WIDTH   : {data_width}")
        self.logger.info(f"===================================================")
        self.probe_in    = Signal(input_probe_width)
        self.probe_out   = Signal(output_probe_width)

        self.IP_CLK        = Signal(1)
        self.OP_CLK        = Signal(1)
        self.S_AXI_ACLK    = Signal(1) 
        self.S_AXI_ARESETN = Signal(1)

        # Module instance.
        # ----------------
        self.specials += Instance("eio_top",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE               = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID                 = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION            = Instance.PreformattedParam("IP_VERSION"),
            p_C_S_AXI_DATA_WIDTH    = Instance.PreformattedParam(data_width),
            p_C_S_AXI_ADDR_WIDTH    = Instance.PreformattedParam(address_width),
            p_INPUT_PROBE_WIDTH     = Instance.PreformattedParam(input_probe_width),
            p_OUTPUT_PROBE_WIDTH    = Instance.PreformattedParam(output_probe_width),
            p_AXI_IN_CLOCKS_SYNCED  = axi_input_clk_sync,
            p_AXI_OUT_CLOCKS_SYNCED = axi_output_clk_sync,

            # Clk / Rst.
            # ----------
            i_S_AXI_ACLK     = self.S_AXI_ACLK,
            i_S_AXI_ARESETN  = self.S_AXI_ARESETN,
            i_IP_CLK         = self.IP_CLK,
            i_OP_CLK         = self.OP_CLK,
            
            # IN/OUT probes
            # -------------
            i_probe_in       = self.probe_in,
            o_probe_out      = self.probe_out,
            
            # AXI Slave Interface
            # ----------------------
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
            i_S_AXI_RREADY   = s_axil.r.ready
        )
        
        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "eio_top.v"))
