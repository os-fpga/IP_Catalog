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
		$dumpfile("ahb_sram.vcd");
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
                write_t(32'h00004,32'h11111111);
                write_t(32'h00008,32'h22222222);
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

                read_t(32'h00004,data_rt);
				hready = 1'b0;
                read_t(32'h00008,data_rt);
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
		$stop;
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
