///////////////////////////////////////////////////////
//  gemini_pss_wrapper.v
//  Copyright (c) 2023 Rapid Silicon
//  All Right Reserved.
///////////////////////////////////////////////////////

`timescale 1 ps / 1 ps 

module gemini_pss_wrapper (
	//Slave AHB3 Interface 0
	input	[31:0]	S_AHB3_0_HADDR,
	input	[2:0]	S_AHB3_0_HBURST,
	input			S_AHB3_0_HMASTLOCK,
	output	[3:0]	S_AHB3_0_HPROT,
	output	[31:0]	S_AHB3_0_HRDATA,
	output			S_AHB3_0_HREADY,
	output			S_AHB3_0_HRESP,
	input			S_AHB3_0_HSEL,
	input	[2:0]	S_AHB3_0_HSIZE,
	input	[1:0]	S_AHB3_0_HTRANS,
	input	[3:0]	S_AHB3_0_HWBE,
	input	[31:0]	S_AHB3_0_HWDATA,
	input			S_AHB3_0_HWRITE,
	input			S_AHB3_0_RST_N,

	//Master AXI4 Interface 0
	output	[31:0]	M_AXI4_0_ARADDR,
	output	[1:0]	M_AXI4_0_ARBURST,
	output	[3:0]	M_AXI4_0_ARCACHE,
	output	[3:0]	M_AXI4_0_ARID,
	output	[2:0]	M_AXI4_0_ARLEN,
	output			M_AXI4_0_ARLOCK,
	output	[2:0]	M_AXI4_0_ARPROT,
	input			M_AXI4_0_ARREADY,
	output	[2:0]	M_AXI4_0_ARSIZE,
	output			M_AXI4_0_ARVALID,
	output	[31:0]	M_AXI4_0_AWADDR,
	output	[1:0]	M_AXI4_0_AWBURST,
	output	[3:0]	M_AXI4_0_AWCACHE,
	output	[3:0]	M_AXI4_0_AWID,
	output	[2:0]	M_AXI4_0_AWLEN,
	output			M_AXI4_0_AWLOCK,
	output	[2:0]	M_AXI4_0_AWPROT,
	input			M_AXI4_0_AWREADY,
	output	[2:0]	M_AXI4_0_AWSIZE,
	output			M_AXI4_0_AWVALID,
	input	[3:0]	M_AXI4_0_BID,
	output			M_AXI4_0_BREADY,
	input	[1:0]	M_AXI4_0_BRESP,
	input			M_AXI4_0_BVALID,
	input	[63:0]	M_AXI4_0_RDATA,
	input	[3:0]	M_AXI4_0_RID,
	input			M_AXI4_0_RLAST,
	output			M_AXI4_0_RREADY,
	input	[1:0]	M_AXI4_0_RRESP,
	input			M_AXI4_0_RVALID,
	output	[63:0]	M_AXI4_0_WDATA,
	output			M_AXI4_0_WLAST,
	output			M_AXI4_0_WREADY,
	output	[7:0]	M_AXI4_0_WSTRB,
	output			M_AXI4_0_WVALID,
	input			M_AXI4_0_RST_N,

	//Master AXI4 Interface 1
	output	[31:0]	M_AXI4_1_ARADDR,
	output	[1:0]	M_AXI4_1_ARBURST,
	output	[3:0]	M_AXI4_1_ARCACHE,
	output	[3:0]	M_AXI4_1_ARID,
	output	[2:0]	M_AXI4_1_ARLEN,
	output			M_AXI4_1_ARLOCK,
	output	[2:0]	M_AXI4_1_ARPROT,
	input			M_AXI4_1_ARREADY,
	output	[2:0]	M_AXI4_1_ARSIZE,
	output			M_AXI4_1_ARVALID,
	output	[31:0]	M_AXI4_1_AWADDR,
	output	[1:0]	M_AXI4_1_AWBURST,
	output	[3:0]	M_AXI4_1_AWCACHE,
	output	[3:0]	M_AXI4_1_AWID,
	output	[2:0]	M_AXI4_1_AWLEN,
	output			M_AXI4_1_AWLOCK,
	output	[2:0]	M_AXI4_1_AWPROT,
	input			M_AXI4_1_AWREADY,
	output	[2:0]	M_AXI4_1_AWSIZE,
	output			M_AXI4_1_AWVALID,
	input	[3:0]	M_AXI4_1_BID,
	output			M_AXI4_1_BREADY,
	input	[1:0]	M_AXI4_1_BRESP,
	input			M_AXI4_1_BVALID,
	input	[63:0]	M_AXI4_1_RDATA,
	input	[3:0]	M_AXI4_1_RID,
	input			M_AXI4_1_RLAST,
	output			M_AXI4_1_RREADY,
	input	[1:0]	M_AXI4_1_RRESP,
	input			M_AXI4_1_RVALID,
	output	[63:0]	M_AXI4_1_WDATA,
	output			M_AXI4_1_WLAST,
	output			M_AXI4_1_WREADY,
	output	[7:0]	M_AXI4_1_WSTRB,
	output			M_AXI4_1_WVALID,
	input			M_AXI4_1_RST_N,

	//FPGA-to-SoC Interrupts
	output	[15:0]	IRQ_OUT;
	output			IRQ_OUT_RST_N,

	//SoC-to-FPGA Interrupts
	input	[15:0]	IRQ_IN,
	input			IRQ_IN_RST_N,

	//SoC-to-FPGA DMA Signals
	input	[3:0]	DMA_IN,
	//FPGA-to-Soc DMA Signals
	output	[3:0]	DMA_OUT
);

//Wires for Slave AHB3 Interface 0
wire	[31:0]	S_AHB3_0_HADDR_wire;
wire	[2:0]	S_AHB3_0_HBURST_wire;
wire			S_AHB3_0_HMASTLOCK_wire;
wire	[3:0]	S_AHB3_0_HPROT_wire;
wire	[31:0]	S_AHB3_0_HRDATA_wire;
wire			S_AHB3_0_HREADY_wire;
wire			S_AHB3_0_HRESP_wire;
wire			S_AHB3_0_HSEL_wire;
wire	[2:0]	S_AHB3_0_HSIZE_wire;
wire	[1:0]	S_AHB3_0_HTRANS_wire;
wire	[3:0]	S_AHB3_0_HWBE_wire;
wire	[31:0]	S_AHB3_0_HWDATA_wire;
wire			S_AHB3_0_HWRITE_wire;
wire			S_AHB3_0_RST_N_wire;

//Wires for Master AXI4 Interface 0
wire	[31:0]	M_AXI4_0_ARADDR_wire;
wire	[1:0]	M_AXI4_0_ARBURST_wire;
wire	[3:0]	M_AXI4_0_ARCACHE_wire;
wire	[3:0]	M_AXI4_0_ARID_wire;
wire	[2:0]	M_AXI4_0_ARLEN_wire;
wire			M_AXI4_0_ARLOCK_wire;
wire	[2:0]	M_AXI4_0_ARPROT_wire;
wire			M_AXI4_0_ARREADY_wire;
wire	[2:0]	M_AXI4_0_ARSIZE_wire;
wire			M_AXI4_0_ARVALID_wire;
wire	[31:0]	M_AXI4_0_AWADDR_wire;
wire	[1:0]	M_AXI4_0_AWBURST_wire;
wire	[3:0]	M_AXI4_0_AWCACHE_wire;
wire	[3:0]	M_AXI4_0_AWID_wire;
wire	[2:0]	M_AXI4_0_AWLEN_wire;
wire			M_AXI4_0_AWLOCK_wire;
wire	[2:0]	M_AXI4_0_AWPROT_wire;
wire			M_AXI4_0_AWREADY_wire;
wire	[2:0]	M_AXI4_0_AWSIZE_wire;
wire			M_AXI4_0_AWVALID_wire;
wire	[3:0]	M_AXI4_0_BID_wire;
wire			M_AXI4_0_BREADY_wire;
wire	[1:0]	M_AXI4_0_BRESP_wire;
wire			M_AXI4_0_BVALID_wire;
wire	[63:0]	M_AXI4_0_RDATA_wire;
wire	[3:0]	M_AXI4_0_RID_wire;
wire			M_AXI4_0_RLAST_wire;
wire			M_AXI4_0_RREADY_wire;
wire	[1:0]	M_AXI4_0_RRESP_wire;
wire			M_AXI4_0_RVALID_wire;
wire	[63:0]	M_AXI4_0_WDATA_wire;
wire			M_AXI4_0_WLAST_wire;
wire			M_AXI4_0_WREADY_wire;
wire	[7:0]	M_AXI4_0_WSTRB_wire;
wire			M_AXI4_0_WVALID_wire;
wire			M_AXI4_0_RST_N_wire;

//Wires for Master AXI4 Interface 1
wire	[31:0]	M_AXI4_1_ARADDR_wire;
wire	[1:0]	M_AXI4_1_ARBURST_wire;
wire	[3:0]	M_AXI4_1_ARCACHE_wire;
wire	[3:0]	M_AXI4_1_ARID_wire;
wire	[2:0]	M_AXI4_1_ARLEN_wire;
wire			M_AXI4_1_ARLOCK_wire;
wire	[2:0]	M_AXI4_1_ARPROT_wire;
wire			M_AXI4_1_ARREADY_wire;
wire	[2:0]	M_AXI4_1_ARSIZE_wire;
wire			M_AXI4_1_ARVALID_wire;
wire	[31:0]	M_AXI4_1_AWADDR_wire;
wire	[1:0]	M_AXI4_1_AWBURST_wire;
wire	[3:0]	M_AXI4_1_AWCACHE_wire;
wire	[3:0]	M_AXI4_1_AWID_wire;
wire	[2:0]	M_AXI4_1_AWLEN_wire;
wire			M_AXI4_1_AWLOCK_wire;
wire	[2:0]	M_AXI4_1_AWPROT_wire;
wire			M_AXI4_1_AWREADY_wire;
wire	[2:0]	M_AXI4_1_AWSIZE_wire;
wire			M_AXI4_1_AWVALID_wire;
wire	[3:0]	M_AXI4_1_BID_wire;
wire			M_AXI4_1_BREADY_wire;
wire	[1:0]	M_AXI4_1_BRESP_wire;
wire			M_AXI4_1_BVALID_wire;
wire	[63:0]	M_AXI4_1_RDATA_wire;
wire	[3:0]	M_AXI4_1_RID_wire;
wire			M_AXI4_1_RLAST_wire;
wire			M_AXI4_1_RREADY_wire;
wire	[1:0]	M_AXI4_1_RRESP_wire;
wire			M_AXI4_1_RVALID_wire;
wire	[63:0]	M_AXI4_1_WDATA_wire;
wire			M_AXI4_1_WLAST_wire;
wire			M_AXI4_1_WREADY_wire;
wire	[7:0]	M_AXI4_1_WSTRB_wire;
wire			M_AXI4_1_WVALID_wire;
wire			M_AXI4_1_RST_N_wire;

//Wires for FPGA-to-SoC Interrupts
wire	[15:0]	IRQ_OUT_wire;
wire			IRQ_OUT_RST_N_wire;

//Wires for SoC-to-FPGA Interrupts
wire	[15:0]	IRQ_IN_wire;
wire			IRQ_IN_RST_N_wire;

//Wires for SoC-to-FPGA DMA Signals
wire	[3:0]	DMA_IN_wire;

//Wires for FPGA-to-Soc DMA Signals
wire	[3:0]	DMA_OUT_wire;


//Wire assignment for Slave AHB3 Interface 0
assign	S_AHB3_0_HADDR_wire = S_AHB3_0_HADDR;
assign	S_AHB3_0_HBURST_wire = S_AHB3_0_HBURST;
assign	S_AHB3_0_HMASTLOCK_wire = S_AHB3_0_HMASTLOCK;
assign	S_AHB3_0_HPROT_wire = S_AHB3_0_HPROT;
assign	S_AHB3_0_HRDATA_wire = S_AHB3_0_HRDATA;
assign	S_AHB3_0_HREADY_wire = S_AHB3_0_HREADY;
assign	S_AHB3_0_HRESP_wire = S_AHB3_0_HRESP;
assign	S_AHB3_0_HSIZE_wire = S_AHB3_0_HSIZE;
assign	S_AHB3_0_HSIZE_wire = S_AHB3_0_HSIZE;
assign	S_AHB3_0_HTRANS_wire = S_AHB3_0_HTRANS;
assign	S_AHB3_0_HWBE_wire = S_AHB3_0_HWBE;
assign	S_AHB3_0_HWDATA_wire = S_AHB3_0_HWDATA;
assign	S_AHB3_0_HWRITE_wire = S_AHB3_0_HWRITE;
assign	S_AHB3_0_RST_N_wire = S_AHB3_0_RST_N;

//Wire assignment for Master AXI4 Interface 0
assign	M_AXI4_0_ARADDR_wire = M_AXI4_0_ARADDR;
assign	M_AXI4_0_ARBURST_wire = M_AXI4_0_ARBURST;
assign	M_AXI4_0_ARCACHE_wire = M_AXI4_0_ARCACHE_wire;
assign	M_AXI4_0_ARID_wire = M_AXI4_0_ARID;
assign	M_AXI4_0_ARLEN_wire = M_AXI4_0_ARLEN;
assign	M_AXI4_0_ARLOCK_wire = M_AXI4_0_ARLOCK;
assign	M_AXI4_0_ARPROT_wire = M_AXI4_0_ARPROT;
assign	M_AXI4_0_ARREADY_wire = M_AXI4_0_ARREADY;
assign	M_AXI4_0_ARSIZE_wire = M_AXI4_0_ARSIZE;
assign	M_AXI4_0_ARVALID_wire = M_AXI4_0_ARVALID;
assign	M_AXI4_0_AWADDR_wire = M_AXI4_0_AWADDR;
assign	M_AXI4_0_AWBURST_wire = M_AXI4_0_AWBURST;
assign	M_AXI4_0_AWCACHE_wire = M_AXI4_0_AWCACHE;
assign	M_AXI4_0_AWID_wire = M_AXI4_0_AWID;
assign	M_AXI4_0_AWLEN_wire = M_AXI4_0_AWLEN;
assign	M_AXI4_0_AWLOCK_wire = M_AXI4_0_AWLOCK;
assign	M_AXI4_0_AWPROT_wire = M_AXI4_0_AWPROT;
assign	M_AXI4_0_AWREADY_wire = M_AXI4_0_AWREADY;
assign	M_AXI4_0_AWSIZE_wire = M_AXI4_0_AWSIZE;
assign	M_AXI4_0_AWVALID_wire = M_AXI4_0_AWVALID;
assign	M_AXI4_0_BID_wire = M_AXI4_0_BID;
assign	M_AXI4_0_BREADY_wire = M_AXI4_0_BREADY;
assign	M_AXI4_0_BRESP_wire = M_AXI4_0_BRESP;
assign	M_AXI4_0_BVALID_wire = M_AXI4_0_BVALID;
assign	M_AXI4_0_RDATA_wire = M_AXI4_0_RDATA;
assign	M_AXI4_0_RID_wire = M_AXI4_0_RID;
assign	M_AXI4_0_RLAST_wire = M_AXI4_0_RLAST;
assign	M_AXI4_0_RREADY_wire = M_AXI4_0_RREADY;
assign	M_AXI4_0_RRESP_wire = M_AXI4_0_RRESP;
assign	M_AXI4_0_RVALID_wire = M_AXI4_0_RVALID;
assign	M_AXI4_0_WDATA_wire = M_AXI4_0_WDATA;
assign	M_AXI4_0_WLAST_wire = M_AXI4_0_WLAST;
assign	M_AXI4_0_WREADY_wire = M_AXI4_0_WREADY;
assign	M_AXI4_0_WSTRB_wire = M_AXI4_0_WSTRB;
assign	M_AXI4_0_WVALID_wire = M_AXI4_0_WVALID;
assign	M_AXI4_0_RST_N_wire = M_AXI4_0_RST_N;

//Wire assignment for Master AXI4 Interface 1
assign	M_AXI4_1_ARADDR_wire = M_AXI4_1_ARADDR;
assign	M_AXI4_1_ARBURST_wire = M_AXI4_1_ARBURST;
assign	M_AXI4_1_ARCACHE_wire = M_AXI4_1_ARCACHE_wire;
assign	M_AXI4_1_ARID_wire = M_AXI4_1_ARID;
assign	M_AXI4_1_ARLEN_wire = M_AXI4_1_ARLEN;
assign	M_AXI4_1_ARLOCK_wire = M_AXI4_1_ARLOCK;
assign	M_AXI4_1_ARPROT_wire = M_AXI4_1_ARPROT;
assign	M_AXI4_1_ARREADY_wire = M_AXI4_1_ARREADY;
assign	M_AXI4_1_ARSIZE_wire = M_AXI4_1_ARSIZE;
assign	M_AXI4_1_ARVALID_wire = M_AXI4_1_ARVALID;
assign	M_AXI4_1_AWADDR_wire = M_AXI4_1_AWADDR;
assign	M_AXI4_1_AWBURST_wire = M_AXI4_1_AWBURST;
assign	M_AXI4_1_AWCACHE_wire = M_AXI4_1_AWCACHE;
assign	M_AXI4_1_AWID_wire = M_AXI4_1_AWID;
assign	M_AXI4_1_AWLEN_wire = M_AXI4_1_AWLEN;
assign	M_AXI4_1_AWLOCK_wire = M_AXI4_1_AWLOCK;
assign	M_AXI4_1_AWPROT_wire = M_AXI4_1_AWPROT;
assign	M_AXI4_1_AWREADY_wire = M_AXI4_1_AWREADY;
assign	M_AXI4_1_AWSIZE_wire = M_AXI4_1_AWSIZE;
assign	M_AXI4_1_AWVALID_wire = M_AXI4_1_AWVALID;
assign	M_AXI4_1_BID_wire = M_AXI4_1_BID;
assign	M_AXI4_1_BREADY_wire = M_AXI4_1_BREADY;
assign	M_AXI4_1_BRESP_wire = M_AXI4_1_BRESP;
assign	M_AXI4_1_BVALID_wire = M_AXI4_1_BVALID;
assign	M_AXI4_1_RDATA_wire = M_AXI4_1_RDATA;
assign	M_AXI4_1_RID_wire = M_AXI4_1_RID;
assign	M_AXI4_1_RLAST_wire = M_AXI4_1_RLAST;
assign	M_AXI4_1_RREADY_wire = M_AXI4_1_RREADY;
assign	M_AXI4_1_RRESP_wire = M_AXI4_1_RRESP;
assign	M_AXI4_1_RVALID_wire = M_AXI4_1_RVALID;
assign	M_AXI4_1_WDATA_wire = M_AXI4_1_WDATA;
assign	M_AXI4_1_WLAST_wire = M_AXI4_1_WLAST;
assign	M_AXI4_1_WREADY_wire = M_AXI4_1_WREADY;
assign	M_AXI4_1_WSTRB_wire = M_AXI4_1_WSTRB;
assign	M_AXI4_1_WVALID_wire = M_AXI4_1_WVALID;
assign	M_AXI4_1_RST_N_wire = M_AXI4_1_RST_N;

//Wire assignment for FPGA-to-SoC Interrupts
assign	IRQ_OUT_wire = IRQ_OUT;
assign	IRQ_OUT_RST_N_wire = IRQ_OUT_RST_N;

//Wire assignment for SoC-to-FPGA Interrupts
assign	IRQ_IN_wire = IRQ_IN;
assign	IRQ_IN_RST_N_wire = IRQ_IN_RST_N;

//Wire assignment for SoC-to-FPGA DMA Signals
assign	DMA_IN_wire = DMA_IN;

//Wire assignment for FPGA-to-Soc DMA Signals
assign	DMA_OUT_wire = DMA_OUT;

gemini_pss gemini_pss_i (
	//Slave AHB3 Interface 0
	.FPGA_AHB_S0_HADDR(S_AHB3_0_HADDR_wire),
	.FPGA_AHB_S0_HBURST(S_AHB3_0_HBURST_wire),
	.FPGA_AHB_S0_HMASTLOCK(S_AHB3_0_HMASTLOCK_wire),
	.FPGA_AHB_S0_HPROT(S_AHB3_0_HPROT_wire),
	.FPGA_AHB_S0_HRDATA(S_AHB3_0_HRDATA_wire),
	.FPGA_AHB_S0_HREADY(S_AHB3_0_HREADY_wire),
	.FPGA_AHB_S0_HRESP(S_AHB3_0_HRESP_wire),
	.FPGA_AHB_S0_HSEL(S_AHB3_0_HSEL_wire),
	.FPGA_AHB_S0_HSIZE(S_AHB3_0_HSIZE_wire),
	.FPGA_AHB_S0_HTRANS(S_AHB3_0_HTRANS_wire),
	.FPGA_AHB_S0_HWBE(S_AHB3_0_HWBE_wire),
	.FPGA_AHB_S0_HWDATA(S_AHB3_0_HWDATA_wire),
	.FPGA_AHB_S0_HWRITE(S_AHB3_0_HWRITE_wire),
	.FPGA_AHB_S0_RST_N(S_AHB3_0_RST_N_wire),

	//Master AXI4 Interface 0
	.FPGA_AXI_M0_AR_ADDR(M_AXI4_0_ARADDR_wire),
	.FPGA_AXI_M0_AR_BURST(M_AXI4_0_ARBURST_wire),
	.FPGA_AXI_M0_AR_CACHE(M_AXI4_0_ARCACHE_wire),
	.FPGA_AXI_M0_AR_ID(M_AXI4_0_ARID_wire),
	.FPGA_AXI_M0_AR_LEN(M_AXI4_0_ARLEN_wire),
	.FPGA_AXI_M0_AR_LOCK(M_AXI4_0_ARLOCK_wire),
	.FPGA_AXI_M0_AR_PROT(M_AXI4_0_ARPROT_wire),
	.FPGA_AXI_M0_AR_READY(M_AXI4_0_ARREADY_wire),
	.FPGA_AXI_M0_AR_SIZE(M_AXI4_0_ARSIZE_wire),
	.FPGA_AXI_M0_AR_VALID(M_AXI4_0_ARVALID_wire),
	.FPGA_AXI_M0_AW_ADDR(M_AXI4_0_AWADDR_wire),
	.FPGA_AXI_M0_AW_BURST(M_AXI4_0_AWBURST_wire),
	.FPGA_AXI_M0_AW_CACHE(M_AXI4_0_AWCACHE_wire),
	.FPGA_AXI_M0_AW_ID(M_AXI4_0_AWID_wire),
	.FPGA_AXI_M0_AW_LEN(M_AXI4_0_AWLEN_wire),
	.FPGA_AXI_M0_AW_LOCK(M_AXI4_0_AWLOCK_wire),
	.FPGA_AXI_M0_AW_PROT(M_AXI4_0_AWPROT_wire),
	.FPGA_AXI_M0_AW_READY(M_AXI4_0_AWREADY_wire),
	.FPGA_AXI_M0_AW_SIZE(M_AXI4_0_AWSIZE_wire),
	.FPGA_AXI_M0_AW_VALID(M_AXI4_0_AWVALID_wire),
	.FPGA_AXI_M0_B_ID(M_AXI4_0_BID_wire),
	.FPGA_AXI_M0_B_READY(M_AXI4_0_BREADY_wire),
	.FPGA_AXI_M0_B_RESP(M_AXI4_0_BRESP_wire),
	.FPGA_AXI_M0_B_VALID(M_AXI4_0_BVALID_wire),
	.FPGA_AXI_M0_R_DATA(M_AXI4_0_RDATA_wire),
	.FPGA_AXI_M0_R_ID(M_AXI4_0_RID_wire),
	.FPGA_AXI_M0_R_LAST(M_AXI4_0_RLAST_wire),
	.FPGA_AXI_M0_R_READY(M_AXI4_0_RREADY_wire),
	.FPGA_AXI_M0_R_RESP(M_AXI4_0_RRESP_wire),
	.FPGA_AXI_M0_R_VALID(M_AXI4_0_RVALID_wire),
	.FPGA_AXI_M0_W_DATA(M_AXI4_0_WDATA_wire),
	.FPGA_AXI_M0_W_LAST(M_AXI4_0_WLAST_wire),
	.FPGA_AXI_M0_W_READY(M_AXI4_0_WREADY_wire),
	.FPGA_AXI_M0_W_STRB(M_AXI4_0_WSTRB_wire),
	.FPGA_AXI_M0_W_VALID(M_AXI4_0_WVALID_wire),
	.FPGA_AXI_M0_RST_N(M_AXI4_0_RST_N_wire),

	//Master AXI4 Interface 1
	.FPGA_AXI_M1_AR_ADDR(M_AXI4_1_ARADDR_wire),
	.FPGA_AXI_M1_AR_BURST(M_AXI4_1_ARBURST_wire),
	.FPGA_AXI_M1_AR_CACHE(M_AXI4_1_ARCACHE_wire),
	.FPGA_AXI_M1_AR_ID(M_AXI4_1_ARID_wire),
	.FPGA_AXI_M1_AR_LEN(M_AXI4_1_ARLEN_wire),
	.FPGA_AXI_M1_AR_LOCK(M_AXI4_1_ARLOCK_wire),
	.FPGA_AXI_M1_AR_PROT(M_AXI4_1_ARPROT_wire),
	.FPGA_AXI_M1_AR_READY(M_AXI4_1_ARREADY_wire),
	.FPGA_AXI_M1_AR_SIZE(M_AXI4_1_ARSIZE_wire),
	.FPGA_AXI_M1_AR_VALID(M_AXI4_1_ARVALID_wire),
	.FPGA_AXI_M1_AW_ADDR(M_AXI4_1_AWADDR_wire),
	.FPGA_AXI_M1_AW_BURST(M_AXI4_1_AWBURST_wire),
	.FPGA_AXI_M1_AW_CACHE(M_AXI4_1_AWCACHE_wire),
	.FPGA_AXI_M1_AW_ID(M_AXI4_1_AWID_wire),
	.FPGA_AXI_M1_AW_LEN(M_AXI4_1_AWLEN_wire),
	.FPGA_AXI_M1_AW_LOCK(M_AXI4_1_AWLOCK_wire),
	.FPGA_AXI_M1_AW_PROT(M_AXI4_1_AWPROT_wire),
	.FPGA_AXI_M1_AW_READY(M_AXI4_1_AWREADY_wire),
	.FPGA_AXI_M1_AW_SIZE(M_AXI4_1_AWSIZE_wire),
	.FPGA_AXI_M1_AW_VALID(M_AXI4_1_AWVALID_wire),
	.FPGA_AXI_M1_B_ID(M_AXI4_1_BID_wire),
	.FPGA_AXI_M1_B_READY(M_AXI4_1_BREADY_wire),
	.FPGA_AXI_M1_B_RESP(M_AXI4_1_BRESP_wire),
	.FPGA_AXI_M1_B_VALID(M_AXI4_1_BVALID_wire),
	.FPGA_AXI_M1_R_DATA(M_AXI4_1_RDATA_wire),
	.FPGA_AXI_M1_R_ID(M_AXI4_1_RID_wire),
	.FPGA_AXI_M1_R_LAST(M_AXI4_1_RLAST_wire),
	.FPGA_AXI_M1_R_READY(M_AXI4_1_RREADY_wire),
	.FPGA_AXI_M1_R_RESP(M_AXI4_1_RRESP_wire),
	.FPGA_AXI_M1_R_VALID(M_AXI4_1_RVALID_wire),
	.FPGA_AXI_M1_W_DATA(M_AXI4_1_WDATA_wire),
	.FPGA_AXI_M1_W_LAST(M_AXI4_1_WLAST_wire),
	.FPGA_AXI_M1_W_READY(M_AXI4_1_WREADY_wire),
	.FPGA_AXI_M1_W_STRB(M_AXI4_1_WSTRB_wire),
	.FPGA_AXI_M1_W_VALID(M_AXI4_1_WVALID_wire),
	.FPGA_AXI_M1_RST_N(M_AXI4_1_RST_N_wire),

	//FPGA-to-SoC Interrupts
	.IRQ_F2A(IRQ_OUT_wire),
	.IRQ_F2A_RST_N(IRQ_OUT_RST_N_wire),

	//SoC-to-FPGA Interrupts
	.IRQ_A2F(IRQ_IN_wire),
	.IRQ_IN_RST_N_wire(_wire),

	//SoC-to-FPGA DMA Signals
	.DMA_A2F(DMA_IN_wire),
	//FPGA-to-Soc DMA Signals
	.DMA_F2A(DMA_OUT_wire)
);

endmodule