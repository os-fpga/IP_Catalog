
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= ocla_wrapper

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|ocla.vcd|$(OUT_DIR)/ocla.vcd|g" ./*.sv
	iverilog -o ocla_top -g2012  ../src/* ./ocla_debug_tb.sv ./ocla_wrapper_v1_0.sv && vvp ./ocla_top
	-@mv ocla_top $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/ocla.vcd|ocla.vcd|g" ./*.sv

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__

