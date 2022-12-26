//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/02/2022 11:00:52 AM
// Design Name: 
// Module Name: edge_detector
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

module trigger_unit #(parameter PROBE_WIDHT = 4 ) (

    input logic sample_clk,
    input logic rstn,
    input logic in_sig,
    input logic [6:0] config_bits,
    `ifdef VALUE_COMPARE_TRIGGER
    input logic [PROBE_WIDHT-1:0] reg_value,
    input logic [PROBE_WIDHT-1:0] compare_value,
    `endif
    output logic trigger_event

);

  logic trigger_event_ed;
  `ifdef VALUE_COMPARE_TRIGGER

  logic trigger_event_vc;
  `endif
  logic trigger_event_lvl;
  logic out_sig;

  dflop dff_out_sig (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .D(out_sig),
      .Q(trigger_event)
  );

  always_comb begin
    case (config_bits[1:0])
      2'b00:   out_sig = 1'b0;  // no trigger
      2'b01:   out_sig = trigger_event_ed;  //  edge detect
      2'b10:   out_sig = trigger_event_lvl;  // level detect
      `ifdef VALUE_COMPARE_TRIGGER
      2'b11:   out_sig = trigger_event_vc;  // value compare
      `endif
      default: out_sig = 1'b0;  // default
    endcase
  end

  edge_detector ed (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .en(config_bits[1:0] == 2'b01),
      .in_sig(in_sig),
      .config_bits(config_bits[3:2]),
      .edge_trigger_event(trigger_event_ed)
  );
  level_detect lvld (
      .sample_clk(sample_clk),

      .rstn(rstn),
      .in_sig(in_sig),
      .en(config_bits[1:0] == 2'b10),
      .config_bits(config_bits[4]),
      .lvl_trigger_event(trigger_event_lvl)
  );
  `ifdef VALUE_COMPARE_TRIGGER
  value_compare #(.PROBE_WIDHT(PROBE_WIDHT))
  vc (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .en(config_bits[1:0] == 2'b11),
      .in_sig(compare_value),
      .reg_value(reg_value),
      .config_bits(config_bits[6:5]),
      .vc_trigger_event(trigger_event_vc)
  );

  `endif

endmodule

module edge_detector (
    input logic sample_clk,
    input logic rstn,
    input logic en,
    input logic in_sig,
    input logic [1:0] config_bits,
    output logic edge_trigger_event
);

  logic in_sig_ff;
  logic out_sig;

  dflop dff_in_sig (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .D(in_sig),
      .Q(in_sig_ff)
  );
  dflop dff_out_sig (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .D(out_sig),
      .Q(edge_trigger_event)
  );

  always_comb begin
    if (en) begin
      case (config_bits)
        2'b00:   out_sig = 1'b0;  // no trigger
        2'b01:   out_sig = in_sig & !(in_sig_ff);  // rising edge detect
        2'b10:   out_sig = !(in_sig) & in_sig_ff;  // falling edge detect
        2'b11:   out_sig = in_sig ^ in_sig_ff;  // either edge detec
        default: out_sig = 1'b0;  // default
      endcase
    end else out_sig = 1'b0;
  end

endmodule



module value_compare #(parameter PROBE_WIDHT = 4 ) (
    input logic sample_clk,
    input logic rstn,
    input logic en,
    input logic [PROBE_WIDHT-1:0] in_sig,
    input logic [PROBE_WIDHT-1:0] reg_value,
    input logic [1:0] config_bits,
    output logic vc_trigger_event
);

  logic out_sig;

  // dflop dff_out_sig (.sample_clk(sample_clk),.rstn(rstn),.D(out_sig),.Q(vc_trigger_event));

  always_comb begin
    if (en) begin
      case (config_bits)
        2'b00:   out_sig = 1'b0;  // no trigger
        2'b01:   out_sig = reg_value == in_sig;  // equal to detect
        2'b10:   out_sig = in_sig < reg_value;  // less than detect
        2'b11:   out_sig = in_sig > reg_value;  // greater than detect
        default: out_sig = 1'b0;  // default
      endcase
    end else out_sig = 1'b0;

  end

  lvl2pulse level2pulse (
    .sample_clk(sample_clk),
    .rstn(rstn),
    .in_sig (out_sig),
    .out_sig(vc_trigger_event)
);

endmodule

module level_detect (
    input  logic sample_clk,
    input  logic rstn,
    input  logic en,
    input  logic in_sig,
    input  logic config_bits,
    output logic lvl_trigger_event
);

  logic in_sig_ff;
  logic out_sig;

  //dflop dff_out_sig (.sample_clk(sample_clk),.rstn(rstn),.D(out_sig),.Q(trigger_event));
  always_comb begin
    if (en) begin
      case (config_bits)
        1'b0:    out_sig = !in_sig;  // low level
        1'b1:    out_sig = in_sig;  // high level
        default: out_sig = 1'b0;  // default
      endcase
    end 
    else out_sig = 1'b0;
  end

  lvl2pulse level2pulse (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .in_sig (out_sig),
      .out_sig(lvl_trigger_event)
  );
endmodule


module dflop(
    input  logic sample_clk,
    input  logic rstn,
    input  logic D,
    output logic Q
);

  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) Q <= 1'b0;
    else Q <= D;
  end
endmodule

module lvl2pulse (
    input  logic sample_clk,
    input logic rstn,
    input  logic in_sig,
    output logic out_sig
);
  logic r1, r2, r3;

  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      r1 <= 1'b0;
      r2 <= 1'b0;
      r3 <= 1'b0;
      
    end
    else begin
    r1 <= in_sig;  // first reg in synchronizer
    r2 <= r1;  // second reg in synchronizer, output is in sync!
    r3 <= r2;  // remembers previous state of button
    end
  end
  // rising edge = old value is 0, new value is 1
  assign out_sig = ~r3 & r2;
endmodule
