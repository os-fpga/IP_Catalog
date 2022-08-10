# AXI-GPIO Core Generation 
## Introduction

AXI-GPIO is AXI4-Lite based IP core.


## Generator Script

This directory contains the generator script which places the RTL to `/<build_name>/rapidsilicon/ip/axi_gpio/v1_0/src` directory and generates its wrapper in the same directory. 

## Parameters
There are two parameters for AXI-GPIO core. These parameters, their keywords and values are given below:

    | Sr.No.|       Parameter           |           Keyword         |       Value      |
    | ----- |       ---------           |           -------         |       -----      |
    |   1.  |   DATA_WIDTH              |       data_width          |      8,16,32     |
    |   2.  |   ADDRESS_WIDTH           |       addr_width          |      8,16        |


To generate RTL with above parameters, run the following command:
```
python3 axi_gpio_gen.py --data_width=16 --addr_width=8 --build_name=gpio --mod_name=wrapper --build
```

## TCL File
This python script also generates a raptor.tcl file which will be placed in `/<build_name>/rapidsilicon/ip/axi_gpio/v1_0/synth` directory.

## Design Generation

To generate your design, follow these steps.

1-  First, you have to source the Raptor.

2-  Run the following command to generate your design.
```
raptor --batch --script raptor.tcl
```

## References

https://github.com/smartfoxdata/axi4lite_gpio/tree/master/rtl
