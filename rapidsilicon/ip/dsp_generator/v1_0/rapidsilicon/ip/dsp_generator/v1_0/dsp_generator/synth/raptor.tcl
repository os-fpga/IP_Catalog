create_design dsp_generator
target_device GEMINI
add_include_path ../src
add_library_path ../src
add_library_ext .v .sv
add_design_file ../src/dsp_generator.v
set_top_module dsp_generator
synthesize