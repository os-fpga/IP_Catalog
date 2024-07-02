`timescale 1ns / 1ps

module testbench();
reg   [9:0] addr_A;
reg   [31:0] din_A;
wire  [31:0] dout_dut, dout_wrap;
reg          clk_A;
reg          wen_A;
reg          ren_A;
reg [3:0] be_A;

integer mismatch=0;
reg [6:0]cycle;

on_chip_memory on_chip_memory_inst (
    .addr_A(addr_A),
    .din_A(din_A),
    .clk_A(clk_A),
    .wen_A(wen_A),
    .ren_A(ren_A),
    .be_A({4{1'b1}}),
    .dout_A(dout_wrap)
);

ram dut (
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
    {clk_A, wen_A, ren_A, addr_A ,din_A, cycle, i} = 0;
    
    repeat (2) @(posedge clk_A);
    
    // writing Data
    for (i=0; i<= 1023; i=i+1)begin
        repeat (1) @ (posedge clk_A)
        addr_A <= i; wen_A <=1; ren_A<=0; din_A<= $random;
        cycle = cycle +1;
    end

    //  Reading Data
    for (i=0; i<= 1023; i=i+1)begin
        repeat (1) @ (posedge clk_A)
        addr_A <= i; wen_A <=0; ren_A<=1; 
        cycle = cycle +1;
        compare(cycle);
    end

    // writes and reads simulatnously 
    for (i=0; i<= 1023; i=i+1)begin
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
    if(dout_dut !== dout_wrap) begin
        $display("dout_A mismatch. Golden: %0h, Wrapper: %0h, Time: %0t", dout_dut, dout_wrap, $time);
        mismatch = mismatch+1;
    end
    endtask

initial begin
    $dumpfile("ocm.vcd");
    $dumpvars;
end
endmodule

module ram (clk_A, wen_A, ren_A, addr_A, din_A, dout_A);
input clk_A;
input wen_A, ren_A;
input [9:0] addr_A;
input [31:0] din_A;
output reg [31:0] dout_A = 0;
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
