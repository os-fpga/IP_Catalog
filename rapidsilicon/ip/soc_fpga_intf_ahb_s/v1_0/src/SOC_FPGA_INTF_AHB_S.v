`timescale 1ns/1ps
`celldefine
//
// SOC_FPGA_INTF_AHB_S simulation model
// SOC interface connection AHB Slave
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module SOC_FPGA_INTF_AHB_S (
  output S0_HRESETN_I, // None
  output [31:0] S0_HADDR, // None
  output [2:0] S0_HBURST, // None
  output S0_HMASTLOCK, // None
  input S0_HREADY, // None
  output [3:0] S0_HPROT, // None
  input [31:0] S0_HRDATA, // None
  input S0_HRESP, // None
  output S0_HSEL, // None
  output [2:0] S0_HSIZE, // None
  output [1:0] S0_HTRANS, // None
  output [3:0] S0_HWBE, // None
  output [31:0] S0_HWDATA, // None
  output S0_HWRITE, // None
  input S0_HCLK // None
);

endmodule
`endcelldefine
