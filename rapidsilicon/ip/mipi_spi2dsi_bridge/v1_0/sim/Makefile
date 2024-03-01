# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= mipi_spi2dsi_bridge

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|mipi_dsi.vcd|$(OUT_DIR)/mipi_dsi.vcd|g" ./tb_spi_bridge.v
	iverilog -g2012 -o mipi_dsi ./tb_spi_bridge.v ./PLL_RS.v ../src/*.v
	vvp mipi_dsi
	-@mv mipi_dsi $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/mipi_dsi.vcd|mipi_dsi.vcd|g" ./tb_spi_bridge.v

clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__