`timescale 1ns/1ps
`celldefine
//
// O_BUFT simulation model
// Output tri-state buffer
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module O_BUFT #(
      parameter WEAK_KEEPER = "NONE" // Enable pull-up/pull-down on output (NONE/PULLUP/PULLDOWN)
) (
  input I, // Data input
  input T, // Tri-state output
  output O // Data output (connect to top-level port)
);

  generate
    if ( WEAK_KEEPER == "PULLUP" )  begin: add_pullup
      pullup(O);
    end else if ( WEAK_KEEPER == "PULLDOWN" ) begin: add_pulldown
      pulldown(O);
    end
  endgenerate

  assign O = T ? I : 1'bz; 

   initial begin
    case(WEAK_KEEPER)
      "NONE" ,
      "PULLUP" ,
      "PULLDOWN": begin end
      default: begin
        $display("\nError: O_BUFT instance %m has parameter WEAK_KEEPER set to %s.  Valid values are NONE, PULLUP, PULLDOWN\n", WEAK_KEEPER);
        #1 $stop ;
      end
    endcase


  end

endmodule
`endcelldefine