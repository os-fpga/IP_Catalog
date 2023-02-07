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
reg [11:0]a;
reg [9:0]b;
wire [21:0]z1, z2;
reg clk;

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

integer i, mismatch=0;
reg [6:0]cycle;

initial
begin
for (i=0; i<=100; i=i+1)
begin
repeat (1) @ (posedge clk);
a <= $random;
b <= $random;
compare(cycle);
end

if(mismatch == 0)
        $display("\n**** All Comparison Matched ***\n**** Simulation Passed ****");
    else
        $display("%0d comparison(s) mismatched\nERROR: SIM: Simulation Failed", mismatch);
$finish;
end

task compare(input integer cycle);
    if(z1 !== z2) begin
        $display("Z_Out mismatch. dut1: %0h, dut2: %0h, Time: %0t", z1, z2,$time);
        mismatch = mismatch+1;
    end
endtask

initial begin
    $dumpfile("dsp.vcd");
    $dumpvars;
end
endmodule


module dsp(a, b, z);
input wire [11:0]a;
input wire [9:0]b;
output wire [21:0]z;
assign z = a*b;
endmodule