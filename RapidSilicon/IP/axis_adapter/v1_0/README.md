# AXIS ADAPTER Core Generation 

## Introduction
AXIS-ADAPTER is AXI4-Stream based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axis/start

## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axis_adapter/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
There are eight parameters for AXIS_ADAPTER core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter     |       Keyword      |    Value     |
    |-------|--------------------|--------------------|--------------|
    |   1.  |   S_DATA_WIDTH     |   s_data_width     |    1-4096    |
    |   2.  |   S_DATA_WIDTH     |   m_data_width     |    1-4096    |  
    |   3.  |   ID_ENABLE        |   id_en            |    0/1       |
    |   4.  |   ID_WIDTH         |   id_width         |    1-32      |
    |   5.  |   DEST_ENABLE      |   dest_en          |    0/1       |
    |   6.  |   DEST_WIDTH       |   dest_width       |    1-32      |
    |   7.  |   USER_ENABLE      |   user_en          |    0/1       |
    |   8.  |   USER_WIDTH       |   user_width       |    1-4096    |


To generate RTL with above parameters, run the following command:
```
python3 axis_adapter_gen.py --s_data_width=32 --build-name=adapter --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axis_adapter/v1_0/<build-name>/synth/` directory.

## References

https://github.com/alexforencich/verilog-axis/blob/master/rtl/axis_adapter.v
