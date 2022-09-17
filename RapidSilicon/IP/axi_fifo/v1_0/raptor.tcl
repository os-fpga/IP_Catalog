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
configure_ip axi_fifo_ip_generator -mod_name fifo -version v1_0 -out_file ./fifo.v
ipgenerate
add_design_file ./rapidsilicon/ip/axi_fifo/v1_0/fifo/src/fifo.v
add_library_path rapidsilicon/ip/axi_fifo/v1_0/fifo/src/
set_top_module fifo
synth delay

