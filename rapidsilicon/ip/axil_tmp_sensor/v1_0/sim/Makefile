# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

MODULE_NAME ?= axil_tmp_sensor_wrapper

OUT_DIR ?= $(PWD)

all:
	@sed -i "s|temp_sensor.vcd|$(OUT_DIR)/temp_sensor.vcd|g" ./SOC_FPGA_TEMPERATURE_tb.v
	iverilog -g2012 ../src/*.v -o temp_sensor ./*.v
	vvp temp_sensor
	-@mv temp_sensor $(OUT_DIR)
	@sed -i "s|$(OUT_DIR)/temp_sensor.vcd|temp_sensor.vcd|g" ./SOC_FPGA_TEMPERATURE_tb.v

clean:
	@rm -rf __pycache__ *.lxt *.vvp *.vcd rapidsilicon ../litex_wrapper/__pycache__ temp_sensor
