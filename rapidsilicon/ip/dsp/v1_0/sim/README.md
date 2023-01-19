# Simulations
First you need to generate the IP. For IP generation, run the following command:
```
python3 ../dsp_gen.py --build --feature=A*B --a_width=12 --b_width=10
```
For simulation run the following commands:
```
iverilog -o dsp dsp_AxB.v rapidsilicon/ip/dsp/v1_0/dsp_wrapper/src/dsp_wrapper.v ../../../../../../sim_models/rapidsilicon/genesis2/dsp_sim.v
```
```
vvp bram
```
