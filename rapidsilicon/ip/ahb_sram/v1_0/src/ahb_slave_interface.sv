// Name       : AHB_Slave_Interface
// Version    : 1.0
// Date       : 2018-06-16
// Description: ahb interface and arbiter
//				based on IHI0033B_B_amba_5_ahb_protocol_spec.pdf
//----------------------------------------------------------------------------------------

module ahb_slave_interface	# (	

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
	output[31:0]				hrdata,


	output							sram_we,
	output	[SRAM_ADDR_WIDTH-1:0]	sram_addr,
	output	[DATA_WIDTH-1:0]		sram_wdata,
	output	[3:0] 					bank0_cs,
	output	[3:0] 					bank1_cs,
	input	[SRAM_DATA_WIDTH-1:0]	sram_b0,
	input	[SRAM_DATA_WIDTH-1:0]	sram_b1,
	input	[SRAM_DATA_WIDTH-1:0]	sram_b2,
	input	[SRAM_DATA_WIDTH-1:0]	sram_b3,
	input	[SRAM_DATA_WIDTH-1:0]	sram_b4,
	input	[SRAM_DATA_WIDTH-1:0]	sram_b5,
	input	[SRAM_DATA_WIDTH-1:0]	sram_b6,
	input	[SRAM_DATA_WIDTH-1:0]	sram_b7
);
	parameter
	IDLE   = 2'b00,
	BUSY   = 2'b01,
	NONSEQ = 2'b10,
	SEQ    = 2'b11;

	//reg for ahb input signals
	logic	[ADDR_WIDTH-1:0]	haddr_r;
	logic	[HBURST_WIDTH-1:0]	hburst_r;
	logic	[HTRANS_WIDTH-1:0]	htrans_r;
	logic	[HSIZE_WIDTH-1:0]	hsize_r;
	logic	hwrite_r;

	logic	[3:0]	sram_cs; //select sram in one bank. second sram:0010
	logic	[1:0]	sram_sel; //select sram in one bank. second sram:01
	logic	[1:0]	hsize_sel; //set data length: 8,16,32
	logic 	bank_sel;
	logic 	srams_en;

	logic	[SRAM_ADDR_WIDTH+3-1:0]	srams_addr; //addr for all 8 sram
	logic	[DATA_WIDTH-1:0]	sram_data_out; //data read from sram and send to AHB bus
	
	assign hready_resp = 1'b1;
	assign hresp = 2'b00;

	//sram enable and sram write enable
	assign srams_en = (htrans_r == NONSEQ) || (htrans_r == SEQ);
	assign sram_we = srams_en && hwrite_r;

	//data io
	assign sram_data_out = (bank_sel) ? // if 0, bank0 else bank1
	{sram_b3, sram_b2, sram_b1, sram_b0} :
	{sram_b7, sram_b6, sram_b5, sram_b4} ;
	assign hrdata = sram_data_out;
	assign sram_wdata = hwdata;

	//addr	
	// srams_addr[14:0] for 4 8kbyte srams in one bank
	// srams_addr[15] for bank select
	assign srams_addr = haddr_r[SRAM_ADDR_WIDTH+3-1:0];
	assign sram_addr = srams_addr[14:2]; // addr for 1byte on each sram														

	assign bank_sel = (srams_en && (srams_addr[15] == 1'b0)) ? 1'b0 : 1'b1;
	assign bank0_cs = (srams_en && (srams_addr[15] == 1'b0))  ? sram_cs : 4'b0000;
	assign bank1_cs = (srams_en && (srams_addr[15] == 1'b1))  ? sram_cs : 4'b0000;

	//signals used to generating sram chip select signal in one bank.
	assign sram_sel = srams_addr[1:0];
	assign hsize_sel = hsize_r [1:0];

	//seq part
	always@(posedge hclk , negedge hresetn) begin
		if(!hresetn) begin
			hwrite_r  <= 1'b0	;
			hsize_r   <= 3'b0	;
			hburst_r  <= 3'b0	;
			htrans_r  <= 2'b0  	;
			haddr_r   <= 32'b0 	;
		end
		else if(hsel && hready) begin
			hwrite_r  <= hwrite ;
			hsize_r   <= hsize  ;
			hburst_r  <= hburst ;
			htrans_r  <= htrans ;
			haddr_r   <= haddr 	;
		end
		else begin
			hwrite_r  <= 1'b0	;
			hsize_r   <= 3'b0	;
			hburst_r  <= 3'b0	;
			htrans_r  <= 2'b0  	;
			haddr_r   <= 32'b0 	;
		end
	end

	//comb part
	always@(hsize_sel or sram_sel) begin
		if(hsize_sel == 2'b10) //32bit
			sram_cs = 4'b1111;
		else if(hsize_sel == 2'b01) //16bit
			sram_cs = (sram_sel[1] == 1'b0) ? 4'b0011 : 4'b1100; //sram_sel[1] is low, get data from 1st and 2nd srams
		else if(hsize_sel == 2'b00) begin //8bit
			case(sram_sel) //translate sram_sel to sram_cs
				2'b00 : sram_cs = 4'b0001;
				2'b01 : sram_cs = 4'b0010;
				2'b10 : sram_cs = 4'b0100;
				2'b11 : sram_cs = 4'b1000;
				default : sram_cs = 4'b0000;
			endcase
		end
		else sram_cs=4'b0000;
	end

endmodule