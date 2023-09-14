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

# soc_fpga_intf_axi_s_ahb Wrapper ----------------------------------------------------------------------


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

class SOC_FPGA_INTF_AHB_S(Module):
    def __init__(self, platform, s_ahb):
        self.logger = logging.getLogger("SOC_FPGA_INTF_AHB_S")

        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # Clock Domain.
        clock_domain = s_ahb.clock_domain
        self.logger.info(f"Clock Domain     : {colorer(clock_domain)}")

        # Address width.
        address_width = len(s_ahb.aw.addr)
        self.logger.info(f"Address Width    : {colorer(address_width)}")

        # Data width.
        data_width = len(s_ahb.w.data)
        self.logger.info(f"Data Width       : {colorer(data_width)}")


        # ID width.
        id_width = len(s_ahb.aw.id)
        self.logger.info(f"ID Width         : {colorer(id_width)}")
        

        self.logger.info(f"===================================================")
        # Module instance.
        # ----------------
        self.logger.info("Creating SOC_FPGA_INTF_AHB_S module.")


        self.specials += Instance("soc_fpga_intf_axi_s_ahb",
            # Parameters.
            # -----------
            p_DATA_WIDTH      = Instance.PreformattedParam(data_width),
            p_ADDR_WIDTH      = Instance.PreformattedParam(address_width),
            p_ID_WIDTH        = Instance.PreformattedParam(id_width),                                  

            i_M1_ARADDR       = s_ahb.ar.addr, 
            i_M1_ARBURST      = s_ahb.ar.burst,    
            i_M1_ARCACHE      = s_ahb.ar.cache,    
            i_M1_ARID         = s_ahb.ar.id,
            i_M1_ARLEN        = s_ahb.ar.len,
            i_M1_ARLOCK       = s_ahb.ar.lock,
            i_M1_ARPROT       = s_ahb.ar.prot,
            o_M1_ARREADY      = s_ahb.ar.ready,    
            i_M1_ARSIZE       = s_ahb.ar.size,
            i_M1_ARVALID      = s_ahb.ar.valid,    
            i_M1_AWADDR       = s_ahb.aw.addr,
            i_M1_AWBURST      = s_ahb.aw.burst,    
            i_M1_AWCACHE      = s_ahb.aw.cache,    
            i_M1_AWID         = s_ahb.aw.id,
            i_M1_AWLEN        = s_ahb.aw.len,
            i_M1_AWLOCK       = s_ahb.aw.lock,
            i_M1_AWPROT       = s_ahb.aw.prot,
            o_M1_AWREADY      = s_ahb.aw.ready,    
            i_M1_AWSIZE       = s_ahb.aw.size,
            i_M1_AWVALID      = s_ahb.aw.valid,    
            o_M1_BID          = s_ahb.b.id,
            i_M1_BREADY       = s_ahb.b.ready,
            o_M1_BRESP        = s_ahb.b.resp,
            o_M1_BVALID       = s_ahb.b.valid,
            o_M1_RDATA        = s_ahb.r.data,
            o_M1_RID          = s_ahb.r.id,
            o_M1_RLAST        = s_ahb.r.last,
            i_M1_RREADY       = s_ahb.r.ready,
            o_M1_RRESP        = s_ahb.r.resp,
            o_M1_RVALID       = s_ahb.r.valid,
            i_M1_WDATA        = s_ahb.w.data,
            i_M1_WLAST        = s_ahb.w.last,
            o_M1_WREADY       = s_ahb.w.ready,
            i_M1_WSTRB        = s_ahb.w.strb,
            i_M1_WVALID       = s_ahb.w.valid,
            i_M1_ACLK         = ClockSignal(clock_domain),
            o_M1_ARESETN_I    = ResetSignal(clock_domain),            )
        
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "soc_fpga_intf_axi_s_ahb.v"))