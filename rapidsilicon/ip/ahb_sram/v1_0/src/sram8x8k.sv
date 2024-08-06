// Name       : sram8x8k
// Version    : 1.0
// Date       : 2018-06-16
// Description: Toplevel of sram from eight 8kbyte sync singal-port srams, including 2 banks. 
//				Each bank contains 4 srams.
//----------------------------------------------------------------------------------------

module sram8x8k # (	

parameter SRAM_DATA_WIDTH = 8,
parameter SRAM_ADDR_WIDTH = 13,
parameter DATA_WIDTH	  = 32)(
	input sram_clk, //sramclock
	input							sram_we,
	input	[SRAM_ADDR_WIDTH-1:0]	sram_addr,
	input	[DATA_WIDTH-1:0]		sram_wdata,
	input	[3:0] 					bank0_cs,
	input	[3:0] 					bank1_cs,
	output	[SRAM_DATA_WIDTH-1:0]	sram_b0,
	output	[SRAM_DATA_WIDTH-1:0]	sram_b1,
	output	[SRAM_DATA_WIDTH-1:0]	sram_b2,
	output	[SRAM_DATA_WIDTH-1:0]	sram_b3,
	output	[SRAM_DATA_WIDTH-1:0]	sram_b4,
	output	[SRAM_DATA_WIDTH-1:0]	sram_b5,
	output	[SRAM_DATA_WIDTH-1:0]	sram_b6,
	output	[SRAM_DATA_WIDTH-1:0]	sram_b7
);
	sram sram_block0(
		.clk		(sram_clk),
		.addr		(sram_addr),
		.data_in	(sram_wdata[7:0]),
		.ce			(bank0_cs[0]),
		.we			(sram_we),
		.data_out	(sram_b0)
	);

	sram sram_block1(
		.clk		(sram_clk),
		.addr		(sram_addr),
		.data_in	(sram_wdata[15:8]),
		.ce			(bank0_cs[1]),
		.we			(sram_we),
		.data_out	(sram_b1)
	);

	sram sram_block2(
		.clk		(sram_clk),
		.addr		(sram_addr),
		.data_in	(sram_wdata[23:16]),
		.ce			(bank0_cs[2]),
		.we			(sram_we),
		.data_out	(sram_b2)
	);

	sram sram_block3(
		.clk		(sram_clk),
		.addr		(sram_addr),
		.data_in	(sram_wdata[31:24]),
		.ce			(bank0_cs[3]),
		.we			(sram_we),
		.data_out	(sram_b3)
	);

	sram sram_block4(
		.clk		(sram_clk),
		.addr		(sram_addr),
		.data_in	(sram_wdata[7:0]),
		.ce			(bank1_cs[0]),
		.we			(sram_we),
		.data_out	(sram_b4)
	);

	sram sram_block5(
		.clk		(sram_clk),
		.addr		(sram_addr),
		.data_in	(sram_wdata[15:8]),
		.ce			(bank1_cs[1]),
		.we			(sram_we),
		.data_out	(sram_b5)
	);

	sram sram_block6(
		.clk		(sram_clk),
		.addr		(sram_addr),
		.data_in	(sram_wdata[23:16]),
		.ce			(bank1_cs[2]),
		.we			(sram_we),
		.data_out	(sram_b6)
	);

	sram sram_block7(
		.clk		(sram_clk),
		.addr		(sram_addr),
		.data_in	(sram_wdata[31:24]),
		.ce			(bank1_cs[3]),
		.we			(sram_we),
		.data_out	(sram_b7)
	);

endmodule



















