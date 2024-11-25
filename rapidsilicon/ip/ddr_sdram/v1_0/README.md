# AXI-RAM Core Generation 
## Introduction
AXI-RAM is AXI4 based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axi/start

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/ddr_sdram/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

## Parameters
User can configure ddr_sdram CORE using following parameters:

| Sr.No.|     Parameter       |      Keyword        |    Value    |
|-------|---------------------|---------------------|-------------|
|   1.  |   DATA_WIDTH        |     data_width      |  8,16,32,64 |
|   2.  |   ADDRESS_WIDTH     |     addr_width      |    8-16     |
|   3.  |   ID_WIDTH          |     id_width        |    1-8      |
|   4.  |   PIPELINE_OUTPUT   |     pip_out         |    0/1      |


To generate RTL with above parameters, run the following command:
```
python3 ddr_sdram_gen.py --data_width=32 --addr_width=8 --build-name=ram --build
```


## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/ddr_sdram/v1_0/<build-name>/synth/` directory.


## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/ddr_sdram.v