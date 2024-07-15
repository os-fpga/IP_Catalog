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
    def memory_converter(self, file_path, file_extension):
        if file_path == "":
            return "x"
        binary_data = []
        with open(file_path, "r") as f:
            file_content = f.readlines()
            line_count = 0
            self.logger.info(f"========== MEMORY INITIALIZATION STARTED ==========")
            logging.info("Reading Memory File")
            if (file_extension == ".hex"):
                logging.info("Found (.hex) File")
                logging.info("Processing")
            elif (file_extension == ".bin"):
                logging.info("Found (.bin) File")
                logging.info("Processing")
            else:
                logging.error("Memory Initialization Failed. Invalid File Format")
            
            for line in file_content:
                line_count += 1
                if (file_extension == ".hex"):
                    mem_file_data = int(line.strip(), 16)
                    binary = format(mem_file_data, 'b') # hexadecimal to binary conversion
                    binary_data.append(binary)
                    self.binary_data    = binary_data
                    self.line_count     = line_count
                elif (file_extension == ".bin"):
                    mem_file_data = int(line.strip(), 2) # binary(0b10101) to binary(10101) conversion
                    binary = format(mem_file_data, 'b')
                    binary_data.append(binary)
                    self.binary_data    = binary_data
                    self.line_count     = line_count
                else:
                    exit
                    self.binary_data    = 0
                    self.line_count     = 0
            return binary_data
    
    def memory_init(self, file_path, file_extension):
        self.memory_converter(file_path, file_extension)
        
        sram = {}
        INIT        = []
        INIT_PARITY = []
        
        # Empty File Path
        if (file_path == "") or (self.line_count == 0):
            return "0"
        
        # If File Path Exists
        if self.write_depth in [1024, 2048, 4096, 8192, 16384, 32768]:
            
            # 1K Memory Initialization
            if (self.write_depth == 1024):
                if (len(self.binary_data) > self.write_depth):
                    lines = self.write_depth
                else:
                    lines = self.line_count

                for i in range(lines):
                    if self.data_width % 36 == 0:
                            if len(self.binary_data[i]) < self.data_width:
                                self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                            else:
                                self.binary_data[i] = self.binary_data[i]
                    else:
                        temp = self.data_width % 36
                        self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        self.binary_data[i] = '0' * (36 - temp) + self.binary_data[i]
                
                # Appending 'x' on vacant addresses
                x_data = self.write_depth - self.line_count
                if lines == self.line_count:
                    for i in range(x_data):
                        self.binary_data.append((self.data_width + (36-(self.data_width % 36))) * '0')

                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    for i in range(1024): # 1024 * (1-line per iteration) = 1024 addresses
                        bits = self.binary_data[i*1][(j*36):(j*36)+36]  # Extract 36 bits from the binary data
                        sram[sram1].append(bits[1:9]+bits[10:18]+bits[19:27]+bits[28:36])  # (DATA) [34:27] + [25:18] + [16:9] + [7:0]
                        sram[sram2].append(bits[0]+bits[9]+bits[18]+bits[27])              # (PARITY) [35] + [26] + [17] + [8]
                    sram[data1] = "".join(sram[sram1][::-1]) # inverting indexing of list
                    sram[data2] = "".join(sram[sram2][::-1]) # inverting indexing of list
                    
                    INIT.append(sram[data1])
                    INIT_PARITY.append(sram[data2])
                    
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return INIT, INIT_PARITY
            
            # 2K Memory Initialization
            elif (self.write_depth == 2048):
                if (self.line_count) > 2048:
                    if (len(self.binary_data) > self.write_depth):
                        lines = self.write_depth
                else:
                    lines = self.line_count
                
                for i in range(lines):
                    if self.data_width % 18 == 0:
                        if len(self.binary_data[i]) < self.data_width:
                            self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        else:
                            self.binary_data[i] = self.binary_data[i]
                    else:
                        temp = self.data_width % 18
                        self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        self.binary_data[i] = '0' * (18 - temp) + self.binary_data[i]
                
                # Appending '0' on vacant addresses
                x_data = self.write_depth - self.line_count
                if lines == self.line_count:
                    for i in range(x_data):
                        self.binary_data.append((self.data_width + (18-(self.data_width % 18))) * '0')
                        
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    for i in range(2048): # 2048 * (1-line per iteration) = 2048 addresses
                        bits = self.binary_data[i*1][(j*18):(j*18)+18]  # Extract 18 bits from the binary data
                        sram[sram1].append(bits[1:9]+bits[10:18])  # (DATA) [16:9] + [7:0]
                        sram[sram2].append(bits[0]+bits[9])        # (PARITY) [17] + [8]
                        
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    
                    INIT.append(sram[data1])
                    INIT_PARITY.append(sram[data2])
                    
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return INIT, INIT_PARITY

            # 4K Memory Initialization
            elif (self.write_depth == 4096):
                if (len(self.binary_data) > self.write_depth):
                    lines = self.write_depth
                else:
                    lines = self.line_count

                for i in range(lines):
                    if self.data_width % 9 == 0:
                        if len(self.binary_data[i]) < self.data_width:
                            self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        else:
                            self.binary_data[i] = self.binary_data[i]
                    else:
                        temp = self.data_width % 9
                        self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        self.binary_data[i] = '0' * (9 - temp) + self.binary_data[i]
                
                # Appending 'x' on vacant addresses
                x_data = self.write_depth - self.line_count
                if lines == self.line_count:
                    for i in range(x_data):
                        self.binary_data.append((self.data_width + (9-(self.data_width % 9))) * '0')
                
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    for i in range(4096): # 4096 addresses
                        bits = self.binary_data[i*1][(j*9):(j*9)+9]  # Extract 9 bits from the binary data
                        sram[sram1].append(bits[1:9]) # (DATA) [7:0]
                        sram[sram2].append(bits[0])   # (PARITY) [8]
                        
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    
                    INIT.append(sram[data1])
                    INIT_PARITY.append(sram[data2])
                
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return INIT, INIT_PARITY

            # 8K Memory
            elif (self.write_depth == 8192):
                if (len(self.binary_data) > self.write_depth):
                    lines = self.write_depth
                else:
                    lines = self.line_count
                
                for i in range(lines):
                    if self.data_width % 4 == 0:
                        if len(self.binary_data[i]) < self.data_width:
                            self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        else:
                            self.binary_data[i] = self.binary_data[i]
                    else:
                        temp = self.data_width % 4
                        self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        self.binary_data[i] = '0' * (4 - temp) + self.binary_data[i]
                
                # Appending 'x' on vacant addresses
                x_data = self.write_depth - self.line_count
                if lines == self.line_count:
                    for i in range(x_data):
                        self.binary_data.append((self.data_width + (4-(self.data_width % 4))) * '0')
                        
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    for i in range(8192): # 8192 addresses
                        bits = self.binary_data[i*1][(j*4):(j*4)+4]  # Extract 4 bits from the binary data
                        sram[sram1].append(bits[0:4])  # (DATA) [3:0]
                        sram[sram2].append("0")        # (PARITY) # making parity 0
                        
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    
                    INIT.append(sram[data1])
                    INIT_PARITY.append(sram[data2])
                
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return INIT, INIT_PARITY
                
            # 16K Memory
            elif (self.write_depth == 16384):
                if (len(self.binary_data) > self.write_depth):
                    lines = self.write_depth
                else:
                    lines = self.line_count

                for i in range(lines):
                    if self.data_width % 4 == 0:
                        valid_data_width = self.data_width
                        if len(self.binary_data[i]) < self.data_width:
                            self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        else:
                            self.binary_data[i] = self.binary_data[i]
                    else:
                        temp = self.data_width % 2
                        self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                        self.binary_data[i] = '0' * (2 - temp) + self.binary_data[i]
                        valid_data_width = (self.data_width + (4-(self.data_width % 4)))
                
                # Appending 'x' on vacant addresses
                x_data = self.write_depth - self.line_count
                if lines == self.line_count:
                    for i in range(x_data):
                        self.binary_data.append(valid_data_width * '0')
                
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    for i in range(16384): # 16384 addresses
                        bits = self.binary_data[i*1][(j*2):(j*2)+2]  # [Extract 2 bits from the binary data]
                        sram[sram1].append(bits[0:2])  # (DATA) [1:0]
                        sram[sram2].append("0")        # (PARITY) # making parity 0
                        
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    
                    INIT.append(sram[data1])
                    INIT_PARITY.append(sram[data2])
                    
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return INIT, INIT_PARITY
            
            # 32K Memory
            elif (self.write_depth == 32768):
                if (len(self.binary_data) > self.write_depth):
                    lines = self.write_depth
                else:
                    lines = self.line_count

                for i in range(lines):
                    if len(self.binary_data[i]) < self.data_width:
                        self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                
                # Appending 'x' on vacant addresses
                x_data = self.write_depth - self.line_count
                if lines == self.line_count:
                    for i in range(x_data):
                        self.binary_data.append(self.data_width * '0')
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    for i in range(32768): # 32768 addresses
                        bits = self.binary_data[i*1][(j*1):(j*1)+1]  # Extract 2 bits from the binary data
                        sram[sram1].append(bits[0])  # (DATA) [0]
                        sram[sram2].append("0")      # (PARITY) # making parity 0
                    
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    
                    INIT.append(sram[data1])
                    INIT_PARITY.append(sram[data2])
                    
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return INIT, INIT_PARITY
        
        # Other Memory Size Initialization
        else:
            lines = self.line_count
            
            for i in range(lines):
                if self.data_width % 36 == 0:
                    valid_data_width = self.data_width
                    if len(self.binary_data[i]) < self.data_width:
                        self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                    else:
                        self.binary_data[i] = self.binary_data[i]
                else:
                    temp = self.data_width % 36
                    self.binary_data[i] = '0' * (self.data_width - len(self.binary_data[i])) + self.binary_data[i]
                    self.binary_data[i] = '0' * (36 - temp) + self.binary_data[i]
                    valid_data_width = (self.data_width + (36-(self.data_width % 36)))
                
            valid_depth = self.write_depth + (1024-(self.write_depth % 1024))
            x_data = valid_depth - self.line_count # Appending 'x' on vacant addresses
            k = 0
            for i in range(x_data):
                self.binary_data.append(valid_data_width * '0')
                
            for j in range(self.m): # on depth
                for x in range(self.n-1, -1, -1): # on data_width
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{k}"
                    data2 = f"ram_data2_{k}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    k=k+1 # to manage mxn 
                    for i in range(1024): # 1024 * (1-line per iteration) = 1024 addresses
                        bits = self.binary_data[i+(j*1024)][(x*36):(x*36)+36]  # Extract 36 bits from the binary data
                        
                        sram[sram1].append(bits[1:9]+bits[10:18]+bits[19:27]+bits[28:36])  # (DATA) [34:27] + [25:18] + [16:9] + [7:0]
                        sram[sram2].append(bits[0]+bits[9]+bits[18]+bits[27])              # (PARITY) [35] + [26] + [17] + [8]
                        
                    sram[data1] = "".join(sram[sram1][::-1]) # inverting indexing of list
                    sram[data2] = "".join(sram[sram2][::-1]) # inverting indexing of list
                    
                    INIT.append(sram[data1])
                    INIT_PARITY.append(sram[data2])
            
            logging.info("Memory Initialized Successfully !!!")
            self.logger.info(f"===================================================")
            return INIT, INIT_PARITY
    
    def __init__(self, data_width, memory_type, common_clk, write_depth, memory_mapping, file_path_hex, file_extension, byte_write_enable, op_mode):
        
        self.write_depth = write_depth
        self.data_width  = data_width
        file_path = file_path_hex
        
        # Get/Check Parameters.
        # ---------------------
        self.logger = logging.getLogger("\tON CHIP MEMORY")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        self.logger.info(f"MEMORY_TYPE      : {memory_type}")
        
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        
        self.logger.info(f"WRITE_DEPTH      : {write_depth}")
        
        self.logger.info(f"COMMON_CLK       : {common_clk}")
        
        self.logger.info(f"MEMORY_MAPPING   : {memory_mapping}")
        
        self.addr_A    = Signal(math.ceil(math.log2(write_depth)))
        self.addr_B    = Signal(math.ceil(math.log2(write_depth)))
        
        self.din_A      = Signal(data_width)
        self.din_A_reg  = Signal(data_width)
        self.dout_A     = Signal(data_width)
        self.dout_A_    = Signal(data_width)
        self.dout_A_reg = Signal(data_width)
        
        self.din_B      = Signal(data_width)
        self.din_B_reg  = Signal(data_width)
        self.dout_B     = Signal(data_width)
        self.dout_B_    = Signal(data_width)
        self.dout_B_reg = Signal(data_width)
        
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
        
        if file_path != "":
            k = 0
            init, init_parity = self.memory_init(file_path, file_extension)
        
        if (memory_mapping == "Block_RAM"):
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
        self.wen_A_reg    = Signal(1)
        self.ren_A        = Signal(1)
        self.ren_A_reg    = Signal(1)
        self.wen_B        = Signal(1)
        self.wen_B_reg    = Signal(1)
        self.ren_B        = Signal(1)
        self.ren_B_reg    = Signal(1)
        
        self.be_A         = Signal(math.ceil(data_width/9))
        self.be_B         = Signal(math.ceil(data_width/9))
        
        # read port signals
        self.bram_out_A = [Signal(32*n) for i in range(m)]
        self.bram_out_B = [Signal(32*n) for i in range(m)]
        self.rparity_A  = [Signal(4*n) for i in range(m)]
        self.rparity_B  = [Signal(4*n) for i in range(m)]
        
        # Registered Address for output logic
        self.addr_A_reg = Signal(m)
        self.addr_B_reg = Signal(m)
        
        # Synchronous/ Asynchronous Clock
        if (common_clk == 1):
            clock1 = ClockSignal("sys")
            clock2 = ClockSignal("sys")
        else:
            clock1 = ClockSignal("A")
            clock2 = ClockSignal("B")
        
        # BRAM Utilization Logic
        if (memory_mapping == "Block_RAM"):
            if (write_depth in [1024, 2048, 4096, 8192, 16384, 32768]):
                # Single Port RAM
                if (memory_type == "Single_Port"):
                    if (op_mode in ["No_Change", "Read_First"]):
                        self.comb += If((self.ren_A_reg), self.dout_A_.eq(self.dout_A)).Else(self.dout_A_.eq(self.dout_A_reg))
                        self.sync.A += If(self.ren_A_reg, self.dout_A_reg.eq(self.dout_A))
                        self.sync.A += self.ren_A_reg.eq(self.ren_A)
                    else: # Write_First
                        self.comb += If((self.wen_A_reg), self.dout_A_.eq(self.din_A_reg)).Else(self.dout_A_.eq(self.dout_A))
                        self.sync.A += self.wen_A_reg.eq(self.wen_A)
                        self.sync.A += self.din_A_reg.eq(self.din_A)
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
                    if (op_mode in ["No_Change", "Read_First"]):
                        self.comb += If((self.ren_B_reg), self.dout_B_.eq(self.dout_B)).Else(self.dout_B_.eq(self.dout_B_reg))
                        if (common_clk == 1):
                            self.sync += If(self.ren_B_reg, self.dout_B_reg.eq(self.dout_B))
                            self.sync += self.ren_B_reg.eq(self.ren_B)
                        else:
                            self.sync.B += If(self.ren_B_reg, self.dout_B_reg.eq(self.dout_B))
                            self.sync.B += self.ren_B_reg.eq(self.ren_B)
                    else: # Write_First
                        self.comb += If((self.wen_A_reg), self.dout_B_.eq(self.din_A_reg)).Else(self.dout_B_.eq(self.dout_B))
                        if (common_clk == 1):
                            self.sync += self.wen_A_reg.eq(self.wen_A)
                            self.sync += self.din_A_reg.eq(self.din_A)
                        else:
                            self.sync.A += self.wen_A_reg.eq(self.wen_A)
                            self.sync.A += self.din_A_reg.eq(self.din_A)
                        
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
                    if (op_mode in ["No_Change", "Read_First"]):
                        self.comb += If((self.ren_A_reg), self.dout_A_.eq(self.dout_A)).Else(self.dout_A_.eq(self.dout_A_reg))
                        self.comb += If((self.ren_B_reg), self.dout_B_.eq(self.dout_B)).Else(self.dout_B_.eq(self.dout_B_reg))
                        if (common_clk == 1):
                            self.sync += If(self.ren_A_reg, self.dout_A_reg.eq(self.dout_A))
                            self.sync += self.ren_A_reg.eq(self.ren_A)
                            self.sync += If(self.ren_B_reg, self.dout_B_reg.eq(self.dout_B))
                            self.sync += self.ren_B_reg.eq(self.ren_B)
                        else:
                            self.sync.A += If(self.ren_A_reg, self.dout_A_reg.eq(self.dout_A))
                            self.sync.A += self.ren_A_reg.eq(self.ren_A)
                            self.sync.B += If(self.ren_B_reg, self.dout_B_reg.eq(self.dout_B))
                            self.sync.B += self.ren_B_reg.eq(self.ren_B)
                    else: #Write_First
                        self.comb += If((self.wen_A_reg), self.dout_A_.eq(self.din_A_reg)).Else(self.dout_A_.eq(self.dout_A))
                        self.comb += If((self.wen_B_reg), self.dout_B_.eq(self.din_B_reg)).Else(self.dout_B_.eq(self.dout_B))
                        if (common_clk == 1):
                            self.sync += self.wen_A_reg.eq(self.wen_A)
                            self.sync += self.din_A_reg.eq(self.din_A)
                            self.sync += self.wen_B_reg.eq(self.wen_B)
                            self.sync += self.din_B_reg.eq(self.din_B)
                        else:
                            self.sync.A += self.wen_A_reg.eq(self.wen_A)
                            self.sync.A += self.din_A_reg.eq(self.din_A)
                            self.sync.B += self.wen_B_reg.eq(self.wen_B)
                            self.sync.B += self.din_B_reg.eq(self.din_B)
                            
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
                    self.comb += If((self.ren_A_reg), self.dout_A_.eq(self.dout_A)).Else(self.dout_A_.eq(self.dout_A_reg))
                    self.sync.A += If(self.ren_A_reg, self.dout_A_reg.eq(self.dout_A))
                    self.sync.A += self.ren_A_reg.eq(self.ren_A)
                    
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
                    self.comb += If((self.ren_B_reg), self.dout_B_.eq(self.dout_B)).Else(self.dout_B_.eq(self.dout_B_reg))
                    if (common_clk == 1):
                        self.sync += If(self.ren_B_reg, self.dout_B_reg.eq(self.dout_B))
                        self.sync += self.ren_B_reg.eq(self.ren_B)
                    else:
                        self.sync.B += If(self.ren_B_reg, self.dout_B_reg.eq(self.dout_B))
                        self.sync.B += self.ren_B_reg.eq(self.ren_B)
                    
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
                    self.comb += If((self.ren_A_reg), self.dout_A_.eq(self.dout_A)).Else(self.dout_A_.eq(self.dout_A_reg))
                    self.comb += If((self.ren_B_reg), self.dout_B_.eq(self.dout_B)).Else(self.dout_B_.eq(self.dout_B_reg))
                    if (common_clk == 1):
                        self.sync += If(self.ren_A_reg, self.dout_A_reg.eq(self.dout_A))
                        self.sync += self.ren_A_reg.eq(self.ren_A)
                        self.sync += If(self.ren_B_reg, self.dout_B_reg.eq(self.dout_B))
                        self.sync += self.ren_B_reg.eq(self.ren_B)
                    else:
                        self.sync.A += If(self.ren_A_reg, self.dout_A_reg.eq(self.dout_A))
                        self.sync.A += self.ren_A_reg.eq(self.ren_A)
                        self.sync.B += If(self.ren_B_reg, self.dout_B_reg.eq(self.dout_B))
                        self.sync.B += self.ren_B_reg.eq(self.ren_B)
                    
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
                    if (byte_write_enable):
                        be_A = self.be_A[(i*4):(i*4)+4]
                    else:
                        be_A = Replicate(1, 4)
                        
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
                            write_data_A   = self.din_A[36*(n-1):data_width]
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
                        if (file_path == "") or (self.line_count == 0):
                            data    = '0'
                            parity  = '0'
                        else:
                            if write_depth in [1024, 2048, 4096, 8192, 16384, 32768]:
                                data        = hex(int(init[j], 2))[2:]          # hex conversion and removal of 0x from start of converted data
                                parity      = hex(int(init_parity[j], 2))[2:]   # hex conversion and removal of 0x from start of converted data
                            else:
                                k = j * n + i
                                data        = hex(int(init[k], 2))[2:]             # hex conversion and removal of 0x from start of converted data
                                parity      = hex(int(init_parity[k], 2))[2:]      # hex conversion and removal of 0x from start of converted data
                        
                        if (write_depth == 1024):
                            if (byte_write_enable):
                                be_A = self.be_A[(j*4):(j*4)+4]
                            else:
                                be_A = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j*2):(j*2)+2]
                            else:
                                be_A = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j*1):(j*1)+1]
                            else:
                                be_A = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j//2):(j//2)+1]
                            else:
                                be_A = Replicate(1, 4)
                                
                            write_data_A    = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A      = Replicate(0,4)
                        
                        elif (write_depth == 16384):
                            if (byte_write_enable):
                                be_A = self.be_A[(j//4):(j//4)+1]
                            else:
                                be_A = Replicate(1, 4)
                                
                            write_data_A    = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A      = Replicate(0,4)
                            
                        elif (write_depth == 32768):
                            if (byte_write_enable):
                                be_A = self.be_A[(j//8):(j//8)+1]
                            else:
                                be_A = Replicate(1, 4)
                                
                            write_data_A    = self.din_A[(j*1):((j*1)+1)]
                            w_parity_A      = Replicate(0,4)
                            
                        if (write_depth <= 1024 or write_depth in [2048, 4096, 8192, 16384, 32768]):
                            wen = self.wen_A
                        else:
                            wen = self.wen_A1[j]
                        
                        if (op_mode == "Read_First"):
                            ren = self.ren_A
                        elif (op_mode == "No_Change" or op_mode == "Write_First"):
                            ren = ~self.wen_A
                        
                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "SP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("32768'h{}".format(data)),
                        p_INIT_PARITY       = Instance.PreformattedParam("4096'h{}".format(parity)),
                        p_WRITE_WIDTH_A     = param_write_width_A,
                        p_READ_WIDTH_A      = param_read_width_A,
                        p_WRITE_WIDTH_B     = param_write_width_A,
                        p_READ_WIDTH_B      = param_read_width_A,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_CLK_B     = 0,
                        i_WEN_A     = wen,
                        i_WEN_B     = 0,
                        i_REN_A     = ren,
                        i_REN_B     = 0,
                        i_BE_A      = be_A,
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
                    if (byte_write_enable):
                        be_A = self.be_A[(i*4):(i*4)+4]
                    else:
                        be_A = Replicate(1, 4)
                        
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
                            write_data_A   = self.din_A[36*(n-1):data_width]
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

                    k = 0
                    for j in range(m):
                        if (file_path == "") or (self.line_count == 0):
                            data    = '0'
                            parity  = '0'
                        else:
                            if write_depth in [1024, 2048, 4096, 8192, 16384, 32768]:
                                data        = hex(int(init[j], 2))[2:]          # hex conversion and removal of 0x from start of converted data
                                parity      = hex(int(init_parity[j], 2))[2:]   # hex conversion and removal of 0x from start of converted data
                            else:
                                k = j * n + i
                                data        = hex(int(init[k], 2))[2:]             # hex conversion and removal of 0x from start of converted data
                                parity      = hex(int(init_parity[k], 2))[2:]      # hex conversion and removal of 0x from start of converted data
                        
                        if (write_depth == 1024):
                            if (byte_write_enable):
                                be_A = self.be_A[(j*4):(j*4)+4]
                            else:
                                be_A = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j*2):(j*2)+2]
                            else:
                                be_A = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j*1):(j*1)+1]
                            else:
                                be_A = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j//2):(j//2)+1]
                            else:
                                be_A = Replicate(1, 4)
                                
                            write_data_A    = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A      = Replicate(0,4)
                        
                        elif (write_depth == 16384):
                            if (byte_write_enable):
                                be_A = self.be_A[(j//4):(j//4)+1]
                            else:
                                be_A = Replicate(1, 4)
                                
                            write_data_A    = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A      = Replicate(0,4)
                            
                        elif (write_depth == 32768):
                            if (byte_write_enable):
                                be_A = self.be_A[(j//8):(j//8)+1]
                            else:
                                be_A = Replicate(1, 4)
                                
                            write_data_A    = self.din_A[(j*1):((j*1)+1)]
                            w_parity_A      = Replicate(0,4)
                            
                        # for j in range(m):
                        if (write_depth <= 1024 or write_depth in [2048, 4096, 8192, 16384, 32768]):
                            wen = self.wen_A
                        else:
                            wen = self.wen_A1[j]
                        
                        if (op_mode == "Read_First"):
                            ren = self.ren_B
                        elif (op_mode == "No_Change" or op_mode == "Write_First"):
                            ren = ~self.wen_A

                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "SDP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("32768'h{}".format(data)),
                        p_INIT_PARITY       = Instance.PreformattedParam("4096'h{}".format(parity)),
                        p_WRITE_WIDTH_A     = param_write_width_A,
                        p_WRITE_WIDTH_B     = param_write_width_A,
                        p_READ_WIDTH_A      = param_read_width_B,
                        p_READ_WIDTH_B      = param_read_width_B,
                        # Ports.
                        # -----------
                        i_CLK_A     = clock1,
                        i_CLK_B     = clock2,
                        i_WEN_A     = wen,
                        i_WEN_B     = 0,
                        i_REN_A     = 0,
                        i_REN_B     = ren,
                        i_BE_A      = be_A, 
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
                    if (byte_write_enable):
                        be_A = self.be_A[(i*4):(i*4)+4]
                        be_B = self.be_B[(i*4):(i*4)+4]
                    else:
                        be_A = Replicate(1, 4)
                        be_B = Replicate(1, 4)
                        
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
                            write_data_A   = self.din_A[36*(n-1):data_width]
                            w_parity_A     = Replicate(0,4)
                            write_data_B   = self.din_B[36*(n-1):data_width]
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

                    k = 0
                    for j in range(m):
                        if (file_path == "") or (self.line_count == 0):
                            data    = '0'
                            parity  = '0'
                        else:
                            if write_depth in [1024, 2048, 4096, 8192, 16384, 32768]:
                                data        = hex(int(init[j], 2))[2:]          # hex conversion and removal of 0x from start of converted data
                                parity      = hex(int(init_parity[j], 2))[2:]   # hex conversion and removal of 0x from start of converted data
                            else:
                                k = j * n + i
                                data        = hex(int(init[k], 2))[2:]             # hex conversion and removal of 0x from start of converted data
                                parity      = hex(int(init_parity[k], 2))[2:]      # hex conversion and removal of 0x from start of converted data
                        
                        if (write_depth == 1024):
                            if (byte_write_enable):
                                be_A = self.be_A[(j*4):(j*4)+4]
                                be_B = self.be_B[(j*4):(j*4)+4]
                            else:
                                be_A = Replicate(1, 4)
                                be_B = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j*2):(j*2)+2]
                                be_B = self.be_B[(j*2):(j*2)+2]
                            else:
                                be_A = Replicate(1, 4)
                                be_B = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j*1):(j*1)+1]
                                be_B = self.be_B[(j*1):(j*1)+1]
                            else:
                                be_A = Replicate(1, 4)
                                be_B = Replicate(1, 4)
                                
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
                            if (byte_write_enable):
                                be_A = self.be_A[(j//2):(j//2)+1]
                                be_B = self.be_B[(j//2):(j//2)+1]
                            else:
                                be_A = Replicate(1, 4)
                                be_B = Replicate(1, 4)
                                
                            write_data_A    = self.din_A[(j*4):((j*4)+4)]
                            w_parity_A      = Replicate(0,4)
                            write_data_B    = self.din_B[(j*4):((j*4)+4)]
                            w_parity_B      = Replicate(0,4)
                        
                        elif (write_depth == 16384):
                            if (byte_write_enable):
                                be_A = self.be_A[(j//4):(j//4)+1]
                                be_B = self.be_B[(j//4):(j//4)+1]
                            else:
                                be_A = Replicate(1, 4)
                                be_B = Replicate(1, 4)
                                
                            write_data_A    = self.din_A[(j*2):((j*2)+2)]
                            w_parity_A      = Replicate(0,4)
                            write_data_B    = self.din_B[(j*2):((j*2)+2)]
                            w_parity_B      = Replicate(0,4)
                            
                        elif (write_depth == 32768):
                            if (byte_write_enable):
                                be_A = self.be_A[(j//8):(j//8)+1]
                                be_B = self.be_B[(j//8):(j//8)+1]
                            else:
                                be_A = Replicate(1, 4)
                                be_B = Replicate(1, 4)
                                
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
                        
                        if (op_mode == "Read_First"):
                            renA = self.ren_A
                            renB = self.ren_B
                        elif (op_mode == "No_Change" or op_mode == "Write_First"):
                            renA = ~self.wen_A
                            renB = ~self.wen_B
                        
                        # Module instance.
                        # ----------------
                        self.specials += Instance("TDP_RAM36K", name= "TDP_MEM",
                        # Parameters.
                        # -----------
                        p_INIT              = Instance.PreformattedParam("32768'h{}".format(data)),
                        p_INIT_PARITY       = Instance.PreformattedParam("4096'h{}".format(parity)),
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
                        i_REN_A     = renA,
                        i_REN_B     = renB,
                        i_BE_A      = be_A, 
                        i_BE_B      = be_B, 
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
            # Operational modes of memory
            operation_mode = {
                "Read_First"    : 0,
                "Write_First"   : 1,
                "No_Change"     : 2
            }[op_mode]
            
            self.specials.memory = Memory(width=data_width, depth=write_depth)
            if (memory_type == "Single_Port"):
                self.port = self.memory.get_port(write_capable=True, async_read=False, mode=operation_mode, has_re=True, clock_domain="A")
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
                    self.port_A = self.memory.get_port(write_capable=True, async_read=True, mode=operation_mode, has_re=False, clock_domain="sys")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=False, async_read=False, mode=operation_mode, has_re=True, clock_domain="sys")
                    self.specials += self.port_B
                else:
                    self.port_A = self.memory.get_port(write_capable=True, async_read=True, mode=operation_mode, has_re=False, clock_domain="A")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=False, async_read=False, mode=operation_mode, has_re=True, clock_domain="B")
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
                    self.port_A = self.memory.get_port(write_capable=True, async_read=False, mode=operation_mode, has_re=True, clock_domain="sys")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=True, async_read=False, mode=operation_mode, has_re=True, clock_domain="sys")
                    self.specials += self.port_B
                else:
                    self.port_A = self.memory.get_port(write_capable=True, async_read=False, mode=operation_mode, has_re=True, clock_domain="A")
                    self.specials += self.port_A
                    self.port_B = self.memory.get_port(write_capable=True, async_read=False, mode=operation_mode, has_re=True, clock_domain="B")
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

