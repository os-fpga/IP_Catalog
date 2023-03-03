create_design on_chip_memory_wrapper
target_device GEMINI
add_include_path ../src
add_library_path ../src
add_library_ext .v .sv
add_design_file ../src/on_chip_memory_wrapper.v
set_top_module on_chip_memory_wrapper
synthesize