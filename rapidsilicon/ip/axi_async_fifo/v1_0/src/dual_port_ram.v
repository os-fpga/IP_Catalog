module dual_port_ram #(
    parameter DATASIZE = 32,
    parameter ADDRSIZE = 4
)
(
     output reg [DATASIZE-1:0]  rdata,
     input                      wr_clk,
     input                      rd_clk,
     input                      wen,
     input                      ren,
     input  [DATASIZE-1:0]      wdata,
     input  [ADDRSIZE:0]        waddr,
     input  [ADDRSIZE:0]        raddr
);
    localparam DEPTH = 2**(ADDRSIZE);
    reg [DATASIZE-1:0] mem	[(1<<ADDRSIZE)-1:0];

 
    always @(posedge rd_clk) begin
        if (ren) begin
            rdata   <= mem[raddr[ADDRSIZE-1:0]];
       end
    end

    always @(posedge wr_clk) begin
        if (wen) 
            mem[waddr[ADDRSIZE-1:0]]  <=  wdata;
    end
endmodule
