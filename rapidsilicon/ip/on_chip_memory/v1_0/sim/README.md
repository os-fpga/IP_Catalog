# Simulations
First you need to generate the IP. For IP generation, run the following command:
```
python3 ../on_chip_memory_gen.py --build --memory_type=SP --write_depth=1024 --data_width=32
```
For simulation run the following commands:
```
iverilog -o ocm sp_1024x32.v rapidsilicon/ip/on_chip_memory/v1_0/on_chip_memory_wrapper/src/on_chip_memory_wrapper.v ../../../../../../sim_models/rapidsilicon/genesis2/brams_sim.v ../../../../../../sim_models/rapidsilicon/genesis2/TDP18K_FIFO.v ../../../../../../sim_models/rapidsilicon/genesis2/ufifo_ctl.v ../../../../../../sim_models/rapidsilicon/genesis2/sram1024x18.v
```
```
vvp ocm
```
