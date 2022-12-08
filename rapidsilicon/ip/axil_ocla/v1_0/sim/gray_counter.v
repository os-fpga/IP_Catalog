
/* verilator lint_off WIDTHCONCAT */
// `include "defines.sv"
`define NUM_OF_PROBES 32                                 // number of probes

module gray_counter #(parameter NUM_OF_PROBES1 = `NUM_OF_PROBES)
 (
    input sample_clk,
    input rstn,
    output reg [NUM_OF_PROBES1-1:0] gray_out,
    output wire [NUM_OF_PROBES1-1:0] binary_out
);

  reg [NUM_OF_PROBES1-1:0] q;

  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      q <= 0;
      gray_out <= 0;
    end else begin
      q <= q + 1;

      gray_out <= {q[NUM_OF_PROBES1-1], q[NUM_OF_PROBES1-1:1] ^ q[NUM_OF_PROBES1-2:0]};
    end
  end
  assign binary_out =  {2'b10,32'h11abcdef,{8{q[3:0]}}};
  // assign binary_out = {'b0,q[3:0],q[3:0],q[3:0],q[3:0],q[3:0],q[3:0],q[3:0]};
endmodule
