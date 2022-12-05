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

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

export PARAM_S_COUNT ?= 4
export PARAM_M_COUNT ?= 4

DUT      = axi_interconnect
WRAPPER	 = $(DUT)_wrapper
TOPLEVEL = $(WRAPPER)
MODULE   = test_$(DUT)
VERILOG_SOURCES += ./rapidsilicon/ip/axi_interconnect/v1_0/axi_interconnect_wrapper/src/$(TOPLEVEL).v
VERILOG_SOURCES += ./rapidsilicon/ip/axi_interconnect/v1_0/axi_interconnect_wrapper/src/$(DUT).v
VERILOG_SOURCES += ./rapidsilicon/ip/axi_interconnect/v1_0/axi_interconnect_wrapper/src/arbiter.v
VERILOG_SOURCES += ./rapidsilicon/ip/axi_interconnect/v1_0/axi_interconnect_wrapper/src/priority_encoder.v

# module parameters
export PARAM_DATA_WIDTH ?= 32
export PARAM_ADDR_WIDTH ?= 32
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
export PARAM_FORWARD_ID ?= 1
export PARAM_M_REGIONS ?= 1

$(shell ../$(DUT)_gen.py --s_count=${PARAM_S_COUNT} --m_count=${PARAM_M_COUNT} --build)

ifeq ($(SIM), icarus)
	PLUSARGS += -fst

	ifeq ($(WAVES), 1)
		VERILOG_SOURCES += iverilog_dump.v
		COMPILE_ARGS += -s iverilog_dump
	endif
else ifeq ($(SIM), verilator)
	COMPILE_ARGS += -Wno-SELRANGE -Wno-WIDTH -Wno-fatal

	ifeq ($(WAVES), 1)
		COMPILE_ARGS += --trace-fst
	endif
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

iverilog_dump.v:
	echo 'module iverilog_dump();' > $@
	echo 'initial begin' >> $@
	echo '    $$dumpfile("$(TOPLEVEL).fst");' >> $@
	echo '    $$dumpvars(0, $(TOPLEVEL));' >> $@
	echo 'end' >> $@
	echo 'endmodule' >> $@

clean::
	@rm -rf iverilog_dump.v
	@rm -rf dump.fst $(TOPLEVEL).fst
	@rm -rf *_wrap_*.v
