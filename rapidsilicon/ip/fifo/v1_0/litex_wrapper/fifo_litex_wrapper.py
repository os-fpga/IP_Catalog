#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#

import os
import logging
import math
from migen.genlib.fifo import SyncFIFOBuffered, AsyncFIFO, SyncFIFO, AsyncFIFOBuffered
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
    def __init__(self, platform, data_width, synchronous, full_threshold, empty_threshold, depth, first_word_fall_through, empty_value, full_value, BRAM):
        self.logger = logging.getLogger("FIFO")
        self.logger.propagate = False
        
        # Data Width
        self.logger.info(f"DATA_WIDTH       : {data_width}")

        # User Width
        self.logger.info(f"Synchronous      : {synchronous}")

        self.logger.info(f"FULL THRESHOLD       : {full_value}")

        # Destination Width

        self.logger.info(f"EMPTY THRESHOLD    : {empty_value}")
        
        buses = divide_n_bit_number(data_width)
        size_bram = 36864
        maximum = max(buses, key=len)
        memory = math.ceil(size_bram / len(maximum))

        instances = math.ceil(depth / memory)
        if(synchronous):
            self.counter = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
            self.wrt_ptr = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
            self.rd_ptr = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
        else:
            starting = ((2**(math.ceil(math.log2(depth)))/2) - depth/2) 
            ending = ((2**(math.ceil(math.log2(depth)))/2) + depth/2 - 1) 
            self.wrt_ptr = Signal(math.ceil(math.log2(depth)) + 2, reset=int(starting))
            self.rd_ptr = Signal(math.ceil(math.log2(depth)) + 2, reset=int(starting))

        if (not synchronous):
            self.wrt_ptr_rd_clk1 = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.wrt_ptr_rd_clk2 = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.rd_ptr_wrt_clk1 = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.rd_ptr_wrt_clk2 = Signal(math.ceil(math.log2(depth)) + 2, reset=0)

            self.gray_encoded_rdptr = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.gray_encoded_wrtptr = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.sync_rdclk_wrtptr_binary = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.sync_wrtclk_rdptr_binary = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.rd_en_flop = Signal()
            self.rd_en_flop1 = Signal()
            self.comb += ResetSignal("wrt").eq(ResetSignal("sys"))
            self.comb += ResetSignal("rd").eq(ResetSignal("sys"))
            self.empty_count = Signal(2)
            self.wrt_ptr_reg = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.rd_ptr_reg = Signal(math.ceil(math.log2(depth)) + 2, reset=0)

        self.din    = Signal(data_width)
        self.dout   = Signal(data_width)

        self.delay_full = Signal()
        self.delay_empty = Signal()

        self.rden           = Signal()
        self.wren           = Signal()
        self.empty          = Signal()  
        self.full           = Signal()   
        self.underflow      = Signal()  
        self.overflow       = Signal() 
        self.prog_full      = Signal()  
        self.prog_empty     = Signal()
        self.almost_full    = Signal()
        self.almost_empty   = Signal()
        
        # Using Block RAM
        if (BRAM):
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
                    if(synchronous):
                        if (instances == 1):
                            self.specials += Instance("FIFO",
                            # Parameters.
                            # -----------
                            # Global.
                            p_DATA_WIDTH        = C(data), 
                            p_SYNC_FIFO         = synchronous,
                            p_PROG_FULL_THRESH  = C(depth - full_value, 12),
                            p_PROG_EMPTY_THRESH = C(empty_value, 12),

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
                            o_RD_DATA       = self.dout[j:data + j],
                            o_EMPTY         = self.empty[k],
                            o_FULL          = self.full[k],
                            o_UNDERFLOW     = self.underflow_int[k],
                            o_OVERFLOW      = self.overflow_int[k],
                            o_ALMOST_EMPTY  = self.almost_empty[k],
                            o_ALMOST_FULL   = self.almost_full[k],
                            o_PROG_FULL     = self.prog_full[k],
                            o_PROG_EMPTY    = self.prog_empty[k]
                        )
                        else:
                            self.specials += Instance("FIFO",
                                # Parameters.
                                # -----------
                                # Global.
                                p_DATA_WIDTH        = C(data), 
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
                    else:
                        if (instances == 1):
                            self.specials += Instance("FIFO",
                            # Parameters.
                            # -----------
                            # Global.
                            p_DATA_WIDTH        = C(data), 
                            p_SYNC_FIFO         = synchronous,
                            p_PROG_FULL_THRESH  = C(depth - full_value, 12),
                            p_PROG_EMPTY_THRESH = C(empty_value, 12),

                            # Clk / Rst.
                            # ----------
                            i_RDCLK         = ClockSignal("rd"),
                            i_WRCLK         = ClockSignal("wrt"),
                            i_RESET         = ResetSignal(),

                            # AXI Input
                            # -----------------
                            i_WR_DATA       = self.din[j:data + j],
                            i_RDEN          = self.rden_int[k],
                            i_WREN          = self.wren_int[k],

                            # AXI Output      
                            o_RD_DATA       = self.dout[j:data + j],
                            o_EMPTY         = self.empty[k],
                            o_FULL          = self.full[k],
                            o_UNDERFLOW     = self.underflow_int[k],
                            o_OVERFLOW      = self.overflow_int[k],
                            o_ALMOST_EMPTY  = self.almost_empty[k],
                            o_ALMOST_FULL   = self.almost_full[k],
                            o_PROG_FULL     = self.prog_full[k],
                            o_PROG_EMPTY    = self.prog_empty[k]
                        )
                        else:
                            self.specials += Instance("FIFO",
                                # Parameters.
                                # -----------
                                # Global.
                                p_DATA_WIDTH        = C(data), 
                                p_SYNC_FIFO         = synchronous,
                                p_PROG_FULL_THRESH  = C(4095, 12),
                                p_PROG_EMPTY_THRESH = C(0, 12),

                                # Clk / Rst.
                                # ----------
                                i_RDCLK         = ClockSignal("rd"),
                                i_WRCLK         = ClockSignal("wrt"),
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
                if (instances > 1):
                    # Writing and Reading to FIFOs
                    if(synchronous):
                        self.comb += [
                            If(self.wren,
                               If(~self.overflow,
                                If(self.wrt_ptr < (k + 1)*memory,
                                   If(self.wrt_ptr >= (k)*memory,
                                        self.wren_int[k].eq(1)
                                        )
                                    )
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
                    else:
                        if (k == instances - 1):
                            if (k == 0):
                                self.sync.rd += [
                                If(self.rden,
                                   If(~self.empty,
                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k + 1)*memory) + int(starting - 1),
                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting),
                                                self.rden_int[k].eq(1)
                                        )
                                        .Else(
                                        self.rden_int[k].eq(0))
                                      )
                                      .Else(
                                        self.rden_int[k].eq(0)
                                        )
                                   )
                                   .Else(
                                    self.rden_int[k].eq(0)
                                    )
                                )
                                .Else(
                                self.rden_int[k].eq(0)
                                )
                                ]
                            else:
                                self.sync.rd += [
                                If(self.rden,
                                   If(~self.empty,
                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k + 1)*memory) + int(starting - 1),
                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting - 1),
                                                self.rden_int[k].eq(1)
                                        )
                                        .Else(
                                        self.rden_int[k].eq(0))
                                      )
                                      .Else(
                                        self.rden_int[k].eq(0)
                                        )
                                   )
                                   .Else(
                                    self.rden_int[k].eq(0)
                                    )
                                )
                                .Else(
                                    self.rden_int[k].eq(0)
                                    )
                            ]
                            self.sync.rd += [
                                If(self.rd_en_flop1,
                                   If(~self.underflow,
                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((k + 1)*memory) + int(starting),
                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting),
                                                self.dout.eq(self.dout_int[k])
                                        )
                                      )
                                   )
                                )
                            ]

                            self.sync.wrt += [
                                If(self.wren,
                                   If(~self.full,
                                    If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k + 1)*memory) + int(starting),
                                       If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting),
                                            self.wren_int[k].eq(1)
                                            )
                                            .Else(
                                            self.wren_int[k].eq(0)
                                            )
                                        )
                                        .Else(
                                        self.wren_int[k].eq(0)
                                        )
                                    )
                                    .Else(
                                    self.wren_int[k].eq(0)
                                    )
                                )
                                .Else(
                                self.wren_int[k].eq(0)
                                )
                            ]
                        else:
                            self.sync.wrt += [
                            If(self.wren,
                               If(~self.full,
                                If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k + 1)*memory) + int(starting),
                                   If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting),
                                        self.wren_int[k].eq(1)
                                        )
                                        .Else(
                                        self.wren_int[k].eq(0)
                                        )
                                    )
                                    .Else(
                                    self.wren_int[k].eq(0)
                                    )
                                )
                                .Else(
                                self.wren_int[k].eq(0)
                                )
                            )
                            .Else(
                            self.wren_int[k].eq(0)
                            )
                            ]
                            if (k == 0):
                                self.sync.rd += [
                                    If(self.rden,
                                       If(~self.empty,
                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k + 1)*memory) + int(starting - 1),
                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting),
                                                    self.rden_int[k].eq(1)
                                            )
                                            .Else(
                                    self.rden_int[k].eq(0))
                                          )
                                          .Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                   self.rden_int[k].eq(1)
                                                   )
                                          .Else(
                                            self.rden_int[k].eq(0)
                                            )
                                       )
                                       .Else(
                                        self.rden_int[k].eq(0)
                                        )
                                    )
                                    .Else(
                                    self.rden_int[k].eq(0)
                                    )
                                ]
                            else:
                                self.sync.rd += [
                                If(self.rden,
                                   If(~self.empty,
                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k + 1)*memory) + int(starting - 1),
                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting - 1),
                                                self.rden_int[k].eq(1)
                                        )
                                        .Else(
                                        self.rden_int[k].eq(0)
                                        )
                                      )
                                      .Else(
                                        self.rden_int[k].eq(0)
                                        )
                                   )
                                   .Else(
                                    self.rden_int[k].eq(0)
                                    )
                                )
                                .Else(
                                self.rden_int[k].eq(0)
                                )
                                ]
                            self.sync.rd += [
                                If(self.rd_en_flop1,
                                   If(~self.underflow,
                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k + 1)*memory) + int(starting),
                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting),
                                                self.dout.eq(self.dout_int[k])
                                        )
                                      )
                                   )
                                )
                            ]


                        # First Word Fall Through Implmentation
                        if (first_word_fall_through):
                            if (k == instances - 1):
                                self.sync.rd += [
                                    If(~self.rd_en_flop1,
                                       If(~self.underflow,
                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((k + 1)*memory) + int(starting),
                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting),
                                                self.dout.eq(self.dout_int[k])
                                            )
                                          )
                                       )
                                    )
                                ]
                            else:
                                self.sync.rd += [
                                    If(~self.rd_en_flop1,
                                       If(~self.underflow,
                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k + 1)*memory) + int(starting),
                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k)*memory) + int(starting),
                                                self.dout.eq(self.dout_int[k])
                                            )
                                          )
                                       )
                                    )
                                ]
            if (instances > 1):
                if (not synchronous):
                    self.sync.rd += self.rd_en_flop.eq(self.rden)
                    self.sync.rd += [
                        If(self.rden,
                           self.rd_en_flop1.eq(1)
                           ).Elif(~self.rd_en_flop,
                                  self.rd_en_flop1.eq(0)
                                  )
                    ]
                    if (not first_word_fall_through):
                        self.sync.rd += [
                                If(~self.rd_en_flop,
                                   self.dout.eq(0)
                                   )
                            ]
                    self.sync.rd += [
                        If(self.empty,
                           self.dout.eq(0)
                           )
                    ]

                # wrt_ptr and rd_ptr to check for number of entries in FIFO
                if(synchronous):
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
                           If(~self.delay_full,
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
                else:
                    self.sync.wrt += [
                        If(self.wren,
                           If(~self.full,
                                self.wrt_ptr.eq(self.wrt_ptr + 1)
                           )
                        )
                    ]
                    self.sync.rd += [
                        If(self.rd_en_flop,
                           If(~self.empty,
                                self.rd_ptr.eq(self.rd_ptr + 1)
                           )
                        )
                    ]

                    self.sync.wrt += [
                        If(self.wren,
                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                               If(~self.full,
                                    self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                                    self.wrt_ptr[math.ceil(math.log2(depth)) + 1].eq(~self.wrt_ptr[math.ceil(math.log2(depth)) + 1])
                               )
                            )
                        )
                    ]
                    self.sync.rd += [
                        If(self.rd_en_flop,
                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                               If(~self.empty,
                                self.rd_ptr[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                                self.rd_ptr[math.ceil(math.log2(depth)) + 1].eq(~self.rd_ptr[math.ceil(math.log2(depth)) + 1])
                               )
                            )
                        )
                    ]


                    # Binary to Gray Code----------------------------------------------------------
                    for i in range(0, math.ceil(math.log2(depth))):
                        self.comb += self.gray_encoded_rdptr[i].eq(self.rd_ptr[i + 1] ^ self.rd_ptr[i])
                    self.comb += self.gray_encoded_rdptr[math.ceil(math.log2(depth))].eq(self.rd_ptr[math.ceil(math.log2(depth))])
                    self.comb += self.gray_encoded_rdptr[math.ceil(math.log2(depth)) + 1].eq(self.rd_ptr[math.ceil(math.log2(depth)) + 1])
                    for i in range(0, math.ceil(math.log2(depth))):
                        self.comb += self.gray_encoded_wrtptr[i].eq(self.wrt_ptr[i + 1] ^ self.wrt_ptr[i])
                    self.comb += self.gray_encoded_wrtptr[math.ceil(math.log2(depth))].eq(self.wrt_ptr[math.ceil(math.log2(depth))])
                    self.comb += self.gray_encoded_wrtptr[math.ceil(math.log2(depth)) + 1].eq(self.wrt_ptr[math.ceil(math.log2(depth)) + 1])
                    # -----------------------------------------------------------------------------

                    # Synchronizers----------------------------------------------------------------
                    self.sync.wrt += [
                        self.rd_ptr_wrt_clk1.eq(self.gray_encoded_rdptr),
                        self.rd_ptr_wrt_clk2.eq(self.rd_ptr_wrt_clk1)
                    ]
                    self.sync.rd += [
                        self.wrt_ptr_rd_clk1.eq(self.gray_encoded_wrtptr),
                        self.wrt_ptr_rd_clk2.eq(self.wrt_ptr_rd_clk1)
                    ]
                    # -----------------------------------------------------------------------------

                    # Gray to Binary --------------------------------------------------------------
                    for i in range(0, math.ceil(math.log2(depth)) + 1):
                        expr = self.rd_ptr_wrt_clk2[i]
                        for j in range(i + 1, math.ceil(math.log2(depth)) + 1):
                            expr ^= self.rd_ptr_wrt_clk2[j]
                        self.comb += self.sync_wrtclk_rdptr_binary[i].eq(expr)
                    self.comb += self.sync_wrtclk_rdptr_binary[math.ceil(math.log2(depth)) + 1].eq(self.rd_ptr_wrt_clk2[math.ceil(math.log2(depth)) + 1])

                    for i in range(0, math.ceil(math.log2(depth)) + 1):
                        expr = self.wrt_ptr_rd_clk2[i]
                        for j in range(i + 1, math.ceil(math.log2(depth)) + 1):
                            expr ^= self.wrt_ptr_rd_clk2[j]
                        self.comb += self.sync_rdclk_wrtptr_binary[i].eq(expr)
                    self.comb += self.sync_rdclk_wrtptr_binary[math.ceil(math.log2(depth)) + 1].eq(self.wrt_ptr_rd_clk2[math.ceil(math.log2(depth)) + 1])
                    # -----------------------------------------------------------------------------

                if(synchronous):
                    # Checking if the FIFO is full
                    self.comb += [
                        If(self.counter >= depth - 1,
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
                              If(self.counter == depth - 1,
                                self.overflow.eq(1)
                              )
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
                              If(self.counter == 0,
                                self.underflow.eq(1)
                              )
                            )
                        )
                    ]

                    # Checking for Programmable Full
                    if (full_threshold):
                        self.comb += [
                            If(self.counter >= full_value - 1,
                               self.prog_full.eq(1)
                            )
                        ]

                    # Checking for Programmable Empty
                    if (empty_threshold):
                        self.comb += [
                            If(self.counter <= empty_value - 1,
                               self.prog_empty.eq(1)
                               )
                        ]
                else:
                    # Checking if the FIFO is full
                    self.comb += [
                        If((self.wrt_ptr[math.ceil(math.log2(depth)) + 1] != self.sync_wrtclk_rdptr_binary[math.ceil(math.log2(depth)) + 1]),
                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] == self.sync_wrtclk_rdptr_binary[0:math.ceil(math.log2(depth)) + 1],
                               self.full.eq(1)
                               )
                        )
                    ]

                    # Checking for Overflow in FIFO
                    self.sync.wrt += [
                        If(self.full,
                           If(self.wren,
                              self.overflow.eq(1)
                           ).Else(
                        self.overflow.eq(0)
                           )
                           ).Else(
                        self.overflow.eq(0)
                           )
                    ]

                    # Checking if the FIFO is empty
                    self.comb += [
                        If(self.rd_ptr == self.sync_rdclk_wrtptr_binary,
                           self.empty.eq(1)
                           )
                    ]
                    self.comb += [
                        If(self.empty_count <= 1,
                           self.empty.eq(1))
                    ]
                    self.sync.rd += [
                        If(self.empty_count < 2,
                           self.empty_count.eq(self.empty_count + 1))
                    ]

                    # Checking for underflow in FIFO
                    self.sync.rd += [
                        If(self.empty,
                           If(self.rden,
                              self.underflow.eq(1)
                           ).Else(
                        self.underflow.eq(0)
                           )
                           ).Else(
                        self.underflow.eq(0)
                           )
                    ]

                    # Checking for Programmable Full
                    if (full_threshold):
                        self.comb += [
                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] +  (int(ending) - (full_value + int(starting))) - self.sync_wrtclk_rdptr_binary[0:math.ceil(math.log2(depth)) + 1] < (int(ending) - (full_value + int(starting))),
                                self.prog_full.eq(1)
                            )
                        ]
                        self.comb += [
                            If(self.full,
                               self.prog_full.eq(1))
                        ]
                        self.comb += [
                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] +  (int(ending) - (full_value + int(starting))) >= int(ending),
                               self.wrt_ptr_reg[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                               If(self.wrt_ptr_reg[0:math.ceil(math.log2(depth)) + 1] == self.sync_wrtclk_rdptr_binary[0:math.ceil(math.log2(depth)) + 1],
                               self.prog_full.eq(1)
                               )
                            ).Else(
                            self.wrt_ptr_reg.eq(self.wrt_ptr)
                            )
                        ]

                    # Checking for Programmable Empty
                    if (empty_threshold):
                        self.comb += [
                            If(self.rd_ptr +  empty_value >= int(ending),
                               self.rd_ptr_reg.eq(int(starting)),
                               If(self.rd_ptr_reg == self.sync_rdclk_wrtptr_binary,
                               self.prog_empty.eq(1)
                               )
                            ).Else(
                            self.rd_ptr_reg.eq(self.rd_ptr)
                            )
                        ]
                        self.comb += [
                            If(self.rd_ptr +  empty_value - self.sync_rdclk_wrtptr_binary < empty_value,
                                self.prog_empty.eq(1)
                            )
                        ]
                        self.comb += [
                            If(self.empty,
                               self.prog_empty.eq(1)
                               )
                        ]
            else:
                self.comb += [
                    If(self.full,
                       self.wren_int[0].eq(0)
                       ).Elif(self.wren,
                              self.wren_int[0].eq(self.wren)
                              )
                ]
                self.comb += [
                    If(self.empty,
                       self.rden_int[0].eq(0)
                       ).Elif(self.rden,
                              self.rden_int[0].eq(self.rden)
                              )
                ]
                if (synchronous):
                    self.sync += [
                        If(self.full,
                           If(self.wren,
                              self.overflow.eq(1)
                              ).Else(
                                self.overflow.eq(0)
                                     )
                            ).Else(
                                self.overflow.eq(0)
                                )
                    ]
                    self.sync += [
                        If(self.empty,
                           If(self.rden,
                              self.underflow.eq(1)
                              ).Else(
                                self.underflow.eq(0)
                                     )
                            ).Else(
                                self.underflow.eq(0)
                                )
                    ]
                else:
                    self.sync.wrt += [
                        If(self.full,
                           If(self.wren,
                              self.overflow.eq(1)
                              ).Else(
                                self.overflow.eq(0)
                                     )
                            ).Else(
                                self.overflow.eq(0)
                                )
                    ]
                    self.sync.rd += [
                        If(self.empty,
                           If(self.rden,
                              self.underflow.eq(1)
                              ).Else(
                                self.underflow.eq(0)
                                     )
                            ).Else(
                                self.underflow.eq(0)
                                )
                    ]
        # Using Distributed RAM
        else:
            if (synchronous):
                self.submodules.fifo = SyncFIFO(data_width, depth, first_word_fall_through)
            else:
                self.submodules.fifo = AsyncFIFO(data_width, depth)
                self.fifo = ClockDomainsRenamer({"write": "wrt"})(self.fifo)
                self.fifo = ClockDomainsRenamer({"read": "rd"})(self.fifo)
            self.wr_en = Signal()
            self.comb += [
                If(self.wren,
                   If(~self.full,
                        self.wr_en.eq(1)
                   )
                )
            ]
            if (synchronous):
                if (not first_word_fall_through):
                    self.comb += [
                        If(self.wren,
                            self.fifo.din.eq(self.din)
                        ),
                        self.fifo.we.eq(self.wr_en),
                        self.fifo.re.eq(self.rden),
                        If(self.rden,
                            self.dout.eq(self.fifo.dout)
                        ),
                        If(self.underflow,
                           self.dout.eq(0)
                           )
                        ]
                else:
                    self.comb += [
                        If(self.wren,
                            self.fifo.din.eq(self.din)
                        ),
                        self.fifo.we.eq(self.wr_en),
                        self.fifo.re.eq(self.rden),
                        self.dout.eq(self.fifo.dout),
                        If(self.underflow,
                           self.dout.eq(0)
                           )
                        ]
                self.comb += [
                    self.full.eq(~self.fifo.writable),
                    self.empty.eq(~self.fifo.readable),
                ]
            else:
                self.sync.wrt += [
                    If(self.wren,
                       self.fifo.din.eq(self.din)
                    ),
                    self.fifo.we.eq(self.wr_en)                    
                ]
                if (not first_word_fall_through):
                    self.sync.rd += [
                        If(self.rd_en_flop,
                            self.dout.eq(self.fifo.dout)
                        ).Else(
                            self.dout.eq(0)
                        ),
                        self.fifo.re.eq(self.rden),
                        If(self.empty,
                           self.dout.eq(0)
                           )
                    ]
                else:
                    self.sync.rd += [
                        self.dout.eq(self.fifo.dout),
                        self.fifo.re.eq(self.rden),
                        If(self.empty,
                           self.dout.eq(0)
                           )
                    ]
                self.comb += self.empty.eq(~self.fifo.readable)
                self.comb += self.full.eq(~self.fifo.writable)
                self.sync.rd += [
                    If(self.rden,
                       self.rd_en_flop.eq(1)
                       ).Else(
                        self.rd_en_flop.eq(0)
                       )
                ]
            if (synchronous):
                self.sync += [
                    If(self.rden,
                       If(self.empty,
                          self.underflow.eq(1)
                        ).Else(
                            self.underflow.eq(0)
                        )
                    ).Else(
                            self.underflow.eq(0)
                        )
                ]
                # Programmable Full Flag
                if (full_threshold):
                    self.comb += [
                        If(self.fifo.level >= full_value - 1,
                           self.prog_full.eq(1)
                        )
                    ]
                # Programmable Empty Flag
                if (empty_threshold):
                    self.comb += [
                        If(self.fifo.level <= empty_value - 1,
                           self.prog_empty.eq(1)
                        )
                    ]
                self.sync += [
                    If(self.wren,
                       If(self.full,
                          self.overflow.eq(1)
                        ).Else(
                            self.overflow.eq(0)
                        )
                    ).Else(
                            self.overflow.eq(0)
                        )
                ]
            else:
                self.sync.rd += [
                    If(self.rden,
                       If(self.empty,
                          self.underflow.eq(1)
                        ).Else(
                            self.underflow.eq(0)
                        )
                    ).Else(
                            self.underflow.eq(0)
                        )
                ]
                self.sync.wrt += [
                    If(self.wren,
                       If(self.full,
                          self.overflow.eq(1)
                        ).Else(
                            self.overflow.eq(0)
                        )
                    ).Else(
                            self.overflow.eq(0)
                        )
                ]
            

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "fifo.v"))