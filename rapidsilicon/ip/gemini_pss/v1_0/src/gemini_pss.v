///////////////////////////////////////////////////////
//  gemini_pss.v
//  Copyright (c) 2023 Rapid Silicon
//  All Right Reserved.
///////////////////////////////////////////////////////

`timescale 1 ps / 1 ps 

module gemini_pss (
	//Slave AHB3 Interface 0
	S_AHB3_0_HADDR,
	S_AHB3_0_HBURST,
	S_AHB3_0_HMASTLOCK,
	S_AHB3_0_HPROT,
	S_AHB3_0_HRDATA,
	S_AHB3_0_HREADY,
	S_AHB3_0_HRESP,
	S_AHB3_0_HSEL,
	S_AHB3_0_HSIZE,
	S_AHB3_0_HTRANS,
	S_AHB3_0_HWBE,
	S_AHB3_0_HWDATA,
	S_AHB3_0_HWRITE,
	S_AHB3_0_RST_n,

	//Master AXI4 Interface 0
	M_AXI4_0_AR_ADDR,
	M_AXI4_0_AR_BURST,
	M_AXI4_0_AR_CACHE,
	M_AXI4_0_AR_ID,
	M_AXI4_0_AR_LEN,
	M_AXI4_0_AR_LOCK,
	M_AXI4_0_AR_PROT,
	M_AXI4_0_AR_READY,
	M_AXI4_0_AR_SIZE,
	M_AXI4_0_AR_VALID,
	M_AXI4_0_AW_ADDR,
	M_AXI4_0_AW_BURST,
	M_AXI4_0_AW_CACHE,
	M_AXI4_0_AW_ID,
	M_AXI4_0_AW_LEN,
	M_AXI4_0_AW_LOCK,
	M_AXI4_0_AW_PROT,
	M_AXI4_0_AW_READY,
	M_AXI4_0_AW_SIZE,
	M_AXI4_0_AW_VALID,
	M_AXI4_0_B_ID,
	M_AXI4_0_B_READY,
	M_AXI4_0_B_RESP,
	M_AXI4_0_B_VALID,
	M_AXI4_0_R_DATA,
	M_AXI4_0_R_ID,
	M_AXI4_0_R_LAST,
	M_AXI4_0_R_READY,
	M_AXI4_0_R_RESP,
	M_AXI4_0_R_VALID,
	M_AXI4_0_W_DATA,
	M_AXI4_0_W_LAST,
	M_AXI4_0_W_READY,
	M_AXI4_0_W_STRB,
	M_AXI4_0_W_VALID,
	M_AXI4_0_RST_n,

	//Master AXI4 Interface 1
	M_AXI4_1_AR_ADDR,
	M_AXI4_1_AR_BURST,
	M_AXI4_1_AR_CACHE,
	M_AXI4_1_AR_ID,
	M_AXI4_1_AR_LEN,
	M_AXI4_1_AR_LOCK,
	M_AXI4_1_AR_PROT,
	M_AXI4_1_AR_READY,
	M_AXI4_1_AR_SIZE,
	M_AXI4_1_AR_VALID,
	M_AXI4_1_AW_ADDR,
	M_AXI4_1_AW_BURST,
	M_AXI4_1_AW_CACHE,
	M_AXI4_1_AW_ID,
	M_AXI4_1_AW_LEN,
	M_AXI4_1_AW_LOCK,
	M_AXI4_1_AW_PROT,
	M_AXI4_1_AW_READY,
	M_AXI4_1_AW_SIZE,
	M_AXI4_1_AW_VALID,
	M_AXI4_1_B_ID,
	M_AXI4_1_B_READY,
	M_AXI4_1_B_RESP,
	M_AXI4_1_B_VALID,
	M_AXI4_1_R_DATA,
	M_AXI4_1_R_ID,
	M_AXI4_1_R_LAST,
	M_AXI4_1_R_READY,
	M_AXI4_1_R_RESP,
	M_AXI4_1_R_VALID,
	M_AXI4_1_W_DATA,
	M_AXI4_1_W_LAST,
	M_AXI4_1_W_READY,
	M_AXI4_1_W_STRB,
	M_AXI4_1_W_VALID,
	M_AXI4_1_RST_n,

	//FPGA-to-SoC Interrupts
	IRQ_F2A,
	IRQ_F2A_RST_n,

	//SoC-to-FPGA Interrupts
	IRQ_A2F,
	IRQ_A2F_RST_n,

	//SoC-to-FPGA DMA Signals
	DMA_A2F,
	//FPGA-to-Soc DMA Signals
	DMA_F2A	
);

  
//Slave AHB3 Interface 0
input	[31:0]	S_AHB3_0_HADDR;
input	[2:0]	S_AHB3_0_HBURST;
input			S_AHB3_0_HMASTLOCK;
output	[3:0]	S_AHB3_0_HPROT;
output	[31:0]	S_AHB3_0_HRDATA;
output			S_AHB3_0_HREADY;
output			S_AHB3_0_HRESP;
input			S_AHB3_0_HSEL;
input	[2:0]	S_AHB3_0_HSIZE;
input	[1:0]	S_AHB3_0_HTRANS;
input	[3:0]	S_AHB3_0_HWBE;
input	[31:0]	S_AHB3_0_HWDATA;
input			S_AHB3_0_HWRITE;
input			S_AHB3_0_RST_n;

//Master AXI4 Interface 0
output	[31:0]	M_AXI4_0_AR_ADDR;
output	[1:0]	M_AXI4_0_AR_BURST;
output	[3:0]	M_AXI4_0_AR_CACHE;
output	[3:0]	M_AXI4_0_AR_ID;
output	[2:0]	M_AXI4_0_AR_LEN;
output			M_AXI4_0_AR_LOCK;
output	[2:0]	M_AXI4_0_AR_PROT;
input			M_AXI4_0_AR_READY;
output	[2:0]	M_AXI4_0_AR_SIZE;
output			M_AXI4_0_AR_VALID;
output	[31:0]	M_AXI4_0_AW_ADDR;
output	[1:0]	M_AXI4_0_AW_BURST;
output	[3:0]	M_AXI4_0_AW_CACHE;
output	[3:0]	M_AXI4_0_AW_ID;
output	[2:0]	M_AXI4_0_AW_LEN;
output			M_AXI4_0_AW_LOCK;
output	[2:0]	M_AXI4_0_AW_PROT
input			M_AXI4_0_AW_READY;
output	[2:0]	M_AXI4_0_AW_SIZE;
output			M_AXI4_0_AW_VALID;
input	[3:0]	M_AXI4_0_B_ID;
output			M_AXI4_0_B_READY;
input	[1:0]	M_AXI4_0_B_RESP;
input			M_AXI4_0_B_VALID;
input	[63:0]	M_AXI4_0_R_DATA;
input	[3:0]	M_AXI4_0_R_ID;
input			M_AXI4_0_R_LAST;
output			M_AXI4_0_R_READY;
input	[1:0]	M_AXI4_0_R_RESP;
input			M_AXI4_0_R_VALID;
output	[63:0]	M_AXI4_0_W_DATA;
output			M_AXI4_0_W_LAST;
output			M_AXI4_0_W_READY;
output	[7:0]	M_AXI4_0_W_STRB;
output			M_AXI4_0_W_VALID;
input			M_AXI4_0_RST_n;

//Master AXI4 Interface 1
output	[31:0]	M_AXI4_1_AR_ADDR;
output	[1:0]	M_AXI4_1_AR_BURST;
output	[3:0]	M_AXI4_1_AR_CACHE;
output	[3:0]	M_AXI4_1_AR_ID;
output	[2:0]	M_AXI4_1_AR_LEN;
output			M_AXI4_1_AR_LOCK;
output	[2:0]	M_AXI4_1_AR_PROT;
input			M_AXI4_1_AR_READY;
output	[2:0]	M_AXI4_1_AR_SIZE;
output			M_AXI4_1_AR_VALID;
output	[31:0]	M_AXI4_1_AW_ADDR;
output	[1:0]	M_AXI4_1_AW_BURST;
output	[3:0]	M_AXI4_1_AW_CACHE;
output	[3:0]	M_AXI4_1_AW_ID;
output	[2:0]	M_AXI4_1_AW_LEN;
output			M_AXI4_1_AW_LOCK;
output	[2:0]	M_AXI4_1_AW_PROT
input			M_AXI4_1_AW_READY;
output	[2:0]	M_AXI4_1_AW_SIZE;
output			M_AXI4_1_AW_VALID;
input	[3:0]	M_AXI4_1_B_ID;
output			M_AXI4_1_B_READY;
input	[1:0]	M_AXI4_1_B_RESP;
input			M_AXI4_1_B_VALID;
input	[63:0]	M_AXI4_1_R_DATA;
input	[3:0]	M_AXI4_1_R_ID;
input			M_AXI4_1_R_LAST;
output			M_AXI4_1_R_READY;
input	[1:0]	M_AXI4_1_R_RESP;
input			M_AXI4_1_R_VALID;
output	[63:0]	M_AXI4_1_W_DATA;
output			M_AXI4_1_W_LAST;
output			M_AXI4_1_W_READY;
output	[7:0]	M_AXI4_1_W_STRB;
output			M_AXI4_1_W_VALID;
input			M_AXI4_1_RST_n;

//FPGA-to-SoC Interrupts
output	[15:0]	IRQ_F2A;
output			IRQ_F2A_RST_n;

//SoC-to-FPGA Interrupts
input	[15:0]	IRQ_A2F;
input			IRQ_A2F_RST_n;

//SoC-to-FPGA DMA Signals
input	[3:0]	DMA_A2F;
//FPGA-to-Soc DMA Signals
output	[3:0]	DMA_F2A;

endmodule