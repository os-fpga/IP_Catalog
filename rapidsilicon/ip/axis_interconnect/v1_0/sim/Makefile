# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= axis_interconnect

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|test_axis_crosspoint_4x4.lxt|$(OUT_DIR)/test_axis_crosspoint_4x4.lxt|g" ./test_axis_crosspoint_4x4.v
	-@python3 test_axis_crosspoint_4x4.py && echo "TEST PASSED" || echo "TEST FAILED"
	-@mv test_axis_crosspoint_4x4.vvp $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/test_axis_crosspoint_4x4.lxt|test_axis_crosspoint_4x4.lxt|g" ./test_axis_crosspoint_4x4.v
clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__