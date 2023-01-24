/* verilator lint_off EOFNEWLINE */

`timescale 1ns / 1ps

module eio_tb;

  // Parameters
 `define AXI_DATA_WIDTH 32
 localparam NUM_OF_PROBE = 8;
  // Ports
  reg                            i_S_AXI_ACLK    = 0;
  reg                            i_S_AXI_ARESETN = 1;
  reg                            i_sample_clk    = 0;
  reg                            i_rstn          = 0;
  reg                            s_axil_awvalid  = 0;
  wire                           s_axil_awready;
  reg      [`AXI_DATA_WIDTH-1:0] s_axil_awaddr   = 0;
  reg                      [2:0] s_axil_awprot   = 0;
  reg                            s_axil_wvalid   = 0;
  wire                           s_axil_wready;
  reg      [`AXI_DATA_WIDTH-1:0] s_axil_wdata    = 0;
  reg  [(`AXI_DATA_WIDTH/8)-1:0] s_axil_wstrb    = 0;
  wire                           s_axil_bvalid;
  reg                            s_axil_bready   = 0;
  wire                     [1:0] s_axil_bresp;
  reg                            s_axil_arvalid  = 0;
  wire                           s_axil_arready;
  reg      [`AXI_DATA_WIDTH-1:0] s_axil_araddr   = 0;
  reg                      [2:0] s_axil_arprot   = 0;
  wire                           s_axil_rvalid;
  reg                            s_axil_rready   = 0;
  wire                     [1:0] s_axil_rresp;
  wire   [`AXI_DATA_WIDTH-1 : 0] s_axil_rdata;
  //reg [23:0] i_probes;

  reg   [NUM_OF_PROBE-1 : 0] input_probes = 128'h11223344556677889900aabbccddeeff;
  wire  [NUM_OF_PROBE-1 : 0] output_probes;

  reg ipclk = 0, opclk = 0;
  reg [`AXI_DATA_WIDTH-1 : 0] data_axi = `AXI_DATA_WIDTH'h0000000000000000;
  reg [`AXI_DATA_WIDTH-1 : 0] addr_axi = `AXI_DATA_WIDTH'h0000000000000000;
  
  // Input clock : 80 MHz (variable)
//  always #5ns   ipclk = ~ipclk;
  always #6.25ns   ipclk = ~ipclk;

  // Output clock : 125 MHz (variable)
//  always #5ns      opclk = ~opclk;
  always #4ns      opclk = ~opclk;
  
  // AXI clock : 100 MHz (variable)
  always #5ns      i_S_AXI_ACLK = ~i_S_AXI_ACLK;  

  axil_eio_wrapper  UUT    
            (
             // Global signals
             .IP_CLK        (ipclk),
             .OP_CLK        (opclk),
             .S_AXI_ACLK    (i_S_AXI_ACLK),
             .S_AXI_ARESETN (i_S_AXI_ARESETN),
             
             // AXI-L signals
             .s_axil_awaddr  (s_axil_awaddr),
             .s_axil_awprot  (s_axil_awprot),
             .s_axil_awvalid (s_axil_awvalid),
             .s_axil_awready (s_axil_awready),
             .s_axil_wdata   (s_axil_wdata),
             .s_axil_wstrb   (s_axil_wstrb),
             .s_axil_wvalid  (s_axil_wvalid),
             .s_axil_wready  (s_axil_wready),
             .s_axil_bresp   (s_axil_bresp),
             .s_axil_bvalid  (s_axil_bvalid),
             .s_axil_bready  (s_axil_bready),
             .s_axil_araddr  (s_axil_araddr),
             .s_axil_arprot  (s_axil_arprot),
             .s_axil_arvalid (s_axil_arvalid),
             .s_axil_arready (s_axil_arready),
             .s_axil_rdata   (s_axil_rdata),
             .s_axil_rresp   (s_axil_rresp),
             .s_axil_rvalid  (s_axil_rvalid),
             .s_axil_rready  (s_axil_rready),
             
             // i/o probes
             .probe_in      (input_probes),
             .probe_out     (output_probes)
            );

  initial 
  begin
    # 20
    RESET;
    #100;
    
    for (integer i=0 ; i<((NUM_OF_PROBE/`AXI_DATA_WIDTH) + ((NUM_OF_PROBE % `AXI_DATA_WIDTH) != 0)) ; i++)
    begin
        data_axi = data_axi + {`AXI_DATA_WIDTH'h1111111111111111};
        addr_axi = addr_axi + `AXI_DATA_WIDTH/8; 
        #40  axi_write_transaction(addr_axi, data_axi);
    end
    
    addr_axi = 32'h00000000;
        
    for (integer i=0 ; i<((NUM_OF_PROBE/`AXI_DATA_WIDTH) + ((NUM_OF_PROBE % `AXI_DATA_WIDTH) != 0)) ; i++)
    begin
        addr_axi = addr_axi + `AXI_DATA_WIDTH/8;
        #40  axi_read_transaction(addr_axi);
    end
       
    # 100 $finish;
  end

  // ---------------------------------------------------------------
  // AXI WRITE Transaction
  // ---------------------------------------------------------------
  task axi_write_transaction(input [31:0] awaddr, input [`AXI_DATA_WIDTH-1:0] wdata);
    begin
      fork
        write_addr(awaddr);
        write_data(wdata);
        write_resp;
      join
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
  // AXI WRITE ADDRESS
  // ---------------------------------------------------------------
  task write_addr(input [`AXI_DATA_WIDTH-1:0] awaddr);
    begin
      s_axil_awaddr  <= awaddr;
      s_axil_awprot  <= 0;
      s_axil_awvalid <= 1;
      @(posedge s_axil_awready)
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
  task write_data(input [`AXI_DATA_WIDTH-1:0] wdata);
    begin
      s_axil_wvalid <= 1;
      s_axil_wstrb  <= 8'b11111111;
      s_axil_wdata  <= wdata;
      @(posedge s_axil_wready) begin
        @(posedge i_S_AXI_ACLK) s_axil_wvalid <= 0;
        s_axil_wstrb <= 8'b0;
        s_axil_wdata <= 32'h0;
        //  repeat (2) @ (posedge axi_aclk);
      end
    end
  endtask

  // ---------------------------------------------------------------
  // AXI WRITE RESPONSE
  // ---------------------------------------------------------------
  task write_resp;
    begin
      @(posedge s_axil_bvalid)
      s_axil_bready <= 'b1;
      @(posedge i_S_AXI_ACLK) s_axil_bready <= 'b0;
    end
  endtask

  // ---------------------------------------------------------------
  //  READ ADDRESS
  // ---------------------------------------------------------------
  task read_addr(input [31:0] araddr);
    begin
      s_axil_araddr  <= araddr;

      s_axil_arvalid <= 1;
      @(posedge s_axil_arready) @(posedge i_S_AXI_ACLK) s_axil_arvalid <= 0;

      //i_s_axi_araddr <= 32'd0;
    end
  endtask

  // ---------------------------------------------------------------
  //  READ DATA
  // ---------------------------------------------------------------
  task read_data;
    begin
      @(posedge s_axil_rvalid) @(posedge i_S_AXI_ACLK) s_axil_rready <= 1;
      @(posedge i_S_AXI_ACLK) s_axil_rready <= 0;
    end
  endtask

  // ---------------------------------------------------------------
  // RESET
  // ---------------------------------------------------------------
  task RESET;
    begin
      i_rstn = 1'b0;
      i_S_AXI_ARESETN = 'b0;
      repeat (2) @(posedge i_S_AXI_ACLK);
      i_rstn = 1'b1;
      i_S_AXI_ARESETN = 'b1;
    end
  endtask

endmodule