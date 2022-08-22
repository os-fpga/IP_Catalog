# AXI-RAM Core Generation 
## Introduction

AXI-DPRAM is AXI4 based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axi/start

## Generator Script
This directory contains the generator script which places the RTL to `/ip_build/rapidsilicon/ip/axi_dpram/v1_0/<mod_name>/src` directory and generates its wrapper in the same directory. 

## Parameters
There are seven parameters for AXI-DPRAM core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter       |       Keyword      |    Value   |
    |-------|----------------------|--------------------|------------|
    |   1.  |   DATA_WIDTH         |    data_width      |   8,16,32  |
    |   2.  |   ADDRESS_WIDTH      |    addr_width      |   8,16     |
    |   3.  |   ID_WIDTH           |    id_width        |   1-8      |
    |   4.  |   A_PIPELINE_OUTPUT  |    a_pip_out       |   0/1      |
    |   5.  |   B_PIPELINE_OUTPUT  |    b_pip_out       |   0/1      |
    |   6.  |   A_INTERLEAVE       |    a_interleave    |   0/1      |
    |   7.  |   B_INTERLEAVE       |    b_interleave    |   0/1      |


To generate RTL with above parameters, run the following command:
```
python3 axi_dpram_gen.py --data_width=32 --add_width=8 --build_name=dpram --mod_name=wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `/ip_build/rapidsilicon/ip/axi_dpram/v1_0/<mod_name>/synth` directory.


## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_dp_ram.v