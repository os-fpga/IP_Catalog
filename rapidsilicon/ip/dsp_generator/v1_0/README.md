# DSP Core Generation 
## Introduction

This is a customizable DSP Core module with various algorithms for DSP Decomposition listed below with their respective multiplicand bit widths:
1. Karatsuba Algoritm with k = 18 for both signed and unsigned multiplications.
2. Pipelined Karatsuba Algorithm with k = 18 for unsigned and k = 17 for signed multiplications.
    * Multiplications between 18 (17 for signed) and 36 (34 for signed) bit wide numbers will take 2 clock cycles to compute.
    * Multiplications between 36 (34 for signed) and 54 (51 for signed) bit wide numbers will take 3 clock cycles to compute.
    * Multiplications between 54 (51 for signed) and 72 (68 for signed) bit wide numbers will take 4 clock cycles to compute.
3. Karatsuba-Ofman Algorithm with k = 17 for unsigned and k = 16 for signed multiplications.

For more information, refer to the included documentation.

## Generator Script
This directory contains the generator script which places the generated RTL to `rapidsilicon/ip/dsp_generator/v1_0/<build-name>/src/` directory along with the simulation files.

## Parameters
These are the parameters for DSP core along with their keyword and values: -

| Sr.No. |      Parameter             |       Keyword   |    Value                              |
|--------|----------------------------|-----------------|---------------------------------------|
|   1.   |   EQUATION                 |     equation    | A\*B / A\*B+C\*D / A\*B+C\*D+E\*F+G*H |
|   2.   |   A_WIDTH                  |     a_width     | 1 - 72 (1. and 2. unsigned) / 1 - 68 (2. signed and 3. unsigned) / 1 - 64 (3. signed)|
|   3.   |   B_WIDTH                  |     b_width     | 1 - 72 (1. and 2. unsigned) / 1 - 68 (2. signed and 3. unsigned) / 1 - 64 (3. signed)|
|   4.   |   C_WIDTH                  |     c_width     |               1 - 20                  |
|   5.   |   D_WIDTH                  |     d_width     |               1 - 18                  |
|   6.   |   E_WIDTH                  |     e_width     |               1 - 20                  |
|   7.   |   F_WIDTH                  |     f_width     |               1 - 18                  |
|   8.   |   G_WIDTH                  |     g_width     |               1 - 20                  |
|   9.   |   H_WIDTH                  |     h_width     |               1 - 18                  |
|   10.  |   REG_IN                   |     reg_in      |                0 / 1                  |
|   11.  |   REG_OUT                  |     reg_out     |                0 / 1                  |
|   12.  |   UNSIGNED                 |     unsigned    |                0 / 1                  |
|   13.  |   FEATURE                  |     feature     |      Base / Enhanced / Pipeline       |


To generate RTL with above parameters, run the following command:
```
python3 dsp_gen.py --build --a_width=54 --b_width=54
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/dsp_generator/v1_0/<build-name>/synth/` directory.
