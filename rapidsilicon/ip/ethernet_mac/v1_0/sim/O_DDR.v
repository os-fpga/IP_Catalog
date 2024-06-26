`timescale 1ns/1ps
`celldefine
//
// O_DDR simulation model
// DDR output register
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module O_DDR (
  input [1:0] D, // Data input
  input R, // Active-low asynchrnous reset
  input E, // Active-high enable
  input C, // Clock
  output reg Q = 1'b0 // Data output (connect to output port, buffer or O_DELAY)
);

  reg Q0;
  reg Qp;
  reg Q1;

  always @(negedge R)
    Q <= 1'b0;

  always@(posedge C)
  begin
    if(!R)
    begin
      Qp<=0;
      Q0<=0;
    end

    else 
    begin
      Q0<=D[0];
      Qp<=D[1];
    end
  end

  always@(negedge C)
  begin
    if(!R)
      Q1<=0;
    else
      Q1<=Qp;
  end

  
  always @(*)
  begin
    if (!R)
      Q <= 1'b0;
    else if (E) 
      if (C)
        Q <= Q0;
      else
        Q <= Q1;
  end
  
endmodule
`endcelldefine