# LiteSPI Core Generation

## Introduction
LiteEth is a SPI Flash-MMAP IP core initially design for use in LiteX systems.

## Generator Script
This directory contains the generator script which generates the RTL to `rapidsilicon/ip/axil_eth/v1_0/<build-name>/src/` directory.

## Parameters
LiteEth is a parametrizable core and the list/supported values of the available parameters can be
obtain with `./axil_eth_gen.py --help` command:

```
  --core-phy                          Ethernet PHY (mii or model).
  --core-ntxslots                     Number of TX Slots (1, 2 or 4).
  --core-nrxslots                     Number of RX Slots (1, 2 or 4).
  --core-bus-endianness {big,little}  Bus Endianness (big, little).
```

To generate RTL with above parameters, run the following command:
```
python3 axil_eth_gen.py --core-phy=mii --core-bus-endianness=big --build
```

## TCL File
This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/axil_eth/v1_0/<build-name>/synth/` directory.
