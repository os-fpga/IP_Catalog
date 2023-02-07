# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
DUT = axis_uart

all:
	python3 test_uart_tx.py
	@echo "TEST 1 PASSED"
	python3 test_uart_rx.py
	@echo "TEST 2 PASSED"
clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__