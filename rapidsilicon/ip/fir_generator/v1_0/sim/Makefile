# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

MODULE_NAME ?= fir_generator

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|fir.vcd|$(OUT_DIR)/fir.vcd|g" ./testbench.v
	iverilog -g2012 ../src/*.v -o fir ../sim/*.v
	vvp fir
	@mv fir $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/fir.vcd|fir.vcd|g" ./testbench.v

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__ fir