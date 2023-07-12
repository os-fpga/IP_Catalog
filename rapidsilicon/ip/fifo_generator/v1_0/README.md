# FIFO Core Generation 
## Introduction

This is a customizable FIFO Core module with various different parameters and features a list of which is given below.

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/fifo_generator/v1_0/<build-name>/src/` directory.

## Parameters
These are the parameters for FIFO core along with their keyword and values: -

| Sr.No. |      Parameter             |       Keyword              |    Value      |
|--------|----------------------------|----------------------------|---------------|
|   1.   |   DATA_WIDTH               |     data_width             |    1 - 128   |
|   2.   |   DEPTH               |     depth             |    2 - 32768   |
|   3.   |   FULL_THRESHOLD           |     full_threshold     |    0 / 1     |
|   4.   |   EMPTY_THRESHOLD        |     empty_threshold        |    0 / 1     |
|   6.   |   SYNCHRONOUS             |     synchronous           |    0 / 1     |
|   7.  |   BRAM                    |   bram                |   0 / 1   |
|   8.  |   FIRST_WORD_FALL_THROUGH |   first_word_fall_through   |   0 / 1   |
|   9.   |   FULL_VALUE           |     full_value     |    1 - 4094     |
|   10.   |   EMPTY_VALUE        |     empty_value        |    0 - 4094     |



To generate RTL with above parameters, run the following command:
```
./fifo_generator_gen.py --data_width=72 --depth=3072 --build-name=fifo_wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/fifo_generator/v1_0/<build-name>/synth/` directory.
