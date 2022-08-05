# I2C-SLAVE Core Generation 

## Introduction
I2C-SLAVE is AXI4-Lite master interface based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/i2c/start

## Generator Script
This directory contains the generator script which places the RTL to `/<mod_name>/rapidsilicon/ip/i2c_slave/v1_0/src` directory and generates its wrapper in the same directory. 

## Parameters
There are three parameters for I2C_SLAVE core. These parameters, their keywords and values are given below:

    | Sr.No.|       Parameter           |           Keyword         |       Value      |
    | ----- |       ---------           |           -------         |       -----      |
    |   1.  |   DATA_WIDTH              |       data_width          |      8,16,32     |
    |   2.  |   ADDRESS_WIDTH           |       addr_width          |      8,16        |
    |   3.  |   FILTER_LENGTH           |       filter_len          |      0-4         |



To give above parameters to RTL, write `-P<keyword>=<value>` in configure_ip command in raptor.tcl file.

For example: configure_ip i2c_slave_gen -mod_name i2c_slave_wrapper `-Pdata_width=32` `-Paddr_width=16` `-Pfilter_len=4` -out_file ./i2c_slave_wrapper.v

## TCL File 
This python script also generates a .tcl file which will be placed in `/<mod_name>/rapidsilicon/ip/i2c_slave/v1_0/synth` directory.

## Design Generation
To generate your design, follow these steps.

1- First, you have to source the Raptor.

2- Run the following command to generate your design.
```
raptor --batch --script raptor.tcl
```

## References

https://github.com/alexforencich/verilog-i2c/blob/master/rtl/i2c_slave_axil_master.v