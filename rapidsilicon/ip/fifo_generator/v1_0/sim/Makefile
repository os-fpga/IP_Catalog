# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

DUT = fifo_generator

OUT_DIR ?= 3

all:
	@sed -i "s|fifo.vcd|$(OUT_DIR)/fifo.vcd|g" ./testbench.v
	iverilog ../src/*.v -o fifo ../sim/*.v
	vvp fifo
	@mv fifo $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/fifo.vcd|fifo.vcd|g" ./testbench.v

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__ fifo