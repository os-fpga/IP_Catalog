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
PWD=$(shell pwd)
export PYTHONPATH := $(PWD)/../model:$(PYTHONPATH)

SIM ?= icarus

WAVES ?= 1

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

DUT      = ahb2axi4_bridge
TOPLEVEL = ahb2axi4_wrapper
MODULE   = test_$(TOPLEVEL)
VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/ahb2axi4_bridge/v1_0/ahb2axi4_wrapper/src/ahb2axi4_wrapper.v
VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/ahb2axi4_bridge/v1_0/ahb2axi4_wrapper/src/ahb2axi4.sv
VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/ahb2axi4_bridge/v1_0/ahb2axi4_wrapper/src/beh_lib.sv
#VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/axi2axilite_bridge/v1_0/axi2axilite_wrapper/src/sfifo.v
#VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/axi2axilite_bridge/v1_0/axi2axilite_wrapper/src/skidbuffer.v


$(shell ../$(DUT)_gen.py --data_width=32 --addr_width=32 --id_width=1 --build)

ifeq ($(SIM), icarus)
	PLUSARGS += -fst

	ifeq ($(WAVES), 1)
		VERILOG_SOURCES += iverilog_dump.v
		COMPILE_ARGS += -s iverilog_dump
		#COMPILE_ARGS += --trace-fst
	endif
ifeq ($(SIM), vcs)
         SIM_BUILD = ./
         EXTRA_ARGS := $(EXTRA_ARGS) +vcs+lic+wait 
         EXTRA_ARGS := $(EXTRA_ARGS) -kdb -lca 
         EXTRA_ARGS := $(EXTRA_ARGS) -q 
         EXTRA_ARGS := $(EXTRA_ARGS)-debug_access+all
         EXTRA_ARGS := $(EXTRA_ARGS)-cm line

	
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
	echo '    $$dumpfile("$(TOPLEVEL).fst");' >> $@
	echo '    $$dumpvars(0, $(TOPLEVEL));' >> $@
	echo 'end' >> $@
	echo 'endmodule' >> $@

clean::
	@rm -rf iverilog_dump.v
	@rm -rf dump.fst $(TOPLEVEL).fst
