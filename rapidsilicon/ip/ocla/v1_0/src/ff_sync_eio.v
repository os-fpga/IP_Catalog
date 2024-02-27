`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/04/2022 12:58:01 PM
// Design Name: 
// Module Name: ff_sync
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module ff_sync_eio #
               (
               parameter DATA_SIZE = 1,
               parameter SYNC      = 1 
               )
               (
                input                     destination_clk,
                input                     destination_rstn,
                input   [DATA_SIZE-1 : 0] async_data_in,
                output  [DATA_SIZE-1 : 0] sync_data_out
               );
    
    reg [DATA_SIZE-1 : 0] stage2_ff;
    reg [DATA_SIZE-1 : 0] stage1_ff;
    
    generate 
        if (SYNC)
        begin
            // generate the sync flops
            always @ (posedge destination_clk or negedge destination_rstn)
            begin
                if(!destination_rstn)
                    {stage2_ff, stage1_ff} <= {{DATA_SIZE{1'b0}}, {DATA_SIZE{1'b0}}};
                else
                    {stage2_ff, stage1_ff} <= {stage1_ff, async_data_in};
            end
            
            // assignment of output stage
            assign sync_data_out = stage2_ff;
        end
        else
        begin
            assign sync_data_out = async_data_in;
        end
    endgenerate    
    
endmodule