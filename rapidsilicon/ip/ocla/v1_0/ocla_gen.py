#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
from pathlib import Path
import argparse

from datetime import datetime

from litex_wrapper.ocla_litex_wrapper import AXILITEOCLA

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface

# Hold previous value of no_of probes
# IOs/Interfaces -----------------------------------------------------------------------------------
def get_axiclknrst_ios():
    return [
        ("clk",      0, Pins(1)),
    ]

def get_samplingclknrst_ios():
    return [
        ("rstn",        0, Pins(1)),
    ] 

def get_axisclk_ios():
    return [
        ("axi_sampling_clk",        0, Pins(1)),
    ]    
    
def get_nssclk_ios():
    return [
        ("sampling_clk",        0, Pins(1)),
    ]    
      
def get_sclk_ios(nprobes):
    sampleclk_pins = []
    for i in range(1, nprobes+1):
            pin_name = f"sampling_clk_{i}"
            sampleclk_pins.append((pin_name, 0, Pins(1)))
#            print("------",pins)
    return sampleclk_pins   
    
def jtag_interface():
    return [
    
        ("jtag_tck",   0, Pins(1)),
        ("jtag_tms",   0, Pins(1)),
        ("jtag_tdi",   0, Pins(1)),
        ("jtag_tdo",   0, Pins(1)),
        ("jtag_trst",  0, Pins(1)),
    ]

    
def get_ocla_ios(Input_Probe_Width,Ouput_Probe_width):
    return [
        ("probes_in",   0, Pins(Input_Probe_Width)),
        ("probes_out",   0, Pins(Ouput_Probe_width)), 
    ]
    
def get_eio_clk():
    return [
        ("eio_ip_clk",   0, Pins(1)),
        ("eio_op_clk",   0, Pins(1)), 
    ]
    
    
    
def get_axi_lite_ios():
    return [
        ("awaddr"   , 0, Pins(32)),
        ("awprot"   , 0, Pins(3)),
        ("awvalid"  , 0, Pins(1)),
        ("awready"  , 0, Pins(1)),
        ("wdata"    , 0, Pins(32)),
        ("wstrb"    , 0, Pins(4)),
        ("wvalid"   , 0, Pins(1)),
        ("wready"   , 0, Pins(1)),
        ("bresp"    , 0, Pins(2)),
        ("bvalid"   , 0, Pins(1)),
        ("bready"   , 0, Pins(1)),
        ("araddr"   , 0, Pins(32)),
        ("arprot"   , 0, Pins(3)),
        ("arvalid"  , 0, Pins(1)),
        ("arready"  , 0, Pins(1)),
        ("rdata"    , 0, Pins(32)),
        ("rresp"    , 0, Pins(2)),
        ("rvalid"   , 0, Pins(1)),
        ("rready"   , 0, Pins(1)),
    ]    
    
def get_axi_full_ios():
    return [
        ("AWADDR"   , 0, Pins(32)),
        ("AWPROT"   , 0, Pins(3)),
        ("AWVALID"  , 0, Pins(1)),
        ("AWREADY"  , 0, Pins(1)),
        ("AWBURST"  , 0, Pins(2)),
        ("AWSIZE"   , 0, Pins(3)),
        ("AWLEN"    , 0, Pins(8)),
        ("AWID"     , 0, Pins(1)),
        ("AWCACHE"  , 0, Pins(4)),
        ("AWREGION" , 0, Pins(4)),
        ("AWUSER"   , 0, Pins(1)),
        ("AWQOS"    , 0, Pins(4)),
        ("AWLOCK"   , 0, Pins(1)),
        ("WDATA"    , 0, Pins(32)),
        ("WSTRB"    , 0, Pins(4)),
        ("WVALID"   , 0, Pins(1)),
        ("WREADY"   , 0, Pins(1)),
        ("WID"      , 0, Pins(1)),
        ("WLAST"    , 0, Pins(1)),
        ("BRESP"    , 0, Pins(2)),
        ("BVALID"   , 0, Pins(1)),
        ("BREADY"   , 0, Pins(1)),
        ("BID"      , 0, Pins(1)),
        ("BUSER"    , 0, Pins(1)),
        ("ARADDR"   , 0, Pins(32)),
        ("ARPROT"   , 0, Pins(3)),
        ("ARVALID"  , 0, Pins(1)),
        ("ARREADY"  , 0, Pins(1)),
        ("ARBUSRT"  , 0, Pins(2)),
        ("ARSIZE"   , 0, Pins(3)),
        ("ARLEN"    , 0, Pins(8)),
        ("ARID"     , 0, Pins(1)),
        ("ARCACHE"  , 0, Pins(4)),
        ("ARREGION" , 0, Pins(4)),
        ("ARUSER"   , 0, Pins(1)),
        ("ARQOS"    , 0, Pins(4)),
        ("ARLOCK"   , 0, Pins(1)),
        ("RDATA"    , 0, Pins(32)),
        ("RRESP"    , 0, Pins(2)),
        ("RREADY"   , 0, Pins(1)),
        ("RVALID"   , 0, Pins(1)),
        ("RID"      , 0, Pins(1)),
        ("RUSER"    , 0, Pins(1)),
        ("RLAST"    , 0, Pins(1)),
    ]

def get_io_s(nprobes,probesize):
    pins = []
    are_all_zeros = all(element == 0 for element in probesize)
    if are_all_zeros:
        for i in range(1, nprobes+1):
            pin_name = f"probe_{i}"
            pin_width = "1"
            pins.append((pin_name, 0, Pins(pin_width)))
#            print("--i am in if ----" ,i,"----",nprobes ,  pins)
    else:
        for i in range(1, nprobes+1):
            pin_name = f"probe_{i}"
            pin_width = eval(f'probesize[i]')
            pins.append((pin_name, 0, Pins(pin_width)))
#            print("------",pins)
    return pins

# AXI LITE OCLA Wrapper ----------------------------------------------------------------------------------
class AXILITEOCLAWrapper(Module):
    def __init__(self, platform, address_width, data_width, nprobes,mem_depth,probesize,mode,axi_type,Sampling_Clock,EIO_Enable,Input_Probe_Width,Ouput_Probe_width):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_axiclknrst_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_samplingclknrst_ios())
        #self.clock_domains.cd_sys  = ClockDomain("i_sample_clk")
        #self.comb += self.cd_sys.clk.eq(platform.request("i_sample_clk"))
        self.clock_domains.cd_sys  = ClockDomain("rstn")
        self.comb += self.cd_sys.rst.eq(platform.request("rstn"))


        # AXI LITE --------------------------------------------------------------------------------------
        s_axil = AXILiteInterface(
            address_width       = address_width,
            data_width          = data_width
        )
        
      
   


        # AXI-LITE-OCLA ----------------------------------------------------------------------------------
        self.submodules.ocla = ocla =  AXILITEOCLA(platform, 
            s_axil              =   s_axil,
            nprobes             =   nprobes,
            mem_depth           =   mem_depth,
            probesize           =   probesize,
            mode                =   mode,
            axi_type            =   axi_type,
            Sampling_Clock      =   Sampling_Clock,
            EIO_Enable          =   EIO_Enable,
            Input_Probe_Width   =   Input_Probe_Width,
            Ouput_Probe_width   =   Ouput_Probe_width,
            )
        # OCLA Signals --------------------------------------------------------------------------------
        platform.add_extension(get_ocla_ios(Input_Probe_Width,Ouput_Probe_width))
        platform.add_extension(get_eio_clk())
        platform.add_extension(get_sclk_ios(nprobes))
        platform.add_extension(get_axi_lite_ios())
        platform.add_extension(get_axi_full_ios())
        platform.add_extension(get_nssclk_ios())
        platform.add_extension(jtag_interface())
        platform.add_extension(get_axisclk_ios())  
        self.comb += ocla.jtag_tck.eq(platform.request("jtag_tck"))
        self.comb += ocla.jtag_tms.eq(platform.request("jtag_tms"))
        self.comb += ocla.jtag_tdi.eq(platform.request("jtag_tdi"))
        self.comb += platform.request("jtag_tdo").eq(ocla.jtag_tdo)
        self.comb += ocla.jtag_trst.eq(platform.request("jtag_trst"))

        are_all_zeros = all(element == 0 for element in probesize)
        if EIO_Enable:
            self.comb += ocla.eio_ip_clk.eq(platform.request("eio_ip_clk"))
            self.comb += ocla.eio_op_clk.eq(platform.request("eio_op_clk"))
            self.comb += ocla.probes_in.eq(platform.request("probes_in"))
            self.comb += platform.request("probes_out").eq(ocla.probes_out) 
                   
        if are_all_zeros == False:
            platform.add_extension(get_io_s(nprobes, probesize))
            for i in range(1, nprobes+1):
                if mode == "NATIVE" or mode == "NATIVE_AXI":
                    self.comb += ocla.probes_intr[i].eq(platform.request(f"probe_{i}")) 

        if are_all_zeros == False:

            if Sampling_Clock == "MULTIPLE":
            #    platform.add_extension(get_sclk_ios(nprobes))
                for i in range(1, nprobes+1):
                    if mode == "NATIVE" or mode == "NATIVE_AXI":
                        self.comb += ocla.sampling_clk_int[i].eq(platform.request(f"sampling_clk_{i}"))
            else:
                if mode == "NATIVE" or mode == "NATIVE_AXI":
                    self.comb += ocla.sampling_clk.eq(platform.request("sampling_clk"))

            
                
            
        # Inputs
            
        if mode == "AXI" or mode == "NATIVE_AXI":
            self.comb += ocla.axi_sampling_clk.eq(platform.request("axi_sampling_clk"))
            if axi_type == "AXILite":
                self.comb += ocla.awaddr.eq(platform.request("awaddr"))
                self.comb += ocla.awprot.eq(platform.request("awprot"))
                self.comb += ocla.awvalid.eq(platform.request("awvalid"))
                self.comb += ocla.awready.eq(platform.request("awready"))
                self.comb += ocla.wdata.eq(platform.request("wdata"))
                self.comb += ocla.wstrb.eq(platform.request("wstrb"))
                self.comb += ocla.wvalid.eq(platform.request("wvalid"))
                self.comb += ocla.wready.eq(platform.request("wready"))
                self.comb += ocla.bresp.eq(platform.request("bresp"))
                self.comb += ocla.bvalid.eq(platform.request("bvalid"))
                self.comb += ocla.bready.eq(platform.request("bready"))
                self.comb += ocla.araddr.eq(platform.request("araddr"))
                self.comb += ocla.arprot.eq(platform.request("arprot"))
                self.comb += ocla.arvalid.eq(platform.request("arvalid"))
                self.comb += ocla.arready.eq(platform.request("arready"))
                self.comb += ocla.rdata.eq(platform.request("rdata"))
                self.comb += ocla.rresp.eq(platform.request("rresp"))
                self.comb += ocla.rvalid.eq(platform.request("rvalid"))
                self.comb += ocla.rready.eq(platform.request("rready"))
            else:
                self.comb += ocla.AWADDR.eq(platform.request("AWADDR"))
                self.comb += ocla.AWPROT.eq(platform.request("AWPROT"))
                self.comb += ocla.AWVALID.eq(platform.request("AWVALID"))
                self.comb += ocla.AWREADY.eq(platform.request("AWREADY"))
                self.comb += ocla.AWBURST.eq(platform.request("AWBURST"))
                self.comb += ocla.AWSIZE.eq(platform.request("AWSIZE"))
                self.comb += ocla.AWLEN.eq(platform.request("AWLEN"))
                self.comb += ocla.AWID.eq(platform.request("AWID"))
                self.comb += ocla.AWCACHE.eq(platform.request("AWCACHE"))
                self.comb += ocla.AWREGION.eq(platform.request("AWREGION"))
                self.comb += ocla.AWUSER.eq(platform.request("AWUSER"))
                self.comb += ocla.AWQOS.eq(platform.request("AWQOS"))
                self.comb += ocla.AWLOCK.eq(platform.request("AWLOCK"))
                self.comb += ocla.WDATA.eq(platform.request("WDATA"))
                self.comb += ocla.WSTRB.eq(platform.request("WSTRB"))
                self.comb += ocla.WVALID.eq(platform.request("WVALID"))
                self.comb += ocla.WREADY.eq(platform.request("WREADY"))
                self.comb += ocla.WID.eq(platform.request("WID"))
                self.comb += ocla.WLAST.eq(platform.request("WLAST"))
                self.comb += ocla.BRESP.eq(platform.request("BRESP"))
                self.comb += ocla.BVALID.eq(platform.request("BVALID"))
                self.comb += ocla.BREADY.eq(platform.request("BREADY"))
                self.comb += ocla.BID.eq(platform.request("BID"))
                self.comb += ocla.BUSER.eq(platform.request("BUSER"))
                self.comb += ocla.ARADDR.eq(platform.request("ARADDR"))
                self.comb += ocla.ARPROT.eq(platform.request("ARPROT"))
                self.comb += ocla.ARVALID.eq(platform.request("ARVALID"))
                self.comb += ocla.ARREADY.eq(platform.request("ARREADY"))
                self.comb += ocla.ARBUSRT.eq(platform.request("ARBUSRT"))
                self.comb += ocla.ARSIZE.eq(platform.request("ARSIZE"))
                self.comb += ocla.ARLEN.eq(platform.request("ARLEN"))
                self.comb += ocla.ARID.eq(platform.request("ARID"))
                self.comb += ocla.ARCACHE.eq(platform.request("ARCACHE"))
                self.comb += ocla.ARREGION.eq(platform.request("ARREGION"))
                self.comb += ocla.ARUSER.eq(platform.request("ARUSER"))
                self.comb += ocla.ARQOS.eq(platform.request("ARQOS"))
                self.comb += ocla.ARLOCK.eq(platform.request("ARLOCK"))
                self.comb += ocla.RDATA.eq(platform.request("RDATA"))
                self.comb += ocla.RRESP.eq(platform.request("RRESP"))
                self.comb += ocla.RREADY.eq(platform.request("RREADY"))
                self.comb += ocla.RVALID.eq(platform.request("RVALID"))
                self.comb += ocla.RID.eq(platform.request("RID"))
                self.comb += ocla.RUSER.eq(platform.request("RUSER"))
                self.comb += ocla.RLAST.eq(platform.request("RLAST"))
                

            #else:
             #   self.comb += s_axil.connect_to_pads(platform.request("s_axil"), mode="slave")
    
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI LITE OCLA CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")

    sys.path.append(common_path)

    from common import IP_Builder
    # Parameter Dependency dictionary a 2 b 3 c 4  9
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="ocla", language="sverilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="OCLA IP Core fix parameters")
    core_fix_param_group.add_argument("--mem_depth",             type=int,      default=32,     choices=[32, 64, 128, 256, 512, 1024],   help="OCLA Trace Memory Depth.")
    core_fix_param_group.add_argument("--s_axi_addr_width",      type=int,      default=32,     choices=[8, 16, 32],                     help="OCLA Address Width.")
    core_fix_param_group.add_argument("--s_axi_data_width",      type=int,      default=32,     choices=[32],                            help="OCLA Data Width.")
    
    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="OCLA IP Core range parameters")


 # Core bool value macros.
    core_bool_param_group = parser.add_argument_group(title="OCLA IP Core bool parameters")

   
    # Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--Sampling_Clock",     type=str,      default="SINGLE",      choices=["SINGLE","MULTIPLE"],           help="Select Equation")
    core_string_param_group.add_argument("--mode",               type=str,      default="NATIVE",      choices=["NATIVE","AXI","NATIVE_AXI"],    help="Select Equation")
    core_string_param_group.add_argument("--axi_type",           type=str,      default="AXILite",     choices=["AXILite","AXI4"],              help="Select Equation")


    core_range_param_group.add_argument("--no_of_probes",           type=int,  default=1,       choices=range(1,16),          help="Number of Probes.")
    core_bool_param_group.add_argument("--EIO_Enable",              type=bool, default=False,                                 help="To enable EIO")
    core_range_param_group.add_argument("--Input_Probe_Width",      type=int,  default=1,       choices=range(1,513),         help="EIO Probe In Width.")
    core_range_param_group.add_argument("--Ouput_Probe_width",      type=int,  default=1,       choices=range(1,513),         help="EIO Probe Out Width.")

   
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="ocla_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

    
    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'OCLA',
    'Version' : 'V1_0',
    'Interface' : 'JTAG ',
    'Description' : 'The On Chip Logic Analyzer (OCLA) core is a customizable logic analyzer that conforms to the JTAG specifi-cation and is intended for use in applications that necessitate verification or debugging through the monitoring ofinternal signals within a design on FPGAs'}
    }

    probe_size = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        num_elements  =len(vars(args))

        if (args.EIO_Enable == False):
            dep_dict.update({
                'Input_Probe_Width'     :     'True',
                'Ouput_Probe_width'     :     'True'
            })
            
        if (args.mode == 'NATIVE'):
            dep_dict.update({
                'axi_type'     :     'True'
            })

        if (args.mode == "AXI"):
            dep_dict.update({
                'no_of_probes'   :  'True',
                'probe1_Width'      : 'True'
            })

        n= args.no_of_probes
        for i in range(1, n+1):
            arg_name = "--probe" + str(i) + "_Width"
            arg_help = "probe " + str(i)
            core_range_param_group.add_argument(arg_name, type=int, default=1, choices=range(1, 1025), help="Size of Probe")
            
       # if (args.Sampling_Clock == "MULTIPLE"):
#
       #     n= args.no_of_probes
       #     for i in range(n):
       #         arg_name = "--probe" + str(i) + "_clk"
       #         arg_help = "probe_clock " + str(i)
       #         core_range_param_group.add_argument(arg_name, type=int, default=50, choices=range(1, 251), help="Probe Clock")

        if(num_elements == ((1*n) + 15)):
            for i in range (1, n+1):
                if((i + 15) <= num_elements):
                    arg_name = "probe" + str(i) + "_Width"
                    probe_size[i] = (eval(f'args.{arg_name}'))
                else:
                    probe_size[i] = 1

#        if (args.Sampling_Clock == "MULTIPLE"):
#
#            n= args.no_of_probes
#            for i in range(n):
#                arg_name = "--probe" + str(i) + "_clk"
#                arg_help = "probe_clock " + str(i)
#                core_range_param_group.add_argument(arg_name, type=int, default=50, choices=range(1, 251), help="Probe Clock")

    summary =  { 
    "Buffer size": args.mem_depth,
    "Debug Mode": args.mode,
    "Sampling Clock": args.Sampling_Clock,
        }
    if args.mode == "NATIVE" or args.mode == "NATIVE_AXI":
        summary["Number of Probes"] = args.no_of_probes

    if args.mode == "AXI" or args.mode == "NATIVE_AXI":
        if args.axi_type:
            summary["AXI Type Selected"] = args.axi_type
            
    if args.EIO_Enable:
            summary["EIO Feature Enabled"] = "YES"
            summary["EIO Input Port Width"] = args.Input_Probe_Width,
            summary["EIO Output Port Width"] = args.Ouput_Probe_width,


    else:
            summary["EIO Feature Enabled"] = "NO"
            
    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)
        
    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXILITEOCLAWrapper(platform,
        address_width     = args.s_axi_addr_width,
        data_width        = args.s_axi_data_width,
        nprobes           = args.no_of_probes, 
        mem_depth         = args.mem_depth,
        probesize         = probe_size,
        mode              = args.mode,
        axi_type          = args.axi_type,
        Sampling_Clock    = args.Sampling_Clock,
        EIO_Enable        = args.EIO_Enable,
        Input_Probe_Width = args.Input_Probe_Width,
        Ouput_Probe_width = args.Ouput_Probe_width
        
    )
     
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v1_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
            version  = "v1_0"
        )
        rtl_dir = rs_builder.src_path
        rtl_dir = rtl_dir + "/ocla_debug_subsystem.sv"
        f = open(rtl_dir,"r+")
        if args.Sampling_Clock == "MULTIPLE":
            f.write("`define single_sample_clock \n\n")
        f.close()
        
        # IP_ID Parameter
        now = datetime.now()
        my_year         = now.year - 2022
        year            = (bin(my_year)[2:]).zfill(7) # 7-bits  # Removing '0b' prefix = [2:]
        month           = (bin(now.month)[2:]).zfill(4) # 4-bits
        day             = (bin(now.day)[2:]).zfill(5) # 5-bits
        mod_hour        = now.hour % 12 # 12 hours Format
        hour            = (bin(mod_hour)[2:]).zfill(4) # 4-bits
        minute          = (bin(now.minute)[2:]).zfill(6) # 6-bits
        second          = (bin(now.second)[2:]).zfill(6) # 6-bits
        
        # Concatenation for IP_ID Parameter
        ip_id = ("{}{}{}{}{}{}").format(year, day, month, hour, minute, second)
        ip_id = ("32'h{}").format(hex(int(ip_id,2))[2:])
        
        # IP_VERSION parameter
        #               Base  _  Major _ Minor
        ip_version = "00000000_00000000_0000000000000001"
        ip_version = ("32'h{}").format(hex(int(ip_version, 2))[2:])
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "ocla", "v1_0", args.build_name, "src",args.build_name+".sv")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"OCLA\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)
        
        build_name = args.build_name.rsplit( ".", 1 )[ 0 ]
        file = os.path.join(args.build_dir, "rapidsilicon/ip/ocla/v1_0", build_name, "sim/ocla_wrapper_tb.sv")
        file = Path(file)
        text = file.read_text()
        text = text.replace("ocla_wrapper", "%s" % build_name)
        file.write_text(text)
        
if __name__ == "__main__":
    main()