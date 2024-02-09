
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= axil_eio_wrapper

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|EIO.vcd|$(OUT_DIR)/EIO.vcd|g" ./eio_tb.sv
	iverilog -g2012 ../src/*.v -o axil_eio ./*.sv
	vvp axil_eio
	-@mv axil_eio $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/EIO.vcd|EIO.vcd|g" ./eio_tb.sv

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__

