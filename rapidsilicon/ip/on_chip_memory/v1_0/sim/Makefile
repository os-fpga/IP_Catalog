# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

MODULE_NAME ?= on_chip_memory

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|ocm.vcd|$(OUT_DIR)/ocm.vcd|g" ./testbench.v
	iverilog -g2012 -o ocm ./on_chip_memory_v1_0.v ./testbench.v ./TDP_RAM36K.v
	vvp ocm
	-@mv ocm $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/ocm.vcd|ocm.vcd|g" ./testbench.v

clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__ ocm