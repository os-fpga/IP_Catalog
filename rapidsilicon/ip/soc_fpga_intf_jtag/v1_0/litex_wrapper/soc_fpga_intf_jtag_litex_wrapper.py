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

# SOC_FPGA_INTF_JTAG Wrapper -----------------------------------------------------------------------

class SOC_FPGA_INTF_JTAG(Module):
    def __init__(self, platform):
        self.logger = logging.getLogger("SOC_FPGA_INTF_JTAG")
        self.logger.propagate = True

        self.logger.info("Creating SOC_FPGA_INTF_JTAG module.")

        # Create input signals
        self.boot_jtag_tck = Signal()
        self.boot_jtag_tdo = Signal()
        self.boot_jtag_en = Signal()

        # Create output signals
        self.boot_jtag_tdi = Signal()
        self.boot_jtag_tms = Signal()
        self.boot_jtag_trstn = Signal()

        self.specials += Instance("SOC_FPGA_INTF_JTAG",
            i_BOOT_JTAG_TCK=self.boot_jtag_tck,
            o_BOOT_JTAG_TDI=self.boot_jtag_tdi,
            i_BOOT_JTAG_TDO=self.boot_jtag_tdo,
            o_BOOT_JTAG_TMS=self.boot_jtag_tms,
            o_BOOT_JTAG_TRSTN=self.boot_jtag_trstn,
            i_BOOT_JTAG_EN=self.boot_jtag_en
        )

        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "soc_fpga_intf_jtag.v"))

# Main -------------------------------------------------------------------------------------------

if __name__ == "__main__":
    platform = None  # Create or load your platform here
    logging.basicConfig(filename="IP.log", filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f'Log started at {timestamp}')

    soc_fpga_intf_jtag = SOC_FPGA_INTF_JTAG(platform)
