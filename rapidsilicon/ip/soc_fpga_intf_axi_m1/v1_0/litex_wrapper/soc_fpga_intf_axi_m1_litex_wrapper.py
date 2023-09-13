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

# soc_fpga_intf_axi_m1 Wrapper ----------------------------------------------------------------------


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

class SOC_FPGA_INTF_AXI_M1(Module):
    def __init__(self, platform, m1):
        self.logger = logging.getLogger("SOC_FPGA_INTF_AXI_M1")

        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # Clock Domain.
        clock_domain = m1.clock_domain
        self.logger.info(f"Clock Domain     : {colorer(clock_domain)}")

        # Address width.
        address_width = len(m1.aw.addr)
        self.logger.info(f"Address Width    : {colorer(address_width)}")

        # Data width.
        data_width = len(m1.w.data)
        self.logger.info(f"Data Width       : {colorer(data_width)}")


        # ID width.
        id_width = len(m1.aw.id)
        self.logger.info(f"ID Width         : {colorer(id_width)}")
        

        self.logger.info(f"===================================================")
        # Module instance.
        # ----------------
        self.logger.info("Creating SOC_FPGA_INTF_AXI_M1 module.")


        self.specials += Instance("soc_fpga_intf_axi_m1",
            # Parameters.
            # -----------
            p_DATA_WIDTH      = Instance.PreformattedParam(data_width),
            p_ADDR_WIDTH      = Instance.PreformattedParam(address_width),
            p_ID_WIDTH        = Instance.PreformattedParam(id_width),                                  

            i_M1_ARADDR       = m1.ar.addr, 
            i_M1_ARBURST      = m1.ar.burst,    
            i_M1_ARCACHE      = m1.ar.cache,    
            i_M1_ARID         = m1.ar.id,
            i_M1_ARLEN        = m1.ar.len,
            i_M1_ARLOCK       = m1.ar.lock,
            i_M1_ARPROT       = m1.ar.prot,
            o_M1_ARREADY      = m1.ar.ready,    
            i_M1_ARSIZE       = m1.ar.size,
            i_M1_ARVALID      = m1.ar.valid,    
            i_M1_AWADDR       = m1.aw.addr,
            i_M1_AWBURST      = m1.aw.burst,    
            i_M1_AWCACHE      = m1.aw.cache,    
            i_M1_AWID         = m1.aw.id,
            i_M1_AWLEN        = m1.aw.len,
            i_M1_AWLOCK       = m1.aw.lock,
            i_M1_AWPROT       = m1.aw.prot,
            o_M1_AWREADY      = m1.aw.ready,    
            i_M1_AWSIZE       = m1.aw.size,
            i_M1_AWVALID      = m1.aw.valid,    
            o_M1_BID          = m1.b.id,
            i_M1_BREADY       = m1.b.ready,
            o_M1_BRESP        = m1.b.resp,
            o_M1_BVALID       = m1.b.valid,
            o_M1_RDATA        = m1.r.data,
            o_M1_RID          = m1.r.id,
            o_M1_RLAST        = m1.r.last,
            i_M1_RREADY       = m1.r.ready,
            o_M1_RRESP        = m1.r.resp,
            o_M1_RVALID       = m1.r.valid,
            i_M1_WDATA        = m1.w.data,
            i_M1_WLAST        = m1.w.last,
            o_M1_WREADY       = m1.w.ready,
            i_M1_WSTRB        = m1.w.strb,
            i_M1_WVALID       = m1.w.valid,
            i_M1_ACLK         = ClockSignal(clock_domain),
            o_M1_ARESETN_I    = ResetSignal(clock_domain),            )
        
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "soc_fpga_intf_axi_m1.v"))