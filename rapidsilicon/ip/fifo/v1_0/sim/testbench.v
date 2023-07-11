`timescale 1ns / 1ps

module tb;
parameter DEPTH = 3072;
parameter WIDTH = 36;
reg [WIDTH - 1:0] din; wire [WIDTH - 1:0] dout;
reg wrt_clk, rd_clk, rst, wr_en, rd_en; wire full, empty, almost_empty, almost_full, underflow, overflow, prog_empty, prog_full;
FIFO_wrapper fifo(.din(din), .dout(dout), .clk(wrt_clk), .rst(rst), .wr_en(wr_en), .rd_en(rd_en),
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
    for (i=1; i<=DEPTH+10; i=i+1) begin
        din <= i;
        mem [i] <= i;
        repeat (1) @ (posedge wrt_clk);
    end

    repeat (1) @ (posedge wrt_clk);
    wr_en = 1'b0;
    rd_en = 1'b1;
    for (integer i=1; i<=1000; i=i+1) begin
        repeat (1) @ (posedge wrt_clk);
        if (dout !== mem [i]) begin
            $display("DOUT mismatch. din: %0d, dout: %0d, Entry No.: %0d", mem[i], dout, i);
            mismatch = mismatch+1;
        end
    end
    rd_en = 1'b0;
    wr_en =1'b1;
    for (integer j=1; j<=1020; j=j+1) begin
        din <= j;
        mem [j] <= j;
        repeat (1) @ (posedge wrt_clk);
    end
    wr_en = 1'b0;
    rd_en = 1'b1;
    for (integer i=1; i<=DEPTH; i=i+1) begin
        repeat (1) @ (posedge wrt_clk);
        if (dout !== mem [(i+1000 - 1)%DEPTH + 1]) begin
            $display("DOUT mismatch next. din: %0d, dout: %0d, Entry No.: %0d", mem[(i+1000 - 1)%DEPTH + 1], dout, (i+1000 - 1)%DEPTH + 1);
            mismatch = mismatch+1;
        end
    end

    if(mismatch == 0)
        $display("\n**** All Comparison Matched ***\n**** Simulation Passed ****");
    else
        $display("%0d comparison(s) mismatched\nERROR: SIM: Simulation Failed", mismatch);
end

initial begin
    $dumpfile("fifo.vcd");
    $dumpvars;
    #200000;
    $finish;
end
endmodule