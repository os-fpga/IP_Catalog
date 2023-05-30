`timescale 1ns / 1ps

module fifo_test();
reg   [35:0] WR_DATA;
reg RDEN;
reg WREN;
reg RESET;

wire   [35:0] RD_DATA;
wire EMPTY;
wire FULL;
wire OVERFLOW;
wire UNDERFLOW;
wire ALMOST_EMPTY;
wire ALMOST_FULL;
wire PROG_FULL;
wire PROG_EMPTY;

reg WRCLK;
reg RDCLK;

integer mismatch=0;
reg [6:0]cycle;

FIFO wrapper(.*, .RD_DATA(RD_DATA));

always #(10)   
WRCLK = !WRCLK;

integer i, j;
initial begin
    {WRCLK,  WR_DATA, RDEN, WREN ,RESET, cycle, i} = 0;
    RDCLK =1;
    RESET = 1;
    #10;
    RESET = 0;
    repeat (10) @(posedge WRCLK);

    for (i=0; i<1030; i=i+1)begin
        repeat (1) @ (posedge WRCLK)
        WREN <=1; RDEN<=0; WR_DATA<= $random;
        cycle = cycle +1;
    end

    RESET = 1;
    #10;
    RESET = 0;

    for (i=0; i<1024; i=i+1)begin
        repeat (1) @ (posedge WRCLK)
        WREN <=1; RDEN<=0; WR_DATA<= $random;
        cycle = cycle +1;
    end
    
    WREN <=0;
    repeat (10) @(posedge WRCLK);
    
    for (j=0; j<1024; j=j+1)begin
        repeat (1) @ (posedge WRCLK)
        WREN <=0; RDEN<=1; 
        cycle = cycle +1;
    end
    
    repeat (10) @(posedge WRCLK); 
    $finish;
    end

initial begin
    $dumpfile("tb.vcd");
    $dumpvars;
end
endmodule