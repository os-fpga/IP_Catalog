`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:  
// Engineer: anxu chan
// 
// Create Date:    16:17:14 08/02/2017 
// Design Name:    FIR filter
// Module Name:    fir 
// Project Name:   FirDesign
// Target Devices: Xilinix V5
// Description: fir res file
// Revision: 1.0
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module fir(
	input clk,
	input rst,
	input wire signed [17:0] filter_in,
	output reg signed [37:0] filter_out
    );
	
	parameter word_width = 18;
	parameter order = 4;

	// define delay unit , input width is 16  , filter order is 16
	reg signed [word_width-1:0] delay_pipeline[order:0];
	
	// define coef
	wire signed [word_width-1:0]  coef[order:0];
	assign coef[0] = 20'd2;
	assign coef[1] = 20'd4;
	assign coef[2] = 20'd4;
	assign coef[3] = 20'd2;

	// define multipler
	reg signed [31:0]  product[3:0];

	// define sum buffer
	reg signed [31:0]  sum_buf;	

	// define input data buffer
	reg signed [17:0] data_in_buf;

	// data buffer
	always @(posedge clk or negedge rst) begin
		if (rst) begin
			data_in_buf <= 0;
		end
		else begin
			data_in_buf <= filter_in;
		end
	end

	// delay units pipeline
	always @(posedge clk or negedge rst) begin
		if (rst) begin
			delay_pipeline[0] <= 0 ;
			delay_pipeline[1] <= 0 ;
			delay_pipeline[2] <= 0 ;
			delay_pipeline[3] <= 0 ;
		end 
		else begin
			delay_pipeline[0] <= data_in_buf ;
			delay_pipeline[1] <= delay_pipeline[0] ;
			delay_pipeline[2] <= delay_pipeline[1] ;
			delay_pipeline[3] <= delay_pipeline[2] ;
		end
	end

	// implement product with coef 
	always @(posedge clk or negedge rst) begin
		if (rst) begin
			product[0] <= 0;
			product[1] <= 0;
			product[2] <= 0;
			product[3] <= 0;
		end
		else begin
			product[0] <= coef[0] * delay_pipeline[0];
			product[1] <= coef[1] * delay_pipeline[1];
			product[2] <= coef[2] * delay_pipeline[2];
			product[3] <= coef[3] * delay_pipeline[3];
		end
	end

	// accumulation
	always @(posedge clk or negedge rst) begin
		if (rst) begin
			sum_buf <= 0;
		end
		else begin
			sum_buf <= product[0] + product[1]+ product[2]+ product[3];
		end
	end

	always @(sum_buf) begin
		if (rst) begin
			filter_out = 0;
		end
		else begin
			filter_out = sum_buf;
		end
	end

initial begin
$dumpfile("fir.vcd");
  for (integer idx = 0; idx < 4; idx = idx + 1) $dumpvars(0, product[idx]);
  for (integer idx = 0; idx < 4; idx = idx + 1) $dumpvars(0, delay_pipeline[idx]);
end

endmodule
