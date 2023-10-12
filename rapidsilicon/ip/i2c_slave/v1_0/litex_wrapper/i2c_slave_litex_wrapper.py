#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich verilog-i2c's i2c_slave_axil_master.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# I2C_SLAVE  -------------------------------------------------------------------------------------
class I2CSLAVE(Module):
    def __init__(self, platform, m_axil, filter_len):
        
        self.logger = logging.getLogger("I2C_SLAVE")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # DATA_WIDTH
        data_width = len(m_axil.w.data)
        self.logger.info(f"DATA_WIDTH     : {data_width}")
        
        # ADDRESS_WIDTH
        addr_width = len(m_axil.aw.addr)
        self.logger.info(f"ADDRESS_WIDTH  : {addr_width}")
        
        # FILTER_LENGTH
        self.logger.info(f"FILTER_LENGTH  : {filter_len}")
        
        self.logger.info(f"===================================================")
        
        # I2C interface
        self.i2c_scl_i        = Signal()
        self.i2c_scl_o        = Signal()
        self.i2c_scl_t        = Signal()
        self.i2c_sda_i        = Signal()
        self.i2c_sda_o        = Signal()
        self.i2c_sda_t        = Signal()
        
        # Status
        self.busy             = Signal()
        self.bus_addressed    = Signal()
        self.bus_active       = Signal()
        
        # Configuration
        self.enable           = Signal()
        self.device_address   = Signal(7)
        
        # Module instance.
        # ----------------
        self.specials += Instance("i2c_slave_axil_master",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE         = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID           = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION      = Instance.PreformattedParam("IP_VERSION"),
            p_DATA_WIDTH      = Instance.PreformattedParam(data_width),
            p_ADDR_WIDTH      = Instance.PreformattedParam(addr_width),
            p_FILTER_LEN      = Instance.PreformattedParam(filter_len),
            
            # Clk / Rst.
            # ----------
            i_clk             = ClockSignal(),
            i_rst             = ResetSignal(),
            
            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            o_m_axil_awaddr   = m_axil.aw.addr,
            o_m_axil_awprot   = m_axil.aw.prot,
            o_m_axil_awvalid  = m_axil.aw.valid,
            i_m_axil_awready  = m_axil.aw.ready,

            # W.
            o_m_axil_wdata    = m_axil.w.data,
            o_m_axil_wstrb    = m_axil.w.strb,
            o_m_axil_wvalid   = m_axil.w.valid,
            i_m_axil_wready   = m_axil.w.ready,

            # B.
            i_m_axil_bresp    = m_axil.b.resp,
            i_m_axil_bvalid   = m_axil.b.valid,
            o_m_axil_bready   = m_axil.b.ready,

            # AR.
            o_m_axil_araddr   = m_axil.ar.addr,
            o_m_axil_arprot   = m_axil.ar.prot,
            o_m_axil_arvalid  = m_axil.ar.valid,
            i_m_axil_arready  = m_axil.ar.ready,

            # R.
            i_m_axil_rdata    = m_axil.r.data,
            i_m_axil_rresp    = m_axil.r.resp,
            i_m_axil_rvalid   = m_axil.r.valid,
            o_m_axil_rready   = m_axil.r.ready,
            
            # I2C interface
            # -------------
            i_i2c_scl_i       = self.i2c_scl_i,
            o_i2c_scl_o       = self.i2c_scl_o,
            o_i2c_scl_t       = self.i2c_scl_t,
            i_i2c_sda_i       = self.i2c_sda_i,
            o_i2c_sda_o       = self.i2c_sda_o,
            o_i2c_sda_t       = self.i2c_sda_t,
            
            # Status
            # ------
            o_busy            = self.busy,
            o_bus_addressed   = self.bus_addressed,
            o_bus_active      = self.bus_active,
            
            # Configuration
            # -------------
            i_enable          = self.enable,
            i_device_address  = self.device_address
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)
    
    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "i2c_slave_axil_master.v"))