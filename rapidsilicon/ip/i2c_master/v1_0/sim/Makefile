# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
DUT = i2c_master

$(shell ../$(DUT)_gen.py --build)

all:
	python3 test_i2c.py
	@echo "TEST 1 PASSED"
	python3 test_i2c_master_axil.py
	@echo "TEST 2 PASSED"
clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__