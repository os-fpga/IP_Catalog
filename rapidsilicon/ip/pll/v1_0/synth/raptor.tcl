create_design pll_wrapper
target_device GEMINI
add_include_path ../src
add_library_path ../src
add_library_ext .v .sv
add_design_file ../src/pll_wrapper.v
set_top_module pll_wrapper
synthesize