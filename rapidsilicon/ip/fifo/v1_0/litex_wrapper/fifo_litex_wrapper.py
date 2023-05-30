#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXIS's axis_switch.v

import os
import logging
import math

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)


def divide_n_bit_number(number):
    # Convert the number to a binary string
    binary_string = '0' * number
    buses = []

    for i in range(0, len(binary_string), 36):
        bus = binary_string[i:i+36]
        buses.append(bus)
    
    return buses

# AXIS_SWITCH ---------------------------------------------------------------------------------------
class FIFO(Module):
    def __init__(self, platform, data_width, common_clk, sync_fifo, full_threshold, empty_threshold, depth):
        self.logger = logging.getLogger("FIFO")
        self.logger.propagate = False
        
        # Data Width
        self.logger.info(f"DATA_WIDTH       : {data_width}")

        # User Width
        self.logger.info(f"SYNC_FIFO      : {sync_fifo}")

        self.logger.info(f"FULL THRESHOLD       : {full_threshold}")

        # Destination Width

        self.logger.info(f"EMPTY THRESHOLD    : {empty_threshold}")
        buses = divide_n_bit_number(data_width)
        size_bram = 36864
        maximum = max(buses, key=len)
        memory = math.ceil(size_bram / len(maximum))

        instances = math.ceil(depth / memory)

        self.din    = Signal(data_width)
        self.dout   = Signal(data_width)

        self.rden           = Signal()
        self.wren           = Signal()
        self.empty          = Signal()  
        self.full           = Signal()   
        self.underflow      = Signal()  
        self.overflow       = Signal()   
        self.almost_empty   = Signal()   
        self.almost_full    = Signal()    
        self.prog_full      = Signal()  
        self.prog_empty     = Signal()

        self.rden1          = Array(Signal() for _ in range(instances))
        self.wren1          = Array(Signal() for _ in range(instances))
        self.empty1         = Array(Signal() for _ in range(instances))
        self.full1          = Array(Signal() for _ in range(instances))
        self.underflow1     = Array(Signal() for _ in range(instances))
        self.overflow1      = Array(Signal() for _ in range(instances))
        self.almost_empty1  = Array(Signal() for _ in range(instances))
        self.almost_full1   = Array(Signal() for _ in range(instances))
        self.prog_full1     = Array(Signal() for _ in range(instances))
        self.prog_empty1    = Array(Signal() for _ in range(instances))
        self.dout1          = Array(Signal() for _ in range(instances))

        for k in range(instances):
            j = 0

            self.rden1[k]           = Signal(name=f"rden1_{k}")
            self.wren1[k]           = Signal(name=f"wren1_{k}")
            self.empty1[k]          = Signal(name=f"empty1_{k}")  
            self.full1[k]           = Signal(name=f"full1_{k}")   
            self.underflow1[k]      = Signal(name=f"underflow1_{k}")  
            self.overflow1[k]       = Signal(name=f"overflow1_{k}")   
            self.almost_empty1[k]   = Signal(name=f"almost_empty1_{k}")   
            self.almost_full1[k]    = Signal(name=f"almost_full1_{k}")    
            self.prog_full1[k]      = Signal(name=f"prog_full1_{k}")  
            self.prog_empty1[k]     = Signal(name=f"prog_empty1_{k}")
            self.dout1[k]           = Signal(data_width, name=f"dout1_{k}")

            for i, bus in enumerate(buses):
                if (len(bus) <= 2):
                    data = len(bus)
                elif (len(bus) <= 4):
                    data = 4
                elif (len(bus) <= 9):
                    data = 9
                elif (len(bus) <= 18):
                    data = 18
                elif (len(bus) <= 36):
                    data = 36
                 
                # Module Instance.
                # ----------------
                self.specials += Instance("FIFO",
                    # Parameters.
                    # -----------
                    # Global.
                    p_DATA_WIDTH        = Instance.PreformattedParam(data), 
                    p_SYNC_FIFO         = sync_fifo,
                    p_PROG_FULL_THRESH  = C(full_threshold, 12),
                    p_PROG_EMPTY_THRESH = C(empty_threshold, 12),

                    # Clk / Rst.
                    # ----------
                    i_RDCLK         = ClockSignal(),
                    i_WRCLK         = ClockSignal(),
                    i_RESET         = ResetSignal(),

                    # AXI Input
                    # -----------------
                    i_WR_DATA       = self.din[j:data + j],
                    i_RDEN          = self.rden1[k],
                    i_WREN          = self.wren1[k],

                    # AXI Output      
                    o_RD_DATA       = self.dout1[k][j:data + j],
                    o_EMPTY         = self.empty1[k],
                    o_FULL          = self.full1[k],
                    o_UNDERFLOW     = self.underflow1[k],
                    o_OVERFLOW      = self.overflow1[k],
                    o_ALMOST_EMPTY  = self.almost_empty1[k],
                    o_ALMOST_FULL   = self.almost_full1[k],
                    o_PROG_FULL     = self.prog_full1[k],
                    o_PROG_EMPTY    = self.prog_empty1[k]
                )
                j = data + j

        # Writing and Reading to FIFOs
            if (k > 0):
                self.comb += [
                    If(self.wren,
                        If(~self.full1[k],
                            If(self.full1[k - 1],
                                self.wren1[k].eq(1)
                            )
                        )
                    )
                ]
                self.comb += [
                    If(self.rden,
                       If(~self.empty1[k],
                          If(self.empty1[k - 1],
                             self.rden1[k].eq(1),
                             self.dout.eq(self.dout1[k]
                                )
                            )
                        )
                    )
                ]
            else:
                self.comb += [
                    If(self.wren,
                       If(~self.full1[k],
                            self.wren1[k].eq(1)
                        )
                    )
                ]
                self.comb += [
                    If(self.rden,
                       If(~self.empty1[k],
                          self.rden1[k].eq(1),
                             self.dout.eq(self.dout1[k]
                            )
                       )
                    )
                ]

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "fifo.v"))