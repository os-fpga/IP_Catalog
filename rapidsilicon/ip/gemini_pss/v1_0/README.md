# Gemini Processing Subsystem Core Generation 
## Introduction

The Gemini Processing SubSystem (PSS) is the hardened processing and peripheral complex in the Gemini family of devices.  This IP core creates the base IP RTL references and accompanying SDC contraints to use the Gemini PSS in a Raptor design.

For more information, visit: https://rapidsilicon.com/gemini-product-brief/

## Generator Script
This directory contains the generator script which places the RTL to `rapidsilicon/ip/gemini_pss/v1_0/<build-name>/src/` directory and generates its wrapper in the same directory.

The Gemini PSS is not a user-customizable IP.  The generator script simply creates the appropriate wrapper RTL and SDC contraints and places them in the output directory for inclusion in the Raptor DS design.

## TCL File

This python script also generates a raptor.tcl file which will be placed in `rapidsilicon/ip/vexriscv_cpu/v1_0/<build-name>/synth/` directory.


## References
