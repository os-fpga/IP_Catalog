// --------------------------------------------------------------------------
// ---------------- Copyright (C) 2023 RapidSilicon -------------------------
// --------------------------------------------------------------------------
// ---------------------- FIFO18K Primitive ---------------------------------
// --------------------------------------------------------------------------

module FIFO18K #(
    parameter   DATA_WIDTH          = 18,                  // Data Width of FIFO from 1, 2, 4, 9, 18
    parameter   SYNC_FIFO           = "TRUE",              // Synchronous or Asynchronous FIFO "TRUE"/"FALSE"
    parameter   PROG_FULL_THRESH    = 12'b100000000000,    // Threshold indicating that the FIFO buffer is considered Full
    parameter   PROG_EMPTY_THRESH   = 12'b111111111100     // Threshold indicating that the FIFO buffer is considered Empty
)
(
    input wire  [DATA_WIDTH-1:0] WR_DATA,                  // 18-bits Data coming inside FIFO
    output wire [DATA_WIDTH-1:0] RD_DATA,                  // 18-bits Data coming out from FIFO
    output wire EMPTY,                                     // 1-bit output: Empty Flag
    output wire FULL,                                      // 1-bit output: Full Flag
    output wire OVERFLOW,                                  // 1-bit output: Overflow Flag 
    output wire UNDERFLOW,                                 // 1-bit output: Underflow Flag
    input wire  RDEN,                                      // 1-bit input:  Read Enable
    input wire  WREN,                                      // 1-bit input:  Write Enable
    output wire ALMOST_EMPTY,                              // 1-bit output: This Flag is asserted when FIFO contains EMPTY plus one data words.
    output wire ALMOST_FULL,                               // 1-bit output: This Flag is asserted when FIFO contains FULL minus one data words.
    output wire PROG_EMPTY,                                // 1-bit output: Empty Watermark Flag
    output wire PROG_FULL,                                 // 1-bit output: Full Watermark Flag
    input wire  WRCLK,                                     // 1-bit input:  Write Clock
    input wire  RDCLK,                                     // 1-bit input:  Read Clock
    input wire  RESET                                      // 1-bit input:  Active Low Synchronous Reset
);

initial 
begin
    if (!(DATA_WIDTH == 1 || DATA_WIDTH == 2 || DATA_WIDTH == 4 || DATA_WIDTH == 9 || DATA_WIDTH == 18)) 
        begin
        $error("Incorrect DATA_WIDTH: %0d\nEnter valid DATA_WIDTH: 1, 2, 4, 8, 9, 18", DATA_WIDTH);
        $finish;
        end
end

FIFO #(
    .DATA_WIDTH(DATA_WIDTH),
    .SYNC_FIFO(SYNC_FIFO),
    .PROG_FULL_THRESH(PROG_FULL_THRESH),
    .PROG_EMPTY_THRESH(PROG_EMPTY_THRESH)
)
FIFO_insta_1(
    .WR_DATA(WR_DATA),
    .RD_DATA(RD_DATA),
    .EMPTY(EMPTY),
    .FULL(FULL),
    .ALMOST_EMPTY(ALMOST_EMPTY),
    .ALMOST_FULL(ALMOST_FULL),
    .PROG_EMPTY(PROG_EMPTY),
    .PROG_FULL(PROG_FULL),
    .OVERFLOW(OVERFLOW),
    .UNDERFLOW(UNDERFLOW),
    .RDEN(RDEN),
    .WREN(WREN),
    .WRCLK(WRCLK),
    .RDCLK(RDCLK),
    .RESET(RESET)
);
endmodule