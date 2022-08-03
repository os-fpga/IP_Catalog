## AXI-GPIO Core Generation 

AXI-GPIO is AXI4-Lite based IP core.

### RTL

This directory contains the generator script which places the RTL to `/<mod_name>/rapidsilicon/ip/axi_gpio/v1_0/src` directory and generates its wrapper in the same directory. 

### Parameters
There are two parameters for AXI-GPIO core.i.e. Data_Width and Address_Width

1-  Data_Width can be 8, 16, 32 (Keyword: data_width)

2-  Address_Width can be 8, 16 (Keyword: addr_width)

To give above parameters to RTL, write `-P<parameter>=<value>` in configure_ip command in raptor.tcl file.

For example:
configure_ip axi_gpio_gen -mod_name axi_gpio_wrapper `-Pdata_width=32` `-Paddr_width=16` -out_file ./axi_gpio_wrapper.v

### TCL File

This python script also generates a .tcl file which will be placed in `/<mod_name>/rapidsilicon/ip/axi_gpio/v1_0/synth` directory.

### Design Generation

To generate your design, follow these steps.

1-  First, you have to source the Raptor.

2-  After this, run the following command to generate your design.
```
raptor --batch --script raptor.tcl
```

### References
This IP core is taken from smartfoxdata repository.

https://github.com/smartfoxdata/axi4lite_gpio/tree/master/rtl