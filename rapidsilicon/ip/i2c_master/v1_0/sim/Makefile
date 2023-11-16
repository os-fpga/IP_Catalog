# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= i2c_master

OUT_DIR ?=3

all:
	@sed -i "s|test_i2c_master_axil.lxt|$(OUT_DIR)/test_i2c_master_axil.lxt|g" ./test_i2c_master_axil.v
	python3 test_i2c.py
	@echo "TEST 1 PASSED"
	python3 test_i2c_master_axil.py
	@mv test_i2c_master_axil.vvp $(OUT_DIR)
	@mv test_i2c.vcd $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/test_i2c_master_axil.lxt|test_i2c_master_axil.lxt|g" ./test_i2c_master_axil.v
	@echo "TEST 2 PASSED"
clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__