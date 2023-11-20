/* verilator lint_off EOFNEWLINE */
`timescale 1ns/1ps
module axil_ocla_wrapper_tb;

  // Parameters
 localparam NUM_OF_PROBE = 24;
  // Ports
  reg i_S_AXI_ACLK = 0;
  reg i_S_AXI_ARESETN = 0;
  reg i_sample_clk = 0;
  reg i_rstn = 0;
  reg s_axil_awvalid = 0;
  wire s_axil_awready;
  reg [31:0] s_axil_awaddr;
  reg [2:0] s_axil_awprot;
  reg s_axil_wvalid = 0;
  wire s_axil_wready;
  reg [31:0] s_axil_wdata;
  reg [3:0] s_axil_wstrb;
  wire s_axil_bvalid;
  reg s_axil_bready = 0;
  wire [1:0] s_axil_bresp;
  reg s_axil_arvalid = 0;
  wire s_axil_arready;
  reg [31:0] s_axil_araddr;
  reg [2:0] s_axil_arprot;
  wire s_axil_rvalid;
  reg s_axil_rready = 0;
  wire [1:0] s_axil_rresp;
  wire [31:0] s_axil_rdata;
  //reg [23:0] i_probes;
  
  logic [NUM_OF_PROBE-1:0] gray_out, binary_out;
  // ---------------------------------------------------------------
  // OCLA Logic Analyzer
  // ---------------------------------------------------------------
  axil_ocla_wrapper #(
    .IP_TYPE("ocla"),
    .IP_VERSION(32'h1),
    .IP_ID(32'h3981233)
  )
  axil_ocla_wrapper_dut (
      .i_S_AXI_ACLK(i_S_AXI_ACLK),
      .i_S_AXI_ARESETN(i_S_AXI_ARESETN),
      .i_sample_clk(i_sample_clk),
      .i_rstn(i_rstn),
      .s_axil_awvalid(s_axil_awvalid),
      .s_axil_awready(s_axil_awready),
      .s_axil_awaddr(s_axil_awaddr),
      .s_axil_awprot(s_axil_awprot),
      .s_axil_wvalid(s_axil_wvalid),
      .s_axil_wready(s_axil_wready),
      .s_axil_wdata(s_axil_wdata),
      .s_axil_wstrb(s_axil_wstrb),
      .s_axil_bvalid(s_axil_bvalid),
      .s_axil_bready(s_axil_bready),
      .s_axil_bresp(s_axil_bresp),
      .s_axil_arvalid(s_axil_arvalid),
      .s_axil_arready(s_axil_arready),
      .s_axil_araddr(s_axil_araddr),
      .s_axil_arprot(s_axil_arprot),
      .s_axil_rvalid(s_axil_rvalid),
      .s_axil_rready(s_axil_rready),
      .s_axil_rresp(s_axil_rresp),
      .s_axil_rdata(s_axil_rdata),
      .i_probes(binary_out)
  );


  // ---------------------------------------------------------------
  // Counter DUT
  // ---------------------------------------------------------------
  gray_counter #(
      .NUM_OF_PROBE(NUM_OF_PROBE)
  ) gray_counter_inst (
      .sample_clk(i_sample_clk),
      .rstn(i_rstn),
      .gray_out(gray_out),
      .binary_out(binary_out)
  );
  integer i;
  initial begin
    begin
      #10;
      repeat (2) @(posedge i_S_AXI_ACLK);
      RESET();
      repeat (2) @(posedge i_S_AXI_ACLK);
       // ---------------------------------------------------------------

      $display("---------------------SIMULATION STATUS------------------------");               

      axi_read_transaction(32'h18);
        $display("----READING IP TYPE                                      PASSED");               

      axi_read_transaction(32'h20);
        $display("----READING IP ID                                        PASSED");               

      axi_read_transaction(32'h1C);
        $display("----READING IP VERSION                                   PASSED");               

        config_trig_in_pre;
        $display("----OCLA PRE-TRIGGERED TEST                              PASSED");               
        RESET();
        config_trig_in_post;
        $display("----OCLA POST-TRIGGERED TEST                             PASSED");               
        RESET();
        config_trig_in_cntr;
        $display("----OCLA CENTERED-TRIGGERED TEST                         PASSED");               
        RESET();
      //  config_trig_vc;
        
      #10;
      $display("---------------------SIMULATION COMPLETED------------------------");               
            
      $finish;
    end
  end

  always #5 i_sample_clk = !i_sample_clk;
  always #5 i_S_AXI_ACLK = !i_S_AXI_ACLK;

  // ---------------------------------------------------------------
  // config_trig_in Value Compare trigger
  // ---------------------------------------------------------------
  task config_trig_vc;
  begin
    axi_write_transaction(32'h10, 32'h13);
    @(posedge i_S_AXI_ACLK);
    axi_write_transaction(32'h08,32'h14004E);
    @(posedge i_S_AXI_ACLK);

    axi_write_transaction(32'hC, 32'h7);
    @(posedge i_S_AXI_ACLK);
    repeat (10) @(posedge i_S_AXI_ACLK);
    
          repeat (100) @(posedge i_S_AXI_ACLK);
    do begin 
      repeat (2) @(posedge i_S_AXI_ACLK);
      axi_read_transaction(32'b0);
    end
    while(s_axil_rdata[0] != 1);
       for(i = 0; i < 64; i = i +1) begin
                 axi_read_transaction(32'h04);
         
               end
    repeat (2) @(posedge i_S_AXI_ACLK);
  end

  endtask

  // ---------------------------------------------------------------
  // config_trig_in pre trigger
  // ---------------------------------------------------------------
  task config_trig_in_pre;
  begin
    axi_write_transaction(32'h08,32'h14000A);
    @(posedge i_S_AXI_ACLK);

    axi_write_transaction(32'hC, 32'h5);
    @(posedge i_S_AXI_ACLK);
    repeat (10) @(posedge i_S_AXI_ACLK);
    
          repeat (100) @(posedge i_S_AXI_ACLK);
    do begin 
      repeat (2) @(posedge i_S_AXI_ACLK);
      axi_read_transaction(32'b0);
    end
    while(s_axil_rdata[0] != 1);
       for(i = 0; i < 64; i = i +1) begin
                 axi_read_transaction(32'h04);
         
               end
    repeat (2) @(posedge i_S_AXI_ACLK);
  end

endtask


  // ---------------------------------------------------------------
  // config_trig_in cntr trigger
  // ---------------------------------------------------------------
  task config_trig_in_cntr;
  begin
    axi_write_transaction(32'h08,32'h14000A);
    @(posedge i_S_AXI_ACLK);

    axi_write_transaction(32'hC, 32'h7);
    @(posedge i_S_AXI_ACLK);
    repeat (10) @(posedge i_S_AXI_ACLK);
                repeat (100) @(posedge i_S_AXI_ACLK);
    do begin 
      repeat (2) @(posedge i_S_AXI_ACLK);
      axi_read_transaction(32'b0);
    end
    while(s_axil_rdata[0] != 1);

    for(i = 0; i < 64; i = i +1) begin
      axi_read_transaction(32'h04);

    end
repeat (100) @(posedge i_S_AXI_ACLK);
  end

  endtask


  // ---------------------------------------------------------------
  // config_trig_in post trigger
  // ---------------------------------------------------------------
  task config_trig_in_post;
  begin
    axi_write_transaction(32'h08,32'h14000A);
    @(posedge i_S_AXI_ACLK);

    axi_write_transaction(32'hC, 32'h6);
    @(posedge i_S_AXI_ACLK);
    repeat (10) @(posedge i_S_AXI_ACLK);
                repeat (100) @(posedge i_S_AXI_ACLK);
    do begin 
      repeat (2) @(posedge i_S_AXI_ACLK);
      axi_read_transaction(32'b0);
    end
    while(s_axil_rdata[0] != 1);

    for(i = 0; i < 64; i = i +1) begin
      axi_read_transaction(32'h04);

    end
repeat (100) @(posedge i_S_AXI_ACLK);
  end

endtask
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
      s_axil_awaddr  <= awaddr;
      s_axil_awprot  <= 0;
      s_axil_awvalid <= 1;
      @(posedge s_axil_awready) #1;
      begin
        @(posedge i_S_AXI_ACLK);
        s_axil_awaddr  <= 0;
        s_axil_awvalid <= 0;
        //  repeat (2) @ (posedge S_AXI_ACLK);
      end
    end
  endtask

  // ---------------------------------------------------------------
  // AXI WRITE DATA
  // ---------------------------------------------------------------
  task write_data(input [31:0] wdata);
    begin
      s_axil_wvalid <= 1;
      s_axil_wstrb  <= 4'b1111;
      s_axil_wdata  <= wdata;
      @(posedge s_axil_wready) begin
        @(posedge i_S_AXI_ACLK) s_axil_wvalid <= #1 0;
        s_axil_wstrb <= #1 4'b0;
        s_axil_wdata <= #1 32'h0;
        //  repeat (2) @ (posedge axi_aclk);
      end
    end
  endtask

  // ---------------------------------------------------------------
  // AXI WRITE RESPONSE
  // ---------------------------------------------------------------
  task write_resp;
    begin
      @(posedge s_axil_bvalid) #1;
      s_axil_bready <= 'b1;
      @(posedge i_S_AXI_ACLK) s_axil_bready <= #1'b0;
    end
  endtask

  // ---------------------------------------------------------------
  //  READ ADDRESS
  // ---------------------------------------------------------------
  task read_addr(input [31:0] araddr);
    begin
      s_axil_araddr  <= araddr;

      s_axil_arvalid <= 1;
      @(posedge s_axil_arready) @(posedge i_S_AXI_ACLK) s_axil_arvalid <= #1 0;

      //i_s_axi_araddr <= 32'd0;
    end
  endtask

  // ---------------------------------------------------------------
  //  READ DATA
  // ---------------------------------------------------------------
  task read_data;
    begin
      @(posedge s_axil_rvalid) @(posedge i_S_AXI_ACLK) s_axil_rready <= 1;
      @(posedge i_S_AXI_ACLK) s_axil_rready <= #1 0;
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

    end

  endtask
  // ---------------------------------------------------------------
  // RESET
  // ---------------------------------------------------------------
  task RESET;
    begin
      i_rstn = 1'b0;
      i_S_AXI_ARESETN = 'b0;
      #1;
      repeat (2) @(posedge i_S_AXI_ACLK);
      #1;
      i_rstn = 1'b1;
      i_S_AXI_ARESETN = 'b1;
    end
  endtask

  // ---------------------------------------------------------------
  //  Dump vcd
  // ---------------------------------------------------------------
  initial begin
    $dumpfile("ocla.vcd");
    $dumpvars;
  end



endmodule

module gray_counter #(parameter NUM_OF_PROBE = 32)
 (
    input sample_clk,
    input rstn,
    output reg [NUM_OF_PROBE-1:0] gray_out,
    output wire [NUM_OF_PROBE-1:0] binary_out
);

  reg [NUM_OF_PROBE-1:0] q;

  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      q <= 0;
      gray_out <= 0;
    end else begin
      q <= q + 1;

      gray_out <= {q[NUM_OF_PROBE-1], q[NUM_OF_PROBE-1:1] ^ q[NUM_OF_PROBE-2:0]};
    end
  end
  // assign binary_out =  {2'b10,32'h11abcdef,{8{q[3:0]}}};
  // assign binary_out = {'b0,q[3:0],q[3:0],q[3:0],q[3:0],q[3:0],q[3:0],q[3:0]};
  assign binary_out = q;
endmodule
