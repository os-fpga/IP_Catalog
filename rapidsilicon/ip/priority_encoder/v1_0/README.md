# PRIORITY_ENCODER Core Generation 
## Introduction

PRIORITY_ENCODER is an IP core for Raptor toolchain.

For more information, visit: http://alexforencich.com/wiki/en/verilog/uart/start

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/priority_encoder/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

## Parameters
User can configure PRIORITY_ENCODER CORE using following parameters:

| Sr.No.|        Parameter       |        Keyword         |    Value   |
|-------|------------------------|------------------------|------------|
|   1.  |   WIDTH                |    width               |    2 - 8   |
|   2.  |   LSB_HIGH_PRIORITY    |    lsb_high_priority   |    0/1     |



To generate RTL with above parameters, run the following command:
```
python3 priority_encoder_gen.py --width=7 --build-name=encoder --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/priority_encoder/v1_0/<build-name>/synth/` directory.


## References

https://github.com/alexforencich/verilog-axi/blob/master/rtl/priority_encoder.v