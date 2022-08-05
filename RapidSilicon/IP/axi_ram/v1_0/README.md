# AXI-RAM Core Generation 
## Introduction

AXI-RAM is AXI4-Lite based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axi/start

## Generator Script
This directory contains the generator script which places the RTL to `/<mod_name>/rapidsilicon/ip/axi_ram/v1_0/src` directory and generates its wrapper in the same directory. 

## Parameters
There are four parameters for AXI-RAM core. These parameters, their keywords and values are given below:

    | Sr.No.|       Parameter           |           Keyword         |       Value      |
    | ----- |       ---------           |           -------         |       -----      |
    |   1.  |   DATA_WIDTH              |       data_width          |      8,16,32     |
    |   2.  |   ADDRESS_WIDTH           |       addr_width          |      8,16        |
    |   2.  |   ID_WIDTH                |       id_width            |      0-8         |
    |   2.  |   PIPELINE_OUTPUT         |       pip_out             |      0/1         |


To give above parameters to RTL, write `-P<keyword>=<value>` in configure_ip command in raptor.tcl file.

For example: configure_ip axi_ram_gen -mod_name axi_ram_wrapper `-Pdata_width=32` `-Paddr_width=16` `-Pid_width=5` `-Ppip_out=1` -out_file ./axi_ram_wrapper.v

## TCL File

This python script also generates a .tcl file which will be placed in `/<mod_name>/rapidsilicon/ip/axi_ram/v1_0/synth` directory.

## Design Generation

To generate your design, follow these steps.

1- First, you have to source the Raptor.

2- Run the following command to generate your design.
```
raptor --batch --script raptor.tcl
```

## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_ram.v