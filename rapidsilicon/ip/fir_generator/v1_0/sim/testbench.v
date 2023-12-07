`timescale 1ns/1ps

module tb;
reg clk, rst; reg [17:0] din; wire [37:0] dout1, dout2;
initial begin
    clk = 1'b1;
    forever #5 clk = ~clk;
end
initial begin
    rst = 1'b1;
    # 10;
    rst = 1'b0;
end

FIR_generator fir_filter_dut(
    .clk(clk),
    .rst(rst),
    .data_in(din),
    .data_out(dout1)
);

fir fir_dut(
    .clk(clk),
    .rst(rst),
    .filter_in(din),
    .filter_out(dout2)
);


initial begin
    for (integer i = 0; i <=30; i = i + 1) begin
        din <= $random;
        repeat(1) @ (posedge clk);
    end
    #500;
    $finish;
end

initial begin
    // $dumpfile("fir.vcd");
    $dumpvars;
end
endmodule