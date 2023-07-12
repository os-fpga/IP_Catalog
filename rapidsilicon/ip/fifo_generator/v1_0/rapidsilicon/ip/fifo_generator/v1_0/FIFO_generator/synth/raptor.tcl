create_design FIFO_generator
target_device GEMINI
add_include_path ../src
add_library_path ../src
add_library_ext .v .sv
add_design_file ../src/FIFO_generator.v
set_top_module FIFO_generator
synthesize