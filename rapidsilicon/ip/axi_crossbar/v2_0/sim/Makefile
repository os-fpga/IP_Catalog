# Copyright (c) 2020 Alex Forencich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

TOPLEVEL_LANG = verilog

SIM ?= verilator
WAVES ?= 1

OUT_DIR ?= $(PWD)

SIM_BUILD = $(OUT_DIR)


COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

export PARAM_S_COUNT ?= 4
export PARAM_M_COUNT ?= 4
export PARAM_AXI4FULL ?= 1

DUT      = axi_crossbar
MODULE_NAME ?= $(DUT)_wrapper
TOPLEVEL = $(MODULE_NAME)
MODULE   = test_$(DUT)

VERILOG_SOURCES += ../src/*.v

ifeq ($(SIM), icarus)
	PLUSARGS += -fst

	ifeq ($(WAVES), 1)
		VERILOG_SOURCES += iverilog_dump.v
		COMPILE_ARGS += -s iverilog_dump
	endif
else ifeq ($(SIM), verilator)
	COMPILE_ARGS += -Wno-SELRANGE -Wno-WIDTH -Wno-lint -Wno-fatal --timing

	ifeq ($(WAVES), 1)
		COMPILE_ARGS += --trace-fst
	endif
endif



EXTRA_ARGS += --coverage
#EXTRA_ARGS += --coverage-toggle
#EXTRA_ARGS += --coverage-line
#EXTRA_ARGS += --coverage-user

include $(shell cocotb-config --makefiles)/Makefile.sim

#$(WRAPPER).v: ../../rtl/$(DUT)_wrap.py
#	$< -p $(PARAM_S_COUNT) $(PARAM_M_COUNT)

iverilog_dump.v:
	echo 'module iverilog_dump();' > $@
	echo 'initial begin' >> $@
	echo '    $$dumpfile("$(SIM_BUILD)/$(TOPLEVEL).fst");' >> $@
	echo '    $$dumpvars(0, $(TOPLEVEL));' >> $@
	echo 'end' >> $@
	echo 'endmodule' >> $@

clear::
	@rm -rf iverilog_dump.v
	@rm -rf dump.fst $(TOPLEVEL).fst
	@rm -rf coverage
	@rm -rf coverage.dat
	@rm -rf coverage.info
	@rm -rf dump.vcd
	@rm -rf results.xml
	@rm -rf __pycache__
	
