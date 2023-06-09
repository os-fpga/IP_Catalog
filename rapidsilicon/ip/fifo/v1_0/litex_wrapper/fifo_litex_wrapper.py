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

def generate_nested_if_statements(signals, index, signal):
    if (index == len(signals) - 1):
        return If(signals[index], signal.eq(1))
    else:
        return If(signals[index], generate_nested_if_statements(signals, index + 1, signal))


# AXIS_SWITCH ---------------------------------------------------------------------------------------
class FIFO(Module):
    def __init__(self, platform, data_width, synchronous, full_threshold, empty_threshold, depth, first_word_fall_through):
        self.logger = logging.getLogger("FIFO")
        self.logger.propagate = False
        
        # Data Width
        self.logger.info(f"DATA_WIDTH       : {data_width}")

        # User Width
        self.logger.info(f"Synchronous      : {synchronous}")

        self.logger.info(f"FULL THRESHOLD       : {full_threshold}")

        # Destination Width

        self.logger.info(f"EMPTY THRESHOLD    : {empty_threshold}")
        buses = divide_n_bit_number(data_width)
        size_bram = 36864
        maximum = max(buses, key=len)
        memory = math.ceil(size_bram / len(maximum))

        instances = math.ceil(depth / memory)
        self.counter = Signal(math.ceil(math.log2(depth)) + 1, reset=1)

        self.wrt_ptr = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
        self.rd_ptr = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
        self.temp = Signal(bits_sign=(math.ceil(math.log2(depth)) + 2, True))
        self.temp_abs = Signal(math.ceil(math.log2(depth)) + 1)
        self.delay_full = Signal()
        self.delay_empty = Signal()

        self.din    = Signal(data_width)
        self.dout   = Signal(data_width)

        self.rden           = Signal()
        self.wren           = Signal()
        self.empty          = Signal()  
        self.full           = Signal()   
        self.underflow      = Signal()  
        self.overflow       = Signal() 
        self.prog_full      = Signal()  
        self.prog_empty     = Signal()

        self.rden_int           = Array(Signal() for _ in range(instances))
        self.wren_int           = Array(Signal() for _ in range(instances))
        self.empty_int          = Array(Signal() for _ in range(instances))
        self.full_int           = Array(Signal() for _ in range(instances))
        self.almost_empty_int   = Array(Signal() for _ in range(instances))
        self.almost_full_int    = Array(Signal() for _ in range(instances))
        self.prog_full_int      = Array(Signal() for _ in range(instances))
        self.prog_empty_int     = Array(Signal() for _ in range(instances))
        self.dout_int           = Array(Signal() for _ in range(instances))
        self.underflow_int      = Array(Signal() for _ in range(instances))
        self.overflow_int       = Array(Signal() for _ in range(instances))

        for k in range(instances):
            j = 0

            self.rden_int[k]           = Signal(name=f"rden_int_{k}")
            self.wren_int[k]           = Signal(name=f"wren_int_{k}")
            self.empty_int[k]          = Signal(name=f"empty_int_{k}")  
            self.full_int[k]           = Signal(name=f"full_int_{k}")
            self.prog_full_int[k]      = Signal(name=f"prog_full_int_{k}")  
            self.prog_empty_int[k]     = Signal(name=f"prog_empty_int_{k}")
            self.almost_empty_int[k]   = Signal(name=f"almost_empty_int_{k}")
            self.almost_full_int[k]    = Signal(name=f"almost_full_int_{k}")
            self.dout_int[k]           = Signal(data_width, name=f"dout_int_{k}")
            self.underflow_int[k]      = Signal(name=f"underflow_int_{k}")
            self.overflow_int[k]       = Signal(name=f"overflow_int_{k}")

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
                    p_DATA_WIDTH        = C(data, 6), 
                    p_SYNC_FIFO         = synchronous,
                    p_PROG_FULL_THRESH  = C(4095, 12),
                    p_PROG_EMPTY_THRESH = C(0, 12),

                    # Clk / Rst.
                    # ----------
                    i_RDCLK         = ClockSignal(),
                    i_WRCLK         = ClockSignal(),
                    i_RESET         = ResetSignal(),

                    # AXI Input
                    # -----------------
                    i_WR_DATA       = self.din[j:data + j],
                    i_RDEN          = self.rden_int[k],
                    i_WREN          = self.wren_int[k],

                    # AXI Output      
                    o_RD_DATA       = self.dout_int[k][j:data + j],
                    o_EMPTY         = self.empty_int[k],
                    o_FULL          = self.full_int[k],
                    o_UNDERFLOW     = self.underflow_int[k],
                    o_OVERFLOW      = self.overflow_int[k],
                    o_ALMOST_EMPTY  = self.almost_empty_int[k],
                    o_ALMOST_FULL   = self.almost_full_int[k],
                    o_PROG_FULL     = self.prog_full_int[k],
                    o_PROG_EMPTY    = self.prog_empty_int[k]
                )
                j = data + j

            # Writing and Reading to FIFOs
            # if (k > 0):
            self.comb += [
                If(self.wren,
                   If(~self.overflow,
                    If(self.wrt_ptr < (k + 1)*memory,
                       If(self.wrt_ptr >= (k)*memory,
                          If(~self.full_int[k],
                            self.wren_int[k].eq(1)
                          )
                        )
                    )
                    
                    #    If(self.wrt_ptr == depth,
                    #       self.wren_int[k].eq(0)
                    #       )
                    #       .Elif(
                    #         self.full_int[k - 1],
                    #         self.wren_int[k].eq(1)
                    #     )
                    )
                )
            ]

            self.comb += [
                If(self.rden,
                   If(~self.underflow,
                        If(self.rd_ptr <= (k + 1)*memory,
                          If(self.rd_ptr > (k)*memory,
                            self.rden_int[k].eq(1),
                            self.dout.eq(self.dout_int[k]
                            )
                        )
                      )
                   )
                )
            ]

            # First Word Fall Through Implmentation
            if (first_word_fall_through):
                if (k == 0):
                    self.comb += [
                        If(~self.rden,
                           If(~self.underflow,
                              If(self.rd_ptr <= (k + 1)*memory,
                                If(self.rd_ptr >= (k)*memory,
                                    self.dout.eq(self.dout_int[k])
                                )
                              )
                           )
                        )
                    ]
                else:
                    self.comb += [
                        If(~self.rden,
                           If(~self.underflow,
                              If(self.rd_ptr <= (k + 1)*memory,
                                If(self.rd_ptr > (k)*memory,
                                    self.dout.eq(self.dout_int[k])
                                )
                              )
                           )
                        )
                    ]
            # self.comb += [
            #     If(self.rden,
            #        If(~self.empty_int[k],
            #           If(self.wrt_ptr == 0,
            #              self.rden_int[k].eq(0)
            #           ).Elif(
            #                 self.empty_int[k - 1],
            #                     self.rden_int[k].eq(1),
            #                     self.dout.eq(self.dout_int[k]
            #                 )
            #             )
            #         )
            #     )
            # ]
            # else:
            #     self.comb += [
            #         If(self.wren,
            #            If(~self.full_int[k],
            #               If(self.wrt_ptr == depth,
            #                 self.wren_int[k].eq(0)
            #                 )
            #                 .Else(
            #                    self.wren_int[k].eq(1)
            #                 )
            #             )
            #         )
            #     ]
            #     self.comb += [
            #         If(self.rden,
            #            If(~self.empty_int[k],
            #               If(self.wrt_ptr == 0,
            #                  self.rden_int[k].eq(0)
            #               )
            #               .Else(
            #                     self.rden_int[k].eq(1),
            #                     self.dout.eq(self.dout_int[k]
            #                  )
            #                 )
            #             )
            #         )
            #     ]

        # wrt_ptr to check for number of entries in FIFO
        self.sync += [
            If(self.wren,
               If(~self.full,
                    self.wrt_ptr.eq(self.wrt_ptr + 1)
               )
            )
        ]
        self.sync += [
            If(self.rden,
               If(~self.empty,
                    self.rd_ptr.eq(self.rd_ptr + 1)
               )
            )
        ]
        self.sync += [
            If(self.wren,
               If(~self.full,
                  self.counter.eq(self.counter + 1)
               )
            )
        ]
        self.sync += [
            If(self.rden,
               If(~self.empty,
                  self.counter.eq(self.counter - 1)
               )
            )
        ]
            # elif(k == 0):
            #     self.sync += [
            #         If(self.wren,
            #            If(~self.full_int[k],
            #                 self.wrt_ptr.eq(self.wrt_ptr + 1)
            #            )
            #         )
            #     ]
            #     self.sync += [
            #         If(self.rden,
            #            If(~self.empty_int[k],
            #                 self.rd_ptr.eq(self.rd_ptr + 1)
            #            )
            #         )
            #     ]
            # else:
            #     self.sync += [
            #         If(self.wren,
            #            If(~self.full_int[k],
            #               If(self.full_int[k -1],
            #                 self.wrt_ptr.eq(self.wrt_ptr + 1)
            #               )
            #            )
            #         )
            #     ]
            #     self.sync += [
            #         If(self.rden,
            #            If(~self.empty_int[k],
            #               If(self.empty_int[k - 1],
            #                 self.rd_ptr.eq(self.rd_ptr + 1)
            #               )
            #            )
            #         )
            #     ]
        self.sync += [
            If(self.wren,
                If(self.wrt_ptr == depth - 1,
                   If(~self.full,
                        self.wrt_ptr.eq(0)
                   )
                )
            )
        ]
        self.sync += [
            If(self.rden,
                If(self.rd_ptr == depth,
                   If(~self.empty,
                    self.rd_ptr.eq(1)
                   )
                )
            )
        ]

        # Checking if the FIFO is full
        self.comb += [
            If(self.counter == depth,
               self.full.eq(1)
            )
        ]

        # Checking for Overflow in FIFO
        self.sync += [
            If(self.full,
               self.delay_full.eq(self.full)
               ).Else(
            self.delay_full.eq(0)
               )
        ]
        self.comb += [
            If(self.wren,
               If(self.delay_full,
                  self.overflow.eq(1)
                )
            )
        ]

            
        # Checking if the FIFO is empty
        self.comb += [
            If(self.counter == 0,
               self.empty.eq(1)
               )
        ]

        # Checking for underflow in FIFO
        self.sync += [
            If(self.empty,
               self.delay_empty.eq(self.empty)
               ).Else(
            self.delay_empty.eq(0)
               )
        ]
        self.comb += [
            If(self.rden,
               If(self.delay_empty,
                  self.underflow.eq(1)
                )
            )
        ]
        # Checking for Programmable Full
        self.comb += [
            If(self.counter >= full_threshold - 1,
               self.prog_full.eq(1)
            )
        ]

        # Checking for Programmable Empty
        self.comb += [
            If(self.counter <= empty_threshold - 1,
               self.prog_empty.eq(1)
               )
        ]
        

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "fifo.v"))