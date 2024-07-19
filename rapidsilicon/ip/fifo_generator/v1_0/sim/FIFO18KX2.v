`timescale 1ns/1ps
`celldefine
//
// FIFO18KX2 simulation model
// Dual 18Kb FIFO
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module FIFO18KX2 #(
  parameter DATA_WRITE_WIDTH1 = 18, // FIFO data write width, FIFO 1 (9, 18)
  parameter DATA_READ_WIDTH1 = 18, // FIFO data read width, FIFO 1 (9, 18)
  parameter FIFO_TYPE1 = "SYNCHRONOUS", // Synchronous or Asynchronous data transfer, FIFO 1 (SYNCHRONOUS/ASYNCHRONOUS)
  parameter [10:0] PROG_EMPTY_THRESH1 = 11'h004, // 11-bit Programmable empty depth, FIFO 1
  parameter [10:0] PROG_FULL_THRESH1 = 11'h7fa, // 11-bit Programmable full depth, FIFO 1
  parameter DATA_WRITE_WIDTH2 = 18, // FIFO data write width, FIFO 2 (9, 18)
  parameter DATA_READ_WIDTH2 = 18, // FIFO data read width, FIFO 2 (9, 18)
  parameter FIFO_TYPE2 = "SYNCHRONOUS", // Synchronous or Asynchronous data transfer, FIFO 2 (SYNCHRONOUS/ASYNCHRONOUS)
  parameter [10:0] PROG_EMPTY_THRESH2 = 11'h004, // 11-bit Programmable empty depth, FIFO 2
  parameter [10:0] PROG_FULL_THRESH2 = 11'h7fa // 11-bit Programmable full depth, FIFO 2
) (
  input RESET1, // Active high asynchronous FIFO reset, FIFO 1
  input WR_CLK1, // Write clock, FIFO 1
  input RD_CLK1, // Read clock, FIFO 1
  input WR_EN1, // Write enable, FIFO 1
  input RD_EN1, // Read enable, FIFO 1
  input [DATA_WRITE_WIDTH1-1:0] WR_DATA1, // Write data, FIFO 1
  output [DATA_READ_WIDTH1-1:0] RD_DATA1, // Read data, FIFO 1
  output reg EMPTY1 = 1'b1, // FIFO empty flag, FIFO 1
  output reg FULL1 = 1'b0, // FIFO full flag, FIFO 1
  output reg ALMOST_EMPTY1 = 1'b0, // FIFO almost empty flag, FIFO 1
  output reg ALMOST_FULL1 = 1'b0, // FIFO almost full flag, FIFO 1
  output reg PROG_EMPTY1 = 1'b1, // FIFO programmable empty flag, FIFO 1
  output reg PROG_FULL1 = 1'b0, // FIFO programmable full flag, FIFO 1
  output reg OVERFLOW1 = 1'b0, // FIFO overflow error flag, FIFO 1
  output reg UNDERFLOW1 = 1'b0, // FIFO underflow error flag, FIFO 1
  input RESET2, // Active high synchronous FIFO reset, FIFO 2
  input WR_CLK2, // Write clock, FIFO 2
  input RD_CLK2, // Read clock, FIFO 2
  input WR_EN2, // Write enable, FIFO 2
  input RD_EN2, // Read enable, FIFO 2
  input [DATA_WRITE_WIDTH2-1:0] WR_DATA2, // Write data, FIFO 2
  output [DATA_READ_WIDTH2-1:0] RD_DATA2, // Read data, FIFO 2
  output reg EMPTY2 = 1'b1, // FIFO empty flag, FIFO 2
  output reg FULL2 = 1'b0, // FIFO full flag, FIFO 2
  output reg ALMOST_EMPTY2 = 1'b0, // FIFO almost empty flag, FIFO 2
  output reg ALMOST_FULL2 = 1'b0, // FIFO almost full flag, FIFO 2
  output reg PROG_EMPTY2 = 1'b1, // FIFO programmable empty flag, FIFO 2
  output reg PROG_FULL2 = 1'b0, // FIFO programmable full flag, FIFO 2
  output reg OVERFLOW2 = 1'b0, // FIFO overflow error flag, FIFO 2
  output reg UNDERFLOW2 = 1'b0 // FIFO underflow error flag, FIFO 2
);

  //FIFO1
  localparam DATA_WIDTH1 = DATA_WRITE_WIDTH1;
  localparam  fifo_depth1 = (DATA_WIDTH1 <= 9) ? 2048 : 1024;  
  localparam  fifo_addr_width1 = (DATA_WIDTH1 <= 9) ? 11 :  10;

  reg [fifo_addr_width1-1:0] fifo_wr_addr1 = {fifo_addr_width1{1'b0}};
  reg [fifo_addr_width1-1:0] fifo_rd_addr1 = {fifo_addr_width1{1'b0}};

  wire [15:0] ram_wr_data1;
  wire [1:0] ram_wr_parity1;

  reg fwft1 = 1'b0;
  reg fall_through1;
  reg wr_data_fwft1;
  reg [DATA_WIDTH1-1:0] fwft_data1 = {DATA_WIDTH1{1'b0}};

  wire [15:0] ram_rd_data1; 
  wire [1:0]  ram_rd_parity1;
  wire ram_clk_b1;
  
  integer number_entries1 = 0;
  reg underrun_status1 = 0;
  reg overrun_status1 = 0;

  generate

    if ((DATA_WIDTH1 == 9)|| (DATA_WIDTH1 == 17)) begin: one_parity
      assign ram_wr_data1 = {{16-DATA_WIDTH1{1'b0}}, WR_DATA1};
      assign ram_wr_parity1 = {1'b0, WR_DATA1[DATA_WIDTH1-1]};
      assign RD_DATA1 = fwft1 ? fwft_data1 : {ram_rd_parity1[0], ram_rd_data1[DATA_WIDTH1-2:0]};
    end else if ((DATA_WIDTH1 == 18)) begin: two_parity
      assign ram_wr_data1 = WR_DATA1[15:0];
      assign ram_wr_parity1 = WR_DATA1[DATA_WIDTH1-1:DATA_WIDTH1-2];
      assign RD_DATA1 = fwft1 ? fwft_data1 : {ram_rd_parity1[1:0], ram_rd_data1[DATA_WIDTH1-3:0]};
    end else begin: no_parity
      assign ram_wr_data1 = fall_through1 ? wr_data_fwft1 : {{16-DATA_WIDTH1{1'b0}}, WR_DATA1};
      assign ram_wr_parity1 = 2'b0;
      assign RD_DATA1 = fwft1 ? fwft_data1 : ram_rd_data1[DATA_WIDTH1-1:0];
    end

    if ( FIFO_TYPE1 == "SYNCHRONOUS" )  begin: sync

      always @(posedge WR_CLK1)
        if (WR_EN1 && !RD_EN1) begin
          number_entries1 <= number_entries1 + 1;
          underrun_status1 = 0;
          if (number_entries1 >= fifo_depth1)
            overrun_status1  = 1;
        end
        else if (!WR_EN1 && RD_EN1 && number_entries1 == 0) begin
          number_entries1 <= 0;
          underrun_status1 = 1;
        end
        else if (!WR_EN1 && RD_EN1) begin
          number_entries1 <= number_entries1 - 1;
          underrun_status1 = 0;
        end

      always @(posedge RESET1, posedge WR_CLK1)
        if (RESET1) begin
          fifo_wr_addr1 <= {fifo_addr_width1{1'b0}};
          fifo_rd_addr1 <= {fifo_addr_width1{1'b0}};
          EMPTY1        <= 1'b1;
          FULL1         <= 1'b0;
          ALMOST_EMPTY1 <= 1'b0;
          ALMOST_FULL1  <= 1'b0;
          PROG_EMPTY1   <= 1'b1;
          PROG_FULL1    <= 1'b0;
          OVERFLOW1     <= 1'b0;
          UNDERFLOW1    <= 1'b0;
          number_entries1 = 0;
          fwft1         <= 1'b0;
          fwft_data1    <= {DATA_WIDTH1-1{1'b0}};
          underrun_status1 <=1'b0;
          overrun_status1  <= 1'b0;
        end else begin
          if (WR_EN1)
            fifo_wr_addr1 <= fifo_wr_addr1 + 1'b1;
          EMPTY1        <= ((number_entries1==0) && (underrun_status1==0) || ((RD_EN1 && !WR_EN1) && (number_entries1==1)));
          FULL1         <= ((number_entries1==fifo_depth1) || ((number_entries1==(fifo_depth1-1)) && WR_EN1 && !RD_EN1));
          ALMOST_EMPTY1 <= (((number_entries1==1) && !(RD_EN1 && !WR_EN1)) ||  ((RD_EN1 && !WR_EN1) && (number_entries1==2)));
          ALMOST_FULL1  <= (((number_entries1==(fifo_depth1-1)) && !(!RD_EN1 && WR_EN1)) ||  ((!RD_EN1 && WR_EN1) && (number_entries1==fifo_depth1-2)));
          PROG_EMPTY1   <= ((number_entries1) < (PROG_EMPTY_THRESH1)) || ((RD_EN1 && !WR_EN1) && ((number_entries1) <= PROG_EMPTY_THRESH1) );
          PROG_FULL1    <= ((fifo_depth1-number_entries1) < (PROG_FULL_THRESH1)) || ((!RD_EN1 && WR_EN1) && ((fifo_depth1-number_entries1) <= PROG_FULL_THRESH1) );
          UNDERFLOW1    <= (EMPTY1 && RD_EN1) || (underrun_status1==1);
          OVERFLOW1     <= (FULL1 && WR_EN1) || (overrun_status1==1);
          if (EMPTY1 && WR_EN1 && !fwft1) begin
            fwft_data1 <= WR_DATA1;
            fifo_rd_addr1 <= fifo_rd_addr1 + 1'b1;
            fwft1 <= 1'b1;
          end else if (RD_EN1) begin
            fwft1 <= 1'b0;
            if (!(ALMOST_EMPTY1 && !WR_EN1))
              fifo_rd_addr1 <= fifo_rd_addr1 + 1'b1;
          end
        end

        assign ram_clk_b1 = WR_CLK1;

        initial begin
          #1;
          @(RD_CLK1);
          $display("\nWarning: FIFO36K instance %m RD_CLK1 should be tied to ground when FIFO36K is configured as FIFO1_TYPE=SYNCHRONOUS.");
        end

    end else begin: async

      assign ram_clk_b1 = RD_CLK1;

    end

  endgenerate

  //FIFO2
  localparam DATA_WIDTH2 = DATA_WRITE_WIDTH2;
  localparam  fifo_depth2 = (DATA_WIDTH2 <= 9) ? 2048 : 1024;  
  localparam  fifo_addr_width2 = (DATA_WIDTH2 <= 9) ? 11 :  10;

  reg [fifo_addr_width2-1:0] fifo_wr_addr2 = {fifo_addr_width2{1'b0}};
  reg [fifo_addr_width2-1:0] fifo_rd_addr2 = {fifo_addr_width2{1'b0}};

  wire [15:0] ram_wr_data2;
  wire [1:0] ram_wr_parity2;

  reg fwft2 = 1'b0;
  reg fall_through2;
  reg wr_data_fwft2;
  reg [DATA_WIDTH2-1:0] fwft_data2 = {DATA_WIDTH2{1'b0}};

  wire [15:0] ram_rd_data2; 
  wire [1:0]  ram_rd_parity2;
  wire ram_clk_b2;
  
  integer number_entries2 = 0;
  reg underrun_status2 = 0;
  reg overrun_status2 = 0;

  generate

    if ((DATA_WIDTH2 == 9)|| (DATA_WIDTH2 == 17)) begin: one_parity_fifo2
      assign ram_wr_data2 = {{16-DATA_WIDTH2{1'b0}}, WR_DATA2};
      assign ram_wr_parity2 = {1'b0, WR_DATA2[DATA_WIDTH2-1]};
      assign RD_DATA2 = fwft2 ? fwft_data2 : {ram_rd_parity2[0], ram_rd_data2[DATA_WIDTH2-2:0]};
    end else if ((DATA_WIDTH2 == 18)) begin: two_parity_fifo2
      assign ram_wr_data2 = WR_DATA2[15:0];
      assign ram_wr_parity2 = WR_DATA2[DATA_WIDTH2-1:DATA_WIDTH2-2];
      assign RD_DATA2 = fwft2 ? fwft_data2 : {ram_rd_parity2[1:0], ram_rd_data2[DATA_WIDTH2-3:0]};
    end else begin: no_parity_fifo2
      assign ram_wr_data2 = fall_through2 ? wr_data_fwft2 : {{16-DATA_WIDTH2{1'b0}}, WR_DATA2};
      assign ram_wr_parity2 = 2'b0;
      assign RD_DATA2 = fwft2 ? fwft_data2 : ram_rd_data2[DATA_WIDTH2-1:0];
    end

    if ( FIFO_TYPE2 == "SYNCHRONOUS" )  begin: sync_fifo2

      always @(posedge WR_CLK2)
        if (WR_EN2 && !RD_EN2) begin
          number_entries2 <= number_entries2 + 1;
          underrun_status2 = 0;
          if (number_entries2 >= fifo_depth2)
            overrun_status2  = 1;
        end
        else if (!WR_EN2 && RD_EN2 && number_entries2 == 0) begin
          number_entries2 <= 0;
          underrun_status2 = 1;
        end
        else if (!WR_EN2 && RD_EN2) begin
          number_entries2 <= number_entries2 - 1;
          underrun_status2 = 0;
        end

      always @(posedge RESET2, posedge WR_CLK2)
        if (RESET2) begin
          fifo_wr_addr2 <= {fifo_addr_width2{1'b0}};
          fifo_rd_addr2 <= {fifo_addr_width2{1'b0}};
          EMPTY2        <= 1'b1;
          FULL2         <= 1'b0;
          ALMOST_EMPTY2 <= 1'b0;
          ALMOST_FULL2  <= 1'b0;
          PROG_EMPTY2   <= 1'b1;
          PROG_FULL2    <= 1'b0;
          OVERFLOW2     <= 1'b0;
          UNDERFLOW2    <= 1'b0;
          number_entries2 = 0;
          fwft2         <= 1'b0;
          fwft_data2    <= {DATA_WIDTH2-1{1'b0}};
          underrun_status2 <=1'b0;
          overrun_status2  <= 1'b0;
        end else begin
          if (WR_EN2)
            fifo_wr_addr2 <= fifo_wr_addr2 + 1'b1;
          EMPTY2        <= ((number_entries2==0) && (underrun_status2==0) || ((RD_EN2 && !WR_EN2) && (number_entries2==1)));
          FULL2         <= ((number_entries2==fifo_depth2) || ((number_entries2==(fifo_depth2-1)) && WR_EN2 && !RD_EN2));
          ALMOST_EMPTY2 <= (((number_entries2==1) && !(RD_EN2 && !WR_EN2)) ||  ((RD_EN2 && !WR_EN2) && (number_entries2==2)));
          ALMOST_FULL2  <= (((number_entries2==(fifo_depth2-1)) && !(!RD_EN2 && WR_EN2)) ||  ((!RD_EN2 && WR_EN2) && (number_entries2==fifo_depth2-2)));
          PROG_EMPTY2   <= ((number_entries2) < (PROG_EMPTY_THRESH2)) || ((RD_EN2 && !WR_EN2) && ((number_entries2) <= PROG_EMPTY_THRESH2) );
          PROG_FULL2    <= ((fifo_depth2-number_entries2) < (PROG_FULL_THRESH2)) || ((!RD_EN2 && WR_EN2) && ((fifo_depth2-number_entries2) <= PROG_FULL_THRESH2) );
          UNDERFLOW2    <= (EMPTY2 && RD_EN2) || (underrun_status2==1);
          OVERFLOW2     <= (FULL2 && WR_EN2) || (overrun_status2==1);
          if (EMPTY2 && WR_EN2 && !fwft2) begin
            fwft_data2 <= WR_DATA2;
            fifo_rd_addr2 <= fifo_rd_addr2 + 1'b1;
            fwft2 <= 1'b1;
          end else if (RD_EN2) begin
            fwft2 <= 1'b0;
            if (!(ALMOST_EMPTY2 && !WR_EN2))
              fifo_rd_addr2 <= fifo_rd_addr2 + 1'b1;
          end
        end

        assign ram_clk_b2 = WR_CLK2;

        initial begin
          #1;
          @(RD_CLK2);
          $display("\nWarning: FIFO36K instance %m RD_CLK2 should be tied to ground when FIFO36K is configured as FIFO_TYPE2=SYNCHRONOUS.");
        end

    end else begin: async_fifo2

      assign ram_clk_b2 = RD_CLK2;

    end

  endgenerate

// Use BRAM
TDP_RAM18KX2 #(
  .INIT1({16384{1'b0}}), // Initial Contents of memory, RAM 1
  .INIT1_PARITY({2048{1'b0}}), // Initial Contents of memory
  .WRITE_WIDTH_A1(DATA_WRITE_WIDTH1), // Write data width on port A, RAM 1 (1-18)
  .WRITE_WIDTH_B1(DATA_WRITE_WIDTH1), // Write data width on port B, RAM 1 (1-18)
  .READ_WIDTH_A1(DATA_READ_WIDTH1), // Read data width on port A, RAM 1 (1-18)
  .READ_WIDTH_B1(DATA_READ_WIDTH1), // Read data width on port B, RAM 1 (1-18)
  .INIT2({16384{1'b0}}), // Initial Contents of memory, RAM 2
  .INIT2_PARITY({2048{1'b0}}), // Initial Contents of memory
  .WRITE_WIDTH_A2(DATA_WRITE_WIDTH2), // Write data width on port A, RAM 2 (1-18)
  .WRITE_WIDTH_B2(DATA_WRITE_WIDTH2), // Write data width on port B, RAM 2 (1-18)
  .READ_WIDTH_A2(DATA_READ_WIDTH2), // Read data width on port A, RAM 2 (1-18)
  .READ_WIDTH_B2(DATA_READ_WIDTH2) // Read data width on port B, RAM 2 (1-18)
) 
tdp_ram18kx2_inst
(
  // Ports for 1st 18K RAM
  .WEN_A1(WR_EN1), // Write-enable port A, RAM 1
  .WEN_B1(1'b0), // Write-enable port B, RAM 1
  .REN_A1(1'b0), // Read-enable port A, RAM 1
  .REN_B1(RD_EN1), // Read-enable port B, RAM 1
  .CLK_A1(WR_CLK1), // Clock port A, RAM 1
  .CLK_B1(ram_clk_b1), // Clock port B, RAM 1
  .BE_A1(2'b11), // Byte-write enable port A, RAM 1
  .BE_B1(2'b11), // Byte-write enable port B, RAM 1
  .ADDR_A1({fifo_wr_addr1, {14-fifo_addr_width1{1'b0}}}), // Address port A, RAM 1
  .ADDR_B1({fifo_rd_addr1, {14-fifo_addr_width1{1'b0}}}), // Address port B, RAM 1
  .WDATA_A1(ram_wr_data1), // Write data port A, RAM 1
  .WPARITY_A1(ram_wr_parity1), // Write parity port A, RAM 1
  .WDATA_B1(16'h0000), // Write data port B, RAM 1
  .WPARITY_B1(2'b00), // Write parity port B, RAM 1
  .RDATA_A1(), // Read data port A, RAM 1
  .RPARITY_A1(), // Read parity port A, RAM 1
  .RDATA_B1(ram_rd_data1), // Read data port B, RAM 1
  .RPARITY_B1(ram_rd_parity1), // Read parity port B, RAM 1
  // Ports for 2nd 18K RAM
  .WEN_A2(WR_EN2), // Write-enable port A, RAM 2
  .WEN_B2(1'b0), // Write-enable port B, RAM 2
  .REN_A2(1'b0), // Read-enable port A, RAM 2
  .REN_B2(RD_EN2), // Read-enable port B, RAM 2
  .CLK_A2(WR_CLK2), // Clock port A, RAM 2
  .CLK_B2(ram_clk_b2), // Clock port B, RAM 2
  .BE_A2(2'b11), // Byte-write enable port A, RAM 2
  .BE_B2(2'b11), // Byte-write enable port B, RAM 2
  .ADDR_A2({fifo_wr_addr2, {14-fifo_addr_width2{1'b0}}}), // Address port A, RAM 2
  .ADDR_B2({fifo_rd_addr2, {14-fifo_addr_width2{1'b0}}}), // Address port B, RAM 2
  .WDATA_A2(ram_wr_data2), // Write data port A, RAM 2
  .WPARITY_A2(ram_wr_parity2), // Write parity port A, RAM 2
  .WDATA_B2(16'h0000), // Write data port B, RAM 2
  .WPARITY_B2(2'b00), // Write parity port B, RAM 2
  .RDATA_A2(), // Read data port A, RAM 2
  .RPARITY_A2(), // Read parity port A, RAM 2
  .RDATA_B2(ram_rd_data2), // Read data port B, RAM 2
  .RPARITY_B2(ram_rd_parity2) // Read parity port B, RAM 2
); initial begin
    case(DATA_WRITE_WIDTH1)
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: FIFO18KX2 instance %m has parameter DATA_WRITE_WIDTH1 set to %d.  Valid values are 9, 18\n", DATA_WRITE_WIDTH1);
      end
    endcase
    case(DATA_READ_WIDTH1)
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: FIFO18KX2 instance %m has parameter DATA_READ_WIDTH1 set to %d.  Valid values are 9, 18\n", DATA_READ_WIDTH1);
      end
    endcase
    case(FIFO_TYPE1)
      "SYNCHRONOUS" ,
      "ASYNCHRONOUS": begin end
      default: begin
        $fatal(1,"\nError: FIFO18KX2 instance %m has parameter FIFO_TYPE1 set to %s.  Valid values are SYNCHRONOUS, ASYNCHRONOUS\n", FIFO_TYPE1);
      end
    endcase
    case(DATA_WRITE_WIDTH2)
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: FIFO18KX2 instance %m has parameter DATA_WRITE_WIDTH2 set to %d.  Valid values are 9, 18\n", DATA_WRITE_WIDTH2);
      end
    endcase
    case(DATA_READ_WIDTH2)
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: FIFO18KX2 instance %m has parameter DATA_READ_WIDTH2 set to %d.  Valid values are 9, 18\n", DATA_READ_WIDTH2);
      end
    endcase
    case(FIFO_TYPE2)
      "SYNCHRONOUS" ,
      "ASYNCHRONOUS": begin end
      default: begin
        $fatal(1,"\nError: FIFO18KX2 instance %m has parameter FIFO_TYPE2 set to %s.  Valid values are SYNCHRONOUS, ASYNCHRONOUS\n", FIFO_TYPE2);
      end
    endcase

  end

endmodule
`endcelldefine