#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around on chip memory.

import math
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# On Chip Memory ------------------------------------------------------------------------------------------
class OCM(Module):
    def __init__(self, platform, data_width, memory_type, common_clk, write_depth, bram):

        # Get/Check Parameters.
        # ---------------------
        self.logger = logging.getLogger("\tON CHIP MEMORY")
        
        self.logger.propagate = False
        
        self.logger.info(f"\tMEMORY TYPE      : {memory_type}")
        
        self.logger.info(f"\tDEPTH            : {write_depth}")
        
        self.logger.info(f"\tDATA WIDTH       : {data_width}")
        
        self.logger.info(f"\tCOMMON CLK       : {common_clk}")
        
        self.addr_A    = Signal(math.ceil(math.log2(write_depth)))
        self.addr_B    = Signal(math.ceil(math.log2(write_depth)))
        
        self.din_A     = Signal(data_width)
        self.dout_A    = Signal(data_width)
        
        self.din_B     = Signal(data_width)
        self.dout_B    = Signal(data_width)
        
        MEMORY_SIZE = data_width * write_depth
        
        # OCM Instances.
        if MEMORY_SIZE <= 36864 and (not(32 <= data_width < 36 and write_depth > 1024)):
            n = 1
            m = 1
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
        
        if (bram == 1):
            # Number of Data Out Ports from BRAMS
            self.bram_out_A = [Signal(36*n) for i in range(m)]
            self.bram_out_B = [Signal(36*n) for i in range(m)]

            if (MEMORY_SIZE <= 36864):
                # Single Port RAM
                if (memory_type == "Single_Port"):
                    self.comb += If((self.wen_A == 1), self.wen_A1[0].eq(1)).Else(self.wen_A1[0].eq(0))
                    self.comb += self.dout_A.eq(self.bram_out_A[0])
                # Simple Dual Port RAM
                elif (memory_type == "Simple_Dual_Port"):
                    self.comb += If((self.wen_A == 1), self.wen_A1[0].eq(1)).Else(self.wen_A1[0].eq(0))
                    self.comb += self.dout_B.eq(self.bram_out_B[0])
                # True Dual Port RAM
                elif (memory_type == "True_Dual_Port"):
                    self.comb += If((self.wen_A == 1), self.wen_A1[0].eq(1)).Else(self.wen_A1[0].eq(0))
                    self.comb += If((self.wen_B == 1), self.wen_B1[0].eq(1)).Else(self.wen_B1[0].eq(0))
                    self.comb += self.dout_A.eq(self.bram_out_A[0])
                    self.comb += self.dout_B.eq(self.bram_out_B[0])
                    
            else:
                # Single Port RAM
                if (memory_type == "Single_Port"):
                    self.comb += self.address_A[0:10].eq(self.addr_A[0:10])
                    cases = {}
                    for i in range(m):
                        cases[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i))).Else(self.wen_A1.eq(0))
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], cases)
                    case_output = {}
                    for i in range(m):
                        case_output[i] = self.dout_A.eq(self.bram_out_A[i])
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], case_output)
                    else:
                        self.comb += self.dout_A.eq(self.bram_out_A[0])
                        
                # Simple Dual Port RAM
                elif (memory_type == "Simple_Dual_Port"):
                    self.comb += self.address_A[0:10].eq(self.addr_A[0:10])
                    self.comb += self.address_B[0:10].eq(self.addr_B[0:10])
                    case1 = {}
                    for i in range(m):
                        case1[i] = If((self.wen_A == 1), self.wen_A1.eq(1 << i)).Else(self.wen_A1.eq(0))
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], case1)
                    else:
                        self.comb += self.dout_B.eq(self.bram_out_B[0])
                    case2 = {}
                    for i in range(m):
                        case2[i] = self.dout_B.eq(self.bram_out_B[i])
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_B[10:msb], case2)
                # True Dual Port RAM
                elif (memory_type == "True_Dual_Port"):
                    self.comb += self.address_A[0:10].eq(self.addr_A[0:10])
                    self.comb += self.address_B[0:10].eq(self.addr_B[0:10])
                    case1 = {}
                    for i in range(m):
                        case1[i] = (If((self.wen_A == 1), self.wen_A1.eq(1 << i)).Else(self.wen_A1.eq(0)),
                                    self.dout_A.eq(self.bram_out_A[i]))
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], case1)
                    else:
                        self.comb += self.dout_A.eq(self.bram_out_A[0])
                    case2 = {}
                    for i in range(m):
                        case2[i] = (If((self.wen_B == 1), self.wen_B1.eq(1 << i)).Else(self.wen_B1[i].eq(0)),
                                    self.dout_B.eq(self.bram_out_B[i]))
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_B[10:msb], case2)
                    else:
                        self.comb += self.dout_B.eq(self.bram_out_B[0])

            # Single Port RAM
            if (memory_type == "Single_Port"):
                y = data_width - 36*(n-1)
                # Number of BRAMS
                for i in range(n):
                    # Data Width Calculations.
                    if (n == (i+1)):
                        if (y > 18):
                            write_data_A1   = self.din_A[(i*36):((i*36)+18)]
                            write_data_A2   = Cat(self.din_A[(((i*36)+18)):((i*36)+36)], Replicate(0,(36-y)))
                        else:
                            write_data_A1   = Cat(self.din_A[36*(n-1):data_width], Replicate(0,(18-y)))
                            write_data_A2   = 0
                    else:
                        if (data_width > 36):
                            write_data_A1   = self.din_A[(i*36):((i*36)+18)]
                            write_data_A2   = self.din_A[((i*36)+18):((i*36)+36)]

                    # Mode Bits
                    if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                        w_mode_a1 = "101"
                        w_mode_b1 = "000"
                        w_mode_a2 = "101"
                        w_mode_b2 = "000"
                        r_mode_a1 = "101"
                        r_mode_b1 = "000"
                        r_mode_a2 = "101"
                        r_mode_b2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address = Cat(self.addr_A[0:msb])
                        else:
                            address = Cat(self.address_A[0:10], Replicate(0,5))

                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        w_mode_a1 = "011"
                        w_mode_b1 = "000"
                        w_mode_a2 = "011"
                        w_mode_b2 = "000"
                        r_mode_a1 = "011"
                        r_mode_b1 = "000"
                        r_mode_a2 = "011"
                        r_mode_b2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address = Cat(Replicate(0,1), self.addr_A[0:msb])
                        else:
                            address = Cat(Replicate(0,1), self.address_A[0:10], Replicate(0,4))

                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        w_mode_a1 = "001"
                        w_mode_b1 = "000"
                        w_mode_a2 = "001"
                        w_mode_b2 = "000"
                        r_mode_a1 = "001"
                        r_mode_b1 = "000"
                        r_mode_a2 = "001"
                        r_mode_b2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address = Cat(Replicate(0,2), self.addr_A[0:msb])
                        else:
                            address = Cat(Replicate(0,2), self.address_A[0:10], Replicate(0,3))

                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        w_mode_a1 = "100"
                        w_mode_b1 = "000"
                        w_mode_a2 = "100"
                        w_mode_b2 = "000"
                        r_mode_a1 = "100"
                        r_mode_b1 = "000"
                        r_mode_a2 = "100"
                        r_mode_b2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address = Cat(Replicate(0,3), self.addr_A[0:msb])
                        else:
                            address = Cat(Replicate(0,3), self.address_A[0:10], Replicate(0,2))

                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        w_mode_a1 = "010"
                        w_mode_b1 = "000"
                        w_mode_a2 = "010"
                        w_mode_b2 = "000"
                        r_mode_a1 = "010"
                        r_mode_b1 = "000"
                        r_mode_a2 = "010"
                        r_mode_b2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address = Cat(Replicate(0,4), self.addr_A[0:msb])
                        else:
                            address = Cat(Replicate(0,4), self.address_A[0:10], Replicate(0,1))

                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        w_mode_a1 = "110"
                        w_mode_b1 = "000"
                        w_mode_a2 = "110"
                        w_mode_b2 = "000"
                        r_mode_a1 = "110"
                        r_mode_b1 = "000"
                        r_mode_a2 = "110"
                        r_mode_b2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address = Cat(Replicate(0,5), self.addr_A[0:msb])
                        else:
                            address = Cat(Replicate(0,5), self.address_A[0:10])
                    
                    if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)]) > 8):
                        ben_A = 3
                    else:
                        ben_A = 1

                    mode = int ("0{}{}{}{}00000000000000000000000000000{}{}{}{}000000000000000000000000000".format(r_mode_a1, r_mode_b1, w_mode_a1, w_mode_b1, r_mode_a2, r_mode_b2, w_mode_a2, w_mode_b2))
                    mode_bits = Instance.PreformattedParam("81'b{:d}".format(mode))
                    init_i = Instance.PreformattedParam("36864'hx")

                    for j in range(m):
                        read_data_A1   = self.bram_out_A[j][(i*36):((i*36)+18)]
                        read_data_A2   = self.bram_out_A[j][((i*36)+18):((i*36)+36)]
                        # Module instance.
                        # ----------------
                        self.specials += Instance("RS_TDP36K",
                        # Parameters.
                        # -----------
                        p_INIT_i        = init_i,
                        p_MODE_BITS     = mode_bits,
                        # Clk / Rst.
                        # ----------
                        i_CLK_A1        = ClockSignal(),
                        i_CLK_B1        = 0,
                        i_CLK_A2        = ClockSignal(),
                        i_CLK_B2        = 0,
                        i_WEN_A1        = self.wen_A1[j],
                        i_WEN_B1        = 0,
                        i_REN_A1        = self.ren_A,
                        i_REN_B1        = 0,
                        i_BE_A1         = ben_A,
                        i_BE_B1         = 0,
                        i_ADDR_A1       = address,
                        i_ADDR_B1       = 0,
                        i_WDATA_A1      = write_data_A1,
                        i_WDATA_B1      = 0,
                        o_RDATA_A1      = read_data_A1,
                        i_FLUSH1        = 0,
                        i_WEN_A2        = self.wen_A1[j],
                        i_WEN_B2        = 0,
                        i_REN_A2        = self.ren_A,
                        i_REN_B2        = 0,
                        i_BE_A2         = ben_A,
                        i_BE_B2         = 0,
                        i_ADDR_A2       = address,
                        i_ADDR_B2       = 0,
                        i_WDATA_A2      = write_data_A2,
                        i_WDATA_B2      = 0,
                        o_RDATA_A2      = read_data_A2,
                        i_FLUSH2        = 0
                )

            # Simple Dual Port RAM
            elif (memory_type == "Simple_Dual_Port"):
                y = data_width - 36*(n-1)
                for i in range(n):
                    if (n == (i+1)):
                        if (y > 18):
                            write_data_A1   = Cat(self.din_A[(i*36):((i*36)+18)],  Replicate(0,2))
                            write_data_A2   = Cat(self.din_A[(((i*36)+18)):((i*36)+36)], Replicate(0,(36-y)))
                        else:
                            write_data_A1   = Cat(self.din_A[36*(n-1):data_width], Replicate(0,(18-y)))
                            write_data_A2   = 0
                    else:
                        if (data_width > 36):
                            write_data_A1   = Cat(self.din_A[(i*36):((i*36)+18)], Replicate(0,2))
                            write_data_A2   = Cat(self.din_A[((i*36)+18):((i*36)+36)], Replicate(0,2))

                    # Mode Bits
                    # Port A
                    if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                        w_mode_a1 = "101"
                        w_mode_a2 = "101"
                        r_mode_a1 = "000"
                        r_mode_a2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(self.addr_A[0:msb])
                        else:
                            address_A = Cat(self.address_A[0:10], Replicate(0,5))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        w_mode_a1 = "011"
                        w_mode_a2 = "011"
                        r_mode_a1 = "000"
                        r_mode_a2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,1), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,1), self.address_A[0:10], Replicate(0,4))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        w_mode_a1 = "001"
                        w_mode_a2 = "001"
                        r_mode_a1 = "000"
                        r_mode_a2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,2), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,2), self.address_A[0:10], Replicate(0,3))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        w_mode_a1 = "100"
                        w_mode_a2 = "100"
                        r_mode_a1 = "000"
                        r_mode_a2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,3), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,3), self.address_A[0:10], Replicate(0,2))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        w_mode_a1 = "010"
                        w_mode_a2 = "010"
                        r_mode_a1 = "000"
                        r_mode_a2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,4), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,4), self.address_A[0:10], Replicate(0,1))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        w_mode_a1 = "110"
                        w_mode_a2 = "110"
                        r_mode_a1 = "000"
                        r_mode_a2 = "000"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,5), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,5), self.address_A[0:10])

                    # Port B
                    if (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                        w_mode_b1 = "000"
                        w_mode_b2 = "000"
                        r_mode_b1 = "101"
                        r_mode_b2 = "101"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(self.addr_B[0:msb])
                        else:
                            address_B = Cat(self.address_B[0:10], Replicate(0,5))
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        w_mode_b1 = "000"
                        w_mode_b2 = "000"
                        r_mode_b1 = "011"
                        r_mode_b2 = "011"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,1), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,1), self.address_B[0:10], Replicate(0,4))
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        w_mode_b1 = "000"
                        w_mode_b2 = "000"
                        r_mode_b1 = "001"
                        r_mode_b2 = "001"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,2), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,2), self.address_B[0:10], Replicate(0,3))
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        w_mode_b1 = "000"
                        w_mode_b2 = "000"
                        r_mode_b1 = "100"
                        r_mode_b2 = "100"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,3), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,3), self.address_B[0:10], Replicate(0,2))
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        w_mode_b1 = "000"
                        w_mode_b2 = "000"
                        r_mode_b1 = "010"
                        r_mode_b2 = "010"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,4), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,4), self.address_B[0:10], Replicate(0,1))
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        w_mode_b1 = "000"
                        w_mode_b2 = "000"
                        r_mode_b1 = "110"
                        r_mode_b2 = "110"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,5), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,5), self.address_B[0:10])
                    
                    if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)]) > 8):
                        ben_A = 3
                    else:
                        ben_A = 1

                    mode = int ("0{}{}{}{}00000000000000000000000000000{}{}{}{}000000000000000000000000000".format(r_mode_a1, r_mode_b1, w_mode_a1, w_mode_b1, r_mode_a2, r_mode_b2, w_mode_a2, w_mode_b2))
                    mode_bits = Instance.PreformattedParam("81'b{:d}".format(mode))
                    init_i = Instance.PreformattedParam("36864'hx")

                    for j in range(m): 
                        read_data_B1   = self.bram_out_B[j][(i*36):((i*36)+18)]
                        read_data_B2   = self.bram_out_B[j][((i*36)+18):((i*36)+36)]

                        if (common_clk == 1):
                            # Module instance.
                            # ----------------
                            self.specials += Instance("RS_TDP36K",
                            # Parameters.
                            # -----------
                            p_INIT_i        = init_i,
                            p_MODE_BITS     = mode_bits,
                            # Clk / Rst.
                            # ----------
                            i_CLK_A1        = ClockSignal(),
                            i_CLK_B1        = ClockSignal(),
                            i_CLK_A2        = ClockSignal(),
                            i_CLK_B2        = ClockSignal(),
                            i_WEN_A1        = self.wen_A1[j],
                            i_WEN_B1        = 0,
                            i_REN_A1        = 0,
                            i_REN_B1        = self.ren_B,
                            i_BE_A1         = ben_A,
                            i_BE_B1         = 0,
                            i_ADDR_A1       = address_A,
                            i_ADDR_B1       = address_B,
                            i_WDATA_A1      = write_data_A1,
                            i_WDATA_B1      = 0,
                            o_RDATA_B1      = read_data_B1,
                            i_FLUSH1        = 0,
                            i_WEN_A2        = self.wen_A1[j],
                            i_WEN_B2        = 0,
                            i_REN_A2        = 0,
                            i_REN_B2        = self.ren_B,
                            i_BE_A2         = ben_A,
                            i_BE_B2         = 0,
                            i_ADDR_A2       = address_A,
                            i_ADDR_B2       = address_B,
                            i_WDATA_A2      = write_data_A2,
                            i_WDATA_B2      = 0,
                            o_RDATA_B2      = read_data_B2,
                            i_FLUSH2        = 0
                        )
                        else: 
                            # Module instance.
                            # ----------------
                            self.specials += Instance("RS_TDP36K",
                            # Parameters.
                            # -----------
                            p_INIT_i        = init_i,
                            p_MODE_BITS     = mode_bits,
                            # Clk / Rst.
                            # ----------
                            i_CLK_A1        = ClockSignal("clk1"),
                            i_CLK_B1        = ClockSignal("clk2"),
                            i_CLK_A2        = ClockSignal("clk1"),
                            i_CLK_B2        = ClockSignal("clk2"),
                            i_WEN_A1        = self.wen_A1[j],
                            i_WEN_B1        = 0,
                            i_REN_A1        = 0,
                            i_REN_B1        = self.ren_B,
                            i_BE_A1         = ben_A,
                            i_BE_B1         = 0,
                            i_ADDR_A1       = address_A,
                            i_ADDR_B1       = address_B,
                            i_WDATA_A1      = write_data_A1,
                            i_WDATA_B1      = 0,
                            o_RDATA_B1      = read_data_B1,
                            i_FLUSH1        = 0,
                            i_WEN_A2        = self.wen_A1[j],
                            i_WEN_B2        = 0,
                            i_REN_A2        = 0,
                            i_REN_B2        = self.ren_B,
                            i_BE_A2         = ben_A,
                            i_BE_B2         = 0,
                            i_ADDR_A2       = address_A,
                            i_ADDR_B2       = address_B,
                            i_WDATA_A2      = write_data_A2,
                            i_WDATA_B2      = 0,
                            o_RDATA_B2      = read_data_B2,
                            i_FLUSH2        = 0
                        )

            # True Dual Port RAM
            elif (memory_type == "True_Dual_Port"):
                y = data_width - 36*(n-1)
                for i in range(n):
                    if (n == (i+1)):
                        if (y > 18):
                            write_data_A1   = Cat(self.din_A[(i*36):((i*36)+18)],  Replicate(0,2))
                            write_data_A2   = Cat(self.din_A[(((i*36)+18)):((i*36)+36)], Replicate(0,(36-y)))
                            write_data_B1   = Cat(self.din_B[(i*36):((i*36)+18)],  Replicate(0,2))
                            write_data_B2   = Cat(self.din_B[(((i*36)+18)):((i*36)+36)], Replicate(0,(36-y)))
                        else:
                            write_data_A1   = Cat(self.din_A[36*(n-1):data_width], Replicate(0,(18-y)))
                            write_data_A2   = 0
                            write_data_B1   = Cat(self.din_B[36*(n-1):data_width], Replicate(0,(18-y)))
                            write_data_B2   = 0
                    else:
                        if (data_width > 36):
                            write_data_A1   = Cat(self.din_A[(i*36):((i*36)+18)], Replicate(0,2))
                            write_data_A2   = Cat(self.din_A[((i*36)+18):((i*36)+36)], Replicate(0,2))
                            write_data_B1   = Cat(self.din_B[(i*36):((i*36)+18)], Replicate(0,2))
                            write_data_B2   = Cat(self.din_B[((i*36)+18):((i*36)+36)], Replicate(0,2))

                    # Mode Bits
                    # Port A Write
                    if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                        w_mode_a1 = "101"
                        w_mode_a2 = "101"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(self.addr_A[0:msb])
                        else:
                            address_A = Cat(self.address_A[0:10], Replicate(0,5))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        w_mode_a1 = "011"
                        w_mode_a2 = "011"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,1), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,1), self.address_A[0:10], Replicate(0,4))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        w_mode_a1 = "001"
                        w_mode_a2 = "001"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,2), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,2), self.address_A[0:10], Replicate(0,3))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        w_mode_a1 = "100"
                        w_mode_a2 = "100"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,3), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,3), self.address_A[0:10], Replicate(0,2))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        w_mode_a1 = "010"
                        w_mode_a2 = "010"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,4), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,4), self.address_A[0:10], Replicate(0,1))
                    elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        w_mode_a1 = "110"
                        w_mode_a2 = "110"
                        if (MEMORY_SIZE <= 36864):
                            address_A = Cat(Replicate(0,5), self.addr_A[0:msb])
                        else:
                            address_A = Cat(Replicate(0,5), self.address_A[0:10])

                    # Port A Read
                    if (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                        r_mode_a1 = "101"
                        r_mode_a2 = "101"
                    elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        r_mode_a1 = "011"
                        r_mode_a2 = "011"
                    elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        r_mode_a1 = "001"
                        r_mode_a2 = "001"
                    elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        r_mode_a1 = "100"
                        r_mode_a2 = "100"
                    elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        r_mode_a1 = "010"
                        r_mode_a2 = "010"
                    elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        r_mode_a1 = "110"
                        r_mode_a2 = "110"

                    # Port B Write
                    if (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                        w_mode_b1 = "101"
                        w_mode_b2 = "101"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(self.addr_B[0:msb])
                        else:
                            address_B = Cat(self.address_B[0:10], Replicate(0,5))
                    elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        w_mode_b1 = "011"
                        w_mode_b2 = "011"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,1), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,1), self.address_B[0:10], Replicate(0,4))
                    elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        w_mode_b1 = "001"
                        w_mode_b2 = "001"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,2), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,2), self.address_B[0:10], Replicate(0,3))
                    elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        w_mode_b1 = "100"
                        w_mode_b2 = "100"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,3), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,3), self.address_B[0:10], Replicate(0,2))
                    elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        w_mode_b1 = "010"
                        w_mode_b2 = "010"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,4), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,4), self.address_B[0:10], Replicate(0,1))
                    elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        w_mode_b1 = "110"
                        w_mode_b2 = "110"
                        if (MEMORY_SIZE <= 36864):
                            address_B = Cat(Replicate(0,5), self.addr_B[0:msb])
                        else:
                            address_B = Cat(Replicate(0,5), self.address_B[0:10])

                    # Port B Read
                    if (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                        r_mode_b1 = "101"
                        r_mode_b2 = "101"
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        r_mode_b1 = "011"
                        r_mode_b2 = "011"
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        r_mode_b1 = "001"
                        r_mode_b2 = "001"
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        r_mode_b1 = "100"
                        r_mode_b2 = "100"
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        r_mode_b1 = "010"
                        r_mode_b2 = "010"
                    elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        r_mode_b1 = "110"
                        r_mode_b2 = "110"
                    
                    if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)]) > 8):
                        ben_A = 3
                    else:
                        ben_A = 1

                    if (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)]) > 8):
                        ben_B = 3
                    else:
                        ben_B = 1

                    mode = int ("0{}{}{}{}00000000000000000000000000000{}{}{}{}000000000000000000000000000".format(r_mode_a1, r_mode_b1, w_mode_a1, w_mode_b1, r_mode_a2, r_mode_b2, w_mode_a2, w_mode_b2))
                    mode_bits = Instance.PreformattedParam("81'b{:d}".format(mode))
                    init_i = Instance.PreformattedParam("36864'hx")

                    for j in range(m): 
                        read_data_A1    = self.bram_out_A[j][(i*36):((i*36)+18)]
                        read_data_A2    = self.bram_out_A[j][(((i*36)+18)):((i*36)+36)]
                        read_data_B1    = self.bram_out_B[j][(i*36):((i*36)+18)]
                        read_data_B2    = self.bram_out_B[j][(((i*36)+18)):((i*36)+36)]
                        if (common_clk == 1):
                            # Module instance.
                            # ----------------
                            self.specials += Instance("RS_TDP36K",
                            # Parameters.
                            # -----------
                            p_INIT_i        = init_i,
                            p_MODE_BITS     = mode_bits,
                            # Clk / Rst.
                            # ----------
                            i_CLK_A1        = ClockSignal(),
                            i_CLK_B1        = ClockSignal(),
                            i_CLK_A2        = ClockSignal(),
                            i_CLK_B2        = ClockSignal(),
                            i_WEN_A1        = self.wen_A1[j],
                            i_WEN_B1        = self.wen_B1[j],
                            i_REN_A1        = self.ren_A,
                            i_REN_B1        = self.ren_B,
                            i_BE_A1         = ben_A,
                            i_BE_B1         = ben_B,
                            i_ADDR_A1       = address_A,
                            i_ADDR_B1       = address_B,
                            i_WDATA_A1      = write_data_A1,
                            i_WDATA_B1      = write_data_B1,
                            o_RDATA_A1      = read_data_A1,
                            o_RDATA_B1      = read_data_B1,
                            i_FLUSH1        = 0,
                            i_WEN_A2        = self.wen_A1[j],
                            i_WEN_B2        = self.wen_B1[j],
                            i_REN_A2        = self.ren_A,
                            i_REN_B2        = self.ren_B,
                            i_BE_A2         = ben_A,
                            i_BE_B2         = ben_B,
                            i_ADDR_A2       = address_A,
                            i_ADDR_B2       = address_B,
                            i_WDATA_A2      = write_data_A2,
                            i_WDATA_B2      = write_data_B2,
                            o_RDATA_A2      = read_data_A2,
                            o_RDATA_B2      = read_data_B2,
                            i_FLUSH2        = 0
                        )
                        else: 
                            # Module instance.
                            # ----------------
                            self.specials += Instance("RS_TDP36K",
                            # Parameters.
                            # -----------
                            p_INIT_i        = init_i,
                            p_MODE_BITS     = mode_bits,
                            # Clk / Rst.
                            # ----------
                            i_CLK_A1        = ClockSignal("clk1"),
                            i_CLK_B1        = ClockSignal("clk2"),
                            i_CLK_A2        = ClockSignal("clk1"),
                            i_CLK_B2        = ClockSignal("clk2"),
                            i_WEN_A1        = self.wen_A1[j],
                            i_WEN_B1        = self.wen_B1[j],
                            i_REN_A1        = self.ren_A,
                            i_REN_B1        = self.ren_B,
                            i_BE_A1         = ben_A,
                            i_BE_B1         = ben_B,
                            i_ADDR_A1       = address_A,
                            i_ADDR_B1       = address_B,
                            i_WDATA_A1      = write_data_A1,
                            i_WDATA_B1      = write_data_B1,
                            o_RDATA_A1      = read_data_A1,
                            o_RDATA_B1      = read_data_B1,
                            i_FLUSH1        = 0,
                            i_WEN_A2        = self.wen_A1[j],
                            i_WEN_B2        = self.wen_B1[j],
                            i_REN_A2        = self.ren_A,
                            i_REN_B2        = self.ren_B,
                            i_BE_A2         = ben_A,
                            i_BE_B2         = ben_B,
                            i_ADDR_A2       = address_A,
                            i_ADDR_B2       = address_B,
                            i_WDATA_A2      = write_data_A2,
                            i_WDATA_B2      = write_data_B2,
                            o_RDATA_A2      = read_data_A2,
                            o_RDATA_B2      = read_data_B2,
                            i_FLUSH2        = 0
                        )
        
        # DRAM
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

