# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

MODULE_NAME ?= on_chip_memory

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|O_SERDES.vcd|$(OUT_DIR)/O_SERDES.vcd|g" ./testbench.v 
	iverilog -g2012 -o io ./io_configurator_v1_0.v ./testbench.v ./BOOT_CLOCK.v ./O_BUFT.v ./O_DELAY.v ./PLL.v ./O_SERDES.v
	vvp io
	-@mv io $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/O_SERDES.vcd|O_SERDES.vcd|g" ./testbench.v

clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__ io