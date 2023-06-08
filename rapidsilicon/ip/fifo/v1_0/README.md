# FIFO Core Generation 
## Introduction

This is a customizable FIFO Core module with various different parameters and features a list of which is given below.

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/fifo/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

## Parameters
These are the parameters for FIFO core along with their keyword and values: -

| Sr.No. |      Parameter             |       Keyword              |    Value      |
|--------|----------------------------|----------------------------|---------------|
|   1.   |   DATA_WIDTH               |     data_width             |    1 - 128   |
|   2.   |   DEPTH               |     depth             |    2 - 32768   |
|   3.   |   FULL_THRESHOLD           |     full_threshold     |    1 - 4094     |
|   4.   |   EMPTY_THRESHOLD        |     empty_threshold        |    0 - 4094     |
|   5.   |   COMMON_CLK               |     common_clk             |    0 / 1     |
|   6.   |   SYNC_FIFO             |     sync_fifo           |    0 / 1     |
|   7.  |   DRAM                    |   dram                |   0 / 1   |
|   8.  |   FIRST_WORD_FALL_THROUGH |   fwft                |   0 / 1   |




To generate RTL with above parameters, run the following command:
```
./fifo_gen.py --data_width=72 --depth=3072 --build-name=fifo_wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/fifo/v1_0/<build-name>/synth/` directory.
