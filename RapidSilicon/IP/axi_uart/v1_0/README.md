# AXI-UART Core Generation 

## Introduction
AXI-UART is AXI4-Lite based IP core.

## Generator Script

This directory contains the generator script which places the RTL to `/ip_build/rapidsilicon/ip/axi_uart/v1_0/<mod_name>/src` directory and generates its wrapper in the same directory. 
    
## Parameters
There are four parameters for AXI_UART core. These parameters, their keywords and values are given below:

    | Sr.No.|       Parameter           |           Keyword         |       Value      |
    | ----- |       ---------           |           -------         |       -----      |
    |   1.  |   AXI4_ADDRESS_WIDTH      |       addr_width          |        0-16      |
    |   2.  |   AXI4_RDATA_WIDTH        |       rdata_width         |        8,16,32   |
    |   3.  |   AXI4_WDATA_WIDTH        |       wdata_width         |        8,16,32   |  
    |   4.  |   AXI4_PROT_WIDTH         |       prot_width          |        3         |


To generate RTL with above parameters, run the following command:
```
python3 axi_uart_gen.py --addr_width=8 --rdata_width=32 --build_name=uart --mod_name=uart_wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `/ip_build/rapidsilicon/ip/axi_uart/v1_0/<mod_name>/synth` directory.


## References

https://github.com/RapidSilicon/axi_uart/tree/main/rtl
