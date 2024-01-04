# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= reset_release

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|reset.vcd|$(OUT_DIR)/reset.vcd|g" ./testbench.v
	iverilog -g2012 -o res_rel ./testbench.v ../src/*.v
	vvp res_rel
	-@mv res_rel $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/reset.vcd|reset.vcd|g" ./testbench.v

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__