#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around on chip memory.

import math
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# On Chip Memory ------------------------------------------------------------------------------------------
class OCM_SYM(Module):
    def __init__(self, data_width, memory_type, common_clk, write_depth, bram, file_path, file_extension):
        
        self.write_depth = write_depth
        self.data_width  = data_width
        
        # Get/Check Parameters.
        # ---------------------
        self.logger = logging.getLogger("\tON CHIP MEMORY")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        self.logger.info(f"MEMORY_TYPE      : {memory_type}")
        
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        
        self.logger.info(f"WRITE_DEPTH      : {write_depth}")
        
        self.logger.info(f"COMMON_CLK       : {common_clk}")
        
        self.logger.info(f"BRAM             : {bram}")
        
        self.addr_A    = Signal(math.ceil(math.log2(write_depth)))
        self.addr_B    = Signal(math.ceil(math.log2(write_depth)))
        
        self.din_A     = Signal(data_width)
        self.dout_A    = Signal(data_width)
        
        self.din_B     = Signal(data_width)
        self.dout_B    = Signal(data_width)
        
        # OCM Instances.
        # if (write_depth % 1024 ==0):
        if (write_depth == 1024):
            m = math.ceil(data_width/36)
            n = 1  
        elif (write_depth == 2048):
            m = math.ceil(data_width/18)
            n = 1
        elif (write_depth == 4096):
            m = math.ceil(data_width/9)
            n = 1
        elif (write_depth == 8192):
            m = math.ceil(data_width/4)
            n = 1
        elif (write_depth == 16384):
            m = math.ceil(data_width/2)
            n = 1
        elif (write_depth == 32768):
            m = math.ceil(data_width/1)
            n = 1
                
        else:
            if (write_depth > 1024):
                m = write_depth / 1024
                temp = int(m/1)
                if (temp*1 != m):
                    m = int(m)+1
                else:
                    m = int(m)
            else:
                m = write_depth / 1024
                m = math.ceil(m)
            if (data_width > 36):
                n = data_width / 36
                temp = int(n/1)
                if (temp*1 != n):
                    n = int(n)+1
                else:
                    n = int(n)
            else:
                n = data_width / 36
                n = math.ceil(n)
        self.m = m
        self.n = n
        
        if (bram == 1):
            self.logger.info(f"NUMBER OF BRAMS  : {m*n}")
            
        self.logger.info(f"===================================================")
            
        msb = math.ceil(math.log2(write_depth))
        # Internal Addresses
        self.address_A    = Signal(msb)
        self.address_B    = Signal(msb)
        
        # Write Enables
        self.wen_A1       = Signal(m)
        self.wen_B1       = Signal(m)
        
        # External write/read enables
        self.wen_A        = Signal(1)
        self.ren_A        = Signal(1)
        self.wen_B        = Signal(1)
        self.ren_B        = Signal(1)
        
        # read port signals
        self.bram_out_A = [Signal(32*n) for i in range(m)]
        self.bram_out_B = [Signal(32*n) for i in range(m)]
        self.rparity_A  = [Signal(4*n) for i in range(m)]
        self.rparity_B  = [Signal(4*n) for i in range(m)]
        
        # Registered Address for output logic
        self.addr_A_reg = Signal(m*n)
        self.addr_B_reg = Signal(m*n)
        
        # Synchronous/ Asynchronous Clock
        if (common_clk == 1):
            clock1 = ClockSignal("sys")
            clock2 = ClockSignal("sys")
        else:
            clock1 = ClockSignal("A")
            clock2 = ClockSignal("B")
        
        # BRAM Utilization Logic
        if (bram == 1):
            if (write_depth in [1024, 2048, 4096, 8192, 16384, 32768]):
                # Single Port RAM
                if (memory_type == "Single_Port"):
                    for j in range(n):
                        for i in range(m):
                            if (write_depth <= 1024):
                                self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0], self.bram_out_A[i][8:16], self.rparity_A[i][1],
                                            self.bram_out_A[i][16:24], self.rparity_A[i][2], self.bram_out_A[i][24:32], self.rparity_A[i][3]))
                            elif (write_depth == 2048):
                                self.comb += self.dout_A[(i*18):((i*18)+18)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0], self.bram_out_A[i][8:16], self.rparity_A[i][1]))
                            elif (write_depth == 4096):
                                self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0]))
                            elif (write_depth == 8192):
                                self.comb += self.dout_A[(i*4):((i*4)+4)].eq(Cat(self.bram_out_A[i][0:4]))
                            elif (write_depth == 16384):
                                self.comb += self.dout_A[(i*2):((i*2)+2)].eq(Cat(self.bram_out_A[i][0:2]))
                            elif (write_depth == 32768):
                                self.comb += self.dout_A[(i*1):((i*1)+1)].eq(Cat(self.bram_out_A[i][0:1]))
                            
                # Simple Dual Port RAM
                elif (memory_type == "Simple_Dual_Port"):
                    for j in range(n):
                        for i in range(m):
                            if (write_depth <= 1024):
                                self.comb += self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0], self.bram_out_B[i][8:16], self.rparity_B[i][1],
                                            self.bram_out_B[i][16:24], self.rparity_B[i][2], self.bram_out_B[i][24:32], self.rparity_B[i][3]))
                            elif (write_depth == 2048):
                                self.comb += self.dout_B[(i*18):((i*18)+18)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0], self.bram_out_B[i][8:16], self.rparity_B[i][1]))
                            elif (write_depth == 4096):
                                self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0]))
                            elif (write_depth == 8192):
                                self.comb += self.dout_B[(i*4):((i*4)+4)].eq(Cat(self.bram_out_B[i][0:4]))
                            elif (write_depth == 16384):
                                self.comb += self.dout_B[(i*2):((i*2)+2)].eq(Cat(self.bram_out_B[i][0:2]))
                            elif (write_depth == 32768):
                                self.comb += self.dout_B[(i*1):((i*1)+1)].eq(Cat(self.bram_out_B[i][0:1]))
                
                # True Dual Port RAM
                elif (memory_type == "True_Dual_Port"):
                    for i in range(m):
                        if (write_depth <= 1024):
                            self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0], self.bram_out_A[i][8:16], self.rparity_A[i][1],
                                            self.bram_out_A[i][16:24], self.rparity_A[i][2], self.bram_out_A[i][24:32], self.rparity_A[i][3]))
                            self.comb += self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0], self.bram_out_B[i][8:16], self.rparity_B[i][1],
                                            self.bram_out_B[i][16:24], self.rparity_B[i][2], self.bram_out_B[i][24:32], self.rparity_B[i][3]))
                        elif (write_depth == 2048):
                            self.comb += self.dout_A[(i*18):((i*18)+18)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0], self.bram_out_A[i][8:16], self.rparity_A[i][1]))
                            self.comb += self.dout_B[(i*18):((i*18)+18)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0], self.bram_out_B[i][8:16], self.rparity_B[i][1]))
                        elif (write_depth == 4096):
                            self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0]))
                            self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0]))
                        elif (write_depth > 4096 and write_depth <= 8192):
                            self.comb += self.dout_A[(i*4):((i*4)+4)].eq(Cat(self.bram_out_A[i][0:4]))
                            self.comb += self.dout_B[(i*4):((i*4)+4)].eq(Cat(self.bram_out_B[i][0:4]))
                        elif (write_depth == 16384):
                            self.comb += self.dout_A[(i*2):((i*2)+2)].eq(Cat(self.bram_out_A[i][0:2]))
                            self.comb += self.dout_B[(i*2):((i*2)+2)].eq(Cat(self.bram_out_B[i][0:2]))
                        elif (write_depth == 32768):
                            self.comb += self.dout_A[(i*1):((i*1)+1)].eq(Cat(self.bram_out_A[i][0:1]))
                            self.comb += self.dout_B[(i*1):((i*1)+1)].eq(Cat(self.bram_out_B[i][0:1]))
            else:
                # Single Port RAM
                if (memory_type == "Single_Port"):
                    cases        = {}
                    addr_reg_mux = {}
                    for i in range(m):
                        cases[i] = self.wen_A1.eq(Cat(Replicate(0,i), self.wen_A))
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], cases)
                        for i in range(n):
                            for j in range(m):
                                self.comb += If((self.addr_A_reg == j), self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[j][(i*32)+0:(i*32)+8], self.rparity_A[j][(i*4)+0], self.bram_out_A[j][(i*32)+8:(i*32)+16], self.rparity_A[j][(i*4)+1],
                                            self.bram_out_A[j][(i*32)+16:(i*32)+24], self.rparity_A[j][(i*4)+2], self.bram_out_A[j][(i*32)+24:(i*32)+32], self.rparity_A[j][3])))
                    else:
                        for i in range(n):
                            self.comb += self.dout_A[(i*36)+0:(i*36)+36].eq(Cat(self.bram_out_A[0][(i*32)+0:(i*32)+8], self.rparity_A[0][(i*4)+0], self.bram_out_A[0][(i*32)+8:(i*32)+16], self.rparity_A[0][(i*4)+1],
                                                            self.bram_out_A[0][(i*32)+16:(i*32)+24], self.rparity_A[0][(i*4)+2], self.bram_out_A[0][(i*32)+24:(i*32)+32], self.rparity_A[0][(i*4)+3]))
                    if write_depth > 1024:
                        for i in range(m):
                            addr_reg_mux[i] = self.addr_A_reg.eq(i)
                        self.sync.A += Case(self.addr_A[10:msb], addr_reg_mux)
                
                # Simple Dual Port RAM
                elif (memory_type == "Simple_Dual_Port"):
                    cases = {}
                    addr_reg_mux = {}
                    for i in range(m):
                        cases[i] = self.wen_A1.eq(Cat(Replicate(0,i), self.wen_A))
                        
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], cases)
                        for i in range(n):
                            for j in range(m):
                                self.comb += If((self.addr_B_reg == j), self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[j][(i*32)+0:(i*32)+8], self.rparity_B[j][(i*4)+0], self.bram_out_B[j][(i*32)+8:(i*32)+16], self.rparity_B[j][(i*4)+1],
                                            self.bram_out_B[j][(i*32)+16:(i*32)+24], self.rparity_B[j][(i*4)+2], self.bram_out_B[j][(i*32)+24:(i*32)+32], self.rparity_B[j][3])))
                    else:
                        for i in range(n):
                            self.comb += self.dout_B[(i*36)+0:(i*36)+36].eq(Cat(self.bram_out_B[0][(i*32)+0:(i*32)+8], self.rparity_B[0][(i*4)+0], self.bram_out_B[0][(i*32)+8:(i*32)+16], self.rparity_B[0][(i*4)+1],
                                        self.bram_out_B[0][(i*32)+16:(i*32)+24], self.rparity_B[0][(i*4)+2], self.bram_out_B[0][(i*32)+24:(i*32)+32], self.rparity_B[0][(i*4)+3]))
                    if write_depth > 1024:
                        for i in range(m):
                            addr_reg_mux[i] = self.addr_B_reg.eq(i)
                        if common_clk == 1:
                            self.sync += Case(self.addr_B[10:msb], addr_reg_mux)
                        else:
                            self.sync.B += Case(self.addr_B[10:msb], addr_reg_mux)
                            
                # True Dual Port RAM
                elif (memory_type == "True_Dual_Port"):
                    cases_A        = {}
                    addr_reg_mux_A = {}
                    cases_B        = {}
                    addr_reg_mux_B = {}
                    for i in range(m):
                        cases_A[i] = self.wen_A1.eq(Cat(Replicate(0,i), self.wen_A))
                        cases_B[i] = self.wen_B1.eq(Cat(Replicate(0,i), self.wen_B))
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], cases_A)
                        self.comb += Case(self.addr_B[10:msb], cases_B)
                        for i in range(n):
                            for j in range(m):
                                self.comb += If((self.addr_A_reg == j), self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[j][(i*32)+0:(i*32)+8], self.rparity_A[j][(i*4)+0], self.bram_out_A[j][(i*32)+8:(i*32)+16], self.rparity_A[j][(i*4)+1],
                                            self.bram_out_A[j][(i*32)+16:(i*32)+24], self.rparity_A[j][(i*4)+2], self.bram_out_A[j][(i*32)+24:(i*32)+32], self.rparity_A[j][3])))
                                self.comb += If((self.addr_B_reg == j), self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[j][(i*32)+0:(i*32)+8], self.rparity_B[j][(i*4)+0], self.bram_out_B[j][(i*32)+8:(i*32)+16], self.rparity_B[j][(i*4)+1],
                                            self.bram_out_B[j][(i*32)+16:(i*32)+24], self.rparity_B[j][(i*4)+2], self.bram_out_B[j][(i*32)+24:(i*32)+32], self.rparity_B[j][3])))
                    else:
                        for i in range(n):
                            self.comb += self.dout_A[(i*36)+0:(i*36)+36].eq(Cat(self.bram_out_A[0][(i*32)+0:(i*32)+8], self.rparity_A[0][(i*4)+0], self.bram_out_A[0][(i*32)+8:(i*32)+16], self.rparity_A[0][(i*4)+1],
                                        self.bram_out_A[0][(i*32)+16:(i*32)+24], self.rparity_A[0][(i*4)+2], self.bram_out_A[0][(i*32)+24:(i*32)+32], self.rparity_A[0][(i*4)+3]))
                            self.comb += self.dout_B[(i*36)+0:(i*36)+36].eq(Cat(self.bram_out_B[0][(i*32)+0:(i*32)+8], self.rparity_B[0][(i*4)+0], self.bram_out_B[0][(i*32)+8:(i*32)+16], self.rparity_B[0][(i*4)+1],
                                        self.bram_out_B[0][(i*32)+16:(i*32)+24], self.rparity_B[0][(i*4)+2], self.bram_out_B[0][(i*32)+24:(i*32)+32], self.rparity_B[0][(i*4)+3]))
                    
                    if write_depth > 1024:
                        for i in range(m):
                            addr_reg_mux_A[i] = self.addr_A_reg.eq(i)
                            addr_reg_mux_B[i] = self.addr_B_reg.eq(i)
                        if common_clk == 1:
                            self.sync += Case(self.addr_A[10:msb], addr_reg_mux_A)
                            self.sync += Case(self.addr_B[10:msb], addr_reg_mux_B)
                        else:
                            self.sync.A += Case(self.addr_A[10:msb], addr_reg_mux_A)
                            self.sync.B += Case(self.addr_B[10:msb], addr_reg_mux_B)

            # Single Port RAM
            if (memory_type == "Single_Port"):
                # Number of BRAMS
                for i in range(n):
                    if (n == (i+1)):
                        z = data_width - 36*(n-1)
                        if (z > 35):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                        elif (z > 27):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], Replicate(0,1))
                        elif (z > 26):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], Replicate(0,1))
                        elif (z > 18):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], Replicate(0,2))
                        elif (z > 17):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], Replicate(0,2))
                        elif (z > 9):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], Replicate(0,3))
                        elif (z > 8):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], Replicate(0,3))
                        else:
                            write_data_A   = self.din_A[36*(m-1):data_width]
                            w_parity_A     = Replicate(0,4)
                    else:
                        if (data_width > 36):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                    
                    if (write_depth == 1024):
                        param_write_width_A = 36
                        param_read_width_A  = 36
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                    elif (write_depth == 2048):
                        param_write_width_A = 18
                        param_read_width_A  = 18
                        address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                    elif (write_depth == 4096):
                        param_write_width_A = 9
                        param_read_width_A  = 9
                        address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                    elif (write_depth == 8192):
                        param_write_width_A = 4
                        param_read_width_A  = 4
                        address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                    elif (write_depth == 16384):
                        param_write_width_A = 2
                        param_read_width_A  = 2
                        address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                    elif (write_depth == 32768):
                        param_write_width_A = 1
                        param_read_width_A  = 1
                        address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                    else: # memory size 36x1024 for other configurations
                        param_write_width_A = 36
                        param_read_width_A  = 36
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])

                    for j in range(m):
                        if (write_depth == 1024):
                            z = data_width - 36*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 35):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], self.din_A[((j*36)+35)])
                                elif (z > 27):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], Replicate(0,1))
                                elif (z > 26):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], Replicate(0,1))
                                elif (z > 18):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], Replicate(0,2))
                                elif (z > 17):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], Replicate(0,2))
                                elif (z > 9):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], Replicate(0,3))
                                elif (z > 8):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[36*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                            else:
                                if (data_width > 36):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], self.din_A[((j*36)+35)])

                        elif (write_depth == 2048):
                            z = data_width - 18*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 17):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], self.din_A[((j*18)+17)], Replicate(0,2))
                                elif (z > 9):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], Replicate(0,3))
                                elif (z > 8):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[18*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                            else:
                                if (data_width > 18):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], self.din_A[((j*18)+17)], Replicate(0,2))
                            
                        elif (write_depth == 4096):
                            z = data_width - 9*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 8):
                                    write_data_A   = self.din_A[(j*9):((j*9)+8)]
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[9*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                            else:
                                if (data_width > 9):
                                    write_data_A   = self.din_A[(j*9):((j*9)+8)]
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                            
                        elif (write_depth == 8192):
                            write_data_A    = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A      = Replicate(0,4)
                        
                        elif (write_depth == 16384):
                            write_data_A    = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A      = Replicate(0,4)
                            
                        elif (write_depth == 32768):
                            write_data_A    = self.din_A[(j*1):((j*1)+1)]
                            w_parity_A      = Replicate(0,4)
                            
                        if (write_depth <= 1024 or write_depth in [2048, 4096, 8192, 16384, 32768]):
                            wen = self.wen_A
                        else:
                            wen = self.wen_A1[j]
                        
                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "SP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("{32768{1'b0}}"),
                        p_INIT_PARITY       = Instance.PreformattedParam("{4096{1'b0}}"),
                        p_WRITE_WIDTH_A     = param_write_width_A,
                        p_READ_WIDTH_A      = param_read_width_A,
                        p_WRITE_WIDTH_B     = 36,
                        p_READ_WIDTH_B      = 36,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_CLK_B     = 0,
                        i_WEN_A     = wen,
                        i_WEN_B     = 0,
                        i_REN_A     = self.ren_A,
                        i_REN_B     = 0,
                        i_BE_A      = Replicate(1,4), # all ones
                        i_BE_B      = Replicate(0,4),
                        i_ADDR_A    = address_A,
                        i_ADDR_B    = Replicate(0,15),
                        i_WDATA_A   = write_data_A,
                        i_WDATA_B   = Replicate(0,32),
                        i_WPARITY_A = w_parity_A,
                        i_WPARITY_B = Replicate(0,4),
                        o_RDATA_A   = self.bram_out_A[j][((i*32)):((i*32)+32)],
                        o_RDATA_B   = self.bram_out_B[j][((i*32)):((i*32)+32)],
                        o_RPARITY_A = self.rparity_A[j][((i*4)):((i*4)+4)],
                        o_RPARITY_B = self.rparity_B[j][((i*4)):((i*4)+4)]
                        )

            # Simple Dual Port RAM
            elif (memory_type == "Simple_Dual_Port"):
                y = data_width - 36*(n-1)
                for i in range(n):
                    if (n == (i+1)):
                        z = data_width - 36*(n-1)
                        if (z > 35):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                        elif (z > 27):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], Replicate(0,1))
                        elif (z > 26):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], Replicate(0,1))
                        elif (z > 18):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], Replicate(0,2))
                        elif (z > 17):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], Replicate(0,2))
                        elif (z > 9):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], Replicate(0,3))
                        elif (z > 8):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], Replicate(0,3))
                        else:
                            write_data_A   = self.din_A[36*(m-1):data_width]
                            w_parity_A     = Replicate(0,4)
                    else:
                        if (data_width > 36):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                    
                    if (write_depth == 1024):
                        param_write_width_A = 36
                        param_read_width_B  = 36
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                    elif (write_depth == 2048):
                        param_write_width_A = 18
                        param_read_width_B  = 18
                        address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                        address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                    elif (write_depth == 4096):
                        param_write_width_A = 9
                        param_read_width_B  = 9
                        address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                        address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                    elif (write_depth == 8192):
                        param_write_width_A = 4
                        param_read_width_B  = 4
                        address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                        address_B = Cat(Replicate(0,2), self.addr_B[0:13])
                    elif (write_depth == 16384):
                        param_write_width_A = 2
                        param_read_width_B  = 2
                        address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                        address_B = Cat(Replicate(0,1), self.addr_B[0:14])
                    elif (write_depth == 32768):
                        param_write_width_A = 1
                        param_read_width_B  = 1
                        address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                        address_B = Cat(Replicate(0,0), self.addr_B[0:15])
                    else: # memory size 36x1024 for other configurations
                        param_write_width_A = 36
                        param_read_width_B  = 36
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])

                    for j in range(m):
                        if (write_depth == 1024):
                            z = data_width - 36*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 35):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], self.din_A[((j*36)+35)])
                                elif (z > 27):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], Replicate(0,1))
                                elif (z > 26):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], Replicate(0,1))
                                elif (z > 18):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], Replicate(0,2))
                                elif (z > 17):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], Replicate(0,2))
                                elif (z > 9):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], Replicate(0,3))
                                elif (z > 8):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[36*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                            else:
                                if (data_width > 36):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], self.din_A[((j*36)+35)])

                        elif (write_depth == 2048):
                            z = data_width - 18*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 17):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], self.din_A[((j*18)+17)], Replicate(0,2))
                                elif (z > 9):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], Replicate(0,3))
                                elif (z > 8):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[18*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                            else:
                                if (data_width > 18):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], self.din_A[((j*18)+17)], Replicate(0,2))
                            
                        elif (write_depth == 4096):
                            z = data_width - 9*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 8):
                                    write_data_A   = self.din_A[(j*9):((j*9)+8)]
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[9*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                            else:
                                if (data_width > 9):
                                    write_data_A   = self.din_A[(j*9):((j*9)+8)]
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                            
                        elif (write_depth == 8192):
                            write_data_A    = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A      = Replicate(0,4)
                        
                        elif (write_depth == 16384):
                            write_data_A    = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A      = Replicate(0,4)
                            
                        elif (write_depth == 32768):
                            write_data_A    = self.din_A[(j*1):((j*1)+1)]
                            w_parity_A      = Replicate(0,4)
                            
                        # for j in range(m):
                        if (write_depth <= 1024 or write_depth in [2048, 4096, 8192, 16384, 32768]):
                            wen = self.wen_A
                        else:
                            wen = self.wen_A1[j]

                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "SDP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("{32768{1'b0}}"),
                        p_INIT_PARITY       = Instance.PreformattedParam("{4096{1'b0}}"),
                        p_WRITE_WIDTH_A     = param_write_width_A,
                        p_WRITE_WIDTH_B     = 36,
                        p_READ_WIDTH_A      = 36,
                        p_READ_WIDTH_B      = param_read_width_B,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_CLK_B     = clock2,
                        i_WEN_A     = wen,
                        i_WEN_B     = 0,
                        i_REN_A     = 0,
                        i_REN_B     = self.ren_B,
                        i_BE_A      = Replicate(1,4), # all ones
                        i_BE_B      = Replicate(0,4),
                        i_ADDR_A    = address_A,
                        i_ADDR_B    = address_B,
                        i_WDATA_A   = write_data_A,
                        i_WDATA_B   = Replicate(0,32),
                        i_WPARITY_A = w_parity_A,
                        i_WPARITY_B = Replicate(0,4),
                        o_RDATA_A   = self.bram_out_A[j][((i*32)):((i*32)+32)],
                        o_RDATA_B   = self.bram_out_B[j][((i*32)):((i*32)+32)],
                        o_RPARITY_A = self.rparity_A[j][((i*4)):((i*4)+4)],
                        o_RPARITY_B = self.rparity_B[j][((i*4)):((i*4)+4)]
                    )

            # True Dual Port RAM
            elif (memory_type == "True_Dual_Port"):
                y = data_width - 36*(n-1)
                for i in range(n):
                    if (n == (i+1)):
                        z = data_width - 36*(n-1)
                        if (z > 35):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+8)], self.din_B[(i*36)+9:((i*36)+17)], self.din_B[(i*36)+18:((i*36)+26)], self.din_B[(i*36)+27:((i*36)+35)])
                            w_parity_B     = Cat(self.din_B[((i*36)+8)], self.din_B[((i*36)+17)], self.din_B[((i*36)+26)], self.din_B[((i*36)+35)])
                        elif (z > 27):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], Replicate(0,1))
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+8)], self.din_B[(i*36)+9:((i*36)+17)], self.din_B[(i*36)+18:((i*36)+26)], self.din_B[(i*36)+27:((i*36)+35)])
                            w_parity_B     = Cat(self.din_B[((i*36)+8)], self.din_B[((i*36)+17)], self.din_B[((i*36)+26)], Replicate(0,1))
                        elif (z > 26):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], Replicate(0,1))
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+8)], self.din_B[(i*36)+9:((i*36)+17)], self.din_B[(i*36)+18:((i*36)+26)])
                            w_parity_B     = Cat(self.din_B[((i*36)+8)], self.din_B[((i*36)+17)], self.din_B[((i*36)+26)], Replicate(0,1))
                        elif (z > 18):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], Replicate(0,2))
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+8)], self.din_B[(i*36)+9:((i*36)+17)], self.din_B[(i*36)+18:((i*36)+26)])
                            w_parity_B     = Cat(self.din_B[((i*36)+8)], self.din_B[((i*36)+17)], Replicate(0,2))
                        
                        elif (z > 17):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], Replicate(0,2))
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+8)], self.din_B[(i*36)+9:((i*36)+17)])
                            w_parity_B     = Cat(self.din_B[((i*36)+8)], self.din_B[((i*36)+17)], Replicate(0,2))
                        elif (z > 9):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], Replicate(0,3))
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+8)], self.din_B[(i*36)+9:((i*36)+17)])
                            w_parity_B     = Cat(self.din_B[((i*36)+8)], Replicate(0,3))
                        elif (z > 8):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], Replicate(0,3))
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+8)])
                            w_parity_B     = Cat(self.din_B[((i*36)+8)], Replicate(0,3))
                        else:
                            write_data_A   = self.din_A[36*(m-1):data_width]
                            w_parity_A     = Replicate(0,4)
                            write_data_B   = self.din_B[36*(m-1):data_width]
                            w_parity_B     = Replicate(0,4)
                    else:
                        if (data_width > 36):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+8)], self.din_B[(i*36)+9:((i*36)+17)], self.din_B[(i*36)+18:((i*36)+26)], self.din_B[(i*36)+27:((i*36)+35)])
                            w_parity_B     = Cat(self.din_B[((i*36)+8)], self.din_B[((i*36)+17)], self.din_B[((i*36)+26)], self.din_B[((i*36)+35)])

                    if (write_depth == 1024):
                        param_write_width_A = 36
                        param_read_width_A  = 36
                        param_write_width_B = 36
                        param_read_width_B  = 36
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                    elif (write_depth == 2048):
                        param_write_width_A = 18
                        param_read_width_A  = 18
                        param_write_width_B = 18
                        param_read_width_B  = 18
                        address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                        address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                    elif (write_depth == 4096):
                        param_write_width_A = 9
                        param_read_width_A  = 9
                        param_write_width_B = 9
                        param_read_width_B  = 9
                        address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                        address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                    elif (write_depth == 8192):
                        param_write_width_A = 4
                        param_read_width_A  = 4
                        param_write_width_B = 4
                        param_read_width_B  = 4
                        address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                        address_B = Cat(Replicate(0,2), self.addr_B[0:13])
                    elif (write_depth == 16384):
                        param_write_width_A = 2
                        param_read_width_A  = 2
                        param_write_width_B = 2
                        param_read_width_B  = 2
                        address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                        address_B = Cat(Replicate(0,1), self.addr_B[0:14])
                    elif (write_depth == 32768):
                        param_write_width_A = 1
                        param_read_width_A  = 1
                        param_write_width_B = 1
                        param_read_width_B  = 1
                        address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                        address_B = Cat(Replicate(0,0), self.addr_B[0:15])
                    else: # memory size 36x1024 for other configurations
                        param_write_width_A = 36
                        param_read_width_A  = 36
                        param_write_width_B = 36
                        param_read_width_B  = 36
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])

                    for j in range(m): 
                        if (write_depth == 1024):
                            z = data_width - 36*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 35):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], self.din_A[((j*36)+35)])
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+8)], self.din_B[(j*36)+9:((j*36)+17)], self.din_B[(j*36)+18:((j*36)+26)], self.din_B[(j*36)+27:((j*36)+35)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+8)], self.din_B[((j*36)+17)], self.din_B[((j*36)+26)], self.din_B[((j*36)+35)])
                                elif (z > 27):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], Replicate(0,1))
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+8)], self.din_B[(j*36)+9:((j*36)+17)], self.din_B[(j*36)+18:((j*36)+26)], self.din_B[(j*36)+27:((j*36)+35)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+8)], self.din_B[((j*36)+17)], self.din_B[((j*36)+26)], Replicate(0,1))
                                elif (z > 26):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], Replicate(0,1))
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+8)], self.din_B[(j*36)+9:((j*36)+17)], self.din_B[(j*36)+18:((j*36)+26)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+8)], self.din_B[((j*36)+17)], self.din_B[((j*36)+26)], Replicate(0,1))
                                elif (z > 18):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], Replicate(0,2))
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+8)], self.din_B[(j*36)+9:((j*36)+17)], self.din_B[(j*36)+18:((j*36)+26)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+8)], self.din_B[((j*36)+17)], Replicate(0,2))
                                elif (z > 17):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], Replicate(0,2))
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+8)], self.din_B[(j*36)+9:((j*36)+17)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+8)], self.din_B[((j*36)+17)], Replicate(0,2))
                                elif (z > 9):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], Replicate(0,3))
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+8)], self.din_B[(j*36)+9:((j*36)+17)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+8)], Replicate(0,3))
                                elif (z > 8):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], Replicate(0,3))
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+8)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[36*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                                    write_data_B   = self.din_B[36*(m-1):data_width]
                                    w_parity_B     = Replicate(0,4)
                            else:
                                if (data_width > 36):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], self.din_A[((j*36)+35)])
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+8)], self.din_B[(j*36)+9:((j*36)+17)], self.din_B[(j*36)+18:((j*36)+26)], self.din_B[(j*36)+27:((j*36)+35)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+8)], self.din_B[((j*36)+17)], self.din_B[((j*36)+26)], self.din_B[((j*36)+35)])

                        elif (write_depth == 2048):
                            z = data_width - 18*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 17):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], self.din_A[((j*18)+17)], Replicate(0,2))
                                    write_data_B   = Cat(self.din_B[(j*18):((j*18)+8)], self.din_B[(j*18)+9:((j*18)+17)])
                                    w_parity_B     = Cat(self.din_B[((j*18)+8)], self.din_B[((j*18)+17)], Replicate(0,2))
                                elif (z > 9):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], Replicate(0,3))
                                    write_data_B   = Cat(self.din_B[(j*18):((j*18)+8)], self.din_B[(j*18)+9:((j*18)+17)])
                                    w_parity_B     = Cat(self.din_B[((j*18)+8)], Replicate(0,3))
                                elif (z > 8):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], Replicate(0,3))
                                    write_data_B   = Cat(self.din_B[(j*18):((j*18)+8)])
                                    w_parity_B     = Cat(self.din_B[((j*18)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[18*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                                    write_data_B   = self.din_B[18*(m-1):data_width]
                                    w_parity_B     = Replicate(0,4)
                            else:
                                if (data_width > 18):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], self.din_A[((j*18)+17)], Replicate(0,2))
                                    write_data_B   = Cat(self.din_B[(j*18):((j*18)+8)], self.din_B[(j*18)+9:((j*18)+17)])
                                    w_parity_B     = Cat(self.din_B[((j*18)+8)], self.din_B[((j*18)+17)], Replicate(0,2))
                            
                        elif (write_depth == 4096):
                            z = data_width - 9*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 8):
                                    write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                    write_data_B   = Cat(self.din_B[(j*9):((j*9)+8)])
                                    w_parity_B     = Cat(self.din_B[((j*9)+8)], Replicate(0,3))
                                else:
                                    write_data_A   = self.din_A[9*(m-1):data_width]
                                    w_parity_A     = Replicate(0,4)
                                    write_data_B   = self.din_B[9*(m-1):data_width]
                                    w_parity_B     = Replicate(0,4)
                            else:
                                if (data_width > 9):
                                    write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                    write_data_B   = Cat(self.din_B[(j*9):((j*9)+8)])
                                    w_parity_B     = Cat(self.din_B[((j*9)+8)], Replicate(0,3))
                            
                        elif (write_depth == 8192):
                            write_data_A    = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A      = Replicate(0,4)
                            write_data_B    = self.din_B[(j*4):((j*4)+4)]
                            w_parity_B      = Replicate(0,4)
                        
                        elif (write_depth == 16384):
                            write_data_A    = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A      = Replicate(0,4)
                            write_data_B    = self.din_B[(j*2):((j*2)+2)]
                            w_parity_B      = Replicate(0,4)
                            
                        elif (write_depth == 32768):
                            write_data_A    = self.din_A[(j*1):((j*1)+1)]
                            w_parity_A      = Replicate(0,4)
                            write_data_B    = self.din_B[(j*1):((j*1)+1)]
                            w_parity_B      = Replicate(0,4)
                            
                        # for j in range(m):
                        if (write_depth <= 1024 or write_depth in [2048, 4096, 8192, 16384, 32768]):
                            wen_A = self.wen_A
                            wen_B = self.wen_B
                        else:
                            wen_A = self.wen_A1[j]
                            wen_B = self.wen_B1[j]
                        
                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "TDP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("{32768{1'b0}}"),
                        p_INIT_PARITY       = Instance.PreformattedParam("{4096{1'b0}}"),
                        p_WRITE_WIDTH_A     = param_write_width_A,
                        p_READ_WIDTH_A      = param_read_width_A,
                        p_WRITE_WIDTH_B     = param_write_width_B,
                        p_READ_WIDTH_B      = param_read_width_B,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_CLK_B     = clock2,
                        i_WEN_A     = wen_A,
                        i_WEN_B     = wen_B,
                        i_REN_A     = self.ren_A,
                        i_REN_B     = self.ren_B,
                        i_BE_A      = Replicate(1,4), # all ones
                        i_BE_B      = Replicate(1,4), # all ones
                        i_ADDR_A    = address_A,
                        i_ADDR_B    = address_B,
                        i_WDATA_A   = write_data_A,
                        i_WPARITY_A = w_parity_A,
                        i_WDATA_B   = write_data_B,
                        i_WPARITY_B = w_parity_B,
                        o_RDATA_A   = self.bram_out_A[j][((i*32)):((i*32)+32)],
                        o_RPARITY_A = self.rparity_A[j][((i*4)):((i*4)+4)],
                        o_RDATA_B   = self.bram_out_B[j][((i*32)):((i*32)+32)],
                        o_RPARITY_B = self.rparity_B[j][((i*4)):((i*4)+4)]
                        )
        
        # Distributed RAM
        else:
            self.specials.memory = Memory(width=data_width, depth=write_depth)
            if (memory_type == "Single_Port"):
                self.port = self.memory.get_port(write_capable=True, async_read=False, mode=WRITE_FIRST, has_re=True)
                self.specials += self.port

                self.comb += [
                self.port.adr.eq(self.addr_A),
                self.port.dat_w.eq(self.din_A),
                self.port.re.eq(self.ren_A),
                self.port.we.eq(self.wen_A),
                self.dout_A.eq(self.port.dat_r),
                ]

            elif (memory_type == "Simple_Dual_Port"):
                if (common_clk == 1):
                    self.port_A = self.memory.get_port(write_capable=True, async_read=True, mode=WRITE_FIRST, has_re=False, clock_domain="sys")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=False, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="sys")
                    self.specials += self.port_B
                else:
                    self.port_A = self.memory.get_port(write_capable=True, async_read=True, mode=WRITE_FIRST, has_re=False, clock_domain="A")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=False, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="B")
                    self.specials += self.port_B
                
                self.comb += [
                self.port_A.adr.eq(self.addr_A),
                self.port_B.adr.eq(self.addr_B),
                self.port_A.dat_w.eq(self.din_A),
                self.port_B.re.eq(self.ren_B),
                self.port_A.we.eq(self.wen_A),
                self.dout_B.eq(self.port_B.dat_r),
                ]
                
            elif (memory_type == "True_Dual_Port"):
                if (common_clk == 1):
                    self.port_A = self.memory.get_port(write_capable=True, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="sys")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=True, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="sys")
                    self.specials += self.port_B
                else:
                    self.port_A = self.memory.get_port(write_capable=True, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="A")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=True, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="B")
                    self.specials += self.port_B

                self.comb += [
                self.port_A.adr.eq(self.addr_A),
                self.port_A.dat_w.eq(self.din_A),
                self.port_A.re.eq(self.ren_A),
                self.port_A.we.eq(self.wen_A),
                self.dout_A.eq(self.port_A.dat_r),
                
                self.port_B.adr.eq(self.addr_B),
                self.port_B.dat_w.eq(self.din_B),
                self.port_B.re.eq(self.ren_B),
                self.port_B.we.eq(self.wen_B),
                self.dout_B.eq(self.port_B.dat_r),
                ]

