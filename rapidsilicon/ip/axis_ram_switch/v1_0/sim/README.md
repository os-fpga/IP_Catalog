# Simulation  
First, you have to set cocotb environment on your machine. Todo this, run the following commands:
```
pip3 install cocotb
pip3 install cocotb-test
pip3 install cocotb-bus
pip3 install cocotbext-axi
```

For simulation, you have to install either of the simulators `Icarus Verilog` or `Verilator`.

Before starting simulation, you have to create IP with following parameters according to the designed test. To create this IP, run the following command:
```
python3 axis_ram_switch_gen.py --id_en=1 --tid=1 --s_id_width=16 --m_dest_width=8  --build
```
Make sure to update the **m_count** and **s_count** in the __axis_ram_switch_gen.py__ according to the configuration of generated RTL Wrapper.

Run the following command for simulation:
```
make
```  