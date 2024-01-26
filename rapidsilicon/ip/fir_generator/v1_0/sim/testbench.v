`timescale 1ns/1ps

module tb;
reg clk, rst; reg [17:0] din; wire [37:0] dout; wire ready;
initial begin
    clk = 1'b1;
    forever #5 clk = ~clk;
end
initial begin
    rst = 1'b1;
    # 10;
    rst = 1'b0;
end

FIR_generator fir_filter(
    .clk(clk),
    .rst(rst),
    .data_in(din),
    .data_out(dout),
    .ready(ready)
);

initial begin
    din <= 0;
    @(posedge ready);
    for (integer i = 1; i <= 4; i= i + 1) begin
        din <= i;
        repeat (1) @ (posedge clk);
    end
    #1000;
    $finish;
end

initial begin
    $dumpfile("fir.vcd");
    $dumpvars;
end
endmodule