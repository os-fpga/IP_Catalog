`timescale 1ns / 1ps

module testbench;
localparam DEPTH = 2048;
localparam WIDTH = 36;
reg [WIDTH - 1:0] din; wire [WIDTH - 1:0] dout;
reg wrt_clk, rd_clk, rst, wr_en, rd_en; wire full, empty, almost_empty, almost_full, underflow, overflow, prog_empty, prog_full;
FIFO_generator fifo(.din(din), .dout(dout), .wrt_clock(wrt_clk), .rd_clock(rd_clk), .rst(rst), .wr_en(wr_en), .rd_en(rd_en),
.full(full), .empty(empty), .underflow(underflow), .overflow(overflow));
integer mismatch = 0; integer i = 0;
reg [WIDTH - 1:0] mem [0:DEPTH];
initial begin
    rst = 1'b1;
    rd_en = 1'b0;
    # 20;
    rst = 1'b0;
end

initial begin
    wrt_clk = 1'b1;
    forever #5 wrt_clk = ~wrt_clk;
end

initial begin
    rd_clk = 1'b1;
    forever #5 rd_clk = ~rd_clk;
end

initial begin
    # 20;
    repeat (1) @ (posedge wrt_clk);
    wr_en = 1'b1;
    for (i=1; i<=DEPTH; i=i+1) begin
        din <= i;
        mem [i] <= i;
        repeat (1) @ (posedge wrt_clk);
    end

    repeat (1) @ (posedge wrt_clk);
    wr_en = 1'b0;
    rd_en = 1'b1;
    for (integer i=1; i<=DEPTH; i=i+1) begin
        repeat (1) @ (posedge rd_clk);
        if (dout !== mem [i]) begin
            $display("DOUT mismatch. din: %0d, dout: %0d, Entry No.: %0d", mem[i], dout, i);
            mismatch = mismatch+1;
        end
    end
    rd_en = 1'b0;

    if(mismatch == 0)
        $display("\n**** All Comparison Matched ****\n**** Simulation Passed ****");
    else
        $display("%0d comparison(s) mismatched\nERROR: SIM: Simulation Failed", mismatch);
    
    $finish;
end

initial begin
    $dumpfile("fifo.vcd");
    $dumpvars;
end
endmodule