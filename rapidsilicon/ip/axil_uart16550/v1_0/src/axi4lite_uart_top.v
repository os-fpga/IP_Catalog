/* verilator lint_off UNUSED */ 
/* verilator lint_off IMPLICIT */ 
/* verilator lint_off DEFPARAM */ 
////////////////////////////////////////
////                                 ///
////  axi4lite_uart_top.v            ///
////                                 ///
////                                 ///
////    					         ///
////  			                     ///
////                                 ///
////  To Do:                         ///
////                                 ///
////                                 ///
////  Author(s):                     ///
////                                 ///
////  Created:                       ///
////////////////////////////////////////

`include "./uart_defines.vh"
`include "./timescale.v"

module axi4lite_uart_top #(
    parameter IP_TYPE 		    = "ALUR",
	parameter IP_VERSION 	    = 32'h1, 
	parameter IP_ID 	    = 32'h2591807,
    
    parameter ADDRESS_WIDTH     = 16,
    parameter DATA_WIDTH        = 32,
    parameter PROT_WIDTH        = 3,
    parameter STRB_WIDTH        = (DATA_WIDTH/8)
) 
(
    // Global signals
    input  wire                          s_axi_aclk,
    input  wire                          s_axi_aresetn,

    // write address channel
    input  wire                          s_axi_awvalid,
    input  wire [ADDRESS_WIDTH-1:0]      s_axi_awaddr,
    input  wire [PROT_WIDTH-1:0]         s_axi_awprot,
    output wire                          s_axi_awready,

    // write data channel
    input  wire                          s_axi_wvalid,
    input  wire [DATA_WIDTH-1:0]         s_axi_wdata,
    input  wire [STRB_WIDTH-1:0]         s_axi_wstrb,
    output wire                          s_axi_wready,

    // write response channel
    output wire                          s_axi_bvalid,
    output wire  [1:0]                   s_axi_bresp,
    input  wire                          s_axi_bready,

    // read address channel
    input  wire                          s_axi_arvalid,
    input  wire [ADDRESS_WIDTH-1:0]      s_axi_araddr,
    input  wire [PROT_WIDTH-1:0]         s_axi_arprot,
    output wire                          s_axi_arready,

    // read data channel
    output wire                          s_axi_rvalid,
    output wire  [DATA_WIDTH-1:0]        s_axi_rdata,
    output wire  [1:0]                   s_axi_rresp,
    input  wire                          s_axi_rready,

    // UART Signals
    output  wire                         int_o,
    input 	wire					     srx_pad_i,
    output 	wire					     stx_pad_o,
    output 	wire					     rts_pad_o,
    input 	wire					     cts_pad_i,
    output 	wire					     dtr_pad_o,
    input 	wire					     dsr_pad_i,
    input 	wire					     ri_pad_i,
    input 	wire					     dcd_pad_i

);

wire  [3:0]                         ier;
wire  [3:0]                         iir;
wire  [1:0]                         fcr;
wire  [4:0]                         mcr;
wire  [7:0]                         lcr;
wire  [7:0]                         msr;
wire  [7:0]                         lsr;
wire  [`UART_FIFO_COUNTER_W-1:0]    rf_count;
wire  [`UART_FIFO_COUNTER_W-1:0]    tf_count;
wire  [2:0]                         tstate;
wire  [3:0]                         rstate; 
wire  [31:0]                       r_data_in;
wire  [DATA_WIDTH-1:0]              r_data_in_dbg;

wire  [ADDRESS_WIDTH-1:0]           addr_in;
wire  [7:0]                         w_data_in;
wire                                re;
wire                                we; 
wire                                tf_overrun; 

axi4lite_slave #(
.ADDRESS_WIDTH(ADDRESS_WIDTH ),
.DATA_WIDTH(DATA_WIDTH ),
.PROT_WIDTH(PROT_WIDTH )
)
axi4lite_slave_dut (
.s_axi_aclk (s_axi_aclk ),
.s_axi_aresetn (s_axi_aresetn ),
.s_axi_awvalid (s_axi_awvalid ),
.s_axi_awaddr (s_axi_awaddr ),
.s_axi_awprot (s_axi_awprot ),
.s_axi_awready (s_axi_awready ),
.s_axi_wvalid (s_axi_wvalid ),
.s_axi_wdata (s_axi_wdata ),
.s_axi_wstrb (s_axi_wstrb ),
.s_axi_wready (s_axi_wready ),
.s_axi_bvalid (s_axi_bvalid ),
.s_axi_bresp (s_axi_bresp ),
.s_axi_bready (s_axi_bready ),
.s_axi_arvalid (s_axi_arvalid ),
.s_axi_araddr (s_axi_araddr ),
.s_axi_arprot (s_axi_arprot ),
.s_axi_arready (s_axi_arready ),
.s_axi_rvalid (s_axi_rvalid ),
.s_axi_rdata (s_axi_rdata ),
.s_axi_rresp (s_axi_rresp ),
.s_axi_rready  ( s_axi_rready),
.r_data_in (r_data_in),
.r_data_in_dbg(r_data_in_dbg),
.addr_in(addr_in),
.w_data_in(w_data_in),
.re(re),
.we(we),
.tf_overrun(tf_overrun)
);


uart_regs #(
.IP_TYPE(IP_TYPE),
.IP_VERSION(IP_VERSION),
.IP_ID(IP_ID)
) uart_regs_dut (
.clk (s_axi_aclk ),
.wb_rst_i (!s_axi_aresetn ),
.wb_addr_i (addr_in ),
.wb_dat_i ( w_data_in),
.wb_dat_o (r_data_in),
.wb_we_i (we ),
.wb_re_i (re ),
.stx_pad_o (stx_pad_o ),
.srx_pad_i (srx_pad_i ),
.modem_inputs ({cts_pad_i, dsr_pad_i, ri_pad_i,  dcd_pad_i} ),
.rts_pad_o (rts_pad_o ),
.dtr_pad_o (dtr_pad_o ),
.int_o (int_o ),
.ier (ier ),
.iir (iir ),
.fcr (fcr ),
.mcr (mcr ),
.lcr (lcr ),
.msr (msr ),
.lsr (lsr ),
.rf_count (rf_count ),
.tf_count (tf_count ),
.tstate (tstate ),
.rstate  ( rstate),
.tf_overrun(tf_overrun)
);


uart_debug_if 
uart_debug_if_dut 
(
.wb_adr_i (addr_in ),
.wb_dat32_o (r_data_in_dbg ),
.ier (ier ),
.iir (iir ),
.fcr (fcr ),
.mcr (mcr ),
.lcr (lcr ),
.msr (msr ),
.lsr (lsr ),
.rf_count (rf_count ),
.tf_count (tf_count ),
.tstate (tstate ),
.rstate ( rstate)
);

endmodule

