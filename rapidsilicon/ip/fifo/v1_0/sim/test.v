`timescale 1ns / 1ps

module tb;
reg [73:0] din; wire [73:0] dout;
reg clk, rst, wr_en, rd_en; wire full, empty, almost_empty, almost_full, underflow, overflow;
FIFO_wrapper fifo(.din(din), .dout(dout), .clk(clk), .rst(rst), .wr_en(wr_en), .rd_en(rd_en),
.full(full), .empty(empty), .almost_empty(almost_empty), .almost_full(almost_full), .underflow(underflow),
.overflow(overflow));

initial begin
    rst = 1'b1;
    #2;
    rst = 1'b0;
    wr_en = 1'b1;
    rd_en = 1'b0;
end

initial begin
    clk = 1'b1;
    forever #5 clk = ~clk;
end
initial begin
    for (integer i=0; i<3072; i=i+1) begin
        din <= $random;
        repeat (1) @ (posedge clk);
    end
    #5;
    wr_en = 1'b0;
    rd_en = 1'b1;
end

initial begin
    $dumpfile("fifo.vcd");
    $dumpvars;
    #80000;
    $finish;
end
endmodule
