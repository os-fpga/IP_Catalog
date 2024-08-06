module Tb;
    reg   clock;
    reg   pll_lock;
    reg   reset;



  initial begin

//  Reset sequence asserted after 5 cycle ext_rst_in window
        reset = 1'b1;
        pll_lock = 1'b0;
        clock = 1'b0;
        #50;
        reset = 1'b0; 
        #50;
        pll_lock = 1'b1;
        reset = 1'b0; 
        clock = 1'b0;
        #35;
        reset = 1'b1;
        #300;

// Reset sequence asserted in middle of a sequence
        reset = 1'b1;
        pll_lock = 1'b0;
        clock = 1'b0;
        #100;
        reset = 1'b0; 
        pll_lock = 1'b1;
        reset = 1'b0; 
        clock = 1'b0;
        #35;
        reset = 1'b1;
        #60;
        pll_lock = 1'b1;
        
//  Repeat sequence
        reset=1'b0;
        #35;
        reset = 1'b1;

        #1000;
        pll_lock = 1'b0;

        #100;
        pll_lock = 1'b1;
        reset = 1'b0; 
        clock = 1'b0;
        #35
        reset = 1'b1;
        #100;
        pll_lock = 1'b1;


    end
    always  #(2.5)     clock = !clock;

    initial begin
        $dumpfile("reset.vcd");
        $dumpvars;
    end

    initial begin
        #5000;
        $display("\n**** Simulation Passed ****");
        $finish;
    end


    reset_release dut (.slow_clk(clock),
                    .pll_lock(pll_lock),
                    .ext_rst(reset),
                    .cpu_rst(cpu_rst),
                    .periph_aresetn(periph_aresetn),
                    .interconnect_aresetn(interconnect_aresetn),
                    .bus_reset(bus_reset),
                    .periph_reset(periph_reset));
endmodule