`timescale 1ns/1ps
`celldefine
//
// SOC_FPGA_INTF_AXI_M1 simulation model
// SOC interface connection AXI Master 1
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module SOC_FPGA_INTF_AXI_M1 (
  input [31:0] M1_ARADDR, // None
  input [1:0] M1_ARBURST, // None
  input [3:0] M1_ARCACHE, // None
  input [3:0] M1_ARID, // None
  input [2:0] M1_ARLEN, // None
  input M1_ARLOCK, // None
  input [2:0] M1_ARPROT, // None
  output M1_ARREADY, // None
  input [2:0] M1_ARSIZE, // None
  input M1_ARVALID, // None
  input [31:0] M1_AWADDR, // None
  input [1:0] M1_AWBURST, // None
  input [3:0] M1_AWCACHE, // None
  input [3:0] M1_AWID, // None
  input [2:0] M1_AWLEN, // None
  input M1_AWLOCK, // None
  input [2:0] M1_AWPROT, // None
  output M1_AWREADY, // None
  input [2:0] M1_AWSIZE, // None
  input M1_AWVALID, // None
  output [3:0] M1_BID, // None
  input M1_BREADY, // None
  output [1:0] M1_BRESP, // None
  output M1_BVALID, // None
  output [63:0] M1_RDATA, // None
  output [3:0] M1_RID, // None
  output M1_RLAST, // None
  input M1_RREADY, // None
  output [1:0] M1_RRESP, // None
  output M1_RVALID, // None
  input [63:0] M1_WDATA, // None
  input M1_WLAST, // None
  output M1_WREADY, // None
  input [7:0] M1_WSTRB, // None
  input M1_WVALID, // None
  input M1_ACLK, // None
  output M1_ARESETN_I // None
);

endmodule
`endcelldefine
