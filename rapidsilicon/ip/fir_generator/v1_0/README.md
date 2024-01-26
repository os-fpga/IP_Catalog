# FIR Core Generation 
## Introduction

This is a customizable FIR Core module with various different parameters and features, a list of which is given below.

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/fir_generator/v1_0/<build-name>/src/` directory.

## Parameters
These are the parameters for FIR core along with their keyword and values: -

| Sr.No. | Parameter | Keyword | Value |
|--------|-----------|---------|-------|
| 1. | Input Width | input_width | 1 - 18 |
| 2. | Coefficients | coefficients | `<numbers separated by commas or whitespaces>` |
| 3. | Coefficients File | coefficients_file | 1 / 0 |
| 4. | File Path | file_path | `<path to .txt file with numbers separated by commas or whitespaces>` |
| 5. | Optimization | optimization | Area / Performance |
| 6. | Number of Coefficients | number_of_coefficients | 1 - 120 |
| 7. | Coefficient Fractional Bits | coeff_fractional_bits | 0 - 20 |
| 8. | Signed | signed | 0 / 1 |
| 9. | Input Fractional Bits | input_fractional_bits | 0 - 18 |
| 10. | Coefficient Width | coefficient_width | 0 - 20 |
| 11. | Output Data Width | output_data_width | 0 - 38 |
| 12. | Truncated Output | truncated_output | 0 / 1 |



To generate RTL with above parameters, run the following command:
```
./fir_generator_gen.py --build-name=fir_wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/fir_generator/v1_0/<build-name>/synth/` directory.
<>