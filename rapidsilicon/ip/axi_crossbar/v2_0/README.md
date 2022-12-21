# AXI-CROSSBAR Core Generation 
## Introduction
AXI-CROSSBAR is AXI4 based IP core which support multi clock for all master and slave interface.


## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi_crossbar/v2_0/<build-name>/src` directory and generates its wrapper in the same directory. 

## Parameters
User can configure AXI_CROSSBAR CORE using following parameters:

| Sr.No.|     Parameter      |      Keyword       |    Value             |
|-------|--------------------|--------------------|----------------------|
|   1.  |   S_COUNT          |   s_count          |  1-16                |
|   2.  |   M_COUNT          |   m_count          |  2-16                |
|   3.  |   DATA_WIDTH       |   data_width       |  8,16,32,64,128,256  |
|   4.  |   ADDR_WIDTH       |   addr_width       |  32,64               |
|   5.  |   S_ID_WIDTH       |   s_id_width       |  1-8                 |
|   6.  |   AWUSER_ENABLE    |   aw_user_en       |  0/1                 |
|   7.  |   AWUSER_WIDTH     |   aw_user_width    |  1-1024              |
|   8.  |   WUSER_ENABLE     |   w_user_en        |  0/1                 |
|   9.  |   WUSER_WIDTH      |   w_user_width     |  1-1024              |
|   10. |   BUSER_ENABLE     |   b_user_en        |  0/1                 |
|   11. |   BUSER_WIDTH      |   b_user_width     |  1-1024              |
|   12. |   ARUSER_ENABLE    |   ar_user_en       |  0/1                 |
|   13. |   ARUSER_WIDTH     |   ar_user_width    |  1-1024              |
|   14. |   RUSER_ENABLE     |   r_user_en        |  0/1                 |
|   15. |   RUSER_WIDTH      |   r_user_width     |  1-1024              |
|   16. |   SYNC_STAGES      |   sync_stages      |  2-8                 |
|   17. |   FIFO_DEPTH       |   fifo_depth       |  3-8                 |


To generate RTL with above parameters, run the following command:
```
python3 axi_crossbar_gen.py --data_width=32 --addr_width=32 --s_count=7 --m_count=4 --build-name=crossbar_wrapper --build
```

## TCL File
This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi_crossbar/v2_0/<build-name>/synth` directory.


## References
https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_crossbar.v
