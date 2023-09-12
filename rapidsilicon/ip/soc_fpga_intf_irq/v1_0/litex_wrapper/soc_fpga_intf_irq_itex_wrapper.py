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

# SOC_FPGA_INTF_IRQ Wrapper ------------------------------------------------------------------------

class SOC_FPGA_INTF_IRQ(Module):
    def __init__(self, platform):
        self.logger = logging.getLogger("SOC_FPGA_INTF_IRQ")
        self.logger.propagate = True

        self.logger.info("Creating SOC_FPGA_INTF_IRQ module.")

        # Create input signals
        self.irq_src = Signal(16)
        self.irq_clk = Signal()
        self.irq_rst_n = Signal()

        # Create output signals
        self.irq_set = Signal(16)

        self.specials += Instance("SOC_FPGA_INTF_IRQ",
            i_IRQ_SRC=self.irq_src,
            o_IRQ_SET=self.irq_set,
            i_IRQ_CLK=self.irq_clk,
            i_IRQ_RST_N=self.irq_rst_n
        )

        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "soc_fpga_intf_irq.v"))

# Main -------------------------------------------------------------------------------------------

if __name__ == "__main__":
    platform = None  # Create or load your platform here
    logging.basicConfig(filename="IP.log", filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f'Log started at {timestamp}')

    soc_fpga_intf_irq = SOC_FPGA_INTF_IRQ(platform)
