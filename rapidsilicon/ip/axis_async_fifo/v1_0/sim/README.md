# Simulation  
First, you have to set cocotb environment on your machine. Todo this, run the following commands:
```
pip install cocotb

pip install cocotbext-axi
```

For simulation, you have to install either of the simulators `Icarus Verilog` or `Verilator`.

Before starting simulation, you have to create IP with default parameters. To create this IP, run the following command in the previous directory:
```
python3 axis_async_fifo_gen.py --build
```

Run the following command for simulation:
```
make
``` 