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
configure_ip axil_gpio_ip_generator -mod_name gpio -version v1_0 -out_file ./gpio.v
ipgenerate
add_design_file ./rapidsilicon/ip/axil_gpio/v1_0/gpio/src/gpio.v
add_library_path rapidsilicon/ip/axil_gpio/v1_0/gpio/src/
set_top_module gpio
synth delay

