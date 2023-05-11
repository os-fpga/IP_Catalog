# Simulation  

This is a Cocotb based simulation for which either `Icarus Verilog` or `Verilator` is required.

Before starting simulation, you have to create IP with default parameters. To create this IP, run the following command:
```
python3 ../axis_adapter_gen.py --build
```

Run the following command for simulation:
```
make OUT_DIR=$(PWD)
``` 