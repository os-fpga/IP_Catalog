# AXI STREAM INTERCONNECT Core Generation 

## Introduction
AXIS-INTERCONNECT is AXI4-Stream based IP core.

## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axis_interconnect/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
User can configure AXIS_INTERCONNECT CORE using the following parameters:

| Sr. No.|      Parameter     |       Keyword      |          Value          |
|--------|--------------------|--------------------|-------------------------|
|   1.   |   S_COUNT          |   s_count          |    2-16                 |
|   2.   |   M_COUNT          |   m_count          |    2-16                 |
|   3.   |   DATA_WIDTH       |   data_width       |    1-4096               |
|   4.   |   LAST_ENABLE      |   last_en          |    0/1                  |  
|   5.   |   ID_ENABLE        |   id_en            |    0/1                  |
|   6.   |   ID_WIDTH         |   id_width         |    1-32                 |
|   7.   |   DEST_ENABLE      |   dest_en          |    0/1                  |
|   8.   |   DEST_WIDTH       |   dest_width       |    1-32                 |
|   9.   |   USER_ENABLE      |   user_en          |    0/1                  |
|   10.  |   USER_WIDTH       |   user_width       |    1-4096               |


To generate RTL with above parameters, run the following command:
```
python3 axis_interconnect_gen.py --m_count=7 --s_count=15 --data_width=32 --build-name=interconnect --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axis_interconnect/v1_0/<build-name>/synth/` directory.

## References

https://github.com/alexforencich/verilog-axis/blob/master/rtl/axis_crosspoint.v
