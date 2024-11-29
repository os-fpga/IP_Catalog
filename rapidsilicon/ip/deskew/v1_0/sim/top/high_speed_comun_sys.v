module high_speed_comun_sys (

    input reset

  );

  wire fabric_clk_out, s_data;
  wire calib_done, calib_error;


  transmiter_top  transmiter_top_inst (
                    .clk(fabric_clk_out),
                    .rst(reset),
                    .calib_done(calib_done),
                    .calib_error(calib_error),
                    .s_data(s_data),
                    .dly_tap_value(dly_tap_value)
                  );

  receiver_top  receiver_top_inst (
                  .rst(rst),
                  .s_data(s_data),
                  .fabric_clk_out(fabric_clk_out),
                  .calib_done(calib_done),
                  .calib_error(calib_error)
                );

endmodule
