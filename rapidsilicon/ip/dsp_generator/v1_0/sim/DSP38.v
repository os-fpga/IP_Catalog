`timescale 1ns/1ps
`celldefine
//
// DSP38 simulation model
// Paramatizable 20x18-bit multiplier accumulator
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module DSP38 #(
  parameter DSP_MODE = "MULTIPLY_ACCUMULATE", // DSP arithmetic mode (MULTIPLY/MULTIPLY_ADD_SUB/MULTIPLY_ACCUMULATE)
  parameter [19:0] COEFF_0 = 20'h00000, // 20-bit A input coefficient 0
  parameter [19:0] COEFF_1 = 20'h00000, // 20-bit A input coefficient 1
  parameter [19:0] COEFF_2 = 20'h00000, // 20-bit A input coefficient 2
  parameter [19:0] COEFF_3 = 20'h00000, // 20-bit A input coefficient 3
  parameter OUTPUT_REG_EN = "TRUE", // Enable output register (TRUE/FALSE)
  parameter INPUT_REG_EN = "TRUE" // Enable input register (TRUE/FALSE)
) (
  input [19:0] A, // 20-bit data input for multipluier or accumulator loading
  input [17:0] B, // 18-bit data input for multiplication
  input [5:0] ACC_FIR, // 6-bit left shift A input
  output [37:0] Z, // 38-bit data output
  output reg [17:0] DLY_B = 18'h00000, // 18-bit B registered output
  input CLK, // Clock
  input RESET, // Active high reset
  input [2:0] FEEDBACK, // 3-bit feedback input selects coefficient
  input LOAD_ACC, // Load accumulator input
  input SATURATE, // Saturate enable
  input [5:0] SHIFT_RIGHT, // 6-bit Shift right
  input ROUND, // Round
  input SUBTRACT, // Add or subtract
  input UNSIGNED_A, // Selects signed or unsigned data for A input
  input UNSIGNED_B // Selects signed or unsigned data for B input
);

	// registers
	reg subtract_reg = 1'b0;
	reg [5:0] acc_fir_reg = 6'h00;
	reg [2:0] feedback_reg = 3'h0;
	reg [5:0] shift_right_reg1 = 6'h00;
	reg [5:0] shift_right_reg2 = 6'h00;
	reg round_reg1 = 1'b0;
	reg round_reg2 = 1'b0;
	reg saturate_reg1 = 1'b0;
	reg saturate_reg2 = 1'b0;
	reg load_acc_reg = 1'b0;
	reg [19:0] a_reg = 20'h00000;
	reg [17:0] b_reg = 18'h00000;
	reg unsigned_a_reg = 1'b1;
	reg unsigned_b_reg = 1'b1;



	reg subtract_int = 1'b0;
	reg [5:0] acc_fir_int = 6'h00;
	reg [2:0] feedback_int = 3'h0;
	reg [5:0] shift_right_int = 6'h00;
	reg round_int = 1'b0;
	reg saturate_int = 1'b0;
	reg load_acc_int = 1'b0;
	reg [19:0] a_int = 20'h00000;
	reg [17:0] b_int = 18'h00000;
	reg unsigned_a_int = 1'b1;
	reg unsigned_b_int = 1'b1;
	reg signed [63:0] accumulator = 64'h0000000000000000;
	reg signed [63:0] add_sub_in = 64'h0000000000000000;
	reg signed [63:0] mult_out = 64'h0000000000000000;
	reg signed [63:0] add_sub_out = 64'h0000000000000000;
	reg signed [63:0] pre_shift = 64'h0000000000000000;
	reg signed [63:0] shift_right = 64'h0000000000000000;
	reg signed [63:0] round = 64'h0000000000000000;
	reg signed [37:0] saturate = 38'h00000000;
	reg [37:0] z_out = 38'h00000000;
	reg [37:0] z_out_reg = 38'h00000000;



	reg [19:0] mult_a = 20'h00000;
	reg [17:0] mult_b = 18'h00000;

	// pipelining
	always @(posedge CLK or posedge RESET)
	begin
		if (RESET) 
		begin
			subtract_reg <= 1'b0;
			acc_fir_reg <= 6'h00;
			feedback_reg <= 1'b0;
			shift_right_reg1 <= 6'h00;
			shift_right_reg2 <= 6'h00;
			round_reg1 <= 1'b0;
			round_reg2 <= 1'b0;
			saturate_reg1 <= 1'b0;
			saturate_reg2 <= 1'b0;
			load_acc_reg <= 1'b0;
			a_reg <= 20'h00000;
			b_reg <= 18'h00000;
			unsigned_a_reg <= 1'b1;
			unsigned_b_reg <= 1'b1;
		end
		else 
		begin
			subtract_reg <= SUBTRACT;
			acc_fir_reg <= ACC_FIR;
			feedback_reg <= FEEDBACK;
			shift_right_reg1 <= SHIFT_RIGHT;
			shift_right_reg2 <= shift_right_reg1;
			round_reg1 <= ROUND;
			round_reg2 <= round_reg1;
			saturate_reg1 <= SATURATE;
			saturate_reg2 <= saturate_reg1;
			load_acc_reg <= LOAD_ACC;
			a_reg <= A;
			b_reg <= B;
			unsigned_a_reg <= UNSIGNED_A;
			unsigned_b_reg <= UNSIGNED_B;


		end
	end

	always @(*) 
	begin
		if (INPUT_REG_EN == "TRUE")  
		begin
			a_int = a_reg;
    	    b_int = b_reg;
			subtract_int = subtract_reg;
			acc_fir_int = acc_fir_reg;
			feedback_int = feedback_reg;
			load_acc_int = load_acc_reg;
			unsigned_a_int = unsigned_a_reg;
			unsigned_b_int = unsigned_b_reg;
			shift_right_int = (DSP_MODE== "MULTIPLY_ACCUMULATE")?shift_right_reg2:shift_right_reg1;
			round_int = (DSP_MODE== "MULTIPLY_ACCUMULATE")?round_reg2:round_reg1;
			saturate_int = (DSP_MODE== "MULTIPLY_ACCUMULATE")?saturate_reg2:saturate_reg1;
		end 
		else 
		begin
			a_int = A;
    	    b_int = B;
			subtract_int = SUBTRACT;
			acc_fir_int = ACC_FIR;
			feedback_int = FEEDBACK;
			load_acc_int = LOAD_ACC;
			unsigned_a_int = UNSIGNED_A;
			unsigned_b_int = UNSIGNED_B;
			shift_right_int = (DSP_MODE== "MULTIPLY_ACCUMULATE")?shift_right_reg1:SHIFT_RIGHT;
			round_int = (DSP_MODE== "MULTIPLY_ACCUMULATE")?round_reg1:ROUND;
			saturate_int = (DSP_MODE== "MULTIPLY_ACCUMULATE")?saturate_reg1:SATURATE;

    	end
	end

	//  Feedback paths
	always @(*)
	begin
    	case (feedback_int)
      		3'b000:	begin
        				mult_a = a_int;
        				mult_b = b_int;
        				add_sub_in = accumulator;
					end
      		3'b001:	begin
        				mult_a = a_int;
        				mult_b = b_int;
        				add_sub_in = 64'h0000000000000000;
     				end
      		3'b010:	begin
        				mult_a = a_int;
        				mult_b = 18'h00000;
        				add_sub_in = (unsigned_a_int)? a_int<<acc_fir_int : {{44{a_int[19]}},a_int}<<acc_fir_int;
      				end
			3'b011:	begin
        				mult_a = accumulator;
        				mult_b = b_int;
        				add_sub_in = (unsigned_a_int)? a_int<<acc_fir_int : {{44{a_int[19]}},a_int}<<acc_fir_int;
					end
      		3'b100:	begin
        				mult_a = COEFF_0;
        				mult_b = b_int;
        				add_sub_in = (unsigned_a_int)? a_int<<acc_fir_int : {{44{a_int[19]}},a_int}<<acc_fir_int;
      				end
      		3'b101:	begin 
        				mult_a = COEFF_1;
        				mult_b = b_int;
        				add_sub_in = (unsigned_a_int)? a_int<<acc_fir_int : {{44{a_int[19]}},a_int}<<acc_fir_int;
					end
			3'b110:	begin 
						mult_a = COEFF_2;
						mult_b = b_int;
						add_sub_in = (unsigned_a_int)? a_int<<acc_fir_int : {{44{a_int[19]}},a_int}<<acc_fir_int;
					end
			3'b111:	begin
        				mult_a <= COEFF_3;
        				mult_b <= b_int;
        				add_sub_in = (unsigned_a_int)? a_int<<acc_fir_int : {{44{a_int[19]}},a_int}<<acc_fir_int;
					end
    	endcase
	end
	
	// Multiplier
	always@(*)
	begin
		case({unsigned_a_int,unsigned_b_int})
			2'b00:
				mult_out = $signed(mult_a) * $signed(mult_b);
			2'b01:
				mult_out = $signed(mult_a) * $signed({{1'b0},mult_b});
			2'b10:
				mult_out = $signed({{1'b0},mult_a}) * $signed(mult_b);
			2'b11:
				mult_out = mult_a * mult_b;
		endcase
	end	

	// Adder/Subtractor
	always@(*)
	begin
		if(subtract_int)
			add_sub_out = $signed(add_sub_in) - $signed(mult_out);
		else
			add_sub_out = add_sub_in + mult_out;
	end

	// Accumulator
	always @(posedge CLK or posedge RESET)
	begin
		if(RESET)
			accumulator <= 64'h0000000000000000;
	    else if(load_acc_int)
			accumulator <= add_sub_out;
		else
			accumulator <= accumulator;
	end
  
	// Shift Round Saturate
	always@(*)
	begin
		pre_shift   = (DSP_MODE == "MULTIPLY_ACCUMULATE")? accumulator : add_sub_out;
		shift_right = pre_shift >>> shift_right_int;
		round       = (round_int && shift_right_int>0)? (pre_shift[shift_right_int-1]==1)?shift_right+1:shift_right:shift_right; 
	
		if(saturate_int)
		begin
			if(unsigned_a_int && unsigned_b_int)
			begin
				if($signed(round)<0)
					saturate = 38'h0000000000;
				else if($signed(round)>38'h3fffffffff)
					saturate = 38'h3fffffffff;
				else
					saturate = round[37:0];
			end
			else 
			begin
				if($signed(round)>$signed(38'h1fffffffff))
                    saturate = 38'h1fffffffff;
                else if($signed(round)<$signed(38'h2000000000))
                    saturate = 38'h2000000000;
				else
					saturate = round[37:0];
			end
			
		end
		else 
			saturate = round[37:0];

			z_out = (DSP_MODE== "MULTIPLY")? mult_out:saturate;
	end

 
	// output register
	always @(posedge CLK or posedge RESET)
	begin
		if(RESET)
		begin
			DLY_B <= 18'h00000;
			z_out_reg <= 38'h00000000;
		end
		else 
		begin
			DLY_B <= B;
			z_out_reg <= z_out;	
		end
	end

	assign Z = (OUTPUT_REG_EN == "TRUE")?z_out_reg:z_out;

	// If ACC_FIR is greater than 43, result is invalid
	always @(ACC_FIR)
		if (ACC_FIR > 43)
			$display("WARNING: DSP38 instance %m ACC_FIR input is %d which is greater than 43 which serves no function", ACC_FIR);

 initial begin
    case(DSP_MODE)
      "MULTIPLY" ,
      "MULTIPLY_ADD_SUB" ,
      "MULTIPLY_ACCUMULATE": begin end
      default: begin
        $display("\nError: DSP38 instance %m has parameter DSP_MODE set to %s.  Valid values are MULTIPLY, MULTIPLY_ADD_SUB, MULTIPLY_ACCUMULATE\n", DSP_MODE);
        #1 $stop ;
      end
    endcase
    case(OUTPUT_REG_EN)
      "TRUE" ,
      "FALSE": begin end
      default: begin
        $display("\nError: DSP38 instance %m has parameter OUTPUT_REG_EN set to %s.  Valid values are TRUE, FALSE\n", OUTPUT_REG_EN);
        #1 $stop ;
      end
    endcase
    case(INPUT_REG_EN)
      "TRUE" ,
      "FALSE": begin end
      default: begin
        $display("\nError: DSP38 instance %m has parameter INPUT_REG_EN set to %s.  Valid values are TRUE, FALSE\n", INPUT_REG_EN);
        #1 $stop ;
      end
    endcase

  end

endmodule
`endcelldefine