# AXI-RAM Core Generation 
## Introduction

AXI-RAM is AXI4 based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axi/start

## Generator Script
This directory contains the generator script which places the RTL to `/ip_build/rapidsilicon/ip/axi_ram/v1_0/<mod_name>/src` directory and generates its wrapper in the same directory. 

## Parameters
There are four parameters for AXI-RAM core. These parameters, their keywords and values are given below:

    | Sr.No.|     Parameter       |      Keyword        |    Value    |
    |-------|---------------------|---------------------|-------------|
    |   1.  |   DATA_WIDTH        |     data_width      |   8,16,32   |
    |   2.  |   ADDRESS_WIDTH     |     addr_width      |   1-16      |
    |   3.  |   ID_WIDTH          |     id_width        |   0-8       |
    |   4.  |   PIPELINE_OUTPUT   |     pip_out         |   0/1       |


To generate RTL with above parameters, run the following command:
```
python3 axi_ram_gen.py --data_width=32 --add _width=8 --build_name=ram --mod_name=wrapper --build
```


## TCL File

This python script also generates a raptor.tcl file which will be placed in `/ip_build/rapidsilicon/ip/axi_ram/v1_0/<mod_name>/synth` directory.


## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_ram.v