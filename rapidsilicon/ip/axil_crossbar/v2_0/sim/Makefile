# Copyright (c) 2021 Alex Forencich
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

#SIM ?= icarus
SIM ?= verilator
WAVES ?= 1

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

export PARAM_S_COUNT ?= 2
export PARAM_M_COUNT ?= 2
export PARAM_AXI4FULL ?= 0

DUT      = axil_crossbar_wrapper
TOPLEVEL = $(DUT)
MODULE   = test_axil_crossbar

VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/$(DUT).v
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/axil_crossbar.v 
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/axi_cdc.v 
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/axil_crossbar_addr.v 
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/axil_crossbar_rd.v 
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/axil_crossbar_wr.v 
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/axil_register_rd.v 
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/axil_register_wr.v 
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/arbiter.v
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/priority_encoder.v
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/dual_port_ram.v
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/afifo.v
VERILOG_SOURCES += ./rapidsilicon/ip/axil_crossbar/v2_0/axil_crossbar_wrapper/src/synchronizer.v

$(shell ../axil_crossbar_gen.py --s_count=${PARAM_S_COUNT} --m_count=${PARAM_M_COUNT} --build)

ifeq ($(SIM), icarus)
	PLUSARGS += -fst

	ifeq ($(WAVES), 1)
		VERILOG_SOURCES += iverilog_dump.v
		COMPILE_ARGS += -s iverilog_dump
	endif
else ifeq ($(SIM), verilator)
	COMPILE_ARGS += -Wno-SELRANGE -Wno-WIDTH -Wno-lint

	ifeq ($(WAVES), 1)
		COMPILE_ARGS += --trace-fst
	endif
endif

#EXTRA_ARGS += --coverage # Enables all forms of coverage, alias for --coverage-line --coverage-toggle --coverage-user
#EXTRA_ARGS += --coverage-line # Enables basic block line coverage analysis.
#EXTRA_ARGS += --coverage-toggle # Enables adding signal toggle coverage.
#EXTRA_ARGS += --coverage-underscore # Enable coverage of signals that start with an underscore.
#EXTRA_ARGS += --coverage-user Enables adding user inserted functional coverage.
 

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
	@rm -rf __pycache__
	@rm -rf coverage
	@rm -rf coverage.dat
	@rm -rf coverage.info
	@rm -rf results.xml
	
