# AXI STREAM UART Core Generation 
## Introduction

AXIS-UART is an AXI Stream based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/uart/start

## Generator Script
This directory contains the generator script which places the RTL to `/ip_build/rapidsilicon/ip/axis_uart/v1_0/<build_name>/src` directory and generates its wrapper in the same directory. 

## Parameters
There is one parameter for AXIS-UART core. This parameter, it's keyword and value is given below:

    | Sr.No.|      Parameter       |       Keyword      |    Value   |
    |-------|----------------------|--------------------|------------|
    |   1.  |   DATA_WIDTH         |    data_width      |    5 - 8   |



To generate RTL with above parameters, run the following command:
```
python3 axis_uart_gen.py --data_width=7 --build-name=uart --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `/ip_build/rapidsilicon/ip/axis_uart/v1_0/<build_name>/synth` directory.


## References

https://github.com/alexforencich/verilog-uart/tree/master/rtl