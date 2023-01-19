/*
Top-level module for the Vexriscv SoC with AXI RAM and AXI Interconnect
*/
module vex_soc (
    input wire      reset,
    input wire      clock_1,
    input wire      clock_2
);
    wire   	      	vexriscv_dBusAxi_ar_ready;
    wire   	      	vexriscv_dBusAxi_aw_ready;
    wire    	[7:0] 	vexriscv_dBusAxi_b_payload_id;
    wire    	[1:0] 	vexriscv_dBusAxi_b_payload_resp;
    wire    	      	vexriscv_dBusAxi_b_valid;
    reg    	[31:0]	vexriscv_dBusAxi_rf_payload_data;
    wire   	[7:0] 	vexriscv_dBusAxi_r_payload_id;
    wire    	      	vexriscv_dBusAxi_r_payload_last;
    wire    	[1:0] 	vexriscv_dBusAxi_r_payload_resp;
    wire   	      	vexriscv_dBusAxi_r_valid;
    wire    	      	vexriscv_dBusAxi_w_ready;
    wire   	      	vexriscv_debugReset = 1'd0;
    wire   	      	vexriscv_externalInterrupt  = 1'd0;
    wire    	      	vexriscv_iBusAxi_ar_ready;
    wire    	[31:0]	vexriscv_iBusAxi_r_payload_data;
    wire    	[7:0] 	vexriscv_iBusAxi_r_payload_id;
    wire    	      	vexriscv_iBusAxi_r_payload_last;
    wire    	[1:0] 	vexriscv_iBusAxi_r_payload_resp;
    wire    	      	vexriscv_iBusAxi_r_valid;
    reg    	      	vexriscv_jtag_tck = 1'd0;
    reg    	      	vexriscv_jtag_tdi = 1'd0;
    reg    	      	vexriscv_jtag_tms = 1'd0;
    wire   	      	vexriscv_reset;
    wire 	[2:0] 	vexriscv_dBusAxi_ar_payload_size;
    wire 	[3:0] 	vexriscv_dBusAxi_ar_payload_qos;
    wire 	[7:0] 	vexriscv_dBusAxi_ar_payload_id;
    wire   	      	vexriscv_iBusAxi_ar_valid;
    reg    	      	vexriscv_iBusAxi_ar_first;
    reg    	      	vexriscv_iBusAxi_ar_last;
    wire 	[31:0]	vexriscv_iBusAxi_ar_payload_addr;
    wire 	[1:0] 	vexriscv_iBusAxi_ar_payload_burst;
    wire 	[7:0] 	vexriscv_iBusAxi_ar_payload_len;
    wire 	[2:0] 	vexriscv_iBusAxi_ar_payload_size;
    wire 	[1:0] 	vexriscv_iBusAxi_ar_payload_lock;
    wire 	[2:0] 	vexriscv_iBusAxi_ar_payload_prot;
    wire	[3:0] 	vexriscv_iBusAxi_ar_payload_cache;
    wire 	[3:0] 	vexriscv_iBusAxi_ar_payload_qos;
    wire   	      	vexriscv_dBusAxi_ar_valid;
    reg    	      	vexriscv_dBusAxi_ar_first;
    reg    	      	vexriscv_dBusAxi_ar_last;
    wire 	[31:0]	vexriscv_dBusAxi_ar_payload_addr;
    wire 	[1:0] 	vexriscv_dBusAxi_ar_payload_burst;
    wire 	[7:0] 	vexriscv_dBusAxi_ar_payload_len;
    wire   	      	vexriscv_dBusAxi_ar_payload_lock;
    wire 	[2:0] 	vexriscv_dBusAxi_ar_payload_prot;
    wire		[31:0]	vexriscv_dBusAxi_r_payload_data;
    wire	[3:0] 	vexriscv_dBusAxi_ar_payload_cache;
    wire	[31:0]	vexriscv_dBusAxi_aw_payload_addr;
    wire	[1:0] 	vexriscv_dBusAxi_aw_payload_burst;
    wire	[7:0] 	vexriscv_dBusAxi_aw_payload_len;
    wire	[3:0] 	vexriscv_dBusAxi_aw_payload_size;
    wire   	      	vexriscv_dBusAxi_aw_payload_lock;
    wire	[2:0] 	vexriscv_dBusAxi_aw_payload_prot;
    wire	[3:0] 	vexriscv_dBusAxi_aw_payload_cache;
    wire	[3:0] 	vexriscv_dBusAxi_aw_payload_qos;
    wire   	      	vexriscv_dBusAxi_aw_payload_id;
    wire   	      	vexriscv_dBusAxi_aw_valid;
    reg    	      	vexriscv_dBusAxi_aw_first;
    reg    	      	vexriscv_dBusAxi_aw_last;
    wire   	      	vexriscv_dBusAxi_b_ready;
    wire   	      	vexriscv_dBusAxi_r_ready;
    wire   	      	vexriscv_iBusAxi_r_ready;
    wire		[31:0]	vexriscv_dBusAxi_w_payload_data;
    wire	[31:0]	axilitesram1_dat_w;
    wire	[3:0] 	vexriscv_dBusAxi_w_payload_strb;
    wire   	      	vexriscv_dBusAxi_w_last;
    wire   	      	vexriscv_dBusAxi_w_valid;
    wire   	      	vexriscv_iBusAxi_ar_payload_id;
    wire   	      	vexriscv_jtag_tdo;
    wire	[3:0] 	vexriscv_dBusAxi_ar_payload_region;
    wire   	      	vexriscv_dBusAxi_w_payload_last;
    wire   		vexriscv_dBusAxi_aw_payload_user;
    wire		vexriscv_dBusAxi_w_payload_user;
    wire		vexriscv_dBusAxi_b_payload_user;
    wire		vexriscv_dBusAxi_ar_payload_user;
    wire		vexriscv_dBusAxi_r_payload_user;
    wire   	      	vexriscv5;
    wire   	      	vexriscv6;
    wire     	[7:0]  	axi4_m00_axi_awid;
    wire     	[31:0] 	axi4_m00_axi_awaddr;
    wire     	[7:0]   axi4_m00_axi_awlen;
    wire     	[2:0]   axi4_m00_axi_awsize;
    wire     	[1:0]   axi4_m00_axi_awburst;
    wire        	    	axi4_m00_axi_awlock;
    wire     	[3:0]   axi4_m00_axi_awcache;
    wire     	[2:0]   axi4_m00_axi_awprot;
    wire             	axi4_m00_axi_awvalid;
    wire       	     	axi4_m00_axi_awready;
    wire     	[31:0]  axi4_m00_axi_wdata;
    wire     	[3:0]   axi4_m00_axi_wstrb;
    wire      	       	axi4_m00_axi_wlast;
    wire             	axi4_m00_axi_wvalid;
    wire            	axi4_m00_axi_wready;
    wire    	[7:0]   axi4_m00_axi_bid;
    wire    	[1:0]   axi4_m00_axi_bresp;
    wire            	axi4_m00_axi_bvalid;
    wire             	axi4_m00_axi_bready;
    wire     	[7:0]   axi4_m00_axi_arid;
    wire     	[31:0]  axi4_m00_axi_araddr;
    wire     	[7:0]   axi4_m00_axi_arlen;
    wire     	[2:0]   axi4_m00_axi_arsize;
    wire     	[1:0]   axi4_m00_axi_arburst;
    wire             	axi4_m00_axi_arlock;
    wire     	[3:0]   axi4_m00_axi_arcache;
    wire     	[2:0]   axi4_m00_axi_arprot;
    wire             	axi4_m00_axi_arvalid;
    wire            	axi4_m00_axi_arready;
    wire    	[7:0]   axi4_m00_axi_rid;
    wire    	[31:0]  axi4_m00_axi_rdata;
    wire    	[1:0]   axi4_m00_axi_rresp;
    wire            	axi4_m00_axi_rlast;
    wire            	axi4_m00_axi_rvalid;
    wire             	axi4_m00_axi_rready;
    wire		axi4_m00_axi_buser;
    wire 		axi4_m00_axi_ruser;

	
//------	-Ram--	---------------    
    reg 	[7:0] 	ram_s_axi_awid; 
    reg 	[31:0]	ram_s_axi_awaddr; 
    reg 	[7:0] 	ram_s_axi_awlen; 
    reg 	[2:0] 	ram_s_axi_awsize; 
    reg 	[1:0] 	ram_s_axi_awburst; 
    reg 	      	ram_s_axi_awlock; 
    reg 	[3:0] 	ram_s_axi_awcache; 
    reg 	[2:0] 	ram_s_axi_awprot; 
    reg 	      	ram_s_axi_awvalid; 
    wire	      	ram_s_axi_awready; 
    reg 	[31:0]	ram_s_axi_wdata; 
    reg 	[3:0] 	ram_s_axi_wstrb; 
    reg 	      	ram_s_axi_wlast; 
    reg 	      	ram_s_axi_wvalid; 
    wire	      	ram_s_axi_wready; 
    wire	[7:0] 	ram_s_axi_bid; 
    wire	[1:0] 	ram_s_axi_bresp; 
    wire	      	ram_s_axi_bvalid; 
    reg 	      	ram_s_axi_bready; 
    reg 	[7:0] 	ram_s_axi_arid; 
    reg 	[31:0]	ram_s_axi_araddr; 
    reg 	[7:0] 	ram_s_axi_arlen; 
    reg 	[2:0] 	ram_s_axi_arsize; 
    reg 	[1:0] 	ram_s_axi_arburst; 
    reg 	      	ram_s_axi_arlock; 
    reg 	[3:0] 	ram_s_axi_arcache; 
    reg 	[2:0] 	ram_s_axi_arprot; 
    reg 	      	ram_s_axi_arvalid; 
    wire	      	ram_s_axi_arready; 
    wire	[7:0] 	ram_s_axi_rid; 
    wire	[31:0]	ram_s_axi_rdata; 
    wire	[1:0] 	ram_s_axi_rresp; 
    wire	      	ram_s_axi_rlast; 
    wire	      	ram_s_axi_rvalid; 

    //-----------AXI2AXILite Interconnections
    wire     	[7:0]  	fifo_awid;
    wire     	[31:0] 	fifo_awaddr;
    wire     	[7:0]   fifo_awlen;
    wire     	[2:0]   fifo_awsize;
    wire     	[1:0]   fifo_awburst;
    wire        	    fifo_awlock;
    wire     	[3:0]   fifo_awcache;
    wire     	[2:0]   fifo_awprot;
    wire             	fifo_awvalid;
    wire       	     	fifo_awready;
    wire     	[31:0]  fifo_wdata;
    wire     	[3:0]   fifo_wstrb;
    wire      	       	fifo_wlast;
    wire             	fifo_wvalid;
    wire            	fifo_wready;
    wire    	[7:0]   fifo_bid;
    wire    	[1:0]   fifo_bresp;
    wire            	fifo_bvalid;
    wire             	fifo_bready;
    wire     	[7:0]   fifo_arid;
    wire     	[31:0]  fifo_araddr;
    wire     	[7:0]   fifo_arlen;
    wire     	[2:0]   fifo_arsize;
    wire     	[1:0]   fifo_arburst;
    wire             	fifo_arlock;
    wire     	[3:0]   fifo_arcache;
    wire     	[2:0]   fifo_arprot;
    wire             	fifo_arvalid;
    wire            	fifo_arready;
    wire    	[7:0]   fifo_rid;
    wire    	[31:0]  fifo_rdata;
    wire    	[1:0]   fifo_rresp;
    wire            	fifo_rlast;
    wire            	fifo_rvalid;
    wire             	fifo_rready;
    wire		        fifo_buser;
    wire 		        fifo_ruser;


//----------------Instansiation------------//


//---------------VexRiscv----------------

VexRiscvAxi4 cpu(
	.clk					(clock_1),
	.dBusAxi_ar_ready			(vexriscv_dBusAxi_ar_ready),
	.dBusAxi_aw_ready			(vexriscv_dBusAxi_aw_ready),
	.dBusAxi_b_payload_id			(vexriscv_dBusAxi_b_payload_id),
	.dBusAxi_b_payload_resp			(vexriscv_dBusAxi_b_payload_resp),
	.dBusAxi_b_valid			(vexriscv_dBusAxi_b_valid),
	.dBusAxi_r_payload_data			(vexriscv_dBusAxi_r_payload_data),
	.dBusAxi_r_payload_id			(vexriscv_dBusAxi_r_payload_id),
	.dBusAxi_r_payload_last			(vexriscv_dBusAxi_r_payload_last),
	.dBusAxi_r_payload_resp			(vexriscv_dBusAxi_r_payload_resp),
	.dBusAxi_r_valid			(vexriscv_dBusAxi_r_valid),
	.dBusAxi_w_ready			(vexriscv_dBusAxi_w_ready),
	.debugReset				(vexriscv_debugReset),
	.externalInterrupt			(vexriscv_externalInterrupt),
	.iBusAxi_ar_ready			(vexriscv_iBusAxi_ar_ready),
	.iBusAxi_r_payload_data			(vexriscv_iBusAxi_r_payload_data),
	.iBusAxi_r_payload_id			(vexriscv_iBusAxi_r_payload_id),
	.iBusAxi_r_payload_last			(vexriscv_iBusAxi_r_payload_last),
	.iBusAxi_r_payload_resp			(vexriscv_iBusAxi_r_payload_resp),
	.iBusAxi_r_valid			(vexriscv_iBusAxi_r_valid),
	.jtag_tck				(vexriscv_jtag_tck),
	.jtag_tdi				(vexriscv_jtag_tdi),
	.jtag_tms				(vexriscv_jtag_tms),
	.reset					(reset),
	.softwareInterrupt			(1'd0),
	.timerInterrupt				(1'd0),
	.dBusAxi_ar_payload_addr		(vexriscv_dBusAxi_ar_payload_addr),
	.dBusAxi_ar_payload_burst		(vexriscv_dBusAxi_ar_payload_burst),
	.dBusAxi_ar_payload_cache		(vexriscv_dBusAxi_ar_payload_cache),
	.dBusAxi_ar_payload_id			(vexriscv_dBusAxi_ar_payload_id),
	.dBusAxi_ar_payload_len			(vexriscv_dBusAxi_ar_payload_len),
	.dBusAxi_ar_payload_lock		(vexriscv_dBusAxi_ar_payload_lock),
	.dBusAxi_ar_payload_prot		(vexriscv_dBusAxi_ar_payload_prot),
	.dBusAxi_ar_payload_qos			(vexriscv_dBusAxi_ar_payload_qos),
	.dBusAxi_ar_payload_region		(vexriscv_dBusAxi_ar_payload_region),
	.dBusAxi_ar_payload_size		(vexriscv_dBusAxi_ar_payload_size),
	.dBusAxi_ar_valid			(vexriscv_dBusAxi_ar_valid),
	.dBusAxi_aw_payload_addr		(vexriscv_dBusAxi_aw_payload_addr),
	.dBusAxi_aw_payload_burst		(vexriscv_dBusAxi_aw_payload_burst),
	.dBusAxi_aw_payload_cache		(vexriscv_dBusAxi_aw_payload_cache),
	.dBusAxi_aw_payload_id			(vexriscv_dBusAxi_aw_payload_id),
	.dBusAxi_aw_payload_len			(vexriscv_dBusAxi_aw_payload_len),
	.dBusAxi_aw_payload_lock		(vexriscv_dBusAxi_aw_payload_lock),
	.dBusAxi_aw_payload_prot		(vexriscv_dBusAxi_aw_payload_prot),
	.dBusAxi_aw_payload_qos			(vexriscv_dBusAxi_aw_payload_qos),
	.dBusAxi_aw_payload_region		(vexriscv6),
	.dBusAxi_aw_payload_size		(vexriscv_dBusAxi_aw_payload_size),
	.dBusAxi_aw_valid			(vexriscv_dBusAxi_aw_valid),
	.dBusAxi_b_ready			(vexriscv_dBusAxi_b_ready),
	.dBusAxi_r_ready			(vexriscv_dBusAxi_r_ready),
	.dBusAxi_w_payload_data			(vexriscv_dBusAxi_w_payload_data),
	.dBusAxi_w_payload_last			(vexriscv_dBusAxi_w_payload_last),
	.dBusAxi_w_payload_strb			(vexriscv_dBusAxi_w_payload_strb),
	.dBusAxi_w_valid			(vexriscv_dBusAxi_w_valid),
	.iBusAxi_ar_payload_addr		(vexriscv_iBusAxi_ar_payload_addr),
	.iBusAxi_ar_payload_burst		(vexriscv_iBusAxi_ar_payload_burst),
	.iBusAxi_ar_payload_cache		(vexriscv_iBusAxi_ar_payload_cache),
	.iBusAxi_ar_payload_id			(vexriscv_iBusAxi_ar_payload_id),
	.iBusAxi_ar_payload_len			(vexriscv_iBusAxi_ar_payload_len),
	.iBusAxi_ar_payload_lock		(vexriscv_iBusAxi_ar_payload_lock),
	.iBusAxi_ar_payload_prot		(vexriscv_iBusAxi_ar_payload_prot),
	.iBusAxi_ar_payload_qos			(vexriscv_iBusAxi_ar_payload_qos),
	.iBusAxi_ar_payload_region		(vexriscv7),
	.iBusAxi_ar_payload_size		(vexriscv_iBusAxi_ar_payload_size),
	.iBusAxi_ar_valid			(vexriscv_iBusAxi_ar_valid),
	.iBusAxi_r_ready			(vexriscv_iBusAxi_r_ready),
	.jtag_tdo				(vexriscv5),
	.debug_resetOut				(vexriscv8));

////-----------AXI_ASYNC_FIFO---------------------
//
//axi_async_fifo_wrapper fifo(
//    .s_clk                      (clock_1),
//    .s_rst                        (reset),
//    .s_axi_awvalid              (vexriscv_dBusAxi_aw_valid),
//    .s_axi_awready              (vexriscv_dBusAxi_aw_ready),
//    .s_axi_awid                 (vexriscv_dBusAxi_aw_payload_id),
//    .s_axi_awaddr               (vexriscv_dBusAxi_aw_payload_addr),
//    .s_axi_awlen                (vexriscv_dBusAxi_aw_payload_len),
//    .s_axi_awsize               (vexriscv_dBusAxi_aw_payload_size),
//    .s_axi_awburst              (vexriscv_dBusAxi_aw_payload_burst),
//    .s_axi_awlock               (vexriscv_dBusAxi_aw_payload_lock),
//    .s_axi_awcache              (vexriscv_dBusAxi_aw_payload_cache),
//    .s_axi_awprot               (vexriscv_dBusAxi_aw_payload_prot),
//    .s_axi_awqos                (vexriscv_dBusAxi_aw_payload_qos),
//    .s_axi_wvalid               (vexriscv_dBusAxi_w_valid),
//    .s_axi_wready               (vexriscv_dBusAxi_w_ready),
//    .s_axi_wdata                (vexriscv_dBusAxi_w_payload_data),
//    .s_axi_wstrb                (vexriscv_dBusAxi_w_payload_strb),
//    .s_axi_wlast                (vexriscv_dBusAxi_w_payload_last),
//    .s_axi_bvalid               (vexriscv_dBusAxi_b_valid),
//    .s_axi_bready               (vexriscv_dBusAxi_b_ready),
//    .s_axi_bid                  (vexriscv_dBusAxi_b_payload_id),
//    .s_axi_bresp                (vexriscv_dBusAxi_b_payload_resp),
//    .s_axi_arvalid              (vexriscv_dBusAxi_ar_valid),
//    .s_axi_arready              (vexriscv_dBusAxi_ar_ready),
//    .s_axi_arid                 (vexriscv_dBusAxi_ar_payload_id),
//    .s_axi_araddr               (vexriscv_dBusAxi_ar_payload_addr),
//    .s_axi_arlen                (vexriscv_dBusAxi_ar_payload_len),
//    .s_axi_arsize               (vexriscv_dBusAxi_ar_payload_size),
//    .s_axi_arburst              (vexriscv_dBusAxi_ar_payload_burst),
//    .s_axi_arlock               (vexriscv_dBusAxi_ar_payload_lock),
//    .s_axi_arcache              (vexriscv_dBusAxi_ar_payload_cache),
//    .s_axi_arprot               (vexriscv_dBusAxi_ar_payload_prot),
//    .s_axi_arqos                (vexriscv_dBusAxi_ar_payload_qos),
//    .s_axi_rvalid               (vexriscv_dBusAxi_r_valid),
//    .s_axi_rready               (vexriscv_dBusAxi_r_ready),
//    .s_axi_rid                  (vexriscv_dBusAxi_r_payload_id),
//    .s_axi_rdata                (vexriscv_dBusAxi_r_payload_data),
//    .s_axi_rresp                (vexriscv_dBusAxi_r_payload_resp),
//    .s_axi_rlast                (vexriscv_dBusAxi_r_payload_last),
//    //----------AXI4 Lite
//    
//    .m_clk                      (clock_1),
//    .m_rst                      (reset),    
//    .m_axi_awid                 (fifo_awid),
//    .m_axi_awprot               (fifo_awprot),
//    .m_axi_wvalid               (fifo_wvalid),
//    .m_axi_wready               (fifo_wready),
//    .m_axi_wdata                (fifo_wdata),
//    .m_axi_wstrb                (fifo_wstrb),
//    .m_axi_bvalid               (fifo_bvalid),
//    .m_axi_bready               (fifo_bready),
//    .m_axi_bresp                (fifo_bresp),
//    .m_axi_arvalid              (fifo_arvalid),
//    .m_axi_arready              (fifo_arready),
//    .m_axi_araddr               (fifo_araddr),
//    .m_axi_arprot               (fifo_arprot),
//    .m_axi_rvalid               (fifo_rvalid),
//    .m_axi_rready               (fifo_rready),
//    .m_axi_rdata                (fifo_rdata),
//    .m_axi_rresp                (fifo_rresp),
//    .m_axi_awaddr               (fifo_awaddr),
//    .m_axi_awprot               (fifo_awprot),
//    .m_axi_awvalid              (fifo_awvalid),
//    .m_axi_awready              (fifo_awready),
//    .m_axi_wdata                (fifo_wdata),
//    .m_axi_wstrb                (fifo_wstrb),
//    .m_axi_wvalid               (fifo_wvalid),
//    .m_axi_wready               (fifo_wready),
//    .m_axi_bresp                (fifo_bresp),
//    .m_axi_bvalid               (fifo_bvalid),
//    .m_axi_bready               (fifo_bready),
//    .m_axi_araddr               (fifo_araddr),
//    .m_axi_arprot               (fifo_arprot),
//    .m_axi_arvalid              (fifo_arvalid),
//    .m_axi_arready              (fifo_arready),
//    .m_axi_rvalid               (fifo_rvalid),
//    .m_axi_rready               (fifo_rready),
//    .m_axi_rdata                (fifo_rdata),
//    .m_axi_rresp                (fifo_rresp));
//


axi_cdc fifo(
    .S_AXI_ACLK                      (clock_1),
    .S_AXI_ARESETN                        (reset),
    .S_AXI_AWVALID              (vexriscv_dBusAxi_aw_valid),
    .S_AXI_AWREADY              (vexriscv_dBusAxi_aw_ready),
    .S_AXI_AWID                 (vexriscv_dBusAxi_aw_payload_id),
    .S_AXI_AWADDR               (vexriscv_dBusAxi_aw_payload_addr),
    .S_AXI_AWLEN                (vexriscv_dBusAxi_aw_payload_len),
    .S_AXI_AWSIZE               (vexriscv_dBusAxi_aw_payload_size),
    .S_AXI_AWBURST              (vexriscv_dBusAxi_aw_payload_burst),
    .S_AXI_AWLOCK               (vexriscv_dBusAxi_aw_payload_lock),
    .S_AXI_AWCACHE              (vexriscv_dBusAxi_aw_payload_cache),
    .S_AXI_AWPROT               (vexriscv_dBusAxi_aw_payload_prot),
    .S_AXI_AWQOS                (vexriscv_dBusAxi_aw_payload_qos),
    .S_AXI_WVALID               (vexriscv_dBusAxi_w_valid),
    .S_AXI_WREADY               (vexriscv_dBusAxi_w_ready),
    .S_AXI_WDATA                (vexriscv_dBusAxi_w_payload_data),
    .S_AXI_WSTRB                (vexriscv_dBusAxi_w_payload_strb),
    .S_AXI_WLAST                (vexriscv_dBusAxi_w_payload_last),
    .S_AXI_BVALID               (vexriscv_dBusAxi_b_valid),
    .S_AXI_BREADY               (vexriscv_dBusAxi_b_ready),
    .S_AXI_BID                  (vexriscv_dBusAxi_b_payload_id),
    .S_AXI_BRESP                (vexriscv_dBusAxi_b_payload_resp),
    .S_AXI_ARVALID              (vexriscv_dBusAxi_ar_valid),
    .S_AXI_ARREADY              (vexriscv_dBusAxi_ar_ready),
    .S_AXI_ARID                 (vexriscv_dBusAxi_ar_payload_id),
    .S_AXI_ARADDR               (vexriscv_dBusAxi_ar_payload_addr),
    .S_AXI_ARLEN                (vexriscv_dBusAxi_ar_payload_len),
    .S_AXI_ARSIZE               (vexriscv_dBusAxi_ar_payload_size),
    .S_AXI_ARBURST              (vexriscv_dBusAxi_ar_payload_burst),
    .S_AXI_ARLOCK               (vexriscv_dBusAxi_ar_payload_lock),
    .S_AXI_ARCACHE              (vexriscv_dBusAxi_ar_payload_cache),
    .S_AXI_ARPROT               (vexriscv_dBusAxi_ar_payload_prot),
    .S_AXI_ARQOS                (vexriscv_dBusAxi_ar_payload_qos),
    .S_AXI_RVALID               (vexriscv_dBusAxi_r_valid),
    .S_AXI_RREADY               (vexriscv_dBusAxi_r_ready),
    .S_AXI_RID                  (vexriscv_dBusAxi_r_payload_id),
    .S_AXI_RDATA                (vexriscv_dBusAxi_r_payload_data),
    .S_AXI_RRESP                (vexriscv_dBusAxi_r_payload_resp),
    .S_AXI_RLAST                (vexriscv_dBusAxi_r_payload_last),
    //----------AXI4 Lite
    
    .M_AXI_ACLK                      (clock_2),
    .M_AXI_ARESETN                      (reset),    
    .M_AXI_AWID                 (fifo_awid),
    .M_AXI_AWPROT               (fifo_awprot),
    .M_AXI_WVALID               (fifo_wvalid),
    .M_AXI_WREADY               (fifo_wready),
    .M_AXI_WDATA                (fifo_wdata),
    .M_AXI_WSTRB                (fifo_wstrb),
    .M_AXI_BVALID               (fifo_bvalid),
    .M_AXI_BREADY               (fifo_bready),
    .M_AXI_BRESP                (fifo_bresp),
    .M_AXI_ARVALID              (fifo_arvalid),
    .M_AXI_ARREADY              (fifo_arready),
    .M_AXI_ARADDR               (fifo_araddr),
    .M_AXI_ARPROT               (fifo_arprot),
    .M_AXI_RVALID               (fifo_rvalid),
    .M_AXI_RREADY               (fifo_rready),
    .M_AXI_RDATA                (fifo_rdata),
    .M_AXI_RRESP                (fifo_rresp),
    .M_AXI_AWADDR               (fifo_awaddr),
    .M_AXI_AWPROT               (fifo_awprot),
    .M_AXI_AWVALID              (fifo_awvalid),
    .M_AXI_AWREADY              (fifo_awready),
    .M_AXI_WDATA                (fifo_wdata),
    .M_AXI_WSTRB                (fifo_wstrb),
    .M_AXI_WVALID               (fifo_wvalid),
    .M_AXI_WREADY               (fifo_wready),
    .M_AXI_BRESP                (fifo_bresp),
    .M_AXI_BVALID               (fifo_bvalid),
    .M_AXI_BREADY               (fifo_bready),
    .M_AXI_ARADDR               (fifo_araddr),
    .M_AXI_ARPROT               (fifo_arprot),
    .M_AXI_ARVALID              (fifo_arvalid),
    .M_AXI_ARREADY              (fifo_arready),
    .M_AXI_RVALID               (fifo_rvalid),
    .M_AXI_RREADY               (fifo_rready),
    .M_AXI_RDATA                (fifo_rdata),
    .M_AXI_RRESP                (fifo_rresp));

axi_ram ram_inst(
    .clk					    (clock_1),
    .rst					    (reset),
    .s_axi_awid					(ram_s_axi_awid),
    .s_axi_awaddr				(ram_s_axi_awaddr),
    .s_axi_awlen				(ram_s_axi_awlen),
    .s_axi_awsize				(ram_s_axi_awsize),
    .s_axi_awburst				(ram_s_axi_awburst),
    .s_axi_awlock				(ram_s_axi_awlock),
    .s_axi_awcache				(ram_s_axi_awcache),
    .s_axi_awprot				(ram_s_axi_awprot),
    .s_axi_awvalid				(ram_s_axi_awvalid),
    .s_axi_awready				(ram_s_axi_awready),
    .s_axi_wdata				(ram_s_axi_wdata),
    .s_axi_wstrb				(ram_s_axi_wstrb),
    .s_axi_wlast				(ram_s_axi_wlast),
    .s_axi_wvalid				(ram_s_axi_wvalid),
    .s_axi_wready				(ram_s_axi_wready),
    .s_axi_bid					(ram_s_axi_bid),
    .s_axi_bresp				(ram_s_axi_bresp),
    .s_axi_bvalid				(ram_s_axi_bvalid),
    .s_axi_bready				(ram_s_axi_bready),
    .s_axi_arid					(vexriscv_iBusAxi_ar_payload_id),
    .s_axi_araddr				(vexriscv_iBusAxi_ar_payload_addr),
    .s_axi_arlen				(vexriscv_iBusAxi_ar_payload_len),
    .s_axi_arsize				(vexriscv_iBusAxi_ar_payload_size),
    .s_axi_arburst				(vexriscv_iBusAxi_ar_payload_burst),
    .s_axi_arlock				(vexriscv_iBusAxi_ar_payload_lock),
    .s_axi_arcache				(vexriscv_iBusAxi_ar_payload_cache),
    .s_axi_arprot				(vexriscv_iBusAxi_ar_payload_prot),
    .s_axi_arvalid				(vexriscv_iBusAxi_ar_valid),
    .s_axi_arready				(vexriscv_iBusAxi_ar_ready),
    .s_axi_rid					(vexriscv_iBusAxi_r_payload_id),
    .s_axi_rdata				(vexriscv_iBusAxi_r_payload_data),
    .s_axi_rresp				(vexriscv_iBusAxi_r_payload_resp),
    .s_axi_rlast				(vexriscv_iBusAxi_r_payload_last),
    .s_axi_rvalid				(vexriscv_iBusAxi_r_valid),
    .s_axi_rready				(vexriscv_iBusAxi_r_ready));

//-----------Peripheral AXI RAM---------------

axi_ram_per ram_periph(
    .clk					    (clock_1),
    .rst					    (reset),
    .s_axi_awid					(fifo_awid),
    .s_axi_awaddr				(fifo_awaddr),
    .s_axi_awlen				(fifo_awlen),
    .s_axi_awsize				(fifo_awsize),
    .s_axi_awburst				(fifo_awburst),
    .s_axi_awlock				(fifo_awlock),
    .s_axi_awcache				(fifo_awcache),
    .s_axi_awprot				(fifo_awprot),
    .s_axi_awvalid				(fifo_awvalid),
    .s_axi_awready				(fifo_awready),
    .s_axi_wdata				(fifo_wdata),
    .s_axi_wstrb				(fifo_wstrb),
    .s_axi_wlast				(fifo_wlast),
    .s_axi_wvalid				(fifo_wvalid),
    .s_axi_wready				(fifo_wready),
    .s_axi_bid					(fifo_bid),
    .s_axi_bresp				(fifo_bresp),
    .s_axi_bvalid				(fifo_bvalid),
    .s_axi_bready				(fifo_bready),
    .s_axi_arid					(fifo_arid),
    .s_axi_araddr				(fifo_araddr),
    .s_axi_arlen				(fifo_arlen),
    .s_axi_arsize				(fifo_arsize),
    .s_axi_arburst				(fifo_arburst),
    .s_axi_arlock				(fifo_arlock),
    .s_axi_arcache				(fifo_arcache),
    .s_axi_arprot				(fifo_arprot),
    .s_axi_arvalid				(fifo_arvalid),
    .s_axi_arready				(fifo_arready),
    .s_axi_rid					(fifo_rid),
    .s_axi_rdata				(fifo_rdata),
    .s_axi_rresp				(fifo_rresp),
    .s_axi_rlast				(fifo_rlast),
    .s_axi_rvalid				(fifo_rvalid),
    .s_axi_rready				(fifo_rready));

endmodule
