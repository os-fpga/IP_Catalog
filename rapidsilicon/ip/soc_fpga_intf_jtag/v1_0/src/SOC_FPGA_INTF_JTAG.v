`timescale 1ns/1ps
`celldefine
//
// SOC_FPGA_INTF_JTAG simulation model
// SOC JTAG connection
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module SOC_FPGA_INTF_JTAG (
  input BOOT_JTAG_TCK, // JTAG TCK
  output BOOT_JTAG_TDI, // JTAG TDI
  input BOOT_JTAG_TDO, // JTAG TDO
  output BOOT_JTAG_TMS, // JTAG TMS
  output BOOT_JTAG_TRSTN, // JTAG TRSTN
  input BOOT_JTAG_EN // JTAG enable
);

endmodule
`endcelldefine
