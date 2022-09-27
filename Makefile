SHELL := /bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PREFIX ?= $(ROOT_DIR)/instal_dir

build: 
	echo $(PREFIX)
	cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$(PREFIX) -j $(CPU_CORES) -S . -B build 

install: build
	cmake --install build