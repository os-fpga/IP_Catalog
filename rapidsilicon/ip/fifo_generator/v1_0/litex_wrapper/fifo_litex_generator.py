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
from migen.genlib.fifo import SyncFIFO, AsyncFIFOBuffered
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

# FIFO Generator ---------------------------------------------------------------------------------------
class FIFO(Module):
    def __init__(self, data_width, synchronous, full_threshold, empty_threshold, depth, first_word_fall_through, empty_value, full_value, BRAM):
        SYNCHRONOUS = {
            "SYNCHRONOUS"  :   True,
            "ASYNCHRONOUS" :   False
        }
        self.logger = logging.getLogger("FIFO")
        self.logger.propagate = False
        
        # Data Width
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        # Synchronous / Asynchronous
        self.logger.info(f"Synchronous      : {SYNCHRONOUS[synchronous]}")
        # Full and Empty Thresholds
        self.logger.info(f"FULL THRESHOLD       : {full_value}")
        self.logger.info(f"EMPTY THRESHOLD    : {empty_value}")
        # Depth
        self.logger.info(f"DEPTH    : {depth}")

        buses = divide_n_bit_number(data_width)
        size_bram = 36864
        maximum = max(buses, key=len)
        memory = 1024

        instances = math.ceil(depth / memory)
        if(SYNCHRONOUS[synchronous]):
            self.counter = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
            self.wrt_ptr = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
            self.rd_ptr = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
        else:
            starting = ((2**(math.ceil(math.log2(depth)))/2) - depth/2) 
            ending = ((2**(math.ceil(math.log2(depth)))/2) + depth/2 - 1) 
            self.wrt_ptr = Signal(math.ceil(math.log2(depth)) + 2, reset=int(starting))
            self.rd_ptr = Signal(math.ceil(math.log2(depth)) + 2, reset=int(starting))

        if (not SYNCHRONOUS[synchronous]):
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

                    if (data <= 18):
                        instance = "FIFO18KX2"
                    else:
                        instance = "FIFO36K"
                        
                    # Module Instance.
                    # ----------------
                    if(SYNCHRONOUS[synchronous]):
                        if (instances == 1):
                            if (instance == "FIFO36K"):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WIDTH        = C(data), 
                                    p_FIFO_TYPE         = synchronous,
                                    p_PROG_FULL_THRESH  = C(depth - full_value, 12),
                                    p_PROG_EMPTY_THRESH = C(empty_value, 12),

                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK        = ClockSignal(),
                                    i_WR_CLK        = ClockSignal(),
                                    i_RESET         = ResetSignal(),

                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA       = self.din[j:data + j],
                                    i_RD_EN         = self.rden_int[k],
                                    i_WR_EN         = self.wren_int[k],

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
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WIDTH1        = C(data), 
                                    p_FIFO_TYPE1         = synchronous,
                                    p_PROG_FULL_THRESH1  = C(depth - full_value, 11),
                                    p_PROG_EMPTY_THRESH1 = C(empty_value, 11),
                                    p_DATA_WIDTH2        = C(data), 
                                    p_FIFO_TYPE2         = synchronous,
                                    p_PROG_FULL_THRESH2  = C(depth - full_value, 11),
                                    p_PROG_EMPTY_THRESH2 = C(empty_value, 11),
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK1        = ClockSignal(),
                                    i_WR_CLK1        = ClockSignal(),
                                    i_RESET1         = ResetSignal(),
                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA1       = self.din[j:data + j],
                                    i_RD_EN1         = self.rden_int[k-1],
                                    i_WR_EN1         = self.wren_int[k-1],
                                    # AXI Output      
                                    o_RD_DATA1       = self.dout[j:data + j],
                                    o_EMPTY1         = self.empty[k-1],
                                    o_FULL1          = self.full[k-1],
                                    o_UNDERFLOW1     = self.underflow_int[k-1],
                                    o_OVERFLOW1      = self.overflow_int[k-1],
                                    o_ALMOST_EMPTY1  = self.almost_empty[k-1],
                                    o_ALMOST_FULL1   = self.almost_full[k-1],
                                    o_PROG_FULL1     = self.prog_full[k-1],
                                    o_PROG_EMPTY1    = self.prog_empty[k-1],
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK2        = ClockSignal(),
                                    i_WR_CLK2        = ClockSignal(),
                                    i_RESET2         = ResetSignal(),
                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA2       = self.din[j:data + j],
                                    i_RD_EN2         = self.rden_int[k],
                                    i_WR_EN2         = self.wren_int[k],
                                    # AXI Output      
                                    o_RD_DATA2       = self.dout[j:data + j],
                                    o_EMPTY2         = self.empty[k],
                                    o_FULL2          = self.full[k],
                                    o_UNDERFLOW2     = self.underflow_int[k],
                                    o_OVERFLOW2      = self.overflow_int[k],
                                    o_ALMOST_EMPTY2  = self.almost_empty[k],
                                    o_ALMOST_FULL2   = self.almost_full[k],
                                    o_PROG_FULL2     = self.prog_full[k],
                                    o_PROG_EMPTY2    = self.prog_empty[k]
                                )
                        else:
                            if (instance == "FIFO36K"):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WIDTH        = C(data), 
                                    p_FIFO_TYPE         = synchronous,
                                    p_PROG_FULL_THRESH  = C(4095, 12),
                                    p_PROG_EMPTY_THRESH = C(0, 12),

                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK        = ClockSignal(),
                                    i_WR_CLK        = ClockSignal(),
                                    i_RESET         = ResetSignal(),

                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA       = self.din[j:data + j],
                                    i_RD_EN         = self.rden_int[k],
                                    i_WR_EN         = self.wren_int[k],

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
                            elif(k % 2 == 1):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WIDTH1        = C(data), 
                                    p_FIFO_TYPE1         = synchronous,
                                    p_PROG_FULL_THRESH1  = C(3072, 11),
                                    p_PROG_EMPTY_THRESH1 = C(0, 11),
                                    p_DATA_WIDTH2        = C(data), 
                                    p_FIFO_TYPE2         = synchronous,
                                    p_PROG_FULL_THRESH2  = C(3072, 11),
                                    p_PROG_EMPTY_THRESH2 = C(0, 11),
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK1        = ClockSignal(),
                                    i_WR_CLK1        = ClockSignal(),
                                    i_RESET1         = ResetSignal(),
                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA1       = self.din[j:data + j],
                                    i_RD_EN1         = self.rden_int[k-1],
                                    i_WR_EN1         = self.wren_int[k-1],
                                    # AXI Output      
                                    o_RD_DATA1       = self.dout_int[k-1][j:data + j],
                                    o_EMPTY1         = self.empty_int[k-1],
                                    o_FULL1          = self.full_int[k-1],
                                    o_UNDERFLOW1     = self.underflow_int[k-1],
                                    o_OVERFLOW1      = self.overflow_int[k-1],
                                    o_ALMOST_EMPTY1  = self.almost_empty_int[k-1],
                                    o_ALMOST_FULL1   = self.almost_full_int[k-1],
                                    o_PROG_FULL1     = self.prog_full_int[k-1],
                                    o_PROG_EMPTY1    = self.prog_empty_int[k-1],
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK2        = ClockSignal(),
                                    i_WR_CLK2        = ClockSignal(),
                                    i_RESET2         = ResetSignal(),
                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA2       = self.din[j:data + j],
                                    i_RD_EN2         = self.rden_int[k],
                                    i_WR_EN2         = self.wren_int[k],
                                    # AXI Output      
                                    o_RD_DATA2       = self.dout_int[k][j:data + j],
                                    o_EMPTY2         = self.empty_int[k],
                                    o_FULL2          = self.full_int[k],
                                    o_UNDERFLOW2     = self.underflow_int[k],
                                    o_OVERFLOW2      = self.overflow_int[k],
                                    o_ALMOST_EMPTY2  = self.almost_empty_int[k],
                                    o_ALMOST_FULL2   = self.almost_full_int[k],
                                    o_PROG_FULL2     = self.prog_full_int[k],
                                    o_PROG_EMPTY2    = self.prog_empty_int[k]
                                )
                    else:
                        if (instances == 1):
                            if (instance == "FIFO36K"):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WIDTH        = C(data), 
                                    p_FIFO_TYPE         = synchronous,
                                    p_PROG_FULL_THRESH  = C(depth - full_value, 12),
                                    p_PROG_EMPTY_THRESH = C(empty_value, 12),

                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK        = ClockSignal("rd"),
                                    i_WR_CLK        = ClockSignal("wrt"),
                                    i_RESET         = ResetSignal(),

                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA       = self.din[j:data + j],
                                    i_RD_EN         = self.rden_int[k],
                                    i_WR_EN         = self.wren_int[k],

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
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WIDTH1        = C(data), 
                                    p_FIFO_TYPE1         = synchronous,
                                    p_PROG_FULL_THRESH1  = C(depth - full_value, 11),
                                    p_PROG_EMPTY_THRESH1 = C(empty_value, 11),
                                    p_DATA_WIDTH2        = C(data), 
                                    p_FIFO_TYPE2         = synchronous,
                                    p_PROG_FULL_THRESH2  = C(depth - full_value, 11),
                                    p_PROG_EMPTY_THRESH2 = C(empty_value, 11),
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK1        = ClockSignal(),
                                    i_WR_CLK1        = ClockSignal(),
                                    i_RESET1         = ResetSignal(),
                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA1       = self.din[j:data + j],
                                    i_RD_EN1         = self.rden_int[k-1],
                                    i_WR_EN1         = self.wren_int[k-1],
                                    # AXI Output      
                                    o_RD_DATA1       = self.dout[j:data + j],
                                    o_EMPTY1         = self.empty[k-1],
                                    o_FULL1          = self.full[k-1],
                                    o_UNDERFLOW1     = self.underflow_int[k-1],
                                    o_OVERFLOW1      = self.overflow_int[k-1],
                                    o_ALMOST_EMPTY1  = self.almost_empty[k-1],
                                    o_ALMOST_FULL1   = self.almost_full[k-1],
                                    o_PROG_FULL1     = self.prog_full[k-1],
                                    o_PROG_EMPTY1    = self.prog_empty[k-1],
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK2        = ClockSignal(),
                                    i_WR_CLK2        = ClockSignal(),
                                    i_RESET2         = ResetSignal(),
                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA2       = self.din[j:data + j],
                                    i_RD_EN2         = self.rden_int[k],
                                    i_WR_EN2         = self.wren_int[k],
                                    # AXI Output      
                                    o_RD_DATA2       = self.dout[j:data + j],
                                    o_EMPTY2         = self.empty[k],
                                    o_FULL2          = self.full[k],
                                    o_UNDERFLOW2     = self.underflow_int[k],
                                    o_OVERFLOW2      = self.overflow_int[k],
                                    o_ALMOST_EMPTY2  = self.almost_empty[k],
                                    o_ALMOST_FULL2   = self.almost_full[k],
                                    o_PROG_FULL2     = self.prog_full[k],
                                    o_PROG_EMPTY2    = self.prog_empty[k]
                                )
                        else:
                            if (instance == "FIFO36K"):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WIDTH        = C(data), 
                                    p_FIFO_TYPE         = synchronous,
                                    p_PROG_FULL_THRESH  = C(4095, 12),
                                    p_PROG_EMPTY_THRESH = C(0, 12),

                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK        = ClockSignal("rd"),
                                    i_WR_CLK        = ClockSignal("wrt"),
                                    i_RESET         = ResetSignal(),

                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA       = self.din[j:data + j],
                                    i_RD_EN         = self.rden_int[k],
                                    i_WR_EN         = self.wren_int[k],

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
                            elif(k % 2 == 1):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WIDTH1        = C(data), 
                                    p_FIFO_TYPE1         = synchronous,
                                    p_PROG_FULL_THRESH1  = C(4095, 11),
                                    p_PROG_EMPTY_THRESH1 = C(0, 11),
                                    p_DATA_WIDTH2        = C(data), 
                                    p_FIFO_TYPE2         = synchronous,
                                    p_PROG_FULL_THRESH2  = C(4095, 11),
                                    p_PROG_EMPTY_THRESH2 = C(0, 11),
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK1        = ClockSignal("rd"),
                                    i_WR_CLK1        = ClockSignal("wrt"),
                                    i_RESET1         = ResetSignal(),
                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA1       = self.din[j:data + j],
                                    i_RD_EN1         = self.rden_int[k-1],
                                    i_WR_EN1         = self.wren_int[k-1],
                                    # AXI Output      
                                    o_RD_DATA1       = self.dout_int[k-1][j:data + j],
                                    o_EMPTY1         = self.empty_int[k-1],
                                    o_FULL1          = self.full_int[k-1],
                                    o_UNDERFLOW1     = self.underflow_int[k-1],
                                    o_OVERFLOW1      = self.overflow_int[k-1],
                                    o_ALMOST_EMPTY1  = self.almost_empty_int[k-1],
                                    o_ALMOST_FULL1   = self.almost_full_int[k-1],
                                    o_PROG_FULL1     = self.prog_full_int[k-1],
                                    o_PROG_EMPTY1    = self.prog_empty_int[k-1],
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK2        = ClockSignal("rd"),
                                    i_WR_CLK2        = ClockSignal("wrt"),
                                    i_RESET2         = ResetSignal(),
                                    # AXI Input
                                    # -----------------
                                    i_WR_DATA2       = self.din[j:data + j],
                                    i_RD_EN2         = self.rden_int[k],
                                    i_WR_EN2         = self.wren_int[k],
                                    # AXI Output      
                                    o_RD_DATA2       = self.dout_int[k][j:data + j],
                                    o_EMPTY2         = self.empty_int[k],
                                    o_FULL2          = self.full_int[k],
                                    o_UNDERFLOW2     = self.underflow_int[k],
                                    o_OVERFLOW2      = self.overflow_int[k],
                                    o_ALMOST_EMPTY2  = self.almost_empty_int[k],
                                    o_ALMOST_FULL2   = self.almost_full_int[k],
                                    o_PROG_FULL2     = self.prog_full_int[k],
                                    o_PROG_EMPTY2    = self.prog_empty_int[k]
                                )
                    j = data + j
                if (instances > 1):
                    # Writing and Reading to FIFOs
                    if(SYNCHRONOUS[synchronous]):
                        self.comb += [
                            If(self.wren,
                               If(~self.overflow,
                                  If(~self.full_int[k],
                                        If(self.wrt_ptr <= (k + 1)*memory,
                                           If(self.wrt_ptr > (k)*memory,
                                                self.wren_int[k].eq(1)
                                           )
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
                if (not SYNCHRONOUS[synchronous]):
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
                if(SYNCHRONOUS[synchronous]):
                    
                    self.sync += [
                        If(self.rden,
                           If(~self.empty,
                              self.counter.eq(self.counter - 1),
                              self.underflow.eq(0),
                                If(self.rd_ptr == depth,
                                    self.rd_ptr.eq(1)
                                ).Else(
                                    self.rd_ptr.eq(self.rd_ptr + 1)
                                )
                           ).Else(
                                self.underflow.eq(1)    # Checking for Underflow
                            )
                        ).Else(
                                self.underflow.eq(0)
                            )
                    ]

                    self.sync += [
                        If(self.wren,
                           If(~self.full,
                                self.counter.eq(self.counter + 1),
                                self.overflow.eq(0),
                                If(self.wrt_ptr == depth,
                                    self.wrt_ptr.eq(1)
                               ).Else(
                                self.wrt_ptr.eq(self.wrt_ptr + 1)
                                )
                            ).Else(
                                self.overflow.eq(1) # Checking for Overflow
                            )
                        ).Else(
                                self.overflow.eq(0)
                            )
                    ]
                else:
                    self.sync.wrt += [
                        If(self.wren,
                           If(~self.full,
                                self.overflow.eq(0),
                                self.wrt_ptr.eq(self.wrt_ptr + 1),
                                 If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                    self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                                    self.wrt_ptr[math.ceil(math.log2(depth)) + 1].eq(~self.wrt_ptr[math.ceil(math.log2(depth)) + 1])
                               )
                           ).Else(
                            # Checking for Overflow
                            self.overflow.eq(1)
                           )
                        ).Else(
                            self.overflow.eq(0)
                        ),
                        # Read Pointer Synchronizers
                        self.rd_ptr_wrt_clk1.eq(self.gray_encoded_rdptr),
                        self.rd_ptr_wrt_clk2.eq(self.rd_ptr_wrt_clk1)
                    ]
                    self.sync.rd += [
                        If(self.rd_en_flop,
                           If(~self.empty,
                                self.underflow.eq(0),
                                self.rd_ptr.eq(self.rd_ptr + 1),
                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                    self.rd_ptr[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                                    self.rd_ptr[math.ceil(math.log2(depth)) + 1].eq(~self.rd_ptr[math.ceil(math.log2(depth)) + 1])
                               )
                           ).Else(
                            # Checking for Overflow
                            self.underflow.eq(1)
                           )
                        ).Else(
                            self.underflow.eq(0)
                        ),
                        # Write Pointer Synchronizers
                        self.wrt_ptr_rd_clk1.eq(self.gray_encoded_wrtptr),
                        self.wrt_ptr_rd_clk2.eq(self.wrt_ptr_rd_clk1)
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

                if(SYNCHRONOUS[synchronous]):
                    # Checking if the FIFO is full
                    self.comb += [
                        If(self.counter >= depth,
                           self.full.eq(1)
                        )
                    ]

                    # Checking if the FIFO is empty
                    self.comb += [
                        If(self.counter == 0,
                           self.empty.eq(1)
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
                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] +  empty_value >= int(ending),
                               self.rd_ptr_reg[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                               If(self.rd_ptr_reg[0:math.ceil(math.log2(depth)) + 1] == self.sync_rdclk_wrtptr_binary[0:math.ceil(math.log2(depth)) + 1],
                               self.prog_empty.eq(1)
                               )
                            ).Else(
                            self.rd_ptr_reg.eq(self.rd_ptr)
                            )
                        ]
                        self.comb += [
                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] +  empty_value - self.sync_rdclk_wrtptr_binary[0:math.ceil(math.log2(depth)) + 1] < empty_value,
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
                if (SYNCHRONOUS[synchronous]):
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
            if (SYNCHRONOUS[synchronous]):
                self.submodules.fifo = SyncFIFO(data_width, depth, first_word_fall_through)
            else:
                self.submodules.fifo = AsyncFIFOBuffered(data_width, depth)
                self.fifo = ClockDomainsRenamer({"write": "wrt"})(self.fifo)
                self.fifo = ClockDomainsRenamer({"read": "rd"})(self.fifo)
                # depth = depth + 1
            self.wr_en = Signal()
            if(SYNCHRONOUS[synchronous]):
                self.comb += [
                    If(self.wren,
                       If(~self.full,
                            self.wr_en.eq(1)
                       )
                    )
                ]
            else:
                self.sync.wrt += [
                    If(self.wren,
                       If(~self.full,
                            self.wr_en.eq(1)
                       ).Else(
                            self.wr_en.eq(0)
                       )
                    ).Else(
                            self.wr_en.eq(0)
                       )
                ]
            if (SYNCHRONOUS[synchronous]):
                if (not first_word_fall_through):
                    self.comb += [
                        If(self.wren,
                            self.fifo.din.eq(self.din)
                        ),
                        self.fifo.we.eq(self.wr_en),
                        If(self.fifo.re,
                            self.dout.eq(self.fifo.dout)
                        ),
                        If(self.underflow,
                           self.dout.eq(0)
                           )
                        ]
                    self.sync += self.fifo.re.eq(self.rden)
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
                self.sync.rd += self.rd_en_flop.eq(self.rden)
                self.comb += [
                    If(self.wren,
                        self.fifo.din.eq(self.din)
                    ),
                    self.fifo.we.eq(self.wr_en),
                ]
                self.sync.rd += [
                    self.fifo.re.eq(self.rden),
                ]
                if (first_word_fall_through):
                    self.comb += [
                        If(~self.empty,
                            self.dout.eq(self.fifo.dout)
                       )
                    ]
                else:
                    self.comb += [
                        If(self.rden,
                           If(~self.empty,
                                self.dout.eq(self.fifo.dout)
                           )
                        )
                    ]
                    
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
                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] +  empty_value >= int(ending),
                           self.rd_ptr_reg[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                           If(self.rd_ptr_reg[0:math.ceil(math.log2(depth)) + 1] == self.sync_rdclk_wrtptr_binary[0:math.ceil(math.log2(depth)) + 1],
                           self.prog_empty.eq(1)
                           )
                        ).Else(
                        self.rd_ptr_reg.eq(self.rd_ptr)
                        )
                    ]
                    self.comb += [
                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] +  empty_value - self.sync_rdclk_wrtptr_binary[0:math.ceil(math.log2(depth)) + 1] < empty_value,
                            self.prog_empty.eq(1)
                        )
                    ]
                    self.comb += [
                        If(self.empty,
                           self.prog_empty.eq(1)
                           )
                    ]
            if (SYNCHRONOUS[synchronous]):
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