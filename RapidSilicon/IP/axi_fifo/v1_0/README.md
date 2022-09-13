# AXI FIFO Core Generation 

## Introduction
AXI-FIFO is AXI4 based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axi/start

## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi_fifo/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
There are seventeen parameters for AXI_FIFO core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter     |       Keyword      |          Value          |
    |-------|--------------------|--------------------|-------------------------|
    |   1.  |   DATA_WIDTH       |   data_width       |  32,64,128,256,512,1024 |
    |   2.  |   ADDR_WIDTH       |   addr_width       |  1-64                   |
    |   3.  |   ID_WIDTH         |   id_width         |  1-32                   |
    |   4.  |   AWUSER_ENABLE    |   aw_user_en       |  0/1                    |
    |   5.  |   AWUSER_WIDTH     |   aw_user_width    |  0-1024                 |
    |   6.  |   WUSER_ENABLE     |   w_user_en        |  0/1                    |
    |   7.  |   WUSER_WIDTH      |   w_user_width     |  0-1024                 |
    |   8.  |   BUSER_ENABLE     |   b_user_en        |  0/1                    |
    |   9.  |   BUSER_WIDTH      |   b_user_width     |  0-1024                 |
    |   10. |   ARUSER_ENABLE    |   ar_user_en       |  0/1                    |
    |   11. |   ARUSER_WIDTH     |   ar_user_width    |  0-1024                 |
    |   12. |   RUSER_ENABLE     |   r_user_en        |  0/1                    |
    |   13. |   RUSER_WIDTH      |   r_user_width     |  0-1024                 |
    |   14. |   WRITE_FIFO_DEPTH |   write_fifo_depth |  0,32,512               |
    |   15. |   READ_FIFO_DEPTH  |   read_fifo_depth  |  0,32,512               |
    |   16. |   WRITE_FIFO_DELAY |   write_fifo_delay |  0/1                    |
    |   17. |   READ_FIFO_DELAY  |   read_fifo_delay  |  0-4096                 |



To generate RTL with above parameters, run the following command:
```
python3 axi_fifo_gen.py --data_width=32 --addr_width=64 --build-name=fifo --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi_fifo/v1_0/<build-name>/synth/` directory.

## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_fifo.v
