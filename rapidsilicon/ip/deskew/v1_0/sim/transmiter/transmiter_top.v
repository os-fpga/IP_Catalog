module transmiter_top (

    input   wire clk,
    input   wire rst,
    input   wire calib_done,
    input   wire calib_error,
    output  wire s_data,
    output  wire [5:0] dly_tap_value

  );

  wire [7:0] p_data;

  io_configurator_trans io_configurator_trans_inst (
                    .IOPAD_SDATA(s_data),
                    .FABRIC_PDATA_0(p_data),
                    .FABRIC_CLK_IN(clk),
                    .FABRIC_DATA_VALID(),
                    .FABRIC_OE_IN(),
                    .FABRIC_RST(rst),
                    .SEL_DLY(1'b1),
                    .FABRIC_DLY_LOAD(1'b1),
                    .FABRIC_DLY_ADJ(),
                    .FABRIC_DLY_INCDEC(),
                    .FABRIC_DLY_TAP_VALUE_0(dly_tap_value)
                  );
endmodule
