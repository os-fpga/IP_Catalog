#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Smartfox Data Solutions Inc. AXI_LITE_TEMP_SENSOR's AXI_LITE_TEMP_SENSOR.sv

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')
class AXILITETEMPSENSOR(Module):
    def __init__(self, platform, s_axil):

        # Get Parameters
        # --------------
        self.logger = logging.getLogger("AXI_LITE_TEMP_SENSOR")
        
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # Clock Domain.
        clock_domain = s_axil.clock_domain
        self.logger.info(f"Clock Domain     : {clock_domain}")
        
        # Data width.
        data_width = len(s_axil.w.data)
        self.logger.info(f"Data Width       : {data_width}")

        # Address width.
        address_width = len(s_axil.aw.addr)
        self.logger.info(f"Address Width    : {address_width}")
        self.wdata    = Signal(len(s_axil.w.data))
        self.waddr    = Signal(len(s_axil.aw.addr))
        self.wstrb    = Signal(4)
        self.wvalid    = Signal(1)
        self.awdata    = Signal(len(s_axil.w.data))
        self.awaddr    = Signal(len(s_axil.aw.addr))
        self.awprot    = Signal(3)
        self.awvalid    = Signal(1)
        self.bready    = Signal(1)



        
        # Module instance.
        # ----------------
        self.specials += Instance("axi_lite_temp_sensor",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE       = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID         = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION    = Instance.PreformattedParam("IP_VERSION"),
            p_C_S_AXI_DATA_WIDTH    = Instance.PreformattedParam(data_width),
            p_C_S_AXI_ADDR_WIDTH    = Instance.PreformattedParam(address_width),
            
            # Clk / Rst.
            # ----------
            i_S_AXI_ACLK           = ClockSignal(clock_domain),
            i_S_AXI_ARESETN         = ResetSignal(clock_domain),
        
            # AXI-Lite Slave Interface.
            # -------------------------
            i_S_AXI_AWADDR   = self.awaddr,
            i_S_AXI_AWPROT   = self.awprot, 
            i_S_AXI_AWVALID  = self.awvalid,

            # W.
            i_S_AXI_WDATA    = self.wdata,
            i_S_AXI_WSTRB    = self.wstrb,
            i_S_AXI_WVALID   = self.wvalid,

            # B.
            i_S_AXI_BREADY   = self.bready,

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
        platform.add_source_dir(rtl_dir)


