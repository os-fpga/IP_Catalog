# LiteSPI Core Generation

## Introduction
LiteSPI is a SPI Flash-MMAP IP core initially design for use in LiteX systems.

## Generator Script
This directory contains the generator script which generates the RTL to `rapidsilicon/ip/litespi/v1_0/<build-name>/src/` directory.

## Parameters
LiteSPI is a parametrizable core and the list/supported values of the available parameters can be
obtain with `./litespi_gen.py --help` command:

```
  --core-module                       SPI Flash Module.
  --core-mode           {x1,x4}       SPI Mode.
  --core-rate           {1:1,1:2}     SPI Flash Core rate.
  --core-divisor        range(1, 256) SPI Clk Divisor.
  --core-bus-endianness {big,little}  Bus Endianness (big, little).
```

To generate RTL with above parameters, run the following command:
```
python3 litespi_gen.py --core-module=S25FL128L --core-mode=x1 --core-rate=1:1 --core-divisor=1 --core-bus-endianness=big --build
```

## TCL File
This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/litespi/v1_0/<build-name>/synth/` directory.
