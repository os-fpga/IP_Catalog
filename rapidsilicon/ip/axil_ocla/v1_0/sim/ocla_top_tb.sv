
//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer:
//
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: OCLA Controller
// Module Name: OCLA Controller
// Project Name: OCLA IP Core Development
// Target Devices: Gemini RS-75
// Tool Versions: Raptor
// Description:
// TBA
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////

/* verilator lint_off WIDTHCONCAT */
/* verilator lint_off ASSIGNDLY */
/* verilator lint_off STMTDLY */
/* verilator lint_off UNUSED */
/* verilator lint_off MULTITOP */
/* verilator lint_off WIDTH */
`include "/home/users/zafar.ali/Desktop/OCLA/rapidsilicon/ip/axil_ocla/v1_0/ocla_wrapper/src/defines.sv"

module ocla_top_tb;

  // Parameters
  localparam O = 1'b0;
  localparam C1 = 2'b01;
  localparam E1 = 2'b01;
  localparam L1 = 1'b0;
  localparam V1 = 2'b0;
  localparam C2 = 2'b0;
  localparam E2 = 2'b0;
  localparam L2 = 1'b0;
  localparam V2 = 2'b0;
  localparam B = 2'b0;
  localparam P1 = 7'd3;
  localparam P2 = 8'b0;
  localparam NO_OF_PROBES = `NUM_OF_PROBES;

  // Ports

  reg                     sample_clk;
  reg                     rstn = 0;
  reg  [NO_OF_PROBES-1:0] probes;
  reg                     S_AXI_ACLK;
  reg                     S_AXI_ARESETN = 0;
  reg  [        32-1 : 0] S_AXI_AWADDR;
  reg  [           2 : 0] S_AXI_AWPROT;
  reg                     S_AXI_AWVALID = 0;
  wire                    S_AXI_AWREADY;
  reg  [        32-1 : 0] S_AXI_WDATA;
  reg  [    (32/8)-1 : 0] S_AXI_WSTRB;
  reg                     S_AXI_WVALID = 0;
  wire                    S_AXI_WREADY;
  wire [           1 : 0] S_AXI_BRESP;
  wire                    S_AXI_BVALID;
  reg                     S_AXI_BREADY = 0;
  reg  [        32-1 : 0] S_AXI_ARADDR;
  reg  [           2 : 0] S_AXI_ARPROT = 0;
  reg                     S_AXI_ARVALID = 0;
  wire                    S_AXI_ARREADY;
  wire [        32-1 : 0] S_AXI_RDATA;
  wire [           1 : 0] S_AXI_RRESP;
  wire                    S_AXI_RVALID;
  reg                     S_AXI_RREADY = 0;

  wire [NO_OF_PROBES-1:0] gray_out;
  wire [NO_OF_PROBES-1:0] binary_out;
  wire [NO_OF_PROBES-1:0] data_accumulate;
  reg                     trigger_in;

  wire                    data_wen;

  reg  [          32-1:0] ocsr_reg_read = 32'h0;


  ocla ocla_top_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .probes(binary_out),
`ifdef TRIGGER_INPUTS
      .trigger_input(trigger_in),
`endif
      .S_AXI_ACLK(S_AXI_ACLK),
      .S_AXI_ARESETN(S_AXI_ARESETN),
      .S_AXI_AWADDR(S_AXI_AWADDR),
      .S_AXI_AWPROT(S_AXI_AWPROT),
      .S_AXI_AWVALID(S_AXI_AWVALID),
      .S_AXI_AWREADY(S_AXI_AWREADY),
      .S_AXI_WDATA(S_AXI_WDATA),
      .S_AXI_WSTRB(S_AXI_WSTRB),
      .S_AXI_WVALID(S_AXI_WVALID),
      .S_AXI_WREADY(S_AXI_WREADY),
      .S_AXI_BRESP(S_AXI_BRESP),
      .S_AXI_BVALID(S_AXI_BVALID),
      .S_AXI_BREADY(S_AXI_BREADY),
      .S_AXI_ARADDR(S_AXI_ARADDR),
      .S_AXI_ARPROT(S_AXI_ARPROT),
      .S_AXI_ARVALID(S_AXI_ARVALID),
      .S_AXI_ARREADY(S_AXI_ARREADY),
      .S_AXI_RDATA(S_AXI_RDATA),
      .S_AXI_RRESP(S_AXI_RRESP),
      .S_AXI_RVALID(S_AXI_RVALID),
      .S_AXI_RREADY(S_AXI_RREADY)
  );

  gray_counter #(
      .NUM_OF_PROBE(NO_OF_PROBES)
  ) gray_counter_inst (
      .sample_clk(sample_clk),
      .rstn(rstn & ocla_top_inst.sampling_en),
      //.rstn(rstn),
      .gray_out(gray_out),
      .binary_out(binary_out)
  );

  sampler_buffer sampler_buffer_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .probes(binary_out),
      .sampling_en(ocla_top_inst.sampling_en),
      .data_wen(data_wen),
      .data_accumulate(data_accumulate)
  );


  integer error_count = 0;
  integer test_count = 0;


  integer j = 0;
  integer a = 0;

  reg [NO_OF_PROBES-1:0] mem_tb[0:`MEMORY_DEPTH-1];

  reg [NO_OF_PROBES-1:0] read_mem[0:`MEMORY_DEPTH-1];

  always @(posedge sample_clk) begin
    if (ocla_top_inst.ocla_mem_controller_inst.wen) begin
      mem_tb[j] <= data_accumulate;  //{'b0,gray_out};
      if (j == `MEMORY_DEPTH - 1) j = 0;
      else j = j + 1;
    end
  end

  // ---------------------------------------------------------------
  // trigger input assert
  integer trigger_event_value = 0;
  integer trigger_event = 0;

  always @(posedge sample_clk) begin
    if (ocla_top_inst.reset_fifo_wr_pntr_sync) begin
      trigger_event <= 0;
    end else begin
      trigger_event <= trigger_event + 1;
      if (trigger_event >= trigger_event_value) begin
        trigger_in <= 1;
        trigger_event <= 0;
      end else begin
        trigger_in <= 0;
      end
    end
  end
  // ---------------------------------------------------------------
  // TB Memory initialize
  initial begin
    for (j = 0; j < `MEMORY_DEPTH; j = j + 1) begin
      mem_tb[j] = 0;
    end
    j = 0;
  end

  integer indx;

  // ---------------------------------------------------------------//
  // Run Various sanity check tests                                 //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//

  initial begin
    begin
      indx = 0;
      trigger_in = 0;
      RESET();


      // axi_write_transaction(32'h8, {P2, 7'd3, B, V2, L2, E2, C2, V1, L1, E1, C1, O});
      // @(posedge S_AXI_ACLK);

      // axi_write_transaction(32'hC, 32'b100);
      // repeat(256) @(posedge S_AXI_ACLK);

      // @(posedge S_AXI_ACLK);
      // for(indx=0;indx < 100; indx=indx+1 ) begin
      // axi_read_transaction(32'h04);
      // end
      // repeat(10) @(posedge S_AXI_ACLK);

      basic_sanity_check_for_continous_and_fix_mode_0(
          2);  // for number of probes less than or equal to 32
      basic_sanity_check_for_post_triggered_overandunder_flow_mode_0(2);
      basic_sanity_check_for_continous_and_fix_mode_0(
          2);  // for number of probes less than or equal to 32
      basic_sanity_check_for_post_triggered_overandunder_flow_mode_0(2);
      // // $finish;

      // trigger_event_value = 50;
      // centertrig_fix_no_samples();

      // @(posedge S_AXI_ACLK);
      $finish;
    end
  end


  // ---------------------------------------------------------------
  // Continous and fix number of samples capture mode for continous
  // and pre triggered modes
  // ---------------------------------------------------------------

  task basic_sanity_check_for_continous_and_fix_mode_0(input integer times);
    begin
      $display("-----------------------------------------------------");
      $display("STARTING A REGRESSION");

      repeat (times) begin
        j = 0;
        a = 0;
        $display("countinous_full_window_sample");
        countinous_full_window_sample();
        a = 0;
        j = 0;

        $display("countinous_fix_no_samples");
        countinous_fix_no_samples();

        a = 0;
        j = 0;
        $display("pretrig_full_window_sample ");
        pretrig_full_window_sample();
        repeat (2) @(posedge S_AXI_ACLK);
        a = 0;
        j = 0;
        $display("pretrig_fix_no_samples");
        pretrig_fix_no_samples();
        repeat (2) @(posedge S_AXI_ACLK);
        a = 0;
        j = 0;
      end

      $display("-----------------------------------------------------");
      $display("basic_sanity_check_for_continous_and_fix_mode_0 finished");
      $display(" \t \t STATS");
      $display("\t TOTAL TESTS: %d", test_count);
      $display("\t TOTAL PASSED TEST: %d", test_count - error_count);
      $display("\t TOTAL ERRORS COUNT: %d", error_count);

      $display("-----------------------------------------------------");

    end
  endtask

  // ---------------------------------------------------------------
  // basic_sanity_check_for_post_triggered_overandunder_flow_mode_0
  // ---------------------------------------------------------------
  task basic_sanity_check_for_post_triggered_overandunder_flow_mode_0(input integer times);
    begin
      $display("-----------------------------------------------------");
      $display("basic_sanity_check_for_post_triggered_overandunder_flow_mode_0");
      repeat (times) begin
        j = 0;
        a = 0;
        trigger_event_value = 300;  // post trigger over flow
        $display("posttrig_full_window_sample over flow ");
        j = 0;
        a = 0;
        posttrig_full_window_sample();
        @(posedge S_AXI_ACLK);
        $display("posttrig_full_window_sample under flow");

        trigger_event_value = 100;  // post trigger under flow
        posttrig_full_window_sample();

        j = 0;
        a = 0;
        @(posedge S_AXI_ACLK);
        $display("posttrig_full_window_sample over flow");

        trigger_event_value = 900;  // post trigger over flow
        posttrig_full_window_sample();
        @(posedge S_AXI_ACLK);

        $display("posttrig_full_window_sample under flow ");
        j = 0;
        a = 0;
        trigger_event_value = 50;  // post trigger under flow
        posttrig_full_window_sample();
        @(posedge S_AXI_ACLK);

        $display("posttrig_full_window_sample  over flow");
        j = 0;
        a = 0;
        trigger_event_value = 600;  // post trigger over flow
        posttrig_full_window_sample();
        @(posedge S_AXI_ACLK);

        $display("posttrig_full_window_sample under flow ");
        j = 0;
        a = 0;
        trigger_event_value = 200;  // post trigger under flow
        posttrig_full_window_sample();
        @(posedge S_AXI_ACLK);

      end
      $display("-----------------------------------------------------");
      $display("basic_sanity_check_for_post_triggered_overandunder_flow_mode_0 finished");
      $display(" \t \t STATS");
      $display("\t TOTAL TESTS: %d", test_count);
      $display("\t TOTAL PASSED TEST: %d", test_count - error_count);
      $display("\t TOTAL ERRORS COUNT: %d", error_count);
      $display("-----------------------------------------------------");

    end
  endtask

  // ---------------------------------------------------------------
  // Continous full window capture mode
  // ---------------------------------------------------------------
  task countinous_full_window_sample();
    begin
      axi_write_transaction(32'h8, {P2, 7'd3, B, V2, L2, E2, C2, V1, L1, E1, C1, O});
      @(posedge S_AXI_ACLK);

      axi_write_transaction(32'hC, 32'b100);
      @(posedge S_AXI_ACLK);
      repeat (10) @(posedge S_AXI_ACLK);
      do begin
        read_OCSR();
        @(posedge S_AXI_ACLK);

      end while (ocsr_reg_read != 32'hc0000001);
      for (indx = 0; indx < `MEMORY_DEPTH - 1; indx = indx + 1) begin
        axi_read_transaction(32'h04);
        assert (read_mem[indx] == mem_tb[indx]) test_count = test_count + 1;
        else begin
          $error("memory read error %d != %d , index: %d", read_mem[indx], mem_tb[indx], indx);

          error_count = error_count + 1;
          test_count  = test_count + 1;
          $stop;
        end
        @(posedge S_AXI_ACLK);
      end

      // $display("countinous_full_window_sample ending with %d errors ", error_count);
      // $display("----------------------------------------------------");
    end
  endtask

  // ---------------------------------------------------------------
  // Continous fix number of samples capture mode
  // ---------------------------------------------------------------
  task countinous_fix_no_samples();
    begin
      axi_write_transaction(32'h8, {P2, 7'd3, B, V2, L2, E2, C2, V1, L1, E1, C1, O});
      @(posedge S_AXI_ACLK);

      axi_write_transaction(32'hC, 32'b111101100);
      @(posedge S_AXI_ACLK);
      repeat (10) @(posedge S_AXI_ACLK);
      do begin
        read_OCSR();
        @(posedge S_AXI_ACLK);

      end while (ocsr_reg_read != 32'hc0000001);
      for (indx = 0; indx < 30; indx = indx + 1) begin
        axi_read_transaction(32'h04);
        assert (read_mem[indx] == mem_tb[indx]) test_count = test_count + 1;
        else begin
          $error("memory read error %d != %d , index: %d", read_mem[indx], mem_tb[indx], indx);
          error_count = error_count + 1;
          test_count  = test_count + 1;
          $stop;
        end
        @(posedge S_AXI_ACLK);
      end
      //   $display("countinous_fix_no_samples ending with %d errors ", error_count);
      //   $display("----------------------------------------------------");
    end
  endtask

  // ---------------------------------------------------------------
  // Pre trigger full window capture mode
  // ---------------------------------------------------------------
  task pretrig_full_window_sample();
    begin
      trigger_event_value = 60;
      axi_write_transaction(32'h8, {P2, 7'd0, B, V2, L2, E2, C2, V1, L1, E1, C1, O});
      @(posedge S_AXI_ACLK);

      axi_write_transaction(32'hC, 32'b0101);
      repeat (10) @(posedge S_AXI_ACLK);
      do begin
        read_OCSR();
        @(posedge S_AXI_ACLK);

      end while (ocsr_reg_read != 32'hc0000001);
      for (indx = 0; indx < `MEMORY_DEPTH - 1; indx = indx + 1) begin
        axi_read_transaction(32'h04);
        assert (read_mem[indx] == mem_tb[indx]) test_count = test_count + 1;
        else begin
          $error("memory read error %d != %d ", read_mem[indx], mem_tb[indx]);
          error_count = error_count + 1;
          test_count  = test_count + 1;
          $stop;
        end
        @(posedge S_AXI_ACLK);
      end

      // $display("pretrig_full_window_sample ending with %d errors ", error_count);
      // $display("----------------------------------------------------");
    end
  endtask

  // ---------------------------------------------------------------
  // Pre trigger fix number of samples capture mode
  // ---------------------------------------------------------------
  task pretrig_fix_no_samples();
    begin
      axi_write_transaction(32'h8, {P2, 7'd0, B, V2, L2, E2, C2, V1, L1, E1, C1, O});
      @(posedge S_AXI_ACLK);

      axi_write_transaction(32'hC, 32'b11111101);
      @(posedge S_AXI_ACLK);
      repeat (10) @(posedge S_AXI_ACLK);
      do begin
        read_OCSR();
        @(posedge S_AXI_ACLK);

      end while (ocsr_reg_read != 32'hc0000001);
      repeat (10) @(posedge S_AXI_ACLK);

      for (indx = 0; indx < 15; indx = indx + 1) begin
        axi_read_transaction(32'h04);
        assert (read_mem[indx] == mem_tb[indx]) test_count = test_count + 1;
        else begin
          $error("memory read error %d != %d index: %d", read_mem[indx], mem_tb[indx], indx);
          error_count = error_count + 1;
          test_count  = test_count + 1;
          $stop;
        end
        @(posedge S_AXI_ACLK);
      end
      // $display("pretrig_fix_no_samples ending with %d errors ", error_count);
      // $display("----------------------------------------------------");
    end

  endtask

  // ---------------------------------------------------------------
  // Post trigger full window capture mode
  // ---------------------------------------------------------------
  task posttrig_full_window_sample();
    begin
      integer loop_range;

      axi_write_transaction(32'h8, {P2, 7'd0, B, V2, L2, E2, C2, V1, L1, E1, C1, O});
      @(posedge S_AXI_ACLK);

      axi_write_transaction(32'hC, 32'b0110);
      @(posedge S_AXI_ACLK);
      repeat (10) @(posedge S_AXI_ACLK);
      do begin
        read_OCSR();
        @(posedge S_AXI_ACLK);

      end while (ocsr_reg_read != 32'hc0000001);
      a = 0;
      //j = 0;
      while (!ocla_top_inst.mem_empty) begin
        axi_read_transaction(32'h04);
        @(posedge S_AXI_ACLK);
      end
      if (trigger_event_value < `MEMORY_DEPTH) begin
        loop_range = trigger_event_value;
        j = 0;
      end else loop_range = `MEMORY_DEPTH;
      for (indx = 0; indx < loop_range - 1; indx = indx + 1) begin
        assert (read_mem[indx] == mem_tb[j]) test_count = test_count + 1;
        else begin
          $error("memory read error %d != %d index = %d j = %d", read_mem[indx], mem_tb[j], indx,
                 j);
          error_count = error_count + 1;
          test_count  = test_count + 1;
          $stop;
        end
        if (j == loop_range - 1) j = 0;
        else j = j + 1;
        @(posedge S_AXI_ACLK);
      end

      // $display("posttrig_full_window_sample ending with %d errors ", error_count);
      // $display("TOTAL TESTS: %d", test_count);
      j = 0;
      // $display("----------------------------------------------------");
    end
  endtask

  // ---------------------------------------------------------------
  //center trigger overflow and underflow
  // ---------------------------------------------------------------
  task centertrig_fix_no_samples();
    begin

      axi_write_transaction(32'h8, {P2, 7'd0, B, V2, L2, E2, C2, V1, L1, E1, C1, O});
      @(posedge S_AXI_ACLK);

      axi_write_transaction(32'hC, 32'b11111111);
      repeat (10) @(posedge S_AXI_ACLK);
      do begin
        read_OCSR();
        @(posedge S_AXI_ACLK);

      end while (ocsr_reg_read != 32'hc0000001);
      for (indx = 0; indx < 30; indx = indx + 1) begin
        axi_read_transaction(32'h04);
        assert (read_mem[indx] == mem_tb[indx]) test_count = test_count + 1;
        else begin
          $error("memory read error");
          error_count = error_count + 1;
          test_count  = test_count + 1;
        end
        @(posedge S_AXI_ACLK);
      end
      // $display("pretrig_fix_no_samples ending with %d errors ", error_count);
      // $display("----------------------------------------------------");
    end

  endtask


  // always @(posedge sample_clk) begin
  //   probes = $random;
  // end
  // Note: sample_clk must be defined as a reg when using this method

  parameter PERIOD = 10;
  parameter PERIOD2 = 10;
  always begin
    sample_clk = 1'b0;
    #(PERIOD / 2) sample_clk = 1'b1;
    #(PERIOD / 2);
  end
  always begin
    S_AXI_ACLK = 1'b0;
    #(PERIOD2 / 2) S_AXI_ACLK = 1'b1;
    #(PERIOD2 / 2);
  end
  //always #5 sample_clk = !sample_clk;
  // always #5 S_AXI_ACLK = !S_AXI_ACLK;

  // ---------------------------------------------------------------
  // AXI WRITE Transaction
  // ---------------------------------------------------------------
  task axi_write_transaction(input [31:0] awaddr, input [31:0] wdata);
    begin
      fork

        write_addr(awaddr);
        write_data(wdata);
        write_resp;
      join
    end

  endtask

  // ---------------------------------------------------------------
  // AXI WRITE ADDRESS
  // ---------------------------------------------------------------
  task write_addr(input [31:0] awaddr);

    begin
      S_AXI_AWADDR  <= awaddr;
      S_AXI_AWPROT  <= 0;
      S_AXI_AWVALID <= 1;
      @(posedge S_AXI_AWREADY) #1;
      begin
        @(posedge S_AXI_ACLK);
        S_AXI_AWADDR  <= 0;
        S_AXI_AWVALID <= 0;
        //  repeat (2) @ (posedge S_AXI_ACLK);
      end
    end
  endtask

  // ---------------------------------------------------------------
  // AXI WRITE DATA
  // ---------------------------------------------------------------
  task write_data(input [31:0] wdata);
    begin
      S_AXI_WVALID <= 1;
      S_AXI_WSTRB  <= 4'b1111;
      S_AXI_WDATA  <= wdata;
      @(posedge S_AXI_WREADY) begin
        @(posedge S_AXI_ACLK) S_AXI_WVALID <= #1 0;
        S_AXI_WSTRB <= #1 4'b0;
        S_AXI_WDATA <= #1 32'h0;
        //  repeat (2) @ (posedge axi_aclk);
      end
    end
  endtask

  // ---------------------------------------------------------------
  // AXI WRITE RESPONSE
  // ---------------------------------------------------------------
  task write_resp;
    begin
      @(posedge S_AXI_BVALID) #1;
      S_AXI_BREADY <= 'b1;
      @(posedge S_AXI_ACLK) S_AXI_BREADY <= #1'b0;
    end
  endtask


  // ---------------------------------------------------------------
  // RESET
  // ---------------------------------------------------------------
  task RESET;
    begin
      rstn <= 1'b0;
      S_AXI_ARESETN <= 'b0;
      #1;
      repeat (2) @(posedge S_AXI_ACLK);
      #1;
      rstn <= 1'b1;
      S_AXI_ARESETN <= 'b1;
    end
  endtask

  // ---------------------------------------------------------------
  //  READ ADDRESS
  // ---------------------------------------------------------------
  task read_addr(input [31:0] araddr);
    begin
      S_AXI_ARADDR  <= araddr;

      S_AXI_ARVALID <= 1;
      @(posedge S_AXI_ARREADY) @(posedge S_AXI_ACLK) S_AXI_ARVALID <= #1 0;

      //s_axi_araddr <= 32'd0;
    end
  endtask
  // ---------------------------------------------------------------
  //  READ DATA
  // ---------------------------------------------------------------
  task read_data;
    begin
      @(posedge S_AXI_RVALID) @(posedge S_AXI_ACLK) S_AXI_RREADY <= 1;
      read_mem[a] <= S_AXI_RDATA;
      @(posedge S_AXI_ACLK) S_AXI_RREADY <= #1 0;
    end
  endtask
  // ---------------------------------------------------------------
  //  READ Transaction
  // ---------------------------------------------------------------
  task axi_read_transaction(input [31:0] araddr);
    begin
      fork
        read_addr(araddr);
        read_data;
      join
      a = a + 1;

    end

  endtask

  // ---------------------------------------------------------------
  //  READ OCLA Status Register
  // ---------------------------------------------------------------
  task read_OCSR();
    begin
      fork
        read_addr(32'h00);
        begin
          @(posedge S_AXI_RVALID) @(posedge S_AXI_ACLK) S_AXI_RREADY <= 1;
          ocsr_reg_read <= S_AXI_RDATA;
          @(posedge S_AXI_ACLK) S_AXI_RREADY <= #1 0;
        end
      join

    end

  endtask
  // ---------------------------------------------------------------
  //  Dump vcd
  // ---------------------------------------------------------------
  initial begin
    $dumpfile("dump.vcd");
    $dumpvars;
  end
endmodule
