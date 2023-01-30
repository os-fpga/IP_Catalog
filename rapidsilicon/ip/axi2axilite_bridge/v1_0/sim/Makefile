# Auto generated Makefile
# COCO_TB Variables
TOPLEVEL_LANG = verilog

PWD=$(shell pwd)
export PYTHONPATH := $(PWD)/../model:$(PYTHONPATH)

VERILOG_SOURCES += $(PWD)/../src/$(DUT).v
VERILOG_SOURCES += $(PWD)/../src/$ axi2axilite.v
VERILOG_SOURCES += $(PWD)/../src/$ axi_addr.v
VERILOG_SOURCES += $(PWD)/../src/$ sfifo.v
VERILOG_SOURCES += $(PWD)/../src/$ skidbuffer.v
DUT      = axi2axilite_wrapper
TOPLEVEL = $(DUT)
MODULE   = test_$(DUT)

$(shell ../$(DUT)_gen.py --build)

SIM = vcs
SIM_BUILD = ./
#RTL_LIBRARY = work
SIM_ARGS = 
EXTRA_ARGS = 
EXTRA_ARGS := $(EXTRA_ARGS) +vcs+lic+wait 
EXTRA_ARGS := $(EXTRA_ARGS) -kdb -lca 
EXTRA_ARGS := $(EXTRA_ARGS) -q 
EXTRA_ARGS := $(EXTRA_ARGS)-debug_access+all 
EXTRA_ARGS := $(EXTRA_ARGS)-cm line              #+tgl+cond+fsm+branch

include $(shell cocotb-config --makefiles)/Makefile.sim
