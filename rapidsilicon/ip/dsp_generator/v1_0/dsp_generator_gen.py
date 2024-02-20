#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
from migen import *

from litex.gen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex_wrapper.dsp_litex_generator import *

# IOs / Interface ----------------------------------------------------------------------------------
def get_clkin_ios():
    return [
        ("clk",      0, Pins(1)),
        ("reset",    0, Pins(1))
    ]

def get_ios(a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, z_width):
    return [
        ("a",   0, Pins(a_width)),
        ("b",   0, Pins(b_width)),
        ("c",   0, Pins(c_width)),
        ("d",   0, Pins(d_width)),
        ("e",   0, Pins(e_width)),
        ("f",   0, Pins(f_width)),
        ("g",   0, Pins(g_width)),
        ("h",   0, Pins(h_width)),
        ("z",   0, Pins(z_width)),
    ]

class RS_DSP_Wrapper(Module):
    def __init__(self, platform, a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, equation, reg_in, reg_out, unsigned, feature):
    
    # Clocking
        self.clock_domains.cd_sys = ClockDomain()
        platform.add_extension(get_clkin_ios())
        
            # AxB
        if (equation == "AxB"):
            z_width = a_width + b_width
            platform.add_extension(get_ios(a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, z_width))
            if ((a_width >= 0 and a_width <=20) and (b_width >= 0 and b_width <=18)):
                self.submodules.dsp = dsp = RS_DSP_MULT(a_width, b_width, equation, reg_in, reg_out, unsigned)
            else:
                if(feature == "Base"):
                    if ((a_width > 54 and a_width <=72) or (b_width > 54 and b_width <=72)):
                        self.submodules.dsp = dsp = RS_DSP_MULT54(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif ((a_width > 36 and a_width <=54) or (b_width > 36 and b_width <=54)):
                        self.submodules.dsp = dsp = RS_DSP_MULT36(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif ((a_width > 20 and a_width <=36) or (b_width > 18 and b_width <=36)):
                        self.submodules.dsp = dsp = RS_DSP_MULT20(a_width, b_width, equation, reg_in, reg_out, unsigned)
                elif (feature == "Enhanced"):
                    if (unsigned):
                        if ((a_width > 51 and a_width <=72) or (b_width > 51 and b_width <=72)):
                            self.submodules.dsp = dsp = RS_DSP_MULT54_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                        elif ((a_width > 34 and a_width <=51) or (b_width > 34 and b_width <=51)):
                            self.submodules.dsp = dsp = RS_DSP_MULT36_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                        elif ((a_width > 20 and a_width <=34) or (b_width > 18 and b_width <=34)):
                            self.submodules.dsp = dsp = RS_DSP_MULT20_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif (not unsigned):
                        if ((a_width > 48 and a_width <=72) or (b_width > 48 and b_width <=72)):
                            self.submodules.dsp = dsp = RS_DSP_MULT54_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                        elif ((a_width > 32 and a_width <=48) or (b_width > 32 and b_width <=48)):
                            self.submodules.dsp = dsp = RS_DSP_MULT36_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                        elif ((a_width > 20 and a_width <=32) or (b_width > 18 and b_width <=32)):
                            self.submodules.dsp = dsp = RS_DSP_MULT20_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                elif (feature == "Pipeline"):
                    if (unsigned):
                        if ((a_width > 54 and a_width <=72) or (b_width > 54 and b_width <=72)):
                            self.submodules.dsp = dsp = RS_DSP_MULT54_pipeline(a_width, b_width, equation, unsigned)
                            reg_in = True
                        elif ((a_width > 36 and a_width <=54) or (b_width > 36 and b_width <=54)):
                            self.submodules.dsp = dsp = RS_DSP_MULT36_pipeline(a_width, b_width, equation, unsigned)
                            reg_in = True
                        elif ((a_width > 20 and a_width <=36) or (b_width > 18 and b_width <=36)):
                            self.submodules.dsp = dsp = RS_DSP_MULT20_pipeline(a_width, b_width, equation, unsigned)
                            reg_in = True
                    else:
                        if ((a_width > 51 and a_width <=72) or (b_width > 51 and b_width <=72)):
                            self.submodules.dsp = dsp = RS_DSP_MULT54_pipeline(a_width, b_width, equation, unsigned)
                            reg_in = True
                        elif ((a_width > 34 and a_width <=51) or (b_width > 34 and b_width <=51)):
                            self.submodules.dsp = dsp = RS_DSP_MULT36_pipeline(a_width, b_width, equation, unsigned)
                            reg_in = True
                        elif ((a_width > 20 and a_width <=34) or (b_width > 18 and b_width <=34)):
                            self.submodules.dsp = dsp = RS_DSP_MULT20_pipeline(a_width, b_width, equation, unsigned)
                            reg_in = True

        # (AxB)+(CxD)
        elif (equation=="AxB+CxD"):
            if ((a_width + b_width) > (c_width + d_width)):
                z_width = a_width + b_width + 1
            else:
                z_width = c_width + d_width + 1
            self.submodules.dsp = dsp = RS_DSP_MULT_ABCD(a_width, b_width, c_width, d_width, equation, reg_in, reg_out, unsigned)
            platform.add_extension(get_ios(a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, z_width))
            self.comb += dsp.c.eq(platform.request("c"))
            self.comb += dsp.d.eq(platform.request("d"))
        # AxB+CxD+ExF+GxH
        elif (equation=="AxB+CxD+ExF+GxH"):
            if ((a_width + b_width) > (c_width + d_width)):
                z12_width = a_width + b_width + 1
            else:
                z12_width = c_width + d_width + 1
            if ((e_width + f_width) > (g_width + h_width)):
                z34_width = e_width + f_width + 1
            else:
                z34_width = g_width + h_width + 1
            if (z12_width > z34_width):
                z_width = z12_width + 1
            else:
                z_width = z34_width + 1
            self.submodules.dsp = dsp = RS_DSP_MULT_ABCDEFGH(a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, equation, reg_in, reg_out, unsigned)
            platform.add_extension(get_ios(a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, z_width))
            self.comb += dsp.c.eq(platform.request("c"))
            self.comb += dsp.d.eq(platform.request("d"))
            self.comb += dsp.e.eq(platform.request("e"))
            self.comb += dsp.f.eq(platform.request("f"))
            self.comb += dsp.g.eq(platform.request("g"))
            self.comb += dsp.h.eq(platform.request("h"))
            
        self.comb += dsp.a.eq(platform.request("a"))
        self.comb += dsp.b.eq(platform.request("b"))
        # Clock/Reset
        if (reg_in == 1 or reg_out == 1):
            self.comb += self.cd_sys.clk.eq(platform.request("clk"))
            self.comb += self.cd_sys.rst.eq(platform.request("reset"))
        # Registered Output
        if (reg_out == 1 and feature == "Pipeline"):
            self.sync += platform.request("z").eq(dsp.z)
        else:
            self.comb += platform.request("z").eq(dsp.z)
        
def main():
    # DSP CORE -------------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description="DSP CORE")
    
    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder
    
    # Parameter Dependency dictionary
    dep_dict = {}
    
    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="dsp_generator", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))
    
    # Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--equation",     type=str,      default="AxB",      choices=["AxB","AxB+CxD","AxB+CxD+ExF+GxH"],    help="Select Equation")
    core_string_param_group.add_argument("--feature",      type=str,      default="Base",     choices=["Base", "Enhanced", "Pipeline"],       help="Select Feature")
    
    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--a_width",     type=int,       default=20,      choices=range(1, 73),     help="A_Input")
    core_range_param_group.add_argument("--b_width",     type=int,       default=18,      choices=range(1, 73),     help="B_Input")
    core_range_param_group.add_argument("--c_width",     type=int,       default=20,      choices=range(1, 21),     help="C_Input")
    core_range_param_group.add_argument("--d_width",     type=int,       default=18,      choices=range(1, 19),     help="D_Input")
    core_range_param_group.add_argument("--e_width",     type=int,       default=20,      choices=range(1, 21),     help="E_Input")
    core_range_param_group.add_argument("--f_width",     type=int,       default=18,      choices=range(1, 19),     help="F_Input")
    core_range_param_group.add_argument("--g_width",     type=int,       default=20,      choices=range(1, 21),     help="G_Input")
    core_range_param_group.add_argument("--h_width",     type=int,       default=18,      choices=range(1, 19),     help="H_Input")
    
    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--reg_in",      type=bool,    default=False,    help="Registered Inputs")
    core_bool_param_group.add_argument("--reg_out",     type=bool,    default=False,    help="Registered Outputs")
    core_bool_param_group.add_argument("--unsigned",    type=bool,    default=True,     help="Unsigned Input")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="dsp_generator",          help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'DSP Generator',
    'Version' : 'V1_0',
    'Interface' : 'Native',
    'Description' : 'DSP Generator IP is a versatile solution that tailors DSP IPs based on specified parameters. It offers pre-built functions, optimizing performance by allowing the configuration of different multiplicative algorithms suited for custom requirements.'}
    }
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")

        if (args.equation == "AxB"):
            dep_dict.update({
                'c_width'     :     'True',
                'd_width'     :     'True',
                'e_width'     :     'True',
                'f_width'     :     'True',
                'g_width'     :     'True',
                'h_width'     :     'True'
            })
            parser._actions[2].choices = ["Base", "Enhanced", "Pipeline"]
            if (args.feature == "Base") or (args.feature == "Pipeline" and args.unsigned == True):
                if(args.feature == "Pipeline"):
                    parser._actions[11].default = True
                    dep_dict.update({
                        'reg_in'     :     'True'
                    })
                parser._actions[3].choices = range(1, 73)
                parser._actions[4].choices = range(1, 73)
            elif (args.feature == "Pipeline" and args.unsigned == False) or (args.feature == "Enhanced" and args.unsigned == True):
                if(args.feature == "Pipeline"):
                    parser._actions[11].default = True
                    dep_dict.update({
                        'reg_in'     :     'True'
                    })
                if (args.a_width > 68):
                    parser._actions[3].default = 68
                if (args.b_width > 68):
                    parser._actions[4].default = 68
                parser._actions[3].choices = range(1, 69)
                parser._actions[4].choices = range(1, 69)
            elif (args.feature == "Enhanced" and args.unsigned == False):
                if (args.a_width > 64):
                    parser._actions[3].default = 64
                if (args.b_width > 64):
                    parser._actions[4].default = 64
                parser._actions[3].choices = range(1, 65)
                parser._actions[4].choices = range(1, 65)
        else:
            parser._actions[2].choices = ["Base"]
            parser._actions[3].choices = range(1, 21)
            parser._actions[4].choices = range(1, 19)
            if (args.equation == "AxB+CxD"):
                dep_dict.update({
                    'e_width'     :     'True',
                    'f_width'     :     'True',
                    'g_width'     :     'True',
                    'h_width'     :     'True'
                })
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
    
    summary =  { 
    "Multiplier" : args.equation
    }
    if(args.feature == "Base"):
        summary["Algorithm"] = "Karatsuba Algorithm"
        summary["Latency (clock cycles)"] = "1"
        if(args.equation == "AxB"):
            if ((args.a_width > 54 and args.a_width <=72) or (args.b_width > 54 and args.b_width <=72)):
                summary["Count of DSPs"] = "16"
            elif ((args.a_width > 36 and args.a_width <=54) or (args.b_width > 36 and args.b_width <=54)):
                summary["Count of DSPs"] = "9"
            elif ((args.a_width > 20 and args.a_width <=36) or (args.b_width > 18 and args.b_width <=36)):
                summary["Count of DSPs"] = "4"
            else:
                summary["Count of DSPs"] = "1"
        elif (args.equation == "AxB+CxD"):
            summary["Count of DSPs"] = "2"
        else:
            summary["Count of DSPs"] = "4"
    elif (args.feature == "Enhanced"):
        summary["Algorithm"] = "Karatsuba-Offman Algorithm"
        summary["Latency (clock cycles)"] = "1"
        if(args.unsigned):
            if ((args.a_width > 51 and args.a_width <=68) or (args.b_width > 51 and args.b_width <=68)):
                summary["Count of DSPs"] = "10"
            elif ((args.a_width > 34 and args.a_width <=51) or (args.b_width > 34 and args.b_width <=51)):
                summary["Count of DSPs"] = "6"
            elif ((args.a_width > 20 and args.a_width <=34) or (args.b_width > 18 and args.b_width <=34)):
                summary["Count of DSPs"] = "3"
            else:
                summary["Count of DSPs"] = "1"
        else:
            if ((args.a_width > 48 and args.a_width <=64) or (args.b_width > 48 and args.b_width <=64)):
                summary["Count of DSPs"] = "10"
            elif ((args.a_width > 32 and args.a_width <=48) or (args.b_width > 32 and args.b_width <=48)):
                summary["Count of DSPs"] = "6"
            elif ((args.a_width > 20 and args.a_width <=32) or (args.b_width > 18 and args.b_width <=32)):
                summary["Count of DSPs"] = "3"
            else:
                summary["Count of DSPs"] = "1"
    else:
        summary["Algorithm"] = "Pipelined Algorithm"
        if(args.unsigned):
            if ((args.a_width > 54 and args.a_width <=72) or (args.b_width > 54 and args.b_width <=72)):
                summary["Count of DSPs"] = "7"
                summary["Latency (clock cycles)"] = "4"
            elif ((args.a_width > 36 and args.a_width <=54) or (args.b_width > 36 and args.b_width <=54)):
                summary["Count of DSPs"] = "5"
                summary["Latency (clock cycles)"] = "3"
            elif ((args.a_width > 20 and args.a_width <=36) or (args.b_width > 18 and args.b_width <=36)):
                summary["Count of DSPs"] = "3"
                summary["Latency (clock cycles)"] = "2"
            else:
                summary["Count of DSPs"] = "1"
                summary["Latency (clock cycles)"] = "1"
        else:
            if ((args.a_width > 51 and args.a_width <=68) or (args.b_width > 51 and args.b_width <=68)):
                summary["Count of DSPs"] = "7"
                summary["Latency (clock cycles)"] = "4"
            elif ((args.a_width > 34 and args.a_width <=51) or (args.b_width > 34 and args.b_width <=51)):
                summary["Count of DSPs"] = "5"
                summary["Latency (clock cycles)"] = "3"
            elif ((args.a_width > 20 and args.a_width <=34) or (args.b_width > 18 and args.b_width <=34)):
                summary["Count of DSPs"] = "3"
                summary["Latency (clock cycles)"] = "2"
            else:
                summary["Count of DSPs"] = "1"
                summary["Latency (clock cycles)"] = "1"
    if (args.unsigned and not args.reg_in):
        summary["Input"] = "Unregistered and Unsigned"
    elif (args.unsigned and args.reg_in):
        summary["Input"] = "Registered and Unsigned"
    elif (not args.unsigned and args.reg_in):
        summary["Input"] = "Registered and Signed"
    else:
        summary["Input"] = "Unregistered and Signed"
    if (args.reg_out):
        summary["Output"] = "Registered Output"
    else:
        summary["Output"] = "Unregistered Output"

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Wrapper -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = RS_DSP_Wrapper(platform,
        a_width     = args.a_width,
        b_width     = args.b_width,
        c_width     = args.c_width, 
        d_width     = args.d_width,
        e_width     = args.e_width,
        f_width     = args.f_width,
        g_width     = args.g_width,
        h_width     = args.h_width,
        feature     = args.feature,
        reg_in      = args.reg_in,
        reg_out     = args.reg_out,
        unsigned    = args.unsigned,
        equation    = args.equation
    )
    
    # Build Project --------------------------------------------------------------------------------
    if args.build:
        rs_builder.prepare(
            build_dir  = args.build_dir,
            build_name = args.build_name,
            version    = "v1_0"
        )
        rs_builder.copy_files(gen_path=os.path.dirname(__file__))
        rs_builder.generate_tcl(version    = "v1_0")
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
            version = "v1_0"
        )

        # IP_ID Parameter
        now = datetime.datetime.now()
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "dsp_generator", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"DSPG\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(\n".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

        build_name = args.build_name.rsplit( ".", 1 )[ 0 ]
        file = os.path.join(args.build_dir, "rapidsilicon/ip/dsp_generator/v1_0", build_name, "sim/dsp_test.v")
        file = Path(file)
        text = file.read_text()
        text = text.replace("[71:0]a", "[%s:0]a" % (args.a_width-1))
        file.write_text(text)
        text = text.replace("dsp_wrapper", "%s" % build_name)
        file.write_text(text)
        text = text.replace("[6:0]b", "[%s:0]b" % (args.b_width-1))
        file.write_text(text)
        text = text.replace("[78:0]z", "[%s:0]z" % (args.a_width+args.b_width-1))
        file.write_text(text)
        if (args.equation == "AxB+CxD"):
            text = text.replace("a1;", "a1; reg[%s: 0]c;" % (args.c_width - 1))
            file.write_text(text)
            text = text.replace(" b1;", " b1; reg[%s: 0]d;" % (args.d_width - 1))
            file.write_text(text)
            text = text.replace("(.a(a),.b(b),.z(z2))", "(.a(a),.b(b),.z(z2), .c(c), .d(d))")
            file.write_text(text)
            text = text.replace("(.a(a),.b(b),.z(z1))", "(.a(a),.b(b),.z(z1), .c(c), .d(d))")
            file.write_text(text)
            text = text.replace("dsp(a, b, z);", "dsp(a, b, z, c, d);")
            file.write_text(text)
            text = text.replace("z = a*b;", "z = a*b+c*d;")
            file.write_text(text)
            text = text.replace("a <= $random;", "a <= $random; c <= $random; d <= $random;")
            file.write_text(text)
            text = text.replace("a <= {20{1'b1}};", "a <= {20{1'b1}}; c <= {%s{1'b1}};" % args.c_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b1}};", "a <= {20{1'b1}}; d <= {%s{1'b1}};" % args.d_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b0}};", "a <= {20{1'b0}}; c <= {%s{1'b0}};" % args.c_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b0}};", "a <= {20{1'b0}}; d <= {%s{1'b0}};" % args.d_width)
            file.write_text(text)
            if (args.unsigned):
                text = text.replace("]a;", "]a; input [%s:0]c;" % (args.c_width - 1))
                file.write_text(text)
                text = text.replace("]b;", "]b; input [%s:0]d;" % (args.d_width - 1))
                file.write_text(text)
            else:
                text = text.replace("]a;", "]a; input signed [%s:0]c;" % (args.c_width - 1))
                file.write_text(text)
                text = text.replace("]b;", "]b; input signed [%s:0]d;" % (args.d_width - 1))
                file.write_text(text)
            if ((args.a_width + args.b_width) > (args.c_width + args.d_width)):
                text = text.replace("[37:0]z", "[%s:0]z" % (args.a_width + args.b_width))
            else:
                text = text.replace("[37:0]z", "[%s:0]z" % (args.c_width + args.d_width))
            file.write_text(text)
        if (args.equation == "AxB+CxD+ExF+GxH"):
            text = text.replace("a1;", "a1; reg[%s: 0]c;" % (args.c_width - 1))
            file.write_text(text)
            text = text.replace("c;", "c; reg[%s: 0]e;" % (args.e_width - 1))
            file.write_text(text)
            text = text.replace("]e;", "]e; reg[%s: 0]f;" % (args.f_width - 1))
            file.write_text(text)
            text = text.replace(" b1;", " b1; reg[%s: 0]d;" % (args.d_width - 1))
            file.write_text(text)
            text = text.replace("d;", " d; reg[%s: 0]g;" % (args.g_width - 1))
            file.write_text(text)
            text = text.replace("g;", " g; reg[%s: 0]h;" % (args.h_width - 1))
            file.write_text(text)
            text = text.replace("(.a(a),.b(b),.z(z2))", "(.a(a),.b(b),.z(z2), .c(c), .d(d), .e(e), .f(f), .g(g), .h(h))")
            file.write_text(text)
            text = text.replace("(.a(a),.b(b),.z(z1))", "(.a(a),.b(b),.z(z1), .c(c), .d(d), .e(e), .f(f), .g(g), .h(h))")
            file.write_text(text)
            text = text.replace("dsp(a, b, z);", "dsp(a, b, z, c, d, e, f, g, h);")
            file.write_text(text)
            text = text.replace("z = a*b;", "z = a*b+c*d+e*f+g*h;")
            file.write_text(text)
            text = text.replace("a <= $random;", "a <= $random; c <= $random; d <= $random; e <= $random; f <= $random; h <= $random; g <= $random;")
            file.write_text(text)
            text = text.replace("a <= {20{1'b1}};", "a <= {20{1'b1}}; c <= {%s{1'b1}};" % args.c_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b1}};", "a <= {20{1'b1}}; d <= {%s{1'b1}};" % args.d_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b1}};", "a <= {20{1'b1}}; e <= {%s{1'b1}};" % args.e_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b1}};", "a <= {20{1'b1}}; f <= {%s{1'b1}};" % args.f_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b1}};", "a <= {20{1'b1}}; g <= {%s{1'b1}};" % args.g_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b1}};", "a <= {20{1'b1}}; h <= {%s{1'b1}};" % args.h_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b0}};", "a <= {20{1'b0}}; c <= {%s{1'b0}};" % args.c_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b0}};", "a <= {20{1'b0}}; d <= {%s{1'b0}};" % args.d_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b0}};", "a <= {20{1'b0}}; e <= {%s{1'b0}};" % args.e_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b0}};", "a <= {20{1'b0}}; f <= {%s{1'b0}};" % args.f_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b0}};", "a <= {20{1'b0}}; g <= {%s{1'b0}};" % args.g_width)
            file.write_text(text)
            text = text.replace("a <= {20{1'b0}};", "a <= {20{1'b0}}; h <= {%s{1'b0}};" % args.h_width)
            file.write_text(text)
            if ((args.a_width + args.b_width) > (args.c_width + args.d_width)):
                z12_width = args.a_width + args.b_width + 1
            else:
                z12_width = args.c_width + args.d_width + 1
            if ((args.e_width + args.f_width) > (args.g_width + args.h_width)):
                z34_width = args.e_width + args.f_width + 1
            else:
                z34_width = args.g_width + args.h_width + 1
            if (z12_width > z34_width):
                text = text.replace("[37:0]z", "[%s:0]z" % (z12_width))
            else:
                text = text.replace("[37:0]z", "[%s:0]z" % (z34_width))
            file.write_text(text)
            if (args.unsigned):
                text = text.replace("]a;", "]a; input [%s:0]c;" % (args.c_width - 1))
                file.write_text(text)
                text = text.replace("]a;", "]a; input [%s:0]g;" % (args.g_width - 1))
                file.write_text(text)
                text = text.replace("]a;", "]a; input [%s:0]h;" % (args.h_width - 1))
                file.write_text(text)
                text = text.replace("]b;", "]b; input [%s:0]d;" % (args.d_width - 1))
                file.write_text(text)
                text = text.replace("]b;", "]b; input [%s:0]e;" % (args.e_width - 1))
                file.write_text(text)
                text = text.replace("]b;", "]b; input [%s:0]f;" % (args.f_width - 1))
                file.write_text(text)
            else:
                text = text.replace("]a;", "]a; input signed [%s:0]c;" % (args.c_width - 1))
                file.write_text(text)
                text = text.replace("]a;", "]a; input signed [%s:0]g;" % (args.g_width - 1))
                file.write_text(text)
                text = text.replace("]a;", "]a; input signed [%s:0]h;" % (args.h_width - 1))
                file.write_text(text)
                text = text.replace("]b;", "]b; input signed [%s:0]d;" % (args.d_width - 1))
                file.write_text(text)
                text = text.replace("]b;", "]b; input signed [%s:0]e;" % (args.e_width - 1))
                file.write_text(text)
                text = text.replace("]b;", "]b; input signed [%s:0]f;" % (args.f_width - 1))
                file.write_text(text)
        text = text.replace("a <= {20", "a <= {%s" % args.a_width)
        file.write_text(text)
        text = text.replace("b <= {20", "b <= {%s" % args.b_width)
        file.write_text(text)
        if (not args.unsigned):
            text = text.replace("input  ", "input signed")
            file.write_text(text)
        if (args.feature == "Pipeline"):
            text = text.replace(".z(z1))", ".z(z1), .clk(clk1), .reset(reset))")
            file.write_text(text)
            text = text.replace("(.a(a),.b(b),.z(z2))", "(.a(a1),.b(b1),.z(z2))")
            file.write_text(text)
            if (args.unsigned):
                if ((args.a_width > 54 and args.a_width <=72) or (args.b_width > 54 and args.b_width <=72)):
                    text = text.replace("repeat (1)", "repeat (4)")
                    if (args.reg_out):
                        text = text.replace("repeat (4)", "repeat (5)")
                elif ((args.a_width > 36 and args.a_width <=54) or (args.b_width > 36 and args.b_width <=54)):
                    text = text.replace("repeat (1)", "repeat (3)")
                    if (args.reg_out):
                        text = text.replace("repeat (3)", "repeat (4)")
                elif ((args.a_width > 20 and args.a_width <=36) or (args.b_width > 18 and args.b_width <=36)):
                    text = text.replace("repeat (1)", "repeat (2)")
                    if (args.reg_out):
                        text = text.replace("repeat (2)", "repeat (3)")
            else: 
                if ((args.a_width > 51 and args.a_width <=68) or (args.b_width > 51 and args.b_width <=68)):
                    text = text.replace("repeat (1)", "repeat (4)")
                    if (args.reg_out):
                        text = text.replace("repeat (4)", "repeat (5)")
                elif ((args.a_width > 34 and args.a_width <=51) or (args.b_width > 34 and args.b_width <=51)):
                    text = text.replace("repeat (1)", "repeat (3)")
                    if (args.reg_out):
                        text = text.replace("repeat (3)", "repeat (4)")
                elif ((args.a_width > 20 and args.a_width <=34) or (args.b_width > 18 and args.b_width <=34)):
                    text = text.replace("repeat (1)", "repeat (2)")
                    if (args.reg_out):
                        text = text.replace("repeat (2)", "repeat (3)")
            file.write_text(text)
        else:
            if (args.reg_in and args.reg_out):
                text = text.replace("repeat (1) @ (posedge clk1);", "repeat (3) @ (posedge clk1);")
                file.write_text(text)
            if (args.reg_in or args.reg_out):
                text = text.replace(".z(z1)", ".z(z1), .clk(clk1), .reset(reset)")
                file.write_text(text)
                text = text.replace("repeat (1) @ (posedge clk1);", "repeat (2) @ (posedge clk1);")
                file.write_text(text)

if __name__ == "__main__":
    main()
