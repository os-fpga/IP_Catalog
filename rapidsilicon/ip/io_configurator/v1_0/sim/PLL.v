`timescale 1ps/10fs
`celldefine
//
// PLL simulation model
// Phase locked loop
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module PLL #(
  parameter DEV_FAMILY = "VIRGO", // Device Family
  parameter DIVIDE_CLK_IN_BY_2 = "FALSE", // Enable input divider (TRUE/FALSE)
  parameter PLL_MULT = 16, // VCO clock multiplier value (16-640)
  parameter PLL_DIV = 1, // VCO clock divider value (1-63)
  parameter PLL_MULT_FRAC = 0, // Fraction mode not supported
  parameter PLL_POST_DIV = 17 // VCO clock post-divider value (17,18,19,20,21,22,23,34,35,36,37,38,39,51,52,53,54,55,68,69,70,71,85,86,87,102,103,119)
) (
  input PLL_EN, // PLL Enable
  input CLK_IN, // Clock input
  output CLK_OUT, // Output clock, frequency is (CLK_IN/PLL_DIV)*(PLL_MULT/(PLL_POST_DIV0*PLL_POST_DIV1))
  output CLK_OUT_DIV2, // CLK_OUT divided by 2 output
  output CLK_OUT_DIV3, // CLK_OUT divided by 3 output
  output CLK_OUT_DIV4, // CLK_OUT divided by 4 output
  output FAST_CLK, // VCO clock output, frequency is (CLK_IN/PLL_DIV)*(PLL_MULT)
  output LOCK // PLL lock signal
);

	localparam      FAST_LOCK      = 0; // Reduce lock time

	localparam real REF_MAX_PERIOD = PLL_MULT_FRAC ? 100000: 200000; //10 MHz or 5 MHz
	localparam real REF_MIN_PERIOD = 833.33                        ; //1200 MHz

	localparam real VCO_MAX_PERIOD = 62500; //16 MHz
	localparam real VCO_MIN_PERIOD = 312.5; //3200 MHz


	localparam LOCK_TIMER = FAST_LOCK ? 10 : 500;

	logic [ 2:0] PLL_POST_DIV0;
	logic [ 2:0] PLL_POST_DIV1;

	assign PLL_POST_DIV0 = PLL_POST_DIV[2:0];
	assign PLL_POST_DIV1 = PLL_POST_DIV[6:4];
//---------------------------
  real         t0                ;
  real         t1                ;
  real         ref_period        ;
  real         vco_period        ;
  real         postdiv_period    ;
  real         old_ref_period    ;
  logic          clk_pll           ;
  logic          pllen_rse         ;
  logic          pllstart       = 0;
  logic          pllstart_ff1   = 0;
  logic          pllstart_ff2   = 0;
  logic          vcostart       = 0;
  logic          vcostart_ff    = 0;
  logic          lose_lock      = 0;
  logic          clk_out_div2   = 0;
  logic          clk_out_div3   = 0;
  logic          clk_out_div4   = 0;
  logic          clk_vco           ;
  logic          clk_postdiv       ;
  integer        div3_count     = 1;
  logic   [ 5:0] PLL_DIV_ff     = 0;
  logic   [11:0] PLL_MULT_ff    = 0;

	logic [$clog2(LOCK_TIMER)-1:0] lock_counter = 0;


	assign pllen_rse = pllstart==1 && pllstart_ff2==0;

	always @ (posedge  CLK_IN) begin
		if(PLL_EN) pllstart <= 1;
		else      pllstart <= 0;

		pllstart_ff1 <= pllstart;
		pllstart_ff2 <= pllstart_ff1;

	end

	always @ (posedge  CLK_IN) begin
		if(pllstart_ff2) vcostart <= 1;
		else             vcostart <= 0;

		vcostart_ff <= vcostart;
	end


	always @ (posedge  CLK_IN) begin
		@(posedge CLK_IN) t0 = $realtime;
		@(posedge CLK_IN) t1 = $realtime;
		ref_period = t1 - t0;
		vco_period = DIVIDE_CLK_IN_BY_2=="TRUE" ? (ref_period*PLL_DIV*2)/PLL_MULT : (ref_period*PLL_DIV)/PLL_MULT;
    postdiv_period = DIVIDE_CLK_IN_BY_2=="TRUE" ? (ref_period*PLL_DIV*2*PLL_POST_DIV0*PLL_POST_DIV1)/PLL_MULT : (ref_period*PLL_DIV*PLL_POST_DIV0*PLL_POST_DIV1)/PLL_MULT;
	end

	always @ (posedge  CLK_IN) begin
		old_ref_period = ref_period;
	end

	initial begin
		clk_vco = 0;
		forever begin
			wait(vcostart_ff)
				#(vco_period/2) clk_vco = PLL_EN ? ~clk_vco : '0;
		end
	end


  initial begin
    clk_postdiv = 0;
    forever begin
      wait(vcostart_ff)
        #(postdiv_period/2) clk_postdiv = PLL_EN ? ~clk_postdiv : '0;
    end
  end  


	always @(posedge CLK_IN) begin
		PLL_DIV_ff  <= PLL_DIV;
		PLL_MULT_ff <= PLL_MULT;
	end

	always @ (posedge  CLK_IN, negedge PLL_EN) begin
		if(LOCK==0 & vcostart) lock_counter <= lock_counter + 1;
		else if(lose_lock || PLL_EN==0 || PLL_MULT_ff!=PLL_MULT || PLL_DIV_ff!=PLL_DIV )     lock_counter <= 0;
	end


	always @(posedge CLK_OUT, negedge PLL_EN)
		if(PLL_EN==0) clk_out_div2 = 1'b0;
		else          clk_out_div2 = ~clk_out_div2;

	always @(CLK_OUT, negedge PLL_EN)
		if(PLL_EN==0) clk_out_div3 = 1'b0;
		else begin
			if (div3_count==2) begin
				clk_out_div3 = ~clk_out_div3;
				div3_count   = 0;
			end else
			div3_count = div3_count + 1;
		end

	always @(posedge clk_out_div2, negedge PLL_EN)
		if(PLL_EN==0) clk_out_div4 = 1'b0;
		else          clk_out_div4 = ~clk_out_div4;


	assign CLK_OUT      = (PLL_POST_DIV0==1 && PLL_POST_DIV0==1) ? clk_vco : clk_postdiv;
	assign CLK_OUT_DIV2 = clk_out_div2;
	assign CLK_OUT_DIV3 = clk_out_div3;
	assign CLK_OUT_DIV4 = clk_out_div4;
	assign FAST_CLK     = clk_vco;
	assign LOCK         = lock_counter >= LOCK_TIMER;



	// Checking for proper CLK_IN and VCO frequencies
	always @ (posedge CLK_IN) begin
		if(pllstart_ff2)begin
			if (ref_period<VCO_MIN_PERIOD) begin
				$fatal(1,"\nError at time %t: PLL instance %m REF clock period %0d fs violates minimum period.\nMust be greater than %0d fs.\n", $realtime, ref_period, VCO_MIN_PERIOD);
			end
			else if (ref_period>VCO_MAX_PERIOD) begin
				$fatal(1,"\nError at time %t: PLL instance %m REF clock period %0d fs violates maximum period.\nMust be less than %0d fs.\n", $realtime, ref_period, VCO_MAX_PERIOD);
			end
		end
	end


	always @ (posedge CLK_IN) begin
		if ((LOCK==1'b1) && (ref_period > old_ref_period*1.05) || (ref_period < old_ref_period*0.95)) begin
			$display("Warning at time %t: PLL instance %m input clock, CLK_IN, changed frequency and lost lock. Current value = %0d fs, old value = %d fs.\n", $realtime, ref_period, old_ref_period);
			lose_lock = 1;
		end
		else lose_lock = 0;
	end

	always @ (posedge FAST_CLK) begin
		if(vcostart_ff) begin
			if (vco_period<VCO_MIN_PERIOD) begin
				$fatal(1,"\nError at time %t: PLL instance %m VCO clock period %0d fs violates minimum period.\nMust be greater than %0d fs.\nTry increasing PLL_DIV or decreasing PLL_MULT values.\n", $realtime, vco_period, VCO_MIN_PERIOD);
			end
			else if (vco_period>VCO_MAX_PERIOD) begin
				$fatal(1,"\nError at time %t: PLL instance %m VCO clock period %0d fs violates maximum period.\nMust be less than %0d fs.\nTry increasing PLL_MULT or decreasing PLL_DIV values.\n", $realtime, vco_period, VCO_MAX_PERIOD);
			end
		end
	end



	// Checking control inputs
	always @ (posedge CLK_IN, posedge PLL_EN) begin
		if(PLL_EN)begin
			if(PLL_POST_DIV0==0)begin
				$fatal(1,"Error at time %t: \n \t PLL instance %m, PLL_POST_DIV0 is equal to zero.\n \t Must be greater than 0", $realtime);
			end

			else if(PLL_POST_DIV1==0)begin
				$fatal(1,"Error at time %t: \n \t PLL instance %m, PLL_POST_DIV1 is equal to zero.\n \t Must be greater than 0", $realtime);
			end


			else if(PLL_POST_DIV1>PLL_POST_DIV0) begin
				$fatal(1,"Error at time %t: PLL_POST_DIV1 > PLL_POST_DIV0\n", $realtime);
			end
		end
	end


`ifndef SYNTHESIS  
	`ifdef TIMED_SIM
	  specparam T1 = 5;
	  specparam T2 = 0.5;
  
		specify
  
				  (CLK_IN => CLK_OUT)      = (T1);
				  (CLK_IN => CLK_OUT_DIV2) = (T1);
				  (CLK_IN => CLK_OUT_DIV3) = (T1);
				  (CLK_IN => CLK_OUT_DIV4) = (T1);
				  (CLK_IN => FAST_CLK)     = (T1);
  
				  (negedge CLK_IN => (LOCK +: 0)) = (T1);
				  (negedge PLL_EN => (LOCK +: 0)) = (T1);
				  (posedge CLK_IN => (LOCK +: 0)) = (T1);
				  (posedge PLL_EN => (LOCK +: 0)) = (T1);
  
				  $setuphold (posedge CLK_IN, negedge PLL_EN, T2, notifier);
				  $setuphold (posedge CLK_IN, posedge PLL_EN, T2, notifier);
				  $setuphold (negedge CLK_IN, negedge PLL_EN, T2, notifier);
				  $setuphold (negedge CLK_IN, posedge PLL_EN, T2, notifier);
		endspecify
	`endif // `ifdef TIMED_SIM  
`endif //  `ifndef SYNTHESIS
   initial begin
    case(DEV_FAMILY)
      "VIRGO": begin end
      default: begin
        $fatal(1,"\nError: PLL instance %m has parameter DEV_FAMILY set to %s.  Valid values are VIRGO\n", DEV_FAMILY);
      end
    endcase
    case(DIVIDE_CLK_IN_BY_2)
      "TRUE" ,
      "FALSE": begin end
      default: begin
        $fatal(1,"\nError: PLL instance %m has parameter DIVIDE_CLK_IN_BY_2 set to %s.  Valid values are TRUE, FALSE\n", DIVIDE_CLK_IN_BY_2);
      end
    endcase

    if ((PLL_MULT < 16) || (PLL_MULT > 640)) begin
       $fatal(1,"PLL instance %m PLL_MULT set to incorrect value, %d.  Values must be between 16 and 640.", PLL_MULT);
    end

    if ((PLL_DIV < 1) || (PLL_DIV > 63)) begin
       $fatal(1,"PLL instance %m PLL_DIV set to incorrect value, %d.  Values must be between 1 and 63.", PLL_DIV);
    end
    case(PLL_MULT_FRAC)
      0: begin end
      default: begin
        $fatal(1,"\nError: PLL instance %m has parameter PLL_MULT_FRAC set to %d.  Valid values are 0\n", PLL_MULT_FRAC);
      end
    endcase
    case(PLL_POST_DIV)
      17 ,
      18 ,
      19 ,
      20 ,
      21 ,
      22 ,
      23 ,
      34 ,
      35 ,
      36 ,
      37 ,
      38 ,
      39 ,
      51 ,
      52 ,
      53 ,
      54 ,
      55 ,
      68 ,
      69 ,
      70 ,
      71 ,
      85 ,
      86 ,
      87 ,
      102 ,
      103 ,
      119: begin end
      default: begin
        $fatal(1,"\nError: PLL instance %m has parameter PLL_POST_DIV set to %d.  Valid values are 17, 18, 19, 20, 21, 22, 23, 34, 35, 36, 37, 38, 39, 51, 52, 53, 54, 55, 68, 69, 70, 71, 85, 86, 87, 102, 103, 119\n", PLL_POST_DIV);
      end
    endcase

  end

endmodule
`endcelldefine