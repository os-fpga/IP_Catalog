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

from litex_wrapper.on_chip_memory_litex_wrapper_symmetric import OCM_SYM

# On Chip Memory ------------------------------------------------------------------------------------------
class OCM_ASYM(Module):
    
    def memory_init(self, file_path, file_extension, m, n, smaller_width, large_depth, memory_type, large_width):
        binary_data =  OCM_SYM.memory_converter(self, file_path, file_extension)
        
        sram        = {}
        INIT        = []
        INIT_PARITY = []
        
        # Empty File Path
        if (file_path == "") or (self.line_count == 0):
            return "0"
        
        # If File Path Exists
        if self.write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]:
            
            ###################################################################################################
            # Appending zeros
            if (len(self.binary_data) > large_depth):
                lines = large_depth
            else:
                lines = self.line_count
            
            if (smaller_width == 9):
                for i in range(lines):
                    if len(self.binary_data[i]) < smaller_width:
                        self.binary_data[i] = '0' * (smaller_width - len(self.binary_data[i])) + self.binary_data[i]
                    else:
                        self.binary_data[i] = self.binary_data[i]
                        
                # Appending '0' on vacant addresses
                x_data = large_depth - self.line_count
                for i in range(x_data):
                    self.binary_data.append((smaller_width + (9-(smaller_width % 9))) * '0')
            
            elif (smaller_width == 18):
                for i in range(lines):
                    if len(self.binary_data[i]) < smaller_width:
                        self.binary_data[i] = '0' * (smaller_width - len(self.binary_data[i])) + self.binary_data[i]
                    else:
                        self.binary_data[i] = self.binary_data[i]
                    
                # Appending '0' on vacant addresses
                x_data = large_depth - self.line_count
                for i in range(x_data):
                    self.binary_data.append((smaller_width + (18-(smaller_width % 18))) * '0')
            elif (smaller_width >= 36):
                for i in range(lines):
                    if len(self.binary_data[i]) < smaller_width:
                        self.binary_data[i] = '0' * (smaller_width - len(self.binary_data[i])) + self.binary_data[i]
                    else:
                        self.binary_data[i] = self.binary_data[i]
                    
                # Appending '0' on vacant addresses
                x_data = large_depth - self.line_count
                for i in range(x_data):
                    self.binary_data.append((smaller_width + (36-(smaller_width % 36))) * '0')
            
            ###################################################################################################
            # BRAM instance creation
            f = 0
            for i in range(n):
                for j in range(m):
                    sram[f"data_{f}"]          = []
                    sram[f"parity_{f}"]        = []  
                    sram[f"init_{f}"]          = []
                    sram[f"init_parity_{f}"]   = []
                    f = f+1
            
            ###################################################################################################
            # Write Wider for SP
            if memory_type == "Single_Port":
                if (self.write_width_A >= self.read_width_A):
                    if (self.write_depth_A == 1024):
                        # write width less than or equal to 18
                        if self.write_width_A <= 18:
                            for i in range(large_depth):
                                # data from .hex file
                                bits = self.binary_data[i] 
                                c = i % m # Toggling between BRAMs
                                if smaller_width == 9:
                                    bits = self.binary_data[i]  
                                    sram[f"data_{c}"].append(bits[1:9])  
                                    sram[f"parity_{c}"].append(bits[0])              
                                elif smaller_width == 18:
                                    bits = self.binary_data[i]
                                    sram[f"data_{c}"].append(bits[1:9]+bits[10:18]) 
                                    sram[f"parity_{c}"].append(bits[0]+bits[9])
                                else:
                                    bits = self.binary_data[i]
                                    sram[f"data_{c}"].append(bits[1:9]+bits[10:18]+bits[19:27]+bits[28:36])  
                                    sram[f"parity_{c}"].append(bits[0]+bits[9]+bits[18]+bits[27])

                        # write width greater than or equal to 36
                        else:
                            p = 0
                            q = 0
                            r = 0
                            for i in range(large_depth):
                                # data from .hex file
                                bits = self.binary_data[i] 
                                if ((i % 2) == 0): # for writing two lines data in 1 BRAM
                                    q = q +1
                                if ((i % 4) == 0): # for writing four lines data in 1 BRAM
                                    r = r+1
                                if (i % int(((m)*36)/smaller_width) == 0): # reset BRAM number
                                    p = 0
                                    q = 0
                                    r = 0
                                for x in range(math.ceil(smaller_width/36)-1, -1, -1): # BRAM ratio loop
                                    if smaller_width == 9: # in 1 BRAM 
                                        sram[f"data_{r}"].append(bits[1:9])  
                                        sram[f"parity_{r}"].append(bits[0]) 
                                    elif smaller_width == 18: # in 1 BRAM
                                        sram[f"data_{q}"].append(bits[1:9]+bits[10:18]) 
                                        sram[f"parity_{q}"].append(bits[0]+bits[9])
                                    elif smaller_width >= 36:
                                        sram[f"data_{p}"].append(bits[(x*36)+1:(x*36)+9]+bits[(x*36)+10:(x*36)+18]+bits[(x*36)+19:(x*36)+27]+bits[(x*36)+28:(x*36)+36])  
                                        sram[f"parity_{p}"].append(bits[(x*36)+0]+bits[(x*36)+9]+bits[(x*36)+18]+bits[(x*36)+27])
                                        p = p + 1 # incrementing BRAM number

                    elif (self.write_depth_A == 2048):
                        p = 0
                        r = 0
                        for i in range(large_depth):
                            bits = self.binary_data[i]
                            if ((i % 2) == 0):
                                r = r + 1
                            if (i % math.ceil((m*18)/smaller_width) == 0):
                                p = 0
                                r = 0
                            for x in range(math.ceil(smaller_width/18)-1, -1, -1):
                                if smaller_width == 9:
                                    sram[f"data_{r}"].append(bits[1:9])  
                                    sram[f"parity_{r}"].append(bits[0]) 
                                elif smaller_width >= 18:
                                    sram[f"data_{p}"].append(bits[(x*18)+1:(x*18)+9]+bits[(x*18)+10:(x*18)+18])  
                                    sram[f"parity_{p}"].append(bits[(x*18)+0]+bits[(x*18)+9])
                                    p = p + 1

                    elif (self.write_depth_A == 4096):
                        p = 0
                        for i in range(large_depth):
                            bits = self.binary_data[i]
                            if (i % int((m*9)/smaller_width) == 0):
                                p = 0
                            for x in range(math.ceil(smaller_width/9)-1, -1, -1):
                                if smaller_width >= 9:
                                    sram[f"data_{p}"].append(bits[(x*9)+1:(x*9)+9])  
                                    sram[f"parity_{p}"].append(bits[(x*9)+0])
                                    p = p + 1

                    elif (self.write_depth_A in [8192, 16384, 32768]):
                        for j in range(n):
                            for i in range(int(large_depth/n)):
                                
                                bits = self.binary_data[i+(j*int(large_depth/n))]

                                p = (i % m) + (j*m)
                                
                                q = int(smaller_width/9)

                                for x in range(q-1, -1, -1):
                                    if smaller_width == 9:
                                        sram[f"data_{p}"].append(bits[(x*9)+1:(x*9)+9])  
                                        sram[f"parity_{p}"].append(bits[(x*9)+0])
                                    elif smaller_width >= 18:
                                        c = (i % int(self.write_width_A/self.read_width_B))*q + (j*m) + x
                                        sram[f"data_{c}"].append(bits[((q-x-1)*9)+1:((q-x-1)*9)+9])  
                                        sram[f"parity_{c}"].append(bits[((q-x-1)*9)+0])

                ################################################################################################
                # Read Wider for SP
                elif (self.write_width_A < self.read_width_A):
                    if self.read_depth_A <= 1024:
                        if self.write_width_A >= 36:
                            width = 36
                        elif self.write_width_A == 18:
                            width = 18
                        elif self.write_width_A == 9:
                            width = 9
                    elif self.read_depth_A == 2048:
                        if self.write_width_A >= 18:
                            width = 18
                        elif self.write_width_A == 9:
                            width = 9
                    elif self.read_depth_A in [4096, 8192, 16384, 32768]:
                        width = 9

                    for i in range(large_depth):
                        bits = self.binary_data[i]
                        j = math.ceil(smaller_width/width)
                        for x in range(math.ceil(smaller_width/width)):
                            j = j - 1
                            if self.read_depth_A <= 1024:
                                if self.write_width_A >= 36:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*36)+1:(x*36)+9]+bits[(x*36)+10:(x*36)+18]+bits[(x*36)+19:(x*36)+27]+bits[(x*36)+28:(x*36)+36])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*36)+0]+bits[(x*36)+9]+bits[(x*36)+18]+bits[(x*36)+27])
                                elif self.write_width_A == 18:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*18)+1:(x*18)+9]+bits[(x*18)+10:(x*18)+18])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*18)+0]+bits[(x*18)+9])
                                elif self.write_width_A == 9:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*9)+1:(x*9)+9])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*9)+0])
                            elif self.read_depth_A == 2048:
                                if self.write_width_A >= 18:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*18)+1:(x*18)+9]+bits[(x*18)+10:(x*18)+18])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*18)+0]+bits[(x*18)+9])
                                elif self.write_width_A == 9:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*9)+1:(x*9)+9])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*9)+0])
                            elif self.read_depth_A in [4096, 8192, 16384, 32768]:
                                if self.write_width_A >= 9:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*9)+1:(x*9)+9])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*9)+0])
                
                
            ################################################################################################
            elif (memory_type == "Simple_Dual_Port"):
                if (self.write_width_A >= self.read_width_B): # Write Wider
                    if (self.write_depth_A == 1024):
                        # write width less than or equal to 18
                        if self.write_width_A <= 18:
                            for i in range(large_depth):
                                # data from .hex file
                                bits = self.binary_data[i] 
                                c = i % m # Toggling between BRAMs
                                if smaller_width == 9:
                                    bits = self.binary_data[i]  
                                    sram[f"data_{c}"].append(bits[1:9])  
                                    sram[f"parity_{c}"].append(bits[0])              
                                elif smaller_width == 18:
                                    bits = self.binary_data[i]
                                    sram[f"data_{c}"].append(bits[1:9]+bits[10:18]) 
                                    sram[f"parity_{c}"].append(bits[0]+bits[9])
                                else:
                                    bits = self.binary_data[i]
                                    sram[f"data_{c}"].append(bits[1:9]+bits[10:18]+bits[19:27]+bits[28:36])  
                                    sram[f"parity_{c}"].append(bits[0]+bits[9]+bits[18]+bits[27])
                        # write width greater than or equal to 36
                        else:
                            p = 0
                            q = 0
                            r = 0
                            for i in range(large_depth):
                                # data from .hex file
                                bits = self.binary_data[i] 
                                if ((i % 2) == 0): # for writing two lines data in 1 BRAM
                                    q = q +1
                                if ((i % 4) == 0): # for writing four lines data in 1 BRAM
                                    r = r+1
                                if (i % int(((m)*36)/smaller_width) == 0): # reset BRAM number
                                    p = 0
                                    q = 0
                                    r = 0
                                for x in range(math.ceil(smaller_width/36)-1, -1, -1): # BRAM ratio loop
                                    if smaller_width == 9: # in 1 BRAM 
                                        sram[f"data_{r}"].append(bits[1:9])  
                                        sram[f"parity_{r}"].append(bits[0]) 
                                    elif smaller_width == 18: # in 1 BRAM
                                        sram[f"data_{q}"].append(bits[1:9]+bits[10:18]) 
                                        sram[f"parity_{q}"].append(bits[0]+bits[9])
                                    elif smaller_width >= 36:
                                        sram[f"data_{p}"].append(bits[(x*36)+1:(x*36)+9]+bits[(x*36)+10:(x*36)+18]+bits[(x*36)+19:(x*36)+27]+bits[(x*36)+28:(x*36)+36])  
                                        sram[f"parity_{p}"].append(bits[(x*36)+0]+bits[(x*36)+9]+bits[(x*36)+18]+bits[(x*36)+27])
                                        p = p + 1 # incrementing BRAM number
                    
                    elif (self.write_depth_A == 2048):
                        p = 0
                        r = 0
                        for i in range(large_depth):
                            bits = self.binary_data[i]
                            if ((i % 2) == 0):
                                r = r + 1
                            if (i % math.ceil((m*18)/smaller_width) == 0):
                                p = 0
                                r = 0
                            for x in range(math.ceil(smaller_width/18)-1, -1, -1):
                                if smaller_width == 9:
                                    sram[f"data_{r}"].append(bits[1:9])  
                                    sram[f"parity_{r}"].append(bits[0]) 
                                elif smaller_width >= 18:
                                    sram[f"data_{p}"].append(bits[(x*18)+1:(x*18)+9]+bits[(x*18)+10:(x*18)+18])  
                                    sram[f"parity_{p}"].append(bits[(x*18)+0]+bits[(x*18)+9])
                                    p = p + 1
                                    
                    elif (self.write_depth_A == 4096):
                        p = 0
                        for i in range(large_depth):
                            bits = self.binary_data[i]
                            if (i % int((m*9)/smaller_width) == 0):
                                p = 0
                            for x in range(math.ceil(smaller_width/9)-1, -1, -1):
                                if smaller_width >= 9:
                                    sram[f"data_{p}"].append(bits[(x*9)+1:(x*9)+9])  
                                    sram[f"parity_{p}"].append(bits[(x*9)+0])
                                    p = p + 1
                                    
                    elif (self.write_depth_A in [8192, 16384, 32768]):
                        for j in range(n):
                            for i in range(int(large_depth/n)):
                                
                                bits = self.binary_data[i+(j*int(large_depth/n))]

                                p = (i % m) + (j*m)
                                
                                q = int(smaller_width/9)

                                for x in range(q-1, -1, -1):
                                    if smaller_width == 9:
                                        sram[f"data_{p}"].append(bits[(x*9)+1:(x*9)+9])  
                                        sram[f"parity_{p}"].append(bits[(x*9)+0])
                                    elif smaller_width >= 18:
                                        c = (i % int(self.write_width_A/self.read_width_B))*q + (j*m) + x
                                        sram[f"data_{c}"].append(bits[((q-x-1)*9)+1:((q-x-1)*9)+9])  
                                        sram[f"parity_{c}"].append(bits[((q-x-1)*9)+0])

                elif (self.write_width_A < self.read_width_B): # Read Wider      
                    if self.read_depth_B <= 1024:
                        if self.write_width_A >= 36:
                            width = 36
                        elif self.write_width_A == 18:
                            width = 18
                        elif self.write_width_A == 9:
                            width = 9
                    elif self.read_depth_B == 2048:
                        if self.write_width_A >= 18:
                            width = 18
                        elif self.write_width_A == 9:
                            width = 9
                    elif self.read_depth_B in [4096, 8192, 16384, 32768]:
                        width = 9
                        
                    for i in range(large_depth):
                        bits = self.binary_data[i]
                        j = math.ceil(smaller_width/width)
                        for x in range(math.ceil(smaller_width/width)):
                            j = j - 1
                            if self.read_depth_B <= 1024:
                                if self.write_width_A >= 36:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*36)+1:(x*36)+9]+bits[(x*36)+10:(x*36)+18]+bits[(x*36)+19:(x*36)+27]+bits[(x*36)+28:(x*36)+36])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*36)+0]+bits[(x*36)+9]+bits[(x*36)+18]+bits[(x*36)+27])
                                elif self.write_width_A == 18:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*18)+1:(x*18)+9]+bits[(x*18)+10:(x*18)+18])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*18)+0]+bits[(x*18)+9])
                                elif self.write_width_A == 9:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*9)+1:(x*9)+9])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*9)+0])
                            elif self.read_depth_B == 2048:
                                if self.write_width_A >= 18:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*18)+1:(x*18)+9]+bits[(x*18)+10:(x*18)+18])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*18)+0]+bits[(x*18)+9])
                                elif self.write_width_A == 9:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*9)+1:(x*9)+9])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*9)+0])
                            elif self.read_depth_B in [4096, 8192, 16384, 32768]:
                                if self.write_width_A >= 9:
                                    sram[f"data_{j*m+(i%m)}"].append(bits[(x*9)+1:(x*9)+9])  
                                    sram[f"parity_{j*m+(i%m)}"].append(bits[(x*9)+0])
                                    
            elif (memory_type == "True_Dual_Port"):
                r = 0
                q = 0
                y = math.ceil(large_depth/n)
                for a in range(n):
                    for i in range(y):
                        bits = self.binary_data[i + (y * a)]
                        if ((i % 2) == 0): # for writing two lines data in 1 BRAM
                            q = q +1
                        if ((i % 4) == 0): # for writing four lines data in 1 BRAM
                            r = r+1
                        if (i % int(((m)*36)/smaller_width) == 0): # reset BRAM number
                            q = 0
                            r = 0
                        d = math.ceil(smaller_width/36)
                        for x in range(d-1, -1, -1):
                            if smaller_width == 9: # in 1 BRAM 
                                e = r + a * m
                                sram[f"data_{e}"].append(bits[1:9])  
                                sram[f"parity_{e}"].append(bits[0]) 
                            elif smaller_width == 18: # in 1 BRAM
                                g = q + a * m
                                sram[f"data_{g}"].append(bits[1:9]+bits[10:18]) 
                                sram[f"parity_{g}"].append(bits[0]+bits[9])
                            elif smaller_width >= 36:
                                c = ((i%int(large_width/smaller_width))*d + (x+a*m))
                                sram[f"data_{c}"].append(bits[(x*36)+1:(x*36)+9]+bits[(x*36)+10:(x*36)+18]+bits[(x*36)+19:(x*36)+27]+bits[(x*36)+28:(x*36)+36])  
                                sram[f"parity_{c}"].append(bits[(x*36)+0]+bits[(x*36)+9]+bits[(x*36)+18]+bits[(x*36)+27])

            ##############################################################################################
            # Data allocation to corresponding BRAM
            f = 0
            for i in range(n):
                for j in range(m): # appending distributed data into corresponding BRAM
                    sram[f"init_{f}"]           = "".join(sram[f"data_{f}"][::-1]) # inverting indexing of list
                    sram[f"init_parity_{f}"]    = "".join(sram[f"parity_{f}"][::-1]) # inverting indexing of list
                    INIT.append(sram[f"init_{f}"])
                    INIT_PARITY.append(sram[f"init_parity_{f}"])
                    f = f+1
                    
            logging.info("Memory Initialized Successfully !!!")
            self.logger.info(f"===================================================")
            return INIT, INIT_PARITY
    
    def __init__(self, write_width_A, write_width_B, read_width_A, read_width_B, memory_type, common_clk, write_depth_A, read_depth_A, write_depth_B, read_depth_B, memory_mapping, file_path_hex, file_extension, byte_write_enable, op_mode):

        self.write_depth_A  = write_depth_A
        self.write_width_A  = write_width_A
        self.read_depth_A   = read_depth_A
        self.read_depth_B   = read_depth_B
        
        self.write_width_B  = write_width_B
        self.read_width_A   = read_width_A
        self.read_width_B   = read_width_B
        
        file_path = file_path_hex
        
        # Get/Check Parameters.
        # ---------------------
        self.logger = logging.getLogger("\tON CHIP MEMORY")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        self.logger.info(f"MEMORY_TYPE      : {memory_type}")
        
        if memory_type == "Single_Port":
            self.logger.info(f"WRITE_WIDTH_A    : {write_width_A}")
            self.logger.info(f"READ_WIDTH_A     : {read_width_A}")
            self.logger.info(f"WRITE_DEPTH_A    : {write_depth_A}")
            self.logger.info(f"READ_DEPTH_A     : {read_depth_A}")
        
        elif memory_type == "Simple_Dual_Port":
            self.logger.info(f"WRITE_WIDTH_A    : {write_width_A}")
            self.logger.info(f"READ_WIDTH_B     : {read_width_B}")
            self.logger.info(f"WRITE_DEPTH_A    : {write_depth_A}")
            self.logger.info(f"READ_DEPTH_B     : {read_depth_B}")
            
        elif memory_type == "True_Dual_Port":
            self.logger.info(f"WRITE_WIDTH_A    : {write_width_A}")
            self.logger.info(f"READ_WIDTH_A     : {read_width_A}")
            self.logger.info(f"WRITE_WIDTH_B    : {write_width_B}")
            self.logger.info(f"READ_WIDTH_B     : {read_width_B}")
            self.logger.info(f"WRITE_DEPTH_A    : {write_depth_A}")
            self.logger.info(f"READ_DEPTH_A     : {read_depth_A}")
            self.logger.info(f"WRITE_DEPTH_B    : {write_depth_B}")
            self.logger.info(f"READ_DEPTH_B     : {read_depth_B}")
        
        if memory_type != "Single_Port":
            self.logger.info(f"COMMON_CLK       : {common_clk}")
        
        self.logger.info(f"MEMORY_MAPPING       : {memory_mapping}")
        
        if (memory_type == "Single_Port"):
            write_depthA = max(write_depth_A, read_depth_A)
            self.addr_A     = Signal(math.ceil(math.log2(write_depthA)))
            msb_write       = math.ceil(math.log2(write_depth_A))
            msb_SP          = math.ceil(math.log2(write_depthA))
            self.address    = Signal(15)
            msb_read        = math.ceil(math.log2(write_depthA))
            
        elif (memory_type == "Simple_Dual_Port"):
            self.addr_A    = Signal(math.ceil(math.log2(write_depth_A)))
            self.addr_B    = Signal(math.ceil(math.log2(read_depth_B)))
            msb_read       = math.ceil(math.log2(read_depth_B))
        
        elif (memory_type == "True_Dual_Port"):
            self.address_A    = Signal(15)
            self.address_B    = Signal(15)
            depth_A = max(write_depth_A, read_depth_A)
            depth_B = max(write_depth_B, read_depth_B)
            self.addr_A    = Signal(math.ceil(math.log2(depth_A)))
            self.addr_B    = Signal(math.ceil(math.log2(depth_B)))

        msb_A = math.ceil(math.log2(write_depth_A))
        msb_B = math.ceil(math.log2(write_depth_B))
        
        # Port A din/dout
        self.din_A          = Signal(write_width_A)
        self.din_A_reg      = Signal(write_width_A)
        self.dout_A         = Signal(read_width_A)
        self.dout_A_        = Signal(read_width_A)
        self.dout_A_reg     = Signal(read_width_A)
        
        # Port B din/dout
        self.din_B          = Signal(write_width_B)
        self.din_B_reg      = Signal(write_width_B)
        self.dout_B         = Signal(read_width_B)
        self.dout_B_        = Signal(read_width_B)
        self.dout_B_reg     = Signal(read_width_B)
        
        # External write/read enables
        self.wen_A        = Signal(1)
        self.wen_A_reg    = Signal(1)
        self.ren_A        = Signal(1)
        self.ren_A_reg    = Signal(1)
        self.wen_B        = Signal(1)
        self.wen_B_reg    = Signal(1)
        self.ren_B        = Signal(1)
        self.ren_B_reg    = Signal(1)
        
        # Byte Enable
        self.be_A         = Signal(math.ceil(write_width_A/9))
        self.be_B         = Signal(math.ceil(write_width_B/9))
        
        if (memory_type == "Single_Port"):
            large_width   = max(write_width_A, read_width_A)
            smaller_width = min(write_width_A, read_width_A)
            large_depth   = max(write_depth_A, read_depth_A)

            if (write_width_A >= read_width_A):
                memory_width = write_width_A
                memory_depth = write_depth_A
            else:
                memory_width = read_width_A
                memory_depth = read_depth_A
                
        elif (memory_type == "Simple_Dual_Port"):
            large_width   = max(write_width_A, read_width_B)
            smaller_width = min(write_width_A, read_width_B)
            large_depth   = max(write_depth_A, read_depth_B)
            
            if (write_width_A >= read_width_B):
                memory_width = write_width_A
                memory_depth = write_depth_A
            else:
                memory_width = read_width_B
                memory_depth = read_depth_A

        elif (memory_type == "True_Dual_Port"):
            large_width   = max(write_width_A, read_width_A, write_width_B, read_width_B)
            smaller_width = min(write_width_A, read_width_A, write_width_B, read_width_B)
            large_depth   = max(write_depth_A, read_depth_A, write_depth_B, read_depth_B)
            
            
        MEMORY_SIZE = 36*1024
        
        if (memory_type == "Single_Port"):
            if (read_width_A > write_width_A):# Read Wider
                if read_depth_A in [1024, 2048, 4096]:
                    m = math.ceil(read_width_A/write_width_A)
                    n = math.ceil((((write_depth_A*write_width_A)/36)/(1024*m)))
                elif read_depth_A in [8192, 16384, 32768]:
                    n = math.ceil(write_width_A/9)
                    m = math.ceil((((write_depth_A*write_width_A)/9)/(4096*n)))
                else:
                    m = math.ceil(read_width_A/write_width_A)
                    n = math.ceil((((write_depth_A*write_width_A)/36)/(read_depth_A*m)))

            elif (write_width_A == read_width_A): # Symmetric
                if MEMORY_SIZE > (memory_depth * memory_width):
                    m = 1
                    n = 1
                else:
                    # OCM Instances.
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
            else: # write wider
                if MEMORY_SIZE > (memory_depth * memory_width):
                    m = 1
                    n = 1
                else:
                    # OCM Instances.
                    if (memory_depth == 1024):
                        m = math.ceil(memory_width/36)
                        n = 1  
                    elif (memory_depth == 2048):
                        m = math.ceil(memory_width/18)
                        n = 1
                    elif (memory_depth == 4096):
                        m = math.ceil(memory_width/9)
                        n = 1
                    elif write_depth_A in [8192, 16384, 32768]:
                        m = math.ceil(write_width_A/9)
                        n = math.ceil(write_depth_A/4096)
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
            
        elif (memory_type == "Simple_Dual_Port"):
            if (read_width_B > write_width_A):# Read Wider
                if read_depth_B in [1024, 2048, 4096]:
                    m = math.ceil(read_width_B/write_width_A)
                    n = math.ceil((((write_depth_A*write_width_A)/36)/(1024*m)))
                elif read_depth_B in [8192, 16384, 32768]:
                    n = math.ceil(write_width_A/9)
                    m = math.ceil((((write_depth_A*write_width_A)/9)/(4096*n)))
                else:
                    m = math.ceil(read_width_B/write_width_A)
                    n = math.ceil((((write_depth_A*write_width_A)/36)/(read_depth_B*m)))

            elif (write_width_A == read_width_B): # Symmetric
                if MEMORY_SIZE > (memory_depth * memory_width):
                    m = 1
                    n = 1
                else:
                    # OCM Instances.
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
            else: # write wider
                if MEMORY_SIZE > (memory_depth * memory_width):
                    m = 1
                    n = 1
                else:
                    # OCM Instances.
                    if (memory_depth == 1024):
                        m = math.ceil(memory_width/36)
                        n = 1  
                    elif (memory_depth == 2048):
                        m = math.ceil(memory_width/18)
                        n = 1
                    elif (memory_depth == 4096):
                        m = math.ceil(memory_width/9)
                        n = 1
                    elif write_depth_A in [8192, 16384, 32768]:
                        m = math.ceil(write_width_A/9)
                        n = math.ceil(write_depth_A/4096)
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
            
        elif (memory_type == "True_Dual_Port"):
            m = math.ceil(large_width/36)
            n = math.ceil(write_depth_A/1024)
        
        if file_path != "":
            k = 0
            init, init_parity = self.memory_init(file_path, file_extension, m, n, smaller_width, large_depth, memory_type, large_width)
                
        self.m = m # vertical memory
        self.n = n # horizontal memory
        
        # Write Enables internal
        self.wen_A1       = Signal(m*n)
        self.wen_B1       = Signal(m*n)
        
        if memory_type == "Simple_Dual_Port" and read_depth_B in [8192, 16384, 32768]:
            self.wen_A1       = Signal(m*n)
            self.wen_B1       = Signal(m*n)
        
        # Internal read Enables
        self.ren_A1       = Signal(m*n)
        self.ren_B1       = Signal(m*n)
        
        # read port signals
        self.bram_out_A = [Signal(32*n) for i in range(m)]
        self.bram_out_B = [Signal(32*n) for i in range(m)]
        self.rparity_A  = [Signal(4*n) for i in range(m)]
        self.rparity_B  = [Signal(4*n) for i in range(m)]
        
        self.addr_reg_A   = Signal(m)
        self.addr_reg_B   = Signal(m)
        
        if (write_depth_A > 1024):
            self.addr_A_reg = Signal(msb_A - 10)
            if (memory_type != "Single_Port"):
                self.addr_B_reg = Signal(msb_A - 10)
        
        # write enbale mux array
        wen_mux = {}
        
        # Synchronous/ Asynchronous Clock
        if ((common_clk == 1) and (memory_type != "Single_Port")):
            clock1 = ClockSignal("sys")
            clock2 = ClockSignal("sys")
        else:
            clock1 = ClockSignal("A")
            clock2 = ClockSignal("B")
        
        # Block RAM Mapping
        if (memory_mapping == "Block_RAM"):
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            # Single Port RAM
            if (memory_type == "Single_Port"):
                if (op_mode in ["No_Change", "Read_First"]):
                    self.comb += If((self.ren_A_reg), self.dout_A_.eq(self.dout_A)).Else(self.dout_A_.eq(self.dout_A_reg))
                    self.sync.A += If(self.ren_A_reg, self.dout_A_reg.eq(self.dout_A))
                    self.sync.A += self.ren_A_reg.eq(self.ren_A)
                else: # WRITE_FIRST
                    self.comb += If((self.wen_A_reg), self.dout_A_.eq(self.din_A_reg)).Else(self.dout_A_.eq(self.dout_A))
                    self.sync.A += self.wen_A_reg.eq(self.wen_A)
                    self.sync.A += self.din_A_reg.eq(self.din_A)
                    
                if (write_width_A == read_width_A): # Symmetric Memory
                    if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                        if n > 1:
                            self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic
                        else:
                            wen = self.wen_A
                        for i in range(m): # Output logic
                            if (write_depth_A == 1024):
                                self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0], self.bram_out_A[i][8:16], self.rparity_A[i][1],
                                                                self.bram_out_A[i][16:24], self.rparity_A[i][2], self.bram_out_A[i][24:32], self.rparity_A[i][3]))
                            if ( write_depth_A == 2048):
                                self.comb += self.dout_A[(i*18):(i*18)+18].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0], self.bram_out_A[i][8:16], self.rparity_A[i][1]))
                            elif (write_depth_A == 4096):
                                self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][0:8], self.rparity_A[i][0]))
                            elif (write_depth_A == 8192):
                                self.comb += self.dout_A[(i*4):((i*4)+4)].eq(Cat(self.bram_out_A[i][0:4]))
                            elif (write_depth_A == 16384):
                                self.comb += self.dout_A[(i*2):((i*2)+2)].eq(Cat(self.bram_out_A[i][0:2]))
                            elif (write_depth_A == 32768):
                                self.comb += self.dout_A[(i*1):((i*1)+1)].eq(Cat(self.bram_out_A[i][0:1]))
                
                # Write Wider Memory 
                elif (write_width_A > read_width_A): 
                    # Read Loop Calculations
                    ratio = math.ceil(math.log2(write_width_A / read_width_A))
                    if write_depth_A in [1024, 8192, 16384, 32768]:
                        read_loop = math.ceil(read_width_A / 36)
                        if (read_width_A <= 36):
                            ratio = int(math.ceil(math.log2(36 / read_width_A)))
                    elif write_depth_A == 2048:
                        read_loop = math.ceil(read_width_A / 18)
                        if (read_width_A <= 18):
                            ratio = int(math.ceil(math.log2(18/read_width_A)))
                            
                    elif write_depth_A == 4096:
                        read_loop = math.ceil(read_width_A / 9)
                        if (read_width_A <= 9):
                            ratio = int(math.ceil(math.log2(9/read_width_A)))
                            
                    # Output Logic for 1K, 2K, 4K
                    k = 0
                    for i in range(int(m/read_loop)):
                        for j in range(read_loop):
                            if (write_depth_A == 1024):
                                if (write_width_A > 36):
                                    self.comb += If((self.addr_reg_A == i), self.dout_A[(j*36):(j*36)+36].eq(Cat(self.bram_out_A[k+j][0:8], self.rparity_A[k+j][0], self.bram_out_A[k+j][8:16], self.rparity_A[k+j][1],
                                                    self.bram_out_A[k+j][16:24], self.rparity_A[k+j][2], self.bram_out_A[k+j][24:32], self.rparity_A[k+j][3])))
                                else:
                                    self.comb += self.dout_A[(j*36):(j*36)+36].eq(Cat(self.bram_out_A[k+j][0:8], self.rparity_A[k+j][0], self.bram_out_A[k+j][8:16], self.rparity_A[k+j][1],
                                                self.bram_out_A[k+j][16:24], self.rparity_A[k+j][2], self.bram_out_A[k+j][24:32], self.rparity_A[k+j][3]))
                            elif (write_depth_A == 2048):
                                if (write_width_A > 18):
                                    self.comb += If((self.addr_reg_A == i), self.dout_A[(j*18):(j*18)+18].eq(Cat(self.bram_out_A[k+j][0:8], self.rparity_A[k+j][0], self.bram_out_A[k+j][8:16], self.rparity_A[k+j][1])))
                                else:
                                    self.comb += self.dout_A[(j*18):(j*18)+18].eq(Cat(self.bram_out_A[k+j][0:8], self.rparity_A[k+j][0], self.bram_out_A[k+j][8:16], self.rparity_A[k+j][1]))
                            elif (write_depth_A == 4096):
                                if (write_width_A > 9):
                                    self.comb += If((self.addr_reg_A == i), self.dout_A[(j*9):(j*9)+9].eq(Cat(self.bram_out_A[k+j][0:8], self.rparity_A[k+j][0])))
                                else:
                                    self.comb += self.dout_A[(j*9):(j*9)+9].eq(Cat(self.bram_out_A[k+j][0:8], self.rparity_A[k+j][0]))
                        k = k + read_loop
                    
                    if (write_depth_A in [8192, 16384, 32768]):
                        for i in range(n):
                            for j in range(m):
                                if read_width_A >= 18:
                                    x = j % int(read_width_A/9)
                                    k =  j // int(read_width_A/9) + (i*int(m/int(read_width_A/9)))
                                    width = 9
                                    self.comb += If((self.addr_reg_A == k), self.dout_A[( x *width):( x *width)+width].eq(Cat(self.bram_out_A[j][(i*32):(i*32)+8], self.rparity_A[j][(i*4)])))
                                elif read_width_A == 9:
                                    k =  i * m + j
                                    width = 9
                                    self.comb += If((self.addr_reg_A == k), self.dout_A[(0*width):(0*width)+width].eq(Cat(self.bram_out_A[j][(i*32):(i*32)+8], self.rparity_A[j][(i*4)])))

                    # Read Enable, Write Enable and Read Registered Address Mux Generation
                    m_mux = math.ceil(math.log2(m*n))
                    dout_mux        = {}
                    ren_mux         = {}
                    addr_reg_mux    = {}
                    if (write_depth_A == 1024 and read_width_A <= 36):
                        for i in range(m):
                            if (op_mode in ["No_Change", "Read_First"]):
                                ren_mux[i] = self.ren_A1.eq(Cat(Replicate(0,i), self.ren_A))
                            addr_reg_mux[i] = self.addr_reg_A.eq(i)
                    elif (write_depth_A == 2048 and read_width_A <= 18):
                        for i in range(m):
                            if (op_mode in ["No_Change", "Read_First"]):
                                ren_mux[i] = self.ren_A1.eq(Cat(Replicate(0,i), self.ren_A))
                            addr_reg_mux[i] = self.addr_reg_A.eq(i)
                    elif (write_depth_A == 4096 and read_width_A <= 9):
                        for i in range(m):
                            if (op_mode in ["No_Change", "Read_First"]):
                                ren_mux[i] = self.ren_A1.eq(Cat(Replicate(0,i), self.ren_A))
                            addr_reg_mux[i] = self.addr_reg_A.eq(i)
                    elif (write_depth_A in [8192, 16384, 32768]):
                        if (read_width_A >= 9):
                            for i in range(n * int(write_width_A/read_width_A)):
                                if (op_mode in ["No_Change", "Read_First"]):
                                    ren_mux[i] = self.ren_A1.eq(Cat(Replicate(0,i), self.ren_A))
                                addr_reg_mux[i] = self.addr_reg_A.eq(i)
                                        
                        if (m > 1 or n > 1):
                            for j in range(n):
                                wen_mux[j] = self.wen_A1.eq(Cat(Replicate(0,j), self.wen_A))
                    else:
                        if (write_width_A > read_width_A):
                            for i in range(int(write_width_A/read_width_A)):
                                if (op_mode in ["No_Change", "Read_First"]):
                                    ren_mux[i] = self.ren_A1.eq(Cat(Replicate(0,i), self.ren_A))
                                addr_reg_mux[i] = self.addr_reg_A.eq(i)

                    # For more than 1 BRAMS
                    if (m > 1):
                        if (write_depth_A == 1024 and read_width_A <= 36):
                            self.sync.A += Case(self.addr_A[ratio:m_mux+ratio], addr_reg_mux)
                            self.comb += Case(self.addr_reg_A, dout_mux)
                            self.comb += Case(self.addr_A[ratio:m_mux+ratio], ren_mux)
                        elif (write_depth_A == 2048 and read_width_A <= 18):
                            self.sync.A += Case(self.addr_A[ratio:m_mux+ratio], addr_reg_mux)
                            self.comb += Case(self.addr_reg_A, dout_mux)
                            self.comb += Case(self.addr_A[ratio:m_mux+ratio], ren_mux)
                        elif (write_depth_A == 4096 and read_width_A <= 9):
                            self.sync.A += Case(self.addr_A[ratio:m_mux+ratio], addr_reg_mux)
                            self.comb += Case(self.addr_reg_A, dout_mux)
                            self.comb += Case(self.addr_A[ratio:m_mux+ratio], ren_mux)
                        elif (write_depth_A in [8192, 16384, 32768]):
                            read_depth = int(read_depth_A / (m*n))
                            if (read_width_A >= 9):
                                self.comb += Case(Cat(self.addr_A[0:math.ceil(math.log2(write_width_A/read_width_A))], self.addr_A[msb_read-math.ceil(math.log2(n)):msb_read]), ren_mux)
                                self.sync.A += Case(Cat(self.addr_A[0:math.ceil(math.log2(write_width_A/read_width_A))], self.addr_A[msb_read-math.ceil(math.log2(n)):msb_read]), addr_reg_mux)
                            self.comb += Case(self.addr_reg_A, dout_mux)
                            self.comb += Case(self.addr_A[12:msb_A], wen_mux)
                        else:
                            self.sync.A += Case(self.addr_A[0:ratio], addr_reg_mux)
                            self.comb += Case(self.addr_reg_A, dout_mux)
                            self.comb += Case(self.addr_A[0:ratio], ren_mux)
                
                # Read Wider Memory
                elif (read_width_A > write_width_A):
                    ratio = math.ceil(math.log2(read_width_A / write_width_A))
                    if write_depth_A in [1024, 8192, 16384, 32768]:
                        read_loop = math.ceil(read_width_A / 36)
                        
                    elif write_depth_A in [2048]:
                        read_loop = math.ceil(read_width_A / 18)
                    
                    elif write_depth_A in [4096]:
                        read_loop = math.ceil(read_width_A / 9)
                    
                    wen_mux         = {}
                    ren_mux         = {}
                    addr_reg_mux    = {}
                    dout_mux        = {}
                    k= 0
                    p = 0
                    for j in range(m):
                        wen_mux[j] = self.wen_A1.eq(Cat(Replicate(0,j), self.wen_A))
                        for i in range(n):
                            if read_depth_A <= 1024:
                                k = j * n + i
                                if (write_width_A >= 72):
                                    self.comb += self.dout_A[(k*36):(k*36)+36].eq(Cat(self.bram_out_A[j][(i*32)+0:(i*32)+8], self.rparity_A[j][(i*4)+0], self.bram_out_A[j][(i*32)+8:(i*32)+16], self.rparity_A[j][(i*4)+1],
                                                self.bram_out_A[j][(i*32)+16:(i*32)+24], self.rparity_A[j][(i*4)+2], self.bram_out_A[j][(i*32)+24:(i*32)+32], self.rparity_A[j][(i*4)+3]))
                                elif (write_width_A == 36):
                                    self.comb += self.dout_A[(j*36):(j*36)+36].eq(Cat(self.bram_out_A[j][0:8], self.rparity_A[j][0], self.bram_out_A[j][8:16], self.rparity_A[j][1],
                                                self.bram_out_A[j][16:24], self.rparity_A[j][2], self.bram_out_A[j][24:32], self.rparity_A[j][3]))
                                elif (write_width_A == 18):
                                    self.comb += self.dout_A[(j*18):(j*18)+18].eq(Cat(self.bram_out_A[j][0:8], self.rparity_A[j][0], self.bram_out_A[j][8:16], self.rparity_A[j][1]))
                                elif (write_width_A == 9):
                                    self.comb += self.dout_A[(j*9):(j*9)+9].eq(Cat(self.bram_out_A[j][0:8], self.rparity_A[j][0]))
                            elif read_depth_A == 2048:
                                k = j * n + i
                                if (write_width_A >= 18):
                                    self.comb += self.dout_A[(k*18):(k*18)+18].eq(Cat(self.bram_out_A[j][(i*32)+0:(i*32)+8], self.rparity_A[j][(i*4)+0], self.bram_out_A[j][(i*32)+8:(i*32)+16], self.rparity_A[j][(i*4)+1]))
                                elif (write_width_A == 9):
                                    self.comb += self.dout_A[(j*9):(j*9)+9].eq(Cat(self.bram_out_A[j][0:8], self.rparity_A[j][0]))
                            elif read_depth_A == 4096:
                                k = j * n + i
                                if (write_width_A >= 9):
                                    self.comb += self.dout_A[(k*9):(k*9)+9].eq(Cat(self.bram_out_A[j][(i*32)+0:(i*32)+8], self.rparity_A[j][(i*4)+0]))
                            elif read_depth_A >= 8192:
                                if read_depth_A == 8192:
                                    k = 0 if (j * n + i) < (int(m*n/2)) else 1
                                elif read_depth_A in [16384, 32768]:
                                    k = j // 2
                                x = (j * n + i) % (int(read_width_A/9))
                                self.comb += If((self.addr_reg_A == k), self.dout_A[(x*9):(x*9)+9].eq(Cat(self.bram_out_A[j][(i*32):(i*32)+8], self.rparity_A[j][(i*4)])))
                                wen_mux[j] = self.wen_A1.eq(Cat(Replicate(0,j), self.wen_A))
                    
                    if (read_depth_A >= 8192):
                        n_temp = int(read_depth_A/4096)
                        for i in range(n_temp):
                            if (op_mode in ["No_Change", "Read_First"]):
                                ren_mux[i] = self.ren_A1.eq(Cat(Replicate(0,i), self.ren_A))
                            dout_mux[i] = self.addr_reg_A.eq(i)
                            
                    if read_depth_A <= 1024 or read_depth_A in [2048, 4096]:
                        self.comb += Case(self.addr_A[0:ratio], wen_mux)
                    else:
                        self.comb += Case(Cat(self.addr_A[0:ratio], self.addr_A[msb_A-(math.ceil(math.log2(n_temp))):msb_A]), wen_mux)
                        self.comb += Case(self.addr_A[msb_read-(math.ceil(math.log2(n_temp))):msb_read], ren_mux)
                        self.sync.A += Case(self.addr_A[msb_read-(math.ceil(math.log2(n_temp))):msb_read], dout_mux)
                
                f = 0
                for i in range(n):  # horizontal memory
                    
                    if (write_width_A == read_width_A):
                        if (write_depth_A == 1024):
                            param_write_width_A = 36
                            param_read_width_A  = 36
                            address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                            address_B = Cat(Replicate(0,5), self.addr_A[0:10])
                        elif (write_depth_A == 2048):
                            param_write_width_A = 18
                            param_read_width_A  = 18
                            address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                            address_B = Cat(Replicate(0,4), self.addr_A[0:11])
                        elif (write_depth_A == 4096):
                            param_write_width_A = 9
                            param_read_width_A  = 9
                            address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                            address_B = Cat(Replicate(0,3), self.addr_A[0:12])
                        elif (write_depth_A == 8192):
                            param_write_width_A = 4
                            param_read_width_A  = 4
                            address_A = Cat(Replicate(0,2), self.addr_A[0:13])
                            address_B = Cat(Replicate(0,2), self.addr_A[0:13])
                        elif (write_depth_A == 16384):
                            param_write_width_A = 2
                            param_read_width_A  = 2
                            address_A = Cat(Replicate(0,1), self.addr_A[0:14])
                            address_B = Cat(Replicate(0,1), self.addr_A[0:14])
                        elif (write_depth_A == 32768):
                            param_write_width_A = 1
                            param_read_width_A  = 1
                            address_A = Cat(Replicate(0,0), self.addr_A[0:15])
                            address_B = Cat(Replicate(0,0), self.addr_A[0:15])
                        else: # memory size 36x1024 for other configurations
                            address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                            address_B = Cat(Replicate(0,5), self.addr_A[0:10])
                                
                    # Address and Modes Selection
                    elif (write_width_A > read_width_A):
                        read_depth = int(read_depth_A / (m*n))
                        if (write_depth_A == 1024):
                            param_write_width_A = 36
                            param_read_width_A  = 36
                            address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                            
                            if m == 1:
                                if write_width_A == 36:
                                    address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                                    param_write_width_A  = 36
                                elif write_width_A == 18:
                                    address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                                    param_write_width_A  = 18
                                elif write_width_A == 9:
                                    address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                                    param_write_width_A  = 9
                                
                                if read_width_A == 18:
                                    address_B = Cat(Replicate(0,4), self.addr_A[0:11])
                                    param_read_width_A  = 18
                                elif read_width_A == 9:
                                    address_B = Cat(Replicate(0,3), self.addr_A[0:12])
                                    param_read_width_A  = 9
                            else:
                                if (read_depth == 1024):
                                    address_B = Cat(Replicate(0,5), self.addr_A[ratio+m_mux:msb_SP])
                                    param_read_width_A  = 36
                                elif (read_depth == 2048):
                                    address_B = Cat(Replicate(0,4), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                                    param_read_width_A = 18
                                elif (read_depth == 4096):
                                    address_B = Cat(Replicate(0,3), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                                    param_read_width_A = 9
                                elif (read_depth == 8192):
                                    address_B = Cat(Replicate(0,3), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                                elif (read_depth == 16384):
                                    address_B = Cat(Replicate(0,2), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                                elif (read_depth == 32768):
                                    address_B = Cat(Replicate(0,1), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                                else: 
                                    address_B = Cat(Replicate(0,5), self.addr_A[ratio:msb_SP])
                                    param_read_width_A = 36

                        elif (write_depth_A == 2048):
                            param_write_width_A = 18
                            param_read_width_A  = 18
                            address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                            if (read_depth == 1024):
                                address_B = Cat(Replicate(0,4), self.addr_A[ratio:msb_SP])
                            elif (read_depth == 2048):
                                address_B = Cat(Replicate(0,4), self.addr_A[ratio+m_mux:msb_SP])
                                param_read_width_A = 18
                            elif (read_depth == 4096):
                                address_B = Cat(Replicate(0,3), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                                param_read_width_A = 9
                            elif (read_depth == 8192):
                                address_B = Cat(Replicate(0,3), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                                param_read_width_A = 9
                            elif (read_depth == 16384):
                                address_B = Cat(Replicate(0,2), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                            elif (read_depth == 32768):
                                address_B = Cat(Replicate(0,1), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                            else: 
                                address_B = Cat(Replicate(0,4), self.addr_A[ratio:msb_SP])
                                param_read_width_A = 18

                        elif (write_depth_A == 4096):
                            param_write_width_A = 9
                            param_read_width_A  = 9
                            address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                            if (read_depth == 1024):
                                address_B = Cat(Replicate(0,5), self.addr_A[ratio+m_mux:msb_SP])
                            elif (read_depth == 2048):
                                address_B = Cat(Replicate(0,4), self.addr_A[ratio+m_mux:msb_SP])
                            if (read_depth == 4096):
                                address_B = Cat(Replicate(0,3), self.addr_A[ratio+m_mux:msb_SP])
                                param_read_width_A = 9
                            elif (read_depth == 8192):
                                address_B = Cat(Replicate(0,3), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                            elif (read_depth == 16384):
                                address_B = Cat(Replicate(0,2), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                            elif (read_depth == 32768):
                                address_B = Cat(Replicate(0,1), self.addr_A[0:ratio], self.addr_A[ratio+m_mux:msb_SP])
                            else: 
                                address_B = Cat(Replicate(0,3), self.addr_A[ratio:msb_SP])
                                param_read_width_A = 9
                        
                        elif (write_depth_A in [8192, 16384, 32768]):
                            param_write_width_A = 9
                            param_read_width_A  = 9
                            address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                            address_B = Cat(Replicate(0,3), self.addr_A[math.ceil(math.log2(write_width_A/read_width_A)):msb_read-math.ceil(math.log2(n))])
                    
                    elif (read_width_A > write_width_A): 
                        
                        if read_depth_A <= 1024:
                            if (write_width_A >= 36):
                                param_write_width_A = 36
                                param_read_width_A  = 36
                                address_B = Cat(Replicate(0,5), self.addr_A[0:msb_read])
                                address_A = Cat(Replicate(0,5), self.addr_A[ratio:msb_A])   
                            elif (write_width_A == 18):
                                param_write_width_A = 18
                                param_read_width_A  = 18
                                address_B = Cat(Replicate(0,4), self.addr_A[0:msb_read])
                                address_A = Cat(Replicate(0,4), self.addr_A[ratio:msb_A])   
                            elif (write_width_A == 9):
                                param_write_width_A = 9
                                param_read_width_A  = 9
                                address_B = Cat(Replicate(0,3), self.addr_A[0:msb_read])
                                address_A = Cat(Replicate(0,3), self.addr_A[ratio:msb_A])

                        elif read_depth_A == 2048:
                            if (write_width_A >= 18):
                                param_write_width_A = 18
                                param_read_width_A  = 18
                                address_B = Cat(Replicate(0,4), self.addr_A[0:msb_read])
                                address_A = Cat(Replicate(0,4), self.addr_A[ratio:msb_A])   
                            elif (write_width_A == 9):
                                param_write_width_A = 9
                                param_read_width_A  = 9
                                address_B = Cat(Replicate(0,3), self.addr_A[0:msb_read])
                                address_A = Cat(Replicate(0,3), self.addr_A[ratio:msb_A])

                        elif read_depth_A in [4096, 8192, 16384]:
                            diff_depth = int(math.log2(read_depth_A/4096))
                            if (write_width_A >= 9):
                                param_write_width_A = 9
                                param_read_width_A  = 9
                                address_B = Cat(Replicate(0,3), self.addr_A[0:12])
                                address_A = Cat(Replicate(0,3), self.addr_A[ratio:msb_A-diff_depth])
                    
                    
                    for j in range(m): # vertical memory
                        
                        if (file_path == "") or (self.line_count == 0):
                            data    = '0'
                            parity  = '0'
                        else:
                            data        = hex(int(init[f], 2))[2:]          # hex conversion and removal of 0x from start of converted data
                            parity      = hex(int(init_parity[f], 2))[2:]   # hex conversion and removal of 0x from start of converted data
                            f = f + 1
                        
                        # read enable logic
                        if (write_width_A == read_width_A):
                            if read_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]:
                                ren = self.ren_A
                            else:
                                ren = self.ren_A1[j]
                        elif (write_width_A > read_width_A): # write wider
                            if write_depth_A in [1024, 2048, 4096]:
                                if (m > 1 or n > 1):
                                    ren = self.ren_A1[int(j/read_loop)]
                                else:
                                    ren = self.ren_A
                            else:
                                if (read_width_A >= 18):
                                    k =  j // int(read_width_A/9) + (i*int(m/int(read_width_A/9)))
                                    ren = self.ren_A1[k]
                                else:
                                    k = i * m + j
                                    ren = self.ren_A1[k]
                                    
                        elif (read_width_A >  write_width_A): # read wider
                            if read_depth_A in [8192]:
                                k = 0 if (j * n + i) < (int((m*n)/2)) else 1
                                ren = self.ren_A1[k]
                            elif read_depth_A in [16384, 32768]:
                                k = j // 2
                                ren = self.ren_A1[k]
                            else:
                                ren = self.ren_A
                        
                        # write enable logic
                        if (write_width_A == read_width_A): # symmetric
                            if write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]:
                                wen = self.wen_A
                            else:
                                wen = self.wen_A1[j]
                        elif (write_width_A > read_width_A): # write wider
                            if write_depth_A in [1024, 2048, 4096]:
                                wen = self.wen_A
                            else: # depth = 8K, 16K, 32K
                                k = i
                                wen = self.wen_A1[k]
                        elif (read_width_A > write_width_A): # read wider
                            wen = self.wen_A1[j]
                            
                        if (write_width_A > read_width_A):
                            if (write_depth_A == 1024):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*4):(j*4)+4]
                                else:
                                    be_A = Replicate(1, 4)
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
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*2):(j*2)+2]
                                else:
                                    be_A = Replicate(1, 4)
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

                            elif (write_depth_A in [4096]):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*1):(j*1)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                z = write_width_A - 9*(m-1)
                                if (m == (j+1)):
                                    if (z > 8):
                                        write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                        w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                    else:
                                        write_data_A = self.din_A[(j*9):((j*9)+8)]
                                        w_parity_A   = Replicate(0,4)
                                else:
                                    write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                            
                            elif write_depth_A in [8192, 16384, 32768]:
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*1):(j*1)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                        
                        # Read Wider
                        elif (read_width_A > write_width_A):
                            if (read_depth_A <= 1024):
                                if (write_width_A >= 36):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*4):(i*4)+4]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                                elif (write_width_A == 18):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*2):(i*2)+2]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*18):((i*18)+8)], self.din_A[(i*18)+9:((i*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((i*18)+8)], self.din_A[((i*18)+17)], Replicate(0,2))
                                elif (write_width_A == 9):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*1):(i*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*9):((i*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((i*9)+8)], Replicate(0,3))
                                    
                            elif (read_depth_A == 2048):
                                if (write_width_A >= 18):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*2):(i*2)+2]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*18):((i*18)+8)], self.din_A[(i*18)+9:((i*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((i*18)+8)], self.din_A[((i*18)+17)], Replicate(0,2))
                                elif (write_width_A == 9):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*1):(i*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*9):((i*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((i*9)+8)], Replicate(0,3))
                                    
                            elif (read_depth_A == 4096):
                                if (write_width_A >= 9):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*1):(i*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*9):((i*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((i*9)+8)], Replicate(0,3))
                            
                            elif (read_depth_A in [8192, 16384, 32768]):
                                if (write_width_A >= 9):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*1):(i*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*9):((i*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((i*9)+8)], Replicate(0,3))
                        
                        if (write_width_A == read_width_A): # Symmetric Memory
                            if (write_depth_A == 1024):
                                if (write_width_A >= 36):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(j*4):(j*4)+4]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(j*36):((j*36)+8)], self.din_A[(j*36)+9:((j*36)+17)], self.din_A[(j*36)+18:((j*36)+26)], self.din_A[(j*36)+27:((j*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((j*36)+8)], self.din_A[((j*36)+17)], self.din_A[((j*36)+26)], self.din_A[((j*36)+35)])
                                elif (write_width_A == 18):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(j*2):(j*2)+2]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A   = Cat(self.din_A[(j*18)+8], self.din_A[(j*18)+17], Replicate(0,2))
                                elif write_width_A == 9:
                                    if (byte_write_enable):
                                        be_A = self.be_A[(j*1):(j*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                    
                            elif (write_depth_A == 2048):
                                if write_width_A >= 18:
                                    if (byte_write_enable):
                                        be_A = self.be_A[(j*2):(j*2)+2]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A = Cat(self.din_A[(j*18):((j*18)+8)], self.din_A[(j*18)+9:((j*18)+17)])
                                    w_parity_A   = Cat(self.din_A[(j*18)+8], self.din_A[(j*18)+17], Replicate(0,2))
                                elif write_width_A == 9:
                                    if (byte_write_enable):
                                        be_A = self.be_A[(j*1):(j*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                            
                            elif (write_depth_A == 4096):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*1):(j*1)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                            
                            elif (write_depth_A == 8192):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j//2):(j//2)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A = self.din_A[(j*4):((j*4)+4)]
                                w_parity_A   = Replicate(0,4)

                            elif (write_depth_A == 16384):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j//4):(j//4)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A = self.din_A[(j*2):((j*2)+2)]
                                w_parity_A   = Replicate(0,4)

                            elif (write_depth_A == 32768):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j//8):(j//8)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A = self.din_A[(j*1):((j*1)+1)]
                                w_parity_A   = Replicate(0,4)
                        
                        if (op_mode == "Read_First"):
                            renA = ren
                        elif (op_mode == "No_Change" or op_mode == "Write_First"):
                            renA = ~self.wen_A
                        
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
                        i_REN_A     = renA,
                        i_REN_B     = 0,
                        i_BE_A      = be_A,
                        i_BE_B      = Replicate(0,4),
                        i_ADDR_A    = self.address,
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
                self.comb += If((self.wen_A), self.address.eq(address_A))
                self.comb += If((self.ren_A), self.address.eq(address_B))
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
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
                else: # WRITE_FIRST
                    self.comb += If((self.wen_A_reg), self.dout_B_.eq(self.din_A_reg)).Else(self.dout_B_.eq(self.dout_B))
                    if (common_clk == 1):
                        self.sync += self.wen_A_reg.eq(self.wen_A)
                        self.sync += self.din_A_reg.eq(self.din_A)
                    else:
                        self.sync.A += self.wen_A_reg.eq(self.wen_A)
                        self.sync.A += self.din_A_reg.eq(self.din_A)
                    
                if (write_width_A == read_width_B): # Symmetric
                    read_loop = m
                    y = write_width_A - 36*(n-1)
                    if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                        if n > 1:
                            self.comb += If((self.wen_A == 1), self.wen_A1.eq(1)) # write enable logic
                        else:
                            wen = self.wen_A
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
                        if (read_width_B > write_width_A): # read wider
                            ratio = math.ceil(math.log2(read_width_B / write_width_A))
                            if write_depth_A in [1024, 8192, 16384, 32768]:
                                read_loop = math.ceil(read_width_B / 36)
                                
                            elif write_depth_A in [2048]:
                                read_loop = math.ceil(read_width_B / 18)
                            
                            elif write_depth_A in [4096]:
                                read_loop = math.ceil(read_width_B / 9)
                        
                        elif (write_width_A > read_width_B):
                            
                            ratio = math.ceil(math.log2(write_width_A / read_width_B))
                            
                            if write_depth_A in [1024]:
                                read_loop = math.ceil(read_width_B / 36)
                                if (read_width_B <= 36):
                                    ratio = int(math.ceil(math.log2(36 / read_width_B)))

                            elif write_depth_A == 2048:
                                read_loop = math.ceil(read_width_B / 18)
                                if (read_width_B <= 18):
                                    ratio = int(math.ceil(math.log2(18/read_width_B)))

                            elif write_depth_A == 4096:
                                read_loop = math.ceil(read_width_B / 9)
                                if (read_width_B <= 9):
                                    ratio = int(math.ceil(math.log2(9/read_width_B)))

                            elif write_depth_A in [8192, 16384, 32768]:
                                read_loop = math.ceil(read_width_B / 36)
                                if (read_width_B <= 36):
                                    ratio = (math.ceil(math.log2(36 / read_width_B)))
                        
                        if (write_width_A > read_width_B):
                            k=0
                            for i in range(int(m/read_loop)):
                                for j in range(read_loop):
                                    if (write_depth_A == 1024):
                                        if (write_width_A > 36):
                                            self.comb += If((self.addr_reg_B == i), self.dout_B[(j*36):(j*36)+36].eq(Cat(self.bram_out_B[k+j][0:8], self.rparity_B[k+j][0], self.bram_out_B[k+j][8:16], self.rparity_B[k+j][1],
                                                            self.bram_out_B[k+j][16:24], self.rparity_B[k+j][2], self.bram_out_B[k+j][24:32], self.rparity_B[k+j][3])))
                                        else:
                                            self.comb += self.dout_B[(j*36):(j*36)+36].eq(Cat(self.bram_out_B[k+j][0:8], self.rparity_B[k+j][0], self.bram_out_B[k+j][8:16], self.rparity_B[k+j][1],
                                                        self.bram_out_B[k+j][16:24], self.rparity_B[k+j][2], self.bram_out_B[k+j][24:32], self.rparity_B[k+j][3]))
                                    elif (write_depth_A == 2048):
                                        if (write_width_A > 18):
                                            self.comb += If((self.addr_reg_B == i), self.dout_B[(j*18):(j*18)+18].eq(Cat(self.bram_out_B[k+j][0:8], self.rparity_B[k+j][0], self.bram_out_B[k+j][8:16], self.rparity_B[k+j][1])))
                                        else:
                                            self.comb += self.dout_B[(j*18):(j*18)+18].eq(Cat(self.bram_out_B[k+j][0:8], self.rparity_B[k+j][0], self.bram_out_B[k+j][8:16], self.rparity_B[k+j][1]))
                                    elif (write_depth_A == 4096):
                                        if (write_width_A > 9):
                                            self.comb += If((self.addr_reg_B == i), self.dout_B[(j*9):(j*9)+9].eq(Cat(self.bram_out_B[k+j][0:8], self.rparity_B[k+j][0])))
                                        else:
                                            self.comb += self.dout_B[(j*9):(j*9)+9].eq(Cat(self.bram_out_B[k+j][0:8], self.rparity_B[k+j][0]))
                                k = k + read_loop

                            if (write_depth_A in [8192, 16384, 32768]):
                                for i in range(n):
                                    for j in range(m):
                                        if read_width_B >= 18:
                                            x = j % int(read_width_B/9)
                                            k =  j // int(read_width_B/9) + (i*int(m/int(read_width_B/9)))
                                            width = 9
                                            self.comb += If((self.addr_reg_B == k), self.dout_B[( x *width):( x *width)+width].eq(Cat(self.bram_out_B[j][(i*32):(i*32)+8], self.rparity_B[j][(i*4)])))
                                        elif read_width_B == 9:
                                            k =  i * m + j
                                            width = 9
                                            self.comb += If((self.addr_reg_B == k), self.dout_B[(0*width):(0*width)+width].eq(Cat(self.bram_out_B[j][(i*32):(i*32)+8], self.rparity_B[j][(i*4)])))
                            
                            m_mux = math.ceil(math.log2(m*n))
                            dout_mux        = {}
                            ren_mux         = {}
                            addr_reg_mux    = {}
                            if (write_depth_A == 1024 and read_width_B <= 36):
                                for i in range(m):
                                    if (op_mode in ["No_Change", "Read_First"]):
                                        ren_mux[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                                    addr_reg_mux[i] = self.addr_reg_B.eq(i)

                            elif (write_depth_A == 2048 and read_width_B <= 18):
                                for i in range(m):
                                    if (op_mode in ["No_Change", "Read_First"]):
                                        ren_mux[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                                    addr_reg_mux[i] = self.addr_reg_B.eq(i)

                            elif (write_depth_A == 4096 and read_width_B <= 9):
                                for i in range(m):
                                    if (op_mode in ["No_Change", "Read_First"]):
                                        ren_mux[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                                    addr_reg_mux[i] = self.addr_reg_B.eq(i)

                            elif (write_depth_A in [8192, 16384, 32768]):
                                if (read_width_B >= 9):
                                    for i in range(n * int(write_width_A/read_width_B)):
                                        if (op_mode in ["No_Change", "Read_First"]):
                                            ren_mux[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                                        addr_reg_mux[i] = self.addr_reg_B.eq(i)

                                if (m > 1 or n > 1):
                                    for j in range(n):
                                        wen_mux[j] = self.wen_A1.eq(Cat(Replicate(0,j), self.wen_A))

                            else:
                                if (write_width_A > read_width_B):
                                    for i in range(math.ceil(write_width_A/read_width_B)):
                                        if (op_mode in ["No_Change", "Read_First"]):
                                            ren_mux[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                                        addr_reg_mux[i] = self.addr_reg_B.eq(i)
                                        
                            if (m > 1):
                                if (write_depth_A == 1024 and read_width_B <= 36):
                                    self.comb += Case(self.addr_reg_B, dout_mux)
                                    self.comb += Case(self.addr_B[ratio:m_mux+ratio], ren_mux)
                                    if common_clk == 1:
                                        self.sync += Case(self.addr_B[ratio:m_mux+ratio], addr_reg_mux)
                                    else:
                                        self.sync.B += Case(self.addr_B[ratio:m_mux+ratio], addr_reg_mux)

                                elif (write_depth_A == 2048 and read_width_B <= 18):
                                    self.comb += Case(self.addr_reg_B, dout_mux)
                                    self.comb += Case(self.addr_B[ratio:m_mux+ratio], ren_mux)
                                    if common_clk == 1:
                                        self.sync += Case(self.addr_B[ratio:m_mux+ratio], addr_reg_mux)
                                    else:
                                        self.sync.B += Case(self.addr_B[ratio:m_mux+ratio], addr_reg_mux)

                                elif (write_depth_A == 4096 and read_width_B <= 9):
                                    self.comb += Case(self.addr_reg_B, dout_mux)
                                    self.comb += Case(self.addr_B[ratio:m_mux+ratio], ren_mux)
                                    if common_clk == 1:
                                        self.sync += Case(self.addr_B[ratio:m_mux+ratio], addr_reg_mux)
                                    else:
                                        self.sync.B += Case(self.addr_B[ratio:m_mux+ratio], addr_reg_mux)

                                elif (write_depth_A in [8192, 16384, 32768]):
                                    read_depth = int(read_depth_B / (m*n))
                                    
                                    if (read_width_B >= 9):
                                        self.comb += Case(Cat(self.addr_B[0:math.ceil(math.log2(write_width_A/read_width_B))], self.addr_B[msb_read-math.ceil(math.log2(n)):msb_read]), ren_mux)
                                        if common_clk == 1:
                                            self.sync += Case(Cat(self.addr_B[0:math.ceil(math.log2(write_width_A/read_width_B))], self.addr_B[msb_read-math.ceil(math.log2(n)):msb_read]), addr_reg_mux)
                                        else:
                                            self.sync.B += Case(Cat(self.addr_B[0:math.ceil(math.log2(write_width_A/read_width_B))], self.addr_B[msb_read-math.ceil(math.log2(n)):msb_read]), addr_reg_mux)
                                    self.comb += Case(self.addr_reg_B, dout_mux)
                                    self.comb += Case(self.addr_A[12:msb_A], wen_mux)
                                else:
                                    self.comb += Case(self.addr_reg_B, dout_mux)
                                    self.comb += Case(self.addr_B[0:ratio], ren_mux)
                                    if common_clk == 1:
                                        self.sync += Case(self.addr_B[0:ratio], addr_reg_mux)
                                    else:
                                        self.sync.B += Case(self.addr_B[0:ratio], addr_reg_mux)
                                    
                        elif (read_width_B > write_width_A): # read wider output mux and write enable mux
                            wen_mux         = {}
                            ren_mux         = {}
                            addr_reg_mux    = {}
                            dout_mux        = {}
                            k= 0
                            p = 0
                            for j in range(m):
                                wen_mux[j] = self.wen_A1.eq(Cat(Replicate(0,j), self.wen_A))
                                for i in range(n):
                                    if read_depth_B <= 1024:
                                        k = j * n + i
                                        if (write_width_A >= 72):
                                            self.comb += self.dout_B[(k*36):(k*36)+36].eq(Cat(self.bram_out_B[j][(i*32)+0:(i*32)+8], self.rparity_B[j][(i*4)+0], self.bram_out_B[j][(i*32)+8:(i*32)+16], self.rparity_B[j][(i*4)+1],
                                                        self.bram_out_B[j][(i*32)+16:(i*32)+24], self.rparity_B[j][(i*4)+2], self.bram_out_B[j][(i*32)+24:(i*32)+32], self.rparity_B[j][(i*4)+3]))
                                        elif (write_width_A == 36):
                                            self.comb += self.dout_B[(j*36):(j*36)+36].eq(Cat(self.bram_out_B[j][0:8], self.rparity_B[j][0], self.bram_out_B[j][8:16], self.rparity_B[j][1],
                                                        self.bram_out_B[j][16:24], self.rparity_B[j][2], self.bram_out_B[j][24:32], self.rparity_B[j][3]))
                                        elif (write_width_A == 18):
                                            self.comb += self.dout_B[(j*18):(j*18)+18].eq(Cat(self.bram_out_B[j][0:8], self.rparity_B[j][0], self.bram_out_B[j][8:16], self.rparity_B[j][1]))
                                        elif (write_width_A == 9):
                                            self.comb += self.dout_B[(j*9):(j*9)+9].eq(Cat(self.bram_out_B[j][0:8], self.rparity_B[j][0]))
                                    elif read_depth_B == 2048:
                                        k = j * n + i
                                        if (write_width_A >= 18):
                                            self.comb += self.dout_B[(k*18):(k*18)+18].eq(Cat(self.bram_out_B[j][(i*32)+0:(i*32)+8], self.rparity_B[j][(i*4)+0], self.bram_out_B[j][(i*32)+8:(i*32)+16], self.rparity_B[j][(i*4)+1]))
                                        elif (write_width_A == 9):
                                            self.comb += self.dout_B[(j*9):(j*9)+9].eq(Cat(self.bram_out_B[j][0:8], self.rparity_B[j][0]))
                                    elif read_depth_B == 4096:
                                        k = j * n + i
                                        if (write_width_A >= 9):
                                            self.comb += self.dout_B[(k*9):(k*9)+9].eq(Cat(self.bram_out_B[j][(i*32)+0:(i*32)+8], self.rparity_B[j][(i*4)+0]))
                                    elif read_depth_B >= 8192:
                                        if read_depth_B == 8192:
                                            k = 0 if (j * n + i) < (int(m*n/2)) else 1
                                        elif read_depth_B in [16384, 32768]:
                                            k = j // 2
                                        x = (j * n + i) % (int(read_width_B/9))
                                        self.comb += If((self.addr_reg_B == k), self.dout_B[(x*9):(x*9)+9].eq(Cat(self.bram_out_B[j][(i*32):(i*32)+8], self.rparity_B[j][(i*4)])))
                                        wen_mux[j] = self.wen_A1.eq(Cat(Replicate(0,j), self.wen_A))
                            
                            if (read_depth_B >= 8192):
                                n_temp = int(read_depth_B/4096)
                                for i in range(n_temp):
                                    if (op_mode in ["No_Change", "Read_First"]):    
                                        ren_mux[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                                    dout_mux[i] = self.addr_reg_B.eq(i)
                                    
                            if read_depth_B <= 1024 or read_depth_B in [2048, 4096]:
                                self.comb += Case(self.addr_A[0:ratio], wen_mux)
                            else:
                                self.comb += Case(Cat(self.addr_A[0:ratio], self.addr_A[msb_A-(math.ceil(math.log2(n_temp))):msb_A]), wen_mux)
                                self.comb += Case(self.addr_B[msb_read-(math.ceil(math.log2(n_temp))):msb_read], ren_mux)
                                if common_clk == 1:
                                    self.sync += Case(self.addr_B[msb_read-(math.ceil(math.log2(n_temp))):msb_read], dout_mux)
                                else:
                                    self.sync.B += Case(self.addr_B[msb_read-(math.ceil(math.log2(n_temp))):msb_read], dout_mux)
                b = 0
                out_data = 0
                f = 0
                for i in range(n):  # horizontal memory
                    z = write_width_A - 36*(n-1)
                    if (n == (i+1)): # for last bram input data calculations
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
                            write_data_A   = self.din_A[36*(n-1):write_width_A]
                            w_parity_A     = Replicate(0,4)
                    else:
                        if (z > 35):
                            write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                            w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                    
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
                    
                    elif (write_width_A > read_width_B):
                        read_depth = int(read_depth_B / (m*n))
                        if (write_depth_A == 1024):
                            param_write_width_A = 36
                            param_read_width_B  = 36
                            address_A = Cat(Replicate(0,5), self.addr_A[0:10])
                            if (read_depth == 1024):
                                address_B = Cat(Replicate(0,5), self.addr_B[ratio+m_mux:msb_read])
                            elif (read_depth == 2048):
                                address_B = Cat(Replicate(0,4), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                                param_read_width_B = 18
                            elif (read_depth == 4096):
                                address_B = Cat(Replicate(0,3), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                                param_read_width_B = 9
                            elif (read_depth == 8192):
                                address_B = Cat(Replicate(0,3), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                            elif (read_depth == 16384):
                                address_B = Cat(Replicate(0,2), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                            elif (read_depth == 32768):
                                address_B = Cat(Replicate(0,1), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                            else: 
                                address_B = Cat(Replicate(0,5), self.addr_B[ratio:msb_read])
                                param_read_width_B = 36
                                
                        elif (write_depth_A == 2048):
                            param_write_width_A = 18
                            param_read_width_B  = 18
                            address_A = Cat(Replicate(0,4), self.addr_A[0:11])
                            if (read_depth == 1024):
                                address_B = Cat(Replicate(0,4), self.addr_B[ratio:msb_read])
                            elif (read_depth == 2048):
                                address_B = Cat(Replicate(0,4), self.addr_B[ratio+m_mux:msb_read])
                                param_read_width_B = 18
                            elif (read_depth == 4096):
                                address_B = Cat(Replicate(0,3), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                                param_read_width_B = 9
                            elif (read_depth == 8192):
                                address_B = Cat(Replicate(0,3), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                                param_read_width_B = 9
                            elif (read_depth == 16384):
                                address_B = Cat(Replicate(0,2), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                            elif (read_depth == 32768):
                                address_B = Cat(Replicate(0,1), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                            else: 
                                address_B = Cat(Replicate(0,4), self.addr_B[ratio:msb_read])
                                param_read_width_B = 18
                            
                        elif (write_depth_A == 4096):
                            param_write_width_A = 9
                            param_read_width_B  = 9
                            address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                            if (read_depth == 1024):
                                address_B = Cat(Replicate(0,5), self.addr_B[ratio+m_mux:msb_read])
                            elif (read_depth == 2048):
                                address_B = Cat(Replicate(0,4), self.addr_B[ratio+m_mux:msb_read])
                            if (read_depth == 4096):
                                address_B = Cat(Replicate(0,3), self.addr_B[ratio+m_mux:msb_read])
                                param_read_width_B = 9
                            elif (read_depth == 8192):
                                address_B = Cat(Replicate(0,3), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                            elif (read_depth == 16384):
                                address_B = Cat(Replicate(0,2), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                            elif (read_depth == 32768):
                                address_B = Cat(Replicate(0,1), self.addr_B[0:ratio], self.addr_B[ratio+m_mux:msb_read])
                            else: 
                                address_B = Cat(Replicate(0,3), self.addr_B[ratio:msb_read])
                                param_read_width_B = 9
                            
                        elif (write_depth_A in [8192, 16384, 32768]):
                            param_write_width_A = 9
                            param_read_width_B  = 9
                            address_A = Cat(Replicate(0,3), self.addr_A[0:12])
                            address_B = Cat(Replicate(0,3), self.addr_B[math.ceil(math.log2(write_width_A/read_width_B)):msb_read-math.ceil(math.log2(n))])
                    
                    elif (read_width_B > write_width_A):
                        
                        if read_depth_B <= 1024:
                            if (write_width_A >= 36):
                                param_write_width_A = 36
                                param_read_width_B  = 36
                                address_B = Cat(Replicate(0,5), self.addr_B[0:msb_read])
                                address_A = Cat(Replicate(0,5), self.addr_A[ratio:msb_A])

                            elif (write_width_A == 18):
                                param_write_width_A = 18
                                param_read_width_B  = 18
                                address_B = Cat(Replicate(0,4), self.addr_B[0:msb_read])
                                address_A = Cat(Replicate(0,4), self.addr_A[ratio:msb_A])

                            elif (write_width_A == 9):
                                param_write_width_A = 9
                                param_read_width_B  = 9
                                address_B = Cat(Replicate(0,3), self.addr_B[0:msb_read])
                                address_A = Cat(Replicate(0,3), self.addr_A[ratio:msb_A])
                                
                        elif read_depth_B == 2048:
                            if (write_width_A >= 18):
                                param_write_width_A = 18
                                param_read_width_B  = 18
                                address_B = Cat(Replicate(0,4), self.addr_B[0:msb_read])
                                address_A = Cat(Replicate(0,4), self.addr_A[ratio:msb_A])

                            elif (write_width_A == 9):
                                param_write_width_A = 9
                                param_read_width_B  = 9
                                address_B = Cat(Replicate(0,3), self.addr_B[0:msb_read])
                                address_A = Cat(Replicate(0,3), self.addr_A[ratio:msb_A])
                                
                        elif read_depth_B in [4096, 8192, 16384]:
                            diff_depth = int(math.log2(read_depth_B/4096))
                            if (write_width_A >= 9):
                                param_write_width_A = 9
                                param_read_width_B  = 9
                                address_B = Cat(Replicate(0,3), self.addr_B[0:12])
                                address_A = Cat(Replicate(0,3), self.addr_A[ratio:msb_A-diff_depth])
                    
                    k = 0
                    for j in range(m): # vertical memory
                        
                        if (file_path == "") or (self.line_count == 0):
                            data    = '0'
                            parity  = '0'
                        else:
                            data        = hex(int(init[f], 2))[2:]             # hex conversion and removal of 0x from start of converted data
                            parity      = hex(int(init_parity[f], 2))[2:]      # hex conversion and removal of 0x from start of converted data
                            f = f + 1 # incrementing BRAM
                        
                        # read enable logic
                        if (write_width_A == read_width_B):
                            if read_depth_B in [1024, 2048, 4096, 8192, 16384, 32768]:
                                ren = self.ren_B
                            else:
                                ren = self.ren_B1[j]
                        elif (write_width_A > read_width_B): # write wider
                            if write_depth_A in [1024, 2048, 4096]:
                                if (m > 1 or n > 1):
                                    ren = self.ren_B1[int(j/read_loop)]
                                else:
                                    ren = self.ren_B
                            else:
                                if (read_width_B >= 18):
                                    k =  j // int(read_width_B/9) + (i*int(m/int(read_width_B/9)))
                                    ren = self.ren_B1[k]
                                else:
                                    k = i * m + j
                                    ren = self.ren_B1[k]
                                    
                        elif (read_width_B >  write_width_A): # read wider
                            if read_depth_B in [8192]:
                                k = 0 if (j * n + i) < (int((m*n)/2)) else 1
                                ren = self.ren_B1[k]
                            elif read_depth_B in [16384, 32768]:
                                k = j // 2
                                ren = self.ren_B1[k]
                            else:
                                ren = self.ren_B
                        
                        # write enable logic
                        if (write_width_A == read_width_B): # symmetric
                            if write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]:
                                wen = self.wen_A
                            else:
                                wen = self.wen_A1[j]
                        elif (write_width_A > read_width_B): # write wider
                            if write_depth_A in [1024, 2048, 4096]:
                                wen = self.wen_A
                            else: # depth = 8K, 16K, 32K
                                k = i
                                wen = self.wen_A1[k]
                        elif (read_width_B > write_width_A): # read wider
                            if (read_depth_B in [8192, 16384, 32768]):
                                wen = self.wen_A1[j]
                            else:
                                wen = self.wen_A1[j]

                        if (write_width_A > read_width_B):
                            if (write_depth_A in [1024]):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*4):(j*4)+4]
                                else:
                                    be_A = Replicate(1, 4)
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
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*2):(j*2)+2]
                                else:
                                    be_A = Replicate(1, 4)
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
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*1):(j*1)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                z = write_width_A - 9*(m-1)
                                if (m == (j+1)):
                                    if (z > 8):
                                        write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                        w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                    else:
                                        write_data_A = self.din_A[(j*9):((j*9)+8)]
                                        w_parity_A   = Replicate(0,4)
                                else:
                                    write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                            
                            elif write_depth_A in [8192, 16384, 32768]:
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*1):(j*1)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                    
                        # Read Wider
                        elif (read_width_B > write_width_A):
                            if (read_depth_B <= 1024):
                                if (write_width_A >= 36):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*4):(i*4)+4]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*36):((i*36)+8)], self.din_A[(i*36)+9:((i*36)+17)], self.din_A[(i*36)+18:((i*36)+26)], self.din_A[(i*36)+27:((i*36)+35)])
                                    w_parity_A     = Cat(self.din_A[((i*36)+8)], self.din_A[((i*36)+17)], self.din_A[((i*36)+26)], self.din_A[((i*36)+35)])
                                elif (write_width_A == 18):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*2):(i*2)+2]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*18):((i*18)+8)], self.din_A[(i*18)+9:((i*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((i*18)+8)], self.din_A[((i*18)+17)], Replicate(0,2))
                                elif (write_width_A == 9):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*1):(i*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*9):((i*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((i*9)+8)], Replicate(0,3))
                                    
                            elif (read_depth_B == 2048):
                                if (write_width_A >= 18):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*2):(i*2)+2]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*18):((i*18)+8)], self.din_A[(i*18)+9:((i*18)+17)])
                                    w_parity_A     = Cat(self.din_A[((i*18)+8)], self.din_A[((i*18)+17)], Replicate(0,2))
                                elif (write_width_A == 9):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*1):(i*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*9):((i*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((i*9)+8)], Replicate(0,3))
                                    
                            elif (read_depth_B == 4096):
                                if (write_width_A >= 9):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*1):(i*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*9):((i*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((i*9)+8)], Replicate(0,3))
                            
                            elif (read_depth_B in [8192, 16384, 32768]):
                                if (write_width_A >= 9):
                                    if (byte_write_enable):
                                        be_A = self.be_A[(i*1):(i*1)+1]
                                    else:
                                        be_A = Replicate(1, 4)
                                    write_data_A   = Cat(self.din_A[(i*9):((i*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((i*9)+8)], Replicate(0,3))
                        
                        elif (write_width_A == read_width_B): # Symmetric Memory
                            if (write_depth_A in [1024]):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*4):(j*4)+4]
                                else:
                                    be_A = Replicate(1, 4)
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
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*2):(j*2)+2]
                                else:
                                    be_A = Replicate(1, 4)
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
                                if (byte_write_enable):
                                    be_A = self.be_A[(j*1):(j*1)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                z = write_width_A - 9*(m-1)
                                if (m == (j+1)):
                                    if (z > 8):
                                        write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                        w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                                    else:
                                        write_data_A = self.din_A[(j*9):((j*9)+8)]
                                        w_parity_A   = Replicate(0,4)
                                else:
                                    write_data_A   = Cat(self.din_A[(j*9):((j*9)+8)])
                                    w_parity_A     = Cat(self.din_A[((j*9)+8)], Replicate(0,3))
                            elif (write_depth_A == 8192):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j//2):(j//2)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A = self.din_A[(j*4):((j*4)+4)]
                                w_parity_A   = Replicate(0,4)
                            
                            elif (write_depth_A == 16384):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j//4):(j//4)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A = self.din_A[(j*2):((j*2)+2)]
                                w_parity_A   = Replicate(0,4)
                                
                            elif (write_depth_A == 32768):
                                if (byte_write_enable):
                                    be_A = self.be_A[(j//8):(j//8)+1]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A = self.din_A[(j*1):((j*1)+1)]
                                w_parity_A   = Replicate(0,4)
                        
                        if (op_mode == "Read_First"):
                            renB = ren
                        elif (op_mode == "No_Change" or op_mode == "Write_First"):
                            renB = ~self.wen_A
                        
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
                        i_REN_B     = renB,
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
                    k = k + int(m/read_loop)
                    
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
            
            #################################################################################################
            #################################################################################################
            # -----------------------------------True Dual Port RAM------------------------------------------
            #################################################################################################
            #################################################################################################
            elif (memory_type == "True_Dual_Port"):
                #############################################################################################
                # Block RAM Operational Modes
                #############################################################################################
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
                else: # Write_First
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
                        
                write_ratio_A   = math.ceil(math.log2(large_width / write_width_A))
                write_ratio_B   = math.ceil(math.log2(large_width / write_width_B))
                read_ratio_A    = math.ceil(math.log2(large_width / read_width_A))
                read_ratio_B    = math.ceil(math.log2(large_width / read_width_B))
                
                n_log = math.ceil(math.log2(n))
                m_log = math.ceil(math.log2(m))
                
                #############################################################################################
                # Write Read Loops Calculations
                #############################################################################################
                if write_width_A >= 36:
                    write_loop_A      = math.ceil(large_width/write_width_A)*n
                else:
                    write_loop_A      = math.ceil(large_width/36)*n
                
                if write_width_B >=36:
                    write_loop_B      = math.ceil(large_width/write_width_B)*n
                else:
                    write_loop_B      = math.ceil(large_width/36)*n
                
                if read_width_A >= 36:
                    read_loop_A       = math.ceil(large_width/read_width_A)*n
                else:
                    read_loop_A       = math.ceil(large_width/36)*n
                    
                if read_width_B >= 36:
                    read_loop_B       = math.ceil(large_width/read_width_B)*n
                else:
                    read_loop_B       = math.ceil(large_width/36)*n
                
                msb_write_A = math.ceil(math.log2(write_depth_A))
                msb_read_A  = math.ceil(math.log2(read_depth_A))
                msb_write_B = math.ceil(math.log2(write_depth_B))
                msb_read_B  = math.ceil(math.log2(read_depth_B))
                
                #############################################################################################
                # MUX Initialization
                #############################################################################################
                wen_mux_A         = {}
                wen_mux_B         = {}
                ren_mux_A         = {}
                ren_mux_B         = {}
                addr_reg_mux_A    = {}
                addr_reg_mux_B    = {}
                
                #############################################################################################
                # Output Logic Port A
                #############################################################################################
                read_temp_A = math.ceil(read_width_A/36)
                if (read_ratio_A > 0):
                    if (m == 1 and n == 1):
                        if (read_width_A == 36):
                            self.comb += self.dout_A[0:36].eq(Cat(self.bram_out_A[0][0:8], self.rparity_A[0][0], self.bram_out_A[0][8:16], self.rparity_A[0][1],
                                                self.bram_out_A[0][16:24], self.rparity_A[0][2], self.bram_out_A[0][24:32], self.rparity_A[0][3]))
                        elif (read_width_A == 18):
                            self.comb += self.dout_A[0:18].eq(Cat(self.bram_out_A[0][0:8], self.rparity_A[0][0], self.bram_out_A[0][8:16], self.rparity_A[0][1]))
                        elif (read_width_A == 9):
                            self.comb += self.dout_A[0:9].eq(Cat(self.bram_out_A[0][0:8], self.rparity_A[0][0]))
                    else:
                        # Output Logic
                        for j in range(n): 
                            for i in range(m):
                                if m > read_temp_A:
                                    k = (i // read_temp_A) + (j * (m // read_temp_A))
                                    x = (i % read_temp_A)
                                else:
                                    k = 0
                                    x = 0
                                if read_width_A == 9:
                                    self.comb += If((self.addr_reg_A == k), self.dout_A[(x*9):(x*9)+9].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0])))
                                elif read_width_A == 18:
                                    self.comb += If((self.addr_reg_A == k), self.dout_A[(x*18):(x*18)+18].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0], self.bram_out_A[i][(j*32)+8:(j*32)+16], self.rparity_A[i][(j*4)+1])))
                                elif read_width_A >= 36:
                                    self.comb += If((self.addr_reg_A == k), self.dout_A[(x*36):(x*36)+36].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0], self.bram_out_A[i][(j*32)+8:(j*32)+16], self.rparity_A[i][(j*4)+1],
                                                    self.bram_out_A[i][(j*32)+16:(j*32)+24], self.rparity_A[i][(j*4)+2], self.bram_out_A[i][(j*32)+24:(j*32)+32], self.rparity_A[i][(j*4)+3])))
                
                else:
                    if n == 1:
                        for j in range(n):
                            for i in range(m): # Output logic
                                if (read_width_A >= 36):
                                    self.comb += self.dout_A[(i*36):((i*36)+36)].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0], self.bram_out_A[i][(j*32)+8:(j*32)+16], self.rparity_A[i][(j*4)+1],
                                                self.bram_out_A[i][(j*32)+16:(j*32)+24], self.rparity_A[i][(j*4)+2], self.bram_out_A[i][(j*32)+24:(j*32)+32], self.rparity_A[i][(j*4)+3]))
                                elif (read_width_A == 18):
                                    self.comb += self.dout_A[(i*18):(i*18)+18].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0], self.bram_out_A[i][(j*32)+8:(j*32)+16], self.rparity_A[i][(j*4)+1]))
                                elif (read_width_A == 9):
                                    self.comb += self.dout_A[(i*9):((i*9)+9)].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0]))
                    else:
                        for j in range(n): 
                            for i in range(m):
                                k = j
                                x = (i % read_temp_A)
                                if read_width_A == 9:
                                    self.comb += If((self.addr_reg_A == k), self.dout_A[(x*9):(x*9)+9].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0])))
                                elif read_width_A == 18:
                                    self.comb += If((self.addr_reg_A == k), self.dout_A[(x*18):(x*18)+18].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0], self.bram_out_A[i][(j*32)+8:(j*32)+16], self.rparity_A[i][(j*4)+1])))
                                elif read_width_A >= 36:
                                    self.comb += If((self.addr_reg_A == k), self.dout_A[(x*36):(x*36)+36].eq(Cat(self.bram_out_A[i][(j*32)+0:(j*32)+8], self.rparity_A[i][(j*4)+0], self.bram_out_A[i][(j*32)+8:(j*32)+16], self.rparity_A[i][(j*4)+1],
                                                    self.bram_out_A[i][(j*32)+16:(j*32)+24], self.rparity_A[i][(j*4)+2], self.bram_out_A[i][(j*32)+24:(j*32)+32], self.rparity_A[i][(j*4)+3])))
                
                #############################################################################################
                # Output Logic Port A
                #############################################################################################
                read_temp_B = math.ceil(read_width_B/36)
                if (read_ratio_B > 0):
                    if (m == 1 and n == 1):
                        if (read_width_B == 36):
                            self.comb += self.dout_B[0:36].eq(Cat(self.bram_out_B[0][0:8], self.rparity_B[0][0], self.bram_out_B[0][8:16], self.rparity_B[0][1],
                                                self.bram_out_B[0][16:24], self.rparity_B[0][2], self.bram_out_B[0][24:32], self.rparity_B[0][3]))
                        elif (read_width_B == 18):
                            self.comb += self.dout_B[0:18].eq(Cat(self.bram_out_B[0][0:8], self.rparity_B[0][0], self.bram_out_B[0][8:16], self.rparity_B[0][1]))
                        elif (read_width_B == 9):
                            self.comb += self.dout_B[0:9].eq(Cat(self.bram_out_B[0][0:8], self.rparity_B[0][0]))
                    else:
                        for j in range(n):
                            for i in range(m):
                                if m > read_temp_B:
                                    k = (i // read_temp_B) + (j * (m // read_temp_B))
                                    x = (i % read_temp_B)
                                else:
                                    k = 0
                                    x = 0
                                if read_width_B == 9:
                                    self.comb += If((self.addr_reg_B == k), self.dout_B[(x*9):(x*9)+9].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0])))
                                elif read_width_B == 18:
                                    self.comb += If((self.addr_reg_B == k), self.dout_B[(x*18):(x*18)+18].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0], self.bram_out_B[i][(j*32)+8:(j*32)+16], self.rparity_B[i][(j*4)+1])))
                                elif read_width_B >= 36:
                                    self.comb += If((self.addr_reg_B == k), self.dout_B[(x*36):(x*36)+36].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0], self.bram_out_B[i][(j*32)+8:(j*32)+16], self.rparity_B[i][(j*4)+1],
                                                    self.bram_out_B[i][(j*32)+16:(j*32)+24], self.rparity_B[i][(j*4)+2], self.bram_out_B[i][(j*32)+24:(j*32)+32], self.rparity_B[i][(j*4)+3])))
                else:
                    if n == 1: # depth is 1K
                        for j in range(n):
                            for i in range(m): # Output logic
                                if (read_width_B >= 36):
                                    self.comb += self.dout_B[(i*36):((i*36)+36)].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0], self.bram_out_B[i][(j*32)+8:(j*32)+16], self.rparity_B[i][(j*4)+1],
                                                self.bram_out_B[i][(j*32)+16:(j*32)+24], self.rparity_B[i][(j*4)+2], self.bram_out_B[i][(j*32)+24:(j*32)+32], self.rparity_B[i][(j*4)+3]))
                                elif (read_width_B == 18):
                                    self.comb += self.dout_B[(i*18):(i*18)+18].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0], self.bram_out_B[i][(j*32)+8:(j*32)+16], self.rparity_B[i][(j*4)+1]))
                                elif (read_width_B == 9):
                                    self.comb += self.dout_B[(i*9):((i*9)+9)].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0]))
                    else: # depth greater than 1K
                        for j in range(n):
                            for i in range(m):
                                k = j
                                x = (i % read_temp_B)
                                if read_width_B == 9:
                                    self.comb += If((self.addr_reg_B == k), self.dout_B[(x*9):(x*9)+9].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0])))
                                elif read_width_B == 18:
                                    self.comb += If((self.addr_reg_B == k), self.dout_B[(x*18):(x*18)+18].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0], self.bram_out_B[i][(j*32)+8:(j*32)+16], self.rparity_B[i][(j*4)+1])))
                                elif read_width_B >= 36:
                                    self.comb += If((self.addr_reg_B == k), self.dout_B[(x*36):(x*36)+36].eq(Cat(self.bram_out_B[i][(j*32)+0:(j*32)+8], self.rparity_B[i][(j*4)+0], self.bram_out_B[i][(j*32)+8:(j*32)+16], self.rparity_B[i][(j*4)+1],
                                                    self.bram_out_B[i][(j*32)+16:(j*32)+24], self.rparity_B[i][(j*4)+2], self.bram_out_B[i][(j*32)+24:(j*32)+32], self.rparity_B[i][(j*4)+3])))
                                    
                #############################################################################################
                # Write Mux A
                #############################################################################################
                if write_ratio_A > 0:
                    for j in range(n):
                        for i in range(write_loop_A):
                            wen_mux_A[i] = self.wen_A1.eq(Cat(Replicate(0,i), self.wen_A))
                    if (n == 1 and m > 1): # When write depth is 1024
                        if write_width_A >= 36:
                            self.comb += Case(self.addr_A[0:write_ratio_A], wen_mux_A)
                        elif write_width_A == 18:
                            self.comb += Case(self.addr_A[1:write_ratio_A], wen_mux_A)
                        elif write_width_A == 9:
                            self.comb += Case(self.addr_A[2:write_ratio_A], wen_mux_A)
                            
                    elif (n > 1 and m > 1):
                        if write_width_A >= 36:
                            self.comb += Case(Cat(self.addr_A[0:write_ratio_A], self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                        elif write_width_A == 18:
                            self.comb += Case(Cat(self.addr_A[1:write_ratio_A], self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                        elif write_width_A == 9:
                            self.comb += Case(Cat(self.addr_A[2:write_ratio_A], self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                        
                    elif (n > 1 and m == 1):
                        if write_width_A >= 36:
                            self.comb += Case(Cat(self.addr_A[0], self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                        elif write_width_A == 18:
                            self.comb += Case(Cat(self.addr_A[1], self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                        elif write_width_A == 9:
                            self.comb += Case(Cat(self.addr_A[2], self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                            
                else:
                    for j in range(n):
                        for i in range(write_loop_A):
                            wen_mux_A[i] = self.wen_A1.eq(Cat(Replicate(0,i), self.wen_A))
                    if (n > 1): # When write depth is greater than 1024
                        if write_width_A >= 36:
                            self.comb += Case(Cat(self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                        elif write_width_A == 18:
                            self.comb += Case(Cat(self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                        elif write_width_A == 9:
                            self.comb += Case(Cat(self.addr_A[msb_write_A-n_log:msb_write_A]), wen_mux_A)
                
                #############################################################################################
                # Write Mux B
                #############################################################################################
                if write_ratio_B > 0:
                    for j in range(n):
                        for i in range(write_loop_B):
                            wen_mux_B[i] = self.wen_B1.eq(Cat(Replicate(0,i), self.wen_B))
                    if (n == 1 and m > 1): # when depth is 1024
                        if write_width_B >= 36:
                            self.comb += Case(self.addr_B[0:write_ratio_B], wen_mux_B)
                        elif write_width_B == 18:
                            self.comb += Case(self.addr_B[1:write_ratio_B], wen_mux_B)
                        elif write_width_B == 9:
                            self.comb += Case(self.addr_B[2:write_ratio_B], wen_mux_B)
                            
                    elif (n > 1 and m > 1):
                        if write_width_B >= 36:
                            self.comb += Case(Cat(self.addr_B[0:write_ratio_B], self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)
                        elif write_width_B == 18:
                            self.comb += Case(Cat(self.addr_B[1:write_ratio_B], self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)
                        elif write_width_B == 9:
                            self.comb += Case(Cat(self.addr_B[2:write_ratio_B], self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)
                            
                    elif (n > 1 and m == 1):
                        if write_width_B >= 36:
                            self.comb += Case(Cat(self.addr_B[0], self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)
                        elif write_width_B == 18:
                            self.comb += Case(Cat(self.addr_B[1], self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)
                        elif write_width_B == 9:
                            self.comb += Case(Cat(self.addr_B[2], self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)

                else:
                    for j in range(n):
                        for i in range(write_loop_B):
                            wen_mux_B[i] = self.wen_B1.eq(Cat(Replicate(0,i), self.wen_B))
                    if (n > 1): # when write depth is greater than 1024
                        if write_width_B >= 36:
                            self.comb += Case(Cat(self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)
                        elif write_width_B == 18:
                            self.comb += Case(Cat(self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)
                        elif write_width_B == 9:
                            self.comb += Case(Cat(self.addr_B[msb_write_B-n_log:msb_write_B]), wen_mux_B)
                
                #############################################################################################
                # Read Mux A
                #############################################################################################
                if read_ratio_A > 0:
                    for j in range(n):
                        for i in range(read_loop_A):
                            addr_reg_mux_A[i] = self.addr_reg_A.eq(i)
                            if (op_mode in ["No_Change", "Read_First"]):
                                ren_mux_A[i] = self.ren_A1.eq(Cat(Replicate(0,i), self.ren_A)) 
                    if (m > 1 and n == 1): # when write depth is 1024 and width greater than 36
                        if read_width_A == 9:
                            self.comb += Case(self.addr_A[2:read_ratio_A+n_log], ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(self.addr_A[2:read_ratio_A+n_log], addr_reg_mux_A)
                            else:
                                self.sync.A += Case(self.addr_A[2:read_ratio_A+n_log], addr_reg_mux_A)
                        elif read_width_A == 18:
                            self.comb += Case(self.addr_A[1:read_ratio_A+n_log], ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(self.addr_A[1:read_ratio_A+n_log], addr_reg_mux_A)
                            else:
                                self.sync.A += Case(self.addr_A[1:read_ratio_A+n_log], addr_reg_mux_A)
                        elif read_width_A >= 36:
                            self.comb += Case(self.addr_A[0:read_ratio_A+n_log], ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(self.addr_A[0:read_ratio_A+n_log], addr_reg_mux_A)
                            else:
                                self.sync.A += Case(self.addr_A[0:read_ratio_A+n_log], addr_reg_mux_A)
                                
                    elif (m > 1 and n > 1): # when write depth greater than 1024 and width greater than 36
                        if read_width_A == 9:
                            self.comb += Case(Cat(self.addr_A[2:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_A[2:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                            else:
                                self.sync.A += Case(Cat(self.addr_A[2:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                                
                        elif read_width_A == 18:
                            self.comb += Case(Cat(self.addr_A[1:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_A[1:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                            else:
                                self.sync.A += Case(Cat(self.addr_A[1:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                        elif read_width_A >= 36:
                            self.comb += Case(Cat(self.addr_A[0:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_A[0:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                            else: 
                                self.sync.A += Case(Cat(self.addr_A[0:read_ratio_A], self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                
                    elif (m == 1 and n > 1): # when write depth greater than 1024 and width equal or less than 36
                        if read_width_A == 9:
                            self.comb += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                            else:
                                self.sync.A += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                        elif read_width_A == 18:
                            self.comb += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                            else:
                                self.sync.A += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                        elif read_width_A >= 36:
                            self.comb += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                            else:
                                self.sync.A += Case(Cat(self.addr_A[msb_read_A-n_log:msb_read_A]), addr_reg_mux_A)
                else:
                    if n > 1:
                        for j in range(n):
                            for i in range(read_loop_A):
                                addr_reg_mux_A[i] = self.addr_reg_A.eq(i)
                                if (op_mode in ["No_Change", "Read_First"]):
                                    ren_mux_A[i] = self.ren_A1.eq(Cat(Replicate(0,i), self.ren_A))
                        if read_width_A == 9:
                            self.comb += Case(self.addr_A[msb_read_A-n_log:msb_read_A], ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(self.addr_A[msb_read_A-n_log:msb_read_A], addr_reg_mux_A)
                            else:
                                self.sync.A += Case(self.addr_A[msb_read_A-n_log:msb_read_A], addr_reg_mux_A)
                        elif read_width_A == 18:
                            self.comb += Case(self.addr_A[msb_read_A-n_log:msb_read_A], ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(self.addr_A[msb_read_A-n_log:msb_read_A], addr_reg_mux_A)
                            else:
                                self.sync.A += Case(self.addr_A[msb_read_A-n_log:msb_read_A], addr_reg_mux_A)
                        elif read_width_A >= 36:
                            self.comb += Case(self.addr_A[msb_read_A-n_log:msb_read_A], ren_mux_A)
                            if common_clk == 1:
                                self.sync += Case(self.addr_A[msb_read_A-n_log:msb_read_A], addr_reg_mux_A)
                            else:
                                self.sync.A += Case(self.addr_A[msb_read_A-n_log:msb_read_A], addr_reg_mux_A)
                    
                #############################################################################################
                # Read Mux B
                #############################################################################################
                if read_ratio_B > 0:
                    for j in range(n):
                        for i in range(read_loop_B):
                            addr_reg_mux_B[i] = self.addr_reg_B.eq(i)
                            if (op_mode in ["No_Change", "Read_First"]):
                                ren_mux_B[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                    if (n == 1 and m > 1): # when write depth is 1024 and width greater than 36
                        if read_width_B == 9:
                            self.comb += Case(self.addr_B[2:read_ratio_B+n_log], ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(self.addr_B[2:read_ratio_B+n_log], addr_reg_mux_B)
                            else:
                                self.sync.B += Case(self.addr_B[2:read_ratio_B+n_log], addr_reg_mux_B)
                        elif read_width_B == 18:
                            self.comb += Case(self.addr_B[1:read_ratio_B+n_log], ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(self.addr_B[1:read_ratio_B+n_log], addr_reg_mux_B)
                            else:
                                self.sync.B += Case(self.addr_B[1:read_ratio_B+n_log], addr_reg_mux_B)
                        elif read_width_B >= 36:
                            self.comb += Case(self.addr_B[0:read_ratio_B+n_log], ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(self.addr_B[0:read_ratio_B+n_log], addr_reg_mux_B)
                            else:
                                self.sync.B += Case(self.addr_B[0:read_ratio_B+n_log], addr_reg_mux_B)
                                
                    elif (n > 1 and m > 1): # when write depth greater than 1024 and width greater than 36
                        if read_width_B == 9:
                            self.comb += Case(Cat(self.addr_B[2:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_B[2:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                            else:
                                self.sync.B += Case(Cat(self.addr_B[2:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                        elif read_width_B == 18:
                            self.comb += Case(Cat(self.addr_B[1:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_B[1:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                            else:
                                self.sync.B += Case(Cat(self.addr_B[1:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                        elif read_width_B >= 36:
                            self.comb += Case(Cat(self.addr_B[0:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_B[0:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                            else:
                                self.sync.B += Case(Cat(self.addr_B[0:read_ratio_B], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                
                    elif (m == 1 and n > 1): # when write depth greater than 1024 and width equal or less than 36
                        if read_width_B == 9:
                            self.comb += Case(Cat(self.addr_B[2], self.addr_B[msb_read_B-n_log:msb_read_B]), ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_B[2], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                            else:
                                self.sync.B += Case(Cat(self.addr_B[2], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                        elif read_width_B == 18:
                            self.comb += Case(Cat(self.addr_B[1], self.addr_B[msb_read_B-n_log:msb_read_B]), ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_B[1], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                            else:
                                self.sync.B += Case(Cat(self.addr_B[1], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                        elif read_width_B >= 36:
                            self.comb += Case(Cat(self.addr_B[0], self.addr_B[msb_read_B-n_log:msb_read_B]), ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(Cat(self.addr_B[0], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                            else:
                                self.sync.B += Case(Cat(self.addr_B[0], self.addr_B[msb_read_B-n_log:msb_read_B]), addr_reg_mux_B)
                else:
                    if n > 1:
                        for j in range(n):
                            for i in range(read_loop_B):
                                addr_reg_mux_B[i] = self.addr_reg_B.eq(i)
                                if (op_mode in ["No_Change", "Read_First"]):
                                    ren_mux_B[i] = self.ren_B1.eq(Cat(Replicate(0,i), self.ren_B))
                        if read_width_B == 9:
                            self.comb += Case(self.addr_B[msb_read_B-n_log:msb_read_B], ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(self.addr_B[msb_read_B-n_log:msb_read_B], addr_reg_mux_B)
                            else:
                                self.sync.B += Case(self.addr_B[msb_read_B-n_log:msb_read_B], addr_reg_mux_B)
                        elif read_width_B == 18:
                            self.comb += Case(self.addr_B[msb_read_B-n_log:msb_read_B], ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(self.addr_B[msb_read_B-n_log:msb_read_B], addr_reg_mux_B)
                            else:
                                self.sync.B += Case(self.addr_B[msb_read_B-n_log:msb_read_B], addr_reg_mux_B)
                        elif read_width_B >= 36:
                            self.comb += Case(self.addr_B[msb_read_B-n_log:msb_read_B], ren_mux_B)
                            if common_clk == 1:
                                self.sync += Case(self.addr_B[msb_read_B-n_log:msb_read_B], addr_reg_mux_B)
                            else:
                                self.sync.B += Case(self.addr_B[msb_read_B-n_log:msb_read_B], addr_reg_mux_B)
                    
                l = 0 # din_A variable
                p = 0 # din_B variable
                f = 0 # mem. init variable
                
                for i in range(n):  # horizontal memory
                    
                    #############################################################################################
                    # Write A Address and Mode
                    #############################################################################################
                    if write_width_A >= 36:
                        write_address_A = Cat(Replicate(0,5), self.addr_A[write_ratio_A :msb_write_A - n_log])
                        param_write_width_A = 36
                        
                    elif write_width_A == 18:
                        write_address_A = Cat(Replicate(0,4), self.addr_A[0], self.addr_A[write_ratio_A :msb_write_A - n_log])
                        param_write_width_A = 18
                        
                    elif write_width_A == 9:
                        write_address_A = Cat(Replicate(0,3), self.addr_A[0:2], self.addr_A[write_ratio_A :msb_write_A - n_log])
                        param_write_width_A = 9
                    
                    #############################################################################################
                    # Write B Address and Mode
                    #############################################################################################
                    if write_width_B >= 36:
                        write_address_B = Cat(Replicate(0,5), self.addr_B[write_ratio_B :msb_write_B - n_log])
                        param_write_width_B = 36
                        
                    elif write_width_B >= 18:
                        write_address_B = Cat(Replicate(0,4), self.addr_B[0], self.addr_B[write_ratio_B :msb_write_B - n_log])
                        param_write_width_B = 18
                        
                    elif write_width_B >= 9:
                        write_address_B = Cat(Replicate(0,3), self.addr_B[0:2], self.addr_B[write_ratio_B :msb_write_B - n_log])
                        param_write_width_B = 9
                    
                    #############################################################################################
                    # Read A Address and Mode
                    #############################################################################################
                    if (read_width_A == 9):
                        read_address_A = Cat(Replicate(0,3), self.addr_A[0:2], self.addr_A[read_ratio_A :msb_read_A - n_log])
                        param_read_width_A = 9
                        
                    elif (read_width_A == 18):
                        read_address_A = Cat(Replicate(0,4), self.addr_A[0], self.addr_A[read_ratio_A :msb_read_A - n_log])
                        param_read_width_A = 18
                        
                    elif (read_width_A >= 36):
                        read_address_A = Cat(Replicate(0,5), self.addr_A[read_ratio_A :msb_read_A - n_log])
                        param_read_width_A = 36
                    
                    #############################################################################################
                    # Read B Address and Mode
                    #############################################################################################
                    if (read_width_B == 9):
                        read_address_B = Cat(Replicate(0,3), self.addr_B[0:2], self.addr_B[read_ratio_B :msb_read_B - n_log])
                        param_read_width_B = 9
                        
                    elif (read_width_B == 18):
                        read_address_B = Cat(Replicate(0,4), self.addr_B[0], self.addr_B[read_ratio_B :msb_read_B - n_log])
                        param_read_width_B = 18
                        
                    elif (read_width_B >= 36):
                        read_address_B = Cat(Replicate(0,5), self.addr_B[read_ratio_B :msb_read_B - n_log])
                        param_read_width_B = 36
                    
                    for j in range(m): # vertical memory
                        
                        #############################################################################################
                        # Memory Initialization 
                        #############################################################################################
                        if (file_path == "") or (self.line_count == 0):
                            data    = '0'
                            parity  = '0'
                        else:
                            data        = hex(int(init[f], 2))[2:]          # hex conversion and removal of 0x from start of converted data
                            parity      = hex(int(init_parity[f], 2))[2:]   # hex conversion and removal of 0x from start of converted data
                            f = f + 1
                        
                        #############################################################################################
                        # Write din A 
                        #############################################################################################
                        if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                            if (write_width_A >= 36):
                                if (byte_write_enable):
                                    be_A = self.be_A[(l*4):(l*4)+4]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A   = Cat(self.din_A[(l*36):((l*36)+8)], self.din_A[(l*36)+9:((l*36)+17)], self.din_A[(l*36)+18:((l*36)+26)], self.din_A[(l*36)+27:((l*36)+35)])
                                w_parity_A     = Cat(self.din_A[((l*36)+8)], self.din_A[((l*36)+17)], self.din_A[((l*36)+26)], self.din_A[((l*36)+35)])
                            elif (write_width_A == 18):
                                if (byte_write_enable):
                                    be_A = self.be_A[(l*2):(l*2)+2]
                                else:
                                    be_A = Replicate(1, 4)
                                write_data_A = Cat(self.din_A[(l*18):((l*18)+8)], self.din_A[(l*18)+9:((l*18)+17)])
                                w_parity_A   = Cat(self.din_A[(l*18)+8], self.din_A[(l*18)+17], Replicate(0,2))
                            elif write_width_A == 9:
                                if (byte_write_enable):
                                    be_A = self.be_A[(l*1):(l*1)+1]
                                else:
                                    be_A = Relicate(1, 4)
                                write_data_A   = Cat(self.din_A[(l*9):((l*9)+8)])
                                w_parity_A     = Cat(self.din_A[((l*9)+8)], Replicate(0,3))
                        
                        #############################################################################################
                        # Write din B
                        #############################################################################################
                        if (write_depth_A in [1024, 2048, 4096, 8192, 16384, 32768]):
                            if (write_width_B >= 36):
                                if (byte_write_enable):
                                    be_B = self.be_B[(p*4):(p*4)+4]
                                else:
                                    be_B = Replicate(1, 4)
                                write_data_B   = Cat(self.din_B[(p*36):((p*36)+8)], self.din_B[(p*36)+9:((p*36)+17)], self.din_B[(p*36)+18:((p*36)+26)], self.din_B[(p*36)+27:((p*36)+35)])
                                w_parity_B     = Cat(self.din_B[((p*36)+8)], self.din_B[((p*36)+17)], self.din_B[((p*36)+26)], self.din_B[((p*36)+35)])
                            elif (write_width_B == 18):
                                if (byte_write_enable):
                                    be_B = self.be_B[(p*2):(p*2)+2]
                                else:
                                    be_B = Replicate(1, 4)
                                write_data_B = Cat(self.din_B[(p*18):((p*18)+8)], self.din_B[(p*18)+9:((p*18)+17)])
                                w_parity_B   = Cat(self.din_B[(p*18)+8], self.din_B[(p*18)+17], Replicate(0,2))
                            elif write_width_B == 9:
                                if (byte_write_enable):
                                    be_B = self.be_B[(p*1):(p*1)+1]
                                else:
                                    be_B = Replicate(1, 4)
                                write_data_B   = Cat(self.din_B[(p*9):((p*9)+8)])
                                w_parity_B     = Cat(self.din_B[((p*9)+8)], Replicate(0,3))
                        
                        #############################################################################################
                        # Read Enable A Logic
                        #############################################################################################
                        read_temp_A = math.ceil(read_width_A/36)
                        if read_ratio_A > 0:
                            if m > read_temp_A:
                                k = (j // read_temp_A) + (i * (m // read_temp_A))
                            else:
                                k = (j % read_temp_A) 
                            ren_A = self.ren_A1[k]
                            
                        else:
                            if n == 1:
                                ren_A = self.ren_A
                            else:
                                k = (j // read_temp_A) + (i * (m // read_temp_A))
                                ren_A = self.ren_A1[k]
                            
                        #############################################################################################
                        # Read Enable B Logic
                        #############################################################################################
                        read_temp_B = math.ceil(read_width_B/36)
                        if read_ratio_B > 0:
                            if m > read_temp_B:
                                k = (j // read_temp_B) + (i * (m // read_temp_B))
                            else:
                                k = (j % read_temp_B) 
                            ren_B = self.ren_B1[k]
                        else:
                            if n == 1:
                                ren_B = self.ren_B
                            else:
                                k = (j // read_temp_B) + (i * (m // read_temp_B))
                                ren_B = self.ren_B1[k]
                        
                        #############################################################################################
                        # Write Enable A Logic
                        #############################################################################################
                        write_temp_A = math.ceil(write_width_A/36)
                        if write_ratio_A > 0:
                            if m > write_temp_A:
                                k = (j // write_temp_A) + (i * (m // write_temp_A))
                            else:
                                k = (j % write_temp_A) 
                            wen_A = self.wen_A1[k]
                        else:
                            if n == 1:
                                wen_A = self.wen_A
                            else:
                                k = (j // write_temp_A) + (i * (m // write_temp_A))
                                wen_A = self.wen_A1[k]
                        
                        #############################################################################################
                        # Write Enable B Logic
                        #############################################################################################
                        write_temp_B = math.ceil(write_width_B/36)
                        if write_ratio_B > 0:
                            if m > write_temp_B:
                                k = (j // write_temp_B) + (i * (m // write_temp_B))
                            else:
                                k = (j % write_temp_B) 
                            wen_B = self.wen_B1[k]
                        else:
                            if n == 1:
                                wen_B = self.wen_B
                            else:
                                k = (j // write_temp_B) + (i * (m // write_temp_B))
                                wen_B = self.wen_B1[k]
                        
                        #############################################################################################
                        # Block RAM Operational Mode
                        #############################################################################################
                        if (op_mode == "Read_First"):
                            renA = ren_A
                            renB = ren_B
                        elif (op_mode == "No_Change" or op_mode == "Write_First"):
                            renA = ~self.wen_A
                            renB = ~self.wen_B
                        
                        #############################################################################################
                        # True Dual Port Instance
                        #############################################################################################
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
                        i_ADDR_A    = self.address_A,
                        i_ADDR_B    = self.address_B,
                        i_WDATA_A   = write_data_A,
                        i_WPARITY_A = w_parity_A,
                        i_WDATA_B   = write_data_B,
                        i_WPARITY_B = w_parity_B,
                        o_RDATA_A   = self.bram_out_A[j][((i*32)):((i*32)+32)],
                        o_RPARITY_A = self.rparity_A[j][((i*4)):((i*4)+4)],
                        o_RDATA_B   = self.bram_out_B[j][((i*32)):((i*32)+32)],
                        o_RPARITY_B = self.rparity_B[j][((i*4)):((i*4)+4)]
                        )
                        
                        ##################################################################
                        # Write Data Ports Configuration Variables
                        ##################################################################
                        if write_width_A >= 36: # write width A equal or greater than 36
                            if (l == (int(write_width_A/36))-1):    
                                l = 0
                            else:
                                l = l + 1
                        else: # write width A less than 36
                            l = 0
                            
                        if write_width_B >= 36: # write width B equal or greater than 36
                            if (p == (int(write_width_B/36))-1):    
                                p = 0
                            else:
                                p = p + 1
                        else: # write width B less than 36
                            p = 0
                        
                ##################################################################
                # Address Mux for Port A, B
                ##################################################################
                self.comb += If((self.wen_A), self.address_A.eq(write_address_A))
                self.comb += If((self.ren_A), self.address_A.eq(read_address_A))
                self.comb += If((self.wen_B), self.address_B.eq(write_address_B))
                self.comb += If((self.ren_B), self.address_B.eq(read_address_B))
                ##################################################################
            # --------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------
        
        # Distributed RAM Mapping
        # --------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------
        # Distributed RAM
        else:
            self.specials.memory = Memory(width=write_width_A, depth=write_depth_A)
            if (memory_type == "Single_Port"):
                self.port = self.memory.get_port(write_capable=True, async_read=False, mode=WRITE_FIRST, has_re=True, clock_domain="A")
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
        # --------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------