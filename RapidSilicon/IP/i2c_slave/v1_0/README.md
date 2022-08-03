## I2C-SLAVE Core Generation 
I2C-SLAVE is AXI4-Lite master interface based IP core.

### RTL
This directory contains the generator script which places the RTL to `/<mod_name>/rapidsilicon/ip/i2c_slave/v1_0/src` directory and generates its wrapper in the same directory. 

### Parameters
There are three parameters for I2C_SLAVE core.i.e. Data_Width, Address_Width and Filter Length.

1-  Data_Width can be 8, 16, 32 (Keyword: data_width)

2-  Address_Width can be 8, 16 (Keyword: addr_width)

3-  Filter_Length can be 1 to 4 (Keyword: filter_len)

To give above parameters to RTL, write `-P<parameter>=<value>` in configure_ip command in raptor.tcl file.

For example: configure_ip i2c_slave_gen -mod_name i2c_slave_wrapper `-Pdata_width=32` `-Paddr_width=16` `-Pfilter_len=4` -out_file ./i2c_slave_wrapper.v

### TCL File 
This python script also generates a .tcl file which will be placed in `/<mod_name>/rapidsilicon/ip/i2c/v1_0/synth` directory.

### Design Generation
To generate your design, follow these steps.

1- First, you have to source the Raptor.

2- After this, run the following command to generate your design.
```
raptor --batch --script raptor.tcl
```

### References

This IP core is taken from Alex-Forencich repository.

https://github.com/alexforencich/verilog-i2c/blob/master/rtl/i2c_slave_axil_master.v
https://github.com/alexforencich/verilog-i2c/blob/master/rtl/i2c_slave.v