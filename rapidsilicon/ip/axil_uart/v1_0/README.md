# AXI LITE UART Core Generation 

## Introduction
AXI LITE UART is AXI4-Lite based IP core.

## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axil_uart16550/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
There are two parameters for AXI LITE UART core. These parameters, their keywords and values are given below:

    | Sr.No.|       Parameter       |      Keyword     |     Value      |
    |-------|-----------------------|------------------|----------------|
    |   1.  |     ADDRESS_WIDTH     |   addr_width     |   8,16,32      |
    |   2.  |     DATA_WIDTH        |   data_width     |   8,16,32,64   |  


To generate RTL with above parameters, run the following command:
```
python3 axil_uart16550_gen.py --addr_width=8 --data_width=32 --build-name=uart --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axil_uart16550/v1_0/<build-name>/synth` directory.


## References

https://github.com/RapidSilicon/axi_uart/tree/main/rtl
