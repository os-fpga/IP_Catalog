`timescale 1ns/1ps
`celldefine
//
// SOC_FPGA_INTF_AXI_M0 simulation model
// SOC interface connection AXI Master 0
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module SOC_FPGA_INTF_AXI_M0 (
  input [31:0] M0_ARADDR, // None
  input [1:0] M0_ARBURST, // None
  input [3:0] M0_ARCACHE, // None
  input [3:0] M0_ARID, // None
  input [2:0] M0_ARLEN, // None
  input M0_ARLOCK, // None
  input [2:0] M0_ARPROT, // None
  output M0_ARREADY, // None
  input [2:0] M0_ARSIZE, // None
  input M0_ARVALID, // None
  input [31:0] M0_AWADDR, // None
  input [1:0] M0_AWBURST, // None
  input [3:0] M0_AWCACHE, // None
  input [3:0] M0_AWID, // None
  input [2:0] M0_AWLEN, // None
  input M0_AWLOCK, // None
  input [2:0] M0_AWPROT, // None
  output M0_AWREADY, // None
  input [2:0] M0_AWSIZE, // None
  input M0_AWVALID, // None
  output [3:0] M0_BID, // None
  input M0_BREADY, // None
  output [1:0] M0_BRESP, // None
  output M0_BVALID, // None
  output [63:0] M0_RDATA, // None
  output [3:0] M0_RID, // None
  output M0_RLAST, // None
  input M0_RREADY, // None
  output [1:0] M0_RRESP, // None
  output M0_RVALID, // None
  input [63:0] M0_WDATA, // None
  input M0_WLAST, // None
  output M0_WREADY, // None
  input [7:0] M0_WSTRB, // None
  input M0_WVALID, // None
  input M0_ACLK, // None
  output M0_ARESETN_I // None
);

endmodule
`endcelldefine
