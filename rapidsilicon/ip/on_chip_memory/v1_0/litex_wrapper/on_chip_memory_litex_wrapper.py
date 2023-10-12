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
        result = []
        
        # Empty File Path
        if (file_path == "") or (self.line_count == 0):
            return "x"
        
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
                        self.binary_data.append((self.data_width + (36-(self.data_width % 36))) * 'x')

                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram_result = f"result_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    sram[sram_result] = []

                    for i in range(1024): # 1024 * (1-line per iteration) = 1024 addresses
                        bits = self.binary_data[i*1][j*36:(j*36)+36]  # Extract 36 bits from the binary data
                        sram[sram1].append(bits[:18]) # Extracting First 18 bits from binary data
                        sram[sram2].append(bits[18:]) # Extracting Next 18 bits from binary data

                    sram[data1] = "".join(sram[sram1][::-1]) # inverting indexing of list
                    sram[data2] = "".join(sram[sram2][::-1]) # inverting indexing of list
                    sram[sram_result] = sram[data1] + sram[data2]
                    result.append(sram[sram_result])
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return result
            
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
                
                # Appending 'x' on vacant addresses
                x_data = self.write_depth - self.line_count
                if lines == self.line_count:
                    for i in range(x_data):
                        self.binary_data.append((self.data_width + (18-(self.data_width % 18))) * 'x')
                        
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram_result = f"result_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    sram[sram_result] = []
                    for i in range(2048): # 2048 * (1-line per iteration) = 2048 addresses
                        if i % 2 == 0:
                            sram[sram1].append(self.binary_data[(i*1)][(j*18):(j*18)+18])
                        else:
                            sram[sram2].append(self.binary_data[(i*1)][(j*18):(j*18)+18])
                            
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    sram[sram_result] = sram[data2] + sram[data1]
                    result.append(sram[sram_result])
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return result

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
                        self.binary_data.append((self.data_width + (9-(self.data_width % 9))) * 'x')
                
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram_result = f"result_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    sram[sram_result] = []
                    for i in range(2048): # 2048 * (2-lines per iteration) = 4096 addresses
                        if i % 2 == 0:
                            sram[sram1].append(self.binary_data[(i*2)+1][(j*9)] + self.binary_data[(i*2)+0][(j*9)] + self.binary_data[(i*2)+1][(j*9)+1:(j*9)+9] + self.binary_data[(i*2)+0][(j*9)+1:(j*9)+9])
                        else:
                            sram[sram2].append(self.binary_data[(i*2)+1][(j*9)] + self.binary_data[(i*2)+0][(j*9)] + self.binary_data[(i*2)+1][(j*9)+1:(j*9)+9] + self.binary_data[(i*2)+0][(j*9)+1:(j*9)+9])
                    
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    sram[sram_result] = sram[data2] + sram[data1]
                    result.append(sram[sram_result])
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return result

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
                        self.binary_data.append((self.data_width + (4-(self.data_width % 4))) * 'x')
                        
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram_result = f"result_{j}"
                    
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    sram[sram_result] = []
                    
                    for i in range(2048): # 2048 * (4-lines per iteration) = 8192 addresses
                        if i % 2 == 0:
                            sram[sram1].append("xx" + self.binary_data[(i*4)+3][(j*4):(j*4)+4]+self.binary_data[(i*4)+2][(j*4):(j*4)+4]+self.binary_data[(i*4)+1][(j*4):(j*4)+4]+self.binary_data[(i*4)][(j*4):(j*4)+4])
                        else:
                            sram[sram2].append("xx" + self.binary_data[(i*4)+3][(j*4):(j*4)+4]+self.binary_data[(i*4)+2][(j*4):(j*4)+4]+self.binary_data[(i*4)+1][(j*4):(j*4)+4]+self.binary_data[(i*4)][(j*4):(j*4)+4])

                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    sram[sram_result] = sram[data2] + sram[data1]
                    result.append(sram[sram_result])
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return result
                
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
                        self.binary_data.append(valid_data_width * 'x')
                
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram_result = f"result_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    sram[sram_result] = []
                    for i in range(2048): # 2048 * (8-lines per iteration) = 16384 addresses
                        if i % 2 == 0:
                            sram[sram1].append("xx" + self.binary_data[(i*8)+7][(j*2):(j*2)+2] + self.binary_data[(i*8)+6][(j*2):(j*2)+2] + self.binary_data[(i*8)+5][(j*2):(j*2)+2] + self.binary_data[(i*8)+4][(j*2):(j*2)+2] + self.binary_data[(i*8)+3][(j*2):(j*2)+2]+self.binary_data[(i*8)+2][(j*2):(j*2)+2]+self.binary_data[(i*8)+1][(j*2):(j*2)+2]+self.binary_data[(i*8)][(j*2):(j*2)+2])
                        else:
                            sram[sram2].append("xx" + self.binary_data[(i*8)+7][(j*2):(j*2)+2] + self.binary_data[(i*8)+6][(j*2):(j*2)+2] + self.binary_data[(i*8)+5][(j*2):(j*2)+2] + self.binary_data[(i*8)+4][(j*2):(j*2)+2] + self.binary_data[(i*8)+3][(j*2):(j*2)+2]+self.binary_data[(i*8)+2][(j*2):(j*2)+2]+self.binary_data[(i*8)+1][(j*2):(j*2)+2]+self.binary_data[(i*8)][(j*2):(j*2)+2])
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    sram[sram_result] = sram[data2] + sram[data1]
                    result.append(sram[sram_result])
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return result
            
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
                        self.binary_data.append(self.data_width * 'x')
                for j in range(self.m-1, -1, -1):
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    data1 = f"ram_data1_{j}"
                    data2 = f"ram_data2_{j}"
                    sram_result = f"result_{j}"
                    sram[sram1] = []
                    sram[sram2] = []
                    sram[data1] = []
                    sram[data2] = []
                    sram[sram_result] = []
                    for i in range(2048): # 2048 * (16-lines per iteration) = 32768 addresses
                        if i % 2 == 0:
                            sram[sram1].append("xx" + self.binary_data[(i*16)+15][(j*1):(j*1)+1] + self.binary_data[(i*16)+14][(j*1):(j*1)+1] + self.binary_data[(i*16)+13][(j*1):(j*1)+1] + self.binary_data[(i*16)+12][(j*1):(j*1)+1] + self.binary_data[(i*16)+11][(j*1):(j*1)+1] + self.binary_data[(i*16)+10][(j*1):(j*1)+1] + self.binary_data[(i*16)+9][(j*1):(j*1)+1] + self.binary_data[(i*16)+8][(j*1):(j*1)+1] + self.binary_data[(i*16)+7][(j*1):(j*1)+1] + self.binary_data[(i*16)+6][(j*1):(j*1)+1] + self.binary_data[(i*16)+5][(j*1):(j*1)+1] + self.binary_data[(i*16)+4][(j*1):(j*1)+1] + self.binary_data[(i*16)+3][(j*1):(j*1)+1]+self.binary_data[(i*16)+2][(j*1):(j*1)+1]+self.binary_data[(i*16)+1][(j*1):(j*1)+1]+self.binary_data[(i*16)][(j*1):(j*1)+1])
                        else:
                            sram[sram2].append("xx" + self.binary_data[(i*16)+15][(j*1):(j*1)+1] + self.binary_data[(i*16)+14][(j*1):(j*1)+1] + self.binary_data[(i*16)+13][(j*1):(j*1)+1] + self.binary_data[(i*16)+12][(j*1):(j*1)+1] + self.binary_data[(i*16)+11][(j*1):(j*1)+1] + self.binary_data[(i*16)+10][(j*1):(j*1)+1] + self.binary_data[(i*16)+9][(j*1):(j*1)+1] + self.binary_data[(i*16)+8][(j*1):(j*1)+1] + self.binary_data[(i*16)+7][(j*1):(j*1)+1] + self.binary_data[(i*16)+6][(j*1):(j*1)+1] + self.binary_data[(i*16)+5][(j*1):(j*1)+1] + self.binary_data[(i*16)+4][(j*1):(j*1)+1] + self.binary_data[(i*16)+3][(j*1):(j*1)+1]+self.binary_data[(i*16)+2][(j*1):(j*1)+1]+self.binary_data[(i*16)+1][(j*1):(j*1)+1]+self.binary_data[(i*16)][(j*1):(j*1)+1])
                    
                    sram[data1] = "".join(sram[sram1][::-1]) 
                    sram[data2] = "".join(sram[sram2][::-1])
                    sram[sram_result] = sram[data2] + sram[data1]
                    result.append(sram[sram_result])
                logging.info("Memory Initialized Successfully !!!")
                self.logger.info(f"===================================================")
                return result
        
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
                self.binary_data.append(valid_data_width * 'x')
                
            for x in range(self.n-1,-1,-1): # on data_width
                for j in range(self.m): # on depth
                    sram1 = f"sram1_{j}"
                    sram2 = f"sram2_{j}"
                    bits = f"bits_{k}"
                    data1 = f"ram_data1_{k}"
                    data2 = f"ram_data2_{k}"
                    sram_result = f"result_{k}"

                    sram[sram1] = []
                    sram[sram2] = []
                    sram[bits] = []
                    sram[data1] = []
                    sram[data2] = []
                    sram[sram_result] = []
                    k=k+1 # to manage mxn 
                    
                    for i in range(1024): # 1024 * (1-line per iteration) = 1024 addresses
                        sram[bits].append(self.binary_data[i+(j*1024)][x*36:(x*36)+36]) # working 
                        sram[sram1].append(sram[bits][i][:18]) # Extracting First 18 bits from binary data
                        sram[sram2].append(sram[bits][i][18:]) # Extracting Next 18 bits from binary data
                    sram[data1] = "".join(sram[sram1][::-1]) # inverting indexing of SRAM1
                    sram[data2] = "".join(sram[sram2][::-1]) # inverting indexing of SRAM2
                    sram[sram_result] = sram[data1] + sram[data2]
                    result.append(sram[sram_result])
            logging.info("Memory Initialized Successfully !!!")
            self.logger.info(f"===================================================")
            return result
    
    def __init__(self, platform, data_width, memory_type, common_clk, write_depth, bram, file_path, file_extension):
        
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
        
        # Registered Address for output logic
        if write_depth > 1024:
            self.addr_A_reg = Signal(msb-10)
            self.addr_B_reg = Signal(msb-10)
        
        y = data_width - 36*(n-1)
        z = data_width - 36*(m-1)
        
        # BRAM Utilization Logic
        if (bram == 1):
            # Number of Data Out Ports from BRAMS
            self.bram_out_A = [Signal(36*n) for i in range(m)]
            self.bram_out_B = [Signal(36*n) for i in range(m)]

            if (write_depth == 1024 or write_depth == 2048 or write_depth == 4096 or write_depth == 8192 or write_depth == 16384 or write_depth == 32768):
                # Single Port RAM
                if (memory_type == "Single_Port"):
                    self.comb += If((self.wen_A == 1), self.wen_A1.eq(1))
                    for i in range(m):
                        if (write_depth <= 1024):
                            self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][0:36]))
                        elif (write_depth == 2048):
                            self.comb += self.dout_A[(i*18):((i*18)+18)].eq(Cat(self.bram_out_A[i][0:18]))
                        elif (write_depth == 4096):
                            if data_width > 8:
                                if (m == (i+1)):
                                    if (y == i*9):
                                        self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8]))
                                    else:
                                        self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.bram_out_A[i][16]))
                                else:
                                    self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.bram_out_A[i][16]))
                            else:
                                self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:data_width]))
                                
                        elif (write_depth == 8192):
                            self.comb += self.dout_A[(i*4):((i*4)+4)].eq(Cat(self.bram_out_A[i][0:4]))
                        elif (write_depth == 16384):
                            self.comb += self.dout_A[(i*2):((i*2)+2)].eq(Cat(self.bram_out_A[i][0:2]))
                        elif (write_depth == 32768):
                            self.comb += self.dout_A[(i*1):((i*1)+1)].eq(Cat(self.bram_out_A[i][0:1]))
                            
                # Simple Dual Port RAM
                elif (memory_type == "Simple_Dual_Port"):
                    self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)).Else(self.wen_A1.eq(0))
                    for i in range(m):
                        if (write_depth <= 1024):
                            self.comb += self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[i][0:36]))
                        elif (write_depth > 1024 and write_depth <= 2048):
                            self.comb += self.dout_B[(i*18):((i*18)+18)].eq(Cat(self.bram_out_B[i][0:18]))
                        elif (write_depth > 2048 and write_depth <= 4096):
                            if data_width > 8:
                                if (m == (i+1)):
                                    if (y == i*9):
                                        self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8]))
                                    else:
                                        self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.bram_out_B[i][16]))
                                else:
                                    self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.bram_out_B[i][16]))
                            else:
                                self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:data_width]))
                        elif (write_depth > 4096 and write_depth <= 8192):
                            self.comb += self.dout_B[(i*4):((i*4)+4)].eq(Cat(self.bram_out_B[i][0:4]))
                        elif (write_depth == 16384):
                            self.comb += self.dout_B[(i*2):((i*2)+2)].eq(Cat(self.bram_out_B[i][0:2]))
                        elif (write_depth == 32768):
                            self.comb += self.dout_B[(i*1):((i*1)+1)].eq(Cat(self.bram_out_B[i][0:1]))
                
                # True Dual Port RAM
                elif (memory_type == "True_Dual_Port"):
                    self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)).Else(self.wen_A1.eq(0))
                    self.comb += If((self.wen_B == 1), self.wen_B1.eq(1)).Else(self.wen_B1.eq(0))
                    for i in range(m):
                        if (write_depth <= 1024):
                            self.comb += self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[i][0:36]))
                            self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][0:36]))
                        elif (write_depth > 1024 and write_depth <= 2048):
                            self.comb += self.dout_A[(i*18):((i*18)+18)].eq(Cat(self.bram_out_A[i][0:18]))
                            self.comb += self.dout_B[(i*18):((i*18)+18)].eq(Cat(self.bram_out_B[i][0:18]))
                        elif (write_depth > 2048 and write_depth <= 4096):
                            if data_width > 8:
                                if (m == (i+1)):
                                    if (y == i*9):
                                        self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8]))
                                        self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8]))
                                    else:
                                        self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.bram_out_A[i][16]))
                                        self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.bram_out_B[i][16]))
                                else:
                                    self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.bram_out_A[i][16]))
                                    self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:8], self.bram_out_B[i][16]))
                            else:
                                self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:data_width]))
                                self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][0:data_width]))
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
                    self.comb += self.address_A[0:10].eq(self.addr_A[0:10])
                    cases = {}
                    case_output = {}
                    for i in range(m):
                        if write_depth < 1024:
                            self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                        else:
                            cases[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], cases)
                    for i in range(m):
                        case_output[i] = self.dout_A.eq(self.bram_out_A[i])
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A_reg[0:msb-10], case_output)
                    else:
                        self.comb += self.dout_A.eq(self.bram_out_A[0])
                    for i in range(m):
                        if write_depth > 1024:
                            self.sync += If((self.addr_A[10:msb] == i), self.addr_A_reg[0:msb-10].eq(i))
                
                # Simple Dual Port RAM
                elif (memory_type == "Simple_Dual_Port"):
                    self.comb += self.address_A[0:10].eq(self.addr_A[0:10])
                    self.comb += self.address_B[0:10].eq(self.addr_B[0:10])
                    case1 = {}
                    if write_depth < 1024:
                        self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1)))
                    for i in range(m):
                        case1[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_A[10:msb], case1)
                    else:
                        self.comb += self.dout_B.eq(self.bram_out_B[0])
                    case2 = {}
                    for i in range(m):
                        case2[i] = self.dout_B.eq(self.bram_out_B[i])
                    if (write_depth > 1024):
                        self.comb += Case(self.addr_B_reg[0:msb-10], case2)
                    for i in range(m):
                        if write_depth > 1024:
                            if common_clk == 1:
                                self.sync += If((self.addr_B[10:msb] == i), self.addr_B_reg[0:msb-10].eq(i))
                            else:
                                self.sync.clk2 += If((self.addr_B[10:msb] == i), self.addr_B_reg[0:msb-10].eq(i))
                    
                # True Dual Port RAM
                elif (memory_type == "True_Dual_Port"):
                    self.comb += self.address_A[0:10].eq(self.addr_A[0:10])
                    self.comb += self.address_B[0:10].eq(self.addr_B[0:10])
                    case1 = {}
                    case3 = {}
                    if write_depth < 1024:
                        self.comb += If((self.wen_A == 1), (self.wen_A1.eq(1)))
                        self.comb += If((self.wen_B == 1), (self.wen_B1.eq(1)))
                    for i in range(m):
                        case1[i] = If((self.wen_A == 1), (self.wen_A1.eq(1 << i)))
                    
                    for i in range(m):
                        case1[i] = (If((self.wen_A == 1), self.wen_A1.eq(1 << i)))
                        case3[i] =   self.dout_A.eq(self.bram_out_A[i])
                    if (write_depth > 1024):
                        
                        self.comb += Case(self.addr_A[10:msb], case1)
                        self.comb += Case(self.addr_A_reg[0:msb-10], case3)
                    else:
                        self.comb += self.dout_A.eq(self.bram_out_A[0])
                    case2 = {}
                    case4 = {}
                    for i in range(m):
                        case2[i] = (If((self.wen_B == 1), self.wen_B1.eq(1 << i)))
                        case4[i] =  self.dout_B.eq(self.bram_out_B[i])
                    if (write_depth > 1024):
                        
                        self.comb += Case(self.addr_B[10:msb], case2)
                        self.comb += Case(self.addr_B_reg[0:msb-10], case4)
                    else:
                        self.comb += self.dout_B.eq(self.bram_out_B[0])
                    for i in range(m):
                        if write_depth > 1024:
                            if common_clk == 1:
                                self.sync += If((self.addr_A[10:msb] == i), self.addr_A_reg[0:msb-10].eq(i))
                                self.sync += If((self.addr_B[10:msb] == i), self.addr_B_reg[0:msb-10].eq(i))
                            else:
                                self.sync.clk1 += If((self.addr_A[10:msb] == i), self.addr_A_reg[0:msb-10].eq(i))
                                self.sync.clk2 += If((self.addr_B[10:msb] == i), self.addr_B_reg[0:msb-10].eq(i))

            # Memory Initialization Function Calling
            k=0
            init = self.memory_init(file_path, file_extension)
            
            # Single Port RAM
            if (memory_type == "Single_Port"):
                # Number of BRAMS
                for i in range(n):
                    if (n == (i+1)):
                        if (y > 18):
                            write_data_A1   = self.din_A[(i*36):((i*36)+18)]
                            write_data_A2   = Cat(self.din_A[(((i*36)+18)):((i*36)+36)])
                        else:
                            write_data_A1   = Cat(self.din_A[36*(n-1):data_width])
                            write_data_A2   = 0
                    else:
                        if (data_width > 36):
                            write_data_A1   = self.din_A[(i*36):((i*36)+18)]
                            write_data_A2   = self.din_A[((i*36)+18):((i*36)+36)]
                    
                    # if (write_depth % 1024 == 0):
                    if (write_depth == 1024):
                        w_mode_a1 = "110"
                        w_mode_b1 = "000"
                        w_mode_a2 = "110"
                        w_mode_b2 = "000"
                        r_mode_a1 = "110"
                        r_mode_b1 = "000"
                        r_mode_a2 = "110"
                        r_mode_b2 = "000"
                        split     = '0'
                        address = Cat(Replicate(0,5), self.addr_A[0:msb])
                    elif (write_depth == 2048):
                        w_mode_a1 = "010"
                        w_mode_b1 = "000"
                        w_mode_a2 = "010"
                        w_mode_b2 = "000"
                        r_mode_a1 = "010"
                        r_mode_b1 = "000"
                        r_mode_a2 = "010"
                        r_mode_b2 = "000"
                        split     = '0'
                        address = Cat(Replicate(0,4), self.addr_A[0:msb])
                    elif (write_depth == 4096):
                        w_mode_a1 = "100"
                        w_mode_b1 = "000"
                        w_mode_a2 = "100"
                        w_mode_b2 = "000"
                        r_mode_a1 = "100"
                        r_mode_b1 = "000"
                        r_mode_a2 = "100"
                        r_mode_b2 = "000"
                        split     = '0'
                        address = Cat(Replicate(0,3), self.addr_A[0:msb])
                    elif (write_depth == 8192):
                        w_mode_a1 = "001"
                        w_mode_b1 = "000"
                        w_mode_a2 = "001"
                        w_mode_b2 = "000"
                        r_mode_a1 = "001"
                        r_mode_b1 = "000"
                        r_mode_a2 = "001"
                        r_mode_b2 = "000"
                        split     = '0'
                        address = Cat(Replicate(0,2), self.addr_A[0:msb])
                    elif (write_depth == 16384):
                        w_mode_a1 = "011"
                        w_mode_b1 = "000"
                        w_mode_a2 = "011"
                        w_mode_b2 = "000"
                        r_mode_a1 = "011"
                        r_mode_b1 = "000"
                        r_mode_a2 = "011"
                        r_mode_b2 = "000"
                        split     = '0'
                        address = Cat(Replicate(0,1), self.addr_A[0:msb])
                    elif (write_depth == 32768):
                        w_mode_a1 = "101"
                        w_mode_b1 = "000"
                        w_mode_a2 = "101"
                        w_mode_b2 = "000"
                        r_mode_a1 = "101"
                        r_mode_b1 = "000"
                        r_mode_a2 = "101"
                        r_mode_b2 = "000"
                        split     = '0'
                        address = self.addr_A[0:msb]
                    else:
                        address = Cat(Replicate(0,5), self.address_A[0:10])
                        w_mode_a1 = "110"
                        w_mode_b1 = "000"
                        w_mode_a2 = "110"
                        w_mode_b2 = "000"
                        r_mode_a1 = "110"
                        r_mode_b1 = "000"
                        r_mode_a2 = "110"
                        r_mode_b2 = "000"
                        split     = '0'
                        # Mode Bits for other Full Memories
                        # if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                        #     w_mode_a1 = "101"
                        #     w_mode_b1 = "000"
                        #     w_mode_a2 = "101"
                        #     w_mode_b2 = "000"
                        #     r_mode_a1 = "101"
                        #     r_mode_b1 = "000"
                        #     r_mode_a2 = "101"
                        #     r_mode_b2 = "000"
                        #     split     = '1'
                        #     # address = Cat(self.address_A[0:10], Replicate(0,5))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        #     w_mode_a1 = "011"
                        #     w_mode_b1 = "000"
                        #     w_mode_a2 = "011"
                        #     w_mode_b2 = "000"
                        #     r_mode_a1 = "011"
                        #     r_mode_b1 = "000"
                        #     r_mode_a2 = "011"
                        #     r_mode_b2 = "000"
                        #     split     = '1'
                        #     # address = Cat(Replicate(0,1), self.address_A[0:10], Replicate(0,4))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        #     w_mode_a1 = "001"
                        #     w_mode_b1 = "000"
                        #     w_mode_a2 = "001"
                        #     w_mode_b2 = "000"
                        #     r_mode_a1 = "001"
                        #     r_mode_b1 = "000"
                        #     r_mode_a2 = "001"
                        #     r_mode_b2 = "000"
                        #     split     = '1'
                        #     # address = Cat(Replicate(0,2), self.address_A[0:10], Replicate(0,3))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        #     w_mode_a1 = "100"
                        #     w_mode_b1 = "000"
                        #     w_mode_a2 = "100"
                        #     w_mode_b2 = "000"
                        #     r_mode_a1 = "100"
                        #     r_mode_b1 = "000"
                        #     r_mode_a2 = "100"
                        #     r_mode_b2 = "000"
                        #     split     = '1'
                        #     # address = Cat(Replicate(0,3), self.address_A[0:10], Replicate(0,2))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        #     w_mode_a1 = "010"
                        #     w_mode_b1 = "000"
                        #     w_mode_a2 = "010"
                        #     w_mode_b2 = "000"
                        #     r_mode_a1 = "010"
                        #     r_mode_b1 = "000"
                        #     r_mode_a2 = "010"
                        #     r_mode_b2 = "000"
                        #     split     = '1'
                        #     # address = Cat(Replicate(0,4), self.address_A[0:10], Replicate(0,1))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        #     w_mode_a1 = "110"
                        #     w_mode_b1 = "000"
                        #     w_mode_a2 = "110"
                        #     w_mode_b2 = "000"
                        #     r_mode_a1 = "110"
                        #     r_mode_b1 = "000"
                        #     r_mode_a2 = "110"
                        #     r_mode_b2 = "000"
                        #     split     = '0'
                            # address = Cat(Replicate(0,5), self.address_A[0:10])
                    
                    # Byte Enable 
                    if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)]) > 8):
                        ben_A = 3
                    else:
                        ben_A = 1
                    
                    # Mode Bits Calculations
                    mode = int ("0{}{}{}{}00000000000000000000000000000{}{}{}{}00000000000000000000000000{}".format(r_mode_a1, r_mode_b1, w_mode_a1, w_mode_b1, r_mode_a2, r_mode_b2, w_mode_a2, w_mode_b2, split))
                    mode_bits = Instance.PreformattedParam("81'b{:d}".format(mode))
                    
                    for j in range(m):
                        if (file_path == "") or (self.line_count == 0):
                            value = 'x'
                        else:
                            if write_depth in [1024, 2048, 4096, 8192, 16384, 32768]:
                                value = init[j]
                            else:
                                value = init[k]
                                k=k+1
                                
                        init_i = Instance.PreformattedParam("36864'b{}".format(value))
                        
                        if (write_depth == 1024):
                            if (m == (j+1)):
                                if (z > 18):
                                    write_data_A1   = self.din_A[(j*36):((j*36)+18)]
                                    write_data_A2   = self.din_A[(((j*36)+18)):((j*36)+36)]
                                else:
                                    write_data_A1   = self.din_A[36*(m-1):data_width]
                                    write_data_A2   = 0
                            else:
                                if (data_width > 36):
                                    write_data_A1   = self.din_A[(j*36):((j*36)+18)]
                                    write_data_A2   = self.din_A[((j*36)+18):((j*36)+36)]

                        elif (write_depth == 2048):
                            write_data_A1 = self.din_A[(j*18):((j*18)+18)]
                            write_data_A2 = 0
                            
                        elif (write_depth == 4096):
                            if data_width > 8:
                                if (m == (j+1)):
                                    if (y == (j+1)*9):
                                        write_data_A1 = Cat(self.din_A[(j*9):((j*9)+8)], Replicate(0,8), self.din_A[(j*9)+8])
                                        write_data_A2 = 0
                                    else:
                                        write_data_A1 = self.din_A[(j*9):y]
                                        write_data_A2 = 0
                                else:
                                    write_data_A1 = Cat(self.din_A[(j*9):((j*9)+8)], Replicate(0,8), self.din_A[(j*9)+8])
                                    write_data_A2 = 0
                            else:
                                write_data_A1 = self.din_A[0:data_width]
                                write_data_A2 = 0
                            
                        elif (write_depth == 8192):
                            write_data_A1 = self.din_A[(j*4):((j*4)+4)]
                            write_data_A2 = 0
                        
                        if (write_depth == 16384):
                            write_data_A1 = self.din_A[(j*2):((j*2)+2)]
                            write_data_A2 = 0
                            
                        if (write_depth == 32768):
                            write_data_A1 = self.din_A[(j*1):((j*1)+1)]
                            write_data_A2 = 0
                            
                        # for j in range(m):
                        if (write_depth == 1024 or write_depth == 2048 or write_depth == 4096 or write_depth == 8192 or write_depth == 16384 or write_depth == 32768):
                            wen = self.wen_A1
                        else:
                            wen = self.wen_A1[j]
                        
                        read_data_A1   = self.bram_out_A[j][(i*36):((i*36)+18)]
                        read_data_A2   = self.bram_out_A[j][((i*36)+18):((i*36)+36)]
                        
                        self.write_data_A1 = write_data_A1
                        self.write_data_A2 = write_data_A2
                        
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
                        i_CLK_A2        = ClockSignal(),
                        i_WEN_A1        = wen,
                        i_REN_A1        = self.ren_A,
                        i_BE_A1         = ben_A,
                        i_ADDR_A1       = address,
                        i_WDATA_A1      = write_data_A1,
                        o_RDATA_A1      = read_data_A1,
                        i_WEN_A2        = wen,
                        i_REN_A2        = self.ren_A,
                        i_BE_A2         = ben_A,
                        i_ADDR_A2       = address,
                        i_WDATA_A2      = write_data_A2,
                        o_RDATA_A2      = read_data_A2
                )

            # Simple Dual Port RAM
            elif (memory_type == "Simple_Dual_Port"):
                y = data_width - 36*(n-1)
                for i in range(n):
                    if (n == (i+1)):
                        if (y > 18):
                            write_data_A1   = self.din_A[(i*36):((i*36)+18)]
                            write_data_A2   = self.din_A[(((i*36)+18)):((i*36)+36)]
                        else:
                            write_data_A1   = self.din_A[36*(n-1):data_width]
                            write_data_A2   = 0
                    else:
                        if (data_width > 36):
                            write_data_A1   = self.din_A[(i*36):((i*36)+18)]
                            write_data_A2   = self.din_A[((i*36)+18):((i*36)+36)]
                    
                    # if (write_depth % 1024 == 0):
                    if (write_depth == 1024):
                        w_mode_a1 = "110"
                        w_mode_b1 = "110"
                        w_mode_a2 = "110"
                        w_mode_b2 = "110"
                        r_mode_a1 = "110"
                        r_mode_b1 = "110"
                        r_mode_a2 = "110"
                        r_mode_b2 = "110"
                        split     = '0'
                        address_A = Cat(Replicate(0,5), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:msb])
                    elif (write_depth == 2048):
                        w_mode_a1 = "010"
                        w_mode_b1 = "010"
                        w_mode_a2 = "010"
                        w_mode_b2 = "010"
                        r_mode_a1 = "010"
                        r_mode_b1 = "010"
                        r_mode_a2 = "010"
                        r_mode_b2 = "010"
                        split     = '0'
                        address_A = Cat(Replicate(0,4), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,4), self.addr_B[0:msb])
                    elif (write_depth == 4096):
                        w_mode_a1 = "100"
                        w_mode_b1 = "100"
                        w_mode_a2 = "100"
                        w_mode_b2 = "100"
                        r_mode_a1 = "100"
                        r_mode_b1 = "100"
                        r_mode_a2 = "100"
                        r_mode_b2 = "100"
                        split     = '0'
                        address_A = Cat(Replicate(0,3), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,3), self.addr_B[0:msb])
                    elif (write_depth == 8192):
                        w_mode_a1 = "001"
                        w_mode_b1 = "001"
                        w_mode_a2 = "001"
                        w_mode_b2 = "001"
                        r_mode_a1 = "001"
                        r_mode_b1 = "001"
                        r_mode_a2 = "001"
                        r_mode_b2 = "001"
                        split     = '0'
                        address_A = Cat(Replicate(0,2), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,2), self.addr_B[0:msb])
                    elif (write_depth == 16384):
                        w_mode_a1 = "011"
                        w_mode_b1 = "011"
                        w_mode_a2 = "011"
                        w_mode_b2 = "011"
                        r_mode_a1 = "011"
                        r_mode_b1 = "011"
                        r_mode_a2 = "011"
                        r_mode_b2 = "011"
                        split     = '0'
                        address_A = Cat(Replicate(0,1), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,1), self.addr_B[0:msb])
                    elif (write_depth == 32768):
                        w_mode_a1 = "101"
                        w_mode_b1 = "101"
                        w_mode_a2 = "101"
                        w_mode_b2 = "101"
                        r_mode_a1 = "101"
                        r_mode_b1 = "101"
                        r_mode_a2 = "101"
                        r_mode_b2 = "101"
                        split     = '0'
                        address_A = self.addr_A[0:msb]
                        address_B = self.addr_B[0:msb]
                    else:
                        # Mode Bits
                        # Port A
                        w_mode_a1 = "110"
                        w_mode_a2 = "110"
                        r_mode_a1 = "000"
                        r_mode_a2 = "000"
                        split     = '0'
                        address_A = Cat(Replicate(0,5), self.address_A[0:10])
                        
                        # Port B
                        w_mode_b1 = "000"
                        w_mode_b2 = "000"
                        r_mode_b1 = "110"
                        r_mode_b2 = "110"
                        split     = '0'
                        address_B = Cat(Replicate(0,5), self.address_B[0:10])
                        
                        # if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                        #     w_mode_a1 = "101"
                        #     w_mode_a2 = "101"
                        #     r_mode_a1 = "000"
                        #     r_mode_a2 = "000"
                        #     split     = '1'
                        #     address_A = Cat(self.address_A[0:10], Replicate(0,5))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        #     w_mode_a1 = "011"
                        #     w_mode_a2 = "011"
                        #     r_mode_a1 = "000"
                        #     r_mode_a2 = "000"
                        #     split     = '1'
                        #     address_A = Cat(Replicate(0,1), self.address_A[0:10], Replicate(0,4))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        #     w_mode_a1 = "001"
                        #     w_mode_a2 = "001"
                        #     r_mode_a1 = "000"
                        #     r_mode_a2 = "000"
                        #     split     = '1'
                        #     address_A = Cat(Replicate(0,2), self.address_A[0:10], Replicate(0,3))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        #     w_mode_a1 = "100"
                        #     w_mode_a2 = "100"
                        #     r_mode_a1 = "000"
                        #     r_mode_a2 = "000"
                        #     split     = '1'
                        #     address_A = Cat(Replicate(0,3), self.address_A[0:10], Replicate(0,2))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        #     w_mode_a1 = "010"
                        #     w_mode_a2 = "010"
                        #     r_mode_a1 = "000"
                        #     r_mode_a2 = "000"
                        #     split     = '1'
                        #     address_A = Cat(Replicate(0,4), self.address_A[0:10], Replicate(0,1))

                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        #     w_mode_a1 = "110"
                        #     w_mode_a2 = "110"
                        #     r_mode_a1 = "000"
                        #     r_mode_a2 = "000"
                        #     split     = '0'
                        #     address_A = Cat(Replicate(0,5), self.address_A[0:10])

                        # # Port B
                        # if (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                        #     w_mode_b1 = "000"
                        #     w_mode_b2 = "000"
                        #     r_mode_b1 = "101"
                        #     r_mode_b2 = "101"
                        #     split     = '1'
                        #     address_B = Cat(self.address_B[0:10], Replicate(0,5))

                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        #     w_mode_b1 = "000"
                        #     w_mode_b2 = "000"
                        #     r_mode_b1 = "011"
                        #     r_mode_b2 = "011"
                        #     split     = '1'
                        #     address_B = Cat(Replicate(0,1), self.address_B[0:10], Replicate(0,4))

                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        #     w_mode_b1 = "000"
                        #     w_mode_b2 = "000"
                        #     r_mode_b1 = "001"
                        #     r_mode_b2 = "001"
                        #     split     = '1'
                        #     address_B = Cat(Replicate(0,2), self.address_B[0:10], Replicate(0,3))

                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        #     w_mode_b1 = "000"
                        #     w_mode_b2 = "000"
                        #     r_mode_b1 = "100"
                        #     r_mode_b2 = "100"
                        #     split     = '1'
                        #     address_B = Cat(Replicate(0,3), self.address_B[0:10], Replicate(0,2))

                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        #     w_mode_b1 = "000"
                        #     w_mode_b2 = "000"
                        #     r_mode_b1 = "010"
                        #     r_mode_b2 = "010"
                        #     split     = '1'
                        #     address_B = Cat(Replicate(0,4), self.address_B[0:10], Replicate(0,1))

                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        #     w_mode_b1 = "000"
                        #     w_mode_b2 = "000"
                        #     r_mode_b1 = "110"
                        #     r_mode_b2 = "110"
                        #     split     = '0'
                        #     address_B = Cat(Replicate(0,5), self.address_B[0:10])
                    
                    if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)]) > 8):
                        ben_A = 3
                    else:
                        ben_A = 1

                    mode = int ("0{}{}{}{}00000000000000000000000000000{}{}{}{}00000000000000000000000000{}".format(r_mode_a1, r_mode_b1, w_mode_a1, w_mode_b1, r_mode_a2, r_mode_b2, w_mode_a2, w_mode_b2, split))
                    mode_bits = Instance.PreformattedParam("81'b{:d}".format(mode))
                    init_i = Instance.PreformattedParam("36864'hx")

                    for j in range(m):
                        if (file_path == ""):
                            value = 'x'
                        else:
                            if write_depth in [1024, 2048, 4096, 8192, 16384, 32768]:
                                value = init[j]
                            else:
                                value = init[k]
                                k=k+1
                            
                        init_i = Instance.PreformattedParam("36864'b{}".format(value))
                        
                        if (write_depth == 1024):
                            if (m == (j+1)):
                                if (z > 18):
                                    write_data_A1   = self.din_A[(j*36):((j*36)+18)]
                                    write_data_A2   = self.din_A[(((j*36)+18)):((j*36)+36)]
                                else:
                                    write_data_A1   = self.din_A[36*(m-1):data_width]
                                    write_data_A2   = 0
                            else:
                                if (data_width > 36):
                                    write_data_A1   = self.din_A[(j*36):((j*36)+18)]
                                    write_data_A2   = self.din_A[((j*36)+18):((j*36)+36)]
                                    
                        elif (write_depth == 2048):
                                write_data_A1 = self.din_A[(j*18):((j*18)+18)]
                                write_data_A2 = 0
                            
                        elif (write_depth == 4096):
                            if data_width > 8:
                                if (m == (j+1)):
                                    if (y == (j+1)*9):
                                        write_data_A1 = Cat(self.din_A[(j*9):((j*9)+8)], Replicate(0,8), self.din_A[(j*9)+8])
                                        write_data_A2 = 0
                                    else:
                                        write_data_A1 = self.din_A[(j*9):y]
                                        write_data_A2 = 0
                                else:
                                    write_data_A1 = Cat(self.din_A[(j*9):((j*9)+8)], Replicate(0,8), self.din_A[(j*9)+8])
                                    write_data_A2 = 0
                            else:
                                write_data_A1 = self.din_A[0:data_width]
                                write_data_A2 = 0
                            
                        elif (write_depth == 8192):
                            write_data_A1 = self.din_A[(j*4):((j*4)+4)]
                            write_data_A2 = 0
                        
                        if (write_depth == 16384):
                            write_data_A1 = self.din_A[(j*2):((j*2)+2)]
                            write_data_A2 = 0
                            
                        if (write_depth == 32768):
                            write_data_A1 = self.din_A[(j*1):((j*1)+1)]
                            write_data_A2 = 0
                            
                        # for j in range(m):
                        if (write_depth == 1024 or write_depth == 2048 or write_depth == 4096 or write_depth == 8192 or write_depth == 16384 or write_depth == 32768):
                            wen = self.wen_A1
                        else:
                            wen = self.wen_A1[j]
                        
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
                            i_WEN_A1        = wen,
                            i_REN_B1        = self.ren_B,
                            i_BE_A1         = ben_A,
                            i_ADDR_A1       = address_A,
                            i_ADDR_B1       = address_B,
                            i_WDATA_A1      = write_data_A1,
                            o_RDATA_B1      = read_data_B1,
                            i_WEN_A2        = wen,
                            i_REN_B2        = self.ren_B,
                            i_BE_A2         = ben_A,
                            i_ADDR_A2       = address_A,
                            i_ADDR_B2       = address_B,
                            i_WDATA_A2      = write_data_A2,
                            o_RDATA_B2      = read_data_B2
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
                            i_WEN_A1        = wen,
                            i_REN_B1        = self.ren_B,
                            i_BE_A1         = ben_A,
                            i_ADDR_A1       = address_A,
                            i_ADDR_B1       = address_B,
                            i_WDATA_A1      = write_data_A1,
                            o_RDATA_B1      = read_data_B1,
                            i_WEN_A2        = wen,
                            i_REN_B2        = self.ren_B,
                            i_BE_A2         = ben_A,
                            i_ADDR_A2       = address_A,
                            i_ADDR_B2       = address_B,
                            i_WDATA_A2      = write_data_A2,
                            o_RDATA_B2      = read_data_B2
                        )

            # True Dual Port RAM
            elif (memory_type == "True_Dual_Port"):
                y = data_width - 36*(n-1)
                for i in range(n):
                    if (n == (i+1)):
                        if (y > 18):
                            write_data_A1   = self.din_A[(i*36):((i*36)+18)]
                            write_data_A2   = self.din_A[(((i*36)+18)):((i*36)+36)]
                            write_data_B1   = self.din_B[(i*36):((i*36)+18)]
                            write_data_B2   = self.din_B[(((i*36)+18)):((i*36)+36)]
                        else:
                            write_data_A1   = self.din_A[36*(n-1):data_width]
                            write_data_A2   = 0
                            write_data_B1   = self.din_B[36*(n-1):data_width]
                            write_data_B2   = 0
                    else:
                        if (data_width > 36):
                            write_data_A1   = self.din_A[(i*36):((i*36)+18)]
                            write_data_A2   = self.din_A[((i*36)+18):((i*36)+36)]
                            write_data_B1   = self.din_B[(i*36):((i*36)+18)]
                            write_data_B2   = self.din_B[((i*36)+18):((i*36)+36)]

                    # Mode_Bits
                    # if (write_depth % 1024 == 0):
                    if (write_depth == 1024):
                        w_mode_a1 = "110"
                        w_mode_b1 = "110"
                        w_mode_a2 = "110"
                        w_mode_b2 = "110"
                        r_mode_a1 = "110"
                        r_mode_b1 = "110"
                        r_mode_a2 = "110"
                        r_mode_b2 = "110"
                        split     = '0'
                        address_A = Cat(Replicate(0,5), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,5), self.addr_B[0:msb])
                    elif (write_depth == 2048):
                        w_mode_a1 = "010"
                        w_mode_b1 = "010"
                        w_mode_a2 = "010"
                        w_mode_b2 = "010"
                        r_mode_a1 = "010"
                        r_mode_b1 = "010"
                        r_mode_a2 = "010"
                        r_mode_b2 = "010"
                        split     = '0'
                        address_A = Cat(Replicate(0,4), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,4), self.addr_B[0:msb])
                    elif (write_depth == 4096):
                        w_mode_a1 = "100"
                        w_mode_b1 = "100"
                        w_mode_a2 = "100"
                        w_mode_b2 = "100"
                        r_mode_a1 = "100"
                        r_mode_b1 = "100"
                        r_mode_a2 = "100"
                        r_mode_b2 = "100"
                        split     = '0'
                        address_A = Cat(Replicate(0,3), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,3), self.addr_B[0:msb])
                    elif (write_depth == 8192):
                        w_mode_a1 = "001"
                        w_mode_b1 = "001"
                        w_mode_a2 = "001"
                        w_mode_b2 = "001"
                        r_mode_a1 = "001"
                        r_mode_b1 = "001"
                        r_mode_a2 = "001"
                        r_mode_b2 = "001"
                        split     = '0'
                        address_A = Cat(Replicate(0,2), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,2), self.addr_B[0:msb])
                    elif (write_depth == 16384):
                        w_mode_a1 = "011"
                        w_mode_b1 = "011"
                        w_mode_a2 = "011"
                        w_mode_b2 = "011"
                        r_mode_a1 = "011"
                        r_mode_b1 = "011"
                        r_mode_a2 = "011"
                        r_mode_b2 = "011"
                        split     = '0'
                        address_A = Cat(Replicate(0,1), self.addr_A[0:msb])
                        address_B = Cat(Replicate(0,1), self.addr_B[0:msb])
                    elif (write_depth == 32768):
                        w_mode_a1 = "101"
                        w_mode_b1 = "101"
                        w_mode_a2 = "101"
                        w_mode_b2 = "101"
                        r_mode_a1 = "101"
                        r_mode_b1 = "101"
                        r_mode_a2 = "101"
                        r_mode_b2 = "101"
                        split     = '0'
                        address_A = self.addr_A[0:msb]
                        address_B = self.addr_B[0:msb]
                    
                    else:
                        # Mode Bits
                        # Port A Write
                        w_mode_a1 = "110"
                        w_mode_a2 = "110"
                        address_A = Cat(Replicate(0,5), self.address_A[0:10])
                        
                        # Port A Read
                        r_mode_a1 = "110"
                        r_mode_a2 = "110"
                        
                        # Port B Write
                        w_mode_b1 = "110"
                        w_mode_b2 = "110"
                        address_B = Cat(Replicate(0,5), self.address_B[0:10])
                        
                        # Port B Read
                        r_mode_b1 = "110"
                        r_mode_b2 = "110"
                        
                        # Mode Bits
                        # Port A Write
                        # if (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                        #     w_mode_a1 = "101"
                        #     w_mode_a2 = "101"
                        #     address_A = Cat(self.address_A[0:10], Replicate(0,5))
                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        #     w_mode_a1 = "011"
                        #     w_mode_a2 = "011"
                        #     address_A = Cat(Replicate(0,1), self.address_A[0:10], Replicate(0,4))
                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        #     w_mode_a1 = "001"
                        #     w_mode_a2 = "001"
                        #     address_A = Cat(Replicate(0,2), self.address_A[0:10], Replicate(0,3))
                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        #     w_mode_a1 = "100"
                        #     w_mode_a2 = "100"
                        #     address_A = Cat(Replicate(0,3), self.address_A[0:10], Replicate(0,2))
                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        #     w_mode_a1 = "010"
                        #     w_mode_a2 = "010"
                        #     address_A = Cat(Replicate(0,4), self.address_A[0:10], Replicate(0,1))
                        # elif (len(self.din_A[(i*36):((i*36)+18)])+len(self.din_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        #     w_mode_a1 = "110"
                        #     w_mode_a2 = "110"
                        #     address_A = Cat(Replicate(0,5), self.address_A[0:10])

                        # # Port A Read
                        # if (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(2):
                        #     r_mode_a1 = "101"
                        #     r_mode_a2 = "101"
                        # elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        #     r_mode_a1 = "011"
                        #     r_mode_a2 = "011"
                        # elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        #     r_mode_a1 = "001"
                        #     r_mode_a2 = "001"
                        # elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        #     r_mode_a1 = "100"
                        #     r_mode_a2 = "100"
                        # elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        #     r_mode_a1 = "010"
                        #     r_mode_a2 = "010"
                        # elif (len(self.dout_A[(i*36):((i*36)+18)])+len(self.dout_A[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        #     r_mode_a1 = "110"
                        #     r_mode_a2 = "110"

                        # # Port B Write
                        # if (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                        #     w_mode_b1 = "101"
                        #     w_mode_b2 = "101"
                        #     address_B = Cat(self.address_B[0:10], Replicate(0,5))
                        # elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        #     w_mode_b1 = "011"
                        #     w_mode_b2 = "011"
                        #     address_B = Cat(Replicate(0,1), self.address_B[0:10], Replicate(0,4))
                        # elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        #     w_mode_b1 = "001"
                        #     w_mode_b2 = "001"
                        #     address_B = Cat(Replicate(0,2), self.address_B[0:10], Replicate(0,3))
                        # elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        #     w_mode_b1 = "100"
                        #     w_mode_b2 = "100"
                        #     address_B = Cat(Replicate(0,3), self.address_B[0:10], Replicate(0,2))
                        # elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        #     w_mode_b1 = "010"
                        #     w_mode_b2 = "010"
                        #     address_B = Cat(Replicate(0,4), self.address_B[0:10], Replicate(0,1))
                        # elif (len(self.din_B[(i*36):((i*36)+18)])+len(self.din_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        #     w_mode_b1 = "110"
                        #     w_mode_b2 = "110"
                        #     address_B = Cat(Replicate(0,5), self.address_B[0:10])

                        # # Port B Read
                        # if (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2):
                        #     r_mode_b1 = "101"
                        #     r_mode_b2 = "101"
                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(2,3):
                        #     r_mode_b1 = "011"
                        #     r_mode_b2 = "011"
                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(3,5):
                        #     r_mode_b1 = "001"
                        #     r_mode_b2 = "001"
                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(5,10):
                        #     r_mode_b1 = "100"
                        #     r_mode_b2 = "100"
                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(10,19):
                        #     r_mode_b1 = "010"
                        #     r_mode_b2 = "010"
                        # elif (len(self.dout_B[(i*36):((i*36)+18)])+len(self.dout_B[(((i*36)+18)):((i*36)+36)])) in range(19,37):
                        #     r_mode_b1 = "110"
                        #     r_mode_b2 = "110"
                    
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
                        if (file_path == ""):
                            value = 'x'
                        else:
                            if write_depth in [1024, 2048, 4096, 8192, 16384, 32768]:
                                value = init[j]
                            else:
                                value = init[k]
                                k=k+1
                        init_i = Instance.PreformattedParam("36864'b{}".format(value))
                        
                        if (write_depth == 1024):
                            if (m == (j+1)):
                                if (z > 18):
                                    write_data_A1   = self.din_A[(j*36):((j*36)+18)]
                                    write_data_A2   = self.din_A[(((j*36)+18)):((j*36)+36)]
                                    write_data_B1   = self.din_B[(j*36):((j*36)+18)]
                                    write_data_B2   = self.din_B[(((j*36)+18)):((j*36)+36)]
                                else:
                                    write_data_A1   = self.din_A[36*(m-1):data_width]
                                    write_data_A2   = 0
                                    write_data_B1   = self.din_B[36*(m-1):data_width]
                                    write_data_B2   = 0
                            else:
                                if (data_width > 36):
                                    write_data_A1   = self.din_A[(j*36):((j*36)+18)]
                                    write_data_A2   = self.din_A[((j*36)+18):((j*36)+36)]
                                    write_data_B1   = self.din_B[(j*36):((j*36)+18)]
                                    write_data_B2   = self.din_B[((j*36)+18):((j*36)+36)]
                                    
                        elif (write_depth == 2048):
                                write_data_A1 = self.din_A[(j*18):((j*18)+18)]
                                write_data_A2 = 0
                                write_data_B1 = self.din_B[(j*18):((j*18)+18)]
                                write_data_B2 = 0
                            
                        elif (write_depth == 4096):
                            if data_width > 8:
                                if (m == (j+1)):
                                    if (y == (j+1)*9):
                                        write_data_A1 = Cat(self.din_A[(j*9):((j*9)+8)], Replicate(0,8), self.din_A[(j*9)+8])
                                        write_data_A2 = 0
                                        write_data_B1 = Cat(self.din_B[(j*9):((j*9)+8)], Replicate(0,8), self.din_B[(j*9)+8])
                                        write_data_B2 = 0
                                    else:
                                        write_data_A1 = self.din_A[(j*9):y]
                                        write_data_A2 = 0
                                        write_data_B1 = self.din_B[(j*9):y]
                                        write_data_B2 = 0
                                else:
                                    write_data_A1 = Cat(self.din_A[(j*9):((j*9)+8)], Replicate(0,8), self.din_A[(j*9)+8])
                                    write_data_A2 = 0
                                    write_data_B1 = Cat(self.din_B[(j*9):((j*9)+8)], Replicate(0,8), self.din_B[(j*9)+8])
                                    write_data_B2 = 0
                            else:
                                write_data_A1 = self.din_A[0:data_width]
                                write_data_A2 = 0
                                write_data_B1 = self.din_B[0:data_width]
                                write_data_B2 = 0
                            
                        elif (write_depth == 8192):
                            write_data_A1 = self.din_A[(j*4):((j*4)+4)]
                            write_data_A2 = 0
                            write_data_B1 = self.din_B[(j*4):((j*4)+4)]
                            write_data_B2 = 0
                        
                        if (write_depth == 16384):
                            write_data_A1 = self.din_A[(j*2):((j*2)+2)]
                            write_data_A2 = 0
                            write_data_B1 = self.din_B[(j*2):((j*2)+2)]
                            write_data_B2 = 0
                            
                        if (write_depth == 32768):
                            write_data_A1 = self.din_A[(j*1):((j*1)+1)]
                            write_data_A2 = 0
                            write_data_B1 = self.din_B[(j*1):((j*1)+1)]
                            write_data_B2 = 0
                            
                        # for j in range(m):
                        if (write_depth == 1024 or write_depth == 2048 or write_depth == 4096 or write_depth == 8192 or write_depth == 16384 or write_depth == 32768):
                            wen_A = self.wen_A1
                            wen_B = self.wen_B1
                        else:
                            wen_A = self.wen_A1[j]
                            wen_B = self.wen_B1[j]
                            
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
                            i_WEN_A1        = wen_A,
                            i_WEN_B1        = wen_B,
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
                            i_WEN_A2        = wen_A,
                            i_WEN_B2        = wen_B,
                            i_REN_A2        = self.ren_A,
                            i_REN_B2        = self.ren_B,
                            i_BE_A2         = ben_A,
                            i_BE_B2         = ben_B,
                            i_ADDR_A2       = address_A,
                            i_ADDR_B2       = address_B,
                            i_WDATA_A2      = write_data_A2,
                            i_WDATA_B2      = write_data_B2,
                            o_RDATA_A2      = read_data_A2,
                            o_RDATA_B2      = read_data_B2
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
                            i_WEN_A1        = wen_A,
                            i_WEN_B1        = wen_B,
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
                            i_WEN_A2        = wen_A,
                            i_WEN_B2        = wen_B,
                            i_REN_A2        = self.ren_A,
                            i_REN_B2        = self.ren_B,
                            i_BE_A2         = ben_A,
                            i_BE_B2         = ben_B,
                            i_ADDR_A2       = address_A,
                            i_ADDR_B2       = address_B,
                            i_WDATA_A2      = write_data_A2,
                            i_WDATA_B2      = write_data_B2,
                            o_RDATA_A2      = read_data_A2,
                            o_RDATA_B2      = read_data_B2
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

