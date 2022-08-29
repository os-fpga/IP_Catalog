# AXI-REGISTER Core Generation 
## Introduction

AXI-REGISTER is AXI4 based IP core.

For more information, visit: http://alexforencich.com/wiki/en/verilog/axi/start

## Generator Script
This directory contains the generator script which places the RTL to `/ip_build/rapidsilicon/ip/axi_register/v1_0/<build_name>/src` directory and generates its wrapper in the same directory. 

## Parameters
There are thirteen parameters for AXI-REGISTER core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter       |       Keyword      |             Value              |
    |-------|----------------------|--------------------|--------------------------------|
    |   1.  |   DATA_WIDTH         |    data_width      |   8,16,32,64,128,256,512,1024  |
    |   2.  |   ADDRESS_WIDTH      |    addr_width      |   1 - 64                       |
    |   3.  |   ID_WIDTH           |    id_width        |   1 - 32                       |
    |   4.  |   AWUSER_WIDTH       |    aw_user_width   |   1 - 1024                     |
    |   5.  |   WUSER_WIDTH        |    w_user_width    |   1 - 1024                     |
    |   6.  |   BUSER_WIDTH        |    b_user_width    |   1 - 1024                     |
    |   7.  |   ARUSER_WIDTH       |    ar_user_width   |   1 - 1024                     |
    |   8.  |   RUSER_WIDTH        |    r_user_width    |   1 - 1024                     |
    |   9.  |   AW_REG_TYPE        |    aw_reg_type     |   0, 1, 2                      |
    |   10. |   W_REG_TYPE         |    w_reg_type      |   0, 1, 2                      |
    |   11. |   B_REG_TYPE         |    b_reg_type      |   0, 1, 2                      |
    |   12. |   AR_REG_TYPE        |    ar_reg_type     |   0, 1, 2                      |
    |   13. |   R_REG_TYPE         |    r_reg_type      |   0, 1, 2                      |
    


To generate RTL with above parameters, run the following command:
```
python3 axi_register_gen.py --data_width=64 --add_width=32 --build_name=register --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `/ip_build/rapidsilicon/ip/axi_register/v1_0/<build_name>/synth` directory.


## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_register.v