create_design i2c_slave_wrapper
target_device GEMINI
add_library_path ../src
add_design_file ../src/i2c_slave_wrapper.v
set_top_module i2c_slave_wrapper
synthesize