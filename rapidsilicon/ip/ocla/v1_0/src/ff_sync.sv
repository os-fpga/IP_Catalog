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


module ff_sync(
               input      destination_clk,
               input      destination_rstn,
               input      async_data_in,
               output reg sync_data_out
              );
    
    reg stage1_ff;
    
    always @ (posedge destination_clk or negedge destination_rstn)
    begin
        if(!destination_rstn)
        begin
            {sync_data_out, stage1_ff} <= {1'b0, 1'b0};
        end
        else
        begin
            {sync_data_out, stage1_ff} <= {stage1_ff, async_data_in};
        end
    end
    
endmodule