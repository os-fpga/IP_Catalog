# AXI STREAM ASYNCHRONUS FIFO Core Generation 

## Introduction
AXIS-ASYNC-FIFO is AXI4-Stream based asynchronus FIFO.

## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axis_async_fifo/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
There are thirteen parameters for AXIS_FIFO core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter        |       Keyword      |          Value          |
    |-------|--------------------   |--------------------|-------------------------|
    |   1.  |   DEPTH               |   depth            |    16,32,64,...,32768   |
    |   2.  |   DATA_WIDTH          |   data_width       |    1-4096               |
    |   3.  |   LAST_ENABLE         |   last_en          |    0/1                  |  
    |   4.  |   ID_ENABLE           |   id_en            |    0/1                  |
    |   5.  |   ID_WIDTH            |   id_width         |    1-32                 |
    |   6.  |   DEST_ENABLE         |   dest_en          |    0/1                  |
    |   7.  |   DEST_WIDTH          |   dest_width       |    1-32                 |
    |   8.  |   USER_ENABLE         |   user_en          |    0/1                  |
    |   9.  |   USER_WIDTH          |   user_width       |    1-4096               |
    |   10. |   RAM_PIPELINE_OUTPUT |   pip_out          |    0-2                  |
    |   11. |   FRAME_FIFO          |   frame_fifo       |    0/1                  |
    |   12. |   DROP_BAD_FRAME      |   drop_bad_frame   |    0/1                  |
    |   13. |   DROP_WHEN_FULL      |   drop_when_full   |    0/1                  |
    |   14. |   OUTPUT_FIFO_ENABLE  |   out_fifo_en      |    0/1                  |
    |   15. |   BAD_FRAME_VALUE     |   bad_frame_value  |    0/1                  |


To generate RTL with above parameters, run the following command:
```
python3 axis_async_fifo_gen.py --depth=2048 --data_width=32 --build-name=axis_async_fifo --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axis_async_fifo/v1_0/<build-name>/synth/` directory.

## References

https://github.com/alexforencich/verilog-i2c/blob/master/rtl/axis_async_fifo.v
