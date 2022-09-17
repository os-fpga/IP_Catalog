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
configure_ip axi_dpram_ip_generator -mod_name dp_ram -version v1_0 -out_file ./dp_ram.v
ipgenerate
add_design_file ./rapidsilicon/ip/axi_dpram/v1_0/dp_ram/src/dp_ram.v
add_library_path rapidsilicon/ip/axi_dpram/v1_0/dp_ram/src/
set_top_module dp_ram
synth delay

