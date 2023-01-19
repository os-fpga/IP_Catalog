# Simulations
First you need to generate the IP. For IP generation, run the following command:
```
python3 ../bram_gen.py --build --memory_type=SP --write_depth=1024 --data_width=32
```
For simulation run the following commands:
```
iverilog -o bram sp_1024x32.v rapidsilicon/ip/bram/v1_0/bram_wrapper/src/bram_wrapper.v ../../../../../../sim_models/rapidsilicon/genesis2/brams_sim.v ../../../../../../sim_models/rapidsilicon/genesis2/TDP18K_FIFO.v ../../../../../../sim_models/rapidsilicon/genesis2/ufifo_ctl.v ../../../../../../sim_models/rapidsilicon/genesis2/sram1024x18.v
```
```
vvp bram
```
