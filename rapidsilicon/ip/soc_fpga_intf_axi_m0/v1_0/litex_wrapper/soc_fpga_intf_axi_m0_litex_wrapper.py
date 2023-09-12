#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#

import os
import datetime
import logging

from migen import *

# SOC_FPGA_INTF_AXI_M0 Wrapper ----------------------------------------------------------------------

class SOC_FPGA_INTF_AXI_M0(Module):
    def __init__(self, platform):
        self.logger = logging.getLogger("SOC_FPGA_INTF_AXI_M0")
        self.logger.propagate = True

        self.logger.info("Creating SOC_FPGA_INTF_AXI_M0 module.")

        # Create input signals
        self.m0_araddr = Signal(32)
        self.m0_arburst = Signal(2)
        self.m0_arcache = Signal(4)
        self.m0_arid = Signal(4)
        self.m0_arlen = Signal(3)
        self.m0_arlock = Signal()
        self.m0_arprot = Signal(3)
        self.m0_arvalid = Signal()
        self.m0_awaddr = Signal(32)
        self.m0_awburst = Signal(2)
        self.m0_awcache = Signal(4)
        self.m0_awid = Signal(4)
        self.m0_awlen = Signal(3)
        self.m0_awlock = Signal()
        self.m0_awprot = Signal(3)
        self.m0_awvalid = Signal()
        self.m0_bready = Signal()
        self.m0_awsize = Signal(3)
        self.m0_arsize = Signal(3)
        self.m0_wdata = Signal(64)
        self.m0_wlast = Signal()
        self.m0_wstrb = Signal(8)
        self.m0_wvalid = Signal()
        self.m0_aclk = Signal()
        self.m0_aresetn_i = Signal()

        # Create output signals
        self.m0_arready = Signal()
        self.m0_awready = Signal()
        self.m0_bid = Signal(4)
        self.m0_bresp = Signal(2)
        self.m0_bvalid = Signal()
        self.m0_rdata = Signal(64)
        self.m0_rid = Signal(4)
        self.m0_rlast = Signal()
        self.m0_rready = Signal()
        self.m0_rresp = Signal(2)
        self.m0_rvalid = Signal()
        self.m0_wready = Signal()

        self.specials += Instance("SOC_FPGA_INTF_AXI_M0",
            i_M0_ARADDR=self.m0_araddr,
            i_M0_ARBURST=self.m0_arburst,
            i_M0_ARCACHE=self.m0_arcache,
            i_M0_ARID=self.m0_arid,
            i_M0_ARLEN=self.m0_arlen,
            i_M0_ARLOCK=self.m0_arlock,
            i_M0_ARPROT=self.m0_arprot,
            o_M0_ARREADY=self.m0_arready,
            i_M0_ARSIZE=self.m0_arsize,
            i_M0_ARVALID=self.m0_arvalid,
            i_M0_AWADDR=self.m0_awaddr,
            i_M0_AWBURST=self.m0_awburst,
            i_M0_AWCACHE=self.m0_awcache,
            i_M0_AWID=self.m0_awid,
            i_M0_AWLEN=self.m0_awlen,
            i_M0_AWLOCK=self.m0_awlock,
            i_M0_AWPROT=self.m0_awprot,
            o_M0_AWREADY=self.m0_awready,
            i_M0_AWSIZE=self.m0_awsize,
            i_M0_AWVALID=self.m0_awvalid,
            o_M0_BID=self.m0_bid,
            i_M0_BREADY=self.m0_bready,
            o_M0_BRESP=self.m0_bresp,
            o_M0_BVALID=self.m0_bvalid,
            o_M0_RDATA=self.m0_rdata,
            o_M0_RID=self.m0_rid,
            o_M0_RLAST=self.m0_rlast,
            i_M0_RREADY=self.m0_rready,
            o_M0_RRESP=self.m0_rresp,
            o_M0_RVALID=self.m0_rvalid,
            i_M0_WDATA=self.m0_wdata,
            i_M0_WLAST=self.m0_wlast,
            o_M0_WREADY=self.m0_wready,
            i_M0_WSTRB=self.m0_wstrb,
            i_M0_WVALID=self.m0_wvalid,
            i_M0_ACLK=self.m0_aclk,
            o_M0_ARESETN_I=self.m0_aresetn_i
        )

        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "soc_fpga_intf_axi_m0.v"))

# Main -------------------------------------------------------------------------------------------

if __name__ == "__main__":
    platform = None  # Create or load your platform here
    logging.basicConfig(filename="IP.log", filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f'Log started at {timestamp}')

    soc_fpga_intf_axi_m0 = SOC_FPGA_INTF_AXI_M0(platform)
