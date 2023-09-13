`timescale 1ns/1ps
`celldefine
//
// SOC_FPGA_INTF_DMA simulation model
// SOC DMA interface
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module SOC_FPGA_INTF_DMA (
  input [3:0] DMA_REQ, // DMA request
  output [3:0] DMA_ACK, // DMA acknowledge
  input DMA_CLK, // DMA clock
  input DMA_RST_N // DMA reset
);

endmodule
`endcelldefine
