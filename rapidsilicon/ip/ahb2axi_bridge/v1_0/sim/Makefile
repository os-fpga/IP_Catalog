
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
MODULE_NAME ?= ocla_wrapper

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|ahb2axi.vcd|$(OUT_DIR)/ahb2axi.vcd|g" ./*.v
	verilator --timing --Wno-fatal --main --exe --build --trace ./../src/*.sv ./axi_ram.v ./ahb_slave_if_tb.v
	make -j -C obj_dir/ -f Vahb2axi4.mk Vahb2axi4
	obj_dir/Vahb2axi4

#	-@mv ahb2axi $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/ahb2axi.vcd|ahb2axi.vcd|g" ./*.v

clear:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd ahb2axi rapidsilicon ../litex_wrapper/__pycache__

