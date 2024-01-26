`timescale 1ns/1ps
`celldefine
//
// FIFO36K simulation model
// 36Kb FIFO
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module FIFO36K #(
  parameter DATA_WRITE_WIDTH = 36, // FIFO data write width (1-36)
  parameter DATA_READ_WIDTH = 36, // FIFO data read width (1-36)
  parameter FIFO_TYPE = "SYNCHRONOUS", // Synchronous or Asynchronous data transfer (SYNCHRONOUS/ASYNCHRONOUS)
  parameter [11:0] PROG_EMPTY_THRESH = 12'h004, // 12-bit Programmable empty depth
  parameter [11:0] PROG_FULL_THRESH = 12'hffa // 12-bit Programmable full depth
) (
  input RESET, // Active high synchronous FIFO reset
  input WR_CLK, // Write clock
  input RD_CLK, // Read clock
  input WR_EN, // Write enable
  input RD_EN, // Read enable
  input [DATA_WRITE_WIDTH-1:0] WR_DATA, // Write data
  output [DATA_READ_WIDTH-1:0] RD_DATA, // Read data
  output reg EMPTY = 1'b1, // FIFO empty flag
  output reg FULL = 1'b0, // FIFO full flag
  output reg ALMOST_EMPTY = 1'b0, // FIFO almost empty flag
  output reg ALMOST_FULL = 1'b0, // FIFO almost full flag
  output reg PROG_EMPTY = 1'b1, // FIFO programmable empty flag
  output reg PROG_FULL = 1'b0, // FIFO programmable full flag
  output reg OVERFLOW = 1'b0, // FIFO overflow error flag
  output reg UNDERFLOW = 1'b0 // FIFO underflow error flag
);
	
	localparam DATA_WIDTH = DATA_WRITE_WIDTH;
	localparam  fifo_depth = (DATA_WIDTH <= 9) ? 4096 :
                           (DATA_WIDTH <= 18) ? 2048 :
                           1024;
  
  localparam  fifo_addr_width = (DATA_WIDTH <= 9) ? 12 :
                                (DATA_WIDTH <= 18) ? 11 :
                                10;

  reg [fifo_addr_width-1:0] fifo_wr_addr = {fifo_addr_width{1'b0}};
  reg [fifo_addr_width-1:0] fifo_rd_addr = {fifo_addr_width{1'b0}};

  wire [31:0] ram_wr_data;
  wire [3:0] ram_wr_parity;

  reg fwft = 1'b0;
  reg fall_through;
  reg wr_data_fwft;
  reg [DATA_WIDTH-1:0] fwft_data = {DATA_WIDTH{1'b0}};

  wire [31:0] ram_rd_data; 
  wire [3:0]  ram_rd_parity;
  wire ram_clk_b;
  
  integer number_entries = 0;
  reg underrun_status = 0;
  reg overrun_status = 0;

  generate

    if ((DATA_WIDTH == 9)|| (DATA_WIDTH == 17) || (DATA_WIDTH == 25)) begin: one_parity
      assign ram_wr_data = {{32-DATA_WIDTH{1'b0}}, WR_DATA};
      assign ram_wr_parity = {3'b000, WR_DATA[DATA_WIDTH-1]};
      assign RD_DATA = fwft ? fwft_data : {ram_rd_parity[0], ram_rd_data[DATA_WIDTH-2:0]};
    end else if (DATA_WIDTH == 33) begin: width_33
      assign ram_wr_data = WR_DATA[31:0];
      assign ram_wr_parity = {3'b000, WR_DATA[32]};
      assign RD_DATA = fwft ? fwft_data : {ram_rd_parity[0], ram_rd_data[31:0]};
    end else if ((DATA_WIDTH == 18) || (DATA_WIDTH == 26)) begin: two_parity
      assign ram_wr_data = {{32-DATA_WIDTH{1'b0}}, WR_DATA};
      assign ram_wr_parity = {2'b00, WR_DATA[DATA_WIDTH-1:DATA_WIDTH-2]};
      assign RD_DATA = fwft ? fwft_data : {ram_rd_parity[1:0], ram_rd_data[DATA_WIDTH-3:0]};
    end else if (DATA_WIDTH == 34) begin: width_34
      assign ram_wr_data = WR_DATA[31:0];
      assign ram_wr_parity = {2'b00, WR_DATA[33:32]};
      assign RD_DATA = fwft ? fwft_data : {ram_rd_parity[1:0], ram_rd_data[31:0]};
    end else if (DATA_WIDTH == 27) begin: width_27
      assign ram_wr_data = {8'h00, WR_DATA[23:0]};
      assign ram_wr_parity = {1'b0, WR_DATA[26:24]};
      assign RD_DATA = fwft ? fwft_data : {ram_rd_parity[2:0], ram_rd_data[23:0]};
    end else if (DATA_WIDTH == 35) begin: width_35
      assign ram_wr_data = WR_DATA[31:0];
      assign ram_wr_parity = {1'b0, WR_DATA[34:32]};
      assign RD_DATA = fwft ? fwft_data : {ram_rd_parity[2:0], ram_rd_data[31:0]};
    end else if (DATA_WIDTH == 36) begin: width_36
      assign ram_wr_data = WR_DATA[31:0];
      assign ram_wr_parity = WR_DATA[35:32];
      assign RD_DATA = fwft ? fwft_data : {ram_rd_parity[3:0], ram_rd_data[31:0]};
    end else begin: no_parity
      assign ram_wr_data = fall_through ? wr_data_fwft : {{32-DATA_WIDTH{1'b0}}, WR_DATA};
      assign ram_wr_parity = 4'h0;
      assign RD_DATA = fwft ? fwft_data : ram_rd_data[DATA_WIDTH-1:0];
    end

    if ( FIFO_TYPE == "SYNCHRONOUS" )  begin: sync

      always @(posedge WR_CLK)
        if (WR_EN && !RD_EN) begin
          number_entries <= number_entries + 1;
          underrun_status = 0;
          if (number_entries >= fifo_depth)
            overrun_status  = 1;
        end
        else if (!WR_EN && RD_EN && number_entries == 0) begin
          number_entries <= 0;
          underrun_status = 1;
        end
        else if (!WR_EN && RD_EN) begin
          number_entries <= number_entries - 1;
          underrun_status = 0;
        end

      always @(posedge RESET, posedge WR_CLK)
        if (RESET) begin
          fifo_wr_addr <= {fifo_addr_width{1'b0}};
          fifo_rd_addr <= {fifo_addr_width{1'b0}};
          EMPTY        <= 1'b1;
          FULL         <= 1'b0;
          ALMOST_EMPTY <= 1'b0;
          ALMOST_FULL  <= 1'b0;
          PROG_EMPTY   <= 1'b1;
          PROG_FULL    <= 1'b0;
          OVERFLOW     <= 1'b0;
          UNDERFLOW    <= 1'b0;
          number_entries = 0;
          fwft         <= 1'b0;
          fwft_data    <= {DATA_WIDTH-1{1'b0}};
          underrun_status <=1'b0;
          overrun_status  <= 1'b0;
        end else begin
          if (WR_EN)
            fifo_wr_addr <= fifo_wr_addr + 1'b1;
          EMPTY        <= ((number_entries==0) && (underrun_status==0) || ((RD_EN && !WR_EN) && (number_entries==1)));
          FULL         <= ((number_entries==fifo_depth) || ((number_entries==(fifo_depth-1)) && WR_EN && !RD_EN));
          ALMOST_EMPTY <= (((number_entries==1) && !(RD_EN && !WR_EN)) ||  ((RD_EN && !WR_EN) && (number_entries==2)));
          ALMOST_FULL  <= (((number_entries==(fifo_depth-1)) && !(!RD_EN && WR_EN)) ||  ((!RD_EN && WR_EN) && (number_entries==fifo_depth-2)));
          PROG_EMPTY   <= ((number_entries) < (PROG_EMPTY_THRESH)) || ((RD_EN && !WR_EN) && ((number_entries) <= PROG_EMPTY_THRESH) );
          PROG_FULL    <= ((fifo_depth-number_entries) < (PROG_FULL_THRESH)) || ((!RD_EN && WR_EN) && ((fifo_depth-number_entries) <= PROG_FULL_THRESH) );
          UNDERFLOW    <= (EMPTY && RD_EN) || (underrun_status==1);
          OVERFLOW     <= (FULL && WR_EN) || (overrun_status==1);
          if (EMPTY && WR_EN && !fwft) begin
            fwft_data <= WR_DATA;
            fifo_rd_addr <= fifo_rd_addr + 1'b1;
            fwft <= 1'b1;
          end else if (RD_EN) begin
            fwft <= 1'b0;
            if (!(ALMOST_EMPTY && !WR_EN))
              fifo_rd_addr <= fifo_rd_addr + 1'b1;
          end
        end

        assign ram_clk_b = WR_CLK;

        initial begin
          #1;
          @(RD_CLK);
          $display("\nWarning: FIFO36K instance %m RD_CLK should be tied to ground when FIFO36K is configured as FIFO_TYPE=SYNCHRONOUS.");
        end

    end else begin: async

      assign ram_clk_b = RD_CLK;

    end

  endgenerate

  // Use BRAM

  TDP_RAM36K #(
    .INIT({32768{1'b0}}), // Initial Contents of memory
    .INIT_PARITY({2048{1'b0}}), // Initial Contents of memory
    .WRITE_WIDTH_A(DATA_WIDTH), // Write data width on port A (1-36)
    .READ_WIDTH_A(DATA_WIDTH), // Read data width on port A (1-36)
    .WRITE_WIDTH_B(DATA_WIDTH), // Write data width on port B (1-36)
    .READ_WIDTH_B(DATA_WIDTH) // Read data width on port B (1-36)
  ) FIFO_RAM_inst (
    .WEN_A(WR_EN), // Write-enable port A
    .WEN_B(1'b0), // Write-enable port B
    .REN_A(1'b0), // Read-enable port A
    .REN_B(RD_EN), // Read-enable port B
    .CLK_A(WR_CLK), // Clock port A
    .CLK_B(ram_clk_b), // Clock port B
    .BE_A(4'hf), // Byte-write enable port A
    .BE_B(4'h0), // Byte-write enable port B
    .ADDR_A({fifo_wr_addr, {15-fifo_addr_width{1'b0}}}), // Address port A, align MSBs and connect unused MSBs to logic 0
    .ADDR_B({fifo_rd_addr, {15-fifo_addr_width{1'b0}}}), // Address port B, align MSBs and connect unused MSBs to logic 0
    .WDATA_A(ram_wr_data), // Write data port A
    .WPARITY_A(ram_wr_parity), // Write parity data port A
    .WDATA_B(32'h00000000), // Write data port B
    .WPARITY_B(4'h0), // Write parity port B
    .RDATA_A(), // Read data port A
    .RPARITY_A(), // Read parity port A
    .RDATA_B(ram_rd_data), // Read data port B
    .RPARITY_B(ram_rd_parity) // Read parity port B
  ); initial begin

    if ((DATA_WRITE_WIDTH < 1) || (DATA_WRITE_WIDTH > 36)) begin
       $display("FIFO36K instance %m DATA_WRITE_WIDTH set to incorrect value, %d.  Values must be between 1 and 36.", DATA_WRITE_WIDTH);
    #1 $stop;
    end

    if ((DATA_READ_WIDTH < 1) || (DATA_READ_WIDTH > 36)) begin
       $display("FIFO36K instance %m DATA_READ_WIDTH set to incorrect value, %d.  Values must be between 1 and 36.", DATA_READ_WIDTH);
    #1 $stop;
    end
    case(FIFO_TYPE)
      "SYNCHRONOUS" ,
      "ASYNCHRONOUS": begin end
      default: begin
        $display("\nError: FIFO36K instance %m has parameter FIFO_TYPE set to %s.  Valid values are SYNCHRONOUS, ASYNCHRONOUS\n", FIFO_TYPE);
        #1 $stop ;
      end
    endcase

  end

endmodule
`endcelldefine