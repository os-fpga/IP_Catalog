# Simulation

The simulation create a LiteX SoC and integrated the generated `axil_spi.v` core to it as a MMAPed
peripheral. The SPI Flash is then accessible and initial content can be verified.


Run simulation:
```
./test_axil_spi.py
```

User can then interfact with the LiteX BIOS that the SPI Flash is present and accessible:
```
litex> mem_list
Available memory regions:
ROM       0x00000000 0x10000
SRAM      0x10000000 0x2000
AXIL_SPI  0x03000000 0x1000
CSR       0xf0000000 0x10000

litex> mem_read 0x03000000 32
Memory dump:
0x03000000  00 00 00 00 01 00 00 00 02 00 00 00 03 00 00 00  ................
0x03000010  04 00 00 00 05 00 00 00 06 00 00 00 07 00 00 00  ................
```

The initial content that can be seen is the content of `axil_spi_mem.init` and can be modified to
simulate real SPI Flash content.
