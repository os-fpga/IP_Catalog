#!/bin/bash
raptor_exe=`which raptor`
[ -z "$raptor_exe" ] && { echo "Make sure Raptor bin path is in your PATH"; exit 1; }
bin_path=`dirname $raptor_exe`
export PATH=$bin_path/../share/envs/litex/bin:$PATH
export LIBPYTHON_LOC=$bin_path/../share/envs/python3.8/lib/libpython3.8.so.1.0
make
