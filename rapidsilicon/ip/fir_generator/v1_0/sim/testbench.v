`timescale 1ns/1ps

module tb;

parameter INPUT_WIDTH = 18;
parameter NUMBER_TAPS = 4;
reg clk, rst, accelerated_clk; reg [INPUT_WIDTH - 1:0] din; wire [37:0] dout, dout_golden; 
wire ready; integer i = 0, j=0, k=0, mismatch = 0; 

reg signed [INPUT_WIDTH - 1:0] dout_mem [NUMBER_TAPS - 1: 0];
reg signed [INPUT_WIDTH - 1:0] dout_golden_mem [NUMBER_TAPS - 1: 0];

initial begin
    clk = 1'b1;
    forever #5 clk = ~clk;
end
initial begin
    accelerated_clk = 1'b1;
    forever #5 accelerated_clk = ~accelerated_clk;
end

fir_golden #(
    .INPUT_WIDTH(INPUT_WIDTH),
    .NUMBER_TAPS(NUMBER_TAPS)
) fir_golden (
    .clk(clk),
    .rst(rst),
    .filter_in(din),
    .filter_out(dout_golden)
);

FIR_generator fir_filter(
    .clk(clk),
    .rst(rst),
    .data_in(din),
    .ready(ready),
    .data_out(dout)
);

initial begin
    din <= 0;
    for (i = 0; i < NUMBER_TAPS; i= i + 1) begin
        dout_golden_mem[i] <= 0;
        dout_mem[i] <= 0;
    end
    rst = 1'b1;
    repeat(10) @ (posedge clk);
    rst = 1'b0;
    @(posedge ready)
    fork 
        begin
            for (i = 1; i <= NUMBER_TAPS; i= i + 1) begin
                din <= i;
                repeat (1) @ (posedge clk);
            end
        end
        begin
            @(dout)
            for (j = 0; j < NUMBER_TAPS; j= j + 1) begin
                repeat (1) @ (posedge clk);
                dout_mem [j] <= dout;
            end
        end
        begin
            @(dout_golden)
            for (k = 0; k < NUMBER_TAPS; k= k + 1) begin
                repeat (1) @ (posedge clk);
                dout_golden_mem [k] <= dout_golden;
            end
        end
    join
    
    for (i = 0; i < NUMBER_TAPS; i= i + 1) begin
        repeat (1) @ (posedge clk);
        if (dout_mem [i] !== dout_golden_mem [i]) begin
            $display("DOUT mismatch. dout: %0d, dout_golden: %0d, Entry No.: %0d", dout_mem[i], dout_golden_mem[i], i);
            mismatch = mismatch + 1;
        end else begin
            $display("DOUT Matched. dout: %0d, dout_golden: %0d, Entry No.: %0d", dout_mem[i], dout_golden_mem[i], i);
        end
    end

    if (mismatch == 0) begin
        $display("\n**** All Comparison Matched ****\n**** Simulation Passed ****");
    end else begin
        $display("%0d comparison(s) mismatched\nERROR: SIM: Simulation Failed", mismatch);
    end
    #500;
    $finish;
end

initial begin
    $dumpfile("fir.vcd");
    $dumpvars;
end
endmodule