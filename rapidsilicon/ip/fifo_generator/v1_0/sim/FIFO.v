// --------------------------------------------------------------------------
// ---------------- Copyright (C) 2023 RapidSilicon -------------------------
// --------------------------------------------------------------------------
// ---------------------- FIFO Primitive ------------------------------------
// --------------------------------------------------------------------------

module FIFO #(
    // Parameter Definition
    parameter   DATA_WRITE_WIDTH    = 6'd36,
    parameter   DATA_READ_WIDTH     = 6'd36,
    parameter   SYNC_FIFO           = "SYNCHRONOUS",
    parameter   PROG_FULL_THRESH    = 12'b111111111100,
    parameter   PROG_EMPTY_THRESH   = 12'b000000000000
)
(
    // Input/Output
    input wire  [DATA_WRITE_WIDTH-1:0] WR_DATA,
    output wire [DATA_READ_WIDTH-1:0] RD_DATA,
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
wire second_clk;

// Initial Block
initial 
begin
    if (!(SYNC_FIFO === "SYNCHRONOUS" || SYNC_FIFO === "ASYNCHRONOUS")) begin
        $error("Incorrect SYNC_FIFO Value: '%s'\nEnter valid SYNC_FIFO value: 'SYNCHRONOUS'/'ASYNCHRONOUS'", SYNC_FIFO);
        $finish;
    end
end

// Common Clock when Synchronous Selected
assign second_clk         = (SYNC_FIFO == "SYNCHRONOUS")     ? WRCLK     : RDCLK;

// Synchronous/Asynchronous FIFO 
localparam sync_fifo   = (SYNC_FIFO == "SYNCHRONOUS")     ? 1'b1      : 1'b0;

// FIFO
generate
if (DATA_WRITE_WIDTH == 6'd36 && DATA_READ_WIDTH == 6'd36)
    begin
        RS_TDP36K #(
            .MODE_BITS({sync_fifo, {4{3'b110}}, 1'b1, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH, PROG_FULL_THRESH, 39'd0, 1'b0})
            )
        RS_TDP36K_W36_R36 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1(WR_DATA[17:0]),
            .WDATA_A2(WR_DATA[35:18]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[17:0]),
            .RDATA_B2(RD_DATA[35:18]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end

else if (DATA_WRITE_WIDTH == 5'd18 && DATA_READ_WIDTH == 5'd18)
    begin
        RS_TDP36K #(
            // ----------------------------------------------------------Appending 12th bit as dont care bit
            .MODE_BITS({sync_fifo, {4{3'b010}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_W18_R18 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1(WR_DATA[17:0]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[17:0]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end

else if (DATA_WRITE_WIDTH == 4'd9 && DATA_READ_WIDTH == 4'd9)
    begin
        wire [17:0] rd_data;
        assign RD_DATA = {rd_data[16], rd_data[7:0]};
        RS_TDP36K #(
            // ----------------------------------------------------------Appending 12th bit as dont care bit
            .MODE_BITS({sync_fifo, {4{3'b100}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_W9_R9 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1({1'dx, WR_DATA[8], {8{1'dx}}, WR_DATA[7:0]}),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(rd_data),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end
else if (DATA_WRITE_WIDTH == 6'd36 && DATA_READ_WIDTH == 5'd18)
    begin
        RS_TDP36K #(
            .MODE_BITS({sync_fifo, {2{3'b010}}, {2{3'b110}}, 1'b1, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH, PROG_FULL_THRESH, 39'd0, 1'b0})
            )
        RS_TDP36K_W36_R18 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1(WR_DATA[17:0]),
            .WDATA_A2(WR_DATA[35:18]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[17:0]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end
else if (DATA_WRITE_WIDTH == 6'd36 && DATA_READ_WIDTH == 4'd9)
    begin
        wire [17:0] rd_data;
        assign RD_DATA = {rd_data[16], rd_data[7:0]};
        RS_TDP36K #(
            .MODE_BITS({sync_fifo, {2{3'b100}}, {2{3'b110}}, 1'b1, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH, PROG_FULL_THRESH, 39'd0, 1'b0})
            )
        RS_TDP36K_W36_R9 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1({WR_DATA[17], WR_DATA[8], WR_DATA[16:9], WR_DATA[7:0]}),
            .WDATA_A2({WR_DATA[35], WR_DATA[26], WR_DATA[34:27], WR_DATA[25:18]}),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(rd_data),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end
else if (DATA_WRITE_WIDTH == 5'd18 && DATA_READ_WIDTH == 4'd9)
    begin
        wire [17:0] rd_data;
        assign RD_DATA = {rd_data[16], rd_data[7:0]};
        // ----------------------------------------------------------Appending 12th bit as dont care bit
        RS_TDP36K #(
            .MODE_BITS({sync_fifo, {2{3'b100}}, {2{3'b010}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_W18_R9 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1({WR_DATA[17], WR_DATA[8], WR_DATA[16:9], WR_DATA[7:0]}),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(rd_data),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end
else if (DATA_WRITE_WIDTH == 4'd9 && DATA_READ_WIDTH == 5'd18)
    begin
        wire [17:0] rd_data;
        assign RD_DATA = {rd_data[17], rd_data[15:8], rd_data[16], rd_data[7:0]};
        RS_TDP36K #(
            // ----------------------------------------------------------Appending 12th bit as dont care bit
            .MODE_BITS({sync_fifo, {2{3'b010}}, {2{3'b100}}, 1'b1, 1'b0, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH[10:0], 1'b0, PROG_FULL_THRESH[10:0], 39'd0, 1'b1})
            )
        RS_TDP36K_W9_R18 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1({1'hx, WR_DATA[8], {8{1'hx}}, WR_DATA[7:0]}),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(rd_data),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end
else if (DATA_WRITE_WIDTH == 5'd18 && DATA_READ_WIDTH == 6'd36)
    begin
        RS_TDP36K #(
            .MODE_BITS({sync_fifo, {2{3'b110}}, {2{3'b010}}, 1'b1, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH, PROG_FULL_THRESH, 39'd0, 1'b0})
            )
        RS_TDP36K_W18_R36 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1(WR_DATA[17:0]),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(RD_DATA[17:0]),
            .RDATA_B2(RD_DATA[35:18]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end
else 
    begin
        wire [35:0] rd_data;
        assign RD_DATA = {rd_data[35], rd_data[33:26], rd_data[34], rd_data[25:18], rd_data[17], rd_data[15:8] ,rd_data[16], rd_data[7:0]};
        RS_TDP36K #(
            .MODE_BITS({sync_fifo, {2{3'b110}}, {2{3'b100}}, 1'b1, 1'b0, 1'b0, 1'b0, PROG_EMPTY_THRESH, PROG_FULL_THRESH, 39'd0, 1'b0})
            )
        RS_TDP36K_W9_R36 (
            .WEN_A1(WREN),
            .REN_B1(RDEN),
            .CLK_A1(WRCLK),
            .CLK_B1(second_clk),
            .WDATA_A1({1'hx, WR_DATA[8], {8{1'hx}}, WR_DATA[7:0]}),
            .RDATA_A1({EMPTY, ALMOST_EMPTY, PROG_EMPTY, UNDERFLOW, FULL, ALMOST_FULL, PROG_FULL, OVERFLOW}),
            .RDATA_B1(rd_data[17:0]),
            .RDATA_B2(rd_data[35:18]),
            .FLUSH1(RESET),
            .CLK_A2(WRCLK),
            .CLK_B2(second_clk)
        );
    end

endgenerate

endmodule