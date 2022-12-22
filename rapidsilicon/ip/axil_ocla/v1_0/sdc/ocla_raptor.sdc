create_clock -period 10 i_S_AXI_ACLK
set_input_delay 1 -clock i_S_AXI_ACLK [get_ports {*}]
set_output_delay 1 -clock i_S_AXI_ACLK [get_ports {*}]

create_clock -period 5 i_sample_clk
set_input_delay 1 -clock i_sample_clk [get_ports {*}]
set_output_delay 1 -clock i_sample_clk [get_ports {*}]

set_clock_groups -exclusive -group {i_S_AXI_ACLK} -group {i_sample_clk}
