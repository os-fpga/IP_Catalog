import os
import datetime
import logging

from migen import *

# SOC_FPGA_INTF_DMA Wrapper ------------------------------------------------------------------------

class SOC_FPGA_INTF_DMA(Module):
    def __init__(self, platform):
        self.logger = logging.getLogger("SOC_FPGA_INTF_DMA")
        self.logger.propagate = True

        self.logger.info("Creating SOC_FPGA_INTF_DMA module.")

        # Create input signals
        self.dma_req = Signal(4)
        self.dma_clk = Signal()
        self.dma_rst_n = Signal()

        # Create output signals
        self.dma_ack = Signal(4)

        self.specials += Instance("SOC_FPGA_INTF_DMA",
            i_DMA_REQ=self.dma_req,
            o_DMA_ACK=self.dma_ack,
            i_DMA_CLK=self.dma_clk,
            i_DMA_RST_N=self.dma_rst_n
        )

        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "soc_fpga_intf_dma.v"))

# Main -------------------------------------------------------------------------------------------

if __name__ == "__main__":
    platform = None  # Create or load your platform here
    logging.basicConfig(filename="IP.log", filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f'Log started at {timestamp}')

    soc_fpga_intf_dma = SOC_FPGA_INTF_DMA(platform)
