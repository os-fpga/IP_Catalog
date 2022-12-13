
//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer: Zafar Ali
// 
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: OCLA -  
// Module Name: sampler_buffer 
// Project Name: On-Chip Logic Analyzer Soft IP Development
// Target Devices: GEMINI 
// Tool Versions: --
// Description: 
//            This module provides buffer stages for the probe 
//            data before it is stored in the memory ( OCLA FIFO MEMORY )
// Dependencies:  
//   none   
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

/* verilator lint_off DECLFILENAME */

module sampler_buffer #(
  parameter PROBE_DATA_WIDTH = 32,
  parameter BUFFERS =  4
)(
    input logic sample_clk,
    input logic rstn,
    input logic [PROBE_DATA_WIDTH-1:0] probes,
    input logic sampling_en,
    output logic data_wen,
    output logic [PROBE_DATA_WIDTH-1:0] data_accumulate

);

  logic [PROBE_DATA_WIDTH-1:0] sync_register[0:BUFFERS-1];


  assign data_accumulate = sync_register[BUFFERS-1];
  //assign data_wen = sync_register[`BUFFER_STAGES-1][NO_OF_PROBES];
  assign data_wen = sampling_en;
  // first buffer register
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      sync_register[0] <= 'b0;
    end else begin
      //  sync_register[0] <= {sampling_en, probes};
      sync_register[0] <= probes;
    end

  end

  // buffer registers stages
  genvar b;
  generate
    for (b = 0; b < (BUFFERS - 1); b = b + 1) begin
      always @(posedge sample_clk or negedge rstn) begin
        if (!rstn) begin
          sync_register[b+1] <= 0;
        end else begin
          sync_register[b+1] <= sync_register[b];
        end
      end
    end
  endgenerate

endmodule
