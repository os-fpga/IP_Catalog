`timescale 1ns / 1ps

module high_speed_comun_sys_tb;

  // Parameters

  //Ports
  reg reset = 1;

  high_speed_comun_sys  high_speed_comun_sys_inst (
    .reset(reset)
  );
  initial begin
    #100 

reset =0;

#90
$finish;
  end

  initial begin
    
    $dumpfile("deskew_example.vcd");
    $dumpvars();
  end
//always #5  clk = ! clk ;

endmodule