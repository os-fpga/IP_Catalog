# I2C-SLAVE Core Generation 

## Introduction
I2C-SLAVE is AXI4-Lite master interface based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/i2c/start

## Generator Script
This directory contains the generator script which places the RTL to `/ip_build/rapidsilicon/ip/i2c_slave/v1_0/<mod_name>/src` directory and generates its wrapper in the same directory. 

## Parameters
There are three parameters for I2C_SLAVE core. These parameters, their keywords and values are given below:

    | Sr.No.|       Parameter           |           Keyword         |       Value      |
    | ----- |       ---------           |           -------         |       -----      |
    |   1.  |   DATA_WIDTH              |       data_width          |      8,16,32     |
    |   2.  |   ADDRESS_WIDTH           |       addr_width          |      8,16        |
    |   3.  |   FILTER_LENGTH           |       filter_len          |      0-4         |



To generate RTL with above parameters, run the following command:
```
python3 i2c_slave_gen.py --data_width=16 --mod_name=wrapper --build
```

## TCL File 
This python script also generates a raptor.tcl file which will be placed in `/ip_build/rapidsilicon/ip/i2c_slave/v1_0/<mod_name>/synth` directory.

## References

https://github.com/alexforencich/verilog-i2c/blob/master/rtl/i2c_slave_axil_master.v