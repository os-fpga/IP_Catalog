#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around western digital's ahb2axi4.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# AHB_2_AXI4_BRIDGE ---------------------------------------------------------------------------------------
class AHBSRAM(Module):
    def __init__(self, platform, sram_data_width, sram_addr_width, addr_width, data_width):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("AHB_SRAM")
        
        self.logger.propagate = True

        
        self.logger.info(f"===================================================")
        
        self.haddr               = Signal(addr_width)
        self.hburst              = Signal(3)
        self.hsize               = Signal(3)
        self.htrans              = Signal(2)
        self.hwrite              = Signal(1)
        self.hwdata              = Signal(data_width)
        self.hsel                = Signal(1)
        self.hready              = Signal(1)
        self.hrdata              = Signal(data_width)
        self.hready_resp         = Signal(1)
        self.hresp               = Signal(1)

        self.sram_q0             = Signal(sram_data_width)
        self.sram_q1             = Signal(sram_data_width)
        self.sram_q2             = Signal(sram_data_width)
        self.sram_q3             = Signal(sram_data_width)
        self.sram_q4             = Signal(sram_data_width)
        self.sram_q5             = Signal(sram_data_width)
        self.sram_q6             = Signal(sram_data_width)
        self.sram_q7             = Signal(sram_data_width)
        self.sram_w_en           = Signal(1)
        self.bank0_csn           = Signal(4)
        self.bank1_csn           = Signal(4)
        self.sram_addr_out       = Signal(sram_addr_width)
        self.sram_wdata          = Signal(data_width)        
   


        
        # Module instance.
        # ----------------
        self.specials += Instance("sramc_top",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE           = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID             = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION        = Instance.PreformattedParam("IP_VERSION"),
            p_DATA_WIDTH        = Instance.PreformattedParam(data_width),
            p_ADDR_WIDTH        = Instance.PreformattedParam(addr_width),
            p_SRAM_DATA_WIDTH   = Instance.PreformattedParam(sram_data_width),
            p_SRAM_ADDR_WIDTH   = Instance.PreformattedParam(sram_addr_width),
            # Clk / Rst.
            i_hclk               = ClockSignal(),
            i_hresetn            = ResetSignal(),

            # AHB Slave Interface.
            # --------------------
            
            i_haddr            		= self.haddr,
            i_hburst            	= self.hburst,
            i_hsize            		= self.hsize,
            i_htrans           		= self.htrans,
            i_hwrite           		= self.hwrite,
            i_hwdata           		= self.hwdata, 
            i_hsel           	    = self.hsel,
            i_hready            	= self.hready,
            o_hrdata           		= self.hrdata,
            o_hready_resp           = self.hready_resp,  
            o_hresp           		= self.hresp,

            i_sram_q0               = self.sram_q0,              
            i_sram_q1               = self.sram_q1,  
            i_sram_q2               = self.sram_q2,  
            i_sram_q3               = self.sram_q3,  
            i_sram_q4               = self.sram_q4,  
            i_sram_q5               = self.sram_q5,  
            i_sram_q6               = self.sram_q6,  
            i_sram_q7               = self.sram_q7,              
            o_sram_w_en             = self.sram_w_en,
            o_bank0_csn             = self.bank0_csn,            
            o_bank1_csn             = self.bank1_csn,
            o_sram_addr_out         = self.sram_addr_out,
            o_sram_wdata            = self.sram_wdata,
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "ahb_slave_interface.sv"))
        platform.add_source(os.path.join(rtl_dir, "sram.sv"))
        platform.add_source(os.path.join(rtl_dir, "sram8x8k.sv"))
        platform.add_source(os.path.join(rtl_dir, "sramc_top.sv"))
