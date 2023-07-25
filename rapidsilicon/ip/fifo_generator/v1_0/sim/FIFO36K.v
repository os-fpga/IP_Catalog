// --------------------------------------------------------------------------
// ---------------- Copyright (C) 2023 RapidSilicon -------------------------
// --------------------------------------------------------------------------
// ---------------------- FIFO36K Primitive ---------------------------------
// --------------------------------------------------------------------------

module FIFO36K #(
    parameter   DATA_WIDTH          = 6'd36,               // Supported Data Width > 36
    parameter   FIFO_TYPE           = "SYNCHRONOUS",       // Synchronous or Asynchronous
    parameter   PROG_FULL_THRESH    = 12'hffa,             // Threshold indicating that the FIFO buffer is considered Full
    parameter   PROG_EMPTY_THRESH   = 12'h004              // Threshold indicating that the FIFO buffer is considered Empty
)
(
    input wire  [DATA_WIDTH-1:0] WR_DATA,                  // 36-bits Data coming inside FIFO
    output wire [DATA_WIDTH-1:0] RD_DATA,                  // 36-bits Data coming out from FIFO
    output wire EMPTY,                                     // 1-bit output: Empty Flag
    output wire FULL,                                      // 1-bit output: Full Flag
    output wire OVERFLOW,                                  // 1-bit output: Overflow Flag 
    output wire UNDERFLOW,                                 // 1-bit output: Underflow Flag
    input wire  RD_EN,                                     // 1-bit input:  Read Enable
    input wire  WR_EN,                                     // 1-bit input:  Write Enable
    output wire ALMOST_EMPTY,                              // 1-bit output: This Flag is asserted when FIFO contains EMPTY plus one data words.
    output wire ALMOST_FULL,                               // 1-bit output: This Flag is asserted when FIFO contains FULL minus one data words.
    output wire PROG_EMPTY,                                // 1-bit output: Empty Watermark Flag
    output wire PROG_FULL,                                 // 1-bit output: Full Watermark Flag
    input wire  WR_CLK,                                    // 1-bit input:  Write Clock
    input wire  RD_CLK,                                    // 1-bit input:  Read Clock
    input wire  RESET                                      // 1-bit input:  Active Low Synchronous Reset
);

initial 
begin
    if (DATA_WIDTH != 36)
        begin
        $error("Incorrect DATA_WIDTH: %0d\nEnter valid DATA_WIDTH: 36", DATA_WIDTH);
        $finish;
        end
end

FIFO #(
    .DATA_WIDTH(DATA_WIDTH),
    .SYNC_FIFO(FIFO_TYPE),
    .PROG_FULL_THRESH(PROG_FULL_THRESH),
    .PROG_EMPTY_THRESH(PROG_EMPTY_THRESH)
)
FIFO (
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
    .RDEN(RD_EN),
    .WREN(WR_EN),
    .WRCLK(WR_CLK),
    .RDCLK(RD_CLK),
    .RESET(RESET)
);
endmodule