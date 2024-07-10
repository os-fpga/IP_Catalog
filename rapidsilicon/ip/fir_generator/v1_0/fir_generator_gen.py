#!/usr/bin/env python3
#
# This file is Copyright (c) 2023 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
import math

from litex_wrapper.fir_litex_generator import *

from migen import *

from litex.build.generic_platform import *

from litex.build.osfpga import OSFPGAPlatform

# Checking if the file provided is in valid format

def is_valid_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    valid_extensions = ['.txt', '.hex']
    return file_extension.lower() in valid_extensions

# IOs/Interfaces -----------------------------------------------------------------------------------

def get_clkin_ios(data_in, data_out):
    return [
        ("clk",         0,  Pins(1)),
        ("fast_clk",    0,  Pins(1)),
        ("rst",         0,  Pins(1)),
		("data_in",     0,  Pins(data_in)),
        ("data_out",    0,  Pins(data_out)),
        ("ready",       0,  Pins(1))
    ]

# Check if any number in the list is a float with a non-zero fractional part
def has_fractional_number(numbers):
    return any(isinstance(number, float) and not number.is_integer() for number in numbers)

# FIR Generator ----------------------------------------------------------------------------------
class FIRGenerator(Module):
    def __init__(self, platform, input_width, coefficients, coefficients_file, coefficient_fractional_bits, signed, optimization, number_of_coefficients, coefficient_width, input_fractional_bits, truncated_output, output_data_width):
        # Clocking ---------------------------------------------------------------------------------
        if (optimization == "Area" and coefficients_file):
            non_zero_elements = [element for element in extract_numbers(coefficients, coefficients_file) if element != 0]
            coefficient_width = 20
            bit_growth = int(coefficient_width + math.ceil(math.log2(len(non_zero_elements))) if len(non_zero_elements) > 0 else 0)
        elif (coefficients == "" or len(extract_numbers(coefficients, coefficients_file)) <= 0):
            bit_growth = 0
        else:
            abs_sum = sum(abs(coeff) for coeff in extract_numbers(coefficients, coefficients_file))
            bit_growth = math.ceil(math.log2(abs_sum))

        platform.add_extension(get_clkin_ios(input_width, min(input_width + bit_growth, 38) if not truncated_output else output_data_width))
        
        if(optimization == "Area"):
            self.clock_domains.cd_sys  = ClockDomain(reset_less=True)
            self.clock_domains.cd_accelerated	= ClockDomain(reset_less=True)
        else:
            self.clock_domains.cd_sys  = ClockDomain()
	
        self.submodules.fir = fir = FIR(input_width, coefficients, coefficients_file, coefficient_fractional_bits, signed, optimization, number_of_coefficients, coefficient_width, input_fractional_bits, truncated_output, output_data_width)
    
        self.comb += fir.data_in.eq(platform.request("data_in"))
        if (optimization == "Area"):
            self.sync += platform.request("data_out").eq(fir.data_out)
            self.sync += fir.rst.eq(platform.request("rst"))  
            self.comb += platform.request("ready").eq(~fir.rst)
            self.comb += self.cd_accelerated.clk.eq(platform.request("fast_clk"))
        else:
            self.comb += platform.request("ready").eq(fir.ready)
            self.comb += platform.request("data_out").eq(fir.data_out)
            self.comb += self.cd_sys.rst.eq(platform.request("rst"))   
        self.comb += self.cd_sys.clk.eq(platform.request("clk"))
        
         
            
# Build --------------------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="FIR")

    # Import Common Modules.
    common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib")
    sys.path.append(common_path)

    from common import IP_Builder

    # Parameter Dependency dictionary
    #                Ports     :    Dependency
    dep_dict = {}            

    # IP Builder.
    rs_builder = IP_Builder(device="gemini", ip_name="fir_generator", language="verilog")

    logging.info("===================================================")
    logging.info("IP    : %s", rs_builder.ip_name.upper())
    logging.info(("==================================================="))

    # Core string parameters.
    core_string_param_group = parser.add_argument_group(title="Core string parameters")
    core_string_param_group.add_argument("--optimization",     type=str,      default="Area",      choices=["Performance","Area"],    help="Choose what optimization is required")
    
    # Core range value parameters.
    core_range_param_group = parser.add_argument_group(title="Core range parameters")
    core_range_param_group.add_argument("--input_width",      type=int,   default=18,  	choices=range(1,19),   help="Input Data Width of the FIR")
    core_range_param_group.add_argument("--input_fractional_bits",  type=int,   default=2,  	choices=range(0,19),   help="Fractional Bit Width of the Input")
    core_range_param_group.add_argument("--number_of_coefficients",  type=int,   default=4,  	choices=range(1,121),   help="Number of Coefficients for the Filter")
    core_range_param_group.add_argument("--coefficient_width",  type=int,   default=2,  	choices=range(1,21),   help="Bit width for the coefficients")
    core_range_param_group.add_argument("--coefficient_fractional_bits",  type=int,   default=0,  	choices=range(0,21),   help="Fractional Bit Width of the coefficients")
    core_range_param_group.add_argument("--output_data_width",  type=int,   default=2,  	choices=range(1,39),   help="Output Data Bit Width")

    # Core file path parameters.
    core_file_path_group = parser.add_argument_group(title="Core file path parameters")
    core_file_path_group.add_argument("--coefficients",    type=str,   default="", help="Space or comma-separated coefficients in base 10 or hex with 0x prefix for FIR Filter")
    core_file_path_group.add_argument("--file_path",    type=str,   default="",   help="Absolute path for .hex/.txt file for Coefficients of the FIR Filter")

    # Core bool value parameters.
    core_bool_param_group = parser.add_argument_group(title="Core bool parameters")
    core_bool_param_group.add_argument("--coefficients_file",        type=bool,   default=False,     help="Enter Coefficients manually or select a text file containing them")
    core_bool_param_group.add_argument("--truncated_output",        type=bool,   default=False,     help="Truncated Output Data Width")
    core_bool_param_group.add_argument("--signed",        type=bool,   default=False,     help="Signed or Unsigned Input")
    

    # Build Parameters.
    build_group = parser.add_argument_group(title="Build parameters")
    build_group.add_argument("--build",         action="store_true",    help="Build Core")
    build_group.add_argument("--build-dir",     default="./",           help="Build Directory")
    build_group.add_argument("--build-name",    default="FIR_generator", help="Build Folder Name, Build RTL File Name and Module Name")

    # JSON Import/Template
    json_group = parser.add_argument_group(title="JSON Parameters")
    json_group.add_argument("--json",                                   help="Generate Core from JSON File")
    json_group.add_argument("--json-template",  action="store_true",    help="Generate JSON Template")

    args = parser.parse_args()

    details =  {   "IP details": {
    'Name' : 'FIR Generator',
    'Version' : 'V1_0',
    'Interface' : 'Native',
    'Description' : 'FIR Generator lets designers to efficiently design digital filters with customizable taps. Ideal for signal processing in FPGA applications.'}
    }

    # Import JSON (Optional) -----------------------------------------------------------------------
    if args.json:
        args = rs_builder.import_args_from_json(parser=parser, json_filename=args.json)
        rs_builder.import_ip_details_json(build_dir=args.build_dir ,details=details , build_name = args.build_name, version = "v1_0")
        file_path = os.path.dirname(os.path.realpath(__file__))
        rs_builder.copy_images(file_path)
        
        if (args.optimization == "Area"):
            if (not args.coefficients_file):
                option_strings_to_remove = ['--number_of_coefficients']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
            else:
                if (args.number_of_coefficients == 1):
                    parser._actions[4].default = 2
                parser._actions[4].choices = range(2, 121)
                option_strings_to_remove = ['--coefficient_width']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        else:
            if (not args.coefficients_file):
                option_strings_to_remove = ['--number_of_coefficients']
                parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
                parser._actions[4].choices = range(1, 20 - args.input_width + 1)
                parser._actions[5].choices = range(0, 20 - args.input_width + 1)
            else:
                parser._actions[5].choices = range(1, 20 - args.input_width + 1)
                parser._actions[6].choices = range(0, 20 - args.input_width + 1)
        if (args.coefficients_file == False):
            option_strings_to_remove = ['--file_path']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        else:
            option_strings_to_remove = ['--coefficients']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        if (not has_fractional_number(extract_numbers(args.coefficients, args.coefficients_file))):
            dep_dict.update({
                'coefficient_fractional_bits' : 'True'
            })
        if (args.optimization == "Area" and args.coefficients_file):
            option_strings_to_remove = ['--coefficient_fractional_bits']
            parser._actions = [action for action in parser._actions if action.option_strings and action.option_strings[0] not in option_strings_to_remove]
        if (not args.truncated_output):
            dep_dict.update({
                'output_data_width' : 'True'
            })
    if (not args.coefficients_file):
        coefficients = args.coefficients
    else:
        coefficients = args.file_path

    if (args.optimization == "Area" and args.coefficients_file):
        non_zero_elements = [element for element in extract_numbers(coefficients, args.coefficients_file) if element != 0]
        bit_growth = int(args.coefficient_width + math.ceil(math.log2(len(non_zero_elements))) if len(non_zero_elements) > 0 else 0)
    elif (args.coefficients == ""):
        bit_growth = 0
    else:
        abs_sum = sum(abs(coeff) for coeff in extract_numbers(coefficients, args.coefficients_file))
        bit_growth = math.ceil(math.log2(abs_sum))

        #device_dict contains the number of BRAMs and DSP for the device used.
        device_dic = rs_builder.parse_device(args.device_path,args.device)

    summary = {}
    if (args.coefficients_file):
        if (args.optimization == "Area"):
            input_minimum = round(max(800/args.number_of_coefficients, 8), 2)
            input_maximum = round(min(3200/args.number_of_coefficients, 500), 2)
            summary ["Reloadable Coefficient Filter"] = "The coefficients file can be modified after IP generation, but the count of coefficients must remain constant."
            summary ["Coefficient Bit Width"] = "20"
            summary ["Input Frequency"] = f"{input_minimum} MHz - {input_maximum} MHz"
            summary ["Input File"] = "Only .hex file format is supported without any prefix for numbers."
            summary ["Fast Clock Frequency"] = f"Fast clock must be {args.number_of_coefficients}x of the input master clock."
            if (not args.truncated_output):
                summary ["Output Width"] = f"{min(args.input_width + bit_growth, 38)} with worst case bit growth."
            summary ["Number of DSPs"] = "1"
        else:
            summary ["Fixed Coefficient Filter"] = "The coefficients cannot be changed after IP generation."
            if (not args.truncated_output):
                summary ["Output Width"] = f"{min(args.input_width + bit_growth, 38)} with true maximum bit growth."
            summary ["Number of DSPs"] = len(extract_numbers(coefficients, args.coefficients_file))
            summary ["Input File"] = ".txt or .hex file formats are supported with the hex numbers starting with 0x while decimal numbers require no prefix."
        if (args.file_path == ""):
            summary ["Coefficients"] = "None"
            summary ["File"] = "No file provided"
        elif (is_valid_extension(coefficients) and len(extract_numbers(coefficients, args.coefficients_file)) > 0):
            summary ["Coefficients"] = ', '.join(map(str, extract_numbers(coefficients, args.coefficients_file)))
            summary ["Filter Taps"] = len(extract_numbers(coefficients, args.coefficients_file))
        else:
            summary ["Coefficients"] = "None"
            summary["File Not Valid"] = "Only .txt and .hex file formats are supported with numbers having the correct prefix as specified."
    else:
        summary ["Fixed Coefficient Filter"] = "The coefficients cannot be changed after IP generation."
        if (not args.truncated_output):
            summary ["Output Width"] = f"{min(args.input_width + bit_growth, 38)} with true maximum bit growth."
        summary ["Filter Taps"] = len(extract_numbers(coefficients, args.coefficients_file))
        if (args.optimization == "Area"):
            input_minimum = round(max(800/len(extract_numbers(coefficients, args.coefficients_file)) if len(extract_numbers(coefficients, args.coefficients_file)) > 0 else 1, 8), 2)
            input_maximum = round(min(3200/len(extract_numbers(coefficients, args.coefficients_file)) if len(extract_numbers(coefficients, args.coefficients_file)) > 0 else 500, 500), 2)
            summary ["Input Frequency"] = f"{input_minimum} MHz - {input_maximum} MHz"
            summary ["Optimization"] = "Area"
            summary ["Number of DSPs"] = "1"
            summary ["Fast Clock Frequency"] = f"Fast clock must be {len(extract_numbers(coefficients, args.coefficients_file))}x of the input master clock."
        else:
            summary ["Optimization"] = "Performance"
            summary ["Number of DSPs"] = len(extract_numbers(coefficients, args.coefficients_file))
    if (args.truncated_output):
        summary ["Output Fractional Bits"] = f"{args.input_fractional_bits + args.coefficient_fractional_bits - max(0, (args.input_width + bit_growth) - args.output_data_width) if args.input_fractional_bits + args.coefficient_fractional_bits - max(0, (args.input_width + bit_growth) - args.output_data_width) > 0 else 0}"
        summary ["Output Rounding"] = "Truncation Applied."
    else:
        summary ["Output Fractional Bits"] = f"{args.input_fractional_bits + args.coefficient_fractional_bits}"
        summary ["Output Rounding"] = "Full Precision with Saturation Applied when accumulated output becomes greater than 38 bits."

    # Export JSON Template (Optional) --------------------------------------------------------------
    if args.json_template:
        rs_builder.export_json_template(parser=parser, dep_dict=dep_dict, summary=summary)

    # Create Generator -------------------------------------------------------------------------------
    platform = OSFPGAPlatform(io=[], toolchain="raptor", device="gemini")
    module   = FIRGenerator(platform,
            input_width                   = args.input_width,
            coefficients                  = coefficients,
            coefficients_file             = args.coefficients_file,
            coefficient_fractional_bits   = args.coefficient_fractional_bits,
            signed                        = args.signed,
            optimization                  = args.optimization,
            number_of_coefficients        = args.number_of_coefficients,
            coefficient_width             = args.coefficient_width,
            input_fractional_bits         = args.input_fractional_bits,
            truncated_output              = args.truncated_output,
            output_data_width             = args.output_data_width
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
            version    = "v1_0"
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
        
        wrapper = os.path.join(args.build_dir, "rapidsilicon", "ip", "fir_generator", "v1_0", args.build_name, "src",args.build_name + "_" + "v1_0" + ".v")
        new_lines = []
        with open (wrapper, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if ("module {}".format(args.build_name)) in line:
                    new_lines.append("module {} #(\n\tparameter IP_TYPE \t\t= \"FIRG\",\n\tparameter IP_VERSION \t= {}, \n\tparameter IP_ID \t\t= {}\n)\n(\n".format(args.build_name, ip_version, ip_id))
                else:
                    new_lines.append(line)
                
        with open(os.path.join(wrapper), "w") as file:
            file.writelines(new_lines)

        if (args.optimization == "Area"):
            with open(wrapper, 'r') as file:
                lines = file.readlines()

            # Find the line number containing "endmodule"
            endmodule_line_number = None
            for i, line in enumerate(lines):
                if "endmodule" in line:
                    endmodule_line_number = i
            if (args.coefficients_file):
                read_mem = """
initial begin
    $readmemh("{}", coefficients);
end
""".format(args.file_path)

                lines.insert(endmodule_line_number, f"{read_mem}\n")
                # Write the modified content back to the file
                with open(wrapper, 'w') as file:
                    file.writelines(lines)

        build_name = args.build_name.rsplit( ".", 1 )[ 0 ]
        file = os.path.join(args.build_dir, "rapidsilicon/ip/fir_generator/v1_0", build_name, "sim/testbench.v")
        file = Path(file)
        text = file.read_text()
        text = text.replace("FIR_generator", "%s" % build_name)
        file.write_text(text)
        text = text.replace("[17:0] din", "[%s:0] din" % str(args.input_width - 1))
        file.write_text(text)
        if (not args.coefficients_file):
            text = text.replace("i <= 4", "i <= %s" % len(extract_numbers(args.coefficients, args.coefficients_file)))
            file.write_text(text)
        else:
            text = text.replace("i <= 4", "i <= %s" % args.number_of_coefficients)
            file.write_text(text)
        if (args.truncated_output):
            text = text.replace("[37:0] dout", "[%s:0] dout" % args.output_data_width)
        else:
            text = text.replace("[37:0] dout", "[%s:0] dout" % str(min(args.input_width + bit_growth, 38) - 1))
        file.write_text(text)
        if (args.optimization == "Area"):
            text = text.replace("#5 clk", "#%s clk" % str(((1/input_maximum)/2) * 1000))
            file.write_text(text)
            text = text.replace(".data_out(dout)", ".data_out(dout), \n\t.fast_clk(accelerated_clk)")
            file.write_text(text)
            if (not args.coefficients_file):
                text = text.replace("#5 accelerated_clk", "#%s accelerated_clk" % str(round(((1/input_maximum)/2) * 1000 / max(len(extract_numbers(args.coefficients, args.coefficients_file)), 1), 3)))
                file.write_text(text)
            else:
                text = text.replace("#5 accelerated_clk", "#%s accelerated_clk" % str(round(((1/input_maximum)/2) * 1000 / max(args.number_of_coefficients, 1), 3)))
                file.write_text(text)
        text = text.replace("18", "%s" % args.input_width)
        file.write_text(text)
        text = text.replace("4", "%s" % len(extract_numbers(args.coefficients, args.coefficients_file)))
        file.write_text(text)

        file = os.path.join(args.build_dir, "rapidsilicon/ip/fir_generator/v1_0", build_name, "sim/fir_golden.v")
        file = Path(file)
        text = file.read_text()
        if (args.truncated_output):
            text = text.replace("[37:0]", "[%s:0]" % args.output_data_width)
        else:
            text = text.replace("[37:0]", "[%s:0]" % str(min(args.input_width + bit_growth, 38) - 1))
        file.write_text(text)
        if (not args.coefficients_file):
            replacement = " + ".join(f"product[{i}]" for i in range(len(extract_numbers(args.coefficients, args.coefficients_file))))
            text = text.replace("product[0];", f"{replacement};")
            file.write_text(text)
        else:
            replacement = " + ".join(f"product[{i}]" for i in range(args.number_of_coefficients))
            text = text.replace("product[0];", f"{replacement};")
            file.write_text(text)
        if (args.optimization == "Area"):
            text = text.replace("<= data_in_buff", "<= filter_in")
            file.write_text(text)
        with open(file, 'r') as files:
            lines = files.readlines()
        for i, value in enumerate(extract_numbers(args.coefficients, args.coefficients_file)):
            insert_line = f"\tassign coeff[{i}] = {decimal_to_fixed_point(value, args.coefficient_width - args.coefficient_fractional_bits, args.coefficient_fractional_bits, args.signed)};\n"
            lines.insert(21 - 1 + i, insert_line)

        with open(file, 'w') as files:
            files.writelines(lines)

        if (not args.signed):
            with open(file, 'r') as files:
                content = files.read()
            modified_content = content.replace('signed', '')
            with open(file, 'w') as files:
                files.write(modified_content)

if __name__ == "__main__":
    main()
    
