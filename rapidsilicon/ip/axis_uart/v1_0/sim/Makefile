# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= axis_uart

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|test_uart_rx.lxt|$(OUT_DIR)/test_uart_rx.lxt|g" ./test_uart_rx.v
	@sed -i "s|test_uart_tx.lxt|$(OUT_DIR)/test_uart_tx.lxt|g" ./test_uart_tx.v
	-@python3 test_uart_tx.py && echo "TEST TX PASSED" || echo "TEST TX FAILED"
	-@mv test_uart_tx.vvp $(OUT_DIR)
	-@python3 test_uart_rx.py && echo "TEST RX PASSED" || echo "TEST RX FAILED"
	-@mv test_uart_rx.vvp $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/test_uart_rx.lxt|test_uart_rx.lxt|g" ./test_uart_rx.v
	@sed -i "s|$(OUT_DIR)/test_uart_tx.lxt|test_uart_tx.lxt|g" ./test_uart_tx.v
clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__