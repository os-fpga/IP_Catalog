
////////////////////////////////////////////////
`default_nettype	wire




module ocla_debug_subsystem #(

    /**********************IP Special Parameters*******************/

    parameter  IP_TYPE               = "OCLA",
    parameter  IP_VERSION            = 32'h1,
    parameter  IP_ID                 = 32'h3881734,

    /*************************************************************/

    parameter  Mode                  = "NATIVE",     // NATIVE, AXI, NATIVE_AXI
    parameter  Axi_Type              = "AXI4" ,      // AXI4, AXILite
    parameter  No_AXI_Bus            = 1,            // Total number of AXI bus:   Range (1 ----->  4)
    parameter  EIO_Enable            = 1,            // EIO Enable = 1 --------  EIO Disable = 0
    parameter  Sampling_Clk          = "SINGLE",     // SINGLE, MULTIPLE
    parameter  Cores                 = 1,            // Number of OCLA Core used

    parameter  No_Probes             = 4'd5,         // Total Number of Probes: Range (1 ----->  15)
    parameter  Probes_Sum            = 14'd1,        // Total probes width
    parameter  Mem_Depth             = 11'd512,      // Buffer size

    /**********************Width of each probe*******************/
    parameter  Probe01_Width         = 11'd0,
    parameter  Probe02_Width         = 11'd0,
    parameter  Probe03_Width         = 11'd0,
    parameter  Probe04_Width         = 11'd0,
    parameter  Probe05_Width         = 11'd0,
    parameter  Probe06_Width         = 11'd0,
    parameter  Probe07_Width         = 11'd0,
    parameter  Probe08_Width         = 11'd0,
    parameter  Probe09_Width         = 11'd0,
    parameter  Probe10_Width         = 11'd0,
    parameter  Probe11_Width         = 11'd0,
    parameter  Probe12_Width         = 11'd0,
    parameter  Probe13_Width         = 11'd0,
    parameter  Probe14_Width         = 11'd0,
    parameter  Probe15_Width         = 11'd0 ,

    /*************************EIO IP Base Address**************************/

    parameter EIO_BaseAddress        = 32'h01000000,

    /*************************AXI Core Base Address************************/

    parameter AXI_Core_BaseAddress   = 32'h01000000,

    /************************* Native Cores Base Addresses******************/

    parameter IF01_BaseAddress        = 32'h01000000,
    parameter IF02_BaseAddress        = 32'h01000000,
    parameter IF03_BaseAddress        = 32'h01000000,
    parameter IF04_BaseAddress        = 32'h01000000,
    parameter IF05_BaseAddress        = 32'h01000000,
    parameter IF06_BaseAddress        = 32'h01000000,
    parameter IF07_BaseAddress        = 32'h01000000,
    parameter IF08_BaseAddress        = 32'h01000000,
    parameter IF09_BaseAddress        = 32'h01000000,
    parameter IF10_BaseAddress        = 32'h01000000,
    parameter IF11_BaseAddress        = 32'h01000000,
    parameter IF12_BaseAddress        = 32'h01000000,
    parameter IF13_BaseAddress        = 32'h01000000,
    parameter IF14_BaseAddress        = 32'h01000000,
    parameter IF15_BaseAddress        = 32'h01000000,

    /************ Holding Probes information of each Interface**************/

    parameter  IF01_Probes            = 64'h0000000000000000,
    parameter  IF02_Probes            = 64'h0000000000000000,
    parameter  IF03_Probes            = 64'h0000000000000000,
    parameter  IF04_Probes            = 64'h0000000000000000,
    parameter  IF05_Probes            = 64'h0000000000000000,
    parameter  IF06_Probes            = 64'h0000000000000000,
    parameter  IF07_Probes            = 64'h0000000000000000,
    parameter  IF08_Probes            = 64'h0000000000000000,
    parameter  IF09_Probes            = 64'h0000000000000000,
    parameter  IF10_Probes            = 64'h0000000000000000,
    parameter  IF11_Probes            = 64'h0000000000000000,
    parameter  IF12_Probes            = 64'h0000000000000000,
    parameter  IF13_Probes            = 64'h0000000000000000,
    parameter  IF14_Probes            = 64'h0000000000000000,
    parameter  IF15_Probes            = 64'h0000000000000000,

    /*******************EIO Prameter********************/

    parameter Input_Probe_Width       = 10'd32,
    parameter Output_Probe_Width      = 10'd32,
    parameter AXI_IN_CLOCKS_SYNCED    = 0,
    parameter AXI_OUT_CLOCKS_SYNCED   = 0


  )
  (
    input  wire                                RESETn,
    input  wire                                eio_ip_clk,
    input  wire                                eio_op_clk,
    input  wire                                ACLK,

`ifdef single_sample_clock
    input  wire [Cores          -     1 : 0]   native_sampling_clk,
`else
    input  wire                                native_sampling_clk,
`endif

    input  wire                                axi_sampling_clk,
    input  wire                                jtag_tck,
    input  wire                                jtag_tms,
    input  wire                                jtag_tdi,
    output wire                                jtag_tdo,
    input  wire                                jtag_trst,

    input  wire [Probes_Sum     -     1 : 0]   probes,
    input  wire [No_AXI_Bus*250 -     1 : 0]   axi4_probes,
    input  wire [No_AXI_Bus*152 -     1 : 0]   axiLite_probes,


    input  wire [Input_Probe_Width  - 1 : 0]    probes_in,
    output wire [Output_Probe_Width - 1 : 0]    probes_out

  );


  localparam AXI_TOATAL_PROBES = (Axi_Type == "AXI4") ? No_AXI_Bus *250 : No_AXI_Bus * 152;

  localparam M_Count    = (Mode == "NATIVE") ? Cores +2 : Cores + 1;
  localparam m_count    = (Mode == "NATIVE") ? Cores : Cores - 1;


  localparam Data_Width = 32;
  localparam Addr_Width = 32;
  localparam STRB_WIDTH = (Data_Width/8);

  localparam OCLA_COUNT     = (Mode == "NATIVE_AXI")? Cores-1 :Cores;

  localparam [960-1:0]IF_Probes   = {IF15_Probes,IF14_Probes,IF13_Probes,IF12_Probes,IF11_Probes,IF10_Probes,IF09_Probes,IF08_Probes,IF07_Probes,IF06_Probes,IF05_Probes,IF04_Probes,IF03_Probes,IF02_Probes,IF01_Probes};
  localparam [165-1:0]Probes_Size = {Probe15_Width,Probe14_Width,Probe13_Width,Probe12_Width,Probe11_Width,Probe10_Width,Probe09_Width,Probe08_Width,Probe07_Width,Probe06_Width,Probe05_Width,Probe04_Width,Probe03_Width,Probe02_Width,Probe01_Width};

  localparam [543 : 0]InterconnectBaseAddress0 = {IF15_BaseAddress,IF14_BaseAddress,IF13_BaseAddress,IF12_BaseAddress,IF11_BaseAddress,IF10_BaseAddress,IF09_BaseAddress,IF08_BaseAddress,IF07_BaseAddress,IF06_BaseAddress,IF05_BaseAddress,IF04_BaseAddress,IF03_BaseAddress,IF02_BaseAddress,IF01_BaseAddress,AXI_Core_BaseAddress,EIO_BaseAddress};
  localparam [543 : 0]InterconnectBaseAddress1 = {IF15_BaseAddress,IF14_BaseAddress,IF13_BaseAddress,IF12_BaseAddress,IF11_BaseAddress,IF10_BaseAddress,IF09_BaseAddress,IF08_BaseAddress,IF07_BaseAddress,IF06_BaseAddress,IF05_BaseAddress,IF04_BaseAddress,IF03_BaseAddress,IF02_BaseAddress,IF01_BaseAddress,AXI_Core_BaseAddress,32'h010000000};
  localparam [543 : 0]InterconnectBaseAddress  = (EIO_Enable == 1) ? InterconnectBaseAddress0 : InterconnectBaseAddress1;
  // initial
  // begin
  //   $display("M_Count = %0d",M_Count );
  //   $display("Base Addresses are = %0x",InterconnectBaseAddress );
  //   $display("AXI_TOATAL_PROBES = %0d",AXI_TOATAL_PROBES );
  //   $display("OCLA_COUNT = %0d",OCLA_COUNT );
  // end

  //---------- Total no of Probes for each OCLA Core ----------------------//

  function [240-1:0] ProbesNo (input [31:0] dummy);
    integer i,j,k;
    reg [64-1:0] IF_NO ;
    reg [4-1:0] PROBE_NO ;
    reg [16-1:0] PROBE_SIZE;
    reg [16-1:0] TOTAL_PROBE_SIZE;

    begin
      ProbesNo    = 0;
      IF_NO       = 0;
      PROBE_NO    = 0;
      PROBE_SIZE  = 0;
      TOTAL_PROBE_SIZE  = 0;
      for (i = 0; i < 15; i = i + 1)
      begin
        IF_NO = IF_Probes[i*64 +: 64];
        for (j = 0; j < 16; j = j + 1)
        begin
          PROBE_NO = IF_NO[j*4 +: 4];
          if (PROBE_NO > 0)
          begin
            PROBE_SIZE = Probes_Size[((PROBE_NO*11)-11) +: 11];
            TOTAL_PROBE_SIZE = TOTAL_PROBE_SIZE + PROBE_SIZE;
          end
        end
        ProbesNo[i*16 +: 16] = TOTAL_PROBE_SIZE;
        TOTAL_PROBE_SIZE = 0;
      end

    end

  endfunction

  localparam [240-1:0]Probes_No = ProbesNo(0);

  //localparam [240-1:0]Probes_No = {16'd1024,16'd8,16'd4};



  //------------ Probe starting index for each OCLA Core-----------------//

  function [240-1:0] start_index(input [31:0] dummy);
    integer i,j,k;
    reg [16-1:0] PROBE_SIZE ;
    reg [16-1:0] Probes_No_Reg ;
    reg [16-1:0] Start_Index_Reg ;

    reg [240-1:0] TOTAL_PROBE_SIZE;

    begin
      start_index = 240'd0;
      PROBE_SIZE  = 16'd0;
      Probes_No_Reg = 16'd0;
      Start_Index_Reg = 16'd0; 
      for (i = 0; i < 15; i = i + 1)
      begin
        if(i==0)
          start_index[i*16 +: 16] = 0;
        else
        begin
          Probes_No_Reg = Probes_No[(i-1)*16 +: 16];
          Start_Index_Reg = start_index[(i-1)*16 +: 16];
          start_index[i*16 +: 16] = Probes_No_Reg +  Start_Index_Reg;
        end
      end

    end

  endfunction

  localparam [240-1:0] probe_start_index = start_index(0);
  //localparam [240-1:0] probe_start_index = {16'd12,16'd4,16'd0};


  //------------ Probe Ending index for each OCLA Core-----------------//

  function [240-1:0] end_index(input [31:0] dummy);
    integer i,j,k;
    reg [16-1:0] PROBE_SIZE ;
    reg [240-1:0] TOTAL_PROBE_SIZE;

    begin
      end_index = 240'd0;
      for (i = 0; i < 15; i = i + 1)
      begin

        end_index[i*16 +: 16] = Probes_No[i*16 +: 16];

      end

    end

  endfunction


  localparam [240-1:0] probe_end_index = end_index(0);
  //localparam [240-1:0] probe_end_index = {16'd1024,16'd8,16'd4};
  integer k;
  //initial
  //begin
  //  for ( k=0 ; k < 15 ; k= k+1)
  //  begin
  //    $display("No of probes = %0d",Probes_No[k*16 +: 16] );
  //  end
  //  for ( k=0 ; k < 15 ; k= k+1)
  //  begin
  //    $display("starting index= %0d",probe_start_index [k*16 +: 16]);
  //  end
  //  for ( k=0 ; k < 15 ; k= k+1)
  //  begin
  //    $display("end index = %0d",probe_end_index [k*16 +: 16]);
  //  end
  //end

  // clock signals
  wire [OCLA_COUNT-1:0] core_sampling_clk;

  // JTAG_AXI Signals
  wire                  r_m_axi_awvalid;
  wire                  r_m_axi_awready;
  wire      [31 : 0]    r_m_axi_awaddr;
  wire      [1  : 0]    r_m_axi_awburst;
  wire      [7  : 0]    r_m_axi_awlen;
  wire      [2  : 0]    r_m_axi_awsize;
  wire                  r_m_axi_awlock;
  wire      [2  : 0]    r_m_axi_awprot;
  wire      [3  : 0]    r_m_axi_awcache;
  wire      [3  : 0]    r_m_axi_awqos;
  wire      [3  : 0]    r_m_axi_awregion;
  wire      [3  : 0]    r_m_axi_awid;
  wire      [1  : 0]    r_m_axi_awuser;
  wire                  r_m_axi_wvalid;
  wire                  r_m_axi_wready;
  wire                  r_m_axi_wlast;
  wire      [31 : 0]    r_m_axi_wdata;
  wire      [3  : 0]    r_m_axi_wstrb;
  wire      [1  : 0]    r_m_axi_wuser;
  wire                  r_m_axi_bvalid;
  wire                  r_m_axi_bready;
  wire      [1  : 0]    r_m_axi_bresp;
  wire      [3  : 0]    r_m_axi_bid;
  wire      [1  : 0]    r_m_axi_buser;
  wire                  r_m_axi_arvalid;
  wire                  r_m_axi_arready;
  wire      [31 : 0]    r_m_axi_araddr;
  wire      [1  : 0]    r_m_axi_arburst;
  wire      [7  : 0]    r_m_axi_arlen;
  wire      [2  : 0]    r_m_axi_arsize;
  wire                  r_m_axi_arlock;
  wire      [2  : 0]    r_m_axi_arprot;
  wire      [3  : 0]    r_m_axi_arcache;
  wire      [3  : 0]    r_m_axi_arqos;
  wire      [3  : 0]    r_m_axi_arregion;
  wire      [3  : 0]    r_m_axi_arid;
  wire      [1  : 0]    r_m_axi_aruser;
  wire                  r_m_axi_rvalid;
  wire                  r_m_axi_rready;
  wire                  r_m_axi_rlast;
  wire      [1  : 0]    r_m_axi_rresp;
  wire      [31 : 0]    r_m_axi_rdata;
  wire      [3  : 0]    r_m_axi_rid;
  wire      [1  : 0]    r_m_axi_ruser;


  wire                  m_axi_awvalid;
  wire                  m_axi_awready;
  wire      [31 : 0]    m_axi_awaddr;
  wire      [2  : 0]    m_axi_awprot;
  wire                  m_axi_wvalid;
  wire                  m_axi_wready;
  wire      [31 : 0]    m_axi_wdata;
  wire      [3  : 0]    m_axi_wstrb;
  wire                  m_axi_bvalid;
  wire                  m_axi_bready;
  wire      [1  : 0]    m_axi_bresp;
  wire                  m_axi_arvalid;
  wire                  m_axi_arready;
  wire      [31 : 0]    m_axi_araddr;
  wire      [2  : 0]    m_axi_arprot;
  wire                  m_axi_rvalid;
  wire                  m_axi_rready;
  wire      [1  : 0]    m_axi_rresp;
  wire      [31 : 0]    m_axi_rdata;


  //---------------------master interface signals generation----------------

  wire [m_count-1:0]             m_axil_arready;
  wire [m_count-1:0]             m_axil_awready;
  wire [m_count*2-1:0]           m_axil_bresp;
  wire [m_count-1:0]             m_axil_bvalid;
  wire [m_count*Data_Width-1:0]  m_axil_rdata;
  wire [m_count*2-1:0]           m_axil_rresp;
  wire [m_count-1:0]             m_axil_rvali;
  wire [m_count*Addr_Width-1:0]  m_axil_araddr;
  wire [m_count*3-1:0]           m_axil_arprot;
  wire [m_count-1:0]             m_axil_arvalid;
  wire [m_count*Addr_Width-1:0]  m_axil_awaddr;
  wire [m_count*3-1:0]           m_axil_awprot;
  wire [m_count-1:0]             m_axil_awvalid;
  wire [m_count-1:0]             m_axil_bready;
  wire [m_count-1:0]             m_axil_rready;
  wire [m_count*Data_Width-1:0]  m_axil_wdata;
  wire [m_count-1:0]             m_axil_wready;
  wire [m_count*STRB_WIDTH-1:0]  m_axil_wstrb;
  wire [m_count-1:0]             m_axil_wvalid;
  wire [m_count-1:0]             m_axil_rvalid;


  wire                           S_AXI_ARREADY;
  wire                           S_AXI_AWREADY;
  wire   [1  : 0]                S_AXI_BRESP;
  wire                           S_AXI_BVALID;
  wire   [31 : 0]                S_AXI_RDATA;
  wire   [1  : 0]                S_AXI_RRESP;
  wire                           S_AXI_RVALID;
  wire   [31 : 0]                S_AXI_ARADDR;
  wire   [2  : 0]                S_AXI_ARPROT;
  wire                           S_AXI_ARVALID;
  wire   [31 : 0]                S_AXI_AWADDR;
  wire   [2  : 0]                S_AXI_AWPROT;
  wire                           S_AXI_AWVALID;
  wire                           S_AXI_BREADY;
  wire                           S_AXI_RREADY;
  wire   [31 : 0]                S_AXI_WDATA;
  wire                           S_AXI_WREADY;
  wire   [3  : 0]                S_AXI_WSTRB;
  wire                           S_AXI_WVALID;

  wire   [31 : 0]                ma_axil_awaddr;
  wire   [2  : 0]                ma_axil_awprot;
  wire                           ma_axil_awvalid;
  wire                           ma_axil_awready;
  wire   [31 : 0]                ma_axil_wdata;
  wire   [3  : 0]                ma_axil_wstrb;
  wire                           ma_axil_wvalid;
  wire                           ma_axil_wready;
  wire   [1  : 0]                ma_axil_bresp;
  wire                           ma_axil_bvalid;
  wire                           ma_axil_bready;
  wire   [31 : 0]                ma_axil_araddr;
  wire   [2  : 0]                ma_axil_arprot;
  wire                           ma_axil_arvalid;
  wire                           ma_axil_arready;
  wire   [31 : 0]                ma_axil_rdata;
  wire   [1  : 0]                ma_axil_rresp;
  wire                           ma_axil_rvalid;
  wire                           ma_axil_rready;


  assign core_sampling_clk = (Sampling_Clk == "SINGLE") ? {OCLA_COUNT{native_sampling_clk}} : native_sampling_clk;

  //------------------------------------------------------------------------------
  // JTAG_AXI

  jtag_to_axi_top # (
                    .C_S_AXI_ID_WIDTH(4),
                    .C_S_AXI_DATA_WIDTH(32),
                    .C_S_AXI_ADDR_WIDTH(32),
                    .C_S_AXI_AWUSER_WIDTH(2),
                    .C_S_AXI_ARUSER_WIDTH(2),
                    .C_S_AXI_WUSER_WIDTH(2),
                    .C_S_AXI_RUSER_WIDTH(2),
                    .C_S_AXI_BUSER_WIDTH(2)
                  )
                  jtag_to_axi_top_inst (
                    .ACLK(ACLK),
                    .ARESETN(RESETn),
                    .aw_id(r_m_axi_awid),
                    .aw_addr(r_m_axi_awaddr),
                    .aw_lock(r_m_axi_awlock),
                    .aw_cache(r_m_axi_awcache),
                    .aw_prot(r_m_axi_awprot),
                    .aw_region(r_m_axi_awregion),
                    .aw_user(r_m_axi_awuser),
                    .aw_qos(r_m_axi_awqos),
                    .aw_valid(r_m_axi_awvalid),
                    .aw_ready(r_m_axi_awready),
                    .aw_burst(r_m_axi_awburst),
                    .aw_size(r_m_axi_awsize),
                    .aw_len(r_m_axi_awlen),
                    .ar_id(r_m_axi_arid),
                    .ar_addr(r_m_axi_araddr),
                    .ar_lock(r_m_axi_arlock),
                    .ar_cache(r_m_axi_arcache),
                    .ar_prot(r_m_axi_arprot),
                    .ar_region(r_m_axi_arregion),
                    .ar_user(r_m_axi_aruser),
                    .ar_qos(r_m_axi_arqos),
                    .ar_valid(r_m_axi_arvalid),
                    .ar_ready(r_m_axi_arready),
                    .ar_burst(r_m_axi_arburst),
                    .ar_size(r_m_axi_arsize),
                    .ar_len(r_m_axi_arlen),
                    .w_data(r_m_axi_wdata),
                    .w_strb(r_m_axi_wstrb),
                    .w_last(r_m_axi_wlast),
                    .w_user(r_m_axi_wuser),
                    .w_valid(r_m_axi_wvalid),
                    .w_ready(r_m_axi_wready),
                    .r_id(r_m_axi_rid),
                    .r_data(r_m_axi_rdata),
                    .r_last(r_m_axi_rlast),
                    .r_valid(r_m_axi_rvalid),
                    .r_resp(r_m_axi_rresp),
                    .r_ready(r_m_axi_rready),
                    .r_user(r_m_axi_buser),
                    .b_id(r_m_axi_bid),
                    .b_resp(r_m_axi_bresp),
                    .b_valid(r_m_axi_bvalid),
                    .b_ready(r_m_axi_bready),
                    .b_user(r_m_axi_ruser),
                    .JTAG_TCK(jtag_tck),
                    .JTAG_TMS(jtag_tms),
                    .JTAG_TDI(jtag_tdi),
                    .JTAG_TDO(jtag_tdo),
                    .JTAG_TRST(jtag_trst)
                  );


  //------------------------------------------------------------------------------
  // axi2axilite_wrapper

  axi2axilite #(
                .C_AXI_ADDR_WIDTH(32),
                .C_AXI_DATA_WIDTH(32),
                .C_AXI_ID_WIDTH(4)
              ) axi2axilite (
                .M_AXI_ARREADY(m_axi_arready),
                .M_AXI_AWREADY(m_axi_awready),
                .M_AXI_BRESP(m_axi_bresp),
                .M_AXI_BVALID(m_axi_bvalid),
                .M_AXI_RDATA(m_axi_rdata),
                .M_AXI_RRESP(m_axi_rresp),
                .M_AXI_RVALID(m_axi_rvalid),
                .M_AXI_WREADY(m_axi_wready),
                .S_AXI_ACLK(ACLK),
                .S_AXI_ARADDR(r_m_axi_araddr),
                .S_AXI_ARBURST(r_m_axi_arburst),
                .S_AXI_ARCACHE(r_m_axi_arcache),
                .S_AXI_ARESETN(RESETn),
                .S_AXI_ARID(r_m_axi_arid),
                .S_AXI_ARLEN(r_m_axi_arlen),
                .S_AXI_ARLOCK(r_m_axi_arlock),
                .S_AXI_ARPROT(r_m_axi_arprot),
                .S_AXI_ARQOS(r_m_axi_arqos),
                .S_AXI_ARSIZE(r_m_axi_arsize),
                .S_AXI_ARVALID(r_m_axi_arvalid),
                .S_AXI_AWADDR(r_m_axi_awaddr),
                .S_AXI_AWBURST(r_m_axi_awburst),
                .S_AXI_AWCACHE(r_m_axi_awcache),
                .S_AXI_AWID(r_m_axi_awid),
                .S_AXI_AWLEN(r_m_axi_awlen),
                .S_AXI_AWLOCK(r_m_axi_awlock),
                .S_AXI_AWPROT(r_m_axi_awprot),
                .S_AXI_AWQOS(r_m_axi_awqos),
                .S_AXI_AWSIZE(r_m_axi_awsize),
                .S_AXI_AWVALID(r_m_axi_awvalid),
                .S_AXI_BREADY(r_m_axi_bready),
                .S_AXI_RREADY(r_m_axi_rready),
                .S_AXI_WDATA(r_m_axi_wdata),
                .S_AXI_WLAST(r_m_axi_wlast),
                .S_AXI_WSTRB(r_m_axi_wstrb),
                .S_AXI_WVALID(r_m_axi_wvalid),
                .M_AXI_ARADDR(m_axi_araddr),
                .M_AXI_ARPROT(m_axi_arprot),
                .M_AXI_ARVALID(m_axi_arvalid),
                .M_AXI_AWADDR(m_axi_awaddr),
                .M_AXI_AWPROT(m_axi_awprot),
                .M_AXI_AWVALID(m_axi_awvalid),
                .M_AXI_BREADY(m_axi_bready),
                .M_AXI_RREADY(m_axi_rready),
                .M_AXI_WDATA(m_axi_wdata),
                .M_AXI_WSTRB(m_axi_wstrb),
                .M_AXI_WVALID(m_axi_wvalid),
                .S_AXI_ARREADY(r_m_axi_arready),
                .S_AXI_AWREADY(r_m_axi_awready),
                .S_AXI_BID(r_m_axi_bid),
                .S_AXI_BRESP(r_m_axi_bresp),
                .S_AXI_BVALID(r_m_axi_bvalid),
                .S_AXI_RDATA(r_m_axi_rdata),
                .S_AXI_RID(r_m_axi_rid),
                .S_AXI_RLAST(r_m_axi_rlast),
                .S_AXI_RRESP(r_m_axi_rresp),
                .S_AXI_RVALID(r_m_axi_rvalid),
                .S_AXI_WREADY(r_m_axi_wready)
              );

  //------------------------------------------------------------------------------
  // axil_interconnect_wrapper


  axil_interconnect #(

                      .ADDR_WIDTH(32),
                      .DATA_WIDTH(32),
                      .M_COUNT(M_Count),
                      .S_COUNT(1),
                      .M_BASE_ADDR(InterconnectBaseAddress)
                    ) axil_interconnect (
                      .clk(ACLK),
                      .m_axil_arready({m_axil_arready,ma_axil_arready,S_AXI_ARREADY}),
                      .m_axil_awready({m_axil_awready,ma_axil_awready,S_AXI_AWREADY}),
                      .m_axil_bresp  ({m_axil_bresp  ,ma_axil_bresp,S_AXI_BRESP}),
                      .m_axil_bvalid ({m_axil_bvalid ,ma_axil_bvalid,S_AXI_BVALID}),
                      .m_axil_rdata  ({m_axil_rdata  ,ma_axil_rdata,S_AXI_RDATA}),
                      .m_axil_rresp  ({m_axil_rresp  ,ma_axil_rresp,S_AXI_RRESP}),
                      .m_axil_rvalid ({m_axil_rvalid ,ma_axil_rvalid,S_AXI_RVALID}),
                      .rst(!RESETn),
                      .s_axil_araddr(m_axi_araddr),
                      .s_axil_arprot(m_axi_arprot),
                      .s_axil_arvalid(m_axi_arvalid),
                      .s_axil_awaddr(m_axi_awaddr),
                      .s_axil_awprot(m_axi_awprot),
                      .s_axil_awvalid(m_axi_awvalid),
                      .s_axil_bready(m_axi_bready),
                      .s_axil_rready(m_axi_rready),
                      .s_axil_wdata(m_axi_wdata),
                      .s_axil_wstrb(m_axi_wstrb),
                      .s_axil_wvalid(m_axi_wvalid),
                      .m_axil_araddr ({m_axil_araddr ,ma_axil_araddr,S_AXI_ARADDR}),
                      .m_axil_arprot ({m_axil_arprot ,ma_axil_arprot,S_AXI_ARPROT}),
                      .m_axil_arvalid({m_axil_arvalid,ma_axil_arvalid,S_AXI_ARVALID}),
                      .m_axil_awaddr ({m_axil_awaddr ,ma_axil_awaddr,S_AXI_AWADDR}),
                      .m_axil_awprot ({m_axil_awprot ,ma_axil_awprot,S_AXI_AWPROT}),
                      .m_axil_awvalid({m_axil_awvalid,ma_axil_awvalid,S_AXI_AWVALID}),
                      .m_axil_bready ({m_axil_bready ,ma_axil_bready,S_AXI_BREADY}),
                      .m_axil_rready ({m_axil_rready ,ma_axil_rready,S_AXI_RREADY}),
                      .m_axil_wdata  ({m_axil_wdata  ,ma_axil_wdata,S_AXI_WDATA}),
                      .m_axil_wready ({m_axil_wready ,ma_axil_wready,S_AXI_WREADY}),
                      .m_axil_wstrb  ({m_axil_wstrb  ,ma_axil_wstrb,S_AXI_WSTRB}),
                      .m_axil_wvalid ({m_axil_wvalid ,ma_axil_wvalid,S_AXI_WVALID}),
                      .s_axil_arready(m_axi_arready ),
                      .s_axil_awready(m_axi_awready ),
                      .s_axil_bresp(m_axi_bresp),
                      .s_axil_bvalid(m_axi_bvalid),
                      .s_axil_rdata(m_axi_rdata),
                      .s_axil_rresp(m_axi_rresp),
                      .s_axil_rvalid(m_axi_rvalid),
                      .s_axil_wready(m_axi_wready)
                    );




  generate
    begin
      if (Mode == "NATIVE")
      begin: OCLA_GEN_NATIVE

        genvar i;
        for (i = 0; i < OCLA_COUNT; i = i + 1)
          ocla # (
                 .IP_TYPE(IP_TYPE),
                 .IP_VERSION(IP_VERSION),
                 .IP_ID(IP_ID),
                 .NO_OF_PROBES(Probes_No[i*16 +:16]),
                 .MEM_DEPTH(Mem_Depth),
                 .AXI_DATA_WIDTH(Data_Width),
                 .AXI_ADDR_WIDTH(Addr_Width),
                 .INDEX(i)
               )
               ocla_inst (
                 .sample_clk(core_sampling_clk[i]),
                 .rstn(RESETn),
                 .S_AXI_ACLK(ACLK),
                 .S_AXI_ARESETN(RESETn),
                 .S_AXI_AWADDR(m_axil_awaddr[i*32 +:32]),
                 .S_AXI_AWPROT(m_axil_awprot[i*3 +:3]),
                 .S_AXI_AWVALID(m_axil_awvalid[i]),
                 .S_AXI_AWREADY(m_axil_awready[i]),
                 .S_AXI_WDATA(m_axil_wdata[i*32 +:32]),
                 .S_AXI_WSTRB(m_axil_wstrb[i*4 +:4]),
                 .S_AXI_WVALID(m_axil_wvalid[i]),
                 .S_AXI_WREADY(m_axil_wready[i]),
                 .S_AXI_BRESP(m_axil_bresp[i*2 +:2]),
                 .S_AXI_BVALID(m_axil_bvalid[i]),
                 .S_AXI_BREADY(m_axil_bready[i]),
                 .S_AXI_ARADDR(m_axil_araddr[i*32 +:32]),
                 .S_AXI_ARPROT(m_axil_arprot[i*3 +:3]),
                 .S_AXI_ARVALID(m_axil_arvalid[i]),
                 .S_AXI_ARREADY(m_axil_arready[i]),
                 .S_AXI_RDATA(m_axil_rdata[i*32 +:32]),
                 .S_AXI_RRESP(m_axil_rresp[i*2 +: 2]),
                 .S_AXI_RVALID(m_axil_rvalid[i]),
                 .S_AXI_RREADY(m_axil_rready[i]),
                 .probes(probes[probe_start_index[i*16 +:16] +: probe_end_index[i*16 +:16]])

               );
      end
      else if(Mode == "AXI" &&  Axi_Type  == "AXI4" )
      begin: OCLA_GEN_AXI4
        ocla # (
               .IP_TYPE(IP_TYPE),
               .IP_VERSION(IP_VERSION),
               .IP_ID(IP_ID),
               .NO_OF_PROBES(AXI_TOATAL_PROBES),
               .MEM_DEPTH(Mem_Depth),
               .AXI_DATA_WIDTH(Data_Width),
               .AXI_ADDR_WIDTH(Addr_Width),
               .INDEX(0)
             )
             ocla_inst (
               .sample_clk(axi_sampling_clk),
               .rstn(RESETn),
               .S_AXI_ACLK(ACLK),
               .S_AXI_ARESETN(RESETn),
               .S_AXI_AWADDR(ma_axil_awaddr),
               .S_AXI_AWPROT(ma_axil_awprot),
               .S_AXI_AWVALID(ma_axil_awvalid),
               .S_AXI_AWREADY(ma_axil_awready),
               .S_AXI_WDATA(ma_axil_wdata),
               .S_AXI_WSTRB(ma_axil_wstrb),
               .S_AXI_WVALID(ma_axil_wvalid),
               .S_AXI_WREADY(ma_axil_wready),
               .S_AXI_BRESP(ma_axil_bresp),
               .S_AXI_BVALID(ma_axil_bvalid),
               .S_AXI_BREADY(ma_axil_bready),
               .S_AXI_ARADDR(ma_axil_araddr),
               .S_AXI_ARPROT(ma_axil_arprot),
               .S_AXI_ARVALID(ma_axil_arvalid),
               .S_AXI_ARREADY(ma_axil_arready),
               .S_AXI_RDATA(ma_axil_rdata),
               .S_AXI_RRESP(ma_axil_rresp),
               .S_AXI_RVALID(ma_axil_rvalid),
               .S_AXI_RREADY(ma_axil_rready),
               .probes      (axi4_probes)
             );
      end
      else if(Mode == "AXI" &&  Axi_Type  == "AXILite" )
      begin: OCLA_GEN_AXILite
        ocla # (
               .IP_TYPE(IP_TYPE),
               .IP_VERSION(IP_VERSION),
               .IP_ID(IP_ID),
               .NO_OF_PROBES(AXI_TOATAL_PROBES),
               .MEM_DEPTH(Mem_Depth),
               .AXI_DATA_WIDTH(Data_Width),
               .AXI_ADDR_WIDTH(Addr_Width),
               .INDEX(0)
             )
             ocla_inst (
               .sample_clk(axi_sampling_clk),
               .rstn(RESETn),
               .S_AXI_ACLK(ACLK),
               .S_AXI_ARESETN(RESETn),
               .S_AXI_AWADDR  (ma_axil_awaddr),
               .S_AXI_AWPROT  (ma_axil_awprot),
               .S_AXI_AWVALID (ma_axil_awvalid),
               .S_AXI_AWREADY (ma_axil_awready),
               .S_AXI_WDATA   (ma_axil_wdata),
               .S_AXI_WSTRB   (ma_axil_wstrb),
               .S_AXI_WVALID  (ma_axil_wvalid),
               .S_AXI_WREADY  (ma_axil_wready),
               .S_AXI_BRESP   (ma_axil_bresp),
               .S_AXI_BVALID  (ma_axil_bvalid),
               .S_AXI_BREADY  (ma_axil_bready),
               .S_AXI_ARADDR  (ma_axil_araddr),
               .S_AXI_ARPROT  (ma_axil_arprot),
               .S_AXI_ARVALID (ma_axil_arvalid),
               .S_AXI_ARREADY (ma_axil_arready),
               .S_AXI_RDATA   (ma_axil_rdata),
               .S_AXI_RRESP   (ma_axil_rresp),
               .S_AXI_RVALID  (ma_axil_rvalid),
               .S_AXI_RREADY  (ma_axil_rready),
               .probes        (axiLite_probes)
             );
      end
      else
      begin : OCLA_GEN_NATIVE_AXI

        genvar i;
        for (i = 0; i < OCLA_COUNT; i = i + 1)
          ocla # (
                 .IP_TYPE(IP_TYPE),
                 .IP_VERSION(IP_VERSION),
                 .IP_ID(IP_ID),
                 .NO_OF_PROBES(Probes_No[i*16 +:16]),
                 .MEM_DEPTH(Mem_Depth),
                 .AXI_DATA_WIDTH(Data_Width),
                 .AXI_ADDR_WIDTH(Addr_Width),
                 .INDEX(i)
               )
               ocla_inst (
                 .sample_clk(core_sampling_clk[i]),
                 .rstn(RESETn),
                 .S_AXI_ACLK(ACLK),
                 .S_AXI_ARESETN(RESETn),
                 .S_AXI_AWADDR(m_axil_awaddr[i*32 +:32]),
                 .S_AXI_AWPROT(m_axil_awprot[i*3 +:3]),
                 .S_AXI_AWVALID(m_axil_awvalid[i]),
                 .S_AXI_AWREADY(m_axil_awready[i]),
                 .S_AXI_WDATA(m_axil_wdata[i*32 +:32]),
                 .S_AXI_WSTRB(m_axil_wstrb[i*4 +:4]),
                 .S_AXI_WVALID(m_axil_wvalid[i]),
                 .S_AXI_WREADY(m_axil_wready[i]),
                 .S_AXI_BRESP(m_axil_bresp[i*2 +:2]),
                 .S_AXI_BVALID(m_axil_bvalid[i]),
                 .S_AXI_BREADY(m_axil_bready[i]),
                 .S_AXI_ARADDR(m_axil_araddr[i*32 +:32]),
                 .S_AXI_ARPROT(m_axil_arprot[i*3 +:3]),
                 .S_AXI_ARVALID(m_axil_arvalid[i]),
                 .S_AXI_ARREADY(m_axil_arready[i]),
                 .S_AXI_RDATA(m_axil_rdata[i*32 +:32]),
                 .S_AXI_RRESP(m_axil_rresp[i*2 +: 2]),
                 .S_AXI_RVALID(m_axil_rvalid[i]),
                 .S_AXI_RREADY(m_axil_rready[i]),
                 .probes(probes[probe_start_index[i*16 +:16] +: probe_end_index[i*16 +:16]])

               );

        if(Axi_Type  == "AXILite" )
        begin: OCLA_GEN__NATIVE_AXILite
          ocla # (
                 .IP_TYPE(IP_TYPE),
                 .IP_VERSION(IP_VERSION),
                 .IP_ID(IP_ID),
                 .NO_OF_PROBES(AXI_TOATAL_PROBES),
                 .MEM_DEPTH(Mem_Depth),
                 .AXI_DATA_WIDTH(Data_Width),
                 .AXI_ADDR_WIDTH(Addr_Width),
                 .INDEX(OCLA_COUNT)
               )
               ocla_inst_Lite (
                 .sample_clk(axi_sampling_clk),
                 .rstn(RESETn),
                 .S_AXI_ACLK(ACLK),
                 .S_AXI_ARESETN(RESETn),
                 .S_AXI_AWADDR  (ma_axil_awaddr),
                 .S_AXI_AWPROT  (ma_axil_awprot),
                 .S_AXI_AWVALID (ma_axil_awvalid),
                 .S_AXI_AWREADY (ma_axil_awready),
                 .S_AXI_WDATA   (ma_axil_wdata),
                 .S_AXI_WSTRB   (ma_axil_wstrb),
                 .S_AXI_WVALID  (ma_axil_wvalid),
                 .S_AXI_WREADY  (ma_axil_wready),
                 .S_AXI_BRESP   (ma_axil_bresp),
                 .S_AXI_BVALID  (ma_axil_bvalid),
                 .S_AXI_BREADY  (ma_axil_bready),
                 .S_AXI_ARADDR  (ma_axil_araddr),
                 .S_AXI_ARPROT  (ma_axil_arprot),
                 .S_AXI_ARVALID (ma_axil_arvalid),
                 .S_AXI_ARREADY (ma_axil_arready),
                 .S_AXI_RDATA   (ma_axil_rdata),
                 .S_AXI_RRESP   (ma_axil_rresp),
                 .S_AXI_RVALID  (ma_axil_rvalid),
                 .S_AXI_RREADY  (ma_axil_rready),
                 .probes(axiLite_probes)
               );
        end
        else
        begin: OCLA_GEN__NATIVE_AXI4
          ocla # (
                 .IP_TYPE(IP_TYPE),
                 .IP_VERSION(IP_VERSION),
                 .IP_ID(IP_ID),
                 .NO_OF_PROBES(AXI_TOATAL_PROBES),
                 .MEM_DEPTH(Mem_Depth),
                 .AXI_DATA_WIDTH(Data_Width),
                 .AXI_ADDR_WIDTH(Addr_Width),
                 .INDEX(OCLA_COUNT)
               )
               ocla_inst_full (
                 .sample_clk(axi_sampling_clk),
                 .rstn(RESETn),
                 .S_AXI_ACLK(ACLK),
                 .S_AXI_ARESETN(RESETn),
                 .S_AXI_AWADDR(ma_axil_awaddr),
                 .S_AXI_AWPROT(ma_axil_awprot),
                 .S_AXI_AWVALID(ma_axil_awvalid),
                 .S_AXI_AWREADY(ma_axil_awready),
                 .S_AXI_WDATA(ma_axil_wdata),
                 .S_AXI_WSTRB(ma_axil_wstrb),
                 .S_AXI_WVALID(ma_axil_wvalid),
                 .S_AXI_WREADY(ma_axil_wready),
                 .S_AXI_BRESP(ma_axil_bresp),
                 .S_AXI_BVALID(ma_axil_bvalid),
                 .S_AXI_BREADY(ma_axil_bready),
                 .S_AXI_ARADDR(ma_axil_araddr),
                 .S_AXI_ARPROT(ma_axil_arprot),
                 .S_AXI_ARVALID(ma_axil_arvalid),
                 .S_AXI_ARREADY(ma_axil_arready),
                 .S_AXI_RDATA(ma_axil_rdata),
                 .S_AXI_RRESP(ma_axil_rresp),
                 .S_AXI_RVALID(ma_axil_rvalid),
                 .S_AXI_RREADY(ma_axil_rready),
                 .probes(axi4_probes)
               );
        end

      end
    end
  endgenerate


  generate if (EIO_Enable == 1)
    begin : EIO_GEN



      eio_top # (
                .C_S_AXI_DATA_WIDTH(Data_Width),
                .C_S_AXI_ADDR_WIDTH(32),
                .INPUT_PROBE_WIDTH(Input_Probe_Width),
                .OUTPUT_PROBE_WIDTH(Output_Probe_Width),
                .AXI_IN_CLOCKS_SYNCED(AXI_IN_CLOCKS_SYNCED),
                .AXI_OUT_CLOCKS_SYNCED(AXI_OUT_CLOCKS_SYNCED)
              )
              eio_top_inst (
                .IP_CLK(eio_ip_clk),
                .OP_CLK(eio_op_clk),
                .S_AXI_ACLK(ACLK),
                .S_AXI_ARESETN(RESETn),
                .S_AXI_AWADDR(S_AXI_AWADDR[15:0]),
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
                .S_AXI_ARADDR(S_AXI_ARADDR[15:0]),
                .S_AXI_ARPROT(S_AXI_ARPROT),
                .S_AXI_ARVALID(S_AXI_ARVALID),
                .S_AXI_ARREADY(S_AXI_ARREADY),
                .S_AXI_RDATA(S_AXI_RDATA),
                .S_AXI_RRESP(S_AXI_RRESP),
                .S_AXI_RVALID(S_AXI_RVALID),
                .S_AXI_RREADY(S_AXI_RREADY),
                .probe_in(probes_in),
                .probe_out(probes_out)
              );
    end
    /*  else
      begin : EIO_GEN
    always@(*) begin
        S_AXI_ARADDR  =   0;
        S_AXI_ARPROT  =   0;
        S_AXI_ARVALID =   0;
        S_AXI_AWADDR  =   0;
        S_AXI_AWPROT  =   0;
        S_AXI_AWVALID =   0;
        S_AXI_BREADY  =   0;
        S_AXI_RREADY  =   0;
        S_AXI_WDATA   =   0;
        S_AXI_WSTRB   =   0;
        S_AXI_WVALID  =   0;
    end
      end*/
  endgenerate

endmodule

