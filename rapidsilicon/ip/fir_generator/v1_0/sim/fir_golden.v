`timescale 1ns / 1ps

module fir_golden #(
	parameter INPUT_WIDTH = 18,
	parameter NUMBER_TAPS = 4
)
(
	input clk,
	input rst,
	input wire signed [INPUT_WIDTH - 1:0] filter_in,
	output reg signed [37:0] filter_out
);

	reg signed [INPUT_WIDTH-1:0] delay_pipeline[NUMBER_TAPS - 1:0];
	integer i = 0;
	reg signed [INPUT_WIDTH - 1:0] data_in_buff;
	reg signed [INPUT_WIDTH - 1:0] dout_mem [NUMBER_TAPS - 1: 0];
	reg signed [INPUT_WIDTH - 1:0] dout_golden_mem [NUMBER_TAPS - 1: 0];

	wire signed [19:0] coeff[NUMBER_TAPS - 1:0];

	reg signed [21:0] product[NUMBER_TAPS - 1:0];

	always @(posedge clk) begin
    	if (rst) begin
    	    filter_out <= 0;
			data_in_buff <= 0;
			for (i = 0; i < NUMBER_TAPS; i = i + 1) begin
        	    delay_pipeline[i] <= 0;
				product[i] <= 0;
        	end
    	end else begin
			data_in_buff <= filter_in;
			for (i = 0; i < NUMBER_TAPS; i = i + 1) begin
				if (i == 0) begin
					delay_pipeline[i] <= data_in_buff;
				end else begin
					delay_pipeline[i] <= delay_pipeline[i-1];
				end
    		    product[i] <= coeff[i] * delay_pipeline[i];
    		end

        	filter_out <= product[0];
    	end
	end

endmodule
