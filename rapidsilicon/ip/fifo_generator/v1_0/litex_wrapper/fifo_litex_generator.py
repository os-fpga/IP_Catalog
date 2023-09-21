#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#

import datetime
import logging
import math
from migen.genlib.fifo import SyncFIFO, AsyncFIFOBuffered
from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

def divide_n_bit_number(number, depth):
    # Convert the number to a binary string
    binary_string = '0' * number
    buses = []

    for i in range(0, len(binary_string), 36):
        bus = binary_string[i:i+36]
        buses.append(bus)
    if (len(buses[-1]) < 36 and len(buses[-1]) > 18 and depth > 1024):
        for i in range(len(binary_string) - len(buses[-1]), len(binary_string), 18):
            bus = binary_string[i:i+18]
            buses.append(bus)
        buses.pop(-3)
    
    return buses


# FIFO Generator ---------------------------------------------------------------------------------------
class FIFO(Module):
    def __init__(self, data_width, synchronous, full_threshold, empty_threshold, depth, first_word_fall_through, empty_value, full_value, BRAM):
        SYNCHRONOUS = {
            "SYNCHRONOUS"  :   True,
            "ASYNCHRONOUS" :   False
        }
        self.logger = logging.getLogger("FIFO")
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Data Width
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        # Synchronous / Asynchronous
        self.logger.info(f"SYNCHRONOUS      : {SYNCHRONOUS[synchronous]}")
        # Full and Empty Thresholds
        self.logger.info(f"FULL THRESHOLD     : {full_value}")
        self.logger.info(f"EMPTY THRESHOLD    : {empty_value}")
        # Depth
        self.logger.info(f"DEPTH    : {depth}")
        self.logger.info(f"===================================================")

        buses = divide_n_bit_number(data_width, depth)
        size_bram = 36864
        data_36 = sum(1 for item in buses if ((len(item) >= 18 and depth < 1024) or (len(item) == 36 and depth >= 1024)))
        total_mem = math.ceil((data_width * depth) / size_bram)
        remaining_memory = 0
        depth_mem = 18432
        num_9K = 0
        num_18K = 0
        num_36K = 0
        while remaining_memory < data_width * depth:
            for i, bus in enumerate(buses):
                # if (remaining_memory < data_width * depth):
                    if (len(bus) <= 9):
                        data = 9
                        memory = 1024
                        remaining_memory = remaining_memory + (len(bus) * memory)
                        num_9K = num_9K + 1
                    elif (len(bus) <= 18):
                        data = 18
                        memory = 1024
                        num_18K = num_18K + 1
                        remaining_memory = remaining_memory + (len(bus) * memory)
                    elif (len(bus) <= 36):
                        data = 36
                        memory = 1024
                        num_36K = num_36K + 1
                        remaining_memory = remaining_memory + (len(bus) * memory)
        total_mem = num_36K + math.ceil(num_18K/2) + math.ceil(num_9K/4)
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
            self.rden_int           = Array(Signal() for _ in range(total_mem * 2))
            self.wren_int           = Array(Signal() for _ in range(total_mem * 2))
            self.empty_int          = Array(Signal() for _ in range(total_mem * 2))
            self.full_int           = Array(Signal() for _ in range(total_mem * 2))
            self.almost_empty_int   = Array(Signal() for _ in range(total_mem * 2))
            self.almost_full_int    = Array(Signal() for _ in range(total_mem * 2))
            self.prog_full_int      = Array(Signal() for _ in range(total_mem * 2))
            self.prog_empty_int     = Array(Signal() for _ in range(total_mem * 2))
            self.dout_int           = Array(Signal() for _ in range(total_mem * 2))
            self.underflow_int      = Array(Signal() for _ in range(total_mem * 2))
            self.overflow_int       = Array(Signal() for _ in range(total_mem * 2))
            count = 0
            mem = 0
            k36_flag = 0
            index_array = []
            k_loop = 0
            count18K = 0
            old_count18K = 0
            old_count9K = 0
            two_block = 0
            count9K = 0
            count_36K = 0
            k9_flag = 0
            k18_flag = 0
            for k in range(total_mem * 2):
                self.rden_int[k]           = Signal(name=f"rden_int_{k}")
                self.wren_int[k]           = Signal(name=f"wren_int_{k}")
                self.empty_int[k]          = Signal(name=f"empty_int_{k}")  
                self.full_int[k]           = Signal(name=f"full_int_{k}")
                self.prog_full_int[k]      = Signal(name=f"prog_full_int_{k}")  
                self.prog_empty_int[k]     = Signal(name=f"prog_empty_int_{k}")
                self.almost_empty_int[k]   = Signal(name=f"almost_empty_int_{k}")
                self.almost_full_int[k]    = Signal(name=f"almost_full_int_{k}")
                self.dout_int[k]           = Signal(36, name=f"dout_int_{k}")
                self.underflow_int[k]      = Signal(name=f"underflow_int_{k}")
                self.overflow_int[k]       = Signal(name=f"overflow_int_{k}")

            for k in range(total_mem):
                j = 0
                for i, bus in enumerate(buses):
                    if (len(bus) <= 9):
                        data = 9
                        memory = 2048
                        k9_flag = 1
                    elif (len(bus) <= 18):
                        data = 18
                        memory = 1024
                        k18_flag = 1
                    elif (len(bus) <= 36):
                        data = 36
                        memory = 1024
                        k36_flag = 1
                    
                    if (data <= 18):
                        instance = "FIFO18KX2"
                    else:
                        instance = "FIFO36K"
                    # Module Instance.
                    # ----------------
                    if(SYNCHRONOUS[synchronous]):
                        if (total_mem == 1):
                            if (instance == "FIFO36K"):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WRITE_WIDTH  = C(data), 
                                    p_DATA_READ_WIDTH   = C(data),
                                    p_FIFO_TYPE         = synchronous,
                                    p_PROG_FULL_THRESH  = C(depth - full_value, 12),
                                    p_PROG_EMPTY_THRESH = C(empty_value, 12),

                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK        = ClockSignal(),
                                    i_WR_CLK        = ClockSignal(),
                                    i_RESET         = ResetSignal(),

                                    # Input
                                    # -----------------
                                    i_WR_DATA       = self.din[j:data + j],
                                    i_RD_EN         = self.rden_int[count],
                                    i_WR_EN         = self.wren_int[count],

                                    # Output      
                                    o_RD_DATA       = self.dout[j:data + j],
                                    o_EMPTY         = self.empty[count],
                                    o_FULL          = self.full[count],
                                    o_UNDERFLOW     = self.underflow_int[count],
                                    o_OVERFLOW      = self.overflow_int[count],
                                    o_ALMOST_EMPTY  = self.almost_empty[count],
                                    o_ALMOST_FULL   = self.almost_full[count],
                                    o_PROG_FULL     = self.prog_full[count],
                                    o_PROG_EMPTY    = self.prog_empty[count]
                                )
                                count = count + 1
                            else:
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WRITE_WIDTH1  = C(data),
                                    p_DATA_READ_WIDTH1   = C(data),
                                    p_FIFO_TYPE1         = synchronous,
                                    p_PROG_FULL_THRESH1  = C(depth - full_value, 12),
                                    p_PROG_EMPTY_THRESH1 = C(empty_value, 12),
                                    p_DATA_WRITE_WIDTH2  = C(data),
                                    p_DATA_READ_WIDTH2   = C(data), 
                                    p_FIFO_TYPE2         = synchronous,
                                    p_PROG_FULL_THRESH2  = C(depth - full_value, 11),
                                    p_PROG_EMPTY_THRESH2 = C(empty_value, 11),
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK1        = ClockSignal(),
                                    i_WR_CLK1        = ClockSignal(),
                                    i_RESET1         = ResetSignal(),
                                    # Input
                                    # -----------------                                    # -----------------
                                    i_WR_DATA1       = self.din[j:data + j],
                                    i_RD_EN1         = self.rden_int[count],
                                    i_WR_EN1         = self.wren_int[count],
                                    # Output      
                                    o_RD_DATA1       = self.dout_int[count][j:data + j],
                                    o_EMPTY1         = self.empty_int[count],
                                    o_FULL1          = self.full_int[count],
                                    o_UNDERFLOW1     = self.underflow_int[count],
                                    o_OVERFLOW1      = self.overflow_int[count],
                                    o_ALMOST_EMPTY1  = self.almost_empty_int[count],
                                    o_ALMOST_FULL1   = self.almost_full_int[count],
                                    o_PROG_FULL1     = self.prog_full_int[count],
                                    o_PROG_EMPTY1    = self.prog_empty_int[count],
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK2        = ClockSignal(),
                                    i_WR_CLK2        = ClockSignal(),
                                    i_RESET2         = ResetSignal(),
                                    # Input
                                    # -----------------
                                    i_WR_DATA2       = self.din[j:data + j],
                                    i_RD_EN2         = self.rden_int[count + 1],
                                    i_WR_EN2         = self.wren_int[count + 1],
                                    # Output      
                                    o_RD_DATA2       = self.dout_int[count + 1][j:data + j],
                                    o_EMPTY2         = self.empty_int[count + 1],
                                    o_FULL2          = self.full_int[count + 1],
                                    o_UNDERFLOW2     = self.underflow_int[count + 1],
                                    o_OVERFLOW2      = self.overflow_int[count + 1],
                                    o_ALMOST_EMPTY2  = self.almost_empty_int[count + 1],
                                    o_ALMOST_FULL2   = self.almost_full_int[count + 1],
                                    o_PROG_FULL2     = self.prog_full_int[count + 1],
                                    o_PROG_EMPTY2    = self.prog_empty_int[count + 1]
                                )
                                for l in range (2):
                                    if (count + l < num_36K + (num_18K/2)*2 + (num_9K/4)*2):
                                        self.comb += [
                                            If(self.wren,
                                               If(~self.overflow,
                                                  If(~self.full_int[count + l],
                                                        If(self.wrt_ptr <= (count + l + 1)*memory,
                                                           If(self.wrt_ptr > (count + l)*memory,
                                                                self.wren_int[count + l].eq(1)
                                                            )
                                                        )
                                                    )
                                                )
                                            )
                                        ]
                                        self.comb += [
                                            If(self.rden,
                                               If(~self.underflow,
                                                    If(self.rd_ptr <= (count + l + 1)*memory,
                                                      If(self.rd_ptr > (count + l)*memory,
                                                        self.rden_int[count + l].eq(1),
                                                        self.dout[j:data + j].eq(self.dout_int[count + l]
                                                            )
                                                        )
                                                    )
                                                )
                                            )
                                        ]
                                        if (first_word_fall_through):
                                            self.comb += [
                                                If(~self.rden,
                                                    If(~self.underflow,
                                                        If(self.rd_ptr <= (count + l + 1)*memory,
                                                            If(self.rd_ptr >= (count + l)*memory,
                                                                self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                )
                                                            )
                                                        )
                                                    )
                                                )
                                            ]
                                count = count + 2
                        else:
                            if (instance == "FIFO36K" and count_36K < num_36K):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WRITE_WIDTH  = C(data), 
                                    p_DATA_READ_WIDTH   = C(data), 
                                    p_FIFO_TYPE         = synchronous,
                                    p_PROG_FULL_THRESH  = C(4095, 12),
                                    p_PROG_EMPTY_THRESH = C(0, 12),

                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK        = ClockSignal(),
                                    i_WR_CLK        = ClockSignal(),
                                    i_RESET         = ResetSignal(),

                                    # Input
                                    # -----------------
                                    i_WR_DATA       = self.din[j:data + j],
                                    i_RD_EN         = self.rden_int[count],
                                    i_WR_EN         = self.wren_int[count],

                                    # Output      
                                    o_RD_DATA       = self.dout_int[count],
                                    o_EMPTY         = self.empty_int[count],
                                    o_FULL          = self.full_int[count],
                                    o_UNDERFLOW     = self.underflow_int[count],
                                    o_OVERFLOW      = self.overflow_int[count],
                                    o_ALMOST_EMPTY  = self.almost_empty_int[count],
                                    o_ALMOST_FULL   = self.almost_full_int[count],
                                    o_PROG_FULL     = self.prog_full_int[count],
                                    o_PROG_EMPTY    = self.prog_empty_int[count]
                                )
                                count_36K = count_36K + 1
                                count = count + 1
                                mem = mem + 1
                            elif(instance == "FIFO18KX2" and mem < total_mem and ((((k % (instances/(instances/2)) == 1 and data == 18 and count18K < (num_18K/2)) or (k + 2 == total_mem) or (k % (instances/(instances/4)) == 1 and data == 9 and count9K < (num_9K/4)) or (not k36_flag and data == 9 and count9K < num_9K/4) or (not k36_flag and data == 18 and count18K < num_18K/2))))):
                                index_array.append(count)
                                index_array.append(count + 1)
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WRITE_WIDTH1  = C(data),
                                    p_DATA_READ_WIDTH1   = C(data), 
                                    p_FIFO_TYPE1         = synchronous,
                                    p_PROG_FULL_THRESH1  = C(full_value, 12),
                                    p_PROG_EMPTY_THRESH1 = C(empty_value, 12),
                                    p_DATA_WRITE_WIDTH2  = C(data),
                                    p_DATA_READ_WIDTH2   = C(data), 
                                    p_FIFO_TYPE2         = synchronous,
                                    p_PROG_FULL_THRESH2  = C(full_value, 11),
                                    p_PROG_EMPTY_THRESH2 = C(empty_value, 11),
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK1        = ClockSignal(),
                                    i_WR_CLK1        = ClockSignal(),
                                    i_RESET1         = ResetSignal(),
                                    # Input
                                    # -----------------
                                    i_WR_DATA1       = self.din[j:data + j],
                                    i_RD_EN1         = self.rden_int[count],
                                    i_WR_EN1         = self.wren_int[count],
                                    # Output   
                                    # -----------------
                                    o_RD_DATA1       = self.dout_int[count],
                                    o_EMPTY1         = self.empty_int[count],
                                    o_FULL1          = self.full_int[count],
                                    o_UNDERFLOW1     = self.underflow_int[count],
                                    o_OVERFLOW1      = self.overflow_int[count],
                                    o_ALMOST_EMPTY1  = self.almost_empty_int[count],
                                    o_ALMOST_FULL1   = self.almost_full_int[count],
                                    o_PROG_FULL1     = self.prog_full_int[count],
                                    o_PROG_EMPTY1    = self.prog_empty_int[count],
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK2        = ClockSignal(),
                                    i_WR_CLK2        = ClockSignal(),
                                    i_RESET2         = ResetSignal(),
                                    # Input
                                    # -----------------
                                    i_WR_DATA2       = self.din[j:data + j],
                                    i_RD_EN2         = self.rden_int[count + 1],
                                    i_WR_EN2         = self.wren_int[count + 1],
                                    # Output 
                                    # -----------------  
                                    o_RD_DATA2       = self.dout_int[count + 1],
                                    o_EMPTY2         = self.empty_int[count + 1],
                                    o_FULL2          = self.full_int[count + 1],
                                    o_UNDERFLOW2     = self.underflow_int[count + 1],
                                    o_OVERFLOW2      = self.overflow_int[count + 1],
                                    o_ALMOST_EMPTY2  = self.almost_empty_int[count + 1],
                                    o_ALMOST_FULL2   = self.almost_full_int[count + 1],
                                    o_PROG_FULL2     = self.prog_full_int[count + 1],
                                    o_PROG_EMPTY2    = self.prog_empty_int[count + 1]
                                )
                                for l in range (2):
                                    if (count + l < num_36K + (num_18K/2)*2 + (num_9K/4)*2):
                                        if (data == 9):
                                            if (k18_flag):
                                                self.comb += [
                                                    If(self.wren,
                                                       If(~self.overflow,
                                                          If(~self.full_int[count + l],
                                                                If(self.wrt_ptr <= (k_loop + 1 + l + two_block )*memory,
                                                                   If(self.wrt_ptr > (k_loop + l + two_block)*memory,
                                                                        self.wren_int[count + l].eq(1)
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                            else:
                                                self.comb += [
                                                    If(self.wren,
                                                       If(~self.overflow,
                                                          If(~self.full_int[count + l],
                                                                If(self.wrt_ptr <= (k_loop + 1 + l + two_block + count9K)*memory,
                                                                   If(self.wrt_ptr > (k_loop + l + two_block + count9K)*memory,
                                                                        self.wren_int[count + l].eq(1)
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                        else:
                                            if (k9_flag):
                                                self.comb += [
                                                    If(self.wren,
                                                       If(~self.overflow,
                                                          If(~self.full_int[count + l],
                                                                If(self.wrt_ptr <= (k_loop + 1 + l + count18K + count9K)*memory,
                                                                   If(self.wrt_ptr > (k_loop + l + count18K + count9K)*memory,
                                                                        self.wren_int[count + l].eq(1)
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                            else:
                                                self.comb += [
                                                    If(self.wren,
                                                       If(~self.overflow,
                                                          If(~self.full_int[count + l],
                                                                If(self.wrt_ptr <= (k_loop + 1 + l + count18K)*memory,
                                                                   If(self.wrt_ptr > (k_loop + l + count18K)*memory,
                                                                        self.wren_int[count + l].eq(1)
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                        if (data == 9):
                                            if (k18_flag):
                                                self.comb += [
                                                    If(self.rden,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr <= (k_loop + 1 + l + two_block)*memory,
                                                              If(self.rd_ptr > (k_loop + l + two_block)*memory,
                                                                    self.rden_int[count + l].eq(1),
                                                                    self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                            else:
                                                self.comb += [
                                                    If(self.rden,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr <= (k_loop + 1 + l + two_block + count9K)*memory,
                                                              If(self.rd_ptr > (k_loop + l + two_block + count9K)*memory,
                                                                    self.rden_int[count + l].eq(1),
                                                                    self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                        else:
                                            if (k9_flag):
                                                self.comb += [
                                                    If(self.rden,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr <= (k_loop + 1 + l + count18K + count9K)*memory,
                                                              If(self.rd_ptr > (k_loop + l + count18K + count9K)*memory,
                                                                    self.rden_int[count + l].eq(1),
                                                                    self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                            else:
                                                self.comb += [
                                                    If(self.rden,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr <= (k_loop + 1 + l + count18K)*memory,
                                                              If(self.rd_ptr > (k_loop + l + count18K)*memory,
                                                                    self.rden_int[count + l].eq(1),
                                                                    self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                        if (first_word_fall_through):
                                            if (data == 9):
                                                if (k18_flag):
                                                    self.comb += [
                                                        If(~self.rden,
                                                            If(~self.underflow,
                                                                If(self.rd_ptr <= (k_loop + 1 + l + two_block)*memory,
                                                                    If(self.rd_ptr >= (k_loop + l + two_block)*memory,
                                                                        self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                                else:
                                                    self.comb += [
                                                        If(~self.rden,
                                                            If(~self.underflow,
                                                                If(self.rd_ptr <= (k_loop + 1 + l + two_block + count9K)*memory,
                                                                    If(self.rd_ptr >= (k_loop + l + two_block + count9K)*memory,
                                                                        self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                            else:
                                                if (k9_flag):
                                                    self.comb += [
                                                            If(~self.rden,
                                                                If(~self.underflow,
                                                                    If(self.rd_ptr <= (k_loop + 1 + l + count18K + count9K)*memory,
                                                                        If(self.rd_ptr >= (k_loop + l + count18K + count9K)*memory,
                                                                            self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                                else:
                                                    self.comb += [
                                                            If(~self.rden,
                                                                If(~self.underflow,
                                                                    If(self.rd_ptr <= (k_loop + 1 + l + count18K)*memory,
                                                                        If(self.rd_ptr >= (k_loop + l + count18K)*memory,
                                                                            self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                count = count + 2
                                mem = mem + 1
                                if (data == 18):
                                    count18K = count18K + 1
                                elif (data == 9):
                                    count9K = count9K + 1
                                if (count18K != old_count18K):
                                    if (not k9_flag):
                                        k_loop = k_loop + 1
                                    elif (k9_flag or k36_flag):
                                        if (count18K % 2 == 0 and count18K != 0):
                                            k_loop = k_loop + 1
                                    else:
                                        k_loop = k_loop + 1
                                if (count9K != old_count9K):
                                    if (k18_flag or k36_flag):
                                        if (count9K % 1 == 0 and count9K != 0):
                                            two_block = two_block + 1
                                    else:
                                        two_block = two_block + 1
                            old_count18K = count18K
                            old_count9K = count9K
                    else:
                        if (total_mem == 1):
                            if (instance == "FIFO36K"):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WRITE_WIDTH  = C(data), 
                                    p_DATA_READ_WIDTH   = C(data), 
                                    p_FIFO_TYPE         = synchronous,
                                    p_PROG_FULL_THRESH  = C(depth - full_value, 12),
                                    p_PROG_EMPTY_THRESH = C(empty_value, 12),

                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK        = ClockSignal("rd"),
                                    i_WR_CLK        = ClockSignal("wrt"),
                                    i_RESET         = ResetSignal(),

                                    # Input
                                    # -----------------
                                    i_WR_DATA       = self.din[j:data + j],
                                    i_RD_EN         = self.rden_int[count],
                                    i_WR_EN         = self.wren_int[count],

                                    # Output      
                                    o_RD_DATA       = self.dout[j:data + j],
                                    o_EMPTY         = self.empty[count],
                                    o_FULL          = self.full[count],
                                    o_UNDERFLOW     = self.underflow_int[count],
                                    o_OVERFLOW      = self.overflow_int[count],
                                    o_ALMOST_EMPTY  = self.almost_empty[count],
                                    o_ALMOST_FULL   = self.almost_full[count],
                                    o_PROG_FULL     = self.prog_full[count],
                                    o_PROG_EMPTY    = self.prog_empty[count]
                                )
                                count = count + 1
                            else:
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WRITE_WIDTH1  = C(data),
                                    p_DATA_READ_WIDTH1   = C(data), 
                                    p_FIFO_TYPE1         = synchronous,
                                    p_PROG_FULL_THRESH1  = C(full_value, 12),
                                    p_PROG_EMPTY_THRESH1 = C(empty_value, 12),
                                    p_DATA_WRITE_WIDTH2  = C(data),
                                    p_DATA_READ_WIDTH2   = C(data), 
                                    p_FIFO_TYPE2         = synchronous,
                                    p_PROG_FULL_THRESH2  = C(empty_value, 11),
                                    p_PROG_EMPTY_THRESH2 = C(empty_value, 11),
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK1        = ClockSignal("rd"),
                                    i_WR_CLK1        = ClockSignal("wrt"),
                                    i_RESET1         = ResetSignal(),
                                    # Input
                                    # -----------------
                                    i_WR_DATA1       = self.din[j:data + j],
                                    i_RD_EN1         = self.rden_int[count],
                                    i_WR_EN1         = self.wren_int[count],
                                    # Output
                                    # ----------------
                                    o_RD_DATA1       = self.dout_int[count][j:data + j],
                                    o_EMPTY1         = self.empty_int[count],
                                    o_FULL1          = self.full_int[count],
                                    o_UNDERFLOW1     = self.underflow_int[count],
                                    o_OVERFLOW1      = self.overflow_int[count],
                                    o_ALMOST_EMPTY1  = self.almost_empty_int[count],
                                    o_ALMOST_FULL1   = self.almost_full_int[count],
                                    o_PROG_FULL1     = self.prog_full_int[count],
                                    o_PROG_EMPTY1    = self.prog_empty_int[count],
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK2        = ClockSignal("rd"),
                                    i_WR_CLK2        = ClockSignal("wrt"),
                                    i_RESET2         = ResetSignal(),
                                    # Input
                                    # -----------------
                                    i_WR_DATA2       = self.din[j:data + j],
                                    i_RD_EN2         = self.rden_int[count + 1],
                                    i_WR_EN2         = self.wren_int[count + 1],
                                    # Output
                                    # -----------------
                                    o_RD_DATA2       = self.dout_int[count + 1][j:data + j],
                                    o_EMPTY2         = self.empty_int[count + 1],
                                    o_FULL2          = self.full_int[count + 1],
                                    o_UNDERFLOW2     = self.underflow_int[count + 1],
                                    o_OVERFLOW2      = self.overflow_int[count + 1],
                                    o_ALMOST_EMPTY2  = self.almost_empty_int[count + 1],
                                    o_ALMOST_FULL2   = self.almost_full_int[count + 1],
                                    o_PROG_FULL2     = self.prog_full_int[count + 1],
                                    o_PROG_EMPTY2    = self.prog_empty_int[count + 1]
                                )
                                for l in range (2):
                                    if (count + l < num_36K + (num_18K/2)*2 + (num_9K/4)*2):
                                        self.sync.wrt += [
                                            If(self.wren,
                                               If(~self.full,
                                                    If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((count + 1 + l)*memory) + int(starting),
                                                       If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((count + l)*memory) + int(starting),
                                                            self.wren_int[count + l].eq(1)
                                                        )
                                                        .Else(
                                                            self.wren_int[count + l].eq(0)
                                                        )
                                                    )
                                                    .Else(
                                                            self.wren_int[count + l].eq(0)
                                                        )
                                                )
                                                .Else(
                                                    self.wren_int[count + l].eq(0)
                                                        )
                                            )
                                            .Else(
                                                self.wren_int[count + l].eq(0)
                                                        )
                                        ]
                                        if (count + l == 0):
                                            self.sync.rd += [
                                                If(self.rden,
                                                   If(~self.empty,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((count + 1 + l)*memory) + int(starting) - 1,
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((count + l)*memory) + int(starting),
                                                            self.rden_int[count + l].eq(1)
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                                   self.rden_int[count + l].eq(1)
                                                                   ).Else(self.rden_int[count + l].eq(0))
                                                    ).Else(self.rden_int[count + l].eq(0))
                                                ).Else(self.rden_int[count + l].eq(0))
                                            ]
                                        else:
                                            self.sync.rd += [
                                                If(self.rden,
                                                   If(~self.empty,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((count + 1 + l)*memory) + int(starting) - 1,
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((count + l)*memory) + int(starting) - 1,
                                                            self.rden_int[count + l].eq(1)
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ).Else(self.rden_int[count + l].eq(0))
                                                ).Else(self.rden_int[count + l].eq(0))
                                            ]
                                        self.sync.rd += [
                                            If(self.rd_en_flop1,
                                               If(~self.underflow,
                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((count + 1 + l)*memory) + int(starting),
                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((count + l)*memory) + int(starting),
                                                            self.dout[j:data + j].eq(self.dout_int[count + l])
                                                    )
                                                  )
                                               )
                                            )
                                        ]
                                        if (first_word_fall_through):
                                            self.sync.rd += [
                                                If(~self.rden,
                                                    If(~self.underflow,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((count + 1 + l)*memory) + int(starting),
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((count + l)*memory) + int(starting),
                                                                self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                )
                                                            )
                                                        )
                                                    )
                                                )
                                            ]
                                count = count + 2
                        else:
                            if (instance == "FIFO36K" and count_36K < num_36K):
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WRITE_WIDTH  = C(data), 
                                    p_DATA_READ_WIDTH   = C(data), 
                                    p_FIFO_TYPE         = synchronous,
                                    p_PROG_FULL_THRESH  = C(4095, 12),
                                    p_PROG_EMPTY_THRESH = C(0, 12),

                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK        = ClockSignal("rd"),
                                    i_WR_CLK        = ClockSignal("wrt"),
                                    i_RESET         = ResetSignal(),

                                    # Input
                                    # -----------------
                                    i_WR_DATA       = self.din[j:data + j],
                                    i_RD_EN         = self.rden_int[count],
                                    i_WR_EN         = self.wren_int[count],

                                    # Output      
                                    o_RD_DATA       = self.dout_int[count],
                                    o_EMPTY         = self.empty_int[count],
                                    o_FULL          = self.full_int[count],
                                    o_UNDERFLOW     = self.underflow_int[count],
                                    o_OVERFLOW      = self.overflow_int[count],
                                    o_ALMOST_EMPTY  = self.almost_empty_int[count],
                                    o_ALMOST_FULL   = self.almost_full_int[count],
                                    o_PROG_FULL     = self.prog_full_int[count],
                                    o_PROG_EMPTY    = self.prog_empty_int[count]
                                )
                                count = count + 1
                                mem = mem + 1
                                count_36K = count_36K + 1
                            elif(instance == "FIFO18KX2" and mem < total_mem and ((((k % (instances/(instances/2)) == 1 and data == 18 and count18K < (num_18K/2)) or (k + 2 == total_mem) or (k % (instances/(instances/4)) == 1 and data == 9 and count9K < (num_9K/4)) or (not k36_flag and data == 9 and count9K < num_9K/4) or (not k36_flag and data == 18 and count18K < num_18K/2))))):
                                index_array.append(count)
                                index_array.append(count + 1)
                                self.specials += Instance(instance,
                                    # Parameters.
                                    # -----------
                                    # Global.
                                    p_DATA_WRITE_WIDTH1  = C(data),
                                    p_DATA_READ_WIDTH1   = C(data), 
                                    p_FIFO_TYPE1         = synchronous,
                                    p_PROG_FULL_THRESH1  = C(4095, 12),
                                    p_PROG_EMPTY_THRESH1 = C(0, 12),
                                    p_DATA_WRITE_WIDTH2  = C(data),
                                    p_DATA_READ_WIDTH2   = C(data), 
                                    p_FIFO_TYPE2         = synchronous,
                                    p_PROG_FULL_THRESH2  = C(2000, 11),
                                    p_PROG_EMPTY_THRESH2 = C(0, 11),
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK1        = ClockSignal("rd"),
                                    i_WR_CLK1        = ClockSignal("wrt"),
                                    i_RESET1         = ResetSignal(),
                                    # Input
                                    # -----------------
                                    i_WR_DATA1       = self.din[j:data + j],
                                    i_RD_EN1         = self.rden_int[count],
                                    i_WR_EN1         = self.wren_int[count],
                                    # Output     
                                    # ----------------- 
                                    o_RD_DATA1       = self.dout_int[count],
                                    o_EMPTY1         = self.empty_int[count],
                                    o_FULL1          = self.full_int[count],
                                    o_UNDERFLOW1     = self.underflow_int[count],
                                    o_OVERFLOW1      = self.overflow_int[count],
                                    o_ALMOST_EMPTY1  = self.almost_empty_int[count],
                                    o_ALMOST_FULL1   = self.almost_full_int[count],
                                    o_PROG_FULL1     = self.prog_full_int[count],
                                    o_PROG_EMPTY1    = self.prog_empty_int[count],
                                    # Clk / Rst.
                                    # ----------
                                    i_RD_CLK2        = ClockSignal("rd"),
                                    i_WR_CLK2        = ClockSignal("wrt"),
                                    i_RESET2         = ResetSignal(),
                                    # Input
                                    # -----------------
                                    i_WR_DATA2       = self.din[j:data + j],
                                    i_RD_EN2         = self.rden_int[count + 1],
                                    i_WR_EN2         = self.wren_int[count + 1],
                                    # Output      
                                    o_RD_DATA2       = self.dout_int[count + 1],
                                    o_EMPTY2         = self.empty_int[count + 1],
                                    o_FULL2          = self.full_int[count + 1],
                                    o_UNDERFLOW2     = self.underflow_int[count + 1],
                                    o_OVERFLOW2      = self.overflow_int[count + 1],
                                    o_ALMOST_EMPTY2  = self.almost_empty_int[count + 1],
                                    o_ALMOST_FULL2   = self.almost_full_int[count + 1],
                                    o_PROG_FULL2     = self.prog_full_int[count + 1],
                                    o_PROG_EMPTY2    = self.prog_empty_int[count + 1]
                                )
                                for l in range (2):
                                    if (count + l < num_36K + (num_18K/2)*2 + (num_9K/4)*2):
                                        if (data == 9):
                                            if (k18_flag):
                                                self.sync.wrt += [
                                                    If(self.wren,
                                                       If(~self.full,
                                                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + two_block)*memory) + int(starting),
                                                               If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block)*memory) + int(starting),
                                                                    self.wren_int[count + l].eq(1)
                                                                )
                                                                .Else(
                                                                    self.wren_int[count + l].eq(0)
                                                                )
                                                            )
                                                            .Else(
                                                                    self.wren_int[count + l].eq(0)
                                                                )
                                                        )
                                                        .Else(
                                                            self.wren_int[count + l].eq(0)
                                                                )
                                                    )
                                                    .Else(
                                                        self.wren_int[count + l].eq(0)
                                                                )
                                                ]
                                            else:
                                                self.sync.wrt += [
                                                    If(self.wren,
                                                       If(~self.full,
                                                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + two_block + count9K)*memory) + int(starting),
                                                               If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block + count9K)*memory) + int(starting),
                                                                    self.wren_int[count + l].eq(1)
                                                                )
                                                                .Else(
                                                                    self.wren_int[count + l].eq(0)
                                                                )
                                                            )
                                                            .Else(
                                                                    self.wren_int[count + l].eq(0)
                                                                )
                                                        )
                                                        .Else(
                                                            self.wren_int[count + l].eq(0)
                                                                )
                                                    )
                                                    .Else(
                                                        self.wren_int[count + l].eq(0)
                                                                )
                                                ]
                                        else:
                                            if (k9_flag):
                                                self.sync.wrt += [
                                                    If(self.wren,
                                                       If(~self.full,
                                                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + count18K + count9K)*memory) + int(starting),
                                                               If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K + count9K)*memory) + int(starting),
                                                                    self.wren_int[count + l].eq(1)
                                                                )
                                                                .Else(
                                                                    self.wren_int[count + l].eq(0)
                                                                )
                                                            )
                                                            .Else(
                                                                    self.wren_int[count + l].eq(0)
                                                                )
                                                        )
                                                        .Else(
                                                            self.wren_int[count + l].eq(0)
                                                                )
                                                    )
                                                    .Else(
                                                        self.wren_int[count + l].eq(0)
                                                                )
                                                ]
                                            else:
                                                self.sync.wrt += [
                                                    If(self.wren,
                                                       If(~self.full,
                                                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + count18K)*memory) + int(starting),
                                                               If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K)*memory) + int(starting),
                                                                    self.wren_int[count + l].eq(1)
                                                                )
                                                                .Else(
                                                                    self.wren_int[count + l].eq(0)
                                                                )
                                                            )
                                                            .Else(
                                                                    self.wren_int[count + l].eq(0)
                                                                )
                                                        )
                                                        .Else(
                                                            self.wren_int[count + l].eq(0)
                                                                )
                                                    )
                                                    .Else(
                                                        self.wren_int[count + l].eq(0)
                                                                )
                                                ]
                                        if (data == 9):
                                            if (k18_flag):
                                                if ((count + l + count_36K == 0) or (count_36K > 0 and l == 0 and (count9K == 0))):
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + two_block)*memory) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block)*memory) + int(starting),
                                                                    self.rden_int[count + l].eq(1)
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                                           self.rden_int[count + l].eq(1)
                                                                           ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ]
                                                else:
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + two_block)*memory) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block)*memory) + int(starting) - 1,
                                                                    self.rden_int[count + l].eq(1)
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ]
                                                self.sync.rd += [
                                                    If(self.rd_en_flop1,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + two_block)*memory) + int(starting),
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block)*memory) + int(starting),
                                                                    self.dout[j:data + j].eq(self.dout_int[count + l])
                                                            )
                                                          )
                                                       )
                                                    )
                                                ]
                                            else:
                                                if ((count + l + count_36K == 0) or (count_36K > 0 and l == 0 and (count18K + count9K == 0))):
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + two_block + count9K)*memory) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block + count9K)*memory) + int(starting),
                                                                    self.rden_int[count + l].eq(1)
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                                           self.rden_int[count + l].eq(1)
                                                                           ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ]
                                                else:
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + two_block + count9K)*memory) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block + count9K)*memory) + int(starting) - 1,
                                                                    self.rden_int[count + l].eq(1)
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ]
                                                self.sync.rd += [
                                                    If(self.rd_en_flop1,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + two_block + count9K)*memory) + int(starting),
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block + count9K)*memory) + int(starting),
                                                                    self.dout[j:data + j].eq(self.dout_int[count + l])
                                                            )
                                                          )
                                                       )
                                                    )
                                                ]
                                        else:
                                            if (k9_flag):
                                                if ((count + l + count_36K == 0) or (count_36K > 0 and l == 0 and (count18K == 0))):
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + count18K + count9K)*memory) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K + count9K)*memory) + int(starting),
                                                                    self.rden_int[count + l].eq(1)
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                                           self.rden_int[count + l].eq(1)
                                                                           ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ]
                                                else:
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + count18K + count9K)*memory) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K + count9K)*memory) + int(starting) - 1,
                                                                    self.rden_int[count + l].eq(1)
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ]
                                                self.sync.rd += [
                                                    If(self.rd_en_flop1,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + count18K + count9K)*memory) + int(starting),
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K + count9K)*memory) + int(starting),
                                                                    self.dout[j:data + j].eq(self.dout_int[count + l])
                                                            )
                                                          )
                                                       )
                                                    )
                                                ]
                                            else:
                                                if ((count + l + count_36K == 0) or (count_36K > 0 and l == 0 and (count18K + count9K == 0))):
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + count18K)*memory) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K)*memory) + int(starting),
                                                                    self.rden_int[count + l].eq(1)
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                                           self.rden_int[count + l].eq(1)
                                                                           ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ]
                                                else:
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((k_loop + 1 + l + count18K)*memory) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K)*memory) + int(starting)- 1,
                                                                    self.rden_int[count + l].eq(1)
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ]
                                                self.sync.rd += [
                                                    If(self.rd_en_flop1,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((k_loop + 1 + l + count18K)*memory) + int(starting),
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K)*memory) + int(starting),
                                                                    self.dout[j:data + j].eq(self.dout_int[count + l])
                                                            )
                                                          )
                                                       )
                                                    )
                                                ]
                                        if (first_word_fall_through):
                                            if (data == 9):
                                                if (k18_flag):
                                                    self.sync.rd += [
                                                        If(~self.rden,
                                                            If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((k_loop + 1 + l + two_block)*memory) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block)*memory) + int(starting),
                                                                        self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                                else:
                                                    self.sync.rd += [
                                                        If(~self.rden,
                                                            If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((k_loop + 1 + l + two_block + count9K)*memory) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + two_block + count9K)*memory) + int(starting),
                                                                        self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                            else:
                                                if (k9_flag):
                                                    self.sync.rd += [
                                                        If(~self.rden,
                                                            If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((k_loop + 1 + l + count18K + count9K)*memory) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K + count9K)*memory) + int(starting),
                                                                        self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                                else:
                                                    self.sync.rd += [
                                                        If(~self.rden,
                                                            If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((k_loop + 1 + l + count18K)*memory) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((k_loop + l + count18K)*memory) + int(starting),
                                                                        self.dout[j:data + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                count = count + 2
                                mem = mem + 1
                                if (data == 18):
                                    count18K = count18K + 1
                                elif (data == 9):
                                    count9K = count9K + 1
                                if (count18K != old_count18K):
                                    if (not k9_flag):
                                        k_loop = k_loop + 1
                                    elif (k9_flag or k36_flag):
                                        if (count18K % 2 == 0 and count18K != 0):
                                            k_loop = k_loop + 1
                                    else:
                                        k_loop = k_loop + 1
                                if (count9K != old_count9K):
                                    if (k18_flag or k36_flag):
                                        if (count9K % 1 == 0 and count9K != 0):
                                            two_block = two_block + 1
                                    else:
                                        two_block = two_block + 1
                            old_count18K = count18K
                            old_count9K = count9K
                    j = data + j
            memory = 1024
            j_loop = 0
            l = 0
            count_loop = 0
            if (k36_flag):
                for k in range (0, int(mem + (count18K/2)) * math.ceil(data_width/36) + 1, math.ceil(data_width/36)):
                    if (total_mem > 1):
                        for i in range (k, k + math.ceil(data_width/36)):
                            if (i not in index_array and i < count):
                                count_loop = count_loop + 1
                                # Writing and Reading to FIFOs
                                if(SYNCHRONOUS[synchronous]):
                                    self.comb += [
                                        If(self.wren,
                                           If(~self.overflow,
                                              If(~self.full_int[i],
                                                    If(self.wrt_ptr <= (j_loop + 1)*memory,
                                                       If(self.wrt_ptr > (j_loop)*memory,
                                                            self.wren_int[i].eq(1)
                                                       )
                                                    )
                                                )
                                            )
                                        )
                                    ]
                                    self.comb += [
                                        If(self.rden,
                                           If(~self.underflow,
                                                If(self.rd_ptr <= (j_loop + 1)*memory,
                                                  If(self.rd_ptr > (j_loop)*memory,
                                                    self.rden_int[i].eq(1),
                                                    self.dout[(36*l):36 + (36*l)].eq(self.dout_int[i])
                                                    )
                                                )
                                            )
                                        )
                                    ]
                                    
                                    # First Word Fall Through Implmentation
                                    if (first_word_fall_through):
                                        if (j_loop == 0):
                                            self.comb += [
                                                If(~self.rden,
                                                   If(~self.underflow,
                                                      If(self.rd_ptr <= (j_loop + 1)*memory,
                                                        If(self.rd_ptr >= (j_loop)*memory,
                                                            self.dout[(36*l):36 + (36*l)].eq(self.dout_int[i])
                                                        )
                                                      )
                                                   )
                                                )
                                            ]
                                        else:
                                            self.comb += [
                                                If(~self.rden,
                                                   If(~self.underflow,
                                                      If(self.rd_ptr <= (j_loop + 1)*memory,
                                                        If(self.rd_ptr > (j_loop)*memory,
                                                             self.dout[(36*l):36 + (36*l)].eq(self.dout_int[i])
                                                        )
                                                      )
                                                   )
                                                )
                                            ]
                                else:
                                    if (j_loop == total_mem - 1):
                                        if (j_loop == 0):
                                            self.sync.rd += [
                                            If(self.rden,
                                               If(~self.empty,
                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory) + int(starting) - 1,
                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting),
                                                            self.rden_int[i].eq(1)
                                                    )
                                                    .Else(
                                                    self.rden_int[i].eq(0))
                                                  )
                                                  .Else(
                                                    self.rden_int[i].eq(0)
                                                    )
                                               )
                                               .Else(
                                                self.rden_int[i].eq(0)
                                                )
                                            )
                                            .Else(
                                            self.rden_int[i].eq(0)
                                            )
                                            ]
                                        else:
                                            self.sync.rd += [
                                            If(self.rden,
                                               If(~self.empty,
                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory) + int(starting) - 1,
                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting) - 1,
                                                            self.rden_int[i].eq(1)
                                                    )
                                                    .Else(
                                                    self.rden_int[i].eq(0))
                                                  )
                                                  .Else(
                                                    self.rden_int[i].eq(0)
                                                    )
                                               )
                                               .Else(
                                                self.rden_int[i].eq(0)
                                                )
                                            )
                                            .Else(
                                                self.rden_int[i].eq(0)
                                                )
                                        ]
                                        self.sync.rd += [
                                            If(self.rd_en_flop1,
                                               If(~self.underflow,
                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((j_loop + 1)*memory) + int(starting),
                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting),
                                                            self.dout[(36*l):36 + (36*l)].eq(self.dout_int[i])
                                                    )
                                                  )
                                               )
                                            )
                                        ]
                                        self.sync.wrt += [
                                            If(self.wren,
                                               If(~self.full,
                                                If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory) + int(starting),
                                                   If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting),
                                                        self.wren_int[i].eq(1)
                                                        )
                                                        .Else(
                                                        self.wren_int[i].eq(0)
                                                        )
                                                    )
                                                    .Else(
                                                    self.wren_int[i].eq(0)
                                                    )
                                                )
                                                .Else(
                                                self.wren_int[i].eq(0)
                                                )
                                            )
                                            .Else(
                                            self.wren_int[i].eq(0)
                                            )
                                        ]
                                    else:
                                        self.sync.wrt += [
                                        If(self.wren,
                                           If(~self.full,
                                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory) + int(starting),
                                               If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting),
                                                    self.wren_int[i].eq(1)
                                                    )
                                                    .Else(
                                                    self.wren_int[i].eq(0)
                                                    )
                                                )
                                                .Else(
                                                self.wren_int[i].eq(0)
                                                )
                                            )
                                            .Else(
                                            self.wren_int[i].eq(0)
                                            )
                                        )
                                        .Else(
                                        self.wren_int[i].eq(0)
                                        )
                                        ]
                                        if (j_loop == 0):
                                            self.sync.rd += [
                                                If(self.rden,
                                                   If(~self.empty,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory) + int(starting) - 1,
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting),
                                                                self.rden_int[i].eq(1)
                                                        )
                                                        .Else(
                                                        self.rden_int[i].eq(0))
                                                      )
                                                      .Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                               self.rden_int[i].eq(1)
                                                               )
                                                      .Else(
                                                        self.rden_int[i].eq(0)
                                                        )
                                                   )
                                                   .Else(
                                                    self.rden_int[i].eq(0)
                                                    )
                                                )
                                                .Else(
                                                self.rden_int[i].eq(0)
                                                )
                                            ]
                                        else:
                                            self.sync.rd += [
                                            If(self.rden,
                                               If(~self.empty,
                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory) + int(starting) - 1,
                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting) - 1,
                                                            self.rden_int[i].eq(1)
                                                    )
                                                    .Else(
                                                    self.rden_int[i].eq(0)
                                                    )
                                                  )
                                                  .Else(
                                                    self.rden_int[i].eq(0)
                                                    )
                                               )
                                               .Else(
                                                self.rden_int[i].eq(0)
                                                )
                                            )
                                            .Else(
                                            self.rden_int[i].eq(0)
                                            )
                                            ]
                                        self.sync.rd += [
                                            If(self.rd_en_flop1,
                                               If(~self.underflow,
                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory) + int(starting),
                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting),
                                                            self.dout[(36*l):36 + (36*l)].eq(self.dout_int[i])
                                                    )
                                                  )
                                               )
                                            )
                                        ]
                                    # First Word Fall Through Implmentation
                                    if (first_word_fall_through):
                                        if (j_loop == total_mem - 1):
                                            self.sync.rd += [
                                                If(~self.rd_en_flop1,
                                                   If(~self.underflow,
                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= ((j_loop + 1)*memory) + int(starting),
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting),
                                                            self.dout[(36*l):36 + (36*l)].eq(self.dout_int[i])
                                                        )
                                                      )
                                                   )
                                                )
                                            ]
                                        else:
                                            self.sync.rd += [
                                                If(~self.rd_en_flop1,
                                                   If(~self.underflow,
                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory) + int(starting),
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory) + int(starting),
                                                            self.dout[(36*l):36 + (36*l)].eq(self.dout_int[i])
                                                        )
                                                      )
                                                   )
                                                )
                                            ]
                                l = l + 1
                                if (data_width >= 36):
                                    if (count_loop == data_36):
                                        j_loop = j_loop + 1
                                        l = 0
                                        count_loop = 0
                                else:
                                    j_loop = j_loop + 1
                                    l = 0
                                    count_loop = 0
                        
                
            if ((total_mem > 1 and instance == "FIFO36K") or (total_mem >= 1 and instance == "FIFO18KX2")):
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
