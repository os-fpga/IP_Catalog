
//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer: Zafar Ali
// 
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: OCLA -  
// Module Name: stream_out_buffer 
// Project Name: On-Chip Logic Analyzer Soft IP Development
// Target Devices: GEMINI 
// Tool Versions: --
// Description: 
//            This module reads the sampled data from ocla memory one by one   
//            and send outs to the AXI interface in the AXI_DATA_WIDTH sized word chunks
// Dependencies:  
//   none   
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////



/* verilator lint_off WIDTHCONCAT */
/* verilator lint_off WIDTH */
/* verilator lint_off DECLFILENAME */

 
module stream_out_buffer #(
     parameter NUM_OFPROBES =2,
     parameter WORD_CHUNK_COUNTER_WIDTH =2,
     parameter NUM_OF_WORD_CHUNKS =2,     
     parameter PROBE_BITS =2,
     parameter AXI_DATA_WIDTH = 32

) (
    input logic S_AXI_ACLK,
    input logic S_AXI_ARESETN,
    input logic [NUM_OFPROBES-1:0] read_accumulated_data,
    input logic mem_empty,
    input logic read_data_en,
    input logic read_ready,
    output logic mem_read,
    output logic read_valid,

    output logic [AXI_DATA_WIDTH-1:0] read_data

);
  localparam mem_access = 1'b0;  // mem access state
  localparam data_out = 1'b1;    // data out state

  reg                            fetch_data;  // fetch data from mem
  reg                            state;       // state variable 
  reg [WORD_CHUNK_COUNTER_WIDTH:0] word_count;  //  word chunk counter 

  reg [       NUM_OFPROBES-1:0] mem_accumulated_data_reg;  // mem data hold registor
  reg                            mem_read_ff;

  // simple state machine to handle data fetch from memory and send word chunks to the axi slave interface
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
    if (!S_AXI_ARESETN) begin
      state <= mem_access;
      mem_read <= 1'b0;
      mem_read_ff <= 1'b0;
    end else begin
      mem_read_ff <= mem_read;
      case (state)
        mem_access: begin
          if (read_data_en && !mem_empty) begin
            if (mem_read) state <= data_out;
            mem_read <= ~mem_read;
          end else begin
            state <= mem_access;
            mem_read <= 1'b0;
          end
        end
        data_out: begin
          if (!read_data_en & fetch_data) begin
            state <= mem_access;
          end else begin
            state <= data_out;
          end
          mem_read <= 1'b0;

        end
        default: begin  // Fault Recovery
          state <= mem_access;
        end
      endcase
    end

  // this part handles word chunks transfer to the axi slave interface for read transactions
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (!S_AXI_ARESETN) begin
      read_data  <= 'b0;
      word_count <= 'b0;
      read_valid <= 'b0;
      fetch_data <= 'b0;
    end else begin
      if (state == data_out) begin
        if (word_count == 'b0 && !fetch_data) begin
          read_data  <= {'b0, read_accumulated_data};
          //$display("PROBE_BITS chunk %d, %d, %d", NUM_OF_WORD_CHUNKS, PROBE_BITS,`REM_BITS );
          read_valid <= 'b1;
          if (read_ready) word_count <= word_count + 'b1;
          if (word_count >= ((NUM_OF_WORD_CHUNKS) - 1)) fetch_data <= 'b1;
          else fetch_data <= 'b0;
        end else if (word_count >= ((NUM_OF_WORD_CHUNKS) - 1)) begin
          if (read_data_en && !mem_empty && !read_valid && !fetch_data) begin
            read_data  <= {'b0, mem_accumulated_data_reg[32*word_count+:PROBE_BITS]};
            read_valid <= 'b1;
            word_count <= 'b0;
            fetch_data <= 'b1;
            // $display("word chunk %d, %d", NUM_OF_WORD_CHUNKS, word_count);
          end else begin
            if (read_ready) read_valid <= 'b0;
            fetch_data <= 'b0;
          end
        end else begin
          if ((read_data_en && !mem_empty && !read_valid)) begin
            word_count <= word_count + 'b1;
            read_data  <= mem_accumulated_data_reg[32*word_count+:AXI_DATA_WIDTH];
            read_valid <= 'b1;
            fetch_data <= 'b0;
          end else begin
            if (read_ready) read_valid <= 'b0;
          end
        end
      end else begin
        word_count <= 'b0;
        if (read_ready ) read_data <= 'b0;
        read_valid <= 'b0;
        fetch_data <= 'b0;
      end
    end
  end

  // memory fetched data hold register 
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (!S_AXI_ARESETN) begin
      mem_accumulated_data_reg <= 'b0;
    end else begin
      if (mem_read_ff) mem_accumulated_data_reg <= read_accumulated_data;
      // mem_accumulated_data_reg <= 'hAAAAAA32BBBBBB31ABCDEF39ABCDEF38ABCDEF37ABCDEF36ABCDEF35ABCDEF34ABCDEF33ABCDEF32ABCDEF31ABCDEF30ABCDEF29ABCDEF28ABCDEF27ABCDEF26ABCDEF25ABCDEF24ABCDEF23ABCDEF22ABCDEF22ABCDEF20ABCDEF19ABCDEF18ABCDEF17ABCDEF16ABCDEF15ABCDEF14ABCDEF13ABCDEF12ABCDEF11ABCDEF10;
    end
  end

endmodule
