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
        read_depth_A    = int((write_depth_A * write_width_A) / read_width_B)
        
        # read_depth_A depends upon Port A
        if (memory_type == "Single_Port"):
            if (write_depth_A > read_depth_A): # assigning greater value to addr_A port
                write_depth_A = write_depth_A
            else:
                write_depth_A = read_depth_A

        # read_depth_B depends upon Port A
        elif (memory_type == "Simple_Dual_Port"):
            read_depth_B    = int((write_depth_A * write_width_A) / read_width_B)
            write_depth_B   = read_depth_B # assigning greater value to addr_A port

        # read_depth_B depends upon Port B only
        elif (memory_type == "True_Dual_Port"):
            read_depth_B    = int((write_depth_B * write_width_B) / read_width_B)
            if (write_depth_A > read_depth_A): # assigning greater value to addr_A port
                write_depth_A = write_depth_A
            else:
                write_depth_A = read_depth_A

            if (write_depth_B > read_depth_B): # assigning greater value to addr_B port
                write_depth_B = write_depth_B
            else:
                write_depth_B = read_depth_B
        
        # Addressing
        self.addr_A    = Signal(math.ceil(math.log2(write_depth_A)))
        self.addr_B    = Signal(math.ceil(math.log2(write_depth_B)))
        
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
        
        # OCM Instances.
        # if (write_depth_A % 1024 ==0):
        if (write_depth_A == 1024):
            m = math.ceil(write_width_A/36)
            n = 1  
        elif (write_depth_A == 2048):
            m = math.ceil(write_width_A/18)
            n = 1
        elif (write_depth_A == 4096):
            m = math.ceil(write_width_A/9)
            n = 1
        elif (write_depth_A == 8192):
            m = math.ceil(write_width_A/4)
            n = 1
        elif (write_depth_A == 16384):
            m = math.ceil(write_width_A/2)
            n = 1
        elif (write_depth_A == 32768):
            m = math.ceil(write_width_A/1)
            n = 1
                
        else:
            if (write_depth_A > 1024):
                m = write_depth_A / 1024
                temp = int(m/1)
                if (temp*1 != m):
                    m = int(m)+1
                else:
                    m = int(m)
            else:
                m = write_depth_A / 1024
                m = math.ceil(m)
            if (write_width_A > 36):
                n = write_width_A / 36
                temp = int(n/1)
                if (temp*1 != n):
                    n = int(n)+1
                else:
                    n = int(n)
            else:
                n = write_width_A / 36
                n = math.ceil(n)
                
        self.m = m # vertical memory
        self.n = n # horizontal memory
        
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
        
        if (write_depth_A > 1024):
            self.addr_A_reg = Signal(msb_A - 10)
            self.addr_B_reg = Signal(msb_B - 10)
        
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
                if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                    self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic
                else:
                    if (write_depth_A > 1024):
                        self.comb += Case(self.addr_A[10:msb_A], wen_mux)
                for i in range(n):  # horizontal memory
                    
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
                        if write_depth_A < 1024:
                            self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                        else:
                            wen_mux[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                        
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
                        i_WEN_A     = self.wen_A1,
                        i_REN_A     = 1,
                        i_BE_A      = 15,
                        i_ADDR_A    = address,
                        i_WDATA_A   = 1,
                        i_WPARITY_A = 1,
                        o_RDATA_A   = self.bram_out_A[j][((i*32)):((i*32)+32)],
                        o_RPARITY_A = self.rparity_A[j][((i*4)):((i*4)+4)]
                        )
                        
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            # Simple Dual Port RAM
            elif (memory_type == "Simple_Dual_Port"):
                y = write_width_A - 36*(n-1)
                if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                    self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic
                    for i in range(m):
                        if (write_depth_A == 1024):
                            self.comb += self.dout_B[(i*36):(i*36)+36].eq(Cat(self.bram_out_B[i][0:16], self.rparity_B[i][0:2], self.bram_out_B[i][16:32], self.rparity_B[i][2:4]))
                        if ( write_depth_A == 2048):
                            self.comb += self.dout_B[(i*18):(i*18)+18].eq(Cat(self.bram_out_B[i][0:16], self.rparity_B[i][0:2]))
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
                    case1 = {}
                    if write_depth_A < 1024:
                        self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1)))
                    for i in range(m):
                        case1[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                    if (write_depth_A > 1024):
                        self.comb += Case(self.addr_A[10:msb_A], case1)
                    else:
                        self.comb += self.dout_B.eq(Cat(self.bram_out_B[0][0:16], self.rparity_B[0][0:2], self.bram_out_B[0][16:32], self.rparity_B[0][2:4]))
                    case2 = {}
                    for i in range(m):
                        case2[i] = self.dout_B.eq(Cat(self.bram_out_B[i][0:16], self.rparity_B[i][0:2], self.bram_out_B[i][16:32], self.rparity_B[i][2:4]))
                    if (write_depth_A > 1024):
                        self.comb += Case(self.addr_B_reg[0:msb_A-10], case2)
                    for i in range(m):
                        if write_depth_A > 1024:
                            if common_clk == 1:
                                self.sync += If((self.addr_B[10:msb_A] == i), self.addr_B_reg[0:msb_A-10].eq(i))
                            else:
                                self.sync.clk2 += If((self.addr_B[10:msb_A] == i), self.addr_B_reg[0:msb_A-10].eq(i))
                    
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
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])
                    elif (write_depth_A == 2048):
                        param_write_width_A = 18
                        address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                        address_B = Cat(Replicate(0,4), self.addr_B[0:11])
                    elif (write_depth_A == 4096):
                        param_write_width_A = 9
                        address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                        address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                    elif (write_depth_A == 8192):
                        param_write_width_A = 4
                        address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                        address_B = Cat(Replicate(0,2), self.addr_B[0:13])
                    elif (write_depth_A == 16384):
                        param_write_width_A = 2
                        address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                        address_B = Cat(Replicate(0,1), self.addr_B[0:14])
                    elif (write_depth_A == 32768):
                        param_write_width_A = 1
                        address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                        address_B = Cat(Replicate(0,0), self.addr_B[0:15])
                        
                    else: # memory size 36x1024 for other configurations
                        address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:10])
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
                        
                        wen_mux[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i))) # creating multiple write enables
                        
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
                        self.specials += Instance("TDP_RAM36K", name= "SDP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("{32768{1'b0}}"),
                        p_INIT_PARITY       = Instance.PreformattedParam("{2048{1'b0}}"),
                        p_WRITE_WIDTH_A     = param_write_width_A,
                        p_READ_WIDTH_B      = param_read_width_B,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_CLK_B     = clock2,
                        i_WEN_A     = wen,
                        i_REN_B     = self.ren_B,
                        i_BE_A      = 15,
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
                if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                    self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic A
                    self.comb += If((self.wen_B == 1), self.wen_B1.eq(1)) # write enable logic B
                for i in range(n):  # horizontal memory
                    for j in range(m): # vertical memory
                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "TDP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("{32768{1'b0}}"),
                        p_INIT_PARITY       = Instance.PreformattedParam("{2048{1'b0}}"),
                        p_WRITE_WIDTH_A     = write_width_A,
                        p_READ_WIDTH_A      = read_width_A,
                        p_WRITE_WIDTH_B     = write_width_B,
                        p_READ_WIDTH_B      = read_width_B,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_CLK_B     = clock2,
                        i_WEN_A     = self.wen_A1,
                        i_WEN_B     = self.wen_B1,
                        i_REN_A     = 1,
                        i_REN_B     = 1,
                        i_BE_A      = 3,
                        i_BE_B      = 3,
                        i_ADDR_A    = 1,
                        i_ADDR_B    = 1,
                        i_WDATA_A   = 1,
                        i_WPARITY_A = 1,
                        i_WDATA_B   = 1,
                        i_WPARITY_B = 1,
                        o_RDATA_A   = 1,
                        o_RPARITY_A = 1,
                        o_RDATA_B   = 1,
                        o_RPARITY_B = 1
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
