
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= OCLA

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|ocla.vcd|$(OUT_DIR)/ocla.vcd|g" ./axil_ocla_wrapper_tb.sv
	iverilog -g2012 -o axil_ocla ./axil_ocla_wrapper_tb.sv ../src/*.sv
	vvp axil_ocla
	-@mv axil_ocla $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/ocla.vcd|ocla.vcd|g" ./axil_ocla_wrapper_tb.sv

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__
