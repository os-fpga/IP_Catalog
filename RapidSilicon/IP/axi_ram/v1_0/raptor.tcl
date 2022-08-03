target_device GEMINI
add_litex_ip_catalog ./
create_design axi_ram
configure_ip axi_ram_gen -mod_name axi_ram_wrapper -Pdata_width=32 -Paddr_width=8 -Pid_width=5 -Ppip_out=1 -out_file ./axi_ram_wrapper.v
ipgenerate
add_design_file ./axi_ram_wrapper/rapidsilicon/ip/axi_ram/v1_0/src/axi_ram_wrapper.v
add_library_path axi_ram_wrapper/rapidsilicon/ip/axi_ram/v1_0/src/
set_top_module axi_ram_wrapper
synth delay

