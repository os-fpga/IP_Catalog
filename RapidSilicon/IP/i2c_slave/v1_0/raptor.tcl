target_device GEMINI
add_litex_ip_catalog ./
create_design i2c_slave
configure_ip i2c_slave_gen -mod_name i2c_slave_wrapper -Pdata_width=32 -Paddr_width=16 -Pfilter_len=2 -out_file ./i2c_slave_wrapper.v
ipgenerate
add_design_file ./i2c_slave_wrapper/rapidsilicon/ip/i2c_slave/v1_0/src/i2c_slave_wrapper.v
add_library_path i2c_slave_wrapper/rapidsilicon/ip/i2c_slave/v1_0/src/
set_top_module i2c_slave_wrapper
synth delay