# Linux Simulation on VexRiscv

Linux can be booted via the included **Makefile** via the following command after getting to this folder: 
```
make OUT_DIR=$(PWD) MODULE_NAME=<name_of_generated_IP_module>
```
This make command will boot Linux and run a pre-defined Regression to verify the working of Linux on the VexRiscv CPU. This simulation uses Verilator as the Simulator.
## Linux Boot
To just boot Linux on the VexRiscv CPU, type out the following command on the terminal in this folder:
```
make LINUX_SOC=yes LINUX_REGRESSION=no OUT_DIR=$(PWD) MODULE_NAME=<name_of_generated_IP_module>
```
