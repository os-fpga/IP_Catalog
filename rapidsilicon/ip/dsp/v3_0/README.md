# DSP Core Generation 
## Introduction

This is a customizable DSP Core module with Karatsuba-Ofman Algorithm for DSP Decomposition with k = 17 for unsigned and k = 16 for signed numbers.

For more information, refer to the included documentation.

## Generator Script
This directory contains the generator script which places the generated RTL to `rapidsilicon/ip/dsp/v3_0/<build-name>/src/` directory along with the simulation files.

## Parameters
These are the parameters for DSP core along with their keyword and values: -

| Sr.No. |      Parameter             |       Keyword              |    Value                          |
|--------|----------------------------|----------------------------|-----------------------------------|
|   1.   |   FEATURE                  |     feature                |        A\*B                       |
|   2.   |   A_WIDTH                  |     a_width                |1 - 68 (unsigned) / 1 - 64 (signed)|
|   3.   |   B_WIDTH                  |     b_width                |1 - 68 (unsigned) / 1 - 64 (signed)|
|   10.  |   REG_IN                   |     reg_in                 |        0 / 1                      |
|   11.  |   REG_OUT                  |     reg_out                |        0 / 1                      |
|   12.  |   UNSIGNED                 |     unsigned               |        0 / 1                      |


To generate RTL with above parameters, run the following command:
```
python3 dsp_gen.py --build --a_width=51 --b_width=51
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/dsp/v3_0/<build-name>/synth/` directory.
