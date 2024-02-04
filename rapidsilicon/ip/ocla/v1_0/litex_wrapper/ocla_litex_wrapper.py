#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around RS OCLA IP CORE ocla.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

def update_list(n):
    # Create a fixed-size list with zeros
    result_list = [0] * 15  # Adjust the size as needed

    # Update the list based on the given number
    for i in range(1, n + 1):
        result_list[i - 1] = i

    return result_list

def groupArguments(arguments):
    combinedIndexes, currentGroup, currentSum = [],[],0
    
    for i, arg in enumerate(arguments):
        if arg !=0:
            if arg == 1024:
                combinedIndexes.append([i])
            else:
                if currentSum + arg > 1024:
                    if currentGroup:
                        combinedIndexes.append(currentGroup.copy())
                        currentGroup, currentSum = [], 0
                currentGroup.append(i)
                currentSum += arg

    if currentGroup:
        combinedIndexes.append(currentGroup.copy())

    return combinedIndexes



if1_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if2_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if3_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if4_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if5_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if6_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if7_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if8_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if9_probes  = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if10_probes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if11_probes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if12_probes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if13_probes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if14_probes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
if15_probes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]



# AXI LITE OCLA -------------------------------------------------------------------------------------
class AXILITEOCLA(Module):
    def __init__(self, platform, 
                s_axil, 
                nprobes,  
                mem_depth, 
                probesize,
                mode,
                axi_type,
                Sampling_Clock,
                EIO_Enable,
                Input_Probe_Width,
                Ouput_Probe_width):
        dummy_list = groupArguments(probesize)
        result = update_list(nprobes)
        
        #print(f'eio probe size: {probesize}')

        #print(f'CombinedIndexes: {dummy_list}')
        if Sampling_Clock== "MULTIPLE":
            if1_probes[0] = result[0]
            if2_probes[0] = result[1]
            if3_probes[0] = result[2]
            if4_probes[0] = result[3]
            if5_probes[0] = result[4]
            if6_probes[0] = result[5]
            if7_probes[0] = result[6]
            if8_probes[0] = result[7]
            if9_probes[0] = result[8]
            if10_probes[0] = result[9]
            if11_probes[0] = result[10]
            if12_probes[0] = result[11]
            if13_probes[0] = result[12]
            if14_probes[0] = result[13]
            if15_probes[0] = result[14]
        else:
            for i, sublist in enumerate(dummy_list):
                if i == 0:
                    if1_probes[:len(sublist)] = sublist
                elif i == 1:
                    if2_probes[:len(sublist)] = sublist
                elif i == 2:
                    if3_probes[:len(sublist)] = sublist
                elif i == 3:
                    if4_probes[:len(sublist)] = sublist
                elif i == 4:
                    if5_probes[:len(sublist)] = sublist
                elif i == 5:
                    if6_probes[:len(sublist)] = sublist
                elif i == 6:
                    if7_probes[:len(sublist)] = sublist
                elif i == 7:
                    if8_probes[:len(sublist)] = sublist
                elif i == 8:
                    if9_probes[:len(sublist)] = sublist
                elif i == 9:
                    if10_probes[:len(sublist)] = sublist
                elif i == 10:
                    if11_probes[:len(sublist)] = sublist
                elif i == 11:
                    if12_probes[:len(sublist)] = sublist
                elif i == 12:
                    if13_probes[:len(sublist)] = sublist
                elif i == 13:
                    if14_probes[:len(sublist)] = sublist
                elif i == 14:
                    if15_probes[:len(sublist)] = sublist

        self.logger = logging.getLogger("AXI_LITE_OCLA")
        
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        # Clock Domain
        clock_domain = s_axil.clock_domain
        self.logger.info(f"CLOCK_DOMAIN     : {clock_domain}")
        
        # Address width.
        address_width = len(s_axil.aw.addr)
        self.logger.info(f"ADDRESS_WIDTH    : {address_width}")
        
        # Read Data width.
        data_width = len(s_axil.r.data)
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        
        # OCLA features.
        self.logger.info(f"NO_OF_PROBES          : {nprobes}")
        self.logger.info(f"MEM_DEPTH            : {mem_depth}")
        self.logger.info(f"===================================================")
        
        # OCLA Signals
        self.awaddr     =   Signal(32)
        self.awprot     =   Signal(3)
        self.awvalid    =   Signal(1)
        self.awready    =   Signal(1)
        self.wdata      =   Signal(32)
        self.wstrb      =   Signal(4)
        self.wvalid     =   Signal(1)
        self.wready     =   Signal(1)
        self.bresp      =   Signal(2)
        self.bvalid     =   Signal(1)
        self.bready     =   Signal(1)
        self.araddr     =   Signal(32)
        self.arprot     =   Signal(3)
        self.arvalid    =   Signal(1)
        self.arready    =   Signal(1)
        self.rdata      =   Signal(32)
        self.rresp      =   Signal(2)
        self.rvalid     =   Signal(1)
        self.rready     =   Signal(1)
        
        self.AWADDR     =   Signal(32) 
        self.AWPROT     =   Signal(3)
        self.AWVALID    =   Signal(1)
        self.AWREADY    =   Signal(1)
        self.AWBURST    =   Signal(2)
        self.AWSIZE     =   Signal(3)
        self.AWLEN      =   Signal(8)
        self.AWID       =   Signal(1)
        self.AWCACHE    =   Signal(4)
        self.AWREGION   =   Signal(4)
        self.AWUSER     =   Signal(1)
        self.AWQOS      =   Signal(4)
        self.AWLOCK     =   Signal(1)
        self.WDATA      =   Signal(32)
        self.WSTRB      =   Signal(4)
        self.WVALID     =   Signal(1)
        self.WREADY     =   Signal(1)
        self.WID        =   Signal(1)
        self.WLAST      =   Signal(1)
        self.BRESP      =   Signal(2)
        self.BVALID     =   Signal(1)
        self.BREADY     =   Signal(1)
        self.BID        =   Signal(1)
        self.BUSER      =   Signal(1)
        self.ARADDR     =   Signal(32)
        self.ARPROT     =   Signal(3)
        self.ARVALID    =   Signal(1)
        self.ARREADY    =   Signal(1)
        self.ARBUSRT    =   Signal(2)
        self.ARSIZE     =   Signal(3)
        self.ARLEN      =   Signal(8)
        self.ARID       =   Signal(1)
        self.ARCACHE    =   Signal(4)
        self.ARREGION   =   Signal(4)
        self.ARUSER     =   Signal(1)
        self.ARQOS      =   Signal(4)
        self.ARLOCK     =   Signal(1)
        self.RDATA      =   Signal(32)
        self.RRESP      =   Signal(2)
        self.RREADY     =   Signal(1)
        self.RVALID     =   Signal(1)
        self.RID        =   Signal(1)
        self.RUSER      =   Signal(1)
        self.RLAST      =   Signal(1)
        
        
        self.jtag_tck  =   Signal(1)
        self.jtag_tms   =   Signal(1)
        self.jtag_tdi   =   Signal(1)
        self.jtag_tdo   =   Signal(1)
        self.jtag_trst  =   Signal(1)
        self.probes_i   =   Signal(nprobes)
        self.probes_in  =   Signal(Input_Probe_Width)
        self.probes_out =   Signal(Ouput_Probe_width)
        self.eio_ip_clk = Signal(1)
        self.eio_op_clk = Signal(1)
        self.axilite =   Signal(155)
        self.axifull =   Signal(215)
        self.axi_sampling_clk = Signal(1)
        self.sampling_clk = Signal(1)
 
        probes_dict1 = {}
        for sublist in dummy_list:
            for value in sublist:
                probes_dict1[value] = Signal(1, name=f"i_sampling_clk_{value}")
        self.sampling_clk_int = probes_dict1
        probes_names1 = list(probes_dict1.keys())
        
       # nprobes = len(dummy_list)
        probes_dict = {}
        for sublist in dummy_list:
            for value in sublist:
                probes_dict[value] = Signal(probesize[value], name=f"probe_{value}")
        self.probes_intr = probes_dict
        probes_names = list(probes_dict.keys())
        
        if(Sampling_Clock== "MULTIPLE"):
            if mode == "NATIVE":
                if EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
               #     p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk             = Sampling_Clock,
                    p_No_Probes                = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize)}"),
                    p_Cores                    = Instance.PreformattedParam(nprobes),
                    p_Mem_Depth                = Instance.PreformattedParam(mem_depth),
                    p_Probe01_Width            = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width            = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width            = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width            = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width            = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width            = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width            = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width            = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width       = Instance.PreformattedParam(Ouput_Probe_width),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress         = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress         = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress         = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress         = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress         = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress         = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress         = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress         = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress         = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"),      
                    p_IF01_Probes              = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes              = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes              = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes              = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes              = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes              = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes              = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes              = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes              = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes              = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes              = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes              = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes              = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes              = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes              = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,


                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK              = ClockSignal(),
                    i_eio_ip_clk        = self.eio_ip_clk,
                    i_eio_op_clk        = self.eio_op_clk,
                    i_jtag_tck          = self.jtag_tck,
                    i_jtag_tms          = self.jtag_tms,
                    i_jtag_tdi          = self.jtag_tdi,
                    o_jtag_tdo          = self.jtag_tdo,
                    i_jtag_trst         = self.jtag_trst,
                    # OCLA Signals
                    i_probes            = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes    = self.axilite,
                    i_axi4_probes       = self.axifull,
                    i_probes_in         = self.probes_in,
                    o_probes_out        = self.probes_out,
                    )
                else:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
               #     p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk             = Sampling_Clock,
                    p_No_Probes                = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize)}"),
                    p_Cores                    = Instance.PreformattedParam(nprobes),
                    p_Mem_Depth                = Instance.PreformattedParam(mem_depth),
                    p_Probe01_Width            = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width            = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width            = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width            = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width            = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width            = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width            = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width            = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress         = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress         = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress         = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress         = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress         = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress         = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress         = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress         = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress         = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"),        
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    #i_axili_probes     = Cat(self.awaddr,self.awprot,self.awvalid),
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = self.axifull,
                    i_probes_in        = self.probes_in,
                    )                 

            elif mode == "AXI":
                if axi_type == "AXILite" and EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(0),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd152"),
                    p_Cores                    = Instance.PreformattedParam(1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
            
                   p_Probe01_Width           = Instance.PreformattedParam(f"11'd0"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_eio_ip_clk       = self.eio_ip_clk,
                    i_eio_op_clk       = self.eio_op_clk,
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = 0,
                    i_axiLite_probes     = Cat(self.awaddr,self.awprot,self.awvalid,self.awready,self.wdata,self.wstrb,self.wvalid,self.wready,self.bresp,self.bvalid,self.bready,self.araddr,self.arprot,self.arvalid,self.arready,self.rdata,self.rresp,self.rvalid,self.rready),
                    i_axi4_probes      = self.axifull,
                    i_probes_in        =self.probes_in,
                    o_probes_out       =self.probes_out,
                    )   
                elif axi_type == "AXI4" and EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(0),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd215"),
                    p_Cores                    = Instance.PreformattedParam(1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                
                  p_Probe01_Width           = Instance.PreformattedParam(f"11'd0"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      =Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_eio_ip_clk       = self.eio_ip_clk,
                    i_eio_op_clk       = self.eio_op_clk,
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = 0,
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = Cat(self.AWADDR,self.AWPROT,self.AWVALID,self.AWREADY,self.AWBURST,self.AWSIZE,self.AWLEN,self.AWID,self.AWCACHE,self.AWREGION,self.AWUSER,self.AWQOS,self.AWLOCK,self.WDATA,self.WSTRB,self.WVALID,self.WREADY,self.WID,self.WLAST,self.BRESP,self.BVALID,self.BREADY,self.BID,self.BUSER,self.ARADDR,self.ARPROT,self.ARVALID,self.ARREADY,self.ARBUSRT,self.ARSIZE,self.ARLEN,self.ARID,self.ARCACHE,self.ARREGION,self.ARUSER,self.ARQOS,self.ARLOCK,self.RDATA,self.RRESP,self.RREADY,self.RVALID,self.RID,self.RUSER,self.RLAST),
                    i_probes_in        =self.probes_in,
                    o_probes_out       =self.probes_out,
                    )

                elif axi_type == "AXI4" and EIO_Enable == 0:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(0),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd215"),
                    p_Cores                    = Instance.PreformattedParam(1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
               
                   p_Probe01_Width           = Instance.PreformattedParam(f"11'd0"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      =Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = 0,
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = Cat(self.AWADDR,self.AWPROT,self.AWVALID,self.AWREADY,self.AWBURST,self.AWSIZE,self.AWLEN,self.AWID,self.AWCACHE,self.AWREGION,self.AWUSER,self.AWQOS,self.AWLOCK,self.WDATA,self.WSTRB,self.WVALID,self.WREADY,self.WID,self.WLAST,self.BRESP,self.BVALID,self.BREADY,self.BID,self.BUSER,self.ARADDR,self.ARPROT,self.ARVALID,self.ARREADY,self.ARBUSRT,self.ARSIZE,self.ARLEN,self.ARID,self.ARCACHE,self.ARREGION,self.ARUSER,self.ARQOS,self.ARLOCK,self.RDATA,self.RRESP,self.RREADY,self.RVALID,self.RID,self.RUSER,self.RLAST),
                    i_probes_in        =self.probes_in,
                    )
                else:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(0),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd152"),
                    p_Cores                    = Instance.PreformattedParam(1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                 
                   p_Probe01_Width           = Instance.PreformattedParam(f"11'd0"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = 0,
                    i_axiLite_probes     = Cat(self.awaddr,self.awprot,self.awvalid,self.awready,self.wdata,self.wstrb,self.wvalid,self.wready,self.bresp,self.bvalid,self.bready,self.araddr,self.arprot,self.arvalid,self.arready,self.rdata,self.rresp,self.rvalid,self.rready),
                    i_axi4_probes      = self.axifull,
                    i_probes_in        =self.probes_in,
                    )   

            else:
                if axi_type == "AXILite" and EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize) + 152}"),
                    p_Cores                    = Instance.PreformattedParam(nprobes + 1), 
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                 
                  p_Probe01_Width           = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_eio_ip_clk       = self.eio_ip_clk,
                    i_eio_op_clk       = self.eio_op_clk,
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes     = Cat(self.awaddr,self.awprot,self.awvalid,self.awready,self.wdata,self.wstrb,self.wvalid,self.wready,self.bresp,self.bvalid,self.bready,self.araddr,self.arprot,self.arvalid,self.arready,self.rdata,self.rresp,self.rvalid,self.rready),
                    i_axi4_probes      = self.axifull,
                    i_probes_in        =self.probes_in,
                    o_probes_out       =self.probes_out,
                    )   
                elif axi_type == "AXI4" and EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize) + 215}"),
                    p_Cores                    = Instance.PreformattedParam(nprobes + 1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                   
                  p_Probe01_Width           = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_eio_ip_clk       = self.eio_ip_clk,
                    i_eio_op_clk       = self.eio_op_clk,
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = Cat(self.AWADDR,self.AWPROT,self.AWVALID,self.AWREADY,self.AWBURST,self.AWSIZE,self.AWLEN,self.AWID,self.AWCACHE,self.AWREGION,self.AWUSER,self.AWQOS,self.AWLOCK,self.WDATA,self.WSTRB,self.WVALID,self.WREADY,self.WID,self.WLAST,self.BRESP,self.BVALID,self.BREADY,self.BID,self.BUSER,self.ARADDR,self.ARPROT,self.ARVALID,self.ARREADY,self.ARBUSRT,self.ARSIZE,self.ARLEN,self.ARID,self.ARCACHE,self.ARREGION,self.ARUSER,self.ARQOS,self.ARLOCK,self.RDATA,self.RRESP,self.RREADY,self.RVALID,self.RID,self.RUSER,self.RLAST),
                    i_probes_in        =self.probes_in,
                    o_probes_out       =self.probes_out,
                    )

                elif axi_type == "AXI4" and EIO_Enable == 0:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize) + 215}"),
                    p_Cores                    = Instance.PreformattedParam(nprobes + 1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                   
                  p_Probe01_Width           = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = Cat(self.AWADDR,self.AWPROT,self.AWVALID,self.AWREADY,self.AWBURST,self.AWSIZE,self.AWLEN,self.AWID,self.AWCACHE,self.AWREGION,self.AWUSER,self.AWQOS,self.AWLOCK,self.WDATA,self.WSTRB,self.WVALID,self.WREADY,self.WID,self.WLAST,self.BRESP,self.BVALID,self.BREADY,self.BID,self.BUSER,self.ARADDR,self.ARPROT,self.ARVALID,self.ARREADY,self.ARBUSRT,self.ARSIZE,self.ARLEN,self.ARID,self.ARCACHE,self.ARREGION,self.ARUSER,self.ARQOS,self.ARLOCK,self.RDATA,self.RRESP,self.RREADY,self.RVALID,self.RID,self.RUSER,self.RLAST),
                    i_probes_in        =self.probes_in,
                    )
                else:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize) + 152}"),
                    p_Cores                    = Instance.PreformattedParam(nprobes + 1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                   
                   p_Probe01_Width           = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = Cat(*[probes_dict1[value] for value in probes_names1]),
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes     = Cat(self.awaddr,self.awprot,self.awvalid,self.awready,self.wdata,self.wstrb,self.wvalid,self.wready,self.bresp,self.bvalid,self.bready,self.araddr,self.arprot,self.arvalid,self.arready,self.rdata,self.rresp,self.rvalid,self.rready),
                    i_axi4_probes      = self.axifull,
                    i_probes_in        =self.probes_in,
                    )
        else:
            if mode == "NATIVE":
                if EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
               #     p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize)}"),
                    p_Cores                    = Instance.PreformattedParam(len(dummy_list)),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                   
                 p_Probe01_Width           = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                   p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"),       
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,


                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_eio_ip_clk       = self.eio_ip_clk,
                    i_eio_op_clk       = self.eio_op_clk,
                    i_jtag_tck        =  self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    #i_axiLite_probes     = Cat(self.awaddr,self.awprot,self.awvalid),
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = self.axifull,
                    i_probes_in        =self.probes_in,
                    o_probes_out       =self.probes_out,
                    )
                else:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
               #     p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize)}"),
                    p_Cores                    = Instance.PreformattedParam(len(dummy_list)),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                  
                  p_Probe01_Width           = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"),       
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      =  self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    #i_axili_probes     = Cat(self.awaddr,self.awprot,self.awvalid),
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = self.axifull,
                    i_probes_in        = self.probes_in,
                    )                 

            elif mode == "AXI":
                if axi_type == "AXILite" and EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(0),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd152"),
                    p_Cores                    = Instance.PreformattedParam(1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                  
                   p_Probe01_Width           = Instance.PreformattedParam(f"11'd0"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      =  self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_eio_ip_clk       = self.eio_ip_clk,
                    i_eio_op_clk       = self.eio_op_clk,
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = 0,
                    i_axiLite_probes     = Cat(self.awaddr,self.awprot,self.awvalid,self.awready,self.wdata,self.wstrb,self.wvalid,self.wready,self.bresp,self.bvalid,self.bready,self.araddr,self.arprot,self.arvalid,self.arready,self.rdata,self.rresp,self.rvalid,self.rready),
                    i_axi4_probes      = self.axifull,
                    i_probes_in        =self.probes_in,
                    o_probes_out       =self.probes_out,
                    )   
                elif axi_type == "AXI4" and EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(0),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd215"),
                    p_Cores                    = Instance.PreformattedParam(1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                 
                   p_Probe01_Width           = Instance.PreformattedParam(f"11'd0"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                   p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_eio_ip_clk       = self.eio_ip_clk,
                    i_eio_op_clk       = self.eio_op_clk,
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = 0,
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = Cat(self.AWADDR,self.AWPROT,self.AWVALID,self.AWREADY,self.AWBURST,self.AWSIZE,self.AWLEN,self.AWID,self.AWCACHE,self.AWREGION,self.AWUSER,self.AWQOS,self.AWLOCK,self.WDATA,self.WSTRB,self.WVALID,self.WREADY,self.WID,self.WLAST,self.BRESP,self.BVALID,self.BREADY,self.BID,self.BUSER,self.ARADDR,self.ARPROT,self.ARVALID,self.ARREADY,self.ARBUSRT,self.ARSIZE,self.ARLEN,self.ARID,self.ARCACHE,self.ARREGION,self.ARUSER,self.ARQOS,self.ARLOCK,self.RDATA,self.RRESP,self.RREADY,self.RVALID,self.RID,self.RUSER,self.RLAST),
                    i_probes_in        =self.probes_in,
                    o_probes_out       =self.probes_out,
                    )

                elif axi_type == "AXI4" and EIO_Enable == 0:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(0),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd215"),
                    p_Cores                    = Instance.PreformattedParam(1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                
                   p_Probe01_Width           = Instance.PreformattedParam(f"11'd0"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                   p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = 0,
                    i_axiLite_probes     = self.axilite,
                    i_axi4_probes      = Cat(self.AWADDR,self.AWPROT,self.AWVALID,self.AWREADY,self.AWBURST,self.AWSIZE,self.AWLEN,self.AWID,self.AWCACHE,self.AWREGION,self.AWUSER,self.AWQOS,self.AWLOCK,self.WDATA,self.WSTRB,self.WVALID,self.WREADY,self.WID,self.WLAST,self.BRESP,self.BVALID,self.BREADY,self.BID,self.BUSER,self.ARADDR,self.ARPROT,self.ARVALID,self.ARREADY,self.ARBUSRT,self.ARSIZE,self.ARLEN,self.ARID,self.ARCACHE,self.ARREGION,self.ARUSER,self.ARQOS,self.ARLOCK,self.RDATA,self.RRESP,self.RREADY,self.RVALID,self.RID,self.RUSER,self.RLAST),
                    i_probes_in        =self.probes_in,
                    )
                else:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(0),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd152"),
                    p_Cores                    = Instance.PreformattedParam(1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                   
                   p_Probe01_Width           = Instance.PreformattedParam(f"11'd0"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                   p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h0000000000000000"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      =  self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_jtag_tck        = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = 0,
                    i_axiLite_probes     = Cat(self.awaddr,self.awprot,self.awvalid,self.awready,self.wdata,self.wstrb,self.wvalid,self.wready,self.bresp,self.bvalid,self.bready,self.araddr,self.arprot,self.arvalid,self.arready,self.rdata,self.rresp,self.rvalid,self.rready),
                    i_axi4_probes      = self.axifull,
                    i_probes_in        =self.probes_in,
                    )   

            else:
                if axi_type == "AXILite" and EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                  = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                    = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION               = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                     = mode,
                    p_Axi_Type                 = axi_type,
                    p_EIO_Enable               = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk           = Sampling_Clock,
                    p_No_Probes             = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum               = Instance.PreformattedParam(f"14'd{sum(probesize) + 152}"),
                    p_Cores                    = Instance.PreformattedParam(len(dummy_list) + 1),
                    p_Mem_Depth               = Instance.PreformattedParam(mem_depth),
                  
                 p_Probe01_Width           = Instance.PreformattedParam(f"11'd{probesize[0]}"),
                    p_Probe02_Width           = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width           = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width           = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width           = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width           = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width           = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width           = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width            = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width            = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width            = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width            = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width            = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width            = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width            = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width        = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                    p_EIO_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress     = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress         = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress         = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress         = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress         = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress         = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress         = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      =  self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK       = ClockSignal(),
                    i_eio_ip_clk       = self.eio_ip_clk,
                    i_eio_op_clk       = self.eio_op_clk,
                    i_jtag_tck         = self.jtag_tck,
                    i_jtag_tms         = self.jtag_tms,
                    i_jtag_tdi         = self.jtag_tdi,
                    o_jtag_tdo         = self.jtag_tdo,
                    i_jtag_trst        = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes   = Cat(self.awaddr,self.awprot,self.awvalid,self.awready,self.wdata,self.wstrb,self.wvalid,self.wready,self.bresp,self.bvalid,self.bready,self.araddr,self.arprot,self.arvalid,self.arready,self.rdata,self.rresp,self.rvalid,self.rready),
                    i_axi4_probes      = self.axifull,
                    i_probes_in        =self.probes_in,
                    o_probes_out       =self.probes_out,
                    )   
                elif axi_type == "AXI4" and EIO_Enable:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                   = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                     = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION                = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                      = mode,
                    p_Axi_Type                  = axi_type,
                    p_EIO_Enable                = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk              = Sampling_Clock,
                    p_No_Probes                 = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum                = Instance.PreformattedParam(f"14'd{sum(probesize) + 215}"),
                    p_Cores                     = Instance.PreformattedParam(len(dummy_list) + 1),
                    p_Mem_Depth                 = Instance.PreformattedParam(mem_depth),
                
                    p_Probe01_Width             = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width             = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width             = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width             = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width             = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width             = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width             = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width             = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width             = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width             = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width             = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width             = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width             = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width             = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width             = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_Input_Probe_Width         = Instance.PreformattedParam(Input_Probe_Width),
                    p_Output_Probe_Width        = Instance.PreformattedParam(Ouput_Probe_width),
                    p_EIO_BaseAddress           = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress      = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress          = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress          = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress          = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress          = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress          = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress          = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      =  self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK              = ClockSignal(),
                    i_eio_ip_clk        = self.eio_ip_clk,
                    i_eio_op_clk        = self.eio_op_clk,
                    i_jtag_tck          = self.jtag_tck,
                    i_jtag_tms          = self.jtag_tms,
                    i_jtag_tdi          = self.jtag_tdi,
                    o_jtag_tdo          = self.jtag_tdo,
                    i_jtag_trst         = self.jtag_trst,
                    # OCLA Signals
                    i_probes            = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes    = self.axilite,
                    i_axi4_probes       = Cat(self.AWADDR,self.AWPROT,self.AWVALID,self.AWREADY,self.AWBURST,self.AWSIZE,self.AWLEN,self.AWID,self.AWCACHE,self.AWREGION,self.AWUSER,self.AWQOS,self.AWLOCK,self.WDATA,self.WSTRB,self.WVALID,self.WREADY,self.WID,self.WLAST,self.BRESP,self.BVALID,self.BREADY,self.BID,self.BUSER,self.ARADDR,self.ARPROT,self.ARVALID,self.ARREADY,self.ARBUSRT,self.ARSIZE,self.ARLEN,self.ARID,self.ARCACHE,self.ARREGION,self.ARUSER,self.ARQOS,self.ARLOCK,self.RDATA,self.RRESP,self.RREADY,self.RVALID,self.RID,self.RUSER,self.RLAST),
                    i_probes_in         =self.probes_in,
                    o_probes_out        =self.probes_out,
                    )

                elif axi_type == "AXI4" and EIO_Enable == 0:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                   = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                     = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION                = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                      = mode,
                    p_Axi_Type                  = axi_type,
                    p_EIO_Enable                = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk              = Sampling_Clock,
                    p_No_Probes                 = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum                = Instance.PreformattedParam(f"14'd{sum(probesize) + 215}"),
                    p_Cores                     = Instance.PreformattedParam(len(dummy_list) + 1),
                    p_Mem_Depth                 = Instance.PreformattedParam(mem_depth),
                 
                    p_Probe01_Width             = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width             = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width             = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width             = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width             = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width             = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width             = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width             = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width             = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width             = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width             = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width             = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width             = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width             = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width             = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_EIO_BaseAddress           = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress      = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress          = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress          = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress          = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress          = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress          = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress          = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      =  self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK              = ClockSignal(),
                    i_jtag_tck          = self.jtag_tck,
                    i_jtag_tms          = self.jtag_tms,
                    i_jtag_tdi          = self.jtag_tdi,
                    o_jtag_tdo          = self.jtag_tdo,
                    i_jtag_trst         = self.jtag_trst,
                    # OCLA Signals
                    i_probes           = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes   = self.axilite,
                    i_axi4_probes      = Cat(self.AWADDR,self.AWPROT,self.AWVALID,self.AWREADY,self.AWBURST,self.AWSIZE,self.AWLEN,self.AWID,self.AWCACHE,self.AWREGION,self.AWUSER,self.AWQOS,self.AWLOCK,self.WDATA,self.WSTRB,self.WVALID,self.WREADY,self.WID,self.WLAST,self.BRESP,self.BVALID,self.BREADY,self.BID,self.BUSER,self.ARADDR,self.ARPROT,self.ARVALID,self.ARREADY,self.ARBUSRT,self.ARSIZE,self.ARLEN,self.ARID,self.ARCACHE,self.ARREGION,self.ARUSER,self.ARQOS,self.ARLOCK,self.RDATA,self.RRESP,self.RREADY,self.RVALID,self.RID,self.RUSER,self.RLAST),
                    i_probes_in        = self.probes_in,
                    )
                else:
                    self.specials += Instance("ocla_debug_subsystem",
                    # Parameters.
                    # -----------   
                    p_IP_TYPE                   = Instance.PreformattedParam("IP_TYPE"),
                    p_IP_ID                     = Instance.PreformattedParam("IP_ID"),
                    p_IP_VERSION                = Instance.PreformattedParam("IP_VERSION"),
                    p_Mode                      = mode,
                    p_Axi_Type                  = axi_type,
                    p_EIO_Enable                = Instance.PreformattedParam(EIO_Enable),
                    p_Sampling_Clk              = Sampling_Clock,
                    p_No_Probes                 = Instance.PreformattedParam(nprobes),
                    p_Probes_Sum                = Instance.PreformattedParam(f"14'd{sum(probesize) + 152}"),
                    p_Cores                     = Instance.PreformattedParam(len(dummy_list) + 1),
                    p_Mem_Depth                 = Instance.PreformattedParam(mem_depth),
            
                    p_Probe01_Width             = Instance.PreformattedParam(f"11'd{probesize[1]}"),
                    p_Probe02_Width             = Instance.PreformattedParam(f"11'd{probesize[2]}"),
                    p_Probe03_Width             = Instance.PreformattedParam(f"11'd{probesize[3]}"),
                    p_Probe04_Width             = Instance.PreformattedParam(f"11'd{probesize[4]}"),
                    p_Probe05_Width             = Instance.PreformattedParam(f"11'd{probesize[5]}"),                
                    p_Probe06_Width             = Instance.PreformattedParam(f"11'd{probesize[6]}"),
                    p_Probe07_Width             = Instance.PreformattedParam(f"11'd{probesize[7]}"),
                    p_Probe08_Width             = Instance.PreformattedParam(f"11'd{probesize[8]}"),
                    p_Probe09_Width             = Instance.PreformattedParam(f"11'd{probesize[9]}"),
                    p_Probe10_Width             = Instance.PreformattedParam(f"11'd{probesize[10]}"),
                    p_Probe11_Width             = Instance.PreformattedParam(f"11'd{probesize[11]}"),                
                    p_Probe12_Width             = Instance.PreformattedParam(f"11'd{probesize[12]}"),
                    p_Probe13_Width             = Instance.PreformattedParam(f"11'd{probesize[13]}"),
                    p_Probe14_Width             = Instance.PreformattedParam(f"11'd{probesize[14]}"),
                    p_Probe15_Width             = Instance.PreformattedParam(f"11'd{probesize[15]}"),
                    p_EIO_BaseAddress           = Instance.PreformattedParam("32'h01000000"),
                    p_AXI_Core_BaseAddress      = Instance.PreformattedParam("32'h02000000"),
                    p_IF01_BaseAddress          = Instance.PreformattedParam("32'h03000000"),
                    p_IF02_BaseAddress          = Instance.PreformattedParam("32'h04000000"),
                    p_IF03_BaseAddress          = Instance.PreformattedParam("32'h05000000"),
                    p_IF04_BaseAddress          = Instance.PreformattedParam("32'h06000000"),
                    p_IF05_BaseAddress          = Instance.PreformattedParam("32'h07000000"),
                    p_IF06_BaseAddress          = Instance.PreformattedParam("32'h08000000"),
                    p_IF07_BaseAddress          = Instance.PreformattedParam("32'h09000000"),
                    p_IF08_BaseAddress          = Instance.PreformattedParam("32'h01000000"),
                    p_IF09_BaseAddress          = Instance.PreformattedParam("32'h01100000"),
                    p_IF10_BaseAddress          = Instance.PreformattedParam("32'h01200000"),
                    p_IF11_BaseAddress          = Instance.PreformattedParam("32'h01300000"),
                    p_IF12_BaseAddress          = Instance.PreformattedParam("32'h01400000"),
                    p_IF13_BaseAddress          = Instance.PreformattedParam("32'h01500000"),
                    p_IF14_BaseAddress          = Instance.PreformattedParam("32'h01600000"),
                    p_IF15_BaseAddress          = Instance.PreformattedParam("32'h01700000"), 
                    p_IF01_Probes               = Instance.PreformattedParam(f"64'h{if1_probes[15]}{if1_probes[14]}{if1_probes[13]}{if1_probes[12]}{if1_probes[11]}{if1_probes[10]}{if1_probes[9]}{if1_probes[8]}{if1_probes[7]}{if1_probes[6]}{if1_probes[5]}{if1_probes[4]}{if1_probes[3]}{if1_probes[2]}{if1_probes[1]}{if1_probes[0]}"),
                    p_IF02_Probes               = Instance.PreformattedParam(f"64'h{if2_probes[15]}{if2_probes[14]}{if2_probes[13]}{if2_probes[12]}{if2_probes[11]}{if2_probes[10]}{if2_probes[9]}{if2_probes[8]}{if2_probes[7]}{if2_probes[6]}{if2_probes[5]}{if2_probes[4]}{if2_probes[3]}{if2_probes[2]}{if2_probes[1]}{if2_probes[0]}"),
                    p_IF03_Probes               = Instance.PreformattedParam(f"64'h{if3_probes[15]}{if3_probes[14]}{if3_probes[13]}{if3_probes[12]}{if3_probes[11]}{if3_probes[10]}{if3_probes[9]}{if3_probes[8]}{if3_probes[7]}{if3_probes[6]}{if3_probes[5]}{if3_probes[4]}{if3_probes[3]}{if3_probes[2]}{if3_probes[1]}{if3_probes[0]}"),
                    p_IF04_Probes               = Instance.PreformattedParam(f"64'h{if4_probes[15]}{if4_probes[14]}{if4_probes[13]}{if4_probes[12]}{if4_probes[11]}{if4_probes[10]}{if4_probes[9]}{if4_probes[8]}{if4_probes[7]}{if4_probes[6]}{if4_probes[5]}{if4_probes[4]}{if4_probes[3]}{if4_probes[2]}{if4_probes[1]}{if4_probes[0]}"),
                    p_IF05_Probes               = Instance.PreformattedParam(f"64'h{if5_probes[15]}{if5_probes[14]}{if5_probes[13]}{if5_probes[12]}{if5_probes[11]}{if5_probes[10]}{if5_probes[9]}{if5_probes[8]}{if5_probes[7]}{if5_probes[6]}{if5_probes[5]}{if5_probes[4]}{if5_probes[3]}{if5_probes[2]}{if5_probes[1]}{if5_probes[0]}"),
                    p_IF06_Probes               = Instance.PreformattedParam(f"64'h{if6_probes[15]}{if6_probes[14]}{if6_probes[13]}{if6_probes[12]}{if6_probes[11]}{if6_probes[10]}{if6_probes[9]}{if6_probes[8]}{if6_probes[7]}{if6_probes[6]}{if6_probes[5]}{if6_probes[4]}{if6_probes[3]}{if6_probes[2]}{if6_probes[1]}{if6_probes[0]}"),
                    p_IF07_Probes               = Instance.PreformattedParam(f"64'h{if7_probes[15]}{if7_probes[14]}{if7_probes[13]}{if7_probes[12]}{if7_probes[11]}{if7_probes[10]}{if7_probes[9]}{if7_probes[8]}{if7_probes[7]}{if7_probes[6]}{if7_probes[5]}{if7_probes[4]}{if7_probes[3]}{if7_probes[2]}{if7_probes[1]}{if7_probes[0]}"),
                    p_IF08_Probes               = Instance.PreformattedParam(f"64'h{if8_probes[15]}{if8_probes[14]}{if8_probes[13]}{if8_probes[12]}{if8_probes[11]}{if8_probes[10]}{if8_probes[9]}{if8_probes[8]}{if8_probes[7]}{if8_probes[6]}{if8_probes[5]}{if8_probes[4]}{if8_probes[3]}{if8_probes[2]}{if8_probes[1]}{if8_probes[0]}"),
                    p_IF09_Probes               = Instance.PreformattedParam(f"64'h{if9_probes[15]}{if9_probes[14]}{if9_probes[13]}{if9_probes[12]}{if9_probes[11]}{if9_probes[10]}{if9_probes[9]}{if9_probes[8]}{if9_probes[7]}{if9_probes[6]}{if9_probes[5]}{if9_probes[4]}{if9_probes[3]}{if9_probes[2]}{if9_probes[1]}{if9_probes[0]}"),
                    p_IF10_Probes               = Instance.PreformattedParam(f"64'h{if10_probes[15]}{if10_probes[14]}{if10_probes[13]}{if10_probes[12]}{if10_probes[11]}{if10_probes[10]}{if10_probes[9]}{if10_probes[8]}{if10_probes[7]}{if10_probes[6]}{if10_probes[5]}{if10_probes[4]}{if10_probes[3]}{if10_probes[2]}{if10_probes[1]}{if10_probes[0]}"),
                    p_IF11_Probes               = Instance.PreformattedParam(f"64'h{if11_probes[15]}{if11_probes[14]}{if11_probes[13]}{if11_probes[12]}{if11_probes[11]}{if11_probes[10]}{if11_probes[9]}{if11_probes[8]}{if11_probes[7]}{if11_probes[6]}{if11_probes[5]}{if11_probes[4]}{if11_probes[3]}{if11_probes[2]}{if11_probes[1]}{if11_probes[0]}"),
                    p_IF12_Probes               = Instance.PreformattedParam(f"64'h{if12_probes[15]}{if12_probes[14]}{if12_probes[13]}{if12_probes[12]}{if12_probes[11]}{if12_probes[10]}{if12_probes[9]}{if12_probes[8]}{if12_probes[7]}{if12_probes[6]}{if12_probes[5]}{if12_probes[4]}{if12_probes[3]}{if12_probes[2]}{if12_probes[1]}{if12_probes[0]}"),
                    p_IF13_Probes               = Instance.PreformattedParam(f"64'h{if13_probes[15]}{if13_probes[14]}{if13_probes[13]}{if13_probes[12]}{if13_probes[11]}{if13_probes[10]}{if13_probes[9]}{if13_probes[8]}{if13_probes[7]}{if13_probes[6]}{if13_probes[5]}{if13_probes[4]}{if13_probes[3]}{if13_probes[2]}{if13_probes[1]}{if13_probes[0]}"),
                    p_IF14_Probes               = Instance.PreformattedParam(f"64'h{if14_probes[15]}{if14_probes[14]}{if14_probes[13]}{if14_probes[12]}{if14_probes[11]}{if14_probes[10]}{if14_probes[9]}{if14_probes[8]}{if14_probes[7]}{if14_probes[6]}{if14_probes[5]}{if14_probes[4]}{if14_probes[3]}{if14_probes[2]}{if14_probes[1]}{if14_probes[0]}"),
                    p_IF15_Probes               = Instance.PreformattedParam(f"64'h{if15_probes[15]}{if15_probes[14]}{if15_probes[13]}{if15_probes[12]}{if15_probes[11]}{if15_probes[10]}{if15_probes[9]}{if15_probes[8]}{if15_probes[7]}{if15_probes[6]}{if15_probes[5]}{if15_probes[4]}{if15_probes[3]}{if15_probes[2]}{if15_probes[1]}{if15_probes[0]}"),
                    # sampling Clk / Rst.
                    # ----------
                    i_native_sampling_clk      = self.sampling_clk,
                    i_axi_sampling_clk     = self.axi_sampling_clk,
                    i_RESETn             = ResetSignal("rstn"),
                    # AXI Clk / Rst.
                    # ----------
                    i_ACLK              = ClockSignal(),
                    i_jtag_tck          = self.jtag_tck,
                    i_jtag_tms          = self.jtag_tms,
                    i_jtag_tdi          = self.jtag_tdi,
                    o_jtag_tdo          = self.jtag_tdo,
                    i_jtag_trst         = self.jtag_trst,
                    # OCLA Signals
                    i_probes            = Cat(*[probes_dict[value] for value in probes_names]),
                    i_axiLite_probes    = Cat(self.awaddr,self.awprot,self.awvalid,self.awready,self.wdata,self.wstrb,self.wvalid,self.wready,self.bresp,self.bvalid,self.bready,self.araddr,self.arprot,self.arvalid,self.arready,self.rdata,self.rresp,self.rvalid,self.rready),
                    i_axi4_probes       = self.axifull,
                    i_probes_in         = self.probes_in,
                    )
        # Add Sources.
        # ------------
        self.add_sources(platform)
        
        
        
    
    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "ocla_debug_subsystem.sv"))
