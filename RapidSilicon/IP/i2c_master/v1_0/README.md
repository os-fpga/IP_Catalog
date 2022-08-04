# I2C-MASTER Core Generation 

## Introduction
I2C-MASTER is AXI4-Lite slave interface based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/i2c/start

## Generator Script

This directory contains the generator script which places the RTL to `/<mod_name>/rapidsilicon/ip/i2c_master/v1_0/src` directory and generates its wrapper in the same directory. 
    
## Parameters
There are eight parameters for I2C_MASTER core. These parameters, their keywords and values are given below:

    | Sr.No.|       Parameter           |           Keyword         |       Value      |
    | ----- |       ---------           |           -------         |       -----      |
    |   1.  |   DEFAULT_PRESCALE        |       default_prescale    |        0/1       |
    |   2.  |   FIXED_PRESCALE          |       fixed_prescale      |        0/1       |
    |   3.  |   CMD_FIFO                |       cmd_fifo            |        0/1       |  
    |   4.  |   CMD_FIFO_ADDR_WIDTH     |       cmd_addr_width      |        0-5       |
    |   5.  |   WRITE_FIFO              |       write_fifo          |        0/1       |
    |   6.  |   WRITE_FIFO_ADDR_WIDTH   |       write_addr_width    |        0-5       |
    |   7.  |   READ_FIFO               |       read_fifo           |        0/1       |
    |   8.  |   READ_FIFO_ADDR_WIDTH    |       read_addr_width     |        0-5       |


To give above parameters to RTL, write `-P<keyword>=<value>` in configure_ip command in raptor.tcl file.

For example: configure_ip i2c_master_gen -mod_name i2c_master_wrapper `-Pdefault_prescale=1` `-Pfixed_prescale=0` `-Pcmd_fifo=1` `-Pcmd_addr_width=4` `-Pwrite_fifo=1` `-Pwrite_addr_width=4` `-Pread_fifo=1` `-Pread_addr_width=4` -out_file ./i2c_master_wrapper.v


## TCL File

This python script also generates a .tcl file which will be placed in `/<mod_name>/rapidsilicon/ip/i2c_master/v1_0/synth` directory.

## Design Generation

To generate your design, follow these steps.

1-  First, you have to source the Raptor.

2-  Run the following command to generate your design.
```
raptor --batch --script raptor.tcl
```

## References

https://github.com/alexforencich/verilog-i2c/blob/master/rtl/i2c_master_axil.v
