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


# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# Making the read and write data widths into their own buses
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

# Making the read and write data widths into their own buses no depth
def divide_n_bit_number_no_depth(number):
    # Convert the number to a binary string
    binary_string = '0' * number
    buses = []

    for i in range(0, len(binary_string), 36):
        bus = binary_string[i:i+36]
        buses.append(bus)
    if (len(buses[-1]) < 36 and len(buses[-1]) > 18):
        for i in range(len(binary_string) - len(buses[-1]), len(binary_string), 18):
            bus = binary_string[i:i+18]
            buses.append(bus)
        buses.pop(-3)
    
    return buses

# Checking the bit length for a certain decimal number
def decimal_to_binary(decimal_number):
    binary_string = bin(decimal_number)[2:]  # Convert to binary and remove the '0b' prefix
    binary_length = len(binary_string)
    return binary_length

# Checking the number of clocks for the output to appear
def clock_cycles_to_obtain_desired_output(desired_output_size):
    max_output_per_block = 36
    if desired_output_size <= max_output_per_block:
        # If the desired size can be obtained from a single block, return 1 clock cycle
        return 1
    else:
        # Calculate the number of clock cycles required to obtain the desired size
        return (desired_output_size + max_output_per_block - 1) // max_output_per_block

# FIFO Generator ---------------------------------------------------------------------------------------
class FIFO(Module):
    def __init__(self, data_width_write, data_width_read, synchronous, full_threshold, empty_threshold, depth, first_word_fall_through, empty_value, full_value, BRAM):
        SYNCHRONOUS = {
            "SYNCHRONOUS"  :   True,
            "ASYNCHRONOUS" :   False
        }
        self.logger = logging.getLogger("FIFO")
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Data Width
        self.logger.info(f"DATA_WIDTH_READ       : {data_width_read}")
        self.logger.info(f"DATA_WIDTH_WRITE       : {data_width_write}")
        # Synchronous / Asynchronous
        self.logger.info(f"SYNCHRONOUS      : {SYNCHRONOUS[synchronous]}")
        # Full and Empty Thresholds
        self.logger.info(f"FULL THRESHOLD       : {full_value}")
        self.logger.info(f"EMPTY THRESHOLD    : {empty_value}")
        # Depth
        self.logger.info(f"DEPTH    : {depth}")
        self.logger.info(f"===================================================")

        buses_write = divide_n_bit_number(data_width_write, depth)
        buses_write_og = buses_write
        buses_read = divide_n_bit_number_no_depth(data_width_read)
        buses_read_og = buses_read
        data_36_write = sum(1 for item in buses_write if ((len(item) >= 18 and depth < 1024) or (len(item) == 36 and depth >= 1024)))
        data_36_read = sum(1 for item in buses_read if ((len(item) >= 18 and depth < 1024) or (len(item) == 36 and depth >= 1024)))
        # Check which list is shorter
        if len(buses_write) < len(buses_read):
            repeat_count = len(buses_read) // len(buses_write)
            buses_write = buses_write * repeat_count + buses_write[:len(buses_read) % len(buses_write)]
        else:
            repeat_count = len(buses_write) // len(buses_read)
            buses_read = buses_read * repeat_count + buses_read[:len(buses_write) % len(buses_read)]
        write_div_read = int(data_width_write/data_width_read)/len(buses_write)
        write_div_read = decimal_to_binary(int(write_div_read))
        size_bram = 36864
        # print(buses_write_og)
        # print(buses_read_og)
        data_36 = sum(1 for item in buses_write if ((len(item) >= 18 and depth < 1024) or (len(item) == 36 and depth >= 1024)))
        total_mem = math.ceil((data_width_write * depth) / size_bram)
        remaining_memory = 0
        depth_mem = 18432
        num_9K = 0
        num_18K = 0
        num_36K = 0
        old_count18K_read = 0
        one_time = 1
        self.prev_empty = Signal()
        old_count9K_read = 0
        if (data_width_write < data_width_read):
            clocks_for_output = int(clock_cycles_to_obtain_desired_output(data_width_read)/len(buses_write_og))
            clocks_for_output_bin = decimal_to_binary(clocks_for_output)
            self.rden_int_count = Signal(int(clocks_for_output))
            self.din_count = Signal(int(clocks_for_output))
        else:
            clocks_for_output = 1
        while remaining_memory < data_width_write * depth:
            for i, bus_write in enumerate(buses_write_og):
                # if (remaining_memory < data_width * depth):
                if (len(bus_write) <= 9):
                    memory = 1024
                    remaining_memory = remaining_memory + (len(bus_write) * memory)
                    num_9K = num_9K + 1
                elif (len(bus_write) <= 18):
                    memory = 1024
                    num_18K = num_18K + 1
                    remaining_memory = remaining_memory + (len(bus_write) * memory)
                elif (len(bus_write) <= 36):
                    memory = 1024
                    num_36K = num_36K + 1
                    remaining_memory = remaining_memory + (len(bus_write) * memory)
        total_mem = num_36K + math.ceil(num_18K/2) + math.ceil(num_9K/4)
        # print(num_36K, math.ceil(num_18K/2), math.ceil(num_9K/4), total_mem)
        memory = 1024
        instances = math.ceil(depth / memory)
        if(SYNCHRONOUS[synchronous]):
            if (data_width_write >= data_width_read):
                self.counter = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1, reset=0)
                self.rd_ptr = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1, reset=0)
            else:
                self.counter = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
                self.rd_ptr = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
            self.wrt_ptr = Signal(math.ceil(math.log2(depth)) + 1, reset=0)
            
        else:
            starting = ((2**(math.ceil(math.log2(depth)))/2) - depth/2) 
            if (data_width_write >= data_width_read):
                self.rd_ptr = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 2, reset=int(starting))
                ending = ((2**(math.ceil(math.log2((data_width_write/data_width_read)*depth)))/2) + ((data_width_write/data_width_read)*depth)/2 - 1) 
            else:
                ending = ((2**(math.ceil(math.log2(depth)))/2) + (depth)/2 - 1) 
                self.rd_ptr = Signal(math.ceil(math.log2(depth)) + 2, reset=int(starting))
            self.wrt_ptr = Signal(math.ceil(math.log2(depth)) + 2, reset=int(starting))

        if (not SYNCHRONOUS[synchronous]):
            self.wrt_ptr_rd_clk1 = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.wrt_ptr_rd_clk2 = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            if (data_width_write >= data_width_read):
                self.rd_ptr_wrt_clk1 = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 2, reset=0)
                self.rd_ptr_wrt_clk2 = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 2, reset=0)
                self.gray_encoded_rdptr = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 2, reset=0)
                self.sync_wrtclk_rdptr_binary = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 2, reset=0)
                self.rd_ptr_reg = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 2, reset=0)
            else:
                self.rd_ptr_wrt_clk1 = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
                self.rd_ptr_wrt_clk2 = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
                self.gray_encoded_rdptr = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
                self.sync_wrtclk_rdptr_binary = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
                self.rd_ptr_reg = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.gray_encoded_wrtptr = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.sync_rdclk_wrtptr_binary = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
            self.rd_en_flop = Signal()
            self.rd_en_flop1 = Signal()
            self.comb += ResetSignal("wrt").eq(ResetSignal("sys"))
            self.comb += ResetSignal("rd").eq(ResetSignal("sys"))
            if (data_width_write >= data_width_read):
                self.empty_count = Signal(2)
            else:
                self.empty_count = Signal(math.ceil(math.log2(clocks_for_output)) + 1, reset=0)
            self.wrt_ptr_reg = Signal(math.ceil(math.log2(depth)) + 2, reset=0)

        self.din    = Signal(data_width_write)
        self.dout   = Signal(data_width_read)

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

        if (data_width_read > data_width_write):
            self.prev_inter_dout = Signal(data_width_read - (36*(len(buses_write_og))))
            self.inter_dout = Signal(36*(len(buses_write_og)))
            self.prev_dout = Signal(data_width_read)                    

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
            k36_flag_read = 0
            index_array = []
            k_loop = 0
            k_loop_read = 0
            two_block_read = 0
            count18K = 0
            old_count18K = 0
            old_count9K = 0
            two_block = 0
            count9K = 0
            count9K_read = 0
            count18K_read = 0
            count_36K = 0
            k9_flag = 0
            k9_flag_read = 0
            k18_flag = 0
            k18_flag_read = 0
            if (data_width_write >= data_width_read):
                depth_read = (data_width_write/data_width_read)*depth
            else:
                depth_read = depth/clocks_for_output
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
                j_read = 0
                for i, (bus_write, bus_read) in enumerate(zip(buses_write, buses_read)):
                    # if (mem < total_mem):
                        if (len(bus_write) <= 9):
                            data_write = 9
                            memory = 2048
                            k9_flag = 1
                        elif (len(bus_write) <= 18):
                            data_write = 18
                            memory = 1024
                            k18_flag = 1
                        elif (len(bus_write) <= 36):
                            data_write = 36
                            memory = 1024
                            k36_flag = 1
                        if (len(bus_read) <= 9):
                            data_read = 9
                            # memory = 2048
                            k9_flag_read = 1
                        elif (len(bus_read) <= 18):
                            data_read = 18
                            # memory = 1024
                            k18_flag_read = 1
                        elif (len(bus_read) <= 36):
                            data_read = 36
                            # memory = 1024
                            k36_flag = 1

                        if (data_write <= 18 and data_read <= 18):
                            instance = "FIFO18KX2"
                        else:
                            instance = "FIFO36K"
                        # Module Instance.
                        # ----------------
                        if(SYNCHRONOUS[synchronous]):
                            if (total_mem == 1):
                                if (instance == "FIFO36K" and count < total_mem):
                                    self.specials += Instance(instance,
                                        # Parameters.
                                        # -----------
                                        # Global.
                                        p_DATA_WRITE_WIDTH  = C(data_write), 
                                        p_DATA_READ_WIDTH   = C(data_read),
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
                                        i_WR_DATA       = self.din[j:data_write + j],
                                        i_RD_EN         = self.rden_int[count],
                                        i_WR_EN         = self.wren_int[count],

                                        # Output      
                                        o_RD_DATA       = self.dout_int[count][j:data_read + j],
                                        o_EMPTY         = self.empty_int[count],
                                        o_FULL          = self.full_int[count],
                                        o_UNDERFLOW     = self.underflow_int[count],
                                        o_OVERFLOW      = self.overflow_int[count],
                                        o_ALMOST_EMPTY  = self.almost_empty[count],
                                        o_ALMOST_FULL   = self.almost_full[count],
                                        o_PROG_FULL     = self.prog_full_int[count],
                                        o_PROG_EMPTY    = self.prog_empty_int[count]
                                    )
                                    count = count + 1
                                    mem = mem + 1
                                elif(instance == "FIFO18KX2" and count < total_mem):
                                    self.specials += Instance(instance,
                                        # Parameters.
                                        # -----------
                                        # Global.
                                        p_DATA_WRITE_WIDTH1  = C(data_write),
                                        p_DATA_READ_WIDTH1   = C(data_read), 
                                        p_FIFO_TYPE1         = synchronous,
                                        p_PROG_FULL_THRESH1  = C(depth - full_value, 12),
                                        p_PROG_EMPTY_THRESH1 = C(empty_value, 12),
                                        p_DATA_WRITE_WIDTH2  = C(data_write), 
                                        p_DATA_READ_WIDTH2   = C(data_read),
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
                                        i_WR_DATA1       = self.din[j:data_write + j],
                                        i_RD_EN1         = self.rden_int[count],
                                        i_WR_EN1         = self.wren_int[count],
                                        # Output      
                                        o_RD_DATA1       = self.dout_int[count][j:data_read + j],
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
                                        i_WR_DATA2       = self.din[j:data_write + j],
                                        i_RD_EN2         = self.rden_int[count + 1],
                                        i_WR_EN2         = self.wren_int[count + 1],
                                        # Output      
                                        o_RD_DATA2       = self.dout_int[count + 1][j:data_read + j],
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
                                            read_memory = int(memory*(data_width_write/data_width_read))
                                            self.comb += [
                                                If(self.rden,
                                                   If(~self.underflow,
                                                        If(self.rd_ptr <= (count + l + 1)*read_memory,
                                                          If(self.rd_ptr > (count + l)*read_memory,
                                                            self.rden_int[count + l].eq(1),
                                                            self.dout[j:data_read + j].eq(self.dout_int[count + l]
                                                                )
                                                            )
                                                        )
                                                    )
                                                )
                                            ]
                                            if (first_word_fall_through):
                                                self.comb += [
                                                    If(~self.rden,
                                                        If(~self.empty_int[count + l],
                                                            If(self.rd_ptr <= (count + l + 1)*read_memory,
                                                                If(self.rd_ptr >= (count + l)*read_memory,
                                                                    self.dout[j:data_write + j].eq(self.dout_int[count + l]
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                    count = count + 2
                                    mem = mem + 1
                            else:
                                if (instance == "FIFO36K" and (data_read == 36 or data_write == 36) and (count_36K < num_36K or mem < total_mem)):
                                    self.specials += Instance(instance,
                                        # Parameters.
                                        # -----------
                                        # Global.
                                        p_DATA_WRITE_WIDTH  = C(data_write), 
                                        p_DATA_READ_WIDTH   = C(data_read),
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
                                        i_WR_DATA       = self.din[j:data_write + j],
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
                                elif(instance == "FIFO18KX2" and mem < total_mem and ((((k % (instances/(instances/2)) == 1 and (data_write == 18 or data_read == 18) and count18K < (num_18K/2)) or (k + 2 == total_mem) or (k % (instances/(instances/4)) == 1 and (data_write == 9 or data_read == 9) and count9K < (num_9K/4)) or (not k36_flag and (data_write == 9 or data_read == 9) and count9K < num_9K/4) or (not k36_flag and (data_write == 18 or data_read == 18) and count18K < num_18K/2))))):
                                    index_array.append(count)
                                    index_array.append(count + 1)
                                    self.specials += Instance(instance,
                                        # Parameters.
                                        # -----------
                                        # Global.
                                        p_DATA_WRITE_WIDTH1  = C(data_write),
                                        p_DATA_READ_WIDTH1   = C(data_read), 
                                        p_FIFO_TYPE1         = synchronous,
                                        p_PROG_FULL_THRESH1  = C(full_value, 12),
                                        p_PROG_EMPTY_THRESH1 = C(empty_value, 12),
                                        p_DATA_WRITE_WIDTH2  = C(data_write),
                                        p_DATA_READ_WIDTH2   = C(data_read), 
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
                                        i_WR_DATA1       = self.din[j:data_write + j],
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
                                        i_WR_DATA2       = self.din[j:data_write + j],
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
                                            if (data_write == 9):
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
                                            if (data_read == 9):
                                                if (k18_flag_read):
                                                    if (data_width_write == data_width_read):
                                                        self.comb += [
                                                            If(self.rden,
                                                               If(~self.underflow,
                                                                    If(self.rd_ptr <= int((k_loop_read + 1 + l + two_block_read) )*memory,
                                                                        If(self.rd_ptr > int((k_loop_read + l + two_block_read))*memory,
                                                                            self.rden_int[count + l].eq(1),
                                                                            self.dout[j:data_read + j].eq(self.dout_int[count + l])
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                    else:
                                                        self.comb += [
                                                            If(self.rden,
                                                               If(~self.underflow,
                                                                    If(self.rd_ptr <= int((k_loop_read + 1 + l + two_block_read) + (count_36K * (data_width_write/data_width_read)))*memory,
                                                                        If(self.rd_ptr > int((k_loop_read + l + two_block_read) + (count_36K * (data_width_write/data_width_read)))*memory,
                                                                            self.rden_int[count + l].eq(1),
                                                                            self.dout[j:data_read + j].eq(self.dout_int[count + l]
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
                                                                If(self.rd_ptr <= int(k_loop_read + 1 + l + two_block_read + count9K_read)*memory*int(data_width_write/data_width_read),
                                                                  If(self.rd_ptr > int(k_loop_read + l + two_block_read + count9K_read)*memory*int(data_width_write/data_width_read),
                                                                        self.rden_int[count + l].eq(1),
                                                                        self.dout[j:data_read + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                            else:
                                                read_memory = int(memory*(data_width_write/data_width_read))
                                                if (k9_flag_read):
                                                    self.comb += [
                                                        If(self.rden,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr <= (k_loop_read + 1 + l + count18K_read + count9K_read)*read_memory,
                                                                  If(self.rd_ptr > (k_loop_read + l + count18K_read + count9K_read)*read_memory,
                                                                        self.rden_int[count + l].eq(1),
                                                                        self.dout[j:data_read + j].eq(self.dout_int[count + l]
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
                                                                If(self.rd_ptr <= (k_loop_read + 1 + l + count18K_read)*read_memory,
                                                                  If(self.rd_ptr > (k_loop_read + l + count18K_read)*read_memory,
                                                                        self.rden_int[count + l].eq(1),
                                                                        self.dout[j:data_read + j].eq(self.dout_int[count + l]
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    ]
                                            if (first_word_fall_through):
                                                if (data_read == 9):
                                                    if (k18_flag_read):
                                                        self.comb += [
                                                            If(~self.rden,
                                                                If(~self.empty_int[count + l],
                                                                    If(self.rd_ptr <= int(k_loop_read + 1 + l + two_block_read + (count_36K * (data_width_write/data_width_read)))*memory,
                                                                        If(self.rd_ptr >= int(k_loop_read + l + two_block_read + (count_36K * (data_width_write/data_width_read)))*memory,
                                                                            self.dout[j:data_write + j].eq(self.dout_int[count + l]
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                    else:
                                                        self.comb += [
                                                            If(~self.rden,
                                                                If(~self.empty_int[count + l],
                                                                    If(self.rd_ptr <= int(k_loop_read + 1 + l + two_block_read + count9K_read)*memory*int(data_width_write/data_width_read),
                                                                        If(self.rd_ptr >= int(k_loop_read + l + two_block_read + count9K_read)*memory*int(data_width_write/data_width_read),
                                                                            self.dout[j:data_write + j].eq(self.dout_int[count + l]
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                else:
                                                    if (k9_flag_read):
                                                        self.comb += [
                                                                If(~self.rden,
                                                                    If(~self.empty_int[count + l],
                                                                        If(self.rd_ptr <= int(k_loop_read + 1 + l + count18K_read + count9K_read)*read_memory,
                                                                            If(self.rd_ptr >= int(k_loop_read + l + count18K_read + count9K_read)*read_memory,
                                                                                self.dout[j:data_write + j].eq(self.dout_int[count + l]
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                    else:
                                                        self.comb += [
                                                                If(~self.rden,
                                                                    If(~self.empty_int[count + l],
                                                                        If(self.rd_ptr <= int(k_loop_read + 1 + l + count18K_read)*read_memory,
                                                                            If(self.rd_ptr >= int(k_loop_read + l + count18K_read)*read_memory,
                                                                                self.dout[j:data_write + j].eq(self.dout_int[count + l]
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                    count = count + 2
                                    mem = mem + 1
                                    if (data_write == 18):
                                        count18K = count18K + 1
                                    elif (data_write == 9):
                                        count9K = count9K + 1
                                    if (data_read == 18):
                                        count18K_read = count18K_read + 1
                                    elif (data_read == 9):
                                        count9K_read = count9K_read + 1

                                    if (count18K != old_count18K):
                                        if (not k9_flag):
                                            k_loop = k_loop + 1
                                        elif (k9_flag or k36_flag):
                                            if (count18K % 2 == 0 and count18K != 0):
                                                k_loop = k_loop + 1
                                        else:
                                            k_loop = k_loop + 1

                                    if (count18K_read != old_count18K_read):
                                        if (not k9_flag_read):
                                            k_loop_read = k_loop_read + 1
                                        elif (k9_flag_read or k36_flag_read):
                                            if (count18K_read % 2 == 0 and count18K_read != 0):
                                                k_loop_read = k_loop_read + 1
                                        else:
                                            k_loop_read = k_loop_read + 1

                                    if (count9K != old_count9K):
                                        if (k18_flag or k36_flag):
                                            if (count9K % 1 == 0 and count9K != 0):
                                                two_block = two_block + 1
                                        else:
                                            two_block = two_block + 1
                                    if (count9K_read != old_count9K_read):
                                        if (k18_flag_read or k36_flag_read):
                                            if (count9K_read % 1 == 0 and count9K_read != 0):
                                                two_block_read = two_block_read + 1
                                        else:
                                            two_block_read = two_block_read + 1

                                old_count18K = count18K
                                old_count9K = count9K
                                old_count18K_read = count18K_read
                                old_count9K_read = count9K_read
                        else:
                            if (total_mem == 1):
                                if (instance == "FIFO36K" and count < total_mem):
                                    self.specials += Instance(instance,
                                        # Parameters.
                                        # -----------
                                        # Global.
                                        p_DATA_WRITE_WIDTH  = C(data_write),
                                        p_DATA_READ_WIDTH   = C(data_read), 
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
                                        i_WR_DATA       = self.din[j:data_write + j],
                                        i_RD_EN         = self.rden_int[count],
                                        i_WR_EN         = self.wren_int[count],

                                        # Output      
                                        o_RD_DATA       = self.dout_int[count][j:data_read + j],
                                        o_EMPTY         = self.empty_int[count],
                                        o_FULL          = self.full_int[count],
                                        o_UNDERFLOW     = self.underflow_int[count],
                                        o_OVERFLOW      = self.overflow_int[count],
                                        o_ALMOST_EMPTY  = self.almost_empty[count],
                                        o_ALMOST_FULL   = self.almost_full[count],
                                        o_PROG_FULL     = self.prog_full_int[count],
                                        o_PROG_EMPTY    = self.prog_empty_int[count]
                                    )
                                    count = count + 1
                                    mem = mem + 1
                                elif(instance == "FIFO18KX2" and count < total_mem):
                                    self.specials += Instance(instance,
                                        # Parameters.
                                        # -----------
                                        # Global.
                                        p_DATA_WRITE_WIDTH1  = C(data_write),
                                        p_DATA_READ_WIDTH1   = C(data_read), 
                                        p_FIFO_TYPE1         = synchronous,
                                        p_PROG_FULL_THRESH1  = C(depth - full_value, 12),
                                        p_PROG_EMPTY_THRESH1 = C(empty_value, 12),
                                        p_DATA_WRITE_WIDTH2  = C(data_write),
                                        p_DATA_READ_WIDTH2   = C(data_read), 
                                        p_FIFO_TYPE2         = synchronous,
                                        p_PROG_FULL_THRESH2  = C(depth - full_value, 11),
                                        p_PROG_EMPTY_THRESH2 = C(empty_value, 11),
                                        # Clk / Rst.
                                        # ----------
                                        i_RD_CLK1        = ClockSignal("rd"),
                                        i_WR_CLK1        = ClockSignal("wrt"),
                                        i_RESET1         = ResetSignal(),
                                        # Input
                                        # -----------------
                                        i_WR_DATA1       = self.din[j:data_write + j],
                                        i_RD_EN1         = self.rden_int[count],
                                        i_WR_EN1         = self.wren_int[count],
                                        # Output
                                        # ----------------
                                        o_RD_DATA1       = self.dout_int[count][j:data_read + j],
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
                                        i_WR_DATA2       = self.din[j:data_write + j],
                                        i_RD_EN2         = self.rden_int[count + 1],
                                        i_WR_EN2         = self.wren_int[count + 1],
                                        # Output
                                        # -----------------
                                        o_RD_DATA2       = self.dout_int[count + 1][j:data_read + j],
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
                                            read_memory = int(memory*(data_width_write/data_width_read))
                                            if (count + l == 0):
                                                self.sync.rd += [
                                                    If(self.rden,
                                                       If(~self.empty,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((count + 1 + l)*read_memory) + int(starting) - 1,
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((count + l)*read_memory) + int(starting),
                                                                self.rden_int[count + l].eq(1)
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] == int(ending),
                                                                       self.rden_int[count + l].eq(1)
                                                                       ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ).Else(self.rden_int[count + l].eq(0))
                                                ]
                                            else:
                                                self.sync.rd += [
                                                    If(self.rden,
                                                       If(~self.empty,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((count + 1 + l)*read_memory) + int(starting) - 1,
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((count + l)*read_memory) + int(starting) - 1,
                                                                self.rden_int[count + l].eq(1)
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ).Else(self.rden_int[count + l].eq(0))
                                                    ).Else(self.rden_int[count + l].eq(0))
                                                ]
                                            self.sync.rd += [
                                                If(self.rd_en_flop1,
                                                   If(~self.underflow,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((count + 1 + l)*memory) + int(starting),
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((count + l)*memory) + int(starting),
                                                                self.dout[j:data_read + j].eq(self.dout_int[count + l])
                                                        )
                                                      )
                                                   )
                                                )
                                            ]
                                            if (first_word_fall_through):
                                                self.sync.rd += [
                                                    If(~self.rden,
                                                        If(~self.empty_int[count + l],
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] <= int((count + 1 + l)*read_memory) + int(starting),
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= int((count + l)*read_memory) + int(starting),
                                                                    self.dout[j:data_write + j].eq(self.dout_int[count + l]
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                    count = count + 2
                                    mem = mem + 1
                            else:
                                if (instance == "FIFO36K" and (data_read == 36 or data_write == 36) and (count_36K < num_36K or mem < total_mem)):
                                    self.specials += Instance(instance,
                                        # Parameters.
                                        # -----------
                                        # Global.
                                        p_DATA_WRITE_WIDTH  = C(data_write),
                                        p_DATA_READ_WIDTH   = C(data_read), 
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
                                        i_WR_DATA       = self.din[j:data_write + j],
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
                                elif(instance == "FIFO18KX2" and mem < total_mem and ((((k % (instances/(instances/2)) == 1 and (data_write == 18 or data_read == 18) and count18K < (num_18K/2)) or (k + 2 == total_mem) or (k % (instances/(instances/4)) == 1 and (data_write == 9 or data_read == 9) and count9K < (num_9K/4)) or (not k36_flag and (data_write == 9 or data_read == 9) and count9K < num_9K/4) or (not k36_flag and (data_write == 18 or data_read == 18) and count18K < num_18K/2))))):
                                    index_array.append(count)
                                    index_array.append(count + 1)
                                    self.specials += Instance(instance,
                                        # Parameters.
                                        # -----------
                                        # Global.
                                        p_DATA_WRITE_WIDTH1  = C(data_write),
                                        p_DATA_READ_WIDTH1   = C(data_read), 
                                        p_FIFO_TYPE1         = synchronous,
                                        p_PROG_FULL_THRESH1  = C(full_value, 12),
                                        p_PROG_EMPTY_THRESH1 = C(empty_value, 12),
                                        p_DATA_WRITE_WIDTH2  = C(data_write),
                                        p_DATA_READ_WIDTH2   = C(data_read), 
                                        p_FIFO_TYPE2         = synchronous,
                                        p_PROG_FULL_THRESH2  = C(full_value, 11),
                                        p_PROG_EMPTY_THRESH2 = C(empty_value, 11),
                                        # Clk / Rst.
                                        # ----------
                                        i_RD_CLK1        = ClockSignal("rd"),
                                        i_WR_CLK1        = ClockSignal("wrt"),
                                        i_RESET1         = ResetSignal(),
                                        # Input
                                        # -----------------
                                        i_WR_DATA1       = self.din[j:data_write + j],
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
                                        i_WR_DATA2       = self.din[j:data_write + j],
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
                                            if (data_write == 9):
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
                                            if (data_read == 9):
                                                if (k18_flag_read):
                                                    if ((count + l + count_36K == 0) or (count_36K > 0 and l == 0 and (count9K_read == 0))):
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < int((k_loop_read + 1 + l + two_block_read + (count_36K * (data_width_write/data_width_read)))*memory) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= int((k_loop_read + l + two_block_read + (count_36K * (data_width_write/data_width_read)))*memory) + int(starting),
                                                                        self.rden_int[count + l].eq(1)
                                                                        ).Else(self.rden_int[count + l].eq(0))
                                                                    ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] == int(ending),
                                                                               self.rden_int[count + l].eq(1)
                                                                               ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < int((k_loop_read + 1 + l + two_block_read + (count_36K * (data_width_write/data_width_read)))*memory) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= int((k_loop_read + l + two_block_read + (count_36K * (data_width_write/data_width_read)))*memory) + int(starting) - 1,
                                                                        self.rden_int[count + l].eq(1)
                                                                        ).Else(self.rden_int[count + l].eq(0))
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ]
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < int((k_loop_read + 1 + l + two_block_read)*memory) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= int((k_loop_read + l + two_block_read)*memory) + int(starting),
                                                                        self.dout[j_read % data_width_read: ((data_read + j_read) % data_width_read ) + data_read].eq(self.dout_int[count + l])
                                                                )
                                                              )
                                                           )
                                                        )
                                                    ]
                                                else:
                                                    if ((count + l + count_36K == 0) or (count_36K > 0 and l == 0 and (count18K_read + count9K_read == 0))):
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((k_loop_read + 1 + l + two_block_read + count9K_read)*memory)*int(data_width_write/data_width_read) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + two_block_read + count9K_read)*memory)*int(data_width_write/data_width_read) + int(starting),
                                                                        self.rden_int[count + l].eq(1)
                                                                        ).Else(self.rden_int[count + l].eq(0))
                                                                    ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] == int(ending),
                                                                               self.rden_int[count + l].eq(1)
                                                                               ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((k_loop_read + 1 + l + two_block_read + count9K_read)*memory)*int(data_width_write/data_width_read) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + two_block_read + count9K_read)*memory)*int(data_width_write/data_width_read) + int(starting) - 1,
                                                                        self.rden_int[count + l].eq(1)
                                                                        ).Else(self.rden_int[count + l].eq(0))
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ]
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((k_loop_read + 1 + l + two_block_read + count9K_read)*memory)*int(data_width_write/data_width_read) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + two_block_read + count9K_read)*memory)*int(data_width_write/data_width_read) + int(starting),
                                                                        self.dout[j_read % data_width_read: ((data_read + j_read) % data_width_read ) + data_read].eq(self.dout_int[count + l])
                                                                )
                                                              )
                                                           )
                                                        )
                                                    ]
                                            else:
                                                read_memory = int(memory*(data_width_write/data_width_read))
                                                if (k9_flag_read):
                                                    if ((count + l + count_36K == 0) or (count_36K > 0 and l == 0 and (count18K_read == 0))):
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((k_loop_read + 1 + l + count18K_read + count9K_read)*read_memory) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + count18K_read + count9K_read)*read_memory) + int(starting),
                                                                        self.rden_int[count + l].eq(1)
                                                                        ).Else(self.rden_int[count + l].eq(0))
                                                                    ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] == int(ending),
                                                                               self.rden_int[count + l].eq(1)
                                                                               ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((k_loop_read + 1 + l + count18K_read + count9K_read)*read_memory) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + count18K_read + count9K_read)*read_memory) + int(starting) - 1,
                                                                        self.rden_int[count + l].eq(1)
                                                                        ).Else(self.rden_int[count + l].eq(0))
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ]
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((k_loop_read + 1 + l + count18K_read + count9K_read)*read_memory) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + count18K_read + count9K_read)*read_memory) + int(starting),
                                                                        self.dout[j:data_read + j].eq(self.dout_int[count + l])
                                                                )
                                                              )
                                                           )
                                                        )
                                                    ]
                                                else:
                                                    if ((count + l + count_36K == 0) or (count_36K > 0 and l == 0 and (count18K_read + count9K_read == 0))):
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((k_loop_read + 1 + l + count18K_read)*read_memory) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + count18K_read)*read_memory) + int(starting),
                                                                        self.rden_int[count + l].eq(1)
                                                                        ).Else(self.rden_int[count + l].eq(0))
                                                                    ).Elif(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] == int(ending),
                                                                               self.rden_int[count + l].eq(1)
                                                                               ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] < ((k_loop_read + 1 + l + count18K_read)*read_memory) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + count18K_read)*read_memory) + int(starting)- 1,
                                                                        self.rden_int[count + l].eq(1)
                                                                        ).Else(self.rden_int[count + l].eq(0))
                                                                    ).Else(self.rden_int[count + l].eq(0))
                                                                ).Else(self.rden_int[count + l].eq(0))
                                                            ).Else(self.rden_int[count + l].eq(0))
                                                        ]
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] <= ((k_loop_read + 1 + l + count18K_read)*read_memory) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= ((k_loop_read + l + count18K_read)*read_memory) + int(starting),
                                                                        self.dout[j:data_read + j].eq(self.dout_int[count + l])
                                                                )
                                                              )
                                                           )
                                                        )
                                                    ]
                                            if (first_word_fall_through):
                                                if (data_read == 9):
                                                    if (k18_flag_read):
                                                        self.sync.rd += [
                                                            If(~self.rden,
                                                                If(~self.empty_int[count + l],
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] <= int((k_loop_read + 1 + l + two_block_read + (count_36K * (data_width_write/data_width_read)))*memory) + int(starting),
                                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= int((k_loop_read + l + two_block_read + (count_36K * (data_width_write/data_width_read)))*memory) + int(starting),
                                                                            self.dout[j_read % data_width_read: ((data_read + j_read) % data_width_read ) + data_read].eq(self.dout_int[count + l]
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(~self.rden,
                                                                If(~self.empty_int[count + l],
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] <= int((k_loop_read + 1 + l + two_block_read + count9K_read)*memory*int(data_width_write/data_width_read)) + int(starting),
                                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= int((k_loop_read + l + two_block_read + count9K_read)*memory*int(data_width_write/data_width_read)) + int(starting),
                                                                            self.dout[j_read % data_width_read: ((data_read + j_read) % data_width_read ) + data_read].eq(self.dout_int[count + l]
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                else:
                                                    if (k9_flag_read):
                                                        self.sync.rd += [
                                                            If(~self.rden,
                                                                If(~self.empty_int[count + l],
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] <= int((k_loop_read + 1 + l + count18K_read + count9K_read)*read_memory) + int(starting),
                                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= int((k_loop_read + l + count18K_read + count9K_read)*read_memory) + int(starting),
                                                                            self.dout[j:data_write + j].eq(self.dout_int[count + l]
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(~self.rden,
                                                                If(~self.empty_int[count + l],
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] <= int((k_loop_read + 1 + l + count18K_read)*read_memory) + int(starting),
                                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] >= int((k_loop_read + l + count18K_read)*read_memory) + int(starting),
                                                                            self.dout[j:data_write + j].eq(self.dout_int[count + l]
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                    count = count + 2
                                    mem = mem + 1
                                    if (data_write == 18):
                                        count18K = count18K + 1
                                    elif (data_write == 9):
                                        count9K = count9K + 1
                                    if (data_read == 18):
                                        count18K_read = count18K_read + 1
                                    elif (data_read == 9):
                                        count9K_read = count9K_read + 1

                                    if (count18K != old_count18K):
                                        if (not k9_flag):
                                            k_loop = k_loop + 1
                                        elif (k9_flag or k36_flag):
                                            if (count18K % 2 == 0 and count18K != 0):
                                                k_loop = k_loop + 1
                                        else:
                                            k_loop = k_loop + 1

                                    if (count18K_read != old_count18K_read):
                                        if (not k9_flag_read):
                                            k_loop_read = k_loop_read + 1
                                        elif (k9_flag_read or k36_flag_read):
                                            if (count18K_read % 2 == 0 and count18K_read != 0):
                                                k_loop_read = k_loop_read + 1
                                        else:
                                            k_loop_read = k_loop_read + 1

                                    if (count9K != old_count9K):
                                        if (k18_flag or k36_flag):
                                            if (count9K % 1 == 0 and count9K != 0):
                                                two_block = two_block + 1
                                        else:
                                            two_block = two_block + 1
                                    if (count9K_read != old_count9K_read):
                                        if (k18_flag_read or k36_flag_read):
                                            if (count9K_read % 1 == 0 and count9K_read != 0):
                                                two_block_read = two_block_read + 1
                                        else:
                                            two_block_read = two_block_read + 1

                                old_count18K = count18K
                                old_count9K = count9K
                                old_count18K_read = count18K_read
                                old_count9K_read = count9K_read
                        if (len(buses_read_og) < len(buses_write_og)):
                            j = data_write + j
                        elif(data_width_read == data_width_write):
                            j = data_write + j
                        elif (data_write + j < data_width_write):
                            j = data_write + j
                        else:
                            j = 0
                        j_read = data_read + j_read
            memory = 1024
            j_loop = 0
            l = 0
            toggle = 0
            toggle_2x = 0
            count_loop = 0

            #  rd_ptr for checking the 0's and 1's for the switching mechanism
            if (len(buses_read_og) < len(buses_write_og)):
                if (data_width_write >= data_width_read):
                    self.rd_ptr_minus = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1, reset=0)
                    self.rd_ptr_add = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1, reset=0)
                else:
                    self.rd_ptr_minus = Signal(math.ceil(math.log2(depth/clocks_for_output)) + 1, reset=0)
                if (SYNCHRONOUS[synchronous]):
                    self.comb += [
                        If(self.rden,
                           self.rd_ptr_minus.eq(self.rd_ptr - 1)
                           )
                        ]
                else:
                    self.comb += [
                        If(self.rden,
                           self.rd_ptr_add.eq(self.rd_ptr + 1)
                           )
                    ]
            if (not SYNCHRONOUS[synchronous]):
                if (data_width_write > data_width_read):
                    self.wrt_pointer_multiple = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 2, reset=0)
                    self.comb += self.wrt_pointer_multiple[0:math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1].eq(self.wrt_ptr[0: math.ceil(math.log2((data_width_write/data_width_read)*depth)) - 1]*(int(data_width_write/(data_width_read if data_width_read >= 36 else 36))))
                    self.comb += self.wrt_pointer_multiple[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1].eq(self.wrt_ptr[math.ceil(math.log2((data_width_write/data_width_read)*depth)) - 1])
                    self.sync_rdclk_wrtptr_binary_multiple = Signal(math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 2, reset=0)
                    self.comb += self.sync_rdclk_wrtptr_binary_multiple[0:math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1].eq(self.sync_rdclk_wrtptr_binary[0: math.ceil(math.log2((data_width_write/data_width_read)*depth)) - 1]*int(data_width_write/(data_width_read if data_width_read >= 36 else 36)))
                    self.comb += self.sync_rdclk_wrtptr_binary_multiple[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1].eq(self.sync_rdclk_wrtptr_binary[math.ceil(math.log2((data_width_write/data_width_read)*depth)) - 1])
                elif (data_width_write < data_width_read):
                    self.rd_pointer_multiple = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
                    self.comb += self.rd_pointer_multiple[0:math.ceil(math.log2(depth)) + 1].eq(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1]*int((data_width_read/data_width_write)/clocks_for_output))
                    self.comb += self.rd_pointer_multiple[math.ceil(math.log2(depth)) + 1].eq(self.rd_ptr[math.ceil(math.log2(depth)) + 1])
                    self.sync_wrtclk_rdptr_binary_multiple = Signal(math.ceil(math.log2(depth)) + 2, reset=0)
                    self.comb += self.sync_wrtclk_rdptr_binary_multiple[0:math.ceil(math.log2(depth)) + 1].eq(self.sync_wrtclk_rdptr_binary[0:math.ceil(math.log2(depth)) + 1]*int((data_width_read/data_width_write)/clocks_for_output))
                    self.comb += self.sync_wrtclk_rdptr_binary_multiple[math.ceil(math.log2(depth)) + 1].eq(self.sync_wrtclk_rdptr_binary[math.ceil(math.log2(depth)) + 1])

            if (first_word_fall_through):
                self.last_data = Signal(data_width_read)
                if (SYNCHRONOUS[synchronous]):
                    if (data_width_read == data_width_write):
                        self.sync += [
                            If(self.wren,
                               If(~self.overflow,
                                    If(self.full,
                                        self.last_data.eq(self.din)
                                  )
                               )
                            )
                        ]
                        self.comb += [
                            If(self.empty,
                               self.dout.eq(self.last_data)
                               )
                        ]
                    elif (data_width_read > data_width_write):
                        ii_loop = 0
                        for ii in range (int(data_width_read/data_width_write) - 1, -1, -1):
                            self.sync += [
                                If(self.wren,
                                   If(~self.overflow,
                                        If((self.counter + ii_loop) == depth,
                                            self.last_data[(data_width_write*ii) :((data_width_write + (data_width_write*ii)))].eq(self.din)
                                      )
                                   )
                                )
                            ]
                            ii_loop = ii_loop + 1
                    else:
                        self.sync += [
                            If(self.wren,
                                If(~self.overflow,
                                  If(self.full,
                                    self.last_data.eq(self.din[data_width_read : data_width_write])
                              )
                           )
                        )
                        ]
                        self.comb += [
                            If(self.empty,
                               self.dout.eq(self.last_data)
                               )
                        ]
                else:
                    if (data_width_write == data_width_read):
                        self.sync.wrt += [
                            If(self.wren,
                               If(~self.overflow,
                                    If(self.full,
                                        self.last_data.eq(self.din)
                                  )
                               )
                            )
                        ]
                        self.sync.rd += [
                            If(self.empty,
                               self.dout.eq(self.last_data)
                               )
                        ]
                    elif (data_width_read > data_width_write):
                        ii_loop = 0
                        for ii in range (int(data_width_read/data_width_write) - 1, -1, -1):
                            self.sync.wrt += [
                                If(self.wren,
                                   If(~self.overflow,
                                           If(self.wrt_ptr[0:math.ceil(math.log2(depth))] + ii_loop == self.sync_wrtclk_rdptr_binary_multiple[0:math.ceil(math.log2(depth))],
                                                self.last_data[(data_width_write*ii) :((data_width_write + (data_width_write*ii)))].eq(self.din)
                                           )
                                   )
                                )
                            ]
                            ii_loop = ii_loop + 1
                    else:
                        self.sync.wrt += [
                            If(self.wren,
                                If(~self.overflow,
                                  If(self.full,
                                    self.last_data.eq(self.din[data_width_read : data_width_write])
                              )
                           )
                        )
                        ]
                        self.sync.rd += [
                            If(self.empty,
                               self.dout.eq(self.last_data)
                               )
                        ]

            if (clocks_for_output > 1):
                # Checking how many clock cycles taken for the output to appear
                if (SYNCHRONOUS[synchronous]):
                    if (not first_word_fall_through):
                        self.comb += [
                            If(self.rden,
                               If(~self.underflow,
                                If(self.rd_ptr > 0,
                                 If(self.rd_ptr[0:int(clocks_for_output_bin) - 1] == 0,
                                 self.dout.eq(Cat(self.prev_inter_dout, self.inter_dout)
                                              )
                                 ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                               ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                            ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                            )
                        ]
                    else:
                        self.comb += [
                            If(self.rden,
                               If(~self.underflow,
                                If(self.rd_ptr > 0,
                                 If(self.rd_ptr[0:int(clocks_for_output_bin) - 1] == 0,
                                 self.dout.eq(Cat(self.prev_inter_dout, self.inter_dout)
                                              )
                                 ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                               ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                            ).Else(
                                self.dout.eq(self.prev_dout)
                            )
                            ).Else(
                                If(self.rd_ptr >= 0,
                                   If(~self.prev_empty,
                                 self.dout.eq(Cat(self.prev_inter_dout, self.inter_dout)
                                              )
                                ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                               ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                            ),
                            If(self.empty,
                               self.dout.eq(self.last_data)
                               )
                        ]
                        
                    if (clocks_for_output > 2):
                        if (not first_word_fall_through):
                            self.sync += [
                                self.prev_inter_dout.eq(Cat(self.prev_inter_dout[36*(len(buses_write_og)):data_width_read - (36*(len(buses_write_og)))], self.inter_dout)),
                                self.prev_dout.eq(self.dout)                    
                            ]
                        else:
                            self.sync += [
                                If(~self.rden,
                                    If(self.empty != self.prev_empty,
                                        self.prev_inter_dout.eq(Cat(self.prev_inter_dout[36*(len(buses_write_og)):data_width_read - (36*(len(buses_write_og)))], self.inter_dout)) 
                                    )
                                ).Else(
                                    self.prev_inter_dout.eq(Cat(self.prev_inter_dout[36*(len(buses_write_og)):data_width_read - (36*(len(buses_write_og)))], self.inter_dout)) 
                                ),
                                self.prev_dout.eq(self.dout)                          
                            ]
                    else:
                        if (not first_word_fall_through):
                            self.sync += [
                                self.prev_inter_dout.eq(self.inter_dout),
                                self.prev_dout.eq(self.dout)
                            ]
                        else:
                            self.sync += [
                                If(~self.rden,
                                    If(self.empty != self.prev_empty,
                                        self.prev_inter_dout.eq(self.inter_dout)
                                    )
                                ).Else(
                                    self.prev_inter_dout.eq(self.inter_dout)
                                ),
                                self.prev_dout.eq(self.dout)
                            ]
                else:
                    if (not first_word_fall_through):
                        self.sync.rd += [
                            If(self.rden,
                               If(self.rd_ptr > 0,
                                If(self.rd_ptr[0:int(clocks_for_output_bin) - 1] == 0,
                                self.dout.eq(Cat(self.prev_inter_dout, self.inter_dout)
                                             )
                                ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                               ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                            ).Else(
                                 self.dout.eq(0)
                             )
                        ]
                    else:
                        self.sync.rd += [
                            If(self.rden,
                               If(self.rd_ptr > 0,
                                If(self.rd_ptr[0:int(clocks_for_output_bin) - 1] == 0,
                                self.dout.eq(Cat(self.prev_inter_dout, self.inter_dout)
                                             )
                                ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                               ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                            ).Else(
                                If(self.rd_ptr >= 0,
                                If(self.din_count > clocks_for_output,
                                self.dout.eq(Cat(self.prev_inter_dout, self.inter_dout)
                                             )
                                ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                               ).Else(
                                 self.dout.eq(self.prev_dout)
                             )
                            )
                        ]
                    if (clocks_for_output > 2):
                        if(not first_word_fall_through):
                            self.sync.rd += [
                                self.prev_inter_dout.eq(Cat(self.prev_inter_dout[36*(len(buses_write_og)):data_width_read - (36*(len(buses_write_og)))], self.inter_dout)),
                                self.prev_dout.eq(self.dout)
                            ]
                        else:
                            self.sync.rd += [
                                If(~self.rden,
                                    If(self.din_count <= clocks_for_output,
                                       self.prev_inter_dout.eq(Cat(self.prev_inter_dout[36*(len(buses_write_og)):data_width_read - (36*(len(buses_write_og)))], self.inter_dout))
                                    )
                                ).Else(
                                    self.prev_inter_dout.eq(Cat(self.prev_inter_dout[36*(len(buses_write_og)):data_width_read - (36*(len(buses_write_og)))], self.inter_dout))
                                ),
                                self.prev_dout.eq(self.dout)
                            ]
                    else:
                        if(not first_word_fall_through):
                            self.sync.rd += [
                                self.prev_inter_dout.eq(self.inter_dout),
                                self.prev_dout.eq(self.dout)
                            ]
                        else:
                            self.sync.rd += [
                                If(~self.rden,
                                    If(self.din_count <= clocks_for_output,
                                        self.prev_inter_dout.eq(self.inter_dout)
                                    )
                                ).Else(
                                    self.prev_inter_dout.eq(self.inter_dout)
                                ),
                                self.prev_dout.eq(self.dout)
                            ]

            if (k36_flag):
                # This loop is for the read pointers
                for k in range (0, int(mem + (count18K_read/2)) * math.ceil(data_width_read/36) + 1, math.ceil(data_width_read/36)):
                    # if (total_mem > 1):
                        for i in range (k, k + math.ceil(data_width_read/36)):
                            if (i not in index_array and i < (count)):
                                count_loop = count_loop + 1
                                # Reading From FIFOs
                                if(SYNCHRONOUS[synchronous]):
                                    if (data_width_read != data_width_write):
                                        if (len(buses_read_og) < len(buses_write_og)):
                                            if (data_width_read <= 36):
                                                self.comb += [
                                                    If(self.rden,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                              If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                 If(self.rd_ptr_minus[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == toggle_2x,
                                                                    If(self.rd_ptr_minus[int(write_div_read) - 1] == toggle,
                                                                       self.rden_int[i].eq(1),
                                                                       self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read+ 36)].eq(self.dout_int[i])
                                                                    )
                                                                 )
                                                              )
                                                            )
                                                        )
                                                    )
                                                ]
                                                toggle = 1 - toggle
                                                if ((i - 1) % 2 == 0):
                                                    toggle_2x = toggle_2x + 1
                                                if (decimal_to_binary(int(len(buses_write_og)/2)) - 1 == 0):
                                                    toggle_2x = toggle
                                            else:
                                                self.comb += [
                                                    If(self.rden,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                              If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                 If(self.rd_ptr_minus[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == toggle_2x,
                                                                    If(self.rd_ptr_minus[int(write_div_read) - 1] == toggle,
                                                                       self.rden_int[i].eq(1),
                                                                       self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                    )
                                                                 )
                                                              )
                                                            )
                                                        )
                                                    )
                                                ]
                                                if ((36 + (36*l)) == data_width_read):
                                                    toggle = 1 - toggle
                                                if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1) == 0):
                                                    toggle_2x = toggle
                                                else:
                                                    if (count_loop % ((data_width_read/36) * 2) == 0):
                                                        toggle_2x = toggle_2x + 1
                                        else:
                                            if (clocks_for_output == 1):
                                                self.comb += [
                                                    If(self.rden,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                              If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                    self.rden_int[i].eq(1),
                                                                    self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                              )
                                                            )
                                                        )
                                                    )
                                                ]
                                            else:
                                                self.comb += [
                                                    If(self.rden,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                              If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                    self.rden_int[i].eq(1),
                                                                    self.inter_dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                    else:
                                        self.comb += [
                                            If(self.rden,
                                               If(~self.underflow,
                                                    If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                      If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                            self.rden_int[i].eq(1),
                                                            self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                        )
                                                    )
                                                )
                                            )
                                        ]
                                    # First Word Fall Through Implmentation
                                    if (first_word_fall_through):
                                        if (j_loop == 0):
                                            if (data_width_read == data_width_write):
                                                self.comb += [
                                                    If(~self.rden,
                                                       If(~self.empty_int[i],
                                                          If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                            If(self.rd_ptr >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                            )
                                                          )
                                                       )
                                                    )
                                                ]
                                            else:
                                                if (len(buses_read_og) < len(buses_write_og)):
                                                    if (data_width_read <= 36):
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                    If(self.rd_ptr >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                       If(self.rd_ptr_minus[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == (toggle_2x - 1 if (i - 1) % 2 == 0 else toggle_2x),
                                                                        If(self.rd_ptr_minus[int(write_div_read) - 1] == 1 - toggle,
                                                                         self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read+ 36)].eq(self.dout_int[i])
                                                                       )
                                                                    )
                                                                  )
                                                               )
                                                               )
                                                            )
                                                        ]
                                                    else:
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                    If(self.rd_ptr >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                       If(self.rd_ptr_minus[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == ((1 - toggle) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1) == 0 and (36 + (36*l)) == data_width_read) else (toggle_2x - 1) if (count_loop % ((data_width_read/36) * 2) == 0) else toggle_2x),
                                                                        If(self.rd_ptr_minus[int(write_div_read) - 1] == (1 - toggle if data_width_read == (36 + (36*l)) else toggle),
                                                                         self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                       )
                                                                    )
                                                                  )
                                                               )
                                                               )
                                                            )
                                                        ]
                                                else:
                                                    if (clocks_for_output == 1):
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                    If(self.rd_ptr >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                        self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read)].eq(self.dout_int[i])
                                                                    )
                                                                  )
                                                               )
                                                            )
                                                        ]
                                                    else:
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                    If(self.rd_ptr >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                        self.inter_dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                    )
                                                                  )
                                                               )
                                                            )
                                                        ]
                                                        if (one_time):
                                                            if (clocks_for_output > 2):
                                                                self.sync += [
                                                                    If(self.rd_ptr <= (clocks_for_output - 1 ) - 1,
                                                                       self.rd_ptr.eq(self.rd_ptr + 1)
                                                                       ),
                                                                    If(self.empty,
                                                                        self.prev_empty.eq(1),
                                                                    ),
                                                                    If(self.rden_int_count == int(clocks_for_output - 1) - 1,
                                                                        self.prev_empty.eq(0)
                                                                        ),
                                                                    If(~self.empty,
                                                                       If(self.prev_empty,
                                                                        self.rden_int_count.eq(self.rden_int_count + 1)
                                                                        )
                                                                       )
                                                                ]
                                                            else:
                                                                self.sync += [
                                                                    If(self.rd_ptr <= (clocks_for_output - 1 ) - 1,
                                                                       self.rd_ptr.eq(self.rd_ptr + 1)
                                                                       ),
                                                                    self.prev_empty.eq(self.empty)
                                                                ]
                                                            one_time = 0
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty,
                                                                    If(self.empty != self.prev_empty,
                                                                    self.rden_int[i].eq(1)
                                                                    )
                                                                )
                                                               )
                                                        ]
                                        else:
                                            if (data_width_read == data_width_write):
                                                self.comb += [
                                                    If(~self.rden,
                                                       If(~self.empty_int[i],
                                                          If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                            If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                 self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                            )
                                                       )
                                                       )
                                                    )
                                                ]
                                            else:
                                                if (len(buses_read_og) < len(buses_write_og)):
                                                    if (data_width_read <= 36):
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                    If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                       If(self.rd_ptr_minus[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == (toggle_2x - 1 if (i - 1) % 2 == 0 else toggle_2x),
                                                                            If(self.rd_ptr_minus[int(write_div_read) - 1] == 1 - toggle,
                                                                              self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read+ 36)].eq(self.dout_int[i])
                                                                       )
                                                                    )
                                                               )
                                                                  )
                                                               )
                                                            )
                                                        ]
                                                    else:
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                    If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))),
                                                                       If(self.rd_ptr_minus[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == ((1 - toggle) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1) == 0 and (36 + (36*l)) == data_width_read) else (toggle_2x - 1) if (count_loop % ((data_width_read/36) * 2) == 0) else toggle_2x),
                                                                            If(self.rd_ptr_minus[int(write_div_read) - 1] == (1 - toggle if data_width_read == (36 + (36*l)) else toggle),
                                                                              self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                       )
                                                                    )
                                                               )
                                                                  )
                                                               )
                                                            )
                                                        ]
                                                else:
                                                    if (clocks_for_output == 1):
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                    If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                         self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read)].eq(self.dout_int[i])
                                                                    )
                                                               )
                                                               )
                                                            )
                                                        ]
                                                    else:
                                                        self.comb += [
                                                            If(~self.rden,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                    If(self.rd_ptr > int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output),
                                                                         self.inter_dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                    )
                                                               )
                                                               )
                                                            )
                                                        ]
                                else:
                                    if (j_loop == total_mem - 1):
                                        if (j_loop == 0):
                                            if (data_width_write == data_width_read):
                                                self.sync.rd += [
                                                If(self.rden,
                                                   If(~self.empty,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
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
                                                if (len(buses_read_og) < len(buses_write_og)):
                                                    if (data_width_read <= 36):
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                         If(self.rd_ptr_add[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == toggle_2x,
                                                                            If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
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
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                         If(self.rd_ptr_add[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == toggle_2x,
                                                                            If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
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
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ]
                                                
                                                else:
                                                    self.sync.rd += [
                                                    If(self.rden,
                                                       If(~self.empty,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting) - 1,
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
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
                                            if (data_width_read == data_width_write):
                                                self.sync.rd += [
                                                If(self.rden,
                                                   If(~self.empty,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
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
                                                if (len(buses_read_og) < len(buses_write_og)):
                                                    if(data_width_read <= 36):
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                         If(self.rd_ptr_add[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == toggle_2x,
                                                                         If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
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
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                         If(self.rd_ptr_add[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == toggle_2x,
                                                                         If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
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
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ]
                                                else:
                                                    self.sync.rd += [
                                                    If(self.rden,
                                                       If(~self.empty,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting) - 1,
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting) - 1,
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
                                        if (data_width_write != data_width_read):
                                            if (len(buses_read_og) < len(buses_write_og)):
                                                if(data_width_read <= 36):
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                     If(self.rd_ptr[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == toggle_2x,
                                                                        If(self.rd_ptr[int(write_div_read) - 1] == toggle,
                                                                           self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read+ 36)].eq(self.dout_int[i])
                                                                     )
                                                                )
                                                                  )
                                                              )
                                                           )
                                                        )
                                                    ]
                                                    toggle = 1 - toggle
                                                    if ((i - 1) % 2 == 0):
                                                        toggle_2x = toggle_2x + 1
                                                    if (decimal_to_binary(int(len(buses_write_og)/2)) - 1 == 0):
                                                        toggle_2x = toggle
                                                else:
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                     If(self.rd_ptr[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == toggle_2x,
                                                                        If(self.rd_ptr[int(write_div_read) - 1] == toggle,
                                                                           self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                     )
                                                                )
                                                                  )
                                                              )
                                                           )
                                                        )
                                                    ]
                                                    if ((36 + (36*l)) == data_width_read):
                                                        toggle = 1 - toggle
                                                    if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1) == 0):
                                                        toggle_2x = toggle
                                                    else:
                                                        if (count_loop % ((data_width_read/36) * 2) == 0):
                                                            toggle_2x = toggle_2x + 1
                                            else:
                                                if (clocks_for_output == 1):
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                        self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read)].eq(self.dout_int[i])
                                                                )
                                                              )
                                                           )
                                                        )
                                                    ]
                                                else:
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                        self.inter_dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                )
                                                              )
                                                           )
                                                        )
                                                    ]
                                        else:
                                            self.sync.rd += [
                                                If(self.rd_en_flop1,
                                                   If(~self.underflow,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                self.dout[(36*l):36 + (36*l)].eq(self.dout_int[i])
                                                        )
                                                      )
                                                   )
                                                )
                                            ]
                                    else:
                                        if (j_loop == 0):
                                            if (data_width_read == data_width_write):
                                                self.sync.rd += [
                                                    If(self.rden,
                                                       If(~self.empty,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
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
                                                if (len(buses_read_og) < len(buses_write_og)):
                                                    if(data_width_read <= 36):
                                                        self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                     If(self.rd_ptr_add[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == toggle_2x,
                                                                     If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
                                                                        self.rden_int[i].eq(1)
                                                                )
                                                                .Else(
                                                                self.rden_int[i].eq(0))
                                                              )
                                                              .Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                                    If(self.rd_ptr_add[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == toggle_2x,
                                                                        If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
                                                                           self.rden_int[i].eq(1)
                                                                           ).Else(
                                                                self.rden_int[i].eq(0)
                                                                )
                                                                    ).Else(
                                                                        self.rden_int[i].eq(0)
                                                                    )
                                                              ).Else(
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
                                                        ).Else(
                                                            self.rden_int[i].eq(0)
                                                        )
                                                        ).Else(
                                                            self.rden_int[i].eq(0)
                                                        )
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                     If(self.rd_ptr_add[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == toggle_2x,
                                                                     If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
                                                                        self.rden_int[i].eq(1)
                                                                )
                                                                .Else(
                                                                self.rden_int[i].eq(0))
                                                              )
                                                              .Elif(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending),
                                                                    If(self.rd_ptr_add[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == toggle_2x,
                                                                        If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
                                                                           self.rden_int[i].eq(1)
                                                                           ).Else(
                                                                self.rden_int[i].eq(0)
                                                                )
                                                                    ).Else(
                                                                        self.rden_int[i].eq(0)
                                                                    )
                                                              ).Else(
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
                                                        ).Else(
                                                            self.rden_int[i].eq(0)
                                                        )
                                                        ).Else(
                                                            self.rden_int[i].eq(0)
                                                        )
                                                        ]
                                                else:
                                                    self.sync.rd += [
                                                        If(self.rden,
                                                           If(~self.empty,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting) - 1,
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
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
                                            if (data_width_read == data_width_write):
                                                self.sync.rd += [
                                                If(self.rden,
                                                   If(~self.empty,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
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
                                            else:
                                                if (len(buses_read_og) < len(buses_write_og)):
                                                    if(data_width_read <= 36):
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                         If(self.rd_ptr_add[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == toggle_2x,
                                                                            If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
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
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(self.rden,
                                                               If(~self.empty,
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                      If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting) - 1,
                                                                         If(self.rd_ptr_add[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == toggle_2x,
                                                                            If(self.rd_ptr_add[int(write_div_read) - 1] == toggle,
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
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ).Else(
                                                                self.rden_int[i].eq(0)
                                                            )
                                                            ]
                                                else:
                                                    self.sync.rd += [
                                                    If(self.rden,
                                                       If(~self.empty,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting) - 1,
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting) - 1,
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
                                        if (data_width_write == data_width_read):
                                            self.sync.rd += [
                                                If(self.rd_en_flop1,
                                                   If(~self.underflow,
                                                        If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                        )
                                                      )
                                                   )
                                                )
                                            ]
                                        else:
                                            if (len(buses_read_og) < len(buses_write_og)):
                                                if(data_width_read <= 36):
                                                    self.sync.rd += [
                                                    If(self.rd_en_flop1,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                 If(self.rd_ptr[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == toggle_2x,
                                                                    If(self.rd_ptr[int(write_div_read) - 1] == toggle,
                                                                       self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read+ 36)].eq(self.dout_int[i])
                                                                 )
                                                                 )
                                                            )
                                                          )
                                                       )
                                                    )
                                                    ]
                                                    toggle = 1 - toggle
                                                    if ((i - 1) % 2 == 0):
                                                        toggle_2x = toggle_2x + 1
                                                    if (decimal_to_binary(int(len(buses_write_og)/2)) - 1 == 0):
                                                        toggle_2x = toggle
                                                else:
                                                    self.sync.rd += [
                                                    If(self.rd_en_flop1,
                                                       If(~self.underflow,
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                 If(self.rd_ptr[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == toggle_2x,
                                                                    If(self.rd_ptr[int(write_div_read) - 1] == toggle,
                                                                       self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                 )
                                                                 )
                                                            )
                                                          )
                                                       )
                                                    )
                                                    ]
                                                    if ((36 + (36*l)) == data_width_read):
                                                        toggle = 1 - toggle
                                                    if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1) == 0):
                                                        toggle_2x = toggle
                                                    else:
                                                        if (count_loop % ((data_width_read/36) * 2) == 0):
                                                            toggle_2x = toggle_2x + 1
                                            else:
                                                if (clocks_for_output == 1):
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                        self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read)].eq(self.dout_int[i])
                                                                     )
                                                                )
                                                              )
                                                           )
                                                        ]
                                                else:
                                                    self.sync.rd += [
                                                        If(self.rd_en_flop1,
                                                           If(~self.underflow,
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                        self.inter_dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                     )
                                                                )
                                                              )
                                                           )
                                                        ]
                                    # First Word Fall Through Implmentation
                                    if (first_word_fall_through):
                                        if (j_loop == total_mem - 1):
                                            if(data_width_write == data_width_read):
                                                self.sync.rd += [
                                                    If(~self.rd_en_flop1,
                                                       If(~self.empty_int[i],
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                            )
                                                          )
                                                       )
                                                    )
                                                ]
                                            else:
                                                if (len(buses_read_og) < len(buses_write_og)):
                                                    if(data_width_read <= 36):
                                                        self.sync.rd += [
                                                        If(~self.rd_en_flop1,
                                                           If(~self.empty_int[i],
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                    If(self.rd_ptr[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == (toggle_2x - 1 if (i - 1) % 2 == 0 else toggle_2x),
                                                                       If(self.rd_ptr[int(write_div_read) - 1] == 1 - toggle,
                                                                        self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read+ 36)].eq(self.dout_int[i])
                                                                       )
                                                                   )
                                                                )
                                                              )
                                                           )
                                                        )
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                        If(~self.rd_en_flop1,
                                                           If(~self.empty_int[i],
                                                              If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                    If(self.rd_ptr[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == ((1 - toggle) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1) == 0 and (36 + (36*l)) == data_width_read) else (toggle_2x - 1) if (count_loop % ((data_width_read/36) * 2) == 0) else toggle_2x),
                                                                       If(self.rd_ptr[int(write_div_read) - 1] == (1 - toggle if data_width_read == (36 + (36*l)) else toggle),
                                                                        self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                       )
                                                                   )
                                                                )
                                                              )
                                                           )
                                                        )
                                                        ]
                                                else:
                                                    if (clocks_for_output == 1):
                                                        self.sync.rd += [
                                                            If(~self.rd_en_flop1,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                        self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read)].eq(self.dout_int[i])
                                                                    )
                                                                  )
                                                               )
                                                            )
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(~self.rd_en_flop1,
                                                               If(~self.empty_int[i],
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] <= int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                        self.inter_dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                    )
                                                                  )
                                                               )
                                                            )
                                                        ]
                                                        if (one_time):
                                                            if (clocks_for_output > 2):
                                                                self.sync.rd += [
                                                                    If(self.empty,
                                                                        self.prev_empty.eq(1),
                                                                    ),
                                                                    If(self.rden_int_count == int(clocks_for_output - 1) - 1,
                                                                        self.prev_empty.eq(0)
                                                                        ),
                                                                    If(~self.empty,
                                                                       If(self.prev_empty,
                                                                        self.rden_int_count.eq(self.rden_int_count + 1)
                                                                        )
                                                                       ).Else(
                                                                           self.rden_int_count.eq(0)
                                                                       )
                                                                ]
                                                            else:
                                                                self.sync.rd += [
                                                                    If(self.rd_ptr <= (clocks_for_output - 1 ) - 1,
                                                                       self.rd_ptr.eq(self.rd_ptr + 1)
                                                                       ),
                                                                    self.prev_empty.eq(self.empty)
                                                                ]
                                                            self.sync.rd += [If(~self.empty,
                                                                   If(self.din_count <= clocks_for_output,
                                                                        self.din_count.eq(self.din_count + 1)
                                                                        )
                                                                ).Else(
                                                                    self.din_count.eq(0)
                                                                )
                                                            ]
                                                            one_time = 0
                                                        self.sync.rd += [
                                                            If(~self.rden,
                                                               If(~self.empty,
                                                               If(self.empty != self.prev_empty,
                                                               self.rden_int[i].eq(1)
                                                               ).Else(
                                                                self.rden_int[i].eq(0)
                                                               )
                                                               ).Else(
                                                                self.rden_int[i].eq(0)
                                                               )
                                                            )
                                                        ]
                                        else:
                                            if (data_width_write == data_width_read):
                                                self.sync.rd += [
                                                    If(~self.rd_en_flop1,
                                                        If(~self.empty_int[i],
                                                          If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                            If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                )
                                                            )
                                                        )
                                                    )
                                                ]
                                            else:
                                                if (len(buses_read_og) < len(buses_write_og)):
                                                    if (data_width_read <= 36):
                                                        self.sync.rd += [
                                                            If(~self.rd_en_flop1,
                                                                If(~self.empty_int[i],
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                        If(self.rd_ptr[int(write_div_read) - 1 if (decimal_to_binary(int(len(buses_write_og)/2)) - 1) == 0 else int(write_div_read): int(write_div_read) + decimal_to_binary(int(len(buses_write_og)/2)) - 1] == (toggle_2x - 1 if (i - 1) % 2 == 0 else toggle_2x),
                                                                           If(self.rd_ptr[int(write_div_read) - 1] == 1 - toggle,
                                                                            self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read+ 36)].eq(self.dout_int[i])
                                                                       )
                                                                    )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(~self.rd_en_flop1,
                                                                If(~self.empty_int[i],
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))) + int(starting),
                                                                        If(self.rd_ptr[((int(write_div_read) - 1) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)) == 0 else int(write_div_read)): int(write_div_read) + int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1)] == ((1 - toggle) if (int(decimal_to_binary(int((data_width_write/data_width_read)/2)) - 1) == 0 and (36 + (36*l)) == data_width_read) else (toggle_2x - 1) if (count_loop % ((data_width_read/36) * 2) == 0) else toggle_2x),
                                                                           If(self.rd_ptr[int(write_div_read) - 1] == (1 - toggle if data_width_read == (36 + (36*l)) else toggle),
                                                                            self.dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                       )
                                                                    )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                else:
                                                    if (clocks_for_output == 1):
                                                        self.sync.rd += [
                                                            If(~self.rd_en_flop1,
                                                                If(~self.empty_int[i],
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                        self.dout[(36*l) % data_width_read:((36 + (36*l)) % data_width_read)].eq(self.dout_int[i])
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                    else:
                                                        self.sync.rd += [
                                                            If(~self.rd_en_flop1,
                                                                If(~self.empty_int[i],
                                                                  If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] < int((j_loop + 1)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                    If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] >= int((j_loop)*memory*repeat_count*(36/len(buses_read[l % len(buses_read_og)]))/clocks_for_output) + int(starting),
                                                                        self.inter_dout[(36*l) :((36 + (36*l)))].eq(self.dout_int[i])
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        ]
                                                        if (one_time):
                                                            if (clocks_for_output > 2):
                                                                self.sync.rd += [
                                                                    If(self.empty,
                                                                        self.prev_empty.eq(1),
                                                                    ),
                                                                    If(self.rden_int_count == int(clocks_for_output - 1) - 1,
                                                                        self.prev_empty.eq(0)
                                                                        ),
                                                                    If(~self.empty,
                                                                       If(self.prev_empty,
                                                                        self.rden_int_count.eq(self.rden_int_count + 1)
                                                                        )
                                                                       ).Else(
                                                                           self.rden_int_count.eq(0)
                                                                       )
                                                                ]
                                                            else:
                                                                self.sync.rd += [
                                                                    If(self.rd_ptr <= (clocks_for_output - 1 ) - 1,
                                                                       self.rd_ptr.eq(self.rd_ptr + 1)
                                                                       ),
                                                                    self.prev_empty.eq(self.empty)
                                                                ]
                                                            self.sync.rd += [If(~self.empty,
                                                                   If(self.din_count <= clocks_for_output,
                                                                        self.din_count.eq(self.din_count + 1)
                                                                        )
                                                                ).Else(
                                                                    self.din_count.eq(0)
                                                                )
                                                            ]
                                                            one_time = 0
                                                        self.sync.rd += [
                                                            If(~self.rden,
                                                            If(~self.empty,
                                                               If(self.empty != self.prev_empty,
                                                               self.rden_int[i].eq(1)
                                                               ).Else(
                                                                   self.rden_int[i].eq(0)
                                                               )
                                                               ).Else(
                                                                   self.rden_int[i].eq(0)
                                                               )
                                                            )
                                                        ]
                                l = l + 1
                                if (data_width_read >= 36):
                                    if (data_width_write != data_width_read):
                                        if (clocks_for_output > 1):
                                            if (count_loop == repeat_count/(clocks_for_output/len(buses_write_og))):
                                                j_loop = j_loop + 1
                                                l = 0
                                                count_loop = 0
                                        else:
                                            if (count_loop == repeat_count and len(buses_read_og) > len(buses_write_og)):
                                                j_loop = j_loop + 1
                                                l = 0
                                                count_loop = 0
                                            elif((36*l) == data_width_read):
                                                l = 0
                                                # count_loop = 0
                                    else:
                                        if (count_loop == data_36):
                                            j_loop = j_loop + 1
                                            l = 0
                                            count_loop = 0
                                else:
                                    if (data_width_write != data_width_read):
                                        if (count_loop == repeat_count):
                                            j_loop = j_loop + 1
                                            l = 0
                                            count_loop = 0
                                    else:
                                        j_loop = j_loop + 1
                                        l = 0
                                        count_loop = 0

                memory = 1024
                j_loop = 0
                l = 0
                count_loop = 0
                
                # This loop is for write pointers
                for k in range (0, int(mem + (count18K/2)) * math.ceil(data_width_write/36) + 1, math.ceil(data_width_write/36)):
                    # if (total_mem > 1):
                        for i in range (k, k + math.ceil(data_width_write/36)):
                            if (i not in index_array and i < count):
                                count_loop = count_loop + 1
                                # Writing to FIFOs
                                if(SYNCHRONOUS[synchronous]):
                                    if (data_width_write >= data_width_read):
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
                                    else:
                                        self.comb += [
                                            If(self.wren,
                                               If(~self.overflow,
                                                  If(~self.full_int[i],
                                                        If(self.wrt_ptr <= (j_loop + 1)*memory*int((data_width_read/data_width_write)/clocks_for_output),
                                                           If(self.wrt_ptr > (j_loop)*memory*int((data_width_read/data_width_write)/clocks_for_output),
                                                                self.wren_int[i].eq(1)
                                                           )
                                                        )
                                                    )
                                                )
                                            )
                                        ]
                                else:
                                    if (j_loop == total_mem - 1):
                                        if (data_width_write >= data_width_read):
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
                                                    If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory*int((data_width_read/data_width_write)/clocks_for_output)) + int(starting),
                                                       If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory*int((data_width_read/data_width_write)/clocks_for_output)) + int(starting),
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
                                        if (data_width_write >= data_width_read):
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
                                                    If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] < ((j_loop + 1)*memory*int((data_width_read/data_width_write)/clocks_for_output)) + int(starting),
                                                       If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] >= ((j_loop)*memory*int((data_width_read/data_width_write)/clocks_for_output)) + int(starting),
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
                                l = l + 1
                                if (data_width_write >= 36):
                                    if (count_loop == data_36_write):
                                        j_loop = j_loop + 1
                                        l = 0
                                        count_loop = 0
                                else:
                                    j_loop = j_loop + 1
                                    l = 0
                                    count_loop = 0
                        
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
                else:
                    self.sync.rd += [
                        If(self.empty,
                            self.dout.eq(self.last_data)
                        )
                    ]

            # wrt_ptr and rd_ptr to check for number of entries in FIFO
            if(SYNCHRONOUS[synchronous]):
                if (data_width_write >= data_width_read):
                    self.sync += [
                        If(self.rden,
                           If(~self.empty,
                              self.counter.eq(self.counter - 1),
                              self.underflow.eq(0),
                                If(self.rd_ptr == int(data_width_write/data_width_read)*(depth),
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
                else:
                    self.sync += [
                        If(self.rden,
                           If(~self.empty,
                              self.counter.eq((self.counter - int((data_width_read/data_width_write)/clocks_for_output))),
                              self.underflow.eq(0),
                                If(self.rd_ptr == depth,
                                    self.rd_ptr.eq(1)
                                ).Else(
                                    self.rd_ptr.eq(self.rd_ptr + 1)
                                )
                           ).Else(
                               If(~self.underflow,
                                  self.counter.eq(0)
                                  ),
                                self.underflow.eq(1),    # Checking for Underflow
                                self.inter_dout.eq(0)
                            )
                        ).Else(
                                self.underflow.eq(0)
                            )
                    ]
                if (data_width_write >= data_width_read):
                    self.sync += [
                        If(self.wren,
                           If(~self.full,
                                self.counter.eq((self.counter + int(data_width_write/data_width_read))),
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
                                If(~self.overflow,
                                  self.counter.eq(self.counter + clocks_for_output)
                                  ),
                                self.overflow.eq(1) # Checking for Overflow
                            )
                        ).Else(
                                self.overflow.eq(0)
                            )
                    ]
            else:
                if (data_width_write >= data_width_read):
                    self.sync.wrt += [
                        If(self.wren,
                           If(~self.full,
                                self.overflow.eq(0),
                                self.wrt_ptr.eq(self.wrt_ptr + 1),
                                 If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending/(data_width_write/data_width_read)),
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
                if (data_width_write >= data_width_read):
                    self.sync.rd += [
                        If(self.rd_en_flop,
                           If(~self.empty,
                                self.underflow.eq(0),
                                self.rd_ptr.eq(self.rd_ptr + 1),
                                If(self.rd_ptr[0:math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1] == int(ending),
                                    self.rd_ptr[0:math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1].eq(int(starting)),
                                    self.rd_ptr[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1].eq(~self.rd_ptr[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1])
                               )
                           ).Else(
                            # Checking for Underflow
                            self.underflow.eq(1)
                           )
                        ).Else(
                            self.underflow.eq(0)
                        ),
                        # Write Pointer Synchronizers
                        self.wrt_ptr_rd_clk1.eq(self.gray_encoded_wrtptr),
                        self.wrt_ptr_rd_clk2.eq(self.wrt_ptr_rd_clk1)
                    ]
                else:
                    self.sync.rd += [
                        If(self.rd_en_flop,
                           If(~self.empty,
                                self.underflow.eq(0),
                                self.rd_ptr.eq(self.rd_ptr + 1),
                                If(self.rd_ptr[0:math.ceil(math.log2(depth)) + 1] == int((ending)/(data_width_read/data_width_write)*clocks_for_output) + 1,
                                    self.rd_ptr[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                                    self.rd_ptr[math.ceil(math.log2(depth)) + 1].eq(~self.rd_ptr[math.ceil(math.log2(depth)) + 1])
                               )
                           ).Else(
                            # Checking for Underflow
                            self.underflow.eq(1),
                            self.empty_count.eq(0),
                            self.inter_dout.eq(0)
                           )
                        ).Else(
                            self.underflow.eq(0)
                        ),
                        # Write Pointer Synchronizers
                        self.wrt_ptr_rd_clk1.eq(self.gray_encoded_wrtptr),
                        self.wrt_ptr_rd_clk2.eq(self.wrt_ptr_rd_clk1)
                    ]


                # Binary to Gray Code----------------------------------------------------------
                if (data_width_write >= data_width_read):
                    for i in range(0, math.ceil(math.log2((data_width_write/data_width_read)*depth))):
                        self.comb += self.gray_encoded_rdptr[i].eq(self.rd_ptr[i + 1] ^ self.rd_ptr[i])
                    self.comb += self.gray_encoded_rdptr[math.ceil(math.log2((data_width_write/data_width_read)*depth))].eq(self.rd_ptr[math.ceil(math.log2((data_width_write/data_width_read)*depth))])
                    self.comb += self.gray_encoded_rdptr[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1].eq(self.rd_ptr[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1])
                else:
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
                if (data_width_write >= data_width_read):
                    for i in range(0, math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1):
                        expr = self.rd_ptr_wrt_clk2[i]
                        for j in range(i + 1, math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1):
                            expr ^= self.rd_ptr_wrt_clk2[j]
                        self.comb += self.sync_wrtclk_rdptr_binary[i].eq(expr)
                    self.comb += self.sync_wrtclk_rdptr_binary[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1].eq(self.rd_ptr_wrt_clk2[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1])
                else:
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

            # Adding a counter to enable pessimistic full and empty signals to syncrhonous FIFO
            self.pessimistic_empty = Signal(2)
            if (data_width_write >= data_width_read):
                self.pessimistic_full = Signal(int(data_width_write/(data_width_read if data_width_read >= 36 else 36)))

            if(SYNCHRONOUS[synchronous]):
                # Checking if the FIFO is full
                if (data_width_write >= data_width_read):
                    # Checking if the FIFO is full pessismistically
                    self.sync += [
                        If(self.counter <= int(data_width_write/data_width_read)*(depth) + 1,
                           If(self.counter > int(data_width_write/data_width_read)*(depth) - int(data_width_write/(data_width_read if data_width_read >= 36 else 36)),
                           If(self.rden,
                            self.pessimistic_full.eq(self.pessimistic_full + 1)
                           ).Else(
                               self.pessimistic_full.eq(0)
                           )
                           ).Else(
                               self.pessimistic_full.eq(0)
                           )
                        ).Else(
                               self.pessimistic_full.eq(0)
                           )
                    ]
                    self.comb += [
                        If(self.counter >= int(data_width_write/data_width_read)*(depth),
                           self.full.eq(1)
                        ).Elif(self.pessimistic_full <= int(data_width_write/(data_width_read if data_width_read >= 36 else 36) - 1),
                        If(self.pessimistic_full > 0,
                           self.full.eq(1)
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
                else:
                    self.comb += [
                        If(self.counter >= depth,
                           self.full.eq(1)
                        )
                    ]

                    # Checking for Programmable Full
                    if (full_threshold):
                        self.comb += [
                            If(self.counter >= full_value - 1,
                               self.prog_full.eq(1)
                            )
                        ]

                # Checking if the FIFO is empty pessismistically
                self.sync += [
                    If(self.counter > 0,
                       If(self.pessimistic_empty < 2,
                        self.pessimistic_empty.eq(self.pessimistic_empty + 1)
                       )
                    ).Else(
                           self.pessimistic_empty.eq(0)
                       )
                ]

                # Checking if the FIFO is empty
                if (data_width_write >= data_width_read):
                    self.comb += [
                        If(self.counter == 0,
                           self.empty.eq(1)
                           ).Elif(self.pessimistic_empty == 2,
                           self.empty.eq(0)
                           ).Else(
                               self.empty.eq(1)
                           )
                    ]
                else:
                    self.comb += [
                        If(self.counter <= clocks_for_output,
                           self.empty.eq(1)
                           ).Elif(self.pessimistic_empty == 2,
                           self.empty.eq(0)
                           ).Else(
                               self.empty.eq(1)
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
                if (data_width_write > data_width_read):
                    # Checking if the FIFO is full pessismistically
                    self.sync.wrt += [
                        If((self.wrt_pointer_multiple[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1] != self.sync_wrtclk_rdptr_binary[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1]),
                            If(self.rden,
                               If(self.pessimistic_full < int(data_width_write/(data_width_read if data_width_read >= 36 else 36)),
                             self.pessimistic_full.eq(self.pessimistic_full + 1)
                            )
                            ).Else(
                                self.pessimistic_full.eq(0)
                           )
                        ).Else(
                               self.pessimistic_full.eq(0)
                           )
                    ]

                    self.comb += [
                        If((self.wrt_pointer_multiple[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1] != self.sync_wrtclk_rdptr_binary[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1]),
                            If(self.wrt_pointer_multiple[0:math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1] == self.sync_wrtclk_rdptr_binary[0:math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1],
                               self.full.eq(1)
                               ).Elif(self.pessimistic_full <= int(data_width_write/(data_width_read if data_width_read >= 36 else 36) - 1),
                            If(self.pessimistic_full > 0,
                               self.full.eq(1)
                            )
                               )
                        )
                    ]
                elif (data_width_write == data_width_read):
                    self.comb += [
                        If((self.wrt_ptr[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1] != self.sync_wrtclk_rdptr_binary[math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1]),
                            If(self.wrt_ptr[0:math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1] == self.sync_wrtclk_rdptr_binary[0:math.ceil(math.log2((data_width_write/data_width_read)*depth)) + 1],
                               self.full.eq(1)
                               )
                        )
                    ]
                else:
                    self.comb += [
                        If((self.wrt_ptr[math.ceil(math.log2(depth)) + 1] != self.sync_wrtclk_rdptr_binary_multiple[math.ceil(math.log2(depth)) + 1]),
                            If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] == self.sync_wrtclk_rdptr_binary_multiple[0:math.ceil(math.log2(depth)) + 1],
                               self.full.eq(1)
                               )
                            )
                    ]
                
                # Checking if the FIFO is empty pessismistically
                self.sync.rd += [
                    If(self.rd_ptr != self.sync_rdclk_wrtptr_binary,
                       If(self.pessimistic_empty < 2,
                        self.pessimistic_empty.eq(self.pessimistic_empty + 1)
                       )
                    ).Else(
                           self.pessimistic_empty.eq(0)
                       )
                ]

                # Checking if the FIFO is empty
                if (data_width_write > data_width_read):
                    self.comb += [
                        If(self.rd_ptr == self.sync_rdclk_wrtptr_binary_multiple,
                           self.empty.eq(1)
                           ).Elif(self.pessimistic_empty == 2,
                           self.empty.eq(0)
                           ).Else(
                               self.empty.eq(1)
                           )
                    ]
                elif (data_width_write == data_width_read):
                    self.comb += [
                        If(self.rd_ptr == self.sync_rdclk_wrtptr_binary,
                           self.empty.eq(1)
                           ).Elif(self.pessimistic_empty == 2,
                           self.empty.eq(0)
                           ).Else(
                               self.empty.eq(1)
                           )
                    ]
                else:
                    self.comb += [
                        If(self.rd_pointer_multiple == self.sync_rdclk_wrtptr_binary,
                           self.empty.eq(1)
                           ).Elif(self.pessimistic_empty == 2,
                           self.empty.eq(0)
                           ).Else(
                               self.empty.eq(1)
                           )
                    ]
                if (data_width_read > data_width_write):
                    self.sync.wrt += [
                        If(self.wren,
                           If(~self.full,
                            If(self.empty_count < clocks_for_output,
                               self.empty_count.eq(self.empty_count + 1))
                               ))
                    ]
                    self.comb += [
                    If(self.empty_count <= clocks_for_output - 1,
                       self.empty.eq(1))
                ]
                else:
                    self.sync.wrt += [
                        If(self.wren,
                           If(~self.full,
                        If(self.empty_count < 2,
                           self.empty_count.eq(self.empty_count + 1))
                           ))
                    ]
                    self.comb += [
                    If(self.empty_count <= 1,
                       self.empty.eq(1))
                ]

                # Checking for Programmable Full
                if (full_threshold):
                    self.comb += [
                        If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] +  (int(ending/(data_width_write/data_width_read)) - (full_value + int(starting))) - self.sync_wrtclk_rdptr_binary[0:math.ceil(math.log2(depth)) + 1] < (int(ending/(data_width_write/data_width_read)) - (full_value + int(starting))),
                            self.prog_full.eq(1)
                        )
                    ]
                    self.comb += [
                        If(self.full,
                           self.prog_full.eq(1))
                    ]
                    self.comb += [
                        If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] +  (int(ending/(data_width_write/data_width_read)) - (full_value + int(starting))) >= int(ending/(data_width_write/data_width_read)),
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
                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] +  empty_value >= int(ending),
                           self.rd_ptr_reg[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                           If(self.rd_ptr_reg[0:math.ceil(math.log2(depth)) + 1] == self.sync_rdclk_wrtptr_binary[0:math.ceil(math.log2(depth)) + 1],
                           self.prog_empty.eq(1)
                           )
                        ).Else(
                        self.rd_ptr_reg.eq(self.rd_ptr)
                        )
                    ]
                    self.comb += [
                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] +  empty_value - self.sync_rdclk_wrtptr_binary[0:math.ceil(math.log2(depth)) + 1] < empty_value,
                            self.prog_empty.eq(1)
                        )
                    ]
                    self.comb += [
                        If(self.empty,
                           self.prog_empty.eq(1)
                           )
                    ]
            
        # Using Distributed RAM
        else:
            if (SYNCHRONOUS[synchronous]):
                self.submodules.fifo = SyncFIFO(data_width_write, depth, first_word_fall_through)
            else:
                self.submodules.fifo = AsyncFIFOBuffered(data_width_write, depth)
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
                           self.dout.eq(self.last_data)
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
                        If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] == int(ending/(data_width_write/data_width_read)),
                           If(~self.full,
                                self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                                self.wrt_ptr[math.ceil(math.log2(depth)) + 1].eq(~self.wrt_ptr[math.ceil(math.log2(depth)) + 1])
                           )
                        )
                    )
                ]
                self.sync.rd += [
                    If(self.rd_en_flop,
                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] == int(ending),
                           If(~self.empty,
                            self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1].eq(int(starting)),
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
                        If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] +  (int(ending/(data_width_write/data_width_read)) - (full_value + int(starting))) - self.sync_wrtclk_rdptr_binary[0:math.ceil(math.log2(depth)) + 1] < (int(ending/(data_width_write/data_width_read)) - (full_value + int(starting))),
                            self.prog_full.eq(1)
                        )
                    ]
                    self.comb += [
                        If(self.full,
                           self.prog_full.eq(1))
                    ]
                    self.comb += [
                        If(self.wrt_ptr[0:math.ceil(math.log2(depth)) + 1] +  (int(ending/(data_width_write/data_width_read)) - (full_value + int(starting))) >= int(ending/(data_width_write/data_width_read)),
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
                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] +  empty_value >= int(ending),
                           self.rd_ptr_reg[0:math.ceil(math.log2(depth)) + 1].eq(int(starting)),
                           If(self.rd_ptr_reg[0:math.ceil(math.log2(depth)) + 1] == self.sync_rdclk_wrtptr_binary[0:math.ceil(math.log2(depth)) + 1],
                           self.prog_empty.eq(1)
                           )
                        ).Else(
                        self.rd_ptr_reg.eq(self.rd_ptr)
                        )
                    ]
                    self.comb += [
                        If(self.rd_ptr[0:math.ceil(math.log2(depth_read)) + 1] +  empty_value - self.sync_rdclk_wrtptr_binary[0:math.ceil(math.log2(depth)) + 1] < empty_value,
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

