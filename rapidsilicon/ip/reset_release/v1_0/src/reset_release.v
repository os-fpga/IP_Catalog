/*

Copyright (c) 2022 Rapid Silicon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

*/

// Language: Verilog 2001

`timescale 1ns / 1ps

/*
 * Processor system reset IP
 */

module reset_release #
(
    parameter IP_TYPE 		        = "RST_RLSE",
	parameter IP_VERSION 	        = 32'h1, 
	parameter IP_ID 		        = 32'h2e91209,

    parameter EXT_RESET_WIDTH       = 5,
    parameter PERIPHERAL_ARESETN    = 1,
    parameter INTERCONNECTS         = 1,
    parameter BUS_RESET             = 1,
    parameter PERIPHERAL_RESET      = 1
) (

    input                           slow_clk,
    input                           ext_rst,
    input                           cpu_dbg_rst,
    input                           pll_lock,

    output reg                             cpu_rst,
    output reg [PERIPHERAL_ARESETN-1:0]    periph_aresetn,
    output reg [INTERCONNECTS-1:0]         interconnect_aresetn,
    output reg [BUS_RESET-1:0]        bus_reset,
    output reg [PERIPHERAL_RESET-1:0]      periph_reset);
    

reg [4:0] count = 0;
reg [10:0] count_16 = 0;

always @(posedge slow_clk)
begin
    count = count +1;
    count_16 = count_16 +1;


// No lock asserted
    if (!pll_lock) begin
        cpu_rst                  <= 1'b0;
        periph_aresetn          <= {PERIPHERAL_ARESETN{1'b1}};
        interconnect_aresetn    <= {INTERCONNECTS{1'b1}};
        bus_reset               <= {BUS_RESET{1'b0}};
        periph_reset            <= {PERIPHERAL_RESET{1'b0}};
    end

// Reset sequence starts after ext_rst and lock asserted
    if (!ext_rst && count== EXT_RESET_WIDTH && pll_lock) begin
        cpu_rst                 <= 1'b1;
        periph_aresetn          <= {PERIPHERAL_ARESETN{1'b0}};
        interconnect_aresetn    <= {INTERCONNECTS{1'b0}};
        bus_reset               <= {BUS_RESET{1'b1}};
        periph_reset            <= {PERIPHERAL_RESET{1'b1}};
        count_16 = 0;
    end

    if(count_16 == 16 && pll_lock) begin
        interconnect_aresetn    <= {INTERCONNECTS{1'b1}};
        bus_reset               <= {BUS_RESET{1'b0}};
    end

    if(count_16 == 32 && pll_lock) begin
        periph_aresetn          <= {PERIPHERAL_ARESETN{1'b1}};
        periph_reset            <= {PERIPHERAL_RESET{1'b0}};
    end

    if(ext_rst && count_16 == 48) begin
        cpu_rst                  <= 1'b0;
    end


    if(ext_rst || !pll_lock)
    begin
        count = 1'b0;
    end

end

endmodule