`timescale 1ns/1ps
`celldefine
//
// O_SERDES simulation model
// Output Serializer
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//




module SyncFIFO #(
	parameter DEPTH = 4,
    parameter DATA_WIDTH = 5
	)(
	input wire clk,    // core clock   
	input wire reset,     
	input wire wr_en,
	input wire rd_en,
	input wire [DATA_WIDTH:0] wr_data,
	output wire [DATA_WIDTH:0] rd_data,
	output wire empty,    
	output wire full,
	output wire almost_full      
	);

    reg [DATA_WIDTH:0] fifo [DEPTH-1:0];
    reg [DATA_WIDTH:0] rd_data_reg;
    reg [$clog2(DEPTH)-1:0] wr_ptr, rd_ptr;

    assign empty = (wr_ptr == rd_ptr);
    assign full = ((wr_ptr == rd_ptr - 1) || (wr_ptr == DEPTH - 1 && rd_ptr == 0));
	assign almost_full = !empty; //(wr_ptr >= (DEPTH - 4));
	
	always @(posedge clk or negedge reset)
	begin
		if(!reset)
		begin
			rd_data_reg <= 0;
			wr_ptr 		<= 0;
			rd_ptr 		<= 0;
			for (int i = 0; i< DEPTH; i++)
				fifo[i] <= '0;
		end
		else 
		begin
			if(wr_en && !full)
			begin
                fifo[wr_ptr] <= wr_data;
                wr_ptr <= wr_ptr + 1;
            end
            if(rd_en && !empty)
			begin
                rd_data_reg <= fifo[rd_ptr];
                rd_ptr <= rd_ptr + 1;
            end
		end
    end
	
    assign rd_data = rd_data_reg;

endmodule


module O_SERDES #(
  parameter DATA_RATE = "SDR", // Single or double data rate (SDR/DDR)
  parameter WIDTH = 4 // Width of input data to serializer (3-10)
) (
  input [WIDTH-1:0] D, // D input bus
  input RST, // Active-low, asynchronous reset
  input LOAD_WORD, // Load word input
  input CLK_IN, // Fabric clock input
  input OE_IN, // Output tri-state enable input
  output OE_OUT, // Output tri-state enable output (conttect to O_BUFT or inferred tri-state signal)
  output Q, // Data output (Connect to output port, buffer or O_DELAY)
  input CHANNEL_BOND_SYNC_IN, // Channel bond sync input
  output CHANNEL_BOND_SYNC_OUT, // Channel bond sync output
  input PLL_LOCK, // PLL lock input
  input PLL_CLK // PLL clock input
);

  

	// GBOX CLK GEN
	reg core_clk=0;
	reg word_load_en;
	reg [8:0] pll_lock_count;
	reg [3:0] core_clk_count;


	// count cycles after PLL LOCK
	always@(posedge PLL_CLK or negedge RST)
	begin
		if(!RST)
			pll_lock_count<=0;
		else if(!PLL_LOCK)
			pll_lock_count<=0;

		// else if(PLL_LOCK && pll_lock_count<=31+(WIDTH/2)) // delay before clock starting = 32 clocks + rate_sel/2 clocks
		else if(PLL_LOCK && pll_lock_count<=255)
			pll_lock_count<=pll_lock_count+1;
	end

	// Generate Core CLK And Word Load Enable
	always@(posedge PLL_CLK or negedge RST)
	begin
		if(!RST)
		begin
			core_clk<=0;
			core_clk_count<=0;
			word_load_en<=0;
		end

		else if(core_clk_count==WIDTH-1)
		begin
			core_clk_count<=0;
			word_load_en<=1;
		end
		// else if(pll_lock_count>=31+(WIDTH/2))  // if delay before clock starting = 32 clocks + rate_sel/2 clocks
		else if(pll_lock_count>=255)
		begin
			core_clk_count<=core_clk_count+1;
			core_clk<=(core_clk_count<WIDTH/2)?1'b1:1'b0;
			word_load_en<=0;
		end

	end

	// Logic To Be Checked Again for CHANNEL BOND SYNC IN/OUT
	reg fast_clk_sync_out;
	always@(posedge PLL_CLK or negedge RST)
	begin
		if(!RST)
		fast_clk_sync_out<=0;

		else if(CHANNEL_BOND_SYNC_IN && core_clk)
		begin
			fast_clk_sync_out<=1;
		end
		else begin
			fast_clk_sync_out<=0;
		end

	end
	assign CHANNEL_BOND_SYNC_OUT = fast_clk_sync_out;
	// GBOX CLK GEN //

	// Synchronous FIFO
	reg read_en;
	wire afull;
	wire fifo_empty;
	reg fifo_read_en;
	reg word_load_en_sync;
	reg [WIDTH-1:0] data_parallel_reg;
	reg [WIDTH-1:0] data_shift_reg;
	reg oe_parallel_reg;
	reg oe_shift_reg;
	wire fifo_data_oe;
	wire [WIDTH-1:0] fifo_read_data;

	SyncFIFO # (
		.DEPTH(4),
		.DATA_WIDTH(WIDTH)
	  )fifo1 (
		.clk(CLK_IN),
		.reset(RST),
		.wr_en(1'b1),
		.rd_en(fifo_read_en),
		.wr_data({OE_IN,D}),
		.rd_data({fifo_data_oe,fifo_read_data}),
		.empty(fifo_empty),
		.full(),
		.almost_full(afull)
		);

	// Generating read enable signal for fifo				
	always @(posedge CLK_IN or negedge RST) 
	begin
		if(!RST)
			read_en <= 0;  
		else
			read_en <= afull;
	end

	// Word load enable signal to load fifo data
	always @(posedge PLL_CLK or negedge RST) 
	begin
		if(!RST)
			fifo_read_en <= 1'b0;
		else if(fifo_empty)
			fifo_read_en <= 1'b0;
		else if (afull)
			fifo_read_en <= 1'b1;
	end

	assign word_load_en_sync = LOAD_WORD && fifo_read_en ;


	// Parallel data register 
	always @(posedge PLL_CLK or negedge RST) 
	begin
		if(!RST)
		begin
			data_parallel_reg <= 'h0;
			oe_parallel_reg   <= 1'b0;
		end
		else if(word_load_en_sync)
		begin
			data_parallel_reg <= fifo_read_data;
			oe_parallel_reg   <= fifo_data_oe;
		end

	end

	// Shift Register
	always @(posedge PLL_CLK or negedge RST)
	begin
		if(!RST)
		begin
			data_shift_reg <= 0;
			oe_shift_reg   <= 0;
		end
		else if(word_load_en_sync)
		begin
			oe_shift_reg   <= oe_parallel_reg;
			data_shift_reg <= data_parallel_reg;
		end
		else
			data_shift_reg <= {data_shift_reg[WIDTH-2: 0],1'b0};
	end

	always @(negedge PLL_CLK)
	begin
		if(DATA_RATE=="DDR")
			data_shift_reg <= {data_shift_reg[WIDTH-2: 0],1'b0};
	end

	assign OE_OUT = oe_shift_reg;

	assign Q = data_shift_reg[WIDTH - 1];

	 initial begin
    case(DATA_RATE)
      "SDR" ,
      "DDR": begin end
      default: begin
        $display("\nError: O_SERDES instance %m has parameter DATA_RATE set to %s.  Valid values are SDR, DDR\n", DATA_RATE);
        #1 $stop ;
      end
    endcase

    if ((WIDTH < 3) || (WIDTH > 10)) begin
       $display("O_SERDES instance %m WIDTH set to incorrect value, %d.  Values must be between 3 and 10.", WIDTH);
    #1 $stop;
    end

  end

endmodule
`endcelldefine