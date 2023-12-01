# FIFO Core Generation 
## Introduction

This is a customizable FIFO Core module with various different parameters and features a list of which is given below.

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/fifo_generator/v1_0/<build-name>/src/` directory.

## Parameters
These are the parameters for FIFO core along with their keyword and values: -

| Sr.No. |      Parameter             |       Keyword              |    Value      |
|--------|----------------------------|----------------------------|---------------|
|   1.   |   DATA_WIDTH*               |     data_width             |    1 - 1024   |
|   2.   |   DEPTH               |     depth             |    2 - 523264   |
|   3.   |   FULL_THRESHOLD           |     full_threshold     |    0 / 1     |
|   4.   |   EMPTY_THRESHOLD        |     empty_threshold        |    0 / 1     |
|   6.   |   SYNCHRONOUS             |     synchronous           |    0 / 1     |
|   7.  |   BUILTIN_FIFO           |   builtin_fifo           |   0 / 1   |
|   8.  |   FIRST_WORD_FALL_THROUGH |   first_word_fall_through   |   0 / 1   |
|   9.   |   FULL_VALUE**           |     full_value     |    1 - DEPTH - 1     |
|   10.   |   EMPTY_VALUE**        |     empty_value        |    0 - DEPTH  - 1     |
|   11.   |   ASYMMETRIC            |   asymmetric          |   0 / 1       |
|   12.   |   DATA_WIDTH_WRITE***   |     data_width_write  |    9, 18, 36, 72, 144, 288, 576   |
|   13.   |   DATA_WIDTH_READ***   |     data_width_read    |    9, 18, 36, 72, 144, 288, 576   |

```
*   Only Available when Asymmetric = 0
**  Only Available when the respective FULL_THRESHOLD/EMPTY_THRESHOLD = 1
*** Only Available when Asymmetric = 1
```


To generate RTL with above parameters, run the following command:
```
./fifo_generator_gen.py --data_width=72 --depth=3072 --build-name=fifo_wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/fifo_generator/v1_0/<build-name>/synth/` directory.
