module receiver_top (

    input  wire rst,
    input  wire s_data,
    output fabric_clk_out,
    output wire calib_done,
    output wire calib_error

);

  wire  sel_dly;
  wire [7:0] p_data;
  wire [5:0] dly_tape_value;
  wire dly_ld, dly_adj, dly_incdec;


  io_configurator io_configurator_inst (
      .IOPAD_SDATA(s_data),
      .FABRIC_EN(1'b1),
      .FABRIC_BITSLIP_ADJ(),
      .FABRIC_CLK_OUT(fabric_clk_out),
      .FABRIC_DPA_LOCK(),
      .FABRIC_DPA_ERROR(),
      .FABRIC_DATA_VALID(),
      .FABRIC_PDATA_0(p_data),
      .FABRIC_RST(rst),
      .SEL_DLY(sel_dly),
      .FABRIC_DLY_LOAD(dly_ld),
      .FABRIC_DLY_ADJ(dly_adj),
      .FABRIC_DLY_INCDEC(dly_incdec),
      .FABRIC_DLY_TAP_VALUE_0(dly_tape_value)
  );

  deskew_wrapper deskew_wrapper_inst (
      .CLK_IN(fabric_clk_out),
      .RST(rst),
      .DATA_IN(p_data),
      .DLY_TAP_VALUE(dly_tape_value),
      .DLY_LOAD(dly_ld),
      .DLY_ADJ(dly_adj),
      .DLY_INCDEC(dly_incdec),
      .DLY_SEL(sel_dly),
      .CALIB_DONE(calib_done),
      .CALIB_ERROR(calib_error)
  );

endmodule
