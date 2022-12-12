//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer:
//
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: OCLA Top
// Module Name:
// Project Name:
// Target Devices: Gemini RS-75
// Tool Versions: Raptor
// Description:
// TBA
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////

/* verilator lint_off DECLFILENAME */


module dual_port_ram #(
    parameter DATASIZE = 32,
    parameter ADDRSIZE = 8,
    parameter DEPTH = 256
)
(
     output reg [DATASIZE-1:0]  rdata,
     input                  wr_clk,
     input                  rd_clk,
     input                  wen,
     input                  ren,
     input  [DATASIZE-1:0]  wdata,
     input  [ADDRSIZE-1:0]  waddr,
     input  [ADDRSIZE-1:0]  raddr
);
    reg [DATASIZE-1:0] mem [0:DEPTH-1];
    
    always @(posedge rd_clk) begin
        if (ren) begin
            rdata   <= mem[raddr];
        end
    end

    always @(posedge wr_clk) begin
        if (wen) begin
            mem[waddr]  <=  wdata;
        end
    end
endmodule