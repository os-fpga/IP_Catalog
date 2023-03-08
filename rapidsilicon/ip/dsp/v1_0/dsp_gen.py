#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import argparse

from migen import *

from litex.gen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

from litex_wrapper.dsp_litex_wrapper import *

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
        
            # A*B
        if (equation == "A*B"):
            z_width = a_width + b_width
            platform.add_extension(get_ios(a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, z_width))
            if ((a_width >= 0 and a_width <=20) and (b_width >= 0 and b_width <=18)):
                self.submodules.dsp = dsp = RS_DSP_MULT(a_width, b_width, equation, reg_in, reg_out, unsigned)
            else:
                if ((a_width > 54 and a_width <=72) or (b_width > 54 and b_width <=72)):
                    if(feature == "base"):
                        self.submodules.dsp = dsp = RS_DSP_MULT54(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif (feature == "enhanced"):
                        self.submodules.dsp = dsp = RS_DSP_MULT54_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif (feature == "pipeline"):
                        self.submodules.dsp = dsp = RS_DSP_MULT54_pipeline(a_width, b_width, reg_in, reg_out, equation, unsigned)
                        reg_in = True

                elif ((a_width > 36 and a_width <=54) or (b_width > 36 and b_width <=54)):
                    if (feature == "base"):
                        self.submodules.dsp = dsp = RS_DSP_MULT36(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif (feature == "enhanced"):
                        self.submodules.dsp = dsp = RS_DSP_MULT36_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif (feature == "pipeline"):
                        self.submodules.dsp = dsp = RS_DSP_MULT36_pipeline(a_width, b_width, equation, reg_in, reg_out, unsigned)
                        reg_in = True

                elif ((a_width > 20 and a_width <=36) or (b_width > 18 and b_width <=36)):
                    if (feature == "base"):
                        self.submodules.dsp = dsp = RS_DSP_MULT20(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif (feature == "enhanced"):
                        self.submodules.dsp = dsp = RS_DSP_MULT20_enhance(a_width, b_width, equation, reg_in, reg_out, unsigned)
                    elif (feature == "pipeline"):
                        self.submodules.dsp = dsp = RS_DSP_MULT20_pipeline(a_width, b_width, equation, reg_in, reg_out, unsigned)
                        reg_in = True
                        
                self.comb += dsp.a.eq(platform.request("a"))
                self.comb += dsp.b.eq(platform.request("b"))
                # Clock/Reset
                if (reg_in == 1 or reg_out == 1):
                    self.comb += self.cd_sys.clk.eq(platform.request("clk"))
                    self.comb += self.cd_sys.rst.eq(platform.request("reset"))
                # Registered Output
                if (reg_out == 1):
                    self.sync += platform.request("z").eq(dsp.z)
                else:
                    self.comb += platform.request("z").eq(dsp.z)

        # (A*B)+(C*D)
        elif (equation=="A*B+C*D"):
            if ((a_width + b_width) > (c_width + d_width)):
                z_width = a_width + b_width + 1
            else:
                z_width = c_width + d_width + 1
            self.submodules.dsp = dsp = RS_DSP_MULT_ABCD(a_width, b_width, c_width, d_width, equation, reg_in, reg_out, unsigned)
            platform.add_extension(get_ios(a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, z_width))
            self.comb += dsp.a.eq(platform.request("a"))
            self.comb += dsp.b.eq(platform.request("b"))
            self.comb += dsp.c.eq(platform.request("c"))
            self.comb += dsp.d.eq(platform.request("d"))
            # Registered Output
            if (reg_out == 1):
                self.sync += platform.request("z").eq(dsp.z)
            else:
                self.comb += platform.request("z").eq(dsp.z)
        # A*B+C*D+E*F+G*H
        elif (equation=="A*B+C*D+E*F+G*H"):
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
            self.comb += dsp.a.eq(platform.request("a"))
            self.comb += dsp.b.eq(platform.request("b"))
            self.comb += dsp.c.eq(platform.request("c"))
            self.comb += dsp.d.eq(platform.request("d"))
            self.comb += dsp.e.eq(platform.request("e"))
            self.comb += dsp.f.eq(platform.request("f"))
            self.comb += dsp.g.eq(platform.request("g"))
            self.comb += dsp.h.eq(platform.request("h"))
            # Registered Output
            if (reg_out == 1):
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
    rs_builder = IP_Builder(device="gemini", ip_name="dsp", language="verilog")
    
    # Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--equation",     type=str,      default="A*B",      choices=["A*B","A*B+C*D","A*B+C*D+E*F+G*H"],    help="Select Equation")
    core_string_param_group.add_argument("--feature",  type=str,   default="base", choices=["base", "enhanced", "pipeline"],    help="Select Feature")
    
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
    core_bool_param_group.add_argument("--unsigned",  type=bool,    default=True,     help="Unsigned Input")
    
    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",            help="Build Core")
    build_group.add_argument("--build-dir",     default="./",                   help="Build Directory")
    build_group.add_argument("--build-name",    default="dsp_wrapper",          help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                    help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",     help="Generate JSON Template")

    args = parser.parse_args()
    
    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict)

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
        rs_builder.generate_tcl()
        rs_builder.generate_wrapper(
            platform   = platform,
            module     = module,
        )

if __name__ == "__main__":
    main()
