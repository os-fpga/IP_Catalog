
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= ocla_wrapper

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|ahb_sram.vcd|$(OUT_DIR)/ahb_sram.vcd|g" ./*.v
	iverilog -g2012 ./ahb_slave_if_tb.v ./../src/* -o ahb_sram  && vvp ./ahb_sram

	-@mv ahb_sram $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/ahb_sram.vcd|ahb_sram.vcd|g" ./*.v

clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd ahb_sram rapidsilicon ../litex_wrapper/__pycache__

