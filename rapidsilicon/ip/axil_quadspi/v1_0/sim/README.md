# Simulation

The simulation creates a LiteX SoC and integrates the generated `axil_quadspi.v` core as a memory-mapped peripheral. This allows the SPI flash to be accessed and its initial content to be verified.

To run the simulation, use the following command:
```
./test_axil_quadspi.py
```

With the simulation running, you can interact with the firmware to verify that the SPI flash is present and accessible:
```
axil_quadspi> test_mmap
SPI Flash Dump:
0x00000000: 0x00010203
0x00000004: 0x04050607
0x00000008: 0x08090a0b
0x0000000c: 0x0c0d0e0f
0x00000010: 0x00000000
0x00000014: 0x00000000
0x00000018: 0x00000000
0x0000001c: 0x00000000
axil_quadspi> test_program <- Program SPIFlash at 0x00000000/0x00000004.
Writing 00000007
axil_quadspi> test_mmap
SPI Flash Dump:
0x00000000: 0xa55aa55a <- Updated data.
0x00000004: 0x5aa55aa5 <- Updated data.
0x00000008: 0x08090a0b
0x0000000c: 0x0c0d0e0f
0x00000010: 0x00000000
0x00000014: 0x00000000
0x00000018: 0x00000000
0x0000001c: 0x00000000
axil_quadspi>
```

The initial content is read from the `axil_quadspi_mem.init` file, and can be modified to simulate real SPI flash content.
