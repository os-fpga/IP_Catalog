module Idly_Cntrl #(
    parameter NUM_DLY = 5
) (
    input wire CLK_IN,
    input wire RESET,
    input wire [1:0] CMD_INCDEC,  // increment/decrement command
    input wire [$clog2(NUM_DLY)-1:0] SEL_DLY,  // delay selection
    input wire [(6*NUM_DLY)-1:0] DLY_TAP_VALUE_IN,  // tap delay values coming from IDELAY
    output wire [NUM_DLY-1:0] DLY_LOAD,  // dly load signal for DLY_ADDR_CNTRL
    output wire [NUM_DLY-1:0] DLY_ADJ,  // dly adjust signal for DLY_ADDR_CNTRL
    output wire [NUM_DLY-1:0] DLY_INCDEC,  // dly incremet/decrement signal for DLY_ADDR_CNTRL
    output wire [(6*NUM_DLY)-1:0] DLY_TAP_VALUE,  // delay tap value to delay_controller
    output reg LOAD_DONE = 1'b0  // goes high when IDELAYs are initilaized
);

  // State names
  localparam LOAD = 1'b0;
  localparam INCDEC = 1'b1;

  // Signals
  reg                     state = 'd0;
  reg                     dly_adj_i = 'd0;
  reg                     dly_indec_i = 'd0;
  reg [      NUM_DLY-1:0] dly_ld = 'd0;
  reg [      NUM_DLY-1:0] dly_adj = 'd0;
  reg [      NUM_DLY-1:0] dly_incdec = 'd0;
  reg [$clog2(NUM_DLY):0] count = 'd0;

  // increment/ decrement command generation
  always @(*) begin
    case (CMD_INCDEC)
      2'b01: begin
        dly_indec_i <= 1'b1;  // increment
        dly_adj_i   <= 1'b1;
      end
      2'b10: begin
        dly_indec_i <= 1'b0;  // decrement
        dly_adj_i   <= 1'b1;
      end
      default: begin
        dly_indec_i <= 1'b0;  // no action
        dly_adj_i   <= 1'b0;
      end
    endcase

  end

  reg [1:0] clk_count = 'd0;

  // LOAD, ADJUST and INCDEC for selected I/O_DELAY
  always @(posedge CLK_IN) begin
    dly_ld     <= 'd0;
    dly_adj    <= 'd0;
    dly_incdec <= 'd0;

    if (RESET) begin
      state <= 'd0;
      count <= 'd0;
    end else begin
      case (state)

        LOAD: begin  // Load State
          if (clk_count == 1) begin
            clk_count <= 'd0;
            count     <= count + 1;
            if (count == NUM_DLY) begin
              count <= 'd0;
              state <= 1'b1;
            end else dly_ld[count] <= 1'b1;  // first loading delay value to all I/O_DELAYs
          end else begin
            clk_count <= clk_count + 1;
            dly_ld    <= dly_ld;
          end
        end
        INCDEC: begin  // Adjust and increment/decrement State
          LOAD_DONE <= 1'b1;
          clk_count <= clk_count + 1;
          if (clk_count == 0) begin
            dly_adj[SEL_DLY]    <= dly_adj_i;
            dly_incdec[SEL_DLY] <= dly_indec_i;
          end else if (clk_count == 2 | clk_count == 3) begin
            dly_adj    <= 'd0;
            dly_incdec <= 'd0;
          end else begin
            dly_adj    <= dly_adj;
            dly_incdec <= dly_incdec;
          end
        end
        default: state <= 1'b0;
      endcase
    end
  end

  assign DLY_LOAD      = dly_ld;
  assign DLY_ADJ       = dly_adj;
  assign DLY_INCDEC    = dly_incdec;
  assign DLY_TAP_VALUE = DLY_TAP_VALUE_IN;

endmodule
