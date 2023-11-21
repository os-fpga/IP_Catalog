
`timescale 1ns/1ps
`celldefine
//
// PLL simulation model
// Phase locked loop
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module post_div #(
  parameter  div = 2
)(
  input fref,
  input mes_done, 
  input rst_n, 
  input realtime vco_time, 
  output logic fout
);
  logic fc;
  clk_gen post_div_clk_gen
  (
    .clk(fc)
  );    // generate the clock at any frequency
  realtime half_cycle_fout;                   // time period to be set of the post vco clock 
  realtime fout_time;
  always@(posedge fref)                 
  begin
    if (mes_done) begin                         // we can generate both the clocks as we have the reference period of the FREF
      half_cycle_fout =  vco_time*div;  // No need to divide by two because we are using already the half cycle
      if(half_cycle_fout != 0)
        post_div_clk_gen.set_half_cycle(half_cycle_fout);  // reset the time period of the post vco clock
    end
  end
  assign fout_time = half_cycle_fout;
  assign fout = rst_n==1'b1 ?  fc:1'b0;
endmodule


interface clk_gen(
  output bit clk
);
  realtime  half_cycle;
  initial begin
    half_cycle = 10;
    clk = 0;
    forever #half_cycle clk = ~clk;
  end
  function void set_half_cycle(input realtime c);
    begin
      if (half_cycle == 0) begin
        $display("Error - can't set clock half_cycle to 0");
      end else begin
        half_cycle = c;
      end
    end
  endfunction
endinterface


module measure (
  input signal,
  output time period,
  output reg measured
);
  reg last_time_valid = 0;
  time last_time;
  always @(posedge signal) begin
    if (last_time_valid) begin
      period = $time - last_time;
      last_time_valid = 0;
      measured <= 1'b1;
    end else begin
      last_time = $time;
      last_time_valid = 1'b1;
      measured <= 1'b0;
    end
  end
endmodule



module PLL #(
  parameter DIVIDE_CLK_IN_BY_2 = "FALSE", // Enable input divider (TRUE/FALSE)
  parameter PLL_MULT = 16, // Clock multiplier value (16-1000)
  parameter PLL_DIV = 1, // Clock divider value (1-63)
  parameter CLK_OUT0_DIV = 2, // CLK_OUT0 divider value (2,3,4,5,6,7,8,10,12,16,20.24.32.40,48,64) 
  parameter CLK_OUT1_DIV = 2, // CLK_OUT1 divider value (2,3,4,5,6,7,8,10,12,16,20.24.32.40,48,64)
  parameter CLK_OUT2_DIV = 2, // CLK_OUT2 divider value (2,3,4,5,6,7,8,10,12,16,20.24.32.40,48,64)
  parameter CLK_OUT3_DIV = 2 //  CLK_OUT3 divider value (2,3,4,5,6,7,8,10,12,16,20.24.32.40,48,64)
) (
  input  PLL_EN, // PLL Enable
  input  CLK_IN, // Clock input
  input  CLK_OUT0_EN, // Enable CLK_OUT0
  input  CLK_OUT1_EN, // Enable CLK_OUT1
  input  CLK_OUT2_EN, // Enable CLK_OUT2
  input  CLK_OUT3_EN, // Enable CLK_OUT3
  output CLK_OUT0, // CLK_OUT0 output
  output CLK_OUT1, // CLK_OUT1 output
  output CLK_OUT2, // CLK_OUT2 output
  output CLK_OUT3, // CLK_OUT3 output
  output GEARBOX_FAST_CLK, // Gearbox fast clock output
  output LOCK, // PLL lock signal
);

time measured_fref_per;                   // time period of input clk FREF
logic pre_div_out;				// output clk of the pre divider circuit 
logic mes_done;               		// check signal when time period is calcuated it is set to high
realtime half_cycle_prediv;                           // time period of the initial clock  
logic post_vco_out;  // clock which s at the output of the vco
realtime half_cycle_vco;                   // time period to be set of the post vco clock 
logic fc0, fc1,fc2,fc3, fout_postdiv;
realtime half_cycle_fout0,half_cycle_fout1,half_cycle_fout2,half_cycle_fout3;   
int counter=0;
logic DELAY_LOCK =1'b0;//

clk_gen pre_div_clk (
  .clk(pre_div_out)
);    		// start generating the clock at any frequency

measure i_m1 (
  .signal(CLK_IN), 
  .period(measured_fref_per), 
  .measured(mes_done)
  );     // measure the time period of the initial clock FREF
                      
always@(posedge CLK_IN) begin
  if (mes_done && (DIVIDE_CLK_IN_BY_2=="TRUE"))
  begin
      half_cycle_prediv = (measured_fref_per*PLL_DIV);    // The time period of the pre divider clock will be initial will be the time period of CLK_IN* DIV_CLK_IN 
      if(half_cycle_prediv != 0)
        pre_div_clk.set_half_cycle(half_cycle_prediv);       // Update the time period of predivider output clock.
  end
  else  if (mes_done && (DIVIDE_CLK_IN_BY_2=="FALSE"))
  begin
      half_cycle_prediv = (measured_fref_per*PLL_DIV)/2;    // The time period of the pre divider clock will be initial will be the time period of CLK_IN* DIV_CLK_IN 
      if(half_cycle_prediv != 0)
        pre_div_clk.set_half_cycle(half_cycle_prediv);       // Update the time period of predivider output clock.
  end
end

//VCO Generation
clk_gen post_vco_clk (
  .clk(post_vco_out)
);   // generate the clock at any frequency

always@(posedge CLK_IN) begin
  if (mes_done)                          // we can generate both the clocks as we have the reference period of the CLK_IN
  begin
    half_cycle_vco =  half_cycle_prediv/PLL_MULT;  // No need to divide by two because we are using already the half cycle
    if(half_cycle_vco != 0)
      post_vco_clk.set_half_cycle(half_cycle_vco);  // reset the time period of the post vco clock
  end
end

post_div #(.div(CLK_OUT0_DIV))
pd0
(
  .fref(CLK_IN), 
  .mes_done(mes_done),
  .rst_n(CLK_OUT0_EN), 
  .vco_time(half_cycle_vco),  
  .fout(CLK_OUT0)
  //.fout_time(half_cycle_fout0) 
  );
post_div #(.div(CLK_OUT1_DIV))
pd1
(
  .fref(CLK_IN), 
  .mes_done(mes_done),
  .rst_n(CLK_OUT1_EN), 
  .vco_time(half_cycle_vco), 
  .fout(CLK_OUT1)
  //.fout_time(half_cycle_fout1)
  );
post_div #(.div(CLK_OUT2_DIV))
pd2
(
  .fref(CLK_IN), 
  .mes_done(mes_done),
  .rst_n(CLK_OUT2_EN),
  .vco_time(half_cycle_vco), 
  .fout(CLK_OUT2)
  //.fout_time(half_cycle_fout2)
  );
post_div #(.div(CLK_OUT3_DIV))
pd3
(
  .fref(CLK_IN), 
  .mes_done(mes_done),
  .rst_n(CLK_OUT3_EN), 
  .vco_time(half_cycle_vco),  
  .fout(CLK_OUT3)
  //.fout_time(half_cycle_fout3) 
  );

  post_div #(.div(2))
  div2

(
  .fref(GEARBOX_FAST_CLK), 
  .mes_done(mes_done),
  .rst_n(CLK_OUT0_EN), 
  .vco_time(half_cycle_vco), 
  .fout(fout_postdiv)
  //.fout_time(half_cycle_fout1)
  );


// as per specification the lock is guaranted after the 2000 pfd (phase frequency detector) cycles. In the simulation model there is no pfd so a lock is set 
// as we will get the output from the pre divider
always @(posedge CLK_IN)
begin
    counter = counter + 1;
    if (counter == PLL_DIV)
        assign DELAY_LOCK = 1'b1;
end

assign LOCK = ~PLL_EN ? 1'b0 : DELAY_LOCK;
assign GEARBOX_FAST_CLK = post_vco_out;

 initial begin
    case(DIVIDE_CLK_IN_BY_2)
      "TRUE" ,
      "FALSE": begin end
      default: begin
        $display("\nError: PLL instance %m has parameter DIVIDE_CLK_IN_BY_2 set to %s.  Valid values are TRUE, FALSE\n", DIVIDE_CLK_IN_BY_2);
        #1 $stop ;
      end
    endcase

    if ((PLL_MULT < 16) || (PLL_MULT > 1000)) begin
       $display("PLL instance %m PLL_MULT set to incorrect value, %d.  Values must be between 16 and 1000.", PLL_MULT);
    #1 $stop;
    end

    if ((PLL_DIV < 1) || (PLL_DIV > 63)) begin
       $display("PLL instance %m PLL_DIV set to incorrect value, %d.  Values must be between 1 and 63.", PLL_DIV);
    #1 $stop;
    end
    case(CLK_OUT0_DIV)
      2 ,
      3 ,
      4 ,
      5 ,
      6 ,
      8 ,
      10 ,
      12 ,
      16 ,
      20 ,
      24 ,
      32 ,
      40 ,
      48 ,
      64: begin end
      default: begin
        $display("\nError: PLL instance %m has parameter CLK_OUT0_DIV set to %s.  Valid values are 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64\n", CLK_OUT0_DIV);
        #1 $stop ;
      end
    endcase
    case(CLK_OUT1_DIV)
      2 ,
      3 ,
      4 ,
      5 ,
      6 ,
      8 ,
      10 ,
      12 ,
      16 ,
      20 ,
      24 ,
      32 ,
      40 ,
      48 ,
      64: begin end
      default: begin
        $display("\nError: PLL instance %m has parameter CLK_OUT1_DIV set to %s.  Valid values are 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64\n", CLK_OUT1_DIV);
        #1 $stop ;
      end
    endcase
    case(CLK_OUT2_DIV)
      2 ,
      3 ,
      4 ,
      5 ,
      6 ,
      8 ,
      10 ,
      12 ,
      16 ,
      20 ,
      24 ,
      32 ,
      40 ,
      48 ,
      64: begin end
      default: begin
        $display("\nError: PLL instance %m has parameter CLK_OUT2_DIV set to %s.  Valid values are 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64\n", CLK_OUT2_DIV);
        #1 $stop ;
      end
    endcase
    case(CLK_OUT3_DIV)
      2 ,
      3 ,
      4 ,
      5 ,
      6 ,
      8 ,
      10 ,
      12 ,
      16 ,
      20 ,
      24 ,
      32 ,
      40 ,
      48 ,
      64: begin end
      default: begin
        $display("\nError: PLL instance %m has parameter CLK_OUT3_DIV set to %s.  Valid values are 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64\n", CLK_OUT3_DIV);
        #1 $stop ;
      end
    endcase

  end

endmodule
`endcelldefine
