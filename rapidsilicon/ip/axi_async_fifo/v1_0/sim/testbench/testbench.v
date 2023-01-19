`timescale 1ns/1ps 

module Tb;
    reg   clock_1;
    reg   clock_2;
    reg   reset;
    initial begin
        reset = 1'b1;
        clock_1 = 1'b0;
        clock_2 = 1'b0;
        #5;
        reset = 1'b0;
    end
    always  #(2.5)     clock_1 = !clock_1;
    always  #(5)     clock_2 = !clock_2;

        initial begin
            $dumpfile("tb.vcd");
            $dumpvars;
            #40000;
            $display("Finish called from testbench");
            $finish;
        end
    vex_soc soc(.clock_1(clock_1),
                .clock_2(clock_2),
                .reset(reset));
endmodule
