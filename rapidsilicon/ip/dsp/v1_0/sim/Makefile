# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

DUT = dsp

OUT_DIR ?= 3

all:
	@sed -i "s|dsp.vcd|$(OUT_DIR)/reset.vcd|g" ./dsp_test.v
	iverilog -g2012 -o dsp ../src/*.v ./dsp_test.v ./dsp_sim.v
	vvp dsp
	@sed -i "s|$(OUT_DIR)/reset.vcd|dsp.vcd|g" ./dsp_test.v

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__ dsp dsp_tests_unsigned.log