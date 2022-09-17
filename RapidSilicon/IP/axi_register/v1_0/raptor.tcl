create_design ip_test
target_device GEMINI
add_litex_ip_catalog ip_generator/
puts "Catalog:"
foreach ip [ip_catalog] {
    puts "IP: $ip"
    foreach param [ip_catalog $ip] {
        puts "  PARAM [lindex $param 0], default: [lindex $param 1]"
    }
}
configure_ip axi_register_ip_generator -mod_name register -version v1_0 -out_file ./register.v
ipgenerate
add_design_file ./rapidsilicon/ip/axi_register/v1_0/register/src/register.v
add_library_path rapidsilicon/ip/axi_register/v1_0/register/src/
set_top_module register
synth delay

