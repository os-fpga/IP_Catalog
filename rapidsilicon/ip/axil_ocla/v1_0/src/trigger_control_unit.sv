//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/02/2022 11:00:52 AM
// Design Name: 
// Module Name: Trigger Control Unit
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
/* verilator lint_off DECLFILENAME */


 `include "defines.sv"

module trigger_control_unit #(
  parameter NPROBES = `NUM_OF_PROBES,
  parameter PROBE_WIDHT = `PROBE_WIDHT_BITS,
  parameter TRIGGER_INPUTS = `NUM_OF_TRIGGER_INPUTS ) (
    input logic sample_clk,
    input logic rstn,
`ifdef TRIGGER_INPUTS
    input logic [(TRIGGER_INPUTS + NPROBES)-1:0] in_signals,
`else
    input logic [(NPROBES)-1:0] in_signals,
`endif
    input logic [31:0] config_bits,
    `ifdef value_compare_trigger

    input logic [PROBE_WIDHT-1:0] reg_value,
    `endif
    output logic trigger_event

);

  logic out_trig1;

  logic in_sig1;
  `ifdef value_compare_trigger

  logic [PROBE_WIDHT-1:0] compare_value1;
`endif
  logic [31:0] config_bits_ff;
  logic [`TRIGGER_SIGNAL_SELECT_RANGE-1:0] trigger_select;
  assign trigger_select = in_signals[`TRIGGER_SIGNAL_SELECT_RANGE-1:0];

  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      config_bits_ff <= 'b0;
    end else begin
      config_bits_ff <= config_bits;
    end
  end

  //assign compare_value1 = in_signals[config_bits_ff[17+:`SELECT_MUX_WIDTH]+:`WIDTH];
  //assign in_sig1 = in_signals[config_bits_ff[17+:`SELECT_MUX_WIDTH]];

`ifdef value_compare_trigger
  assign compare_value1 = trigger_select[config_bits_ff[17+:`SELECT_MUX_WIDTH]+:PROBE_WIDHT];
`endif
 assign in_sig1 = trigger_select[config_bits_ff[17+:`SELECT_MUX_WIDTH]];

  trigger_unit #(.PROBE_WIDHT(PROBE_WIDHT)) trig_unit_a_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .in_sig(in_sig1),
      .config_bits(config_bits_ff[7:1]),
      `ifdef value_compare_trigger
      .reg_value(reg_value),
      .compare_value(compare_value1),
      `endif
      .trigger_event(out_trig1)
  );

`ifdef ADVANCE_TRIGGER

  logic out_trig2;
  logic in_sig2;
  logic out_trig_bool;
  `ifdef value_compare_trigger

  logic [PROBE_WIDHT-1:0] compare_value2;
`endif
  //  assign in_sig2 = in_signals[config_bits_ff[24+:`SELECT_MUX_WIDTH]];
  //  assign compare_value2 = in_signals[config_bits_ff[24+:`SELECT_MUX_WIDTH]+:`WIDTH];
  assign in_sig2 = trigger_select[config_bits_ff[24+:`SELECT_MUX_WIDTH]];
`ifdef value_compare_trigger
  assign compare_value2 = trigger_select[config_bits_ff[24+:`SELECT_MUX_WIDTH]+:PROBE_WIDHT];
`endif

  trigger_unit #(.PROBE_WIDHT(PROBE_WIDHT))
  trig_unit_b_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .in_sig(in_sig2),
      .config_bits(config_bits_ff[14:8]),
      `ifdef value_compare_trigger
      .reg_value(reg_value),
      .compare_value(compare_value2),
      `endif
      .trigger_event(out_trig2)
  );

  boolean_comparator bool_comp (
      .in_sig1(out_trig1),
      .in_sig2(out_trig2),
      .config_bits(config_bits_ff[16:15]),
      .trigger_event(out_trig_bool)
  );

  assign trigger_event = config_bits_ff[0] ? out_trig_bool : out_trig1;
`else
  assign trigger_event = out_trig1;

`endif

endmodule



module boolean_comparator (

    input logic in_sig1,
    input logic in_sig2,
    input logic [1:0] config_bits,
    output logic trigger_event
);

  logic in_sig_ff;
  logic out_sig;

  assign trigger_event = out_sig;

  always_comb begin
    case (config_bits)
      2'b00:   out_sig = in_sig1 | in_sig2;  // or
      2'b01:   out_sig = in_sig1 & in_sig2;  // and
      2'b10:   out_sig = in_sig1 | in_sig2;  // or
      2'b11:   out_sig = in_sig1 ^ in_sig2;  // xor
      default: out_sig = 1'b0;  // default
    endcase
  end

endmodule
