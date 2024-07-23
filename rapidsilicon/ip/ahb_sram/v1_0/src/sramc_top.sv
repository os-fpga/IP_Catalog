// Name       : sramc_top
// Version    : 1.0
// Date       : 2018-06-16
// Description: toplevel of sramc and ahb, including sram8x8k and ahb_slave_interface
//----------------------------------------------------------------------------------------

module sramc_top # (	

parameter SRAM_DATA_WIDTH = 8,
parameter SRAM_ADDR_WIDTH = 13,
parameter ADDR_WIDTH = 32,
parameter DATA_WIDTH = 32,
parameter HBURST_WIDTH = 3,
parameter HTRANS_WIDTH = 2,
parameter HSIZE_WIDTH = 3,
parameter HRESP_WIDTH =2 )(
	input						sram_clk,
    input                   	hclk,
    input                   	hresetn,
	input						hsel,
	input	[31:0]				haddr,
	input						hwrite,
	input [2:0]					hsize,
	input [2:0]					hburst,
	input	[1:0]				htrans,
	input						hready,
	input	[31:0]				hwdata,
	
	output						hready_resp,
	output[1:0]					hresp,
	output[31:0]				hrdata
);



wire sram_we;
wire [SRAM_ADDR_WIDTH-1:0] sram_addr;
wire [DATA_WIDTH-1:0] sram_wdata;
wire [3:0] bank0_cs;
wire [3:0] bank1_cs;
wire [SRAM_DATA_WIDTH-1:0] sram_b0;
wire [SRAM_DATA_WIDTH-1:0] sram_b1;
wire [SRAM_DATA_WIDTH-1:0] sram_b2;
wire [SRAM_DATA_WIDTH-1:0] sram_b3;
wire [SRAM_DATA_WIDTH-1:0] sram_b4;
wire [SRAM_DATA_WIDTH-1:0] sram_b5;
wire [SRAM_DATA_WIDTH-1:0] sram_b6;
wire [SRAM_DATA_WIDTH-1:0] sram_b7;


	ahb_slave_interface	inst_ahb(
	.hclk(hclk),
	.hresetn(hresetn),
	.hsel(hsel),
	.haddr(haddr),
	.hwrite(hwrite),
	.hsize(hsize),
	.hburst(hburst),
	.htrans(htrans),
	.hready(hready),
	.hwdata(hwdata),
	.hready_resp(hready_resp),
	.hresp(hresp),
	.hrdata(hrdata),
	.sram_we(sram_we),
	.sram_addr(sram_addr),
	.sram_wdata(sram_wdata),
	.bank0_cs(bank0_cs),
	.bank1_cs(bank1_cs),
	.sram_b0(sram_b0),
	.sram_b1(sram_b1),
	.sram_b2(sram_b2),
	.sram_b3(sram_b3),
	.sram_b4(sram_b4),
	.sram_b5(sram_b5),
	.sram_b6(sram_b6),
	.sram_b7(sram_b7)
	);



	sram8x8k inst_srams(
	.sram_clk(sram_clk),
	.sram_we(sram_we),
	.sram_addr(sram_addr),
	.sram_wdata(sram_wdata),
	.bank0_cs(bank0_cs),
	.bank1_cs(bank1_cs),
	.sram_b0(sram_b0),
	.sram_b1(sram_b1),
	.sram_b2(sram_b2),
	.sram_b3(sram_b3),
	.sram_b4(sram_b4),
	.sram_b5(sram_b5),
	.sram_b6(sram_b6),
	.sram_b7(sram_b7)
	);

endmodule