
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= axil_eio

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|eio.vcd|$(OUT_DIR)/eio.vcd|g" ./eio_tb.sv
	iverilog -g2012 -o axil_eio ./eio_tb.sv ../src/*.v
	vvp axil_eio
	-@mv axil_eio $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/axil_eio.vcd|axil_eio.vcd|g" ./eio_tb.v

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__
