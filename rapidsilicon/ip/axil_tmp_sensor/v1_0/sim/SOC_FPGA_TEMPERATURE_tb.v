`timescale 1ns/1ps

module SOC_FPGA_TEMPERATURE_tb();
  // Parameters
  parameter IP_TYPE 		= "TMPS";
  parameter IP_VERSION 	= 32'h1;
  parameter IP_ID 		= 32'h5d116ae;
  parameter  C_S_AXI_DATA_WIDTH = 32;
  parameter  C_S_AXI_ADDR_WIDTH = 8;
  parameter   INITIAL_TEMPERATURE = 50;
  parameter   TEMPERATURE_FILE = "./temp.dat";

  wire [7:0] TEMPERATURE;
  wire VALID;
  wire ERROR;
  integer i=0,result_flag = 1;




  reg  i_S_AXI_ACLK = 0;
  reg  i_S_AXI_ARESETN;

  reg  [C_S_AXI_ADDR_WIDTH-1 : 0]   s_axil_araddr;
  reg                               s_axil_arvalid;
  wire                              s_axil_arready;
  wire [C_S_AXI_DATA_WIDTH-1 : 0]   s_axil_rdata;
  wire  [1 : 0]                     s_axil_rresp;
  wire                              s_axil_rvalid;
  reg                               s_axil_rready;

  axi_lite_temp_sensor # (
                          .INITIAL_TEMPERATURE(INITIAL_TEMPERATURE),
                          .TEMPERATURE_FILE(TEMPERATURE_FILE),
                          .C_S_AXI_DATA_WIDTH(C_S_AXI_DATA_WIDTH),
                          .C_S_AXI_ADDR_WIDTH(C_S_AXI_ADDR_WIDTH)
                        )
                        axi_lite_temp_sensor_inst (
                          .S_AXI_ACLK(i_S_AXI_ACLK),
                          .S_AXI_ARESETN(i_S_AXI_ARESETN),
                          .S_AXI_AWADDR(),
                          .S_AXI_AWPROT(),
                          .S_AXI_AWVALID(),
                          .S_AXI_AWREADY(),
                          .S_AXI_WDATA(),
                          .S_AXI_WSTRB(),
                          .S_AXI_WVALID(),
                          .S_AXI_WREADY(),
                          .S_AXI_BRESP(),
                          .S_AXI_BVALID(),
                          .S_AXI_BREADY(),
                          .S_AXI_ARADDR(s_axil_araddr),
                          .S_AXI_ARVALID(s_axil_arvalid),
                          .S_AXI_ARREADY(s_axil_arready),
                          .S_AXI_RDATA(s_axil_rdata),
                          .S_AXI_RRESP(s_axil_rresp),
                          .S_AXI_RVALID(s_axil_rvalid),
                          .S_AXI_RREADY(s_axil_rready)
                        );
  always #10 i_S_AXI_ACLK = !i_S_AXI_ACLK;

  reg [C_S_AXI_DATA_WIDTH - 1 : 0] compare_data [0:2];

  reg [C_S_AXI_DATA_WIDTH- 1 : 0] test_data [0:7];
  reg [31:0]araddr;
  initial
  begin
    compare_data[0] = IP_TYPE;
    compare_data[1] = IP_ID;
    compare_data[2] = IP_VERSION;
    test_data[0] = 25;
    test_data[1] = 30;
    test_data[2] = 35;
    test_data[3] = 35;
    test_data[4] = 55;
    test_data[5] = 56;
    test_data[6] = 60;
    test_data[7] = 60;

  end

  initial
  begin
    #10;
    repeat (2) @(posedge i_S_AXI_ACLK);
    RESET();
    repeat (2) @(posedge i_S_AXI_ACLK);
    #200001;


    axi_read_transaction(32'h00000000);
    if (s_axil_rdata != compare_data[0])
      result_flag = 0;
    if(result_flag == 1)
      $display("%t:    Reading IP Type                  \t Passed", $realtime);
    else
      $display("%t:    Reading IP Type                  \t Failed", $realtime);
    result_flag = 1;

    axi_read_transaction(32'h00000004);
    if (s_axil_rdata != compare_data[1])
      result_flag = 0;
    if(result_flag == 1)
      $display("%t:    Reading IP ID                    \t Passed", $realtime);
    else
      $display("%t:    Reading IP ID                    \t Failed", $realtime);
    result_flag = 1;

    axi_read_transaction(32'h00000008);
    if (s_axil_rdata != compare_data[2])
      result_flag = 0;
    if(result_flag == 1)
      $display("%t:    Reading IP Version               \t Passed", $realtime);
    else
      $display("%t:    Reading IP Version               \t Failed", $realtime);

    result_flag = 1;
    axi_read_transaction(32'h00000010);

    $monitor("%t:    TEMPERATURE                =%d", $realtime, s_axil_rdata);
    for(i = 0; i<7; i = i+ 1)
    begin
      axi_read_transaction(32'h00000014);
      if (s_axil_rdata != test_data[i])
        result_flag = 0;
    end
    if(result_flag == 1)
      $display("\n\t \t Simulation Passed");
    else
      $display("\nSimulation Failed");

    $display("\n \t Simulation Completed at %t.\n", $realtime);

    $finish;
  end


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
      @(posedge i_S_AXI_ACLK) s_axil_rready <= #1 1;
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
      i_S_AXI_ARESETN = 'b0;
      #1;
      repeat (50) @(posedge i_S_AXI_ACLK);
      #1;
      i_S_AXI_ARESETN = 'b1;
    end
  endtask


  initial
  begin
    $dumpfile("SOC_FPGA_TEMPERATURE.vcd");
    $dumpvars();
  end

  initial
    $timeformat(-9,0," ns", 5);



endmodule
