# AXI LITE GPIO Core Generation 
## Introduction

AXI LITE GPIO is AXI4-Lite based IP core.


## Generator Script

This directory contains the generator script which places the RTL to `rapidsilicon/ip/axil_gpio/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

## Parameters
User can configure AXI_LITE_GPIO CORE using following parameters:

| Sr.No.|     Parameter     |      Keyword      |    Value    |
|-------|-------------------|-------------------|-------------|
|   1.  |   DATA_WIDTH      |   data_width      |   8,16,32   |
|   2.  |   ADDRESS_WIDTH   |   addr_width      |   8-16      |


To generate RTL with above parameters, run the following command:
```
python3 axil_gpio_gen.py --data_width=16 --addr_width=8 --build-name=gpio --build
```

## TCL File
This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axil_gpio/v1_0/<build-name>/synth/` directory.

## References

https://github.com/smartfoxdata/axi4lite_gpio/tree/master/rtl
