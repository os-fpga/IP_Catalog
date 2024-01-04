# Simulation

The simulation creates a LiteX SoC and integrates the generated axil_ethernet.v core as a memory-mapped peripheral. This allows the Ethernet MAC to be accessed and simple packet transmission/reception to be tested.


To run the simulation, use the following command:
```
make OUT_DIR=$(PWD) MODULE_NAME=<name_of_generated_IP_module>
```

With the simulation running, you can interact with the firmware to verify that the Ethernet core is working properly. A simple TX/RX loopback test is provided, which allows you to generate a TX packet and receive it back on the RX (through a loopback at the PHY level):

```
axil_ethernet> test_loopback
..........
RX Slot: 0, Len: 64, Data: 0x01 0x02 0x03 0x04 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
```
For more information on LiteEth CPU control, see the following resources:
- The bare-metal libliteeth library: https://github.com/enjoy-digital/litex/tree/master/litex/soc/software/libliteeth
- The linux driver: https://github.com/torvalds/linux/blob/0326074ff4652329f2a1a9c8685104576bd8d131/drivers/net/ethernet/litex/litex_liteeth.c

