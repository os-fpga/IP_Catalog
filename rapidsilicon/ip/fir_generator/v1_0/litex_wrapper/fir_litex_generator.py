#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2023 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#

import datetime
import logging
import math
from migen import *
import re

# Extracting Numbers from the string obtained from the generator
def extract_numbers(input_string, coefficients_file):
    if (not coefficients_file):
        # Use a regular expression to find all numbers (positive or negative)
        # that are separated by commas or whitespaces
        pattern = r'[-+]?(?:0[xX][\dA-Fa-f]+|\d*\.?\d+)'
        numbers = re.findall(pattern, input_string)

        # Convert the found strings to numbers (float, int, or hex)
        converted_numbers = []
        for num in numbers:
            if '.' in num:
                converted_numbers.append(float(num))
            elif 'x' in num.lower():
                converted_numbers.append(int(num, 16))
            else:
                converted_numbers.append(int(num))
        return converted_numbers
    else:
        try:
            with open(input_string, 'r') as file:
                content = file.read()
                # Use regular expression to find all numbers (positive or negative)
                numbers = [int(num, 16) if 'x' in num.lower() else float(num) if '.' in num else int(num) for num in re.findall(r'[-+]?(?:0[xX][\dA-Fa-f]+|\d*\.?\d+)', content)]
                return numbers
        except FileNotFoundError:
            return []
    

# Converting fractional or signed number into fixed binary and then back to decimal
def decimal_to_fixed_point(decimal_number, integer=4, fraction=4, signed=False):
    integer_part = bin(int(abs(decimal_number)))[2:]
    binary_integer = integer_part.zfill(integer)
    fractional_part = bin(int((abs(decimal_number) - int(abs(decimal_number))) * 2**fraction))[2:]
    binary_fraction = fractional_part.zfill(fraction)
    if (fraction != 0):
        binary_result = str(binary_integer) + str(binary_fraction)
    else:
        binary_result = str(binary_integer)
    if (decimal_number < 0):
        inverted_bits = ''.join('1' if bit == '0' else '0' for bit in binary_result)
        binary_result = bin(int(inverted_bits, 2) + 1)[2:]

    if (len(binary_result) < 20 and signed):
        sign_bit = binary_result[0]
        sign_extension = sign_bit * (20 - len(binary_result))
        binary_result = sign_extension + binary_result
    return int(binary_result, 2)

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# FIR Generator ---------------------------------------------------------------------------------------
class FIR(Module):
    def __init__(self, input_width, coefficients, coefficients_file, fractional_bits, signed, optimization, number_of_coefficients, coefficient_width, input_fractional_bits, truncated_output, output_data_width):

        if (coefficients != ""):
            coefficients = extract_numbers(coefficients, coefficients_file)
            coefficients.reverse()
        
        if (optimization == "Area" and coefficients_file):
            non_zero_elements = [element for element in coefficients if element != 0]
            bit_growth = int(coefficient_width + math.ceil(math.log2(len(non_zero_elements))) if len(non_zero_elements) > 0 else 0)
        elif (coefficients == "" or len(coefficients) <= 0):
            bit_growth = 0
        else:
            abs_sum = sum(abs(coeff) for coeff in coefficients)
            bit_growth = math.ceil(math.log2(abs_sum))

        self.logger = logging.getLogger("FIR")
        self.logger.propagate = True
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Data Width
        self.logger.info(f"DATA_WIDTH_IN       : {input_width}")
        self.logger.info(f"DATA_WIDTH_OUT       : {min(input_width + bit_growth, 38) if not truncated_output else output_data_width}")
        self.logger.info(f"COEFFICIENTS       : {coefficients}")

        self.logger.info(f"===================================================")

        self.data_in = Signal(bits_sign=(input_width, True if signed else False))
        self.data_out = Signal(bits_sign=(min(input_width + bit_growth, 38) if not truncated_output else output_data_width, True if signed else False))

        if (optimization == "Performance"):
            self.ready = Signal()
            self.comb += self.ready.eq(~ResetSignal())
            self.z = Array(Signal() for _ in range (len(coefficients)))
            self.delay_b = Array(Signal() for _ in range (len(coefficients)))

            for i in range (len(coefficients)):
                self.delay_b[i] = Signal(bits_sign=(input_width, True if signed else False), name=f"delay_b_{i}")
                self.z[i] = Signal(bits_sign=(38, True if signed else False), name=f"z_{i}")

            if (not truncated_output and len(coefficients) > 0):
                self.comb += self.data_out.eq(self.z[len(coefficients) - 1][0 : min(input_width + bit_growth, 38)])
            elif (len(coefficients) > 0):
                self.comb += self.data_out.eq(self.z[len(coefficients) - 1][min(input_width + bit_growth, 38) - output_data_width: min(input_width + bit_growth, 38)])

            for i in range(len(coefficients)):
                coefficients[i] = decimal_to_fixed_point(coefficients[i], coefficient_width - fractional_bits, fractional_bits, signed)     # Using Notation of QN.M
                if (i == 0):
                    self.specials += Instance("DSP38",

                        # Parameters.
                        # -----------
                        # Mode Bits to configure DSP
                        p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                        p_OUTPUT_REG_EN = "TRUE",
                        p_INPUT_REG_EN = "TRUE",
                        p_COEFF_0       = C(coefficients[i], 20),

                        # Reset
                        i_CLK           = ClockSignal(),
                        i_RESET        = ResetSignal(),

                        # IOs
                        i_A             = C(0, 20),
                        i_B             = self.data_in,
                        o_Z             = self.z[i],  
                        i_FEEDBACK      = C(4, 3),
                        i_UNSIGNED_A    = not signed,
                        i_UNSIGNED_B    = not signed,
                        o_DLY_B         = self.delay_b[i],
                        i_LOAD_ACC      = 1,
                        i_ACC_FIR       = C(0, 6),
                        i_ROUND         = 0,
                        i_SATURATE      = 0,
                        i_SHIFT_RIGHT   = C(0, 6),
                        i_SUBTRACT      = 0
                    )
                elif (i == len(coefficients) - 1):
                    self.specials += Instance("DSP38",

                        # Parameters.
                        # -----------
                        # Mode Bits to configure DSP
                        p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                        p_OUTPUT_REG_EN = "FALSE",
                        p_INPUT_REG_EN = "TRUE",
                        p_COEFF_0       = C(coefficients[i], 20),

                        # Reset
                        i_CLK           = ClockSignal(),
                        i_RESET        = ResetSignal(),

                        # IOs
                        i_A             = self.z[i - 1][0:20],
                        i_B             = self.delay_b[i - 1],
                        o_Z             = self.z[i],  
                        i_FEEDBACK      = C(4, 3),
                        i_UNSIGNED_A    = not signed,
                        i_UNSIGNED_B    = not signed,
                        i_LOAD_ACC      = 1,
                        i_ACC_FIR       = C(0, 6),
                        i_ROUND         = 0,
                        i_SATURATE      = 1,
                        i_SHIFT_RIGHT   = C(0, 6),
                        i_SUBTRACT      = 0
                    )
                else:
                    self.specials += Instance("DSP38",

                        # Parameters.
                        # -----------
                        # Mode Bits to configure DSP
                        p_DSP_MODE     =  "MULTIPLY_ADD_SUB",
                        p_OUTPUT_REG_EN = "TRUE",
                        p_INPUT_REG_EN = "TRUE",
                        p_COEFF_0       = C(coefficients[i], 20),

                        # Reset
                        i_CLK           = ClockSignal(),
                        i_RESET        = ResetSignal(),

                        # IOs
                        i_A             = self.z[i - 1][0:20],
                        i_B             = self.delay_b[i - 1],
                        o_Z             = self.z[i],  
                        i_FEEDBACK      = C(4, 3),
                        i_UNSIGNED_A    = not signed,
                        i_UNSIGNED_B    = not signed,
                        o_DLY_B         = self.delay_b[i],
                        i_LOAD_ACC      = 1,
                        i_ACC_FIR       = C(0, 6),
                        i_ROUND         = 0,
                        i_SATURATE      = 0,
                        i_SHIFT_RIGHT   = C(0, 6),
                        i_SUBTRACT      = 0
                    )
        elif (len(coefficients) > 0 or number_of_coefficients > 0):
            self.rst = Signal()
            self.ready = Signal()
            self.comb += self.ready.eq(~self.rst)
            if (not coefficients_file):
                number_of_coefficients = len(coefficients)
            self.count = Signal(len(bin(number_of_coefficients - 1)[2:]), reset=0)

            if (not coefficients_file and number_of_coefficients > 0):
                self.sel_coeff = Signal(20)
                self.COEFF = Array(Signal() for _ in range (number_of_coefficients))
                if (coefficients != ""):
                    coefficients.reverse()
                for i in range (number_of_coefficients):
                    self.COEFF[i] = Signal(bits_sign=(20, True if signed else False), name=f"COEFF_{i}", reset=decimal_to_fixed_point(coefficients[i], coefficient_width - fractional_bits, fractional_bits, signed))

                for i in range (number_of_coefficients):
                    self.comb += [
                        If(self.count == i,
                           self.sel_coeff.eq(self.COEFF[i]))
                    ]
            elif (number_of_coefficients > 0):
                self.sel_coeff = Signal(len(bin(number_of_coefficients - 1)[2:]), reset=0)
                if (number_of_coefficients > 1):
                    self.specials.coefficients = Memory(width=20, depth=number_of_coefficients)
                    self.port = self.coefficients.get_port(write_capable=False, async_read=True, mode=READ_FIRST, has_re=False)
                    self.specials += self.port
                    self.comb += self.port.adr.eq(self.count)
            else:
                self.sel_coeff = Signal()
            
            self.feedback = Signal(3)
            self.dsp_out = Signal(bits_sign=(38, True if signed else False))

            # Create shift register signals
            self.shift_reg = [Signal(input_width) for _ in range(number_of_coefficients)]
            if (coefficients != ""):
                self.sync += [
                    self.shift_reg[0].eq(self.data_in),
                    If(self.rst,
                       self.shift_reg[0].eq(0))
                    ]
                for i in range (1, number_of_coefficients):
                    self.sync += [
                        # Shift the data through the register
                        self.shift_reg[i].eq(self.shift_reg[i - 1]
                            ),
                    If(self.rst,
                       self.shift_reg[i].eq(0))

                    ]
            self.sync.accelerated += [
                self.count.eq(self.count - 1),
                If(self.count == 0,
                   self.count.eq(number_of_coefficients - 1)
                   )

            ]
            self.dsp_in = Signal(input_width)
            self.dout_reg = Signal(min(input_width + bit_growth, 38) if not truncated_output else output_data_width)
            if (not truncated_output and number_of_coefficients > 0):
                self.comb += self.data_out.eq(Mux(self.feedback == 1, self.dsp_out[0 : min(input_width + bit_growth, 38)], self.dout_reg))
            elif (number_of_coefficients > 0):
                self.comb += self.data_out.eq(Mux(self.feedback == 1, self.dsp_out[min(input_width + bit_growth, 38) - output_data_width : min(input_width + bit_growth, 38)], self.dout_reg))

            self.comb += [
                self.dout_reg.eq(self.data_out)
            ]
            
            # self.comb += ResetSignal("accelerated").eq(self.rst)
            self.sync.accelerated += [
                If(self.count == 0,
                   self.dsp_in.eq(self.shift_reg[number_of_coefficients - 1])
                   )
            ]
            for i in range(1, number_of_coefficients):
                self.sync.accelerated += [
                    If(self.count == i,
                       self.dsp_in.eq(self.shift_reg[i - 1])
                       )

                ]
            self.input_coeff = Signal(20)
            if (coefficients_file and number_of_coefficients > 1):
                self.comb += self.input_coeff.eq(self.port.dat_r)

            self.comb += self.feedback.eq(Mux(self.count == number_of_coefficients - 1, C(1, 3), C(0, 3)))

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP
                p_DSP_MODE      = "MULTIPLY_ACCUMULATE",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN  = "FALSE",

                # Reset
                i_CLK           = ClockSignal("accelerated"),
                i_RESET         = self.rst,
                # IOs
                i_A             = self.input_coeff if coefficients_file else self.sel_coeff,
                i_B             = self.dsp_in,
                o_Z             = self.dsp_out,  
                i_FEEDBACK      = self.feedback,
                i_UNSIGNED_A    = not signed,
                i_UNSIGNED_B    = not signed,
                i_LOAD_ACC      = 1,
                i_ROUND         = 0,
                i_SATURATE      = 1,
                i_SHIFT_RIGHT   = C(0, 6),
                i_SUBTRACT      = 0
            )
            