target_device GEMINI
add_litex_ip_catalog ./
create_design axi_gpio
add_library_ext .v .sv
configure_ip axi_gpio_gen -mod_name axi_gpio_wrapper -Pdata_width=16 -Paddr_width=8 -out_file ./axi_gpio_wrapper.sv
ipgenerate
add_design_file ./axi_gpio_wrapper/rapidsilicon/ip/axi_gpio/v1_0/src/axi_gpio_wrapper.sv
add_library_path axi_gpio_wrapper/rapidsilicon/ip/axi_gpio/v1_0/src/
set_top_module axi_gpio_wrapper
synth delay

