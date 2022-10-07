# AXI VEXRISCV Core Generation 
## Introduction

AXI-VEXRISCV is AXI4 based IP core.

For more information, visit: https://github.com/SpinalHDL/VexRiscv#description

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/vexriscv/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

To generate RTL wrapper, run the following command:
```
python3 vexriscv_gen.py --build-name=vexriscv_wrap --build-dir=./ --build
```

## TCL File
This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/vexriscv/v1_0/<build-name>/synth/` directory.


## References
https://github.com/SpinalHDL/VexRiscv