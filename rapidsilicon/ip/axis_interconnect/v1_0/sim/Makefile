# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
DUT = axis_interconnect

all:
	python3 test_axis_crosspoint_4x4.py
	@echo "TEST 1 PASSED"
	python3 test_axis_crosspoint_4x4_64.py
	@echo "TEST 2 PASSED"
clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__