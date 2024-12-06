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

SIM ?= icarus
WAVES ?= 1

OUT_DIR ?= $(PWD)

SIM_BUILD = $(OUT_DIR)
POST_SYNTH_SIM ?= 0


COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

DUT      = axi_register
MODULE_NAME ?= $(DUT)_wrapper
TOPLEVEL = $(MODULE_NAME)
MODULE   = test_$(DUT)


Raptor_PATH := $(shell dirname $(shell which raptor ))

FOLDER_PATH = ./../../../../../../../../../ # /path/to/project

# Dynamically fetch the name of the folder (first one in this case)
FOLDER_NAME = $(shell find $(FOLDER_PATH) -maxdepth 1 -type d -name "project*" | xargs -n 1 basename | head -n 1)

#@echo "The folder name is: $(FOLDER_NAME)"

ifeq ($(POST_SYNTH_SIM), 0)
	VERILOG_SOURCES += ./../src*.v
else ifeq ($(POST_SYNTH_SIM), 1)
	VERILOG_SOURCES += $(Raptor_PATH)/../share/yosys/rapidsilicon/genesis3/FPGA_PRIMITIVES_MODELS/sim_models/verilog/*.v
	VERILOG_SOURCES += ./../../../../../../../synth_1_1/synthesis/$(FOLDER_NAME)_post_synth.v
endif

# module parameters
export PARAM_DATA_WIDTH ?= 32
export PARAM_ADDR_WIDTH ?= 16
export PARAM_STRB_WIDTH ?= $(shell expr $(PARAM_DATA_WIDTH) / 8 )
export PARAM_ID_WIDTH ?= 8
export PARAM_AWUSER_ENABLE ?= 0
export PARAM_AWUSER_WIDTH ?= 1
export PARAM_WUSER_ENABLE ?= 0
export PARAM_WUSER_WIDTH ?= 1
export PARAM_BUSER_ENABLE ?= 0
export PARAM_BUSER_WIDTH ?= 1
export PARAM_ARUSER_ENABLE ?= 0
export PARAM_ARUSER_WIDTH ?= 1
export PARAM_RUSER_ENABLE ?= 0
export PARAM_RUSER_WIDTH ?= 1
export PARAM_AW_REG_TYPE ?= $(REG_TYPE)
export PARAM_W_REG_TYPE ?= $(REG_TYPE)
export PARAM_B_REG_TYPE ?= $(REG_TYPE)
export PARAM_AR_REG_TYPE ?= $(REG_TYPE)
export PARAM_R_REG_TYPE ?= $(REG_TYPE)

ifeq ($(SIM), icarus)
	PLUSARGS += -fst

	ifeq ($(WAVES), 1)
		VERILOG_SOURCES += iverilog_dump.v
		COMPILE_ARGS += -s iverilog_dump
	endif
else ifeq ($(SIM), verilator)
	COMPILE_ARGS += -Wno-SELRANGE -Wno-WIDTH -Wno-CASEINCOMPLETE

	ifeq ($(WAVES), 1)
		COMPILE_ARGS += --trace-fst
	endif
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

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
