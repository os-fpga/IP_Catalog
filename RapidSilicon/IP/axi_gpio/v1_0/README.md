# AXI-GPIO Core Generation 
## Introduction

AXI-GPIO is AXI4-Lite based IP core.


## Generator Script

This directory contains the generator script which places the RTL to `/<mod_name>/rapidsilicon/ip/axi_gpio/v1_0/src` directory and generates its wrapper in the same directory. 

## Parameters
There are two parameters for AXI-GPIO core. These parameters, their keywords and values are given below:

    | Sr.No.|       Parameter           |           Keyword         |       Value      |
    | ----- |       ---------           |           -------         |       -----      |
    |   1.  |   DATA_WIDTH              |       data_width          |      8,16,32     |
    |   2.  |   ADDRESS_WIDTH           |       addr_width          |      8,16        |


To give above parameters to RTL, write `-P<keyword>=<value>` in configure_ip command in raptor.tcl file.

For example: configure_ip axi_gpio_gen -mod_name axi_gpio_wrapper `-Pdata_width=32` `-Paddr_width=16` -out_file ./axi_gpio_wrapper.v


## TCL File
This python script also generates a .tcl file which will be placed in `/<mod_name>/rapidsilicon/ip/axi_gpio/v1_0/synth` directory.

## Design Generation

To generate your design, follow these steps.

1-  First, you have to source the Raptor.

2-  Run the following command to generate your design.
```
raptor --batch --script raptor.tcl
```

## References

https://github.com/smartfoxdata/axi4lite_gpio/tree/master/rtl
