# AXI-CDMA Core Generation 
## Introduction

AXI-CDMA is AXI4 based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axi/start

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi_cdma/v1_0/<build-name>/src` directory and generates its wrapper in the same directory. 

## Parameters
There are seven parameters for AXI-CDMA core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter       |         Keyword        |         Value         |
    |-------|----------------------|------------------------|-----------------------|
    |   1.  |   AXI_DATA_WIDTH     |    data_width          |   8,16,32,64,128,256  |
    |   2.  |   AXI_ADDR_WIDTH     |    addr_width          |   8-16                |
    |   3.  |   AXI_ID_WIDTH       |    id_width            |   1-32                |
    |   4.  |   AXI_MAX_BURST_LEN  |    axi_max_burst_len   |   1-256               |
    |   5.  |   LEN_WIDTH          |    len_width           |   1-20                |
    |   6.  |   TAG_WIDTH          |    tag_width           |   1-8                 |
    |   7.  |   ENABLE_UNALIGNED   |    enable_unaligned    |   0/1                 |


To generate RTL with above parameters, run the following command:
```
python3 axi_cdma_gen.py --data_width=256 --add_width=8 --build-name=dpram --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi_cdma/v1_0/<build-name>/synth` directory.


## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_cdma.v