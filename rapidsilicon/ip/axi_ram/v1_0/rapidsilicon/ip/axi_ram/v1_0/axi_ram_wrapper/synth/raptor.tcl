create_design axi_ram_wrapper
target_device GEMINI
add_include_path ../src
add_library_path ../src
add_library_ext .v .sv
add_design_file ../src/axi_ram_wrapper.v
set_top_module axi_ram_wrapper
synthesize