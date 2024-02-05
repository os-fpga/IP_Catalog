
`timescale 1 ns / 1 ps

module axi_lite_temp_sensor #
  (
    parameter IP_TYPE 		= "TMPS",
	  parameter IP_VERSION 	= 32'h1, 
	  parameter IP_ID 		= 32'h5d116ae,

    parameter INITIAL_TEMPERATURE = 25,
    parameter TEMPERATURE_FILE = "",
    parameter BUFFER_SIZE = 16,
    // Width of S_AXI data bus
    parameter integer C_S_AXI_DATA_WIDTH	= 32,
    // Width of S_AXI address bus
    parameter integer C_S_AXI_ADDR_WIDTH	= 4
  )
  (

    // Global Clock Signal
    input wire  S_AXI_ACLK,
    // Global Reset Signal. This Signal is Active LOW
    input wire  S_AXI_ARESETN,
    input wire [C_S_AXI_ADDR_WIDTH-1 : 0] S_AXI_AWADDR,
    input wire [2 : 0] S_AXI_AWPROT,
    input wire  S_AXI_AWVALID,
    output wire  S_AXI_AWREADY,
    input wire [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_WDATA,
    input wire [(C_S_AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
    input wire  S_AXI_WVALID,
    output wire  S_AXI_WREADY,
    output wire [1 : 0] S_AXI_BRESP,
    output wire  S_AXI_BVALID,
    input wire  S_AXI_BREADY,
    input wire [C_S_AXI_ADDR_WIDTH-1 : 0] S_AXI_ARADDR,
    input wire  S_AXI_ARVALID,
    output wire  S_AXI_ARREADY,
    output wire [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_RDATA,
    output wire [1 : 0] S_AXI_RRESP,
    output wire  S_AXI_RVALID,
    input wire  S_AXI_RREADY
  );

  // AXI4LITE signals
  reg [C_S_AXI_ADDR_WIDTH-1 : 0] 	axi_awaddr;
  reg  	axi_awready;
  reg  	axi_wready;
  reg [1 : 0] 	axi_bresp;
  reg  	axi_bvalid;
  reg [C_S_AXI_ADDR_WIDTH-1 : 0] 	axi_araddr;
  reg  	axi_arready;
  reg [C_S_AXI_DATA_WIDTH-1 : 0] 	axi_rdata;
  reg [1 : 0] 	axi_rresp;
  reg  	axi_rvalid;

  wire wr_full, rd_empty;


  localparam integer ADDR_LSB = (C_S_AXI_DATA_WIDTH/32) + 1;
  localparam integer OPT_MEM_ADDR_BITS = 2;
  //----------------------------------------------
  //-- Signals for user logic register space example
  //------------------------------------------------
  wire [8-1:0]	temperature_data;
  wire [8-1:0]	rd_data;



  wire VALID;


  reg [C_S_AXI_DATA_WIDTH-1:0]	IP_TYPE_reg;
  reg [C_S_AXI_DATA_WIDTH-1:0]	IP_VERSION_reg;
  reg [C_S_AXI_DATA_WIDTH-1:0]	IP_ID_reg;
  wire	 slv_reg_rden;
  reg [C_S_AXI_DATA_WIDTH-1:0]	 reg_data_out;
  integer	 byte_index;
  reg	 aw_en;

  // I/O Connections assignments

  assign S_AXI_AWREADY	= axi_awready;
  assign S_AXI_WREADY	= axi_wready;
  assign S_AXI_BRESP	= axi_bresp;
  assign S_AXI_BVALID	= axi_bvalid;
  assign S_AXI_ARREADY	= axi_arready;
  assign S_AXI_RDATA	= axi_rdata;
  assign S_AXI_RRESP	= axi_rresp;
  assign S_AXI_RVALID	= axi_rvalid;


  initial begin
    IP_TYPE_reg     = IP_TYPE;
    IP_ID_reg       = IP_ID;
    IP_VERSION_reg  = IP_VERSION;
  end
  // Implement axi_awready generation
  // axi_awready is asserted for one S_AXI_ACLK clock cycle when both
  // S_AXI_AWVALID and S_AXI_WVALID are asserted. axi_awready is
  // de-asserted when reset is low.

  always @( posedge S_AXI_ACLK )
  begin
    if ( S_AXI_ARESETN == 1'b0 )
    begin
      axi_awready <= 1'b0;
      aw_en <= 1'b1;
    end
    else
    begin
      if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en)
      begin
        // slave is ready to accept write address when
        // there is a valid write address and write data
        // on the write address and data bus. This design
        // expects no outstanding transactions.
        axi_awready <= 1'b1;
        aw_en <= 1'b0;
      end
      else if (S_AXI_BREADY && axi_bvalid)
      begin
        aw_en <= 1'b1;
        axi_awready <= 1'b0;
      end
      else
      begin
        axi_awready <= 1'b0;
      end
    end
  end

  // Implement axi_awaddr latching
  // This process is used to latch the address when both
  // S_AXI_AWVALID and S_AXI_WVALID are valid.

  always @( posedge S_AXI_ACLK )
  begin
    if ( S_AXI_ARESETN == 1'b0 )
    begin
      axi_awaddr <= 0;
    end
    else
    begin
      if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en)
      begin
        // Write Address latching
        axi_awaddr <= S_AXI_AWADDR;
      end
    end
  end

  // Implement axi_wready generation
  // axi_wready is asserted for one S_AXI_ACLK clock cycle when both
  // S_AXI_AWVALID and S_AXI_WVALID are asserted. axi_wready is
  // de-asserted when reset is low.

  always @( posedge S_AXI_ACLK )
  begin
    if ( S_AXI_ARESETN == 1'b0 )
    begin
      axi_wready <= 1'b0;
    end
    else
    begin
      if (~axi_wready && S_AXI_WVALID && S_AXI_AWVALID && aw_en )
      begin
        // slave is ready to accept write data when
        // there is a valid write address and write data
        // on the write address and data bus. This design
        // expects no outstanding transactions.
        axi_wready <= 1'b1;
      end
      else
      begin
        axi_wready <= 1'b0;
      end
    end
  end


  // Implement write response logic generation
  // The write response and response valid signals are asserted by the slave
  // when axi_wready, S_AXI_WVALID, axi_wready and S_AXI_WVALID are asserted.
  // This marks the acceptance of address and indicates the status of
  // write transaction.

  always @( posedge S_AXI_ACLK )
  begin
    if ( S_AXI_ARESETN == 1'b0 )
    begin
      axi_bvalid  <= 0;
      axi_bresp   <= 2'b0;
    end
    else
    begin
      if (axi_awready && S_AXI_AWVALID && ~axi_bvalid && axi_wready && S_AXI_WVALID)
      begin
        // indicates a valid write response is available
        axi_bvalid <= 1'b1;
        axi_bresp  <= 2'b0; // 'OKAY' response
      end                   // work error responses in future
      else
      begin
        if (S_AXI_BREADY && axi_bvalid)
          //check if bready is asserted while bvalid is high)
          //(there is a possibility that bready is always asserted high)
        begin
          axi_bvalid <= 1'b0;
        end
      end
    end
  end

  // Implement axi_arready generation
  // axi_arready is asserted for one S_AXI_ACLK clock cycle when
  // S_AXI_ARVALID is asserted. axi_awready is
  // de-asserted when reset (active low) is asserted.
  // The read address is also latched when S_AXI_ARVALID is
  // asserted. axi_araddr is reset to zero on reset assertion.

  always @( posedge S_AXI_ACLK )
  begin
    if ( S_AXI_ARESETN == 1'b0 )
    begin
      axi_arready <= 1'b0;
      axi_araddr  <= 32'b0;
    end
    else
    begin
      if (~axi_arready && S_AXI_ARVALID)
      begin
        // indicates that the slave has acceped the valid read address
        axi_arready <= 1'b1;
        // Read address latching
        axi_araddr  <= S_AXI_ARADDR;
      end
      else
      begin
        axi_arready <= 1'b0;
      end
    end
  end

  // Implement axi_arvalid generation
  // axi_rvalid is asserted for one S_AXI_ACLK clock cycle when both
  // S_AXI_ARVALID and axi_arready are asserted. The slave registers
  // data are available on the axi_rdata bus at this instance. The
  // assertion of axi_rvalid marks the validity of read data on the
  // bus and axi_rresp indicates the status of read transaction.axi_rvalid
  // is deasserted on reset (active low). axi_rresp and axi_rdata are
  // cleared to zero on reset (active low).
  always @( posedge S_AXI_ACLK )
  begin
    if ( S_AXI_ARESETN == 1'b0 )
    begin
      axi_rvalid <= 0;
      axi_rresp  <= 0;
    end
    else
    begin
      if (axi_arready && S_AXI_ARVALID && ~axi_rvalid & ~rd_empty)
      begin
        // Valid read data is available at the read data bus
        axi_rvalid <= 1'b1;
        axi_rresp  <= 2'b0; // 'OKAY' response
      end
      else if (axi_rvalid && S_AXI_RREADY)
      begin
        // Read data is accepted by the master
        axi_rvalid <= 1'b0;
      end
    end
  end

  // Implement memory mapped register select and read logic generation
  // Slave register read enable is asserted when valid address is available
  // and the slave is ready to accept the read address.
  assign slv_reg_rden = axi_arready & S_AXI_ARVALID & ~axi_rvalid;
  always @(*)
  begin
    // Address decoding for reading registers
    case ( axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )
      3'h0   :
        reg_data_out <= IP_TYPE_reg;
      3'h1   :
        reg_data_out <= IP_ID_reg;
      3'h2   :
        reg_data_out <= IP_VERSION_reg;
      3'h5   :
        reg_data_out <= rd_data;
      default :
        reg_data_out <= 0;
    endcase
  end

  // Output register or memory read data
  always @( posedge S_AXI_ACLK )
  begin
    if ( S_AXI_ARESETN == 1'b0 )
    begin
      axi_rdata  <= 0;
    end
    else
    begin
      // When there is a valid read address (S_AXI_ARVALID) with
      // acceptance of read address by the slave (axi_arready),
      // output the read dada
      if (slv_reg_rden )
      begin
        axi_rdata <= reg_data_out;     // register read data
      end
    end
  end
 
  wire fifo_rd = axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] == 3'h5  ? slv_reg_rden  : 1'b0;
  reg [6:0] time_counter =0;
  reg cnt_tick =0;

 // generating clock of 2us

  always @(posedge S_AXI_ACLK)
  begin
    begin
      if(time_counter == 49)
      begin
        cnt_tick = ~cnt_tick;
        time_counter <= 0;
      end
      else
        time_counter <= time_counter + 1;
    end
  end


  SOC_FPGA_TEMPERATURE # (
                         .INITIAL_TEMPERATURE(INITIAL_TEMPERATURE),
                         .TEMPERATURE_FILE(TEMPERATURE_FILE)
                       )
                       SOC_FPGA_TEMPERATURE_inst (
                         .TEMPERATURE(temperature_data),
                         .VALID(VALID),
                         .ERROR()
                       );

  afifo # (
          .ADDRSIZE(3),
          .DATASIZE(8)
        )
        afifo_inst (
          .wclk(cnt_tick),
          .wr_reset(!S_AXI_ARESETN),
          .wr(VALID),
          .wr_data(temperature_data),
          .wr_full(wr_full),
          .rclk(S_AXI_ACLK),
          .rd_reset(!S_AXI_ARESETN),
          .rd(fifo_rd ),
          .rd_data(rd_data),
          .rd_empty(rd_empty)
        );


endmodule

