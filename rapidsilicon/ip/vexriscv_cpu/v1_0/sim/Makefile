DEBUG=no
MODULE_NAME ?= vexriscv_cpu_wrapper
REGRESSION_PATH?=./
$(shell mv ../src/$(MODULE_NAME)_v1_0.v ../src/$(MODULE_NAME).v)
VEXRISCV_FILE?=../src/$(MODULE_NAME).v
IBUS?=CACHED
IBUS_TC?=no
IBUS_DATA_WIDTH?=32
DBUS?=CACHED
DBUS_LOAD_DATA_WIDTH?=32
DBUS_STORE_DATA_WIDTH?=32
TRACE?=no
TRACE_ACCESS?=no
TRACE_START=0
TRACE_SPORADIC?=no
ISA_TEST?=yes
MUL?=yes
DIV?=yes
RVF?=no
RVD?=no
CSR?=yes
CSR_SKIP_TEST?=yes
EBREAK?=no
FENCEI?=no
MMU?=yes
DBUS_EXCLUSIVE?=no
DBUS_INVALIDATE?=no
PMP?=no
SEED?=no
LRSC?=yes
AMO?=yes
NO_STALL?=yes
DEBUG_PLUGIN?=no
DEBUG_PLUGIN_EXTERNAL?=no
RISCV_JTAG?=no
RUN_HEX?=no
WITH_RISCV_REF=yes
CUSTOM_SIMD_ADD?=no
CUSTOM_CSR?=no
DHRYSTONE=no
FREERTOS?=no
ZEPHYR?=no
REDO?=0
REF=no
TRACE_WITH_TIME=no
REF_TIME=no
THREAD_COUNT?=$(shell nproc)
MTIME_INSTR_FACTOR?=no
COMPRESSED?=no
SUPERVISOR?=yes
STOP_ON_ERROR?=no
COREMARK=no
WITH_USER_IO?=no
LINUX_REGRESSION?=yes
VEXRISCV_JTAG?=yes

OUT_DIR ?= $(PWD)



ADDCFLAGS += -CFLAGS -DREGRESSION_PATH='\"$(REGRESSION_PATH)/\"'
ADDCFLAGS += -CFLAGS -DIBUS_${IBUS}
ADDCFLAGS += -CFLAGS -DIBUS_DATA_WIDTH=${IBUS_DATA_WIDTH}
ADDCFLAGS += -CFLAGS -DDBUS_LOAD_DATA_WIDTH=${DBUS_LOAD_DATA_WIDTH}
ADDCFLAGS += -CFLAGS -DDBUS_STORE_DATA_WIDTH=${DBUS_STORE_DATA_WIDTH}

ADDCFLAGS += -CFLAGS -DDBUS_${DBUS}
ADDCFLAGS += -CFLAGS -DREDO=${REDO}
ADDCFLAGS += -CFLAGS -pthread
ADDCFLAGS += -CFLAGS -Wno-unused-result
VERILATOR_ARGS += --timescale 1ns/1ps


ADDCFLAGS += -CFLAGS -DTHREAD_COUNT=${THREAD_COUNT}

ifeq ($(DEBUG),yes)
	ADDCFLAGS += -CFLAGS -O0 -CFLAGS -g
else
	ADDCFLAGS += -CFLAGS -O3  -O3
endif

ifeq ($(CONCURRENT_OS_EXECUTIONS),yes)
	ADDCFLAGS += -CFLAGS -DCONCURRENT_OS_EXECUTIONS
endif

ifeq ($(LITEX),yes)
	ADDCFLAGS += -CFLAGS -DLITEX
	ADDCFLAGS += -CFLAGS -DVMLINUX='\"$(VMLINUX)\"'
	ADDCFLAGS += -CFLAGS -DDTB='\"$(DTB)\"'
	ADDCFLAGS += -CFLAGS -DRAMDISK='\"$(RAMDISK)\"'
	ADDCFLAGS += -CFLAGS -DEMULATOR='\"$(EMULATOR)\"'
endif

ifeq ($(LINUX_SOC),yes)
	ADDCFLAGS += -CFLAGS -DLINUX_SOC
	ADDCFLAGS += -CFLAGS -DVMLINUX='\"./linux/$(ARCH_LINUX)/Image\"'
	ADDCFLAGS += -CFLAGS -DDTB='\"./linux/$(ARCH_LINUX)/rv32.dtb\"'
	ADDCFLAGS += -CFLAGS -DRAMDISK='\"./linux/$(ARCH_LINUX)/rootfs.cpio\"'
	ADDCFLAGS += -CFLAGS -DEMULATOR='\"./linux/emulator/emulator.bin\"'
endif

ifeq ($(LINUX_SOC_SMP),yes)
	ADDCFLAGS += -CFLAGS -DLINUX_SOC_SMP
	ADDCFLAGS += -CFLAGS -DVMLINUX='\"$(VMLINUX)\"'
	ADDCFLAGS += -CFLAGS -DDTB='\"$(DTB)\"'
	ADDCFLAGS += -CFLAGS -DRAMDISK='\"$(RAMDISK)\"'
	ADDCFLAGS += -CFLAGS -DEMULATOR='\"$(EMULATOR)\"'
endif


ARCH_LINUX=rv32i
ifeq ($(MUL),yes)
ifeq ($(DIV),yes)
ARCH_LINUX:=$(ARCH_LINUX)m
endif
endif
ARCH_LINUX:=$(ARCH_LINUX)a
ifeq ($(COMPRESSED),yes)
ARCH_LINUX:=$(ARCH_LINUX)c
endif

ifeq ($(LINUX_REGRESSION),yes)
ifneq ($(ARCH_LINUX),rv32iac)
ifneq ($(ARCH_LINUX),rv32ia)
	ADDCFLAGS += -CFLAGS -DLINUX_REGRESSION
	ADDCFLAGS += -CFLAGS -DARCH_LINUX='\"$(ARCH_LINUX)\"'
	ADDCFLAGS += -CFLAGS -DVMLINUX='\"./linux/$(ARCH_LINUX)/Image\"'
	ADDCFLAGS += -CFLAGS -DDTB='\"./linux/$(ARCH_LINUX)/rv32.dtb\"'
	ADDCFLAGS += -CFLAGS -DRAMDISK='\"./linux/$(ARCH_LINUX)/rootfs.cpio\"'
	ADDCFLAGS += -CFLAGS -DEMULATOR='\"./linux/emulator/emulator.bin\"'
endif
endif
endif


ifeq ($(FLOW_INFO),yes)
	ADDCFLAGS += -CFLAGS -DFLOW_INFO
endif


ifeq ($(COREMARK),yes)
	ADDCFLAGS += -CFLAGS -DCOREMARK
endif

ifeq ($(WITH_RISCV_REF),yes)
	ADDCFLAGS += -CFLAGS -DWITH_RISCV_REF
endif



ifneq ($(shell grep timerInterrupt ${VEXRISCV_FILE} -w),)
    ADDCFLAGS += -CFLAGS -DTIMER_INTERRUPT
endif

ifneq ($(shell grep externalInterrupt ${VEXRISCV_FILE} -w),)
ifneq ($(EXTERNAL_INTERRUPT),no)
    ADDCFLAGS += -CFLAGS -DEXTERNAL_INTERRUPT
endif
endif

ifneq ($(shell grep utime ${VEXRISCV_FILE} -w),)
    ADDCFLAGS += -CFLAGS -DUTIME_INPUT
endif

ifneq ($(shell grep dBus_rsp_payload_aggregated ${VEXRISCV_FILE} -w),)
    ADDCFLAGS += -CFLAGS -DDBUS_AGGREGATION
endif


ifneq ($(RUN_HEX),no)
	ADDCFLAGS += -CFLAGS -DRUN_HEX='\"$(RUN_HEX)\"'
endif


ifeq ($(IBUS_TC),yes)
	ADDCFLAGS += -CFLAGS -DIBUS_TC=yes
endif
ifeq ($(WITH_USER_IO),yes)
	ADDCFLAGS += -CFLAGS -DWITH_USER_IO=yes
endif


ifeq ($(COMPRESSED),yes)
	ADDCFLAGS += -CFLAGS -DCOMPRESSED
endif
ifeq ($(SUPERVISOR),yes)
	ADDCFLAGS += -CFLAGS -DSUPERVISOR
endif
ifeq ($(FENCEI),yes)
	ADDCFLAGS += -CFLAGS -DFENCEI
endif

ifeq ($(EBREAK),yes)
	ADDCFLAGS += -CFLAGS -DEBREAK
endif


ifeq ($(DHRYSTONE),yes)
	ADDCFLAGS += -CFLAGS -DDHRYSTONE
endif

ifeq ($(STOP_ON_ERROR),yes)
	ADDCFLAGS += -CFLAGS -DSTOP_ON_ERROR
endif


ifeq ($(NO_STALL),yes)
	ADDCFLAGS += -CFLAGS -DSTALL=0
else
    ADDCFLAGS += -CFLAGS -DSTALL=1
endif

ifneq ($(MTIME_INSTR_FACTOR),no)
	ADDCFLAGS += -CFLAGS -DMTIME_INSTR_FACTOR=${MTIME_INSTR_FACTOR}
endif

ifneq ($(SEED),no)
	ADDCFLAGS += -CFLAGS -DSEED=${SEED}
endif

ifeq ($(TRACE),yes)
	VERILATOR_ARGS += --trace-fst
	ADDCFLAGS += -CFLAGS -DTRACE
endif

ifeq ($(TRACE_SPORADIC),yes)
	ADDCFLAGS += -CFLAGS -DTRACE_SPORADIC
endif



ifeq ($(CSR),yes)
	ADDCFLAGS += -CFLAGS -DCSR
endif

ifeq ($(CSR_SKIP_TEST),yes)
	ADDCFLAGS += -CFLAGS -DCSR_SKIP_TEST
endif


ifeq ($(LRSC),yes)
	ADDCFLAGS += -CFLAGS -DLRSC
endif

ifeq ($(AMO),yes)
	ADDCFLAGS += -CFLAGS -DAMO
endif

ifeq ($(CUSTOM_SIMD_ADD),yes)
	ADDCFLAGS += -CFLAGS -DCUSTOM_SIMD_ADD
endif

ifeq ($(CUSTOM_CSR),yes)
	ADDCFLAGS += -CFLAGS -DCUSTOM_CSR
endif

ifeq ($(TRACE_WITH_TIME),yes)
	ADDCFLAGS += -CFLAGS -DTRACE_WITH_TIME
endif

ifeq ($(REF_TIME),yes)
	ADDCFLAGS += -CFLAGS -DREF_TIME
endif

ifeq ($(ISA_TEST),yes)
	ADDCFLAGS += -CFLAGS -DISA_TEST
endif

ifeq ($(MMU),yes)
	ADDCFLAGS += -CFLAGS -DMMU
endif

ifeq ($(DBUS_EXCLUSIVE),yes)
	ADDCFLAGS += -CFLAGS -DDBUS_EXCLUSIVE
endif
ifeq ($(DBUS_INVALIDATE),yes)
	ADDCFLAGS += -CFLAGS -DDBUS_INVALIDATE
endif

ifeq ($(PMP),yes)
	ADDCFLAGS += -CFLAGS -DPMP
endif

ifeq ($(MUL),yes)
	ADDCFLAGS += -CFLAGS -DMUL
endif

ifeq ($(RVF),yes)
	ADDCFLAGS += -CFLAGS -DRVF
endif

ifeq ($(RVD),yes)
	ADDCFLAGS += -CFLAGS -DRVD
endif

ifeq ($(DIV),yes)
	ADDCFLAGS += -CFLAGS -DDIV
endif

ifeq ($(TRACE_ACCESS),yes)
	ADDCFLAGS += -CFLAGS -DTRACE_ACCESS
endif

ifneq ($(DEBUG_PLUGIN),no)
	ADDCFLAGS += -CFLAGS -DDEBUG_PLUGIN
	ADDCFLAGS += -CFLAGS -DDEBUG_PLUGIN_${DEBUG_PLUGIN}
endif

ifeq ($(DEBUG_PLUGIN_EXTERNAL),yes)
	ADDCFLAGS += -CFLAGS -DDEBUG_PLUGIN_EXTERNAL
endif


ifeq ($(RISCV_JTAG),yes)
	ADDCFLAGS += -CFLAGS -DRISCV_JTAG
endif

ifeq ($(VEXRISCV_JTAG),yes)
	ADDCFLAGS += -CFLAGS -DVEXRISCV_JTAG
endif

ifeq ($(REF),yes)
	ADDCFLAGS += -CFLAGS -DREF
endif

ADDCFLAGS += -CFLAGS -DTRACE_START=${TRACE_START}
ifeq ($(FREERTOS),yes)
	ADDCFLAGS += -CFLAGS -DFREERTOS
	ADDCFLAGS += -CFLAGS -DFREERTOS_COUNT=99999
else
ifneq ($(FREERTOS),no)
    ADDCFLAGS += -CFLAGS -DFREERTOS
    ADDCFLAGS += -CFLAGS -DFREERTOS_COUNT=$(FREERTOS)
endif
endif


ifeq ($(ZEPHYR),yes)
	ADDCFLAGS += -CFLAGS -DZEPHYR
	ADDCFLAGS += -CFLAGS -DZEPHYR_COUNT=99999
else
ifneq ($(ZEPHYR),no)
    ADDCFLAGS += -CFLAGS -DZEPHYR
    ADDCFLAGS += -CFLAGS -DZEPHYR_COUNT=$(ZEPHYR)
endif
endif

all: run clear

run: compile rename_back
	./obj_dir/V$(MODULE_NAME)
	-@mv obj_dir $(OUT_DIR)
	-@mv linux.logTrace $(OUT_DIR)
	-@mv linux.debugTrace $(OUT_DIR)

verilate: ${VEXRISCV_FILE}
	verilator -cc  ${VEXRISCV_FILE} -I../src/ -O3 -CFLAGS -std=c++11 -LDFLAGS -pthread  ${ADDCFLAGS} --gdbbt ${VERILATOR_ARGS} -Wno-UNOPTFLAT -Wno-WIDTH --x-assign unique --exe main.cpp

compile: verilate
	make  -j${THREAD_COUNT} -C obj_dir/ -f V$(MODULE_NAME).mk V$(MODULE_NAME)

rename_back:
	mv ../src/$(MODULE_NAME).v ../src/$(MODULE_NAME)_v1_0.v
 	
clear:
	@rm -rf obj_dir ../litex_wrapper/__pycache__
	@rm -rf linux.debugTrace linux.logTrace
	@mv ../src/$(MODULE_NAME).v ../src/$(MODULE_NAME)_v1_0.v