
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= axil_eio_wrapper

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|ddr.vcd|$(OUT_DIR)/dump.vcd|g" ./tb_ddr_sdram_ctrl.v
	iverilog -g2012 ./tb_ddr_sdram_ctrl.v ./micron_ddr_sdram_model.v ./axi_self_test_master.v ./../src/*.v -o ddr
	vvp ddr
	-@mv ddr $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/dump.vcd|ddr.vcd|g" ./tb_ddr_sdram_ctrl.v

clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__

