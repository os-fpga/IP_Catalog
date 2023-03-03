`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01/05/2023 03:54:34 PM
// Design Name: 
// Module Name: test
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


module test();
reg   [9:0] addr_A;
reg   [31:0] din_A;
wire  [31:0] dout_dut, dout_wrap;
reg          clk_A;
reg          wen_A;
reg          ren_A;

integer mismatch=0;
reg [6:0]cycle;

on_chip_memory_wrapper wrapper(.*, .dout_A(dout_wrap));

rams_sp_1024x32 dut (
.addr_A(addr_A),
.din_A(din_A),
.clk_A(clk_A),
.dout_A(dout_dut),
.wen_A(wen_A),
.ren_A(ren_A)
);

always #(10)   
clk_A = !clk_A;

integer i;
initial begin
    {clk_A,  wen_A, ren_A, addr_A ,din_A, cycle, i} = 0;
    
    repeat (2) @(posedge clk_A);
    
    // write and simulatnously reads from registered address
    for (i=0; i<1024; i=i+1)begin
        repeat (1) @ (posedge clk_A)
        addr_A <= i; wen_A <=1; ren_A<=1; din_A<= $random;
        cycle = cycle +1;
        compare(cycle);
    end

    // not writing and reading from the last registered addr_A
    for (i=0; i<1024; i=i+1)begin
        repeat (1) @ (posedge clk_A)
        addr_A <= i; wen_A <=0; ren_A<=1; 
        cycle = cycle +1;
        compare(cycle);
    end

    // write and simulatnously reads from registered address when wen_A was 1
    for (i=0; i<1024; i=i+1)begin
        repeat (1) @ (posedge clk_A)
        addr_A <= i; wen_A <=1; ren_A<=0; din_A<= $random;
        repeat (1) @ (posedge clk_A)
        addr_A <= i; wen_A <=0; ren_A<=1;
        cycle = cycle +2;
        compare(cycle);
    end

    if(mismatch == 0)
        $display("\n**** All Comparison Matched ***\nSimulation Passed");
    else
        $display("%0d comparison(s) mismatched\nERROR: SIM: Simulation Failed", mismatch);
    
    repeat (10) @(posedge clk_A); 
    $finish;
    end

    task compare(input integer cycle);
    //$display("\n Comparison at cycle %0d", cycle);
    if(dout_dut !== dout_wrap) begin
        $display("dout_A mismatch. Golden: %0h, Wrapper: %0h, Time: %0t", dout_dut, dout_wrap,$time);
        mismatch = mismatch+1;
    end
    endtask

initial begin
    $dumpfile("tb.vcd");
    $dumpvars;
end
endmodule

module rams_sp_1024x32 (clk_A, wen_A, ren_A, addr_A, din_A, dout_A);
input clk_A, rst;
input wen_A, ren_A;
input [9:0] addr_A;
input [31:0] din_A;
output reg [31:0] dout_A;
reg [31:0] RAM [1023:0];
always @(posedge clk_A)
    begin
        if (wen_A)
            RAM[addr_A] <= din_A;
        if (ren_A)
            if (wen_A)
                dout_A <= din_A;
            else
                dout_A <= RAM[addr_A];
    end

endmodule
