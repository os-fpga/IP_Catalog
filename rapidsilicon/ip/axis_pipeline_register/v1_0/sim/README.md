# Simulation  

This is a Cocotb based simulation for which either `Icarus Verilog` or `Verilator` is required.

Before starting simulation, you have to create IP with default parameters. To create this IP, run the following command:
```
python3 ../axis_pipeline_register_gen.py --build --id_en=1 --dest_en=1
```

Run the following command for simulation:
```
make OUT_DIR=$(PWD) MODULE_NAME=(name of generated IP module)
``` 