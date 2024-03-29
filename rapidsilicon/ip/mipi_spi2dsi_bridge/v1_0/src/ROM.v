/* Verilog netlist generated by SCUBA Diamond (64-bit) 3.11.0.396.4 */
/* Module Version: 2.8 */
/* C:\lscc\diamond\3.11_x64\ispfpga\bin\nt64\scuba.exe -w -n ROM -lang verilog -synth lse -bus_exp 7 -bb -arch xo3c00f -type rom -addr_width 10 -num_rows 768 -data_width 8 -outdata REGISTERED -memfile c:/users/gaurav/documents/fpga/lattice/counter/rom.mem -memformat orca  */
/* Tue Jan 14 20:17:42 2020 */


`timescale 1 ns / 1 ps
module ROM (Address, OutClock, OutClockEn, Reset, Q)/* synthesis NGD_DRC_MASK=1 */;
    input wire [9:0] Address;
    input wire OutClock;
    input wire OutClockEn;
    input wire Reset;
    output reg [7:0] Q;


  on_chip_memory  bram (
      .addr_A(Address),
      .din_A(),
      .dout_A(Q),
      .clk_A(OutClock),
      .wen_A(0),
      .ren_A(1)
  );

endmodule

