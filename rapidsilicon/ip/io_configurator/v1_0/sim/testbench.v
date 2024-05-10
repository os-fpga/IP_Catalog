`timescale 1ns/1ps

module O_SERDES_tb;

  //Ports
  reg [3:0] FABRIC_D;
  reg  FABRIC_RST;
  reg  FABRIC_LOAD_WORD;
  reg  FABRIC_CLK_IN = 1'd0;
  reg  FABRIC_DLY_LOAD;
  wire  IOPAD_Q;
  reg FABRIC_OE_IN;
  
  io_configurator io_configurator_inst (
    .FABRIC_D(FABRIC_D),
    .FABRIC_RST(FABRIC_RST),
    .FABRIC_LOAD_WORD(FABRIC_LOAD_WORD),
    .FABRIC_CLK_IN(FABRIC_CLK_IN),
    .FABRIC_OE_IN(FABRIC_OE_IN),
    .FABRIC_DLY_LOAD(FABRIC_DLY_LOAD),
    .IOPAD_Q(IOPAD_Q)
  );

always #50 FABRIC_CLK_IN = ~FABRIC_CLK_IN ;

always @(posedge FABRIC_CLK_IN) begin
	FABRIC_D <= $random;
end

initial 
begin
	FABRIC_LOAD_WORD = 0;
	FABRIC_RST = 0;
	FABRIC_OE_IN = 0;
    FABRIC_DLY_LOAD = 0;
	repeat(10)@(posedge FABRIC_CLK_IN);
	FABRIC_LOAD_WORD = 1;
	FABRIC_RST = 1;
	FABRIC_OE_IN = 1;
    FABRIC_DLY_LOAD = 1;
	#100000;
	$finish;
end

initial 
begin
    $dumpfile("O_SERDES.vcd");
    $dumpvars;
end

endmodule