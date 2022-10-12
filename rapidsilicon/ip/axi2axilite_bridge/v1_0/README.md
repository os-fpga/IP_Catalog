# AXI4 to AXI-LITE Brigde IP
## Introduction
AXI4-to-AXILITE Bridge IP

For more information, visit: https://github.com/ZipCPU/wb2axip#wb2axip-bus-interconnects-bridges-and-other-components

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi2axilite_bridge/v1_0/<build-name>/src` directory and generates its wrapper in the same directory. 

## Parameters
There are three parameters for AXI-to-AXILITE core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter       |         Keyword        |         Value         |
    |-------|----------------------|------------------------|-----------------------|
    |   1.  |   C_AXI_DATA_WIDTH   |    data_width          |   8,16,32,64,128,256  |
    |   2.  |   C_AXI_ADDR_WIDTH   |    addr_width          |   6-16                |
    |   3.  |   C_AXI_ID_WIDTH     |    id_width            |   1-32                |



To generate RTL with above parameters, run the following command:
```
python3 axi2axilite_bridge_gen.py --data_width=256 --addr_width=8 --build-name=wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi2axilite_bridge/v1_0/<build-name>/synth` directory.


## References
https://github.com/ZipCPU/wb2axip/blob/master/rtl/axi2axilite.v
