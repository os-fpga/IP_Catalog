# AXI STREAM BROADCAST Core Generation 
## Introduction

AXIS-BROADCAST is AXI4-Stream based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axis/start

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/axis_broadcast/v1_0/<build-name>/src` directory and generates its wrapper in the same directory. 

## Parameters
User can configure AXIS_BROADCAST CORE using following parameters:

| Sr.No.|      Parameter   |       Keyword      |    Value    |
|-------|------------------|--------------------|-------------|
|   1.  |   M_COUNT        |    m_count         |   2-16      |
|   2.  |   DATA_WIDTH     |    data_width      |   1-4096    |
|   3.  |   LAST_ENABLE    |    last_en         |   0/1       |
|   4.  |   ID_ENABLE      |    id_en           |   0/1       |
|   5.  |   ID_WIDTH       |    id_width        |   1-32      |
|   6.  |   DEST_ENABLE    |    dest_en         |   0/1       |
|   7.  |   DEST_WIDTH     |    dest_width      |   1-32      |
|   8.  |   USER_ENABLE    |    user_en         |   0/1       |
|   9.  |   USER_WIDTH     |    user_width      |   1-4096    |


To generate RTL with above parameters, run the following command:
```
python3 axis_broadcast_gen.py --data_width=1024 --m_count=8 --build-name=broadcast --build
```

## TCL File
This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axis_broadcast/v1_0/<build-name>/synth` directory.


## References
https://github.com/alexforencich/verilog-axis/blob/master/rtl/axis_broadcast.v