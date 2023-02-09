///////////////////////////////////////////////////////
//  gemini_pss_reference_top.v
//  Copyright (c) 2023 Rapid Silicon
//  All Right Reserved.
//  Reference signal declarations for Raptor top-level
//  module
///////////////////////////////////////////////////////

`timescale 1 ps / 1 ps 

module top (
//Slave AHB3 Interface 0
//Only add the signals in this section if your
//design connects to interface AHB_3_S0
input	[31:0]	FPGA_AHB_S0_HADDR,
input	[2:0]	FPGA_AHB_S0_HBURST,
input			FPGA_AHB_S0_HMASTLOCK,
output	[3:0]	FPGA_AHB_S0_HPROT,
output	[31:0]	FPGA_AHB_S0_HRDATA,
output			FPGA_AHB_S0_HREADY,
output			FPGA_AHB_S0_HRESP,
input			FPGA_AHB_S0_HSEL,
input	[2:0]	FPGA_AHB_S0_HSIZE,
input	[1:0]	FPGA_AHB_S0_HTRANS,
input	[3:0]	FPGA_AHB_S0_HWBE,
input	[31:0]	FPGA_AHB_S0_HWDATA,
input			FPGA_AHB_S0_HWRITE,
input			FPGA_AHB_S0_RST_N,

//Master AXI4 Interface 0
//Only add the signals in this section if your
//design connects to interface AXI_4_M0
output	[31:0]	FPGA_AXI_M0_AR_ADDR,
output	[1:0]	FPGA_AXI_M0_AR_BURST,
output	[3:0]	FPGA_AXI_M0_AR_CACHE,
output	[3:0]	FPGA_AXI_M0_AR_ID,
output	[2:0]	FPGA_AXI_M0_AR_LEN,
output			FPGA_AXI_M0_AR_LOCK,
output	[2:0]	FPGA_AXI_M0_AR_PROT,
input			FPGA_AXI_M0_AR_READY,
output	[2:0]	FPGA_AXI_M0_AR_SIZE,
output			FPGA_AXI_M0_AR_VALID,
output	[31:0]	FPGA_AXI_M0_AW_ADDR,
output	[1:0]	FPGA_AXI_M0_AW_BURST,
output	[3:0]	FPGA_AXI_M0_AW_CACHE,
output	[3:0]	FPGA_AXI_M0_AW_ID,
output	[2:0]	FPGA_AXI_M0_AW_LEN,
output			FPGA_AXI_M0_AW_LOCK,
output	[2:0]	FPGA_AXI_M0_AW_PROT,
input			FPGA_AXI_M0_AW_READY,
output	[2:0]	FPGA_AXI_M0_AW_SIZE,
output			FPGA_AXI_M0_AW_VALID,
input	[3:0]	FPGA_AXI_M0_B_ID,
output			FPGA_AXI_M0_B_READY,
input	[1:0]	FPGA_AXI_M0_B_RESP,
input			FPGA_AXI_M0_B_VALID,
input	[63:0]	FPGA_AXI_M0_R_DATA,
input	[3:0]	FPGA_AXI_M0_R_ID,
input			FPGA_AXI_M0_R_LAST,
output			FPGA_AXI_M0_R_READY,
input	[1:0]	FPGA_AXI_M0_R_RESP,
input			FPGA_AXI_M0_R_VALID,
output	[63:0]	FPGA_AXI_M0_W_DATA,
output			FPGA_AXI_M0_W_LAST,
output			FPGA_AXI_M0_W_READY,
output	[7:0]	FPGA_AXI_M0_W_STRB,
output			FPGA_AXI_M0_W_VALID,
input			FPGA_AXI_M0_RST_N,

//Master AXI4 Interface 1
//Only add the signals in this section if your
//design connects to interface AXI_4_M1
output	[31:0]	FPGA_AXI_M1_AR_ADDR,
output	[1:0]	FPGA_AXI_M1_AR_BURST,
output	[3:0]	FPGA_AXI_M1_AR_CACHE,
output	[3:0]	FPGA_AXI_M1_AR_ID,
output	[2:0]	FPGA_AXI_M1_AR_LEN,
output			FPGA_AXI_M1_AR_LOCK,
output	[2:0]	FPGA_AXI_M1_AR_PROT,
input			FPGA_AXI_M1_AR_READY,
output	[2:0]	FPGA_AXI_M1_AR_SIZE,
output			FPGA_AXI_M1_AR_VALID,
output	[31:0]	FPGA_AXI_M1_AW_ADDR,
output	[1:0]	FPGA_AXI_M1_AW_BURST,
output	[3:0]	FPGA_AXI_M1_AW_CACHE,
output	[3:0]	FPGA_AXI_M1_AW_ID,
output	[2:0]	FPGA_AXI_M1_AW_LEN,
output			FPGA_AXI_M1_AW_LOCK,
output	[2:0]	FPGA_AXI_M1_AW_PROT,
input			FPGA_AXI_M1_AW_READY,
output	[2:0]	FPGA_AXI_M1_AW_SIZE,
output			FPGA_AXI_M1_AW_VALID,
input	[3:0]	FPGA_AXI_M1_B_ID,
output			FPGA_AXI_M1_B_READY,
input	[1:0]	FPGA_AXI_M1_B_RESP,
input			FPGA_AXI_M1_B_VALID,
input	[63:0]	FPGA_AXI_M1_R_DATA,
input	[3:0]	FPGA_AXI_M1_R_ID,
input			FPGA_AXI_M1_R_LAST,
output			FPGA_AXI_M1_R_READY,
input	[1:0]	FPGA_AXI_M1_R_RESP,
input			FPGA_AXI_M1_R_VALID,
output	[63:0]	FPGA_AXI_M1_W_DATA,
output			FPGA_AXI_M1_W_LAST,
output			FPGA_AXI_M1_W_READY,
output	[7:0]	FPGA_AXI_M1_W_STRB,
output			FPGA_AXI_M1_W_VALID,
input			FPGA_AXI_M1_RST_N,

//FPGA-to-SoC Interrupts
//[15:0] : CPU IRQ[15:0]
output	[15:0]	FPGA_IRQ_SRC,

//SoC-to-FPGA Interrupts
//0: RSVD IRQ 3
//1: Timer IRQ
//2: USB IRQ
//3: Ethernet IRQ
//4: UART0 IRQ
//5: UART1 IRQ
//6: SPI IRQ
//7: I2C IRQ
//8: GPIO IRQ
//9: DMA IRQ
//10: DDR IRQ
//11: RSVD IRQ 0
//12: RSVD IRQ 1
//13: FPGA Mailbox 0 IRQ
//14: FPGA Mailbox 1 IRQ
//15: PUFCC Security IRQ
input	[15:0]	FPGA_IRQ_SET,

// Reset signals from FPGA to SoC
output			RST_N_FPGA_FABRIC_GPIO,
output			RST_N_FPGA_FABRIC_DMA,
output			RST_N_FPGA_FABRIC_IRQ,

//SoC-to-FPGA DMA Signals
input	[3:0]	DMA_ACK_FPGA,
//FPGA-to-Soc DMA Signals
output	[3:0]	DMA_REQ_FPGA
);