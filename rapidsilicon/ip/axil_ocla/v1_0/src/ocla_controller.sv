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

/* verilator lint_off WIDTH */


module ocla_controller #(
  parameter SAMPLE_CNTER_WIDTH = 2,
  parameter MEM_DPTH_HALF = 2

) (

    input logic sample_clk,
    input logic rstn,

    input logic trigger_event,
    input logic [1:0] trigger_mode,
    input logic start_process,
    input logic fixnosamples_en,
    input logic [SAMPLE_CNTER_WIDTH-1:0] noofsamples,

    input logic mem_full,
    input logic mem_empty,

    input logic sample_again,

    output logic sampling_en,
    output logic sampling_done_ff

);

  logic [SAMPLE_CNTER_WIDTH-1:0] samples_count;

  logic triggered_occured_ff;
  logic sampling_done;


  // sampling is done and data is availale
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) sampling_done_ff <= 1'b0;
    else begin
      if (sampling_done) sampling_done_ff <= 1'b1;
      else if (sample_again | mem_empty) sampling_done_ff <= 1'b0;
    end
  end


  // handles the trigger modes 
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      sampling_en   <= 1'b0;
      samples_count <= 'b0;
    end else begin
      if (!start_process | sample_again) begin
        sampling_en   <= 1'b0;
        samples_count <= 'b0;
      end else begin
        case (trigger_mode)
          2'b00: begin  // countinous
            if (fixnosamples_en) begin
              samples_count <= samples_count + 1'b1;
            end
            sampling_en <= !sampling_done_ff & !sampling_done;

          end

          2'b01: begin  // pre trigger
            if ((trigger_event | triggered_occured_ff) & !sampling_done) begin
              sampling_en <= !sampling_done_ff & !sampling_done;
              if (fixnosamples_en) begin
                samples_count <= samples_count + 1'b1;
              end else begin
                samples_count <= 'b0;
              end
            end else begin
              sampling_en <= 1'b0;
            end
          end
          2'b10: begin  // post trigger
            if (trigger_event) begin
              sampling_en <= 1'b0;
            end else begin
              sampling_en <= !sampling_done_ff & !sampling_done;
            end
          end
          2'b11: begin  // center trigger
            if (trigger_event | triggered_occured_ff) begin
              sampling_en   <= !sampling_done_ff & !sampling_done;
              samples_count <= samples_count + 1'b1;
            end else begin
              sampling_en   <= !sampling_done_ff & !sampling_done;
              samples_count <= 'b0;
            end
          end

          default: begin  // default
            sampling_en   <= 1'b0;
            samples_count <= 'b0;
          end

        endcase
      end
    end
  end


  // to generate sampling done signal
  always_comb begin
    case (trigger_mode)
      2'b00: begin
        if (mem_full | fixnosamples_en?samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]:1'b0 ) begin
          sampling_done = 1'b1;
        end else begin
          sampling_done = 1'b0;
        end
      end
      2'b01: begin
        if (mem_full | fixnosamples_en?samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]:1'b0)
          sampling_done = 1'b1;
        else sampling_done = 1'b0;
      end
      2'b10: begin
        if (trigger_event) sampling_done = 1'b1;
        else begin
          sampling_done = 1'b0;
        end
      end
      2'b11: begin
        if (fixnosamples_en) begin
          if (samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]) sampling_done = 1'b1;
          else sampling_done = 1'b0;
        end else begin
          if (samples_count == MEM_DPTH_HALF) sampling_done = 1'b1;
          else sampling_done = 1'b0;
        end
      end
      default: sampling_done = 1'b0;
    endcase
  end

  // flopped trigger event pulse
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) triggered_occured_ff <= 1'b0;
    else begin
      if (!start_process | sample_again | sampling_done_ff) triggered_occured_ff <= 1'b0;
      else if (trigger_event & trigger_mode != 2'b10) triggered_occured_ff <= 1'b1;
    end
  end

endmodule
