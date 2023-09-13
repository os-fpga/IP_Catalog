`timescale 1ns/1ps
`celldefine
//
// SOC_FPGA_INTF_IRQ simulation model
// SOC Interupt connection
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module SOC_FPGA_INTF_IRQ (
  input [15:0] IRQ_SRC, // Interupt source
  output [15:0] IRQ_SET, // Interupt set
  input IRQ_CLK, // interupt clock
  input IRQ_RST_N // Interupt reset
);

endmodule
`endcelldefine
