# AXI-DMA Core Generation 
## Introduction

AXI-DMA is AXI4 based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axi/start

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi_dma/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

## Parameters
There are fifteen parameters for AXI-DMA core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter       |         Keyword        |         Value         |
    |-------|----------------------|------------------------|-----------------------|
    |   1.  |   AXI_DATA_WIDTH     |    axi_data_width      |   8,16,32,64,128,256  |
    |   2.  |   AXI_ADDR_WIDTH     |    axi_addr_width      |   8-16                |
    |   3.  |   AXI_ID_WIDTH       |    axi_id_width        |   1-32                |
    |   4.  |   AXI_MAX_BURST_LEN  |    axi_max_burst_len   |   1-256               |
    |   5.  |   AXIS_LAST_ENABLE   |    axis_last_enable    |   0/1                 |
    |   6.  |   AXIS_ID_ENABLE     |    axis_id_enable      |   0/1                 |
    |   7.  |   AXIS_ID_WIDTH      |    axis_id_width       |   1-32                |
    |   8.  |   AXIS_DEST_ENABLE   |    axis_dest_enable    |   0/1                 |
    |   9.  |   AXIS_DEST_WIDTH    |    axis_dest_width     |   1-8                 |
    |   10. |   AXIS_USER_ENABLE   |    axis_user_enable    |   0/1                 |
    |   11. |   AXIS_USER_WIDTH    |    axis_user_width     |   1-8                 |
    |   12. |   LEN_WIDTH          |    len_width           |   1-20                |
    |   13. |   TAG_WIDTH          |    tag_width           |   1-8                 |
    |   14. |   ENABLE_SG          |    enable_sg           |   0/1                 |
    |   15. |   ENABLE_UNALIGNED   |    enable_unaligned    |   0/1                 |


To generate RTL with above parameters, run the following command:
```
python3 axi_dma_gen.py --axi_data_width=32 --axi_add_width=8 --build_name=dma --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi_dma/v1_0/<build-name>/synth/` directory.


## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_dma.v