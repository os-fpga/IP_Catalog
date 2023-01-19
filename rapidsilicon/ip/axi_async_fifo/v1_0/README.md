# AXI FIFO Core Generation 

## Introduction
AXI-ASYNC-FIFO is AXI4 based IP core.

## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axi_async_fifo/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 
    
## Parameters
User can configure axi_async_fifo CORE using following parameters:

| Sr.No.|      Parameter     |       Keyword      |          Value          |
|-------|--------------------|--------------------|-------------------------|
|   1.  |   DATA_WIDTH       |   data_width       |  32,64,128,256,512,1024 |
|   2.  |   ADDR_WIDTH       |   addr_width       |  1-64                   |
|   3.  |   ID_WIDTH         |   id_width         |  1-32                   |
|   4.  |   FIFO DEPTH       |   fifo_depth       |  8-8192                 |



To generate RTL with above parameters, run the following command:
```
python3 axi_async_fifo_gen.py --data_width=32 --addr_width=64 --build-name=fifo --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axi_async_fifo/v1_0/<build-name>/synth/` directory.
