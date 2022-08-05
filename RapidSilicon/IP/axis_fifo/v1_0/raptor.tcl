target_device GEMINI
add_litex_ip_catalog ./
create_design axis_fifo
configure_ip axis_fifo_gen -mod_name axis_fifo_wrapper -Pdepth=4096 -Pdata_width=32 -out_file ./axis_fifo_wrapper.v
ipgenerate
add_design_file ./axis_fifo_wrapper/rapidsilicon/ip/axis_fifo/v1_0/src/axis_fifo_wrapper.v
add_library_path axis_fifo_wrapper/rapidsilicon/ip/axis_fifo/v1_0/src/
set_top_module axis_fifo_wrapper
synth delay

