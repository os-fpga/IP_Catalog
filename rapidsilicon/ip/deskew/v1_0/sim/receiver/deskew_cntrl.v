`timescale 1ns / 1ps
//
// Module name: delay_controller.v
// Design by:   Roman Shah
// Description: This design describe deskew algorithm to center alligned the serial data with fast clock
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//



module deskew_cntrl #(

    parameter               FREQ       = 'd1000,
    parameter               WIDTH      = 4,          // gearing ratio
    parameter               SAMPLES_NO = 3,          // time to sample count
    parameter [WIDTH-1 : 0] PATTERN    = 'b01010101  // pattern to check
) (
    input              clk,            // clock signal
    input              rst,            // active high rest
    input              start,
    input  [WIDTH-1:0] datain,         // incoming data from serdes
    input  [      5:0] dly_tap_value,  // delay tap value from idelay
    input              dly_ack,
    output             dly_req,        // increment/decrement command for delay controller
    output             calib_error,
    output             calib_done,
    output [      5:0] delay_value

);
  localparam CLK_TAPS = (1000000/FREQ)/43;// converting into time period (ps) and finding center taps

  reg [WIDTH-1:0] datain_ff;
  reg capture_en;
  reg valid_pattern;
  reg initial_pattern_valid;
  reg [$clog2 (SAMPLES_NO):0] samples_count = 0;

  reg mnl_dly_mr;

  reg [5:0] tap_values0[0:5];  // array to hold delay taps
  reg [5:0] tap_values1[0:5];  // array to hold delay taps
  reg [5:0] dly_tap_cnt;  // counting delay taps

  reg [5:0] tap_values0_half[0:5];  // half time of valid window
  reg [5:0] tap_values1_half[0:5];  // half time of valid window

 /* wire [5:0] tap0;
  wire [5:0] tap1;
  wire [5:0] tap2;
  wire [5:0] tap3;
  wire [5:0] tap4;
  wire [5:0] tap5;
  wire [5:0] tap6;
  wire [5:0] tap7;

  assign tap0 = tap_values0[0];
  assign tap1 = tap_values0[1];

  assign tap2 = tap_values0_half[0];

  assign tap3 = tap_values0_half[1];

  assign tap4 = tap_values1[0];
  assign tap5 = tap_values1[1];

  assign tap6 = tap_values1_half[0];

  assign tap7 = tap_values1_half[1]; */

  reg [5:0] iteration;
  reg dly_inc_reg;  // increment delay during processing
  reg dly_inc_int;  // increment delay during processing



  reg [1:0] tap_value_cnt;  // count number of delay taps
  reg calib_error_int;
  reg calib_error_reg;

  reg calib_done_int;
  reg calib_done_reg;

  reg [5:0] delay_value_int;  // final measured delay
  reg [5:0] delay_value_reg;

  assign calib_error = calib_error_reg;
  assign dly_req = dly_inc_reg;
  assign calib_done = calib_done_reg;
  assign delay_value = delay_value_reg;


  localparam IDLE = 4'd0;
  localparam CAPTURE_SAMPLE = 4'd1;
  localparam INITIAL_CHECK = 4'd2;
  localparam PATTERN_CHECK = 4'd3;
  localparam TAP_INCREMENT = 4'd4;
  localparam CALIBRATION_ERROR = 4'd5;
  localparam LOW_FREQ = 4'd6;
  localparam HOLD_TAP_VALUE = 4'd7;
  localparam MEASURE_DELAY = 4'd8;
  localparam WAIT_STATE = 4'D9;

  reg [3:0] state_reg, state_next;

  //****************receiving incoming data************************/
  always @(posedge clk) begin
    if (capture_en) datain_ff <= datain;
    else datain_ff <= datain_ff;
  end

  //*************** total time to capture a sample****************/
  always @(posedge clk) begin
    if (state_reg == CAPTURE_SAMPLE && samples_count != SAMPLES_NO) begin
      samples_count <= samples_count + 1;
    end else begin
      samples_count <= 0;
    end
    //***************** total itteration***************************/
    if (state_reg == TAP_INCREMENT && iteration == 0) begin
      iteration <= iteration + 1;
    end else if (state_reg == HOLD_TAP_VALUE) begin
      iteration <= iteration + 1;
    end else begin
      iteration <= iteration;
    end
    //*************total counts for delay taps***********************//
    if (dly_req) begin
      dly_tap_cnt <= dly_tap_cnt + 1;
    end
  end

  always @(posedge clk) begin
    if (rst) begin
      state_reg <= IDLE;
      calib_error_reg <= 0;
      calib_done_reg <= 0;
      delay_value_reg <= 0;
      dly_inc_reg <= 0;
    end else begin
      state_reg <= state_next;
      calib_error_reg <= calib_error_int;
      calib_done_reg <= calib_done_int;
      delay_value_reg <= delay_value_int;
      dly_inc_reg <= dly_inc_int;
    end
  end

  always @(*) begin
    case (state_reg)

      IDLE: begin
        if (start) begin
          state_next = CAPTURE_SAMPLE;
          capture_en = 0;
          iteration  = 0;
          mnl_dly_mr = 0;
        end else begin
          state_next = IDLE;
        end
      end

      CAPTURE_SAMPLE: begin
        dly_inc_int = 0;
        if (samples_count == SAMPLES_NO) begin
          capture_en = 0;
          if (iteration == 0) state_next = INITIAL_CHECK;  // check first incoming data
          else state_next = PATTERN_CHECK;  // check next incoming data
        end else begin
          capture_en = 1;  // continue capturing input data
          state_next = CAPTURE_SAMPLE;
        end
      end

      INITIAL_CHECK: begin
        state_next = TAP_INCREMENT;
        if (datain_ff == PATTERN || datain_ff == (~PATTERN)) initial_pattern_valid = 1;
        else initial_pattern_valid = 0;
      end

      PATTERN_CHECK: begin
        if ((datain_ff == PATTERN || datain_ff == !(PATTERN))) begin
          valid_pattern = 1;
        end else begin
          valid_pattern = 0;
        end

        if (initial_pattern_valid && iteration == 6'd3) begin
          if (valid_pattern) state_next = TAP_INCREMENT;
          else state_next = MEASURE_DELAY;

        end else begin
          if (initial_pattern_valid) begin
            if (iteration == 1) begin
              if (valid_pattern) begin
                state_next = TAP_INCREMENT;  // keep tap delay incremting if incoming data is valid
              end else begin
                state_next = HOLD_TAP_VALUE;    // store first tap value when the transisation occured (valid data   ------>  metastaibility)
                tap_value_cnt = 2'd0;  // store first tap value to 0 index
              end
            end else begin
              if (valid_pattern) begin
                state_next = HOLD_TAP_VALUE;            // store second tap value when transisation occured (metastaibility   ----> valid data)
                tap_value_cnt = 2'd1;  // store second tap value to 1 index
              end else begin
                state_next = TAP_INCREMENT;  // keep tap delay incrementing until data is metastable
              end
            end

          end else begin
            if (iteration == 1) begin
              if (valid_pattern) begin
                state_next    = HOLD_TAP_VALUE;
                tap_value_cnt = 2'd0;  // store first tap value to 0 index
              end else begin
                state_next = TAP_INCREMENT;
              end
            end else begin
              if (valid_pattern) begin
                state_next = TAP_INCREMENT;
              end else begin
                state_next    = HOLD_TAP_VALUE;
                tap_value_cnt = 2'd1;  // store second tap value to 1 index
              end
            end
          end
        end
      end

      TAP_INCREMENT: begin
        if (dly_tap_value < 62) begin
          dly_inc_int = 1;
          state_next  = WAIT_STATE;
        end else begin
          if (initial_pattern_valid) begin
            if (iteration == 6'd3) begin
              state_next = MEASURE_DELAY;
              mnl_dly_mr = 1;
            end else begin
              state_next = LOW_FREQ;
            end
          end else state_next = CALIBRATION_ERROR;
        end
      end

      WAIT_STATE: begin
        if (dly_ack) state_next = CAPTURE_SAMPLE;
        else state_next = WAIT_STATE;
      end

      LOW_FREQ: begin
        delay_value_int = 6'd32;
        calib_done_int  = 1;
      end

      CALIBRATION_ERROR: begin
        calib_error_int = 1;
        delay_value_int = 6'd0;

      end

      HOLD_TAP_VALUE: begin
        if (~initial_pattern_valid) begin
          if (iteration == 6'd2) begin
            tap_values1[tap_value_cnt] = dly_tap_value;
            state_next = TAP_INCREMENT;
          end else begin
            tap_values1[tap_value_cnt] = dly_tap_value;
            state_next = MEASURE_DELAY;
          end
        end else begin
          tap_values0[tap_value_cnt] = dly_tap_value;
          state_next = TAP_INCREMENT;
        end

      end

      MEASURE_DELAY: begin
        calib_done_int = 1;
        if (~initial_pattern_valid) begin
          tap_values1_half[0] = tap_values1[1] - {1'b0, tap_values1[1][4:1]};  // dividing tap values by 2
          delay_value_int = tap_values1_half[0] + tap_values1[0];
        end else begin
          if (~mnl_dly_mr) begin
            tap_values0_half[0] = tap_values0[1] - {1'b0, tap_values1[1][4:1]};
            delay_value_int = tap_values0[0] - tap_values0_half[0];
          end else begin
            delay_value_int = tap_values0[0] + tap_values0[1];
            delay_value_int = delay_value_int - CLK_TAPS;
          end
        end
      end
    endcase

  end

  /* always@(iteration) begin
    case (iteration)
      6'd0: 
      default: 
    endcase
  end */

endmodule
