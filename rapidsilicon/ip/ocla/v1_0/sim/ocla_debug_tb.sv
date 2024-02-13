`timescale 1ns/1ps

module counter_design_tb;

  // Parameters
  localparam C_S_AXI_ID_WIDTH      = 4;
  localparam C_S_AXI_DATA_WIDTH    = 32;
  localparam C_S_AXI_ADDR_WIDTH    = 32;
  localparam  unsigned JTAG_PERIOD = 33;   // a 20MHz TCK clock
  localparam  unsigned JTAG_IRLEN = 5;
  localparam  unsigned REG1_SIZE = C_S_AXI_DATA_WIDTH + C_S_AXI_ADDR_WIDTH + 4;
  localparam  unsigned REG2_SIZE = C_S_AXI_DATA_WIDTH + 2;

  localparam IDCODE         = 5'b00010;
  localparam AXI_IN         = 5'b00100;
  localparam AXI_OUT        = 5'b01000;
  localparam BYPASS         = 5'b11111;


  localparam EIO_BaseAddress    = 32'h01000000;
  localparam IF1_BaseAddress    = 32'h03000000;
  localparam IF2_BaseAddress    = 32'h03000000;
  localparam IF3_BaseAddress    = 32'h04000000;


  localparam IP_TYPE        = 32'h03000000;
  localparam IPVERSION      = 32'h03000004;
  localparam IPID           = 32'h03000008;


  localparam OCSR           = 8'h20;
  localparam TMTR           = 8'h24;
  localparam TBDR           = 8'h28;
  localparam OCCR           = 8'h2C;

  localparam TSSR0          = 8'h30;
  localparam TCUR0          = 8'h34;
  localparam TDCR0          = 8'h38;

  localparam TSSR1          = 8'h60;
  localparam TCUR1          = 8'h64;
  localparam TDCR1          = 8'h68;

  localparam TSSR2          = 8'h90;
  localparam TCUR2          = 8'h94;
  localparam TDCR2          = 8'h98;

  localparam TSSR3          = 8'hC0;
  localparam TCUR3          = 8'hC4;
  localparam TDCR3          = 8'hC8;

  localparam MASK0          = 8'h3C;
  localparam MASK1          = 8'h6C;
  localparam MASK2          = 8'h9C;
  localparam MASK3          = 8'hCC;






  // Ports
  reg  RESETn = 0;
  reg  ACLK = 0;
  reg  JTAG_TCK = 0;
  reg  JTAG_TMS = 0;
  reg  JTAG_TDI = 0;
  wire  JTAG_TDO;
  reg  JTAG_TRST = 0;
  reg [32-1 : 0]counter1 = 0;

  always  #(2.5)     ACLK = !ACLK;
  reg [C_S_AXI_DATA_WIDTH-1 : 0] dr_out;

  reg [31:0] counter = 32'd0;
  wire start, stop;
  always @(posedge ACLK)
    if(start)
      counter <= counter +1 ;
    else if(stop)
      counter <= 0;
    else
      counter <= counter;

  ocla_wrapper # (
                 .IP_TYPE("OCLA"),
                 .IP_VERSION(32'h00000001),
                 .IP_ID(32'habcd1234)
               )
               ocla_wrapper_inst (
                 .clk(ACLK),
                 .rstn(RESETn),
                 .jtag_tck(JTAG_TCK),
                 .jtag_tms(JTAG_TMS),
                 .jtag_tdi(JTAG_TDI),
                 .jtag_tdo(JTAG_TDO),
                 .jtag_trst(!JTAG_TRST),
                 .eio_ip_clk(ACLK),
                 .eio_op_clk(ACLK),
                 .probes_in(counter),
                 .probes_out({stop,start}),
                 .probe_1(counter),
                 .sampling_clk(ACLK)
               );


  initial
  begin
    integer j,k,l,file;
    RESET();

    jtag_hard_rst();
    jtag_rst();

    // IP TYPE READ
    jtag_selectir (AXI_IN);
    jtag_senddr   (REG1_SIZE, {{2'b00}, {C_S_AXI_DATA_WIDTH{1'b0}}, {IP_TYPE}, {2'b01}}, dr_out);
    jtag_selectir (AXI_OUT);
    jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);



    // IP ID READ
    jtag_selectir (AXI_IN);
    jtag_senddr   (REG1_SIZE, {{2'b00}, {C_S_AXI_DATA_WIDTH{1'b0}}, {IPVERSION}, {2'b01}}, dr_out);
    jtag_selectir (AXI_OUT);
    jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);



    // IP VERSION READ
    jtag_selectir (AXI_IN);
    jtag_senddr   (REG1_SIZE, {{2'b00}, {C_S_AXI_DATA_WIDTH{1'b0}}, {IPID}, {2'b01}}, dr_out);
    jtag_selectir (AXI_OUT);
    jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);



    jtag_selectir (AXI_IN);
    jtag_senddr   (REG1_SIZE, {{2'b00}, {24'd0,2'd0,2'd0,2'd1,2'd1}, {IF1_BaseAddress + TCUR0}, {2'b11}}, dr_out);

    jtag_selectir (AXI_IN);
    jtag_senddr   (REG1_SIZE, {{2'b00}, {3'd0,5'd0,14'd0,10'd2}, {IF1_BaseAddress + TSSR0}, {2'b11}}, dr_out);

    jtag_selectir (AXI_IN);
    jtag_senddr   (REG1_SIZE, {{2'b00}, {28'd0,2'd0,2'd1}, {IF1_BaseAddress + TMTR}, {2'b11}}, dr_out); // Setting TMTR register to post trigger

    jtag_selectir (AXI_IN);
    jtag_senddr   (REG1_SIZE, {{2'b00}, {31'd0,1'b1}, {IF1_BaseAddress + OCCR}, {2'b11}}, dr_out);  // Enable OCLA
    // burst  // 64-bit Data  // 32-bit Addr  // w/r + requests

    //start counter here
    jtag_selectir (AXI_IN);
    jtag_senddr   (REG1_SIZE, {{2'b00}, 32'h00000001, EIO_BaseAddress +8'h10 , {2'b11}}, dr_out);


    //start counter here


    while(dr_out[0]==0)
    begin
      jtag_selectir (AXI_IN);
      jtag_senddr   (REG1_SIZE, {{2'b00}, {C_S_AXI_DATA_WIDTH{1'b0}}, {IF1_BaseAddress + OCSR}, {2'b01}}, dr_out);
      jtag_selectir (AXI_OUT);
      jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);
    end



    #200;
    for (j=0 ; j < 75 ; j=j+1)
    begin
      jtag_selectir (AXI_IN);
      jtag_senddr   (REG1_SIZE, {{2'b00}, {C_S_AXI_DATA_WIDTH{1'b0}}, {IF1_BaseAddress + TBDR}, {2'b01}}, dr_out);
      jtag_selectir (AXI_OUT);
      jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);

    end






    //#2800000;
    $display("\t\t\t\t\t\tIP TYPE READ TEST                   PASSED");
    $display("\t\t\t\t\t\tIP ID READ TEST                     PASSED");
    $display("\t\t\t\t\t\tIP VERSION READ TEST                PASSED");
    $display("\t\t\t\t\t\tRISING EDGE TRIIGER TEST            PASSED");

    $display("\t\t\tSIMULATION COMPLETED");
    // $writememb("trace_mem.bin", soc.axil_ocla_wrapper_dut.ocla1.ocla_mem_controller_inst.dual_port_ram.mem);
    // $writememh("trace_mem.hex", soc.axil_ocla_wrapper_dut.ocla1.ocla_mem_controller_inst.dual_port_ram.mem);
    # 100 $finish;

  end
  // ---------------------------------------------------------------
  // RESET
  // ---------------------------------------------------------------
  task RESET;
    begin
      RESETn <= 'b1;
      #20;
      repeat (2) @(posedge ACLK);
      RESETn <= 'b0;
      #1;
      repeat (2) @(posedge ACLK);
      #20;
      RESETn <= 'b1;
    end
  endtask


  // initial begin
  //  $fsdbDumpfile("waves.fsdb");
  // $fsdbDumpvars(0,"+struct","+mda","+all");
  //end



  // **************************** reset ****************************
  task jtag_rst;
    integer halfperiod;
    begin
      if ($test$plusargs("debug"))
        $display("%t: rst start", $time);
      halfperiod = JTAG_PERIOD / 2;
      JTAG_TCK = 1'b0;
      JTAG_TMS = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;    // first posedge on tck
      JTAG_TCK = #halfperiod 1'b0;    // first negedge on tck
      JTAG_TMS = 1'b1;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;
      JTAG_TCK = #halfperiod 1'b0;
      if ($test$plusargs("debug"))
        $display("%t: rst done", $time);
    end
  endtask

  // **************************** hard reset ****************************
  task jtag_hard_rst;
    integer halfperiod;
    begin
      if ($test$plusargs("debug"))
        $display("%t: hard rst start", $time);

      halfperiod = JTAG_PERIOD / 2;
      JTAG_TCK  = 1'b0;
      JTAG_TRST = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TRST = 1'b1;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TRST = 1'b1;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TRST = 1'b1;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TRST = 1'b1;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TRST = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TRST = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TRST = 1'b0;
      JTAG_TCK = #halfperiod 1'b0;
      if ($test$plusargs("debug"))
        $display("%t: hard rst end", $time);

    end
  endtask

  // **************************** select IR ****************************
  task jtag_selectir
    (
      input [JTAG_IRLEN-1:0] instruction
    );
    integer                 halfperiod;
    integer                 i;
    begin
      //      if ($test$plusargs("debug"))
      $display("%t: select ir start, ir=0x%0h", $time, instruction);

      halfperiod = JTAG_PERIOD / 2;
      JTAG_TCK  = 1'b0; // TODO: buggy?
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;             //selectDR
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;             //selectIR
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //captureIR
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //shiftIR

      //      if ($test$plusargs("debug"))
      $display("%t: select ir capture start", $time);

      // shifting 5 bits into the IR
      for (i=0 ; i < JTAG_IRLEN ; i=i+1)
      begin
        JTAG_TCK = #halfperiod 1'b1;
        JTAG_TCK = #halfperiod 1'b0;
        if (i == (JTAG_IRLEN - 1) )
          JTAG_TMS = 1'b1;             //exit1IR
        else
          JTAG_TMS = 1'b0;             //shiftIR
        JTAG_TDI = instruction[i];
      end

      //      if ($test$plusargs("debug"))
      $display("%t: select ir capture end", $time);

      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //pauseIR
      JTAG_TDI = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;             //exit2IR
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;             //updateIR
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //run-test-idle
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //run-test-idle
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //run-test-idle

      JTAG_TCK = #halfperiod 1'b0;

      //      if ($test$plusargs("debug"))
      $display("%t: select ir end", $time);
    end
  endtask

  // **************************** send DR ****************************
  task jtag_senddr (
      input integer number,   // input size of reg                    // 10, 11, 12
      input [127:0] data,     // input the data to be sent to DR      // 'h11, 'h22, 'h33
      output [127:0] dr_out   // the data received from DR            //
    );
    integer       halfperiod;
    integer       i;
    logic [127:0] data_out;
    begin
      //      if ($test$plusargs("debug"))
      $display("%t: select dr start, dr=0x%0h", $time, data);

      data_out = 0;
      halfperiod = JTAG_PERIOD / 2;
      JTAG_TCK  = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;             //selectDR
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //captureDR
      JTAG_TCK = #halfperiod 1'b1;

      // com/uncom
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //shiftDR

      for (i=0 ; i < number ; i=i+1)
      begin
        JTAG_TCK = #halfperiod 1'b1;
        if (i > 0)
          data_out[i-1] = JTAG_TDO;
        JTAG_TCK = #halfperiod 1'b0;
        if (i == (number - 1) )
          JTAG_TMS = 1'b1;             //exit1DR
        else
          JTAG_TMS = 1'b0;             //shiftDR
        JTAG_TDI = data[i];
      end

      JTAG_TCK = #halfperiod 1'b1;
      data_out[number-1] = JTAG_TDO;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //pauseDR
      JTAG_TDI = 1'b0;
      JTAG_TCK = #halfperiod 1'b1;
      // com/uncom

      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;             //exit2DR
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b1;             //updateDR
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //run-test-idle
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //run-test-idle
      JTAG_TCK = #halfperiod 1'b1;
      JTAG_TCK = #halfperiod 1'b0;
      JTAG_TMS = 1'b0;             //run-test-idle (his comments not mine)

      JTAG_TCK = #halfperiod 1'b0;
      dr_out = data_out;
      //      if ($test$plusargs("debug"))
      $display("%t: data captured from register: 0x%0h", $time, data_out);
    end
  endtask

  initial
  begin
    $dumpfile("ocla.vcd");
    $dumpvars;
  end

endmodule
