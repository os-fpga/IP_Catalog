target_device GEMINI
add_litex_ip_catalog ./
create_design i2c_master
configure_ip i2c_master_gen -mod_name i2c_master_wrapper -Pdefault_prescale=1 -Pfixed_prescale=0 -Pcmd_fifo=1 -Pcmd_addr_width=4 -Pwrite_fifo=1 -Pwrite_addr_width=4 -Pread_fifo=1 -Pread_addr_width=4 -out_file ./i2c_master_wrapper.v
ipgenerate
add_design_file ./i2c_master_wrapper/rapidsilicon/ip/i2c_master/v1_0/src/i2c_master_wrapper.v
add_library_path i2c_master_wrapper/rapidsilicon/ip/i2c_master/v1_0/src/
set_top_module i2c_master_wrapper
synth delay

