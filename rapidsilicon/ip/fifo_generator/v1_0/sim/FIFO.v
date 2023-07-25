// --------------------------------------------------------------------------
// ---------------- Copyright (C) 2023 RapidSilicon -------------------------
// --------------------------------------------------------------------------
// ---------------------- FIFO Primitive ------------------------------------
// --------------------------------------------------------------------------

module FIFO #(
    // Parameter Definition
    parameter   DATA_WIDTH          = 6'd36,
    parameter   SYNC_FIFO           = "SYNCHRONOUS",
    parameter   PROG_FULL_THRESH    = 12'b111111111100,
    parameter   PROG_EMPTY_THRESH   = 12'b000000000000
)
(
    // Input/Output
    input wire  [DATA_WIDTH-1:0] WR_DATA,
    output wire [DATA_WIDTH-1:0] RD_DATA,
    output wire EMPTY,
    output wire FULL,
    output wire OVERFLOW,
    output wire UNDERFLOW,
    input wire  RDEN,
    input wire  WREN,
    output wire ALMOST_EMPTY,
    output wire ALMOST_FULL,
    output wire PROG_FULL,
    output wire PROG_EMPTY,
    input wire  WRCLK,
    input wire  RDCLK,
    input wire  RESET
);

// Signals
wire TEMP_CLK;

// Initial Block
initial 
begin
    if (!(SYNC_FIFO === "SYNCHRONOUS" || SYNC_FIFO === "ASYNCHRONOUS")) begin
        $error("Incorrect SYNC_FIFO Value: '%s'\nEnter valid SYNC_FIFO value: 'SYNCHRONOUS'/'ASYNCHRONOUS'", SYNC_FIFO);
        $finish;
    end
end

// Common Clock when Synchronous Selected
assign TEMP_CLK         = (SYNC_FIFO == "SYNCHRONOUS")     ? WRCLK     : RDCLK;

// Synchronous/Asynchronous FIFO 
localparam SYNC_FIFO1   = (SYNC_FIFO == "SYNCHRONOUS")     ? 1'b1      : 1'b0;

// FIFO
generate
if (DATA_WIDTH == 36)
    begin
        RS_TDP36K #(
            .MODE_BITS({SYNC_FIFO1, {4{3'b110}}, 1'b1, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH, PROG_FULL_THRESH, 39'd0, 1'b0})
            )
        RS_TDP36K_36 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(TEMP_CLK),
            .WDATA_A1(WR_DATA[17:0]),
            .WDATA_A2(WR_DATA[35:18]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[17:0]),
            .RDATA_B2(RD_DATA[35:18]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(TEMP_CLK)
        );
    end

else if (DATA_WIDTH == 18)
    begin
        RS_TDP36K #(
            // ----------------------------------------------------------Appending 12th bit as dont care bit
            .MODE_BITS({SYNC_FIFO1, {4{3'b010}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_18 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(TEMP_CLK),
            .WDATA_A1(WR_DATA[17:0]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[17:0]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(TEMP_CLK)
        );
    end

else if (DATA_WIDTH == 9)
    begin
        RS_TDP36K #(
            // ----------------------------------------------------------Appending 12th bit as dont care bit
            .MODE_BITS({SYNC_FIFO1, {4{3'b100}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_9 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(TEMP_CLK),
            .WDATA_A1(WR_DATA[8:0]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[8:0]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(TEMP_CLK)
        );
    end

else if (DATA_WIDTH == 4)
    begin
        RS_TDP36K #(
            // ----------------------------------------------------------Appending 12th bit as dont care bit
            .MODE_BITS({SYNC_FIFO1, {4{3'b001}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_4 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(TEMP_CLK),
            .WDATA_A1(WR_DATA[3:0]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[3:0]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(TEMP_CLK)
        );
    end

else if (DATA_WIDTH == 2)
    begin
        RS_TDP36K #(
            // ----------------------------------------------------------Appending 12th bit as dont care bit
            .MODE_BITS({SYNC_FIFO1, {4{3'b011}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_2 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(TEMP_CLK),
            .WDATA_A1(WR_DATA[1:0]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[1:0]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(TEMP_CLK)
        );
    end

else
    begin
        RS_TDP36K #(
            // ----------------------------------------------------------Appending 12th bit as dont care bit
            .MODE_BITS({SYNC_FIFO1, {4{3'b101}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_1 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(TEMP_CLK),
            .WDATA_A1(WR_DATA[0:0]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[0:0]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(TEMP_CLK)
        );
    end
endgenerate

endmodule