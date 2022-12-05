# AXI STREAM SWITCH Core Generation 
## Introduction

AXIS-SWITCH is an AXI Stream based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axis/start

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/axis_switch/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

## Parameters
These are the parameters for AXIS-SWITCH core along with their keyword and values: -

| Sr.No. |      Parameter             |       Keyword              |    Value      |
|--------|----------------------------|----------------------------|---------------|
|   1.   |   DATA_WIDTH               |     data_width             |    1 - 4096   |
|   2.   |   USER_WIDTH               |     user_width             |    1 - 4096   |
|   3.   |   S_COUNT                  |     s_count                |    1 - 16     |
|   4.   |   M_COUNT                  |     m_count                |    2 - 16     |
|   5.   |   S_ID_WIDTH               |     s_id_width             |    1 - 32     |
|   6.   |   M_DEST_WIDTH             |     m_dest_width           |    1 - 32     |
|   7.   |   M_REG_TYPE               |     m_reg_type             |    0 - 2      |
|   8.   |   S_REG_TYPE               |     s_reg_type             |    0 - 2      |
|   9.   |   ID_ENABLE                |     id_en                  |    0 / 1      |
|   10.  |   USER_ENABLE              |     user_en                |    0 / 1      |
|   11.  |   ARB_LSB_HIGH_PRIORITY    |     lsb_high_priority      |    0 / 1      |
|   12.  |   ARB_TYPE_ROUND_ROBIN     |     type_round_robin       |    0 / 1      |
|   13.  |   UPDATE_TID               |     tid                    |    0 / 1      |
|   14.  |   M_TOP                    |     m_top                  |    0 - 36     |
|   15.  |   M_BASE                   |     m_base                 |    0 - 36     |



To generate RTL with above parameters, run the following command:
```
python3 axis_switch_gen.py --data_width=7 --s_count=3 --build-name=switch --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axis_switch/v1_0/<build-name>/synth/` directory.


## References

https://github.com/alexforencich/verilog-axis/blob/master/rtl/axis_switch.v