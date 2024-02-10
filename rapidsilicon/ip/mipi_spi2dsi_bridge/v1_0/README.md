# MIPI SPI2DSI Bridge IP Core Generation 
## Introduction

MIPI SPI2DSI Bridge is a MIPI DSI Transmitter, SPI slave interface drives the data to be transmitted on the transmitter

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/mipi_spi2dsi_bridge/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory. 

## Parameters
User can configure MIPI SPI2DSI Bridge CORE using following parameters:

To generate RTL with above parameters, run the following command:
```
python3 mipi_spi2dsi_bridge_gen.py  --build-name=mipi_spi2dsi_bridge_wrap --build
```

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/mipi_spi2dsi_bridge/v1_0/<build-name>/synth/` directory.



