module deskew_cntrl_wrap #(

    parameter                 NUM_DLY    = 2,          // 1 to 4
    parameter                 FREQ       = 'd1000,     // 300Mhz to 2.5 Ghz
    parameter                 WIDTH      = 4,          // gearing ratio
    parameter                 SAMPLES_NO = 3,          // time to sample count  // 10 to 300
    parameter [WIDTH - 1 : 0] PATTERN    = 'b01010101  // pattern to check

) (
    input                                clk,               // clock signal
    input                                rst,               // active high rest
    input      [(NUM_DLY*WIDTH) - 1 : 0] datain,            // incoming data from serdes
    input      [    (6*NUM_DLY) - 1 : 0] dly_tap_value_in,  // dly tap value from DLY_ADDR_CNTRL
    output     [        NUM_DLY - 1 : 0] dly_ld,            // dly load signal to DLY_ADDR_CNTRL
    output     [        NUM_DLY - 1 : 0] dly_adj,           // dly adjust signal to DLY_ADDR_CNTRL
    output     [        NUM_DLY - 1 : 0] dly_incdec,        // dly incdec signal to DLY_ADDR_CNTRL
    output reg [    $clog2(NUM_DLY)-1:0] dly_sel,

    output [NUM_DLY - 1 : 0] calib_error,
    output [NUM_DLY - 1 : 0] calib_done
);


  reg  [(6*NUM_DLY) - 1 : 0] dly_tap_value_in_retain = 0;

  wire [(NUM_DLY*6) - 1 : 0] dly_tap_value;
  wire [    NUM_DLY - 1 : 0] dly_req;
  wire [    NUM_DLY - 1 : 0] dly_ack;
  reg  [     NUM_DLY -1 : 0] dly_ack_reg = 'd0;
  wire [(NUM_DLY*6) - 1 : 0] delay_value;
  wire                       dly_cmd_int;
  wire                       calib_done_int;
  reg                        check_dly;
  wire                       start;



  reg  [    NUM_DLY - 1 : 0] dly_req_reg = 0;
  reg  [                2:0] timer = 0;


  reg  [                1:0] dly_cmd;
  reg [3:0] state_reg, state_next;
  reg [$clog2(NUM_DLY):0] dly_num_cnt;
  reg incdec = 0;

  localparam IDLE = 4'd0;
  localparam PROCESS = 4'd1;
  localparam CHECK_DLY = 4'd2;
  localparam INC_DLY = 4'd3;
  localparam DEC_DLY = 4'd4;
  localparam WAIT1 = 4'd5;
  localparam WAIT2 = 4'd6;
  localparam STOP = 4'd7;

  // delay_controller instances
  generate
    genvar m, n;

    for (m = 0; m < NUM_DLY; m = m + 1) begin


      deskew_cntrl #(
          .FREQ(FREQ),
          .WIDTH(WIDTH),
          .SAMPLES_NO(SAMPLES_NO),
          .PATTERN(PATTERN)
      ) deskew_cntrl_inst (
          .clk(clk),
          .rst(rst),
          .start(start),
          .datain(datain[m*WIDTH+:WIDTH]),
          .dly_tap_value(dly_tap_value[m*6+:6]),
          .dly_ack(dly_ack[m]),
          .dly_req(dly_req[m]),
          .calib_error(calib_error[m]),
          .calib_done(calib_done[m]),
          .delay_value(delay_value[m*6+:6])
      );

      assign dly_ack[m] = (dly_req[m] == 1'b1) ? dly_ack_reg[m] : 1'b0;

      always @(dly_tap_value_in) begin
        if (dly_tap_value_in[m*6+:6] == 0) begin
          dly_tap_value_in_retain[m*6+:6] = dly_tap_value_in_retain[m*6+:6];
        end else dly_tap_value_in_retain[m*6+:6] = dly_tap_value_in[m*6+:6];
      end
    end
  endgenerate


  Idly_Cntrl #(
      .NUM_DLY(NUM_DLY)
  ) Idly_Cntrl_inst (
      .CLK_IN(clk),
      .RESET(rst),
      .CMD_INCDEC(dly_cmd),
      .SEL_DLY(dly_sel),
      .DLY_TAP_VALUE_IN(dly_tap_value_in_retain),
      .DLY_LOAD(dly_ld),
      .DLY_ADJ(dly_adj),
      .DLY_INCDEC(dly_incdec),
      .DLY_TAP_VALUE(dly_tap_value),
      .LOAD_DONE(start)
  );



  assign dly_cmd_int = |dly_req_reg;  // check increment request for any IDELAY
  assign calib_done_int = &calib_done;  // check delay value is computed for all IDELAY

  always @(posedge clk) begin
    dly_req_reg <= dly_req;
    if (state_next == WAIT2 || state_next == CHECK_DLY) dly_num_cnt <= dly_num_cnt + 1;
    else if (state_next == WAIT1 || state_next == PROCESS || state_next == INC_DLY || state_next == DEC_DLY)
      dly_num_cnt <= dly_num_cnt;
    else dly_num_cnt <= 0;
  end


  always @(posedge clk) begin
    if (rst) begin
      state_reg <= IDLE;

    end else begin
      state_reg <= state_next;

      if (state_next == WAIT1) timer <= timer + 1;
      else timer <= 0;

    end
  end

  always @(*) begin
    case (state_reg)

      IDLE: begin
        check_dly = 0;
        if (dly_cmd_int) state_next = PROCESS;
        else if (calib_done_int) begin
          state_next = CHECK_DLY;
        end else begin
          state_next = IDLE;
        end
      end

      PROCESS: begin
        check_dly = 1;
        if (dly_num_cnt != (NUM_DLY)) begin
          // state_next = PROCESS;
          if (dly_req_reg[dly_num_cnt] == 1) begin
            dly_sel = dly_num_cnt;
            dly_cmd = 2'd1;
            dly_ack_reg[dly_num_cnt] = 1'b1;
            state_next = WAIT1;

          end else begin
            dly_sel = 0;
            dly_cmd = 2'd0;
            dly_ack_reg[dly_num_cnt] = 1'b0;
            state_next = WAIT1;

          end
        end else begin
          state_next = IDLE;
          dly_sel = 0;
          dly_cmd = 2'd0;
        end
      end

      WAIT1: begin
        check_dly = 0;
        if (timer == 4) state_next = WAIT2;
        else state_next = WAIT1;

      end
      WAIT2: begin
        if (calib_done && incdec) begin
          state_next = INC_DLY;
        end else if (calib_done && ~incdec) begin
          state_next = DEC_DLY;
        end
        state_next = PROCESS;

      end

      CHECK_DLY: begin
        if (dly_num_cnt == (NUM_DLY)) begin
          state_next = STOP;
        end else begin
          if (dly_tap_value[dly_num_cnt*6+:6] < delay_value[dly_num_cnt*6+:6]) begin
            state_next = INC_DLY;
          end else if (dly_tap_value[dly_num_cnt*6+:6] > delay_value[dly_num_cnt*6+:6]) begin /// Add one more condition for equality.
            state_next = DEC_DLY;
          end else if (dly_tap_value[dly_num_cnt*6+:6] == delay_value[dly_num_cnt*6+:6]) begin
            state_next = INC_DLY;
          end else state_next = CHECK_DLY;
        end
      end

      INC_DLY: begin
        if (dly_tap_value[dly_num_cnt*6+:6] < delay_value[dly_num_cnt*6+:6]) begin
          state_next = WAIT1;
          dly_sel = dly_num_cnt;
          dly_cmd = 2'd1;
          incdec = 1'b1;
        end else begin
          state_next = CHECK_DLY;
          dly_sel = dly_num_cnt;
          dly_cmd = 2'd0;
        end
      end

      DEC_DLY: begin
        if (dly_tap_value[dly_num_cnt*6+:6] > delay_value[dly_num_cnt*6+:6]) begin
          state_next = WAIT1;
          dly_sel = dly_num_cnt;
          dly_cmd = 2'd2;
          incdec = 0;
        end else begin
          state_next = CHECK_DLY;
          dly_sel = dly_num_cnt;
          dly_cmd = 2'd0;
        end

      end

      STOP: begin
        state_next = STOP;
      end
    endcase
  end
endmodule
