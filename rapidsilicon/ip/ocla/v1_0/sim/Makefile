
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= ocla_wrapper

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|ocla.vcd|$(OUT_DIR)/ocla.vcd|g" ./*.sv
	iverilog -o ocla_top1 -g2012  ../src/* ./ocla_debug_tb.sv ./ocla_top.sv && vvp ./ocla_top1
	-@mv ocla_top1 $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/ocla.vcd|ocla.vcd|g" ./*.sv

clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd ocla_top1 rapidsilicon ../litex_wrapper/__pycache__

