`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12/09/2022 11:22:44 AM
// Design Name: 
// Module Name: tb_dsp
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module tb_dsp;
reg [33:0]a;
reg [33:0]b;
wire [65:0]z1, z2;
reg clk, reset, clk1;

dsp_wrapper dut1(
.a(a),
.b(b),
.z(z1)
);

dsp dut2(
.a(a),
.b(b),
.z(z2)
);

initial 
begin
clk = 1'b0;
forever #10 clk = ~clk;
end

initial 
begin
// reset = 1'b0;
// #2;
reset = 1'b1;
a=0;
b=0;
#2;
reset = 1'b0;
end

initial 
begin
clk1 = 1'b0;
forever #5 clk1 = ~clk1;
end

integer i, mismatch=0;
reg [6:0]cycle;

initial
begin
for (i=0; i<4; i=i+1)
begin
repeat (2) @ (posedge clk1);
a <= $random;
b <= $random;
compare(cycle);
end

if(mismatch == 0)
        $display("\n**** All Comparison Matched ***\n**** Simulation Passed ****");
    else
        $display("%0d comparison(s) mismatched\nERROR: SIM: Simulation Failed", mismatch);
        #30;
$finish;
end

task compare(input integer cycle);
    if(z1 !== z2) begin
        $display("Z_Out mismatch. dut1: %0h, dut2: %0h, Time: %0t", z1, z2,$time);
        mismatch = mismatch+1;
    end
endtask

initial begin
    $dumpfile("dsp1.vcd");
    $dumpvars;
end
endmodule


module dsp(a, b, z);
input [33:0]a;
input [33:0]b;
output [65:0]z;
assign z = a*b;
endmodule