# AXIS PIPELINE REGISTER Core Generation 

## Introduction
AXIS-PIPELINE-REGISTER is AXI4-Stream based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axis/start

## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axis_pipeline_register/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

## Parameters
There are ten parameters for AXIS_PIPELINE_REGISTER core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter     |       Keyword      |    Value     |
    |-------|--------------------|--------------------|--------------|
    |   1.  |   DATA_WIDTH       |   data_width       |    1-4096    |
    |   2.  |   LAST_ENABLE      |   last_en          |    0/1       |  
    |   3.  |   ID_ENABLE        |   id_en            |    0/1       |
    |   4.  |   ID_WIDTH         |   id_width         |    1-32      |
    |   5.  |   DEST_ENABLE      |   dest_en          |    0/1       |
    |   6.  |   DEST_WIDTH       |   dest_width       |    1-32      |
    |   7.  |   USER_ENABLE      |   user_en          |    0/1       |
    |   8.  |   USER_WIDTH       |   user_width       |    1-4096    |
    |   9.  |   REG_TYPE         |   reg_type         |    0-2       |
    |   10. |   LENGTH           |   length           |    0-5       |


To generate RTL with above parameters, run the following command:
```
python3 axis_pipeline_register_gen.py --data_width=32 --build-name=reg --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axis_pipeline_register/v1_0/<build-name>/synth/` directory.

## References

https://github.com/alexforencich/verilog-axis/blob/master/rtl/axis_pipeline_register.v
