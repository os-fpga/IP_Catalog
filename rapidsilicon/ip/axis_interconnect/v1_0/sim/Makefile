# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= axis_interconnect

OUT_DIR ?=3

all:
	@sed -i "s|test_axis_crosspoint_4x4.lxt|$(OUT_DIR)/test_axis_crosspoint_4x4.lxt|g" ./test_axis_crosspoint_4x4.v
	@sed -i "s|test_axis_crosspoint_4x4_64.lxt|$(OUT_DIR)/test_axis_crosspoint_4x4_64.lxt|g" ./test_axis_crosspoint_4x4_64.v
	python3 test_axis_crosspoint_4x4.py
	@mv test_axis_crosspoint_4x4.vvp $(OUT_DIR)
	@echo "TEST 1 PASSED"
	python3 test_axis_crosspoint_4x4_64.py
	@mv test_axis_crosspoint_4x4_64.vvp $(OUT_DIR)
	@echo "TEST 2 PASSED"
	@sed -i "s|$(OUT_DIR)/test_axis_crosspoint_4x4.lxt|test_axis_crosspoint_4x4.lxt|g" ./test_axis_crosspoint_4x4.v
	@sed -i "s|$(OUT_DIR)/test_axis_crosspoint_4x4_64.lxt|test_axis_crosspoint_4x4_64.lxt|g" ./test_axis_crosspoint_4x4_64.v
clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__