create_design reset_release_wrapper
target_device GEMINI
add_include_path ../src
add_library_path ../src
add_library_ext .v .sv
add_design_file ../src/reset_release_wrapper.v
set_top_module reset_release_wrapper
synthesize