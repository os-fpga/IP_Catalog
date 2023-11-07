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
class OCM(Module):
    def __init__(self, platform, write_width_A, write_width_B, read_width_A, read_width_B, memory_type, common_clk, write_depth_A, read_depth_A, write_depth_B, read_depth_B, bram, file_path, file_extension):
        
        self.write_depth_A  = write_depth_A
        self.write_width_A  = write_width_A
        
        # Get/Check Parameters.
        # ---------------------
        self.logger = logging.getLogger("\tON CHIP MEMORY")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        self.logger.info(f"MEMORY_TYPE      : {memory_type}")
        
        self.logger.info(f"DATA_WIDTH       : {write_width_A}")
        
        self.logger.info(f"WRITE_DEPTH      : {write_depth_A}")
        
        self.logger.info(f"COMMON_CLK       : {common_clk}")
        
        self.logger.info(f"BRAM             : {bram}")
        
        # read depth for Port A
        # read_depth_A    = int((write_depth_A * write_width_A) / read_width_B)
        # print(write_depth_A, read_depth_A)
        # # read_depth_A depends upon Port A
        # if (memory_type == "Single_Port"):
        #     if (write_depth_A > read_depth_A): # assigning greater value to addr_A port
        #         write_depth_A = write_depth_A
        #     else:
        #         write_depth_A = read_depth_A

        # # read_depth_B depends upon Port A
        # elif (memory_type == "Simple_Dual_Port"):
        #     read_depth_B    = int((write_depth_A * write_width_A) / read_width_B)
        #     write_depth_B   = read_depth_B # assigning greater value to addr_A port

        # # read_depth_B depends upon Port B only
        # elif (memory_type == "True_Dual_Port"):
        #     read_depth_B    = int((write_depth_B * write_width_B) / read_width_B)
        #     if (write_depth_A > read_depth_A): # assigning greater value to addr_A port
        #         write_depth_A = write_depth_A
        #     else:
        #         write_depth_A = read_depth_A

        #     if (write_depth_B > read_depth_B): # assigning greater value to addr_B port
        #         write_depth_B = write_depth_B
        #     else:
        #         write_depth_B = read_depth_B
        
        read_depth_B    = int((write_depth_A * write_width_A) / read_width_B)
        
        # Addressing
        self.addr_A    = Signal(math.ceil(math.log2(write_depth_A)))
        self.addr_B    = Signal(math.ceil(math.log2(read_depth_B)))
        
        msb_A = math.ceil(math.log2(write_depth_A))
        msb_B = math.ceil(math.log2(write_depth_B))
        
        # Port A din/dout
        self.din_A     = Signal(write_width_A)
        self.dout_A    = Signal(read_width_A)
        
        # Port B din/dout
        self.din_B     = Signal(write_width_B)
        self.dout_B    = Signal(read_width_B)
        
        # External write/read enables
        self.wen_A        = Signal(1)
        self.ren_A        = Signal(1)
        self.wen_B        = Signal(1)
        self.ren_B        = Signal(1)
        
        # print("Write_A:", write_depth_A,"Write_B", write_depth_B, "Read_A", read_depth_A, "Read_B", read_depth_B)
        
        if (write_depth_A > write_depth_B):
            memory_depth = write_depth_A
        else:
            memory_depth = write_depth_B
        
        if (memory_type == "True_Dual_Port"):
            if (write_width_A > write_width_B):
                memory_width = write_width_A
            else:
                memory_width = write_width_B
        
        else:
            memory_width = write_width_A
        
        print("Depth:", memory_depth,"Width", memory_width)
        
        # OCM Instances.
        # if (write_depth_A % 1024 ==0):
        if (memory_depth == 1024):
            m = math.ceil(memory_width/36)
            n = 1  
        elif (memory_depth == 2048):
            m = math.ceil(memory_width/18)
            n = 1
        elif (memory_depth == 4096):
            m = math.ceil(memory_width/9)
            n = 1
        elif (memory_depth == 8192):
            m = math.ceil(memory_width/4)
            n = 1
        elif (memory_depth == 16384):
            m = math.ceil(memory_width/2)
            n = 1
        elif (memory_depth == 32768):
            m = math.ceil(memory_width/1)
            n = 1
                
        else:
            if (memory_depth > 1024):
                m = memory_depth / 1024
                temp = int(m/1)
                if (temp*1 != m):
                    m = int(m)+1
                else:
                    m = int(m)
            else:
                m = memory_depth / 1024
                m = math.ceil(m)
            if (memory_width > 36):
                n = memory_width / 36
                temp = int(n/1)
                if (temp*1 != n):
                    n = int(n)+1
                else:
                    n = int(n)
            else:
                n = memory_width / 36
                n = math.ceil(n)
                
        self.m = m # vertical memory
        self.n = n # horizontal memory
        
        print("M:", m , "N:", n)
        
        # Write Enables internal
        self.wen_A1       = Signal(m)
        self.wen_B1       = Signal(m)
        
        # Internal read Enables
        self.ren_A1       = Signal(m)
        self.ren_B1       = Signal(m)
        
        # read port signals
        self.bram_out_A = [Signal(32*n) for i in range(m)]
        self.bram_out_B = [Signal(32*n) for i in range(m)]
        
        self.rparity_A  = [Signal(4*n) for i in range(m)]
        self.rparity_B  = [Signal(4*n) for i in range(m)]
        
        ratio_RW = math.ceil(write_width_A/read_width_B)
        
        read_port_B = math.ceil(read_width_B / 36)
        
        # if (m > read_port_B):
            # ratio_RW = m
        # else:
            # ratio_RW = read_port_B
            
        print("Ratio", ratio_RW, m, read_port_B)
        
        
        if (write_depth_A > 1024):
            self.addr_A_reg = Signal(msb_A - 10)
            # self.addr_B_reg = Signal(msb_A - 10)
            if (memory_type != "Single_Port"):
                self.addr_B_reg = Signal(msb_A - 10)
        
        # write enbale mux array
        wen_mux = {}
        
        # Synchronous/ Asynchronous Clock
        if (common_clk == 1):
            clock1 = ClockSignal("sys")
            clock2 = ClockSignal("sys")
        else:
            clock1 = ClockSignal("clk1")
            clock2 = ClockSignal("clk2")
        
        # Block RAM Mapping
        if (bram == 1):
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            # Single Port RAM
            if (memory_type == "Single_Port"):
                y = write_width_A - 36*(n-1)
                if write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]:
                    print("AAA")
                    self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic
                    for i in range(m):
                        if (write_depth_A == 1024):
                            self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][0:16], self.rparity_A[i][0:2], self.bram_out_A[i][16:32], self.rparity_A[i][2:4]))
                        elif (write_depth_A == 2048):
                            self.comb += self.dout_A[(i*18):((i*18)+18)].eq(Cat(self.bram_out_A[i][0:16], self.rparity_A[i][0:2]))
                        elif (write_depth_A == 4096):
                            if write_width_A > 8:
                                if (m == (i+1)):
                                    if (y == i*9):
                                        self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8]))
                                    else:
                                        self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0]))
                                else:
                                    self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0]))
                            else:
                                self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:write_width_A]))
                                
                        elif (write_depth_A == 8192):
                            self.comb += self.dout_A[(i*4):((i*4)+4)].eq(Cat(self.bram_out_A[i][0:4]))
                        elif (write_depth_A == 16384):
                            self.comb += self.dout_A[(i*2):((i*2)+2)].eq(Cat(self.bram_out_A[i][0:2]))
                        elif (write_depth_A == 32768):
                            self.comb += self.dout_A[(i*1):((i*1)+1)].eq(Cat(self.bram_out_A[i][0:1]))
                            
                else:
                    print("BBBB")
                    case1 = {}
                    if write_depth_A < 1024:
                        self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1)))
                    for i in range(m):
                        case1[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                    if (write_depth_A > 1024):
                        self.comb += Case(self.addr_A[10:msb_A], case1)
                    else:
                        self.comb += self.dout_A.eq(Cat(self.bram_out_A[0][0:16], self.rparity_A[0][0:2], self.bram_out_A[0][16:32], self.rparity_A[0][2:4]))
                    # case2 = {}
                    # for i in range(m):
                    #     case2[i] = self.dout_A.eq(Cat(self.bram_out_A[i][0:16], self.rparity_A[i][0:2], self.bram_out_A[i][16:32], self.rparity_A[i][2:4]))
                    # if (write_depth_A > 1024):
                    #     self.comb += Case(self.addr_A_reg[0:msb_A-10], case2)
                    for i in range(m):
                        if write_depth_A > 1024:
                            self.sync += If((self.addr_A == i), self.addr_A_reg.eq(i))
                    if write_depth_A > 1024:
                        for i in range(m):
                            for j in range(n):
                                self.comb += If((self.addr_A_reg == i), self.dout_A[(j*36):(j*36)+36].eq(Cat(self.bram_out_A[i][(j*32):(j*32)+16], self.rparity_A[i][(j*4):(j*4)+2], self.bram_out_A[i][(j*32)+16:(j*32)+32], self.rparity_A[i][(j*4)+2:(j*4)+4])))
                            
                for i in range(n):  # horizontal memory
                    
                    z = write_width_A - 36*(n-1)
                    if (n == (i+1)): # for last bram input data calculations
                        if (z > 34):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], self.din_A[((i*36)+34):((i*36)+36)])
                        elif (z > 18):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], Replicate(0,2))
                        elif (z > 16):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], Replicate(0,2))
                        else:
                            write_data_A   = self.din_A[36*(m-1):write_width_A]
                            w_parity_A     = 0
                    else:
                        if (write_width_A > 36):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], self.din_A[((i*36)+34):((i*36)+36)])
                    
                    # parameters value assignment for write data A
                    if (write_depth_A == 1024):
                        param_write_width_A = 36
                        address = Cat(Replicate(0,5), self.addr_A[0:10])
                    elif (write_depth_A == 2048):
                        param_write_width_A = 18
                        address = Cat(Replicate(0,4), self.addr_A[0:11])
                    elif (write_depth_A == 4096):
                        param_write_width_A = 9
                        address = Cat(Replicate(0,3), self.addr_A[0:12])
                    elif (write_depth_A == 8192):
                        param_write_width_A = 4
                        address = Cat(Replicate(0,2), self.addr_A[0:13])
                    elif (write_depth_A == 16384):
                        param_write_width_A = 2
                        address = Cat(Replicate(0,1), self.addr_A[0:14])
                    elif (write_depth_A == 32768):
                        param_write_width_A = 1
                        address = Cat(Replicate(0,0), self.addr_A[0:15])
                    else:
                        address = Cat(Replicate(0,5), self.addr_A[0:10])
                        if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                            param_write_width_A = 1
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                            param_write_width_A = 2
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                            param_write_width_A = 4
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                            param_write_width_A = 9
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                            param_write_width_A = 18
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                            param_write_width_A = 36
                    
                    for j in range(m): # vertical memory
                        # write enable logic
                        if write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]:
                            wen = self.wen_A1
                        else:
                            wen = self.wen_A1[j]
                            
                        if (write_depth_A == 1024):
                            z = write_width_A - 36*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 34):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+16)], self.din_A[(j*36)+18:((j*36)+34)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+16):((j*36)+18)], self.din_A[((j*36)+34):((j*36)+36)])
                                elif (z > 18):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+16)], self.din_A[(j*36)+18:((j*36)+34)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+16):((j*36)+18)], Replicate(0,2))
                                elif (z > 16):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+16)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+16):((j*36)+18)], Replicate(0,2))
                                else:
                                    write_data_A   = self.din_A[36*(m-1):write_width_A]
                                    w_parity_A     = 0
                            else:
                                if (write_width_A > 36):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+16)], self.din_A[(j*36)+18:((j*36)+34)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+16):((j*36)+18)], self.din_A[((j*36)+34):((j*36)+36)])
                        
                        elif (write_depth_A == 2048):
                            z = write_width_A - 18*(m-1)
                            if (m == (j+1)): # for last bram input data calculations
                                if (z > 16):
                                    write_data_A = self.din_A[(j*18):((j*18)+16)]
                                    w_parity_A   = Cat(self.din_A[(j*18)+16:(j*18)+18], Replicate(0,2))
                                else:
                                    write_data_A = self.din_A[(j*18):((j*18)+16)]
                                    w_parity_A   = Replicate(0,4)
                            else:
                                write_data_A = self.din_A[(j*18):((j*18)+16)]
                                w_parity_A   = Cat(self.din_A[(j*18)+16:(j*18)+18], Replicate(0,2))
                                
                        elif (write_depth_A == 4096):
                            z = write_width_A - 9*(m-1)
                            if write_width_A > 8:
                                if (m == (j+1)):
                                    if (z > 8):
                                        write_data_A = self.din_A[(j*9):((j*9)+8)]
                                        w_parity_A   = self.din_A[(j*9)+8]
                                    else:
                                        write_data_A = self.din_A[(j*9):(j*9)+16]
                                        w_parity_A   = Replicate(0,4)
                                else:
                                    write_data_A = self.din_A[(j*9):((j*9)+8)]
                                    w_parity_A   = self.din_A[(j*9)+8]
                            
                        elif (write_depth_A == 8192):
                            write_data_A = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A   = Replicate(0,4)
                        
                        elif (write_depth_A == 16384):
                            write_data_A = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A   = Replicate(0,4)
                            
                        elif (write_depth_A == 32768):
                            write_data_A = self.din_A[(j*1):((j*1)+1)]
                            w_parity_A   = Replicate(0,4)
                        
                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "SP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("{32768{1'b0}}"),
                        p_INIT_PARITY       = Instance.PreformattedParam("{2048{1'b0}}"),
                        p_WRITE_WIDTH_A     = param_write_width_A,
                        p_READ_WIDTH_A      = param_write_width_A,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_WEN_A     = wen,
                        i_REN_A     = self.ren_A,
                        i_BE_A      = 15, # all ones
                        i_ADDR_A    = address,
                        i_WDATA_A   = write_data_A,
                        i_WPARITY_A = w_parity_A,
                        o_RDATA_A   = self.bram_out_A[j][((i*32)):((i*32)+32)],
                        o_RPARITY_A = self.rparity_A[j][((i*4)):((i*4)+4)]
                        )
                        
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            # Simple Dual Port RAM
            elif (memory_type == "Simple_Dual_Port"):
                if (write_width_A == read_width_B): # Symmetric
                    y = write_width_A - 36*(n-1)
                    if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                        self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic
                        for i in range(m):
                            if (write_depth_A == 1024):
                                self.comb += self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0], self.bram_out_B[i][8:16], self.rparity_B[i][1],
                                                                self.bram_out_B[i][16:24], self.rparity_B[i][2], self.bram_out_B[i][24:32], self.rparity_B[i][3]))
                            if ( write_depth_A == 2048):
                                self.comb += self.dout_B[(i*18):(i*18)+18].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0], self.bram_out_B[i][8:16], self.rparity_B[i][1]))
                            elif (write_depth_A == 4096):
                                if write_width_A > 8:
                                    if (m == (i+1)):
                                        if (y == i*9):
                                            self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8]))
                                        else:
                                            self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0]))
                                    else:
                                        self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0]))
                                else:
                                    self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:write_width_A]))
                            elif (write_depth_A == 8192):
                                self.comb += self.dout_B[(i*4):((i*4)+4)].eq(Cat(self.bram_out_B[i][0:4]))
                            elif (write_depth_A == 16384):
                                self.comb += self.dout_B[(i*2):((i*2)+2)].eq(Cat(self.bram_out_B[i][0:2]))
                            elif (write_depth_A == 32768):
                                self.comb += self.dout_B[(i*1):((i*1)+1)].eq(Cat(self.bram_out_B[i][0:1]))
                    else:
                        print("BB")
                        case_write = {}
                        if write_depth_A < 1024:
                            self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1)))
                        for i in range(m):
                            case_write[i] = self.wen_A1.eq(Cat(Replicate(0,i), self.wen_A))
                        if (write_depth_A > 1024):
                            self.comb += Case(self.addr_A[10:msb_A], case_write)
                        else:
                            self.comb += self.dout_B.eq(Cat(self.bram_out_B[0][0:8], self.rparity_B[0][0], self.bram_out_B[0][8:16], self.rparity_B[0][1],
                                                                self.bram_out_B[0][16:24], self.rparity_B[0][2], self.bram_out_B[0][24:32], self.rparity_B[0][3]))

                        if write_depth_A > 1024:
                            for i in range(m):
                                for j in range(n):
                                    self.comb += If((self.addr_B_reg == i), self.dout_B[(j*36):(j*36)+36].eq(Cat(self.bram_out_B[i][(j*32):(j*32)+16], self.rparity_B[i][(j*4):(j*4)+2], self.bram_out_B[i][(j*32)+16:(j*32)+32], self.rparity_B[i][(j*4)+2:(j*4)+4])))

                        for i in range(m):
                            if write_depth_A > 1024:
                                if common_clk == 1:
                                    self.sync += If((self.addr_B[10:msb_A] == i), self.addr_B_reg.eq(i))
                                else:
                                    self.sync.clk2 += If((self.addr_B[10:msb_A] == i), self.addr_B_reg.eq(i))
                
                else: # Asymmetric
                    if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                        self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic
                        dout_mux = {}
                        ren_mux = {}
                        addr_reg_mux = {}
                        # cases1 = {}
    
                        if (write_width_A > read_width_B):
                            bram_select = math.ceil(write_width_A/read_width_B)
                        else:
                            bram_select = math.ceil(read_width_B/write_width_A)
                            
                        mux_selectline =  int(math.log2(bram_select))
                        
                        print("mux_selectline", mux_selectline, bram_select)
                        # self.comb += If(self.addr_B[int(math.log2(bram_select))-1])
                        
                        # self.comb += If((self.addr_B[int(math.log2(bram_select))-1]), self.ren_B1.eq(Cat(0 ,self.ren_B))).Else(self.ren_B1.eq(self.ren_B))
                        # self.sync += If((self.addr_B[int(math.log2(bram_select))-1] == 0), self.addr_reg_B.eq(0)). Else(self.addr_reg_B.eq(1))
                        
                        
                        
                        self.addr_reg_B   = Signal(m)
                        for i in range(m):
                        # for i in range(math.ceil(ratio_RW/2)):
                            ren_mux[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                            # for j in range(bram_select):
                            if write_depth_A == 1024:
                                dout_mux[i] = self.dout_B.eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0], self.bram_out_B[i][8:16], self.rparity_B[i][1],
                                                                self.bram_out_B[i][16:24], self.rparity_B[i][2], self.bram_out_B[i][24:32], self.rparity_B[i][3]))
                            elif write_depth_A == 2048:
                                dout_mux[i] = self.dout_B.eq(Cat(self.bram_out_B[i][0:8], self.rparity_B[i][0], self.bram_out_B[i][8:16], self.rparity_B[i][1]))
                            elif write_depth_A == 4096:
                                dout_mux[i] = self.dout_B.eq(Cat(self.bram_out_B[i][0:7], self.rparity_B[i][0]))
                            
                            addr_reg_mux[i] = self.addr_reg_B.eq(i)
                        
                        # if write_depth_A == 1024:
                        #     mux_selectline = int(math.log2(m))
                        #     if read_depth_B == 4096:
                        #         self.sync += Case(self.addr_B[1:mux_selectline], addr_reg_mux)
                        
                        self.sync += Case(self.addr_B[mux_selectline], addr_reg_mux)
                        self.comb += Case(self.addr_reg_B, dout_mux)
                        self.comb += Case(self.addr_B[1:mux_selectline], ren_mux)
                            
                        print("WRITE Size", memory_width*memory_depth, "READ Size", read_depth_B*read_width_B)
                    
                for i in range(n):  # horizontal memory
                    z = write_width_A - 36*(n-1)
                    print("N",n, z)
                    if (n == (i+1)): # for last bram input data calculations
                        
                        if (z > 34):
                            print("A")
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], self.din_A[((i*36)+34):((i*36)+36)])
                        elif (z > 18):
                            print("AA")
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], Replicate(0,2))
                        elif (z > 16):
                            print("AAA")
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], Replicate(0,2))
                        else:
                            print("AAAA")
                            write_data_A   = self.din_A[36*(n-1):write_width_A]
                            w_parity_A     = Replicate(0,4)
                    else:
                        print("B")
                        if (write_width_A > 36):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], self.din_A[((i*36)+34):((i*36)+36)])
                    
                    # parameters value assignment for write data A
                    if (write_depth_A == read_depth_B):
                        if (write_depth_A == 1024):
                            param_write_width_A = 36
                            param_read_width_B  = 36
                            address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                            address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                        elif (write_depth_A == 2048):
                            param_write_width_A = 18
                            param_read_width_B  = 18
                            address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                            address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                        elif (write_depth_A == 4096):
                            param_write_width_A = 9
                            param_read_width_B  = 9
                            address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                            address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                        elif (write_depth_A == 8192):
                            param_write_width_A = 4
                            param_read_width_B  = 4
                            address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                            address_B = Cat(Replicate(0,2), self.addr_B[0:13])
                        elif (write_depth_A == 16384):
                            param_write_width_A = 2
                            param_read_width_B  = 2
                            address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                            address_B = Cat(Replicate(0,1), self.addr_B[0:14])
                        elif (write_depth_A == 32768):
                            param_write_width_A = 1
                            param_read_width_B  = 1
                            address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                            address_B = Cat(Replicate(0,0), self.addr_B[0:15])
                            
                        else: # memory size 36x1024 for other configurations
                            address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                            address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                            if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                                param_write_width_A = 1
                                param_read_width_B  = 1
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                                param_write_width_A = 2
                                param_read_width_B  = 2
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                                param_write_width_A = 4
                                param_read_width_B  = 4
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                                param_write_width_A = 9
                                param_read_width_B  = 9
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                                param_write_width_A = 18
                                param_read_width_B  = 18
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                                param_write_width_A = 36
                                param_read_width_B  = 36
                    
                    
                    # print("Write_A:", write_depth_A,"Write_B", write_depth_B, "Read_A", read_depth_A, "Read_B", read_depth_B)
                    else:
                        if (write_depth_A == 1024):
                            param_write_width_A = 36
                            address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                            if (read_depth_B == 1024):
                                address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                            elif (read_depth_B == 2048):
                                address_B = Cat(Replicate(0,5), self.addr_B[1:11])
                            elif (read_depth_B == 4096):
                                address_B = Cat(Replicate(0,4), self.addr_B[0], self.addr_B[2:12])
                            elif (read_depth_B == 8192):
                                address_B = Cat(Replicate(0,3), self.addr_B[0:2], self.addr_B[3:13])
                            elif (read_depth_B == 16384):
                                address_B = Cat(Replicate(0,2), self.addr_B[0:3],  self.addr_B[4:14])
                            elif (read_depth_B == 32768):
                                address_B = Cat(Replicate(0,1), self.addr_B[0:4],  self.addr_B[5:15])
                            else: 
                                address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                        
                        elif (write_depth_A == 2048):
                            param_write_width_A = 18
                            address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                            if (read_depth_B == 1024):
                                address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                            elif (read_depth_B == 2048):
                                address_B = Cat(Replicate(0,5), self.addr_B[1:11])
                            elif (read_depth_B == 4096):
                                address_B = Cat(Replicate(0,4), self.addr_B[0], self.addr_B[2:12])
                            elif (read_depth_B == 8192):
                                address_B = Cat(Replicate(0,4), self.addr_B[2:13])
                            elif (read_depth_B == 16384):
                                address_B = Cat(Replicate(0,3), self.addr_B[0],  self.addr_B[3:14])
                            elif (read_depth_B == 32768):
                                address_B = Cat(Replicate(0,2), self.addr_B[0:2],  self.addr_B[4:15])
                            else: 
                                address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                            
                            
                        elif (write_depth_A == 4096):
                            param_write_width_A = 9
                            address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                        elif (write_depth_A == 8192):
                            param_write_width_A = 4
                            address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                        elif (write_depth_A == 16384):
                            param_write_width_A = 2
                            address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                        elif (write_depth_A == 32768):
                            param_write_width_A = 1
                            address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                            
                        else: # memory size 36x1024 for other configurations
                            address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                            if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                                param_write_width_A = 1
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                                param_write_width_A = 2
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                                param_write_width_A = 4
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                                param_write_width_A = 9
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                                param_write_width_A = 18
                            elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                                param_write_width_A = 36
                        
                        # parameters value assignment for read data B
                        # if (read_depth_B == 1024):
                        #     address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                        # elif (read_depth_B == 2048):
                        #     address_B = Cat(Replicate(0,5), self.addr_B[1:11])
                        # elif (read_depth_B == 4096):
                        #     address_B = Cat(Replicate(0,4), self.addr_B[0], self.addr_B[2:12])
                        # elif (read_depth_B == 8192):
                        #     address_B = Cat(Replicate(0,3), self.addr_B[0:2], self.addr_B[3:13])
                        # elif (read_depth_B == 16384):
                        #     address_B = Cat(Replicate(0,2), self.addr_B[0:3],  self.addr_B[4:14])
                        # elif (read_depth_B == 32768):
                        #     address_B = Cat(Replicate(0,1), self.addr_B[0:4],  self.addr_B[5:15])
                        # else: 
                        #     address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                    
                        # parameters value assignment for read data B
                        if (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                            param_read_width_B = 1
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                            param_read_width_B = 2
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                            param_read_width_B = 4
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                            param_read_width_B = 9
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                            param_read_width_B = 18
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                            param_read_width_B = 36
                    
                    print("READ",read_depth_B, param_read_width_B )
                    print("Write_A:", write_depth_A,"Write_B", write_depth_B, "Read_A", read_depth_A, "Read_B", read_depth_B)
                    
                    for j in range(m): # vertical memory
                        
                        wen_mux[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i))) # creating multiple write enables
                        
                        # read enable logic
                        if (write_depth_A == read_depth_B):
                            if read_depth_B in [1024, 2048, 4096, 8192, 16384, 32768]:
                                ren = self.ren_B
                            else:
                                ren = self.ren_B1[j]
                        else:
                            ren = self.ren_B1[j]
                        
                        # write enable logic
                        if write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]:
                            wen = self.wen_A1
                        else:
                            wen = self.wen_A1[j]
                        
                        if (write_depth_A == 1024):
                            z = write_width_A - 36*(m-1)
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
                                    write_data_A   = self.din_A[36*(m-1):write_width_A]
                                    w_parity_A     = Replicate(0,4)
                            else:
                                if (write_width_A > 36):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], self.din_A[((j*36)+35)])
                        
                        elif (write_depth_A == 2048):
                            z = write_width_A - 18*(m-1)
                            if (m == (j+1)): # for last bram input data calculations
                                if (z > 17):
                                    write_data_A = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A   = Cat(self.din_A[(j*18)+8], self.din_A[(j*18)+17], Replicate(0,2))
                                elif (z > 16):
                                    write_data_A = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A   = Cat(self.din_A[(j*18)+8], Replicate(0,3))
                                elif (z > 9):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], Replicate(0,3))
                                elif (z > 8):
                                    write_data_A   = Cat(self.din_A[(j*18):((j*18)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*18)+8)], Replicate(0,3))
                                else:
                                    write_data_A = self.din_A[(j*18):((j*18)+8)]
                                    w_parity_A   = Replicate(0,4)
                            else:
                                write_data_A = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                w_parity_A   = Cat(self.din_A[(j*18)+8], self.din_A[(j*18)+17], Replicate(0,2))
                                
                        elif (write_depth_A == 4096):
                            z = write_width_A - 9*(m-1)
                            if write_width_A > 8:
                                if (m == (j+1)):
                                    if (z > 8):
                                        write_data_A = self.din_A[(j*9):((j*9)+8)]
                                        w_parity_A   = self.din_A[(j*9)+8]
                                    else:
                                        write_data_A = self.din_A[(j*9):(j*9)+16]
                                        w_parity_A   = Replicate(0,4)
                                else:
                                    write_data_A = self.din_A[(j*9):((j*9)+8)]
                                    w_parity_A   = self.din_A[(j*9)+8]
                            
                        elif (write_depth_A == 8192):
                            write_data_A = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A   = Replicate(0,4)
                        
                        elif (write_depth_A == 16384):
                            write_data_A = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A   = Replicate(0,4)
                            
                        elif (write_depth_A == 32768):
                            write_data_A = self.din_A[(j*1):((j*1)+1)]
                            w_parity_A   = Replicate(0,4)
                        
                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "SDP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("{32768{1'b0}}"),
                        p_INIT_PARITY       = Instance.PreformattedParam("{4096{1'b0}}"),
                        p_WRITE_WIDTH_A     = param_write_width_A,
                        p_READ_WIDTH_B      = param_read_width_B,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_CLK_B     = clock2,
                        i_WEN_A     = wen,
                        i_REN_B     = ren,
                        i_BE_A      = 15, # all ones
                        i_ADDR_A    = address_A,
                        i_ADDR_B    = address_B,
                        i_WDATA_A   = write_data_A,
                        i_WPARITY_A = w_parity_A,
                        o_RDATA_B   = self.bram_out_B[j][((i*32)):((i*32)+32)],
                        o_RPARITY_B = self.rparity_B[j][((i*4)):((i*4)+4)]
                    )
                    
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            # True Dual Port RAM
            elif (memory_type == "True_Dual_Port"):
                y = write_width_A - 36*(n-1)
                if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                    self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic A
                    # self.comb += If((self.wen_B == 1), self.wen_B1.eq(1)) # write enable logic B
                    for i in range(m):
                        if (write_depth_A == 1024):
                            # self.comb += self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[i][0:32]))
                            self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][0:32], self.rparity_A[i][0:2]))
                        elif (write_depth_A == 2048):
                            self.comb += self.dout_A[(i*18):((i*18)+18)].eq(Cat(self.bram_out_A[i][0:16]))
                            # self.comb += self.dout_B[(i*18):((i*18)+18)].eq(Cat(self.bram_out_B[i][0:16]))
                        elif (write_depth_A == 4096):
                            if write_width_A > 8:
                                if (m == (i+1)):
                                    if (y == i*9):
                                        self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8]))
                                        # self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8]))
                                    else:
                                        self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.bram_out_A[i][16]))
                                        # self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.bram_out_B[i][16]))
                                else:
                                    self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.bram_out_A[i][16]))
                                    # self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.bram_out_B[i][16]))
                            else:
                                self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:write_width_A]))
                                # self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:write_width_A]))
                        elif (write_depth_A == 8192):
                            self.comb += self.dout_A[(i*4):((i*4)+4)].eq(Cat(self.bram_out_A[i][0:4]))
                            # self.comb += self.dout_B[(i*4):((i*4)+4)].eq(Cat(self.bram_out_B[i][0:4]))
                        elif (write_depth_A == 16384):
                            self.comb += self.dout_A[(i*2):((i*2)+2)].eq(Cat(self.bram_out_A[i][0:2]))
                            # self.comb += self.dout_B[(i*2):((i*2)+2)].eq(Cat(self.bram_out_B[i][0:2]))
                        elif (write_depth_A == 32768):
                            self.comb += self.dout_A[(i*1):((i*1)+1)].eq(Cat(self.bram_out_A[i][0:1]))
                            # self.comb += self.dout_B[(i*1):((i*1)+1)].eq(Cat(self.bram_out_B[i][0:1]))
                else:
                    case1 = {}
                    case3 = {}
                    if write_depth_A < 1024:
                        self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1)))
                        # self.comb += If((self.wen_B == 1), (self.wen_B1.eq(1)))
                    for i in range(m):
                        case1[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                    
                    for i in range(m):
                        case1[i] = (If((self.wen_A == 1), self.wen_A1.eq(1 << i)))
                        case3[i] =   self.dout_A.eq(self.bram_out_A[i])
                    if (write_depth_A > 1024):
                        self.comb += Case(self.addr_A[10:msb_A], case1)
                        self.comb += Case(self.addr_A_reg[0:msb_A-10], case3)
                    else:
                        self.comb += self.dout_A.eq(self.bram_out_A[0])
                    # case2 = {}
                    # case4 = {}
                    # for i in range(m):
                    #     case2[i] = (If((self.wen_B == 1), self.wen_B1.eq(1 << i)))
                    #     case4[i] =  self.dout_B.eq(self.bram_out_B[i])
                    # if (write_depth_A > 1024):
                        
                    #     self.comb += Case(self.addr_B[10:msb_B], case2)
                    #     self.comb += Case(self.addr_B_reg[0:msb_B-10], case4)
                    # else:
                    #     self.comb += self.dout_B.eq(self.bram_out_B[0])
                    for i in range(m):
                        if write_depth_A > 1024:
                            if common_clk == 1:
                                self.sync += If((self.addr_A[10:msb_A] == i), self.addr_A_reg[0:msb_A-10].eq(i))
                                # self.sync += If((self.addr_B[10:msb_B] == i), self.addr_B_reg[0:msb_A-10].eq(i))
                            else:
                                self.sync.clk1 += If((self.addr_A[10:msb_A] == i), self.addr_A_reg[0:msb_A-10].eq(i))
                                # self.sync.clk2 += If((self.addr_B[10:msb_B] == i), self.addr_B_reg[0:msb_B-10].eq(i))
                
                # Port B Configuration
                y = write_width_B - 36*(n-1)
                if (write_depth_B in [1024, 2048, 4096, 8192, 16384, 32768]):
                    # self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic A
                    self.comb += If((self.wen_B == 1), self.wen_B1.eq(1)) # write enable logic B
                    for i in range(m):
                        if (write_depth_B == 1024):
                            self.comb += self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[i][0:32]))
                            # self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][0:32]))
                        elif (write_depth_B == 2048):
                            # self.comb += self.dout_A[(i*18):((i*18)+18)].eq(Cat(self.bram_out_A[i][0:16]))
                            self.comb += self.dout_B[(i*18):((i*18)+18)].eq(Cat(self.bram_out_B[i][0:16]))
                        elif (write_depth_B == 4096):
                            if write_width_B > 8:
                                if (m == (i+1)):
                                    if (y == i*9):
                                        # self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8]))
                                        self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8]))
                                    else:
                                        # self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.bram_out_A[i][16]))
                                        self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.bram_out_B[i][16]))
                                else:
                                    # self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.bram_out_A[i][16]))
                                    self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.bram_out_B[i][16]))
                            else:
                                # self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:write_width_A]))
                                self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:write_width_A]))
                        elif (write_depth_B == 8192):
                            # self.comb += self.dout_A[(i*4):((i*4)+4)].eq(Cat(self.bram_out_A[i][0:4]))
                            self.comb += self.dout_B[(i*4):((i*4)+4)].eq(Cat(self.bram_out_B[i][0:4]))
                        elif (write_depth_B == 16384):
                            # self.comb += self.dout_A[(i*2):((i*2)+2)].eq(Cat(self.bram_out_A[i][0:2]))
                            self.comb += self.dout_B[(i*2):((i*2)+2)].eq(Cat(self.bram_out_B[i][0:2]))
                        elif (write_depth_B == 32768):
                            # self.comb += self.dout_A[(i*1):((i*1)+1)].eq(Cat(self.bram_out_A[i][0:1]))
                            self.comb += self.dout_B[(i*1):((i*1)+1)].eq(Cat(self.bram_out_B[i][0:1]))
                else:
                    case1 = {}
                    case3 = {}
                    if write_depth_B < 1024:
                        # self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1)))
                        self.comb += If((self.wen_B == 1), (self.wen_B1.eq(1)))
                    # for i in range(m):
                    #     case1[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                    
                    # for i in range(m):
                    #     case1[i] = (If((self.wen_A == 1), self.wen_A1.eq(1 << i)))
                    #     case3[i] =   self.dout_A.eq(self.bram_out_A[i])
                    # if (write_depth_A > 1024):
                        
                    #     self.comb += Case(self.addr_A[10:msb_A], case1)
                    #     self.comb += Case(self.addr_A_reg[0:msb_A-10], case3)
                    # else:
                    #     self.comb += self.dout_A.eq(self.bram_out_A[0])
                    case2 = {}
                    case4 = {}
                    for i in range(m):
                        case2[i] = (If((self.wen_B == 1), self.wen_B1.eq(1 << i)))
                        case4[i] =  self.dout_B.eq(self.bram_out_B[i])
                    if (write_depth_A > 1024):
                        
                        self.comb += Case(self.addr_B[10:msb_B], case2)
                        self.comb += Case(self.addr_B_reg[0:msb_B-10], case4)
                    else:
                        self.comb += self.dout_B.eq(self.bram_out_B[0])
                    for i in range(m):
                        if write_depth_B > 1024:
                            if common_clk == 1:
                                # self.sync += If((self.addr_A[10:msb_A] == i), self.addr_A_reg[0:msb_A-10].eq(i))
                                self.sync += If((self.addr_B[10:msb_B] == i), self.addr_B_reg[0:msb_B-10].eq(i))
                            else:
                                # self.sync.clk1 += If((self.addr_A[10:msb_A] == i), self.addr_A_reg[0:msb_A-10].eq(i))
                                self.sync.clk2 += If((self.addr_B[10:msb_B] == i), self.addr_B_reg[0:msb_B-10].eq(i))
                                
                for i in range(n):  # horizontal memory
                    
                    # Port A Configuration for 36K memory
                    z = write_width_A - 36*(n-1)
                    if (n == (i+1)): # for last bram input data calculations
                        if (z > 34):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], self.din_A[((i*36)+34):((i*36)+36)])
                        elif (z > 18):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], Replicate(0,2))
                        elif (z > 16):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], Replicate(0,2))
                        else:
                            write_data_A   = self.din_A[36*(m-1):write_width_A]
                            w_parity_A     = 0
                    else:
                        if (write_width_A > 36):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+16)], self.din_A[(i*36)+18:((i*36)+34)])
                            w_parity_A     = Cat(self.din_A[((i*36)+16):((i*36)+18)], self.din_A[((i*36)+34):((i*36)+36)])
                    
                    # Port B Configuration for 36K memory
                    z = write_width_B - 36*(n-1)
                    if (n == (i+1)): # for last bram input data calculations
                        if (z > 34):
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+16)], self.din_B[(i*36)+18:((i*36)+34)])
                            w_parity_B     = Cat(self.din_B[((i*36)+16):((i*36)+18)], self.din_B[((i*36)+34):((i*36)+36)])
                        elif (z > 18):
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+16)], self.din_B[(i*36)+18:((i*36)+34)])
                            w_parity_B     = Cat(self.din_B[((i*36)+16):((i*36)+18)], Replicate(0,2))
                        elif (z > 16):
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+16)])
                            w_parity_B     = Cat(self.din_B[((i*36)+16):((i*36)+18)], Replicate(0,2))
                        else:
                            write_data_B   = self.din_B[36*(m-1):write_width_B]
                            w_parity_B     = 0
                    else:
                        if (write_width_B > 36):
                            write_data_B   = Cat(self.din_B[(i*36):((i*36)+16)], self.din_B[(i*36)+18:((i*36)+34)])
                            w_parity_B     = Cat(self.din_B[((i*36)+16):((i*36)+18)], self.din_B[((i*36)+34):((i*36)+36)])
                    
                    # parameters value assignment for write data A
                    if (write_depth_A == 1024):
                        param_write_width_A = 36
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        # address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                    elif (write_depth_A == 2048):
                        param_write_width_A = 18
                        address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                        # address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                    elif (write_depth_A == 4096):
                        param_write_width_A = 9
                        address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                        # address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                    elif (write_depth_A == 8192):
                        param_write_width_A = 4
                        address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                        # address_B = Cat(Replicate(0,2), self.addr_B[0:13])
                    elif (write_depth_A == 16384):
                        param_write_width_A = 2
                        address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                        # address_B = Cat(Replicate(0,1), self.addr_B[0:14])
                    elif (write_depth_A == 32768):
                        param_write_width_A = 1
                        address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                        # address_B = Cat(Replicate(0,0), self.addr_B[0:15])
                        
                    else: # memory size 36x1024 for other configurations
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        # address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                        if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                            param_write_width_A = 1
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                            param_write_width_A = 2
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                            param_write_width_A = 4
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                            param_write_width_A = 9
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                            param_write_width_A = 18
                        elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                            param_write_width_A = 36
                    
                    # parameters value assignment for read data A
                    if (read_depth_A == 1024):
                        param_read_width_A = 36
                        # address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        # address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                    elif (read_depth_A == 2048):
                        param_read_width_A = 18
                        # address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                        # address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                    elif (read_depth_A == 4096):
                        param_read_width_A = 9
                        # address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                        # address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                    elif (read_depth_A == 8192):
                        param_read_width_A = 4
                        # address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                        # address_B = Cat(Replicate(0,2), self.addr_B[0:13])
                    elif (read_depth_A == 16384):
                        param_read_width_A = 2
                        # address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                        # address_B = Cat(Replicate(0,1), self.addr_B[0:14])
                    elif (read_depth_A == 32768):
                        param_read_width_A = 1
                        # address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                        # address_B = Cat(Replicate(0,0), self.addr_B[0:15])
                    else:
                        # address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        # parameters value assignment for read data A
                        if (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                            param_read_width_A = 1
                        elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                            param_read_width_A = 2
                        elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                            param_read_width_A = 4
                        elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                            param_read_width_A = 9
                        elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                            param_read_width_A = 18
                        elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                            param_read_width_A = 36
                        
                        
                    # parameters value assignment for write data B
                    if (write_depth_B == 1024):
                        param_write_width_B = 36
                        # address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                    elif (write_depth_B == 2048):
                        param_write_width_B = 18
                        # address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                        address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                    elif (write_depth_B == 4096):
                        param_write_width_B = 9
                        # address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                        address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                    elif (write_depth_B == 8192):
                        param_write_width_B = 4
                        # address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                        address_B = Cat(Replicate(0,2), self.addr_B[0:13])
                    elif (write_depth_B == 16384):
                        param_write_width_B = 2
                        # address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                        address_B = Cat(Replicate(0,1), self.addr_B[0:14])
                    elif (write_depth_B == 32768):
                        param_write_width_B = 1
                        # address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                        address_B = Cat(Replicate(0,0), self.addr_B[0:15])
                        
                    else: # memory size 36x1024 for other configurations
                        # address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                        if (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                            param_write_width_B = 1
                        elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                            param_write_width_B = 2
                        elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                            param_write_width_B = 4
                        elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                            param_write_width_B = 9
                        elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                            param_write_width_B = 18
                        elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                            param_write_width_B = 36
                    
                    # parameters value assignment for read data B
                    if (read_depth_B == 1024):
                        param_read_width_B = 36
                        # address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                    elif (read_depth_B == 2048):
                        param_read_width_B = 18
                        # address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                        address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                    elif (read_depth_B == 4096):
                        param_read_width_B = 9
                        # address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                        address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                    elif (read_depth_B == 8192):
                        param_read_width_B = 4
                        # address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                        address_B = Cat(Replicate(0,2), self.addr_B[0:13])
                    elif (read_depth_B == 16384):
                        param_read_width_B = 2
                        # address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                        address_B = Cat(Replicate(0,1), self.addr_B[0:14])
                    elif (read_depth_B == 32768):
                        param_read_width_B = 1
                        # address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                        address_B = Cat(Replicate(0,0), self.addr_B[0:15])
                    else:
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                        # parameters value assignment for read data B
                        if (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                            param_read_width_B = 1
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                            param_read_width_B = 2
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                            param_read_width_B = 4
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                            param_read_width_B = 9
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                            param_read_width_B = 18
                        elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                            param_read_width_B = 36
                    
                    for j in range(m): # vertical memory
                        
                        # write enable logic Port A
                        if write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]:
                            wen_A = self.wen_A1
                        else:
                            wen_A = self.wen_A1[j]
                        
                        # Port A Configuration
                        if (write_depth_A == 1024):
                            z = write_width_A - 36*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 34):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+16)], self.din_A[(j*36)+18:((j*36)+34)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+16):((j*36)+18)], self.din_A[((j*36)+34):((j*36)+36)])
                                elif (z > 18):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+16)], self.din_A[(j*36)+18:((j*36)+34)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+16):((j*36)+18)], Replicate(0,2))
                                elif (z > 16):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+16)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+16):((j*36)+18)], Replicate(0,2))
                                else:
                                    write_data_A   = self.din_A[36*(m-1):write_width_A]
                                    w_parity_A     = 0
                            else:
                                if (write_width_A > 36):
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+16)], self.din_A[(j*36)+18:((j*36)+34)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+16):((j*36)+18)], self.din_A[((j*36)+34):((j*36)+36)])
                        
                        elif (write_depth_A == 2048):
                            z = write_width_A - 18*(m-1)
                            if (m == (j+1)): # for last bram input data calculations
                                if (z > 16):
                                    write_data_A = self.din_A[(j*18):((j*18)+16)]
                                    w_parity_A   = Cat(self.din_A[(j*18)+16:(j*18)+18], Replicate(0,2))
                                else:
                                    write_data_A = self.din_A[(j*18):((j*18)+16)]
                                    w_parity_A   = Replicate(0,4)
                            else:
                                write_data_A = self.din_A[(j*18):((j*18)+16)]
                                w_parity_A   = Cat(self.din_A[(j*18)+16:(j*18)+18], Replicate(0,2))
                                
                        elif (write_depth_A == 4096):
                            z = write_width_A - 9*(m-1)
                            if write_width_A > 8:
                                if (m == (j+1)):
                                    if (z > 8):
                                        write_data_A = self.din_A[(j*9):((j*9)+8)]
                                        w_parity_A   = self.din_A[(j*9)+8]
                                    else:
                                        write_data_A = self.din_A[(j*9):(j*9)+16]
                                        w_parity_A   = Replicate(0,4)
                                else:
                                    write_data_A = self.din_A[(j*9):((j*9)+8)]
                                    w_parity_A   = self.din_A[(j*9)+8]
                            
                        elif (write_depth_A == 8192):
                            write_data_A = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A   = Replicate(0,4)
                        
                        elif (write_depth_A == 16384):
                            write_data_A = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A   = Replicate(0,4)
                            
                        elif (write_depth_A == 32768):
                            write_data_A = self.din_A[(j*1):((j*1)+1)]
                            w_parity_A   = Replicate(0,4)
                        
                        # Port B Configuration
                        if (write_depth_B == 1024):
                            z = write_width_B - 36*(m-1)
                            if (m == (j+1)): # for last bram din calculations
                                if (z > 34):
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+16)], self.din_B[(j*36)+18:((j*36)+34)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+16):((j*36)+18)], self.din_B[((j*36)+34):((j*36)+36)])
                                elif (z > 18):
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+16)], self.din_B[(j*36)+18:((j*36)+34)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+16):((j*36)+18)], Replicate(0,2))
                                elif (z > 16):
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+16)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+16):((j*36)+18)], Replicate(0,2))
                                else:
                                    write_data_B   = self.din_B[36*(m-1):write_width_B]
                                    w_parity_B     = 0
                            else:
                                if (write_width_B > 36):
                                    write_data_B   = Cat(self.din_B[(j*36):((j*36)+16)], self.din_B[(j*36)+18:((j*36)+34)])
                                    w_parity_B     = Cat(self.din_B[((j*36)+16):((j*36)+18)], self.din_B[((j*36)+34):((j*36)+36)])
                        
                        elif (write_depth_B == 2048):
                            z = write_width_B - 18*(m-1)
                            if (m == (j+1)): # for last bram input data calculations
                                if (z > 16):
                                    write_data_B = self.din_B[(j*18):((j*18)+16)]
                                    w_parity_B   = Cat(self.din_B[(j*18)+16:(j*18)+18], Replicate(0,2))
                                else:
                                    write_data_B = self.din_B[(j*18):((j*18)+16)]
                                    w_parity_B   = Replicate(0,4)
                            else:
                                write_data_B = self.din_B[(j*18):((j*18)+16)]
                                w_parity_B   = Cat(self.din_B[(j*18)+16:(j*18)+18], Replicate(0,2))
                                
                        elif (write_depth_B == 4096):
                            z = write_width_B - 9*(m-1)
                            if write_width_B > 8:
                                if (m == (j+1)):
                                    if (z > 8):
                                        write_data_B = self.din_B[(j*9):((j*9)+8)]
                                        w_parity_B   = self.din_B[(j*9)+8]
                                    else:
                                        write_data_B = self.din_B[(j*9):(j*9)+16]
                                        w_parity_B   = Replicate(0,4)
                                else:
                                    write_data_B = self.din_B[(j*9):((j*9)+8)]
                                    w_parity_B   = self.din_B[(j*9)+8]
                            
                        elif (write_depth_B == 8192):
                            write_data_B = self.din_B[(j*4):((j*4)+4)]
                            w_parity_B   = Replicate(0,4)
                        
                        elif (write_depth_B == 16384):
                            write_data_B = self.din_B[(j*2):((j*2)+2)]
                            w_parity_B   = Replicate(0,4)
                            
                        elif (write_depth_B == 32768):
                            write_data_B = self.din_B[(j*1):((j*1)+1)]
                            w_parity_B   = Replicate(0,4)
                        
                        # write enable logic Port B
                        if write_depth_B in [1024, 2048, 4096, 8192, 16384, 32768]:
                            wen_B = self.wen_B1
                        else:
                            wen_B = self.wen_B1[j]
                            
                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "TDP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("{32768{1'b0}}"),
                        p_INIT_PARITY       = Instance.PreformattedParam("{2048{1'b0}}"),
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
                        i_BE_A      = 15, # all ones
                        i_BE_B      = 15, # all ones
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
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
        
        # Distributed RAM Mapping
        # --------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------
        # Distributed RAM
        else:
            self.specials.memory = Memory(width=write_width_A, depth=write_depth_A)
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
                    self.port_A = self.memory.get_port(write_capable=True, async_read=True, mode=WRITE_FIRST, has_re=False, clock_domain="clk1")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=False, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="clk2")
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
                    self.port_A = self.memory.get_port(write_capable=True, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="clk1")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=True, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="clk2")
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
        # --------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------
