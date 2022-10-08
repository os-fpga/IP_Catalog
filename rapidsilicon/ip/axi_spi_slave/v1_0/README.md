# AXI SPI SLAVE Core Generation 

## Introduction
AXI-SPI-SLAVE is AXI4 based IP core.


## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi_spi_slave/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
There are five parameters for AXI_SPI_SLAVE core. These parameters, their keywords and values are given below:

    | Sr.No.|      Parameter        |       Keyword      |      Value     |
    |-------|-----------------------|--------------------|----------------|
    |   1.  |   AXI_ADDR_WIDTH      |   addr_width       |    8,16,32     |
    |   2.  |   AXI_DATA_WIDTH      |   data_width       |    8,16,32,64  |
    |   3.  |   AXI_USER_WIDTH      |   user_width       |    1-8         |
    |   4.  |   AXI_ID_WIDTH        |   id_width         |    1-16        |
    |   5.  |   DUMMY_CYCLES        |   dummy_cycles     |    16,32       |


To generate RTL with above parameters, run the following command:
```
python3 axi_spi_slave_gen.py --data_width=32 --addr_width=16 --build-name=spi --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi_spi_slave/v1_0/<build-name>/synth/` directory.

## References

https://github.com/pulp-platform/axi_spi_slave
