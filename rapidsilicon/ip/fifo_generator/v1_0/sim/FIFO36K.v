// --------------------------------------------------------------------------
// ---------------- Copyright (C) 2023 RapidSilicon -------------------------
// --------------------------------------------------------------------------
// ---------------------- FIFO36K Primitive ---------------------------------
// --------------------------------------------------------------------------

module FIFO36K #(
    parameter   DATA_WIDTH_WRITE    = 6'd36,               // Supported Data Width 1 - 36
    parameter   DATA_WIDTH_READ     = 6'd36,               // Supported Data Width 1 - 36
    parameter   FIFO_TYPE           = "SYNCHRONOUS",       // Synchronous or Asynchronous
    parameter   PROG_FULL_THRESH    = 12'hffa,             // Threshold indicating that the FIFO buffer is considered Full
    parameter   PROG_EMPTY_THRESH   = 12'h004              // Threshold indicating that the FIFO buffer is considered Empty
)
(
    input wire  [DATA_WIDTH_WRITE-1:0] WR_DATA,            // 36-bits Data coming inside FIFO
    output wire [DATA_WIDTH_READ-1:0] RD_DATA,             // 36-bits Data coming out from FIFO
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

localparam data_width_width = 
    (DATA_WIDTH_WRITE > 5'd18) ? 6'd36 :
    (DATA_WIDTH_WRITE > 4'd9)  ? 5'd18 :
                          DATA_WIDTH_WRITE;
localparam data_width_read = 
    (DATA_WIDTH_READ > 5'd18) ? 6'd36 :
    (DATA_WIDTH_READ > 4'd9)  ? 5'd18 :
                          DATA_WIDTH_READ;

initial begin
    if ((DATA_WIDTH_WRITE < 1'd1) || (DATA_WIDTH_WRITE > 6'd36)) begin
       $display("FIFO36K instance %m DATA_WIDTH_WRITE set to incorrect value, %d.  Values must be between 1 and 36.", DATA_WIDTH_WRITE);
    #1 $stop;
    end
    if ((DATA_WIDTH_READ < 1'd1) || (DATA_WIDTH_READ > 6'd36)) begin
       $display("FIFO36K instance %m DATA_WIDTH_READ set to incorrect value, %d.  Values must be between 1 and 36.", DATA_WIDTH_READ);
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

FIFO #(
    .DATA_WIDTH_WRITE(data_width_width),
    .DATA_WIDTH_READ(data_width_read),
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