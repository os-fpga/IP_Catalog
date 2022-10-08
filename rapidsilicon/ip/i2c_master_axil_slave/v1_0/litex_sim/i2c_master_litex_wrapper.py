#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich verilog-i2c's i2c_master_axil.v

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# I2C_MASTER -------------------------------------------------------------------------------------
class I2CMASTER(Module):
    def __init__(self, platform, s_axil, default_prescale, fixed_prescale, cmd_fifo, cmd_addr_width, write_fifo, write_addr_width, read_fifo, read_addr_width):
        
        self.logger = logging.getLogger("I2C_MASTER")
        
        self.logger.propagate = False
        
        # DEFAULT_PRESCALE
        self.logger.info(f"DEFAULT_PRESCALE     : {default_prescale}")
        
        # FIXED_PRESCALE
        self.logger.info(f"FIXED_PRESCALE       : {fixed_prescale}")
        
        # CMD_FIFO
        self.logger.info(f"CMD_FIFO             : {cmd_fifo}")
        
        # CMD_FIFO_ADDR_WIDTH
        self.logger.info(f"CMD_FIFO_ADDR_WIDTH  : {cmd_addr_width}")
        
        # WRITE_FIFO
        self.logger.info(f"WRITE_FIFO           : {write_fifo}")
        
        # WRITE_FIFO_ADDR_WIDTH
        self.logger.info(f"WRITE_FIFO_ADDR_WIDTH: {write_addr_width}")
        
        # READ_FIFO
        self.logger.info(f"READ_FIFO            : {read_fifo}")
        
        # READ_FIFO_ADDR_WIDTH
        self.logger.info(f"READ_FIFO_ADDR_WIDTH : {read_addr_width}")
        
        # I2C interface
        self.i2c_scl_i  = Signal()
        self.i2c_scl_o  = Signal()
        self.i2c_scl_t  = Signal()
        self.i2c_sda_i  = Signal()
        self.i2c_sda_o  = Signal()
        self.i2c_sda_t  = Signal()
        
        # Module instance.
        # ----------------
        self.specials += Instance("i2c_master_axil",
                                                    
            # Parameters.
            # -----------
            p_DEFAULT_PRESCALE      = default_prescale,
            p_FIXED_PRESCALE        = fixed_prescale,
            p_CMD_FIFO              = cmd_fifo,
            p_CMD_FIFO_ADDR_WIDTH   = cmd_addr_width,
            p_WRITE_FIFO            = write_fifo,
            p_WRITE_FIFO_ADDR_WIDTH = write_addr_width,
            p_READ_FIFO             = read_fifo,
            p_READ_FIFO_ADDR_WIDTH  = read_addr_width,
            
            # Clk / Rst.
            # ----------
            i_clk             = ClockSignal(),
            i_rst             = ResetSignal(),
            
            # AXI-Lite Slave Interface.
            # -------------------------
            # AW.
            i_s_axil_awaddr   = s_axil.aw.addr,
            i_s_axil_awprot   = s_axil.aw.prot,
            i_s_axil_awvalid  = s_axil.aw.valid,
            o_s_axil_awready  = s_axil.aw.ready,

            # W.
            i_s_axil_wdata    = s_axil.w.data,
            i_s_axil_wstrb    = s_axil.w.strb,
            i_s_axil_wvalid   = s_axil.w.valid,
            o_s_axil_wready   = s_axil.w.ready,

            # B.
            o_s_axil_bresp    = s_axil.b.resp,
            o_s_axil_bvalid   = s_axil.b.valid,
            i_s_axil_bready   = s_axil.b.ready,

            # AR.
            i_s_axil_araddr   = s_axil.ar.addr,
            i_s_axil_arprot   = s_axil.ar.prot,
            i_s_axil_arvalid  = s_axil.ar.valid,
            o_s_axil_arready  = s_axil.ar.ready,

            # R.
            o_s_axil_rdata    = s_axil.r.data,
            o_s_axil_rresp    = s_axil.r.resp,
            o_s_axil_rvalid   = s_axil.r.valid,
            i_s_axil_rready   = s_axil.r.ready,
            
            # I2C interface
            # -------------
            i_i2c_scl_i       = self.i2c_scl_i,
            o_i2c_scl_o       = self.i2c_scl_o,
            o_i2c_scl_t       = self.i2c_scl_t,
            i_i2c_sda_i       = self.i2c_sda_i,
            o_i2c_sda_o       = self.i2c_sda_o,
            o_i2c_sda_t       = self.i2c_sda_t
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)
    
    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "i2c_master_axil.v"))