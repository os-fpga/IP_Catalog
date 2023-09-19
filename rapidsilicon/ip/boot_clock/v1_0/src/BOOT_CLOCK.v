`timescale 1ns/1ps
`celldefine
//
// BOOT_CLOCK simulation model
// Internal BOOT_CLK connection
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module BOOT_CLOCK #(
  parameter PERIOD = 25.0 // Clock period for simulation purposes (nS)
) (
  output reg O = 1'b0 // Clock output
);
localparam HALF_PERIOD = PERIOD/2.0;

			   
  always
    #HALF_PERIOD O <= ~O;
 initial begin

    if ((PERIOD < 16.0) || (PERIOD > 30.0)) begin
       $display("BOOT_CLOCK instance %m PERIOD set to incorrect value, %f.  Values must be between 16.0 and 30.0.", PERIOD);
    #1 $stop;
    end

  end

endmodule
`endcelldefine
