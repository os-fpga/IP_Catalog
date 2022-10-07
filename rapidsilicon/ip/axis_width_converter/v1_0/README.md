# AXI STREAM WIDTH CONVERTER Core Generation 

## Introduction
AXIS-WIDTH-CONVERTER is AXI4-Stream based IP core.

## Generator Script
This directory contains the generator script which generates the RTL to `rapidsilicon/ip/axis_width_converter/v1_0/<build-name>/src/` directory. 
    
## Parameters
There are four parameters for AXIS_WIDTH_CONVERTER core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter     |       Keyword      |           Value           |
    |-------|--------------------|--------------------|---------------------------|
    |   1.  |   CORE_IN_WIDTH    |   core_in_width    |  8,16,32,64,128,512,1024  |
    |   2.  |   CORE_OUT_WIDTH   |   core_out_width   |  8,16,32,64,128,512,1024  |
    |   3.  |   CORE_USER_WIDTH  |   core_user_width  |  1-4096                   |  
    |   4.  |   CORE_REVERSE     |   core_reverse     |  0/1                      |


To generate RTL with above parameters, run the following command:
```
python3 axis_width_converter_gen.py --core_in_width=1024 --core_out_width=32 --build-name=width_converter --build
```

## TCL File
This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axis_width_converter/v1_0/<build-name>/synth/` directory.


