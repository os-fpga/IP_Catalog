# AXI SPI MASTER Core Generation 

## Introduction
AXI-SPI-MASTER is AXI4 based IP core.


## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi_spi_master/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
There are six parameters for AXI_SPI_MASTER core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter        |       Keyword      |      Value     |
    |-------|-----------------------|--------------------|----------------|
    |   1.  |   AXI4_ADDRESS_WIDTH  |   addr_width       |    8,16,32     |
    |   2.  |   AXI4_RDATA_WIDTH    |   data_width       |    8,16,32     |
    |   3.  |   AXI4_WDATA_WIDTH    |   data_width       |    8,16,32     |
    |   4.  |   AXI4_USER_WIDTH     |   user_width       |    1-4         |
    |   5.  |   AXI4_ID_WIDTH       |   id_width         |    1-16        |
    |   6.  |   BUFFER_DEPTH        |   buffer_depth     |    8,16        |


To generate RTL with above parameters, run the following command:
```
python3 axi_spi_master_gen.py --data_width=32 --addr_width=16 --build-name=spi --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi_spi_master/v1_0/<build-name>/synth/` directory.

## References

https://github.com/pulp-platform/axi_spi_master
