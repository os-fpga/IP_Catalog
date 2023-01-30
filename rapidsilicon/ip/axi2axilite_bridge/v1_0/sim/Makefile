# Auto generated Makefile
# COCO_TB Variables
TOPLEVEL_LANG = verilog

 PWD=$(shell pwd)
export PYTHONPATH := $(PWD)/../model:$(PYTHONPATH)
DUT      =  axi2axilite_bridge
TOPLEVEL =  axi2axilite_wrapper
MODULE   = test_$(TOPLEVEL)
VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/axi2axilite_bridge/v1_0/axi2axilite_wrapper/src/axi2axilite_wrapper.v
VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/axi2axilite_bridge/v1_0/axi2axilite_wrapper/src/axi2axilite.v
VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/axi2axilite_bridge/v1_0/axi2axilite_wrapper/src/axi_addr.v
VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/axi2axilite_bridge/v1_0/axi2axilite_wrapper/src/sfifo.v
VERILOG_SOURCES += $(PWD)/rapidsilicon/ip/axi2axilite_bridge/v1_0/axi2axilite_wrapper/src/skidbuffer.v

$(shell ../$(DUT)_gen.py --data_width=32 --addr_width=16 --id_width=2 --build)

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
