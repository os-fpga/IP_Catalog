# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= axis_uart

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|test_uart_rx.lxt|$(OUT_DIR)/test_uart_rx.lxt|g" ./test_uart_rx.v
	@sed -i "s|test_uart_tx.lxt|$(OUT_DIR)/test_uart_tx.lxt|g" ./test_uart_tx.v
	python3 test_uart_tx.py
	-@mv test_uart_tx.vvp $(OUT_DIR)
	@echo "TEST 1 PASSED"
	python3 test_uart_rx.py
	-@mv test_uart_rx.vvp $(OUT_DIR)
	@echo "TEST 2 PASSED"
	@sed -i "s|$(OUT_DIR)/test_uart_rx.lxt|test_uart_rx.lxt|g" ./test_uart_rx.v
	@sed -i "s|$(OUT_DIR)/test_uart_tx.lxt|test_uart_tx.lxt|g" ./test_uart_tx.v
clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__