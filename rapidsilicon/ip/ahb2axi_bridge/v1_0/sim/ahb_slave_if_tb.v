module ahb_slave_if_tb;
	
	reg                   	hclk, sram_clk;
   reg                   	hresetn;
	reg							hsel;
	reg [31:0]					haddr;
	reg							hwrite;
	reg [2:0]					hsize;
	reg [2:0]					hburst;
	reg [1:0]					htrans;
	reg							hready;
	reg [31:0]					hwdata;
	
	wire						hready_resp;
	wire[1:0]					hresp;
	wire[31:0]					hrdata;
	
	reg [7:0]					sram_q0;
	reg [7:0]					sram_q1;
	reg [7:0]					sram_q2;
	reg [7:0]					sram_q3;
	reg [7:0]					sram_q4;
	reg [7:0]					sram_q5;
	reg [7:0]					sram_q6;
	reg [7:0]					sram_q7;

	wire						sram_w_en;
	wire[31:0]					sram_wdata;
	wire[12:0]					sram_addr_out;
	wire[3:0]					bank0_csn;
	wire[3:0]					bank1_csn;
	
	reg [31:0]					data_rt;


wire	[7:0]		s_axi_awid;
wire	[31:0]		s_axi_awaddr;
wire	[7:0]		s_axi_awlen;
wire	[2:0]		s_axi_awsize;
wire	[1:0]		s_axi_awburst;
wire			s_axi_awlock;
wire			s_axi_awcache;
wire			s_axi_awprot;
wire			s_axi_awvalid;
wire			s_axi_awready;
wire	[31:0]		s_axi_wdata;
wire	[3:0]		s_axi_wstrb;
wire			s_axi_wlast;
wire			s_axi_wvalid;
wire			s_axi_wready;
wire	[7:0]		s_axi_bid;
wire			s_axi_bresp;
wire			s_axi_bvalid;
wire			s_axi_bready;
wire	[7:0]		s_axi_arid;
wire	[31:0]		s_axi_araddr;
wire	[7:0]		s_axi_arlen;
wire	[3:0]		s_axi_arsize;
wire	[1:0]		s_axi_arburst;
wire			s_axi_arlock;
wire			s_axi_arcache;
wire			s_axi_arprot;
wire			s_axi_arvalid;
wire			s_axi_arready;
wire	[7:0]		s_axi_rid;
wire	[31:0]		s_axi_rdata;
wire			s_axi_rresp;
wire			s_axi_rlast;
wire			s_axi_rvalid;
wire			s_axi_rready;

ahb_to_axi4 bridge (

   .clk(sram_clk),
   .rst_l(~hresetn),
//   .scan_mode(scan_mode), 
//   .bus_clk_en(1),                              
//   .clk_override(clk_override),
   .axi_awvalid(s_axi_awvalid),
   .axi_awready(s_axi_awready),
   .axi_awid(s_axi_awid),
   .axi_awaddr(s_axi_awaddr),
   .axi_awsize(s_axi_awsize),
   .axi_wvalid(s_axi_wvalid),                                       
   .axi_wready(s_axi_wready),
   .axi_wdata(s_axi_wdata),
   .axi_wstrb(s_axi_wstrb),
   .axi_wlast(s_axi_wlast),
   .axi_bvalid(s_axi_bvalid),
   .axi_bready(s_axi_bready),
   .axi_bresp(s_axi_bresp),
   .axi_bid(s_axi_bid),
   .axi_arvalid(s_axi_arvalid),
   .axi_arready(s_axi_arready),
   .axi_arid(s_axi_arid),
   .axi_araddr(s_axi_araddr),                                     
   .axi_arsize(s_axi_arsize),
   .axi_rvalid(s_axi_rvalid),
   .axi_rready(s_axi_rready),
   .axi_rid(s_axi_rid),
   .axi_rdata(s_axi_rdata),
   .axi_rresp(s_axi_rresp),
   .axi_rlast(s_axi_rlast),					  
   .ahb_haddr(haddr),       // ahb bus address
   .ahb_hburst(hburst),      // tied to 0
   .ahb_hmastlock(hmastlock),   // tied to 0
   .ahb_hsize(hsize),       // size of bus transaction (possible values 0,1,2,3)
   .ahb_htrans(htrans),      // Transaction type (possible values 0,2 only right now)
   .ahb_hwrite(hwrite),      // ahb bus write
   .ahb_hwdata(hwdata),      // ahb bus write data
   .ahb_hrdata(hrdata),      // ahb bus read data 
   .ahb_hsel(1),
   .ahb_hreadyin(hready),      // slave ready to accept transaction
   .ahb_hresp(hresp));       // slave response (high indicates erro)


axi_ram periph(
    .clk(hclk),
    .rst(~hresetn),
    .s_axi_awid(s_axi_awid),
    .s_axi_awaddr(s_axi_awaddr),
    .s_axi_awlen(s_axi_awlen),
    .s_axi_awsize(s_axi_awsize),
    .s_axi_awburst(s_axi_awburst),
    .s_axi_awlock(s_axi_awlock),
    .s_axi_awcache(s_axi_awcache),
    .s_axi_awprot(s_axi_awprot),
    .s_axi_awvalid(s_axi_awvalid),
    .s_axi_awready(s_axi_awready),
    .s_axi_wdata(s_axi_wdata),
    .s_axi_wstrb(s_axi_wstrb),
    .s_axi_wlast(s_axi_wlast),
    .s_axi_wvalid(s_axi_wvalid),
    .s_axi_wready(s_axi_wready),
    .s_axi_bid(s_axi_bid),
    .s_axi_bresp(s_axi_bresp),
    .s_axi_bvalid(s_axi_bvalid),
    .s_axi_bready(s_axi_bready),
    .s_axi_arid(s_axi_arid),
    .s_axi_araddr(s_axi_araddr),
    .s_axi_arlen(s_axi_arlen),
    .s_axi_arsize(s_axi_arsize),
    .s_axi_arburst(s_axi_arburst),
    .s_axi_arlock(s_axi_arlock),
    .s_axi_arcache(s_axi_arcache),
    .s_axi_arprot(s_axi_arprot),
    .s_axi_arvalid(s_axi_arvalid),
    .s_axi_arready(s_axi_arready),
    .s_axi_rid(s_axi_rid),
    .s_axi_rdata(s_axi_rdata),
    .s_axi_rresp(s_axi_rresp),
    .s_axi_rlast(s_axi_rlast),
    .s_axi_rvalid(s_axi_rvalid),
    .s_axi_rready(s_axi_rready)
);

/*

	sramc_top dut(
	.sram_clk(sram_clk),
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
	.hrdata(hrdata)
	);
	

	sram_top dut(
	.hclk(hclk),
	.sram_clk(hclk),
	.hresetn(hresetn),
	.hsel(hsel),
	.haddr(haddr),
	.hwrite(hwrite),
	.hsize(hsize),
	.hburst(hburst),
	.htrans(htrans),
	.hready(hready),
	.hwdata(hwdata),
	.dft_en(0),
	.bist_en(0),
	.hrdata(hrdata),
	.hready_resp(hready_resp),
	.hresp(hresp),	
	.bist_done(bist_done),
	.bist_fail(bist_fail));

*/


/*

	
	 ahb_slave_if ahb_slave_if(
			//input signals
		  .hclk						( hclk ),
		  .hresetn					( hresetn ),
        .hsel						( hsel ),
        .haddr						( haddr ),
        .hwrite					( hwrite ),
        .hsize						( hsize ),
        .hburst					( hburst ),
        .htrans					( htrans ),
        .hready					( hready ),
        .hwdata					( hwdata ),

		   //output signals
		  .hready_resp				( hready_resp ),
		  .hresp						( hresp ),
		  .hrdata					( hrdata ),

			//sram input signals 
		  .sram_q0					( sram_q0 ),
		  .sram_q1					( sram_q1 ),
		  .sram_q2					( sram_q2 ),
		  .sram_q3					( sram_q3 ),
		  .sram_q4					( sram_q4 ),
		  .sram_q5					( sram_q5 ),
		  .sram_q6					( sram_q6 ),
		  .sram_q7					( sram_q7 ),
			
			//sram output signals 
		  .sram_w_en				( sram_w_en ),
		  .sram_addr_out			( sram_addr_out ),
		  .sram_wdata				( sram_wdata ),
		  .bank0_csn				( bank0_csn ),
		  .bank1_csn				( bank1_csn )
);
*/
	parameter 		 IDLE		= 2'b00;
   parameter       BUSY		= 2'b01;
   parameter       NONSEQ	= 2'b10;
   parameter       SEQ		= 2'b11;
			 
	initial begin
		hclk = 0;
		forever
		begin
			#10 hclk = ~hclk;
		end
	end
	
	initial begin
		sram_clk = 0;
		forever
		begin
			#10 sram_clk = ~sram_clk;
		end
	end

	initial begin
		$dumpfile("ahb2axi.vcd");
		$dumpvars;
//		#1000;
//		$finish;

	end



	initial begin
		hclk = 0;
		hresetn = 0;
		hsel = 0;
		haddr = 0;
		hwrite = 0;
		hsize = 0;
		htrans = 0;
		hready = 0;
		hwdata = 0;
		#100;
                hresetn = 1;
                write_t(32'h00044,32'h11111111);
                write_t(32'h00048,32'h22222222);
                write_t(32'h0000C,32'h33333333);
                write_t(32'h00010,32'h44444444);
                write_t(32'h00014,32'h55555555);
				write_t(32'h00018,32'h66666666);
                write_t(32'h0001C,32'h77777777);
                write_t(32'h00020,32'h88888888);
                write_t(32'h00024,32'h99999999);
                write_t(32'h00028,32'h000000AA);
                hsel = 1;
                haddr = 32'h0000A;
                hwrite = 1;
                hsize = 2'b10;
                htrans = NONSEQ;
                hready = 1'b0;
                #20;
                hwdata = 32'h45678;
                write_t(32'h00006,32'h567890);
				write_t(32'h00007,32'h678901);
                #100;

				hready = 1'b1;

                read_t(32'h00044,data_rt);
				hready = 1'b0;
                read_t(32'h00048,data_rt);
				hready = 1'b0;
                read_t(32'h0000C,data_rt);
				hready = 1'b0;
                read_t(32'h00010,data_rt);
				hready = 1'b0;
                read_t(32'h00014,data_rt);
				hready = 1'b0;
                read_t(32'h00018,data_rt);
				hready = 1'b0;
                read_t(32'h0001C,data_rt);
				hready = 1'b0;
                read_t(32'h00020,data_rt);
				hready = 1'b0;
                read_t(32'h00024,data_rt);
				hready = 1'b0;
                read_t(32'h00028,data_rt);
				hsel = 1;
                haddr = 32'h0000A;
                hwrite = 0;
                hsize = 2'b10;
                htrans = NONSEQ;
                hready = 1'b0;
					 #20;
//					 read_t(32'h00006,data_rt);
//                read_t(32'h00007,data_rt);

	   #100;
	   	$finish;
	end
	
	task write_t(input [31:0] addr_wt , input [31:0]	data_wt );
	begin
		@(posedge hclk)
			hsel = 1;
			haddr = addr_wt;
			hwrite = 1;
			hsize = 2'b10;
			htrans = NONSEQ;
			hready = 1'b1;
		@(posedge hclk)
			hwdata = data_wt;
	end
	endtask
	
	task read_t(input [31:0] addr_rt ,output [31:0]	data_rt );
	begin
		@(posedge hclk)
			hsel = 1;
			haddr = addr_rt;
			hwrite = 0;
			hsize = 2'b10;
			htrans = NONSEQ;
			hready = 1'b1;
		@(posedge hclk)
			sram_q0 = 0;
			sram_q1 = 1;
			sram_q2 = 2;
			sram_q3 = 3;
			sram_q4 = 4;
			sram_q5 = 5;
			sram_q6 = 6;
			sram_q7 = 7;
			data_rt = hrdata;
	end
	endtask
	
	
	
endmodule
