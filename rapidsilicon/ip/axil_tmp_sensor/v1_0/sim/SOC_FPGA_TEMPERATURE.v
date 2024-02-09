`timescale 1ns/1ps
`celldefine
//
// SOC_FPGA_TEMPERATURE simulation model
// SOC Temperature Interface
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module SOC_FPGA_TEMPERATURE #(
  parameter INITIAL_TEMPERATURE = 25, // Specify initial temperature for simulation (0-125)
  parameter TEMPERATURE_FILE = "" // Specify ASCII file containing temperature values over time
) (
  output reg [7:0] TEMPERATURE = INITIAL_TEMPERATURE, // Temperature data
  output reg VALID = 1'b0, // Temperature data valid
  output reg ERROR = 1'b0 // Temperature error
);

  localparam temperature_update_time = 2000.0;  // Update temperature every 2 uS

  integer temp_file;
  integer scan_temp_file;
  integer d;
  integer temp_file_line = 1;
  real delay_time, temp_time;
  integer temp_data = INITIAL_TEMPERATURE, temp_data2 = INITIAL_TEMPERATURE;
  reg valid_data= 1'b1, error_data = 1'b0, valid_data2= 1'b1, error_data2 = 1'b0;
  reg [8*80:0] comment;

  always begin
    if ((temp_data2<0) || (temp_data2>125)) begin
      $display("\nError: Temperature specified at %d is out of range, 0-125C.", temp_data2);
      $finish;
    end
    #temperature_update_time TEMPERATURE = temp_data2;
    VALID = valid_data2;
    ERROR = error_data2;
  end

  initial begin
    if (TEMPERATURE_FILE != "no_file") begin
      temp_file = $fopenr(TEMPERATURE_FILE);
      if (temp_file == 0) begin
        $display("\nError: Could not locate TEMPEARTURE_FILE %s.\nSpecify no_file for TEMPERATUE_FILE if not modifying tempearture for simulation.\n", TEMPERATURE_FILE);
        #1;
        $finish;
      end
      scan_temp_file = $fgetc(temp_file);
      while (scan_temp_file != 32'hffffffff) begin
        d = $ungetc(scan_temp_file, temp_file);
        if (scan_temp_file != "#") begin
          d = $fscanf(temp_file," %f: %d %b %b\n", temp_time, temp_data, valid_data, error_data);
          if ($realtime > temp_time) begin
            $display("\nError: Time specified on line %0d of %0s: %0t is earlier than a previous specified simulation time.\nSimulation times must appear in increasing order.\n", temp_file_line, TEMPERATURE_FILE, temp_time);
            $finish;
          end
          #(temp_time - $realtime);
          temp_data2 = temp_data;
          valid_data2 = valid_data;
          error_data2 = error_data;
        end else begin
          d = $fgets(comment, temp_file);
        end
        scan_temp_file = $fgetc(temp_file);
        temp_file_line = temp_file_line + 1;
      end
      $fclose(temp_file);
    end
  end

 initial begin

    if ((INITIAL_TEMPERATURE < 0) || (INITIAL_TEMPERATURE > 125)) begin
       $display("SOC_FPGA_TEMPERATURE instance %m INITIAL_TEMPERATURE set to incorrect value, %d.  Values must be between 0 and 125.", INITIAL_TEMPERATURE);
    #1 $stop;
    end

  end

endmodule
`endcelldefine
