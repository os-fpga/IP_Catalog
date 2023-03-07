# DSP Core Generation 
## Introduction

This is a customizable DSP Core module with Karatsuba Algorithm for DSP Decomposition with k = 18 for both signed and unsigned.

For more information, refer to the included documentation.

## Generator Script
This directory contains the generator script which places the generated RTL to `rapidsilicon/ip/dsp/v1_0/<build-name>/src/` directory along with the simulation files.

## Parameters
These are the parameters for DSP core along with their keyword and values: -

| Sr.No. |      Parameter             |       Keyword   |    Value                              |
|--------|----------------------------|-----------------|---------------------------------------|
|   1.   |   FEATURE                  |     feature     | A\*B / A\*B+C\*D / A\*B+C\*D+E\*F+G*H |
|   2.   |   A_WIDTH                  |     a_width     |               1 - 72                  |
|   3.   |   B_WIDTH                  |     b_width     |               1 - 72                  |
|   4.   |   C_COUNT                  |     c_count     |               1 - 20                  |
|   5.   |   D_COUNT                  |     d_count     |               1 - 18                  |
|   6.   |   E_COUNT                  |     e_count     |               1 - 20                  |
|   7.   |   F_COUNT                  |     f_count     |               1 - 18                  |
|   8.   |   G_COUNT                  |     g_count     |               1 - 20                  |
|   9.   |   H_COUNT                  |     h_count     |               1 - 18                  |
|   10.  |   REG_IN                   |     reg_in      |                0 / 1                  |
|   11.  |   REG_OUT                  |     reg_out     |                0 / 1                  |
|   12.  |   UNSIGNED                 |     unsigned    |                0 / 1                  |


To generate RTL with above parameters, run the following command:
```
python3 dsp_gen.py --build --a_width=54 --b_width=54
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/dsp/v1_0/<build-name>/synth/` directory.
