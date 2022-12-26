module dual_port_ram #(
    /* Define width of memory */
    parameter DATASIZE = 32,
    /* Define depth of memory */
    parameter ADDRSIZE = 4,
    /* For BRAM set MEM_TYPE=1, while for Distributed memory set MEM_TYPE=0 */
    parameter MEM_TYPE = 0
)
(
    output reg [DATASIZE-1:0]   rdata,
    input                       wr_clk,
    input                       rd_clk,
    input                       wen,
    input                       ren,
    input      [DATASIZE-1:0]   wdata,
    input      [ADDRSIZE:0]     waddr,
    input      [ADDRSIZE:0]     raddr
);
   
   /* Inferring Block memory as Dual Port RAM */
   
   generate if (MEM_TYPE) begin
        (* ram_style = "block" *) reg [DATASIZE-1:0] mem	[(1<<ADDRSIZE)-1:0];

        always @(posedge rd_clk) begin
            if (ren) begin
                rdata   <= mem[raddr[ADDRSIZE-1:0]];
            end
        end

        always @(posedge wr_clk) begin
            if (wen) 
            mem[waddr[ADDRSIZE-1:0]]  <=  wdata;
        end
    end
    /* Inferring Distributed memory */

    else begin 
        (* ram_style = "logic" *) reg [DATASIZE-1:0] mem    [(1<<ADDRSIZE)-1:0];
     
            always @(posedge rd_clk) begin
                if (ren) 
                rdata   <= mem[raddr[ADDRSIZE-1:0]];
            end
     
            always @(posedge wr_clk) begin
                if (wen) 
                mem[waddr[ADDRSIZE-1:0]]  <=  wdata;
            end
    end
    endgenerate
    
endmodule