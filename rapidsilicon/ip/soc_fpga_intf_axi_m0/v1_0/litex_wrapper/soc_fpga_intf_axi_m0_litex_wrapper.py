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

class SOC_FPGA_INTF_AXI_M0(Module):
    def __init__(self, platform, m0):
        self.logger = logging.getLogger("SOC_FPGA_INTF_AXI_M0")

        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # Clock Domain.
        clock_domain = m0.clock_domain
        self.logger.info(f"Clock Domain     : {colorer(clock_domain)}")

        # Address width.
        address_width = len(m0.aw.addr)
        self.logger.info(f"Address Width    : {colorer(address_width)}")

        # Data width.
        data_width = len(m0.w.data)
        self.logger.info(f"Data Width       : {colorer(data_width)}")


        # ID width.
        id_width = len(m0.aw.id)
        self.logger.info(f"ID Width         : {colorer(id_width)}")
        

        self.logger.info(f"===================================================")
        # Module instance.
        # ----------------
        self.logger.info("Creating SOC_FPGA_INTF_AXI_M0 module.")


        self.specials += Instance("soc_fpga_intf_axi_m0",
            # Parameters.
            # -----------
            p_DATA_WIDTH      = Instance.PreformattedParam(data_width),
            p_ADDR_WIDTH      = Instance.PreformattedParam(address_width),
            p_ID_WIDTH        = Instance.PreformattedParam(id_width),                                  

            i_M0_ARADDR       = m0.ar.addr, 
            i_M0_ARBURST      = m0.ar.burst,    
            i_M0_ARCACHE      = m0.ar.cache,    
            i_M0_ARID         = m0.ar.id,
            i_M0_ARLEN        = m0.ar.len,
            i_M0_ARLOCK       = m0.ar.lock,
            i_M0_ARPROT       = m0.ar.prot,
            o_M0_ARREADY      = m0.ar.ready,    
            i_M0_ARSIZE       = m0.ar.size,
            i_M0_ARVALID      = m0.ar.valid,    
            i_M0_AWADDR       = m0.aw.addr,
            i_M0_AWBURST      = m0.aw.burst,    
            i_M0_AWCACHE      = m0.aw.cache,    
            i_M0_AWID         = m0.aw.id,
            i_M0_AWLEN        = m0.aw.len,
            i_M0_AWLOCK       = m0.aw.lock,
            i_M0_AWPROT       = m0.aw.prot,
            o_M0_AWREADY      = m0.aw.ready,    
            i_M0_AWSIZE       = m0.aw.size,
            i_M0_AWVALID      = m0.aw.valid,    
            o_M0_BID          = m0.b.id,
            i_M0_BREADY       = m0.b.ready,
            o_M0_BRESP        = m0.b.resp,
            o_M0_BVALID       = m0.b.valid,
            o_M0_RDATA        = m0.r.data,
            o_M0_RID          = m0.r.id,
            o_M0_RLAST        = m0.r.last,
            i_M0_RREADY       = m0.r.ready,
            o_M0_RRESP        = m0.r.resp,
            o_M0_RVALID       = m0.r.valid,
            i_M0_WDATA        = m0.w.data,
            i_M0_WLAST        = m0.w.last,
            o_M0_WREADY       = m0.w.ready,
            i_M0_WSTRB        = m0.w.strb,
            i_M0_WVALID       = m0.w.valid,
            i_M0_ACLK         = ClockSignal(clock_domain),
            o_M0_ARESETN_I    = ResetSignal(clock_domain),            )
        
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "soc_fpga_intf_axi_m0.v"))