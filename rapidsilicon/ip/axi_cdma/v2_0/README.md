# AXI-CDMA Core Generation 
## Introduction
AXI-CDMA is AXI4 based IP core.

For more information, visit: https://zipcpu.com/blog/2021/03/20/xilinx-forums.html

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi_cdma/v2_0/<build-name>/src` directory and generates its wrapper in the same directory. 

## Parameters
User can configure AXI_CDMA CORE using following parameters:

| Sr.No.|      Parameter       |         Keyword        |         Value         |
|-------|----------------------|------------------------|-----------------------|
|   1.  |   C_AXI_DATA_WIDTH   |    axi_data_width      |   8,16,32,64,128,256  |
|   2.  |   C_AXI_ADDR_WIDTH   |    axi_addr_width      |   8,16,32,64,128,256                |
|   3.  |   C_AXI_ID_WIDTH     |    id_width            |   1-32                |
|   5.  |   C_AXIL_ADDR_WIDTH  |    axil_addr_width     |   1-64                |
|   6.  |   C_AXIL_DATA_WIDTH  |    axil_data_width     |   32                  |



To generate RTL with above parameters, run the following command:
```
python3 axi_cdma_gen.py --axi_data_width=32 --axi_addr_width=32 --build-name=cdma --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi_cdma/v2_0/<build-name>/synth` directory.


## References

https://github.com/ZipCPU/wb2axip/blob/master/rtl/axidma.v
