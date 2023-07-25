// --------------------------------------------------------------------------
// ---------------- Copyright (C) 2023 RapidSilicon -------------------------
// --------------------------------------------------------------------------
// ---------------------- FIFO18KX2 Primitive -------------------------------
// --------------------------------------------------------------------------

module FIFO18KX2 #(
    parameter DATA_WIDTH1 = 5'd18,              // Data Width of FIFO1 from 1, 2, 4, 9, 18
    parameter FIFO_TYPE1 = "SYNCHRONOUS",       // Synchronous or Asynchronous FIFO1     
    parameter PROG_EMPTY_THRESH1 = 11'h004,     // Threshold indicating that the FIFO1 buffer is considered Empty
    parameter PROG_FULL_THRESH1 = 11'h4fa,      // Threshold indicating that the FIFO1 buffer is considered Full
    
    parameter DATA_WIDTH2 = 5'd18,              // Data Width of FIFO2 from 1, 2, 4, 9, 18
    parameter FIFO_TYPE2 = "SYNCHRONOUS",       // Synchronous or Asynchronous FIFO2    
    parameter PROG_EMPTY_THRESH2 = 11'h004,     // Threshold indicating that the FIFO2 buffer is considered Empty
    parameter PROG_FULL_THRESH2 = 11'h4fa       // Threshold indicating that the FIFO2 buffer is considered Full
)
(
    // -------------Ports for FIFO 1-----------------
    input wire RESET1,                          // 1-bit input:  Active Low Synchronous Reset
    input wire WR_CLK1,                         // 1-bit input:  Write Clock
    input wire RD_CLK1,                         // 1-bit input:  Read Clock
    input wire RD_EN1,                          // 1-bit input:  Read Enable
    input wire WR_EN1,                          // 1-bit input:  Write Enable
    input wire [DATA_WIDTH1-1:0] WR_DATA1,      // DATA_WIDTH1-bits Data coming inside FIFO
    output wire [DATA_WIDTH1-1:0] RD_DATA1,     // DATA_WIDTH1-bits Data coming out from FIFO
    output wire EMPTY1,                         // 1-bit output: Empty Flag
    output wire FULL1,                          // 1-bit output: Full Flag
    output wire ALMOST_EMPTY1,                  // 1-bit output: This Flag is asserted when FIFO contains EMPTY plus one data words
    output wire ALMOST_FULL1,                   // 1-bit output: This Flag is asserted when FIFO contains FULL minus one data words
    output wire PROG_EMPTY1,                    // 1-bit output: Empty Watermark Flag
    output wire PROG_FULL1,                     // 1-bit output: Full Watermark Flag
    output wire OVERFLOW1,                      // 1-bit output: Overflow Flag 
    output wire UNDERFLOW1,                     // 1-bit output: Underflow Flag

    // -------------Ports for FIFO 2-----------------
    input wire RESET2,                          // 1-bit input:  Active Low Synchronous Reset
    input wire WR_CLK2,                         // 1-bit input:  Write Clock
    input wire RD_CLK2,                         // 1-bit input:  Read Clock
    input wire RD_EN2,                          // 1-bit input:  Read Enable
    input wire WR_EN2,                          // 1-bit input:  Write Enable
    input wire [DATA_WIDTH2-1:0] WR_DATA2,      // DATA_WIDTH2-bits Data coming inside FIFO
    output wire [DATA_WIDTH2-1:0] RD_DATA2,     // DATA_WIDTH2-bits Data coming out from FIFO
    output wire EMPTY2,                         // 1-bit output: Empty Flag
    output wire FULL2,                          // 1-bit output: Full Flag
    output wire ALMOST_EMPTY2,                  // 1-bit output: This Flag is asserted when FIFO contains EMPTY plus one data words
    output wire ALMOST_FULL2,                   // 1-bit output: This Flag is asserted when FIFO contains FULL minus one data words
    output wire PROG_EMPTY2,                    // 1-bit output: Empty Watermark Flag
    output wire PROG_FULL2,                     // 1-bit output: Full Watermark Flag
    output wire OVERFLOW2,                      // 1-bit output: Overflow Flag 
    output wire UNDERFLOW2                      // 1-bit output: Underflow Flag
);

initial 
begin
    if (!(DATA_WIDTH1 == 1 || DATA_WIDTH1 == 2 || DATA_WIDTH1 == 4 || DATA_WIDTH1 == 9 || DATA_WIDTH1 == 18)) 
        begin
        $error("Incorrect DATA_WIDTH1: %0d\nEnter valid DATA_WIDTH1: 1, 2, 4, 8, 9, 18", DATA_WIDTH1);
        $finish;
        end
    if (!(DATA_WIDTH2 == 1 || DATA_WIDTH2 == 2 || DATA_WIDTH2 == 4 || DATA_WIDTH2 == 9 || DATA_WIDTH2 == 18)) 
        begin
        $error("Incorrect DATA_WIDTH2: %0d\nEnter valid DATA_WIDTH2: 1, 2, 4, 8, 9, 18", DATA_WIDTH2);
        $finish;
    end
end

FIFO #(
    .DATA_WIDTH(DATA_WIDTH1),
    .SYNC_FIFO(FIFO_TYPE1),
    .PROG_FULL_THRESH(PROG_FULL_THRESH1),
    .PROG_EMPTY_THRESH(PROG_EMPTY_THRESH1)
)
FIFO18K_1 (
    .WR_DATA(WR_DATA1),
    .RD_DATA(RD_DATA1),
    .EMPTY(EMPTY1),
    .FULL(FULL1),
    .OVERFLOW(OVERFLOW1),
    .UNDERFLOW(UNDERFLOW1),
    .RDEN(RD_EN1),
    .WREN(WR_EN1),
    .ALMOST_EMPTY(ALMOST_EMPTY1),
    .ALMOST_FULL(ALMOST_FULL1),
    .PROG_EMPTY(PROG_EMPTY1),
    .PROG_FULL(PROG_FULL1),
    .WRCLK(WR_CLK1),
    .RDCLK(RD_CLK1),
    .RESET(RESET1)
);

FIFO #(
    .DATA_WIDTH(DATA_WIDTH2),
    .SYNC_FIFO(FIFO_TYPE2),
    .PROG_FULL_THRESH(PROG_FULL_THRESH2),
    .PROG_EMPTY_THRESH(PROG_EMPTY_THRESH2)
)
FIFO18K_2 (
    .WR_DATA(WR_DATA2),
    .RD_DATA(RD_DATA2),
    .EMPTY(EMPTY2),
    .FULL(FULL2),
    .OVERFLOW(OVERFLOW2),
    .UNDERFLOW(UNDERFLOW2),
    .RDEN(RD_EN2),
    .WREN(WR_EN2),
    .ALMOST_EMPTY(ALMOST_EMPTY2),
    .ALMOST_FULL(ALMOST_FULL2),
    .PROG_EMPTY(PROG_EMPTY2),
    .PROG_FULL(PROG_FULL2),
    .WRCLK(WR_CLK2),
    .RDCLK(RD_CLK2),
    .RESET(RESET2)
);

endmodule