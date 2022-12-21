#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import json
import argparse

from litex_wrapper.axil_ocla_litex_wrapper import AXILITEOCLA

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex.soc.interconnect.axi import AXILiteInterface


# IOs/Interfaces -----------------------------------------------------------------------------------
def get_axiclknrst_ios():
    return [
        ("i_S_AXI_ACLK",      0, Pins(1)),
        ("i_S_AXI_ARESETN",   0, Pins(1)),
    ]

def get_samplingclknrst_ios():
    return [
        ("i_sample_clk",  0, Pins(1)),
        ("i_rstn",        0, Pins(1)),
    ]    
    
def get_ocla_ios(nprobes,trigger_inputs):
    return [
        ("i_probes",       0, Pins(nprobes)),
        ("i_trigger_input",   0, Pins(trigger_inputs)), 
    ]

# AXI LITE OCLA Wrapper ----------------------------------------------------------------------------------
class AXILITEOCLAWrapper(Module):
    def __init__(self, platform, address_width, data_width, nprobes, trigger_inputs, probe_widht,mem_depth, trigger_inputs_en):
        
        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_axiclknrst_ios())
        self.clock_domains.cd_sys  = ClockDomain()
        self.comb += self.cd_sys.clk.eq(platform.request("i_S_AXI_ACLK"))
        self.comb += self.cd_sys.rst.eq(platform.request("i_S_AXI_ARESETN"))

        # Clocking ---------------------------------------------------------------------------------
        platform.add_extension(get_samplingclknrst_ios())
        self.clock_domains.cd_sys  = ClockDomain("i_sample_clk")
        self.comb += self.cd_sys.clk.eq(platform.request("i_sample_clk"))
        self.clock_domains.cd_sys  = ClockDomain("i_rstn")
        self.comb += self.cd_sys.rst.eq(platform.request("i_rstn"))

        # AXI LITE --------------------------------------------------------------------------------------
        s_axil = AXILiteInterface(
            address_width       = address_width,
            data_width          = data_width
        )
        platform.add_extension(s_axil.get_ios("s_axil"))
        self.comb += s_axil.connect_to_pads(platform.request("s_axil"), mode="slave")

        # AXI-LITE-OCLA ----------------------------------------------------------------------------------
       
        self.submodules.ocla = ocla =  AXILITEOCLA(platform, 
            s_axil             = s_axil,
            nprobes          = nprobes,
            trigger_inputs   = trigger_inputs,
            probe_widht      = probe_widht,
            mem_depth        = mem_depth,
            trigger_inputs_en   = trigger_inputs_en
            )
        # OCLA Signals --------------------------------------------------------------------------------
        # print (int(nprobes),int(trigger_inputs))
        platform.add_extension(get_ocla_ios(nprobes,trigger_inputs))
        
        # Inputs
        self.comb += ocla.probes_i.eq(platform.request("i_probes"))
        if(trigger_inputs_en == True):
            self.comb += ocla.trigger_input_i.eq(platform.request("i_trigger_input"))
    

# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AXI LITE OCLA CORE")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    #common_path = os.path.join(os.path.dirname(__file__),"lib")

    sys.path.append(common_path)


    from common import IP_Builder
   # Parameter Dependency dictionary a 2 b 3 c 4  9

    #                Ports     :    Dependency
    dep_dict = {}            


    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="axil_ocla", language="sverilog")

    # Core fix value parameters.
    core_fix_param_group = parser.add_argument_group(title="OCLA IP Core fix parameters")
    core_fix_param_group.add_argument("--mem_depth",       type=int,  default=32, choices=[32, 64, 128, 256, 512, 1024],          help="OCLA Trace Memory Depth.")
    core_fix_param_group.add_argument("--addr_width",      type=int,  default=32, choices=[8, 16, 32],     help="OCLA Address Width.")
    core_fix_param_group.add_argument("--data_width",      type=int,  default=32, choices=[32], help="OCLA Data Width.")
    
    # Core range value parameters.

    core_range_param_group = parser.add_argument_group(title="OCLA IP Core range parameters")
    core_range_param_group.add_argument("--no_of_probes",           type=int,  default=1, choices=range(1,1025),         help="Number of Probes.")
    core_range_param_group.add_argument("--no_of_trigger_inputs",   type=int,  default=1,  choices=range(1,32),          help="Number of Input Triggers.")
    core_range_param_group.add_argument("--probe_width",            type=int,  default=1,  choices=range(1, 32),         help="Width of probe for Value Compare. Only applicable when value compare feature is enable")

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="axil_ocla_wrapper",    help="Build Folder Name, Build RTL File Name and Module Name")

  # Core bool value macros.
    core_bool_param_group = parser.add_argument_group(title="OCLA IP Core bool parameters")
    core_bool_param_group.add_argument("--value_compare",     type=bool, default=False,              help="To enable Value Compare feature")
    core_bool_param_group.add_argument("--advance_trigger",     type=bool, default=False,              help="To enable Advance Trigger Mode")
    core_bool_param_group.add_argument("--trigger_inputs_en",     type=bool, default=False,              help="To enable Trigger inputs")


    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                           help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",            help="Generate JSON Template")

    args = parser.parse_args()
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

    # Create LiteX Core ----------------------------------------------------------------------------
    platform   = OSFPGAPlatform( io=[], device="gemini", toolchain="raptor")
    module     = AXILITEOCLAWrapper(platform,
        address_width     = args.addr_width,
        data_width        = args.data_width,
        nprobes           = args.no_of_probes , 
        trigger_inputs    = args.no_of_trigger_inputs , 
        probe_widht       = args.probe_width , 
        mem_depth         = args.mem_depth,
        trigger_inputs_en = args.trigger_inputs_en
    )
    # Arguments ----------------------------------------------------------------------------
    value_compare     = args.value_compare
    advance_trigger   = args.advance_trigger
    triginpts_en      = args.trigger_inputs_en
    nofprobes         = args.no_of_probes  
    ntrigger_inputs   = args.no_of_trigger_inputs  
    nprobe_widht      = args.probe_width 
    memory_depth      = args.mem_depth
    
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )
        # Update the macro definition file ---------------------------------------------------------
        #rtl_dir = os.path.join(os.path.dirname(__file__),rs_builder.src_path+"/defines.sv")
        rtl_dir = rs_builder.src_path
        rtl_dir = rtl_dir + "/defines.sv"
        f = open(rtl_dir,"r+")
        content = f.read()
        f.seek(0, 0)
        f.write("// ---------------------------------------------------------------\n")
        f.write("// User specified macros\n")
        f.write("// ---------------------------------------------------------------\n")
        f.write("`define NUM_OF_PROBES  " + str(nofprobes) +"\n")
        f.write("`define MEMORY_DEPTH  " + str(memory_depth) +"\n")
        f.write("`define NUM_OF_TRIGGER_INPUTS  "+ str(ntrigger_inputs)+"\n")
        f.write("`define PROBE_WIDHT_BITS "+ str(nprobe_widht)+"\n")   
        if(value_compare):
            f.write("`define VALUE_COMPARE_TRIGGER   \n")
        if(triginpts_en):
            f.write("`define TRIGGER_INPUTS \n")
        if(advance_trigger):
            f.write("`define ADVANCE_TRIGGER \n\n")
        f.write(content)
        f.close()


if __name__ == "__main__":
    main()

