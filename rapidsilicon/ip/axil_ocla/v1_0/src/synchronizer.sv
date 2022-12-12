//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer:
//
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: OCLA Controller
// Module Name: OCLA Controller
// Project Name: OCLA IP Core Development
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

module synchronizer #(
    parameter SYNC_STAGES   = 2,
    parameter ADDRSIZE      = 4
)
(
    output  [ADDRSIZE:0]    wptr_reg,
    output  [ADDRSIZE:0]    rptr_reg,
    input                   wr_clk,
    input                   rd_clk,
    input                   wr_rstn,
    input                   rd_rstn,
    input   [ADDRSIZE:0]    wptr,
    input   [ADDRSIZE:0]    rptr

);
    
    reg [ADDRSIZE:0] wr_sync_register[0:SYNC_STAGES-1];
    reg [ADDRSIZE:0] rd_sync_register[0:SYNC_STAGES-1];


    assign wptr_reg = wr_sync_register[SYNC_STAGES-1];
    assign rptr_reg = rd_sync_register[SYNC_STAGES-1];

    always @(posedge rd_clk or negedge rd_rstn) begin
        if (!rd_rstn) begin
            wr_sync_register[0] <= 0;
        end
        else begin
            wr_sync_register[0] <= wptr;
        end   
    end

    always @(posedge wr_clk or negedge wr_rstn) begin
        if (!wr_rstn) begin
            rd_sync_register[0] <= 0;
        end
        else begin
            rd_sync_register[0] <= rptr;
        end
        
    end
    
    genvar i;

    generate
        for(i=0; i<(SYNC_STAGES-1); i = i+1)begin
            always@(posedge rd_clk or negedge rd_rstn) begin
                if(!rd_rstn) begin
                    wr_sync_register[i+1] <= 0;
                
                end
                else begin
                    wr_sync_register[i+1] <= wr_sync_register[i];
                end
            end     
            always @(posedge wr_clk or negedge wr_rstn) begin
                if (!wr_rstn) begin
                    rd_sync_register[i+1] <= 0;
                end
                else begin
                    rd_sync_register[i+1] <= rd_sync_register[i];
                end    
            end
        end
    endgenerate

endmodule