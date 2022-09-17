# I2C-MASTER Core Generation 

## Introduction
I2C-MASTER is AXI4-Lite slave interface based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/i2c/start

## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/i2c_master/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
There are eight parameters for I2C_MASTER core. These parameters, their keywords and values are given below:

    | Sr.No.|        Parameter          |        Keyword        |   Value   |
    |-------|---------------------------|-----------------------|-----------|
    |   1.  |   DEFAULT_PRESCALE        |   default_prescale    |    0/1    |
    |   2.  |   FIXED_PRESCALE          |   fixed_prescale      |    0/1    |
    |   3.  |   CMD_FIFO                |   cmd_fifo            |    0/1    |  
    |   4.  |   CMD_FIFO_ADDR_WIDTH     |   cmd_addr_width      |    1-5    |
    |   5.  |   WRITE_FIFO              |   write_fifo          |    0/1    |
    |   6.  |   WRITE_FIFO_ADDR_WIDTH   |   write_addr_width    |    1-5    |
    |   7.  |   READ_FIFO               |   read_fifo           |    0/1    |
    |   8.  |   READ_FIFO_ADDR_WIDTH    |   read_addr_width     |    1-5    |


To generate RTL with above parameters, run the following command:
```
python3 i2c_master_gen.py --build-name=i2c --build-dir=./test_dir --write_fifo=1 --write_addr_width=5 --build
```


## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/i2c_master/v1_0/<build-name>/synth/` directory.


## References

https://github.com/alexforencich/verilog-i2c/blob/master/rtl/i2c_master_axil.v
