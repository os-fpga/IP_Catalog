## AXI-RAM Core Generation 

AXI-RAM is AXI4-Lite based IP core.

### RTL
This directory contains the generator script which places the RTL to `/<mod_name>/rapidsilicon/ip/axi_ram/v1_0/src` directory and generates its wrapper in the same directory. 

### Parameters
There are four parameters for AXI-RAM core.i.e. Data_Width, Address_Width, ID_Width and Pipeline_Output.

1-  Data_Width can be 8, 16, 32 (Keyword: data_width)

2-  Address_Width can be 8, 16 (Keyword: addr_width)

3-  ID_Width can be 0 to 8 (Keyword: id_width)

4-  Pipeline_Output can be 0 or 1 (Keyword: pip_out)


To give above parameters to RTL, write `-P<parameter>=<value>` in configure_ip command in raptor.tcl file.

For example: configure_ip axi_ram_gen -mod_name axi_ram_wrapper `-Pdata_width=32` `-Paddr_width=16` `-Pid_width=5` `-Ppip_out=1` -out_file ./axi_ram_wrapper.v

### TCL File

This python script also generates a .tcl file which will be placed in `/<mod_name>/rapidsilicon/ip/axi_ram/v1_0/synth` directory.

### Design Generation

To generate your design, follow these steps.

1- First, you have to source the Raptor.

2- After this, run the following command to generate your design.
```
raptor --batch --script raptor.tcl
```

### References
This IP core is taken from Alex-Forencich repository.

https://github.com/alexforencich/verilog-axi/blob/master/rtl/axi_ram.v