# AXIL ETHERNET Core Generation

## Introduction

The AXIL ETHERNET core is an Ethernet IP Core generated from LiteEth core (used in LiteX designs).

It has the following features:

PHY
    MII, RMII 100Mbps PHYs.
    GMII / RGMII /1000BaseX 1Gbps PHYs.*

Core
    Configurable MAC (HW or SW interface)
    ARP / ICMP / UDP (HW or SW)*

Frontend
    Etherbone (AXI-Lite/Wishbone over UDP: Slave or Master support)*

* Supported by LiteEth but not yet supported in the IP Catalog.

More information and source code of the core can be found at: https://github.com/enjoy-digital/liteeth

## Architecture

AXIL ETHERNET has the following simplified architecture:

```
AXIL ETHERNET
└─── ethphy (LiteEthPHYMII)
│    └─── crg (LiteEthPHYMIICRG)
│    └─── tx (LiteEthPHYMIITX)
│    └─── rx (LiteEthPHYMIIRX)
│    └─── mdio (LiteEthPHYMDIO)
└─── ethmac (LiteEthMAC)
     └─── core (LiteEthMACCore)
     │    └─── tx_datapath (TXDatapath)
     │    └─── rx_datapath (RXDatapath)
     └─── interface (LiteEthMACWishboneInterface)
         └─── sram (LiteEthMACSRAM)
         │    └─── writer (LiteEthMACSRAMWriter))
         │    └─── reader (LiteEthMACSRAMReader)
         │    └─── ev (SharedIRQ)
         └─── sram_0* (SRAM)
         └─── sram_1* (SRAM)
         └─── sram_2* (SRAM)
         └─── sram_3* (SRAM)
         └─── decoder_0* (Decoder)
```

## Generator Script
This directory contains the generator script which generates the RTL to `rapidsilicon/ip/axil_eth/v1_0/<build-name>/src/` directory.

## Parameters
AXIL ETHERNET is a parametrizable core and the list/supported values of the available parameters can be
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
