# AHB to AXI4 Brigde IP
## Introduction
AHB-to-AXI4 Bridge IP

For more information, visit: https://github.com/westerndigitalcorporation/swerv_eh1/blob/master/design/lib/axi4_to_ahb.sv

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/ahb2axi_bridge/v1_0/<build-name>/src` directory and generates its wrapper in the same directory. 

## Parameters
User can configure ahb2axi_bridge CORE using following parameters:

| Sr.No.|      Parameter       |         Keyword        |         Value         |
|-------|----------------------|------------------------|-----------------------|
|   1.  |   data_width         |    data_width          |   32-64               |
|   2.  |   addr_width         |    addr_width          |   6-32                |
|   3.  |   id_width           |    id_width            |   1-32                |



To generate RTL with above parameters, run the following command:
```
python3 ahb2axi_bridge_gen.py --data_width=32 --addr_width=8 --build-name=wrapper --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/ahb2axi_bridge/v1_0/<build-name>/synth` directory.


## References
https://github.com/westerndigitalcorporation/swerv_eh1/blob/master/design/lib/axi4_to_ahb.sv
