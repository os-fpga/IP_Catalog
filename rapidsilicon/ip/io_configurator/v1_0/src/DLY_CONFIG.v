
`timescale 1ns/1ps

`include "header.vh"

module DLY_CONFIG #(
    parameter IO_MODEL                  = "I_DELAY",
    // IO_BUF
    parameter WEAK_KEEPER               = "NONE",
    parameter IOSTANDARD                = "DEFAULT",
    parameter DRIVE_STRENGTH            = 2,
    parameter SLEW_RATE                 = "SLOW",
    parameter DIFFERENTIAL_TERMINATION  = "TRUE",
    parameter IO_TYPE                   = "SINGLE_ENDED",

    //  PLL
    parameter PLL_MULT                  = 16,
    parameter PLL_DIV                   = 1,

    // IO_SERDES
    parameter WIDTH                     = 4,
    parameter DATA_RATE                 = "SDR",
    parameter DPA_MODE                  = "NONE",

    // IO_DELAYs
    parameter DELAY                     = 0,
    parameter NUM_DLY                   = 4,
    parameter DLY_LOC                   = 40'b1100000000000000000000000000000000000011,
    parameter ADDR_WIDTH                = 5,
    parameter DLY_TAP_WIDTH             = 6,
    parameter DLY_SEL_WIDTH             = $clog2(NUM_DLY),
    parameter NUM_GB_SITES              = 20,                 // fixed for VIRGO TC
    parameter DELAY_TYPE                = "STATIC"           // "STATIC", "DYNAMIC"
)
(   
    `ifndef LOCAL_OSCILLATOR
        input  wire                             CLK_IN,
    `endif

    `ifdef I_DELAY
        input  wire [DATA_WIDTH-1:0]            DATA_IN,
        output wire [NUM_DLY-1:0]               DATA_OUT,
    
    `elsif O_DELAY
        input  wire [NUM_DLY-1:0]               DATA_IN,
        output wire [DATA_WIDTH-1:0]            DATA_OUT,

    `elsif I_DELAY_I_SERDES
        input wire  [DATA_WIDTH-1:0]            SDATA_IN,
        input wire  [NUM_DLY-1:0]               EN,
        input wire  [NUM_DLY-1:0]               BITSLIP_ADJ,
        output wire [NUM_DLY-1:0]               CLK_OUT,
        output wire [NUM_DLY-1:0]               DPA_LOCK,
        output wire [NUM_DLY-1:0]               DPA_ERROR,
        output wire [NUM_DLY-1:0]               DATA_VALID,
        output wire [(NUM_DLY*WIDTH)-1:0]       PDATA_OUT,
        
    `elsif I_DELAY_I_DDR
        input  wire [DATA_WIDTH-1:0]            SD_IN,
        input wire  [NUM_DLY-1:0]               EN,
        output wire [(2*NUM_DLY)-1:0]           DD_OUT,

    `elsif O_SERDES_O_DELAY
        input  wire                             FAB_CLK_IN,
        input  wire [(NUM_DLY*WIDTH)-1:0]       PDATA_IN,
        input  wire [NUM_DLY-1:0]               DATA_VALID,
        input  wire [NUM_DLY-1:0]               OE_IN,
        output wire [DATA_WIDTH-1:0]            SDATA_OUT,
    
    `elsif O_DDR_O_DELAY
        input wire  [(2*NUM_DLY)-1:0]           DD_IN,
        input wire  [NUM_DLY-1:0]               EN,
        output wire [DATA_WIDTH-1:0]            SD_OUT,

    `elsif I_DELAY_O_DELAY
        input  wire [(DATA_WIDTH/2)-1:0]        DIN_IDLY,
        input  wire [(NUM_DLY/2)-1:0]           DIN_ODLY,
        output wire [(NUM_DLY/2)-1:0]           DOUT_IDLY,
        output wire [(DATA_WIDTH/2)-1:0]        DOUT_ODLY,
    
    `elsif I_DELAY_I_SERDES_O_DELAY_O_SERDES
        input wire  [(DATA_WIDTH/2)-1:0]        SDATA_IN_IDLY,
        input wire  [((NUM_DLY/2)*WIDTH)-1:0]   PDATA_IN_OSERDES,
        input wire  [(NUM_DLY/2)-1:0]           DATA_VALID_OSERDES,
        input wire  [(NUM_DLY/2)-1:0]           FAB_CLK_IN,
        input wire  [(NUM_DLY/2)-1:0]           OE_IN,
        input wire  [(NUM_DLY/2)-1:0]           EN,
        input wire  [(NUM_DLY/2)-1:0]           BITSLIP_ADJ,
        output wire [(NUM_DLY/2)-1:0]           CLK_OUT,
        output wire [(NUM_DLY/2)-1:0]           DPA_LOCK,
        output wire [(NUM_DLY/2)-1:0]           DPA_ERROR,
        output wire [(NUM_DLY/2)-1:0]           DATA_VALID_ISERDES,
        output wire [((NUM_DLY/2)*WIDTH)-1:0]   PDATA_OUT_ISERDES,
        output wire  [(DATA_WIDTH/2)-1:0]       SDATA_OUT_ODLY,

    `elsif I_DELAY_I_DDR_O_DELAY_O_DDR
        input  wire [(DATA_WIDTH/2)-1:0]        SD_IN_IDDR,
        input  wire [(2*(NUM_DLY/2))-1:0]       DD_IN_ODDR,
        input  wire [(NUM_DLY/2)-1:0]           EN_IDDR,
        input  wire [(NUM_DLY/2)-1:0]           EN_ODDR,
        output wire [(2*(NUM_DLY/2))-1:0]       DD_OUT_IDDR,
        output wire [(DATA_WIDTH/2)-1:0]        SD_OUT_ODDR,

    `elsif I_DELAY_O_DELAY_O_SERDES
        input  wire [(DATA_WIDTH/2)-1:0]        DIN_IDLY,
        input  wire [((NUM_DLY/2)*WIDTH)-1:0]   PDATA_IN_OSERDES,
        input  wire [(NUM_DLY/2)-1:0]           DATA_VALID_OSERDES,
        input  wire [(NUM_DLY/2)-1:0]           FAB_CLK_IN,
        input  wire [(NUM_DLY/2)-1:0]           OE_IN,
        output wire [(NUM_DLY/2)-1:0]           DOUT_IDLY,
        output wire  [(DATA_WIDTH/2)-1:0]       SDATA_OUT_ODLY,
    
    `elsif I_DELAY_O_DELAY_O_DDR
        input  wire [(DATA_WIDTH/2)-1:0]        DIN_IDLY,
        output wire [(NUM_DLY/2)-1:0]           DOUT_IDLY,
        input wire  [(2*(NUM_DLY/2))-1:0]       DD_IN_ODDR,
        input wire  [(NUM_DLY/2)-1:0]           EN_ODDR,
        output wire [(DATA_WIDTH/2)-1:0]        SD_OUT_ODDR,

    `elsif I_DELAY_I_SERDES_O_DELAY
        input wire  [(DATA_WIDTH/2)-1:0]        SDATA_IN_IDLY,
        input wire  [(NUM_DLY/2)-1:0]           EN_ISERDES,
        input wire  [(NUM_DLY/2)-1:0]           BITSLIP_ADJ,
        output wire [(NUM_DLY/2)-1:0]           DATA_VALID_ISERDES,
        output wire [(NUM_DLY/2)-1:0]           DPA_LOCK,
        output wire [(NUM_DLY/2)-1:0]           DPA_ERROR,
        output wire [(NUM_DLY/2)-1:0]           CLK_OUT,
        output wire [((NUM_DLY/2)*WIDTH)-1:0]   PDATA_OUT_ISERDES,
        input  wire [(NUM_DLY/2)-1:0]           DIN_ODLY,
        output wire [(DATA_WIDTH/2)-1:0]        DOUT_ODLY,
    
    `elsif I_DELAY_I_SERDES_O_DELAY_O_DDR
        input wire  [(DATA_WIDTH/2)-1:0]        SDATA_IN_IDLY,
        input wire  [(NUM_DLY/2)-1:0]           EN_ISERDES,
        input wire  [(NUM_DLY/2)-1:0]           BITSLIP_ADJ,
        output wire [(NUM_DLY/2)-1:0]           DATA_VALID_ISERDES,
        output wire [(NUM_DLY/2)-1:0]           DPA_LOCK,
        output wire [(NUM_DLY/2)-1:0]           DPA_ERROR,
        output wire [(NUM_DLY/2)-1:0]           CLK_OUT,
        output wire [((NUM_DLY/2)*WIDTH)-1:0]   PDATA_OUT_ISERDES,
        input wire  [(2*(NUM_DLY/2))-1:0]       DD_IN_ODDR,
        input wire  [(NUM_DLY/2)-1:0]           EN_ODDR,
        output wire [(DATA_WIDTH/2)-1:0]        SD_OUT_ODDR,
        
    `elsif I_DELAY_I_DDR_O_DELAY
        input  wire [(DATA_WIDTH/2)-1:0]        SD_IN_IDDR,
        input  wire [(NUM_DLY/2)-1:0]           EN_IDDR,
        output wire [(2*(NUM_DLY/2))-1:0]       DD_OUT_IDDR,
        input  wire [(NUM_DLY/2)-1:0]           DIN_ODLY,
        output wire [(DATA_WIDTH/2)-1:0]        DOUT_ODLY,

    `elsif I_DELAY_I_DDR_O_DELAY_O_SERDES
        input  wire [(DATA_WIDTH/2)-1:0]        SD_IN_IDDR,
        input  wire [(NUM_DLY/2)-1:0]           EN_IDDR,
        output wire [(2*(NUM_DLY/2))-1:0]       DD_OUT_IDDR,
        input  wire [((NUM_DLY/2)*WIDTH)-1:0]   PDATA_IN_OSERDES,
        input  wire [(NUM_DLY/2)-1:0]           DATA_VALID_OSERDES,
        input  wire [(NUM_DLY/2)-1:0]           FAB_CLK_IN,
        input  wire [(NUM_DLY/2)-1:0]           OE_IN,
        output wire  [(DATA_WIDTH/2)-1:0]       SDATA_OUT_ODLY,
    `endif

    input  wire                                 RESET,
    input  wire [DLY_SEL_WIDTH-1:0]             SEL_DLY,
    input  wire [NUM_DLY-1:0]                   DLY_LOAD,
    input  wire [NUM_DLY-1:0]                   DLY_ADJ,
    input  wire [NUM_DLY-1:0]                   DLY_INCDEC,
    output reg  [(DLY_TAP_WIDTH*NUM_DLY)-1:0]   DELAY_TAP_VALUE
); 

localparam DATA_WIDTH           = (IO_TYPE == "SINGLE_ENDED") ? NUM_DLY : (2*NUM_DLY);
localparam NUM_CNTRL            = ((DLY_LOC[39:20] > 0) && (DLY_LOC[19:0] > 0)) ? 2'd2 : 2'd1;
localparam NUM_DLY_CNTRL        = (NUM_CNTRL == 2) ? 20 : NUM_DLY;
localparam [39:0] DLY_LOC_INT   = (DLY_LOC[19:0] == 0) ? {20'd0, DLY_LOC[39:20]} : DLY_LOC;

reg   [(NUM_GB_SITES*NUM_CNTRL)-1:0] usr_dly_ld;
reg   [(NUM_GB_SITES*NUM_CNTRL)-1:0] usr_dly_adj;
reg   [(NUM_GB_SITES*NUM_CNTRL)-1:0] usr_dly_incdec;
wire  [(DLY_TAP_WIDTH*NUM_GB_SITES*NUM_CNTRL)-1:0] usr_delay_tap_value;
reg  [(DLY_TAP_WIDTH*NUM_GB_SITES*NUM_CNTRL)-1:0] dly_tap_value;

wire clk_in;
wire lock;
// Clocking
`ifdef RX_CLOCK
    wire clk_1;
    // IOPAD Input clock
    I_BUF #(
        .WEAK_KEEPER(WEAK_KEEPER),
        .IOSTANDARD(IOSTANDARD)
    ) I_BUF_data (
        .EN(1'd1),
        .I(CLK_IN),
        .O(clk_1)
    );

    CLK_BUF input_clk (
        .I(clk_1),
        .O(clk_in)
    );

`elsif PLL
    wire clk;
    `ifdef LOCAL_OSCILLATOR
        BOOT_CLOCK # (
            .PERIOD(25.0)
        )
        BOOT_CLOCK_inst (
            .O(clk)
        );
    `elsif RX_IO_CLOCK
        wire clk_1;
        // IOPAD Input clock
        I_BUF #(
            .WEAK_KEEPER(WEAK_KEEPER),
            .IOSTANDARD(IOSTANDARD)
        ) I_BUF_data (
            .EN(1'd1),
            .I(CLK_IN),
            .O(clk_1)
        );

        CLK_BUF input_clk (
            .I(clk_1),
            .O(clk)
        );
    `endif

PLL #(
    .PLL_MULT(PLL_MULT),
    .PLL_DIV(PLL_DIV)
)
PLL_inst (
    .PLL_EN(1'd1),
    .CLK_IN(clk),
    .CLK_OUT(clk_in),
    .LOCK(lock)
);
`endif

always @(*) begin
    usr_dly_ld 				= 'h0;
    usr_dly_adj 		    = 'h0;
    usr_dly_incdec 			= 'h0;
    DELAY_TAP_VALUE         = 'h0;

    if (dly_site_addr[SEL_DLY] > 19) begin
        usr_dly_ld[(NUM_GB_SITES + SEL_DLY) - active_idelay_cnt0]     	= DLY_LOAD[SEL_DLY];
        usr_dly_adj[(NUM_GB_SITES + SEL_DLY) - active_idelay_cnt0]   	= DLY_ADJ[SEL_DLY];
        usr_dly_incdec[(NUM_GB_SITES + SEL_DLY) - active_idelay_cnt0] 	= DLY_INCDEC[SEL_DLY];
        DELAY_TAP_VALUE[SEL_DLY*DLY_TAP_WIDTH +:DLY_TAP_WIDTH]          = usr_delay_tap_value[((NUM_GB_SITES + SEL_DLY) - active_idelay_cnt0)*DLY_TAP_WIDTH +: DLY_TAP_WIDTH];
    end
    else begin
        usr_dly_ld[SEL_DLY]     	                                    = DLY_LOAD[SEL_DLY];
        usr_dly_adj[SEL_DLY]   	                                        = DLY_ADJ[SEL_DLY];
        usr_dly_incdec[SEL_DLY] 	                                    = DLY_INCDEC[SEL_DLY];
        DELAY_TAP_VALUE[SEL_DLY*DLY_TAP_WIDTH +:DLY_TAP_WIDTH]          = usr_delay_tap_value[SEL_DLY*DLY_TAP_WIDTH +: DLY_TAP_WIDTH];
    end
end

wire [DLY_TAP_WIDTH-1:0] dly_tap_val_reg [NUM_DLY-1:0];
always @(*) begin
    // dly_tap_value = 'h0;
    dly_tap_value[(dly_site_addr[SEL_DLY] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH] = dly_tap_val_reg[SEL_DLY];
end

wire [(NUM_CNTRL*ADDR_WIDTH)-1:0] f2g_dly_addr;
wire [NUM_CNTRL-1:0] cntrl_dly_ld;
wire [NUM_CNTRL-1:0] cntrl_dly_adj;
wire [NUM_CNTRL-1:0] cntrl_dly_incdec;
wire [(NUM_GB_SITES*NUM_CNTRL)-1:0] delay_ld_dec_out;
wire [(NUM_GB_SITES*NUM_CNTRL)-1:0] delay_adj_dec_out;
wire [(NUM_GB_SITES*NUM_CNTRL)-1:0] delay_incdec_dec_out;
wire [(NUM_CNTRL*DLY_TAP_WIDTH)-1:0] g2f_rx_dly_tap;

genvar j;
generate
    for (j = 0; j < NUM_CNTRL; j = j + 1) begin
        
        DLY_SEL_DECODER DLY_SEL_DECODER_inst (
            .DLY_LOAD(cntrl_dly_ld[j]),
            .DLY_ADJ(cntrl_dly_adj[j]),
            .DLY_INCDEC(cntrl_dly_incdec[j]),
            .DLY_ADDR(f2g_dly_addr[(j*ADDR_WIDTH) +:ADDR_WIDTH]),
            .DLY0_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+0  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+0  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+0  +: 1]}),
            .DLY1_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+1  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+1  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+1  +: 1]}),
            .DLY2_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+2  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+2  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+2  +: 1]}),
            .DLY3_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+3  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+3  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+3  +: 1]}),
            .DLY4_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+4  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+4  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+4  +: 1]}),
            .DLY5_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+5  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+5  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+5  +: 1]}),
            .DLY6_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+6  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+6  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+6  +: 1]}),
            .DLY7_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+7  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+7  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+7  +: 1]}),
            .DLY8_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+8  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+8  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+8  +: 1]}),
            .DLY9_CNTRL( {delay_ld_dec_out[(j*NUM_GB_SITES)+9  +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+9  +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+9  +: 1]}),
            .DLY10_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+10 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+10 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+10 +: 1]}),
            .DLY11_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+11 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+11 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+11 +: 1]}),
            .DLY12_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+12 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+12 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+12 +: 1]}),
            .DLY13_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+13 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+13 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+13 +: 1]}),
            .DLY14_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+14 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+14 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+14 +: 1]}),
            .DLY15_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+15 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+15 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+15 +: 1]}),
            .DLY16_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+16 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+16 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+16 +: 1]}),
            .DLY17_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+17 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+17 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+17 +: 1]}),
            .DLY18_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+18 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+18 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+18 +: 1]}),
            .DLY19_CNTRL({delay_ld_dec_out[(j*NUM_GB_SITES)+19 +: 1], delay_adj_dec_out[(j*NUM_GB_SITES)+19 +: 1], delay_incdec_dec_out[(j*NUM_GB_SITES)+19 +: 1]})
        );

        DLY_VALUE_MUX DLY_VALUE_MUX_inst (
            .DLY_TAP0_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(0*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP1_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(1*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP2_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(2*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP3_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(3*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP4_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(4*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP5_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(5*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP6_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(6*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP7_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(7*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP8_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(8*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP9_VAL( dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(9*DLY_TAP_WIDTH) )  +:DLY_TAP_WIDTH]),
            .DLY_TAP10_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(10*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP11_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(11*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP12_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(12*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP13_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(13*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP14_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(14*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP15_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(15*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP16_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(16*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP17_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(17*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP18_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(18*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_TAP19_VAL(dly_tap_value[((j*(NUM_GB_SITES*DLY_TAP_WIDTH))+(19*DLY_TAP_WIDTH))  +:DLY_TAP_WIDTH]),
            .DLY_ADDR(f2g_dly_addr[(j*ADDR_WIDTH) +:ADDR_WIDTH]),
            .DLY_TAP_VALUE(g2f_rx_dly_tap[(j*DLY_TAP_WIDTH) +:DLY_TAP_WIDTH])
        );

        DLY_ADDR_CNTRL #(
            .ADDR_WIDTH(ADDR_WIDTH),
            .DLY_LOC(DLY_LOC_INT[(j*NUM_GB_SITES) +:NUM_GB_SITES]),
            .DLY_TAP_WIDTH(DLY_TAP_WIDTH),
            .NUM_DLY(NUM_DLY_CNTRL)
        ) DLY_ADDR_CNTRL_inst (
            .cntrl_dly_tap_value(g2f_rx_dly_tap[(j*DLY_TAP_WIDTH) +:DLY_TAP_WIDTH]),
            .rst(RESET),
            .usr_dly_ld(usr_dly_ld[(j*NUM_GB_SITES) +:NUM_GB_SITES]),
            .usr_dly_adj(usr_dly_adj[(j*NUM_GB_SITES) +:NUM_GB_SITES]),
            .usr_dly_incdec(usr_dly_incdec[(j*NUM_GB_SITES) +:NUM_GB_SITES]),
            .usr_rd_dly_value(1'd0),
            .cntrl_dly_ld(cntrl_dly_ld[j]),
            .cntrl_dly_adj(cntrl_dly_adj[j]),
            .cntrl_dly_incdec(cntrl_dly_incdec[j]),
            .f2g_dly_addr(f2g_dly_addr[(j*ADDR_WIDTH) +:ADDR_WIDTH]),
            .usr_dly_tap_value_out(usr_delay_tap_value[(j*(NUM_GB_SITES*DLY_TAP_WIDTH)) +:(NUM_GB_SITES*DLY_TAP_WIDTH)])
        );
    end
endgenerate

reg [(NUM_CNTRL*NUM_GB_SITES)-1:0] delay_adj;
reg [(NUM_CNTRL*NUM_GB_SITES)-1:0] delay_incdec;

always @(*) begin
    if (DELAY_TYPE == "STATIC") begin
        delay_adj       = 'd0;
        delay_incdec    = 'd0;
    end
    else begin
        delay_adj       = delay_adj_dec_out;
        delay_incdec    = delay_incdec_dec_out;
    end
end

integer ACT_IDLY_CNT;
integer active_idelay_cnt0;
integer active_idelay_cnt1;
reg [NUM_DLY-1:0]                delay_location_index [NUM_GB_SITES-1:0];
reg [(NUM_CNTRL*ADDR_WIDTH)-1:0] dly_site_addr [NUM_DLY-1:0];

function integer act_dly_cnt (input [(NUM_CNTRL*NUM_GB_SITES)-1:0] valid_sites);
integer i;
begin
    act_dly_cnt = 0;
    active_idelay_cnt0= 0;
    active_idelay_cnt1 = 0;
    for (i = 0 ; i<(NUM_CNTRL*NUM_GB_SITES) ; i=i+1)
    begin
        delay_location_index[i] = NUM_DLY;
        if (DLY_LOC_INT[i] == 1'b1) begin
            dly_site_addr[act_dly_cnt] = i;
            delay_location_index[i] = act_dly_cnt;
            act_dly_cnt = act_dly_cnt+1;  // order is important for counting
            if (i < NUM_GB_SITES)
                active_idelay_cnt0 = active_idelay_cnt0 + 1;
            else
                active_idelay_cnt1 = active_idelay_cnt1 + 1;
        end
    end
end
endfunction

always @(*) begin
    if (RESET)
        ACT_IDLY_CNT    = 'h0;
    else
        ACT_IDLY_CNT    = act_dly_cnt(NUM_GB_SITES*NUM_CNTRL);
end

`ifdef bidirectional
wire  [(NUM_DLY/2)-1:0] i_buf_out;
wire  [(NUM_DLY/2)-1:0] odly_out;

generate
    for(genvar i = 0; i < NUM_DLY/2; i = i + 1) begin
        `ifdef I_DELAY_O_DELAY
            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(DIN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUF # (
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUF_inst (
                    .I(odly_out[i]),
                    .O(DOUT_ODLY[i])
                );
            
            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(DIN_IDLY[i+(NUM_DLY/2)]),
                    .I_P(DIN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUF_DS (
                    .I(odly_out[i]),
                    .O_P(DOUT_ODLY[i]),
                    .O_N(DOUT_ODLY[i+(NUM_DLY/2)])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+0]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(DOUT_IDLY[i])
            );

            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(DIN_ODLY[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );

        `elsif I_DELAY_I_SERDES_O_DELAY_O_SERDES
            wire [(NUM_DLY/2)-1:0] idly_out;
            wire [(NUM_DLY/2)-1:0] serdes_clk_out;
            wire [(NUM_DLY/2)-1:0] serdes_out;
            wire [(NUM_DLY/2)-1:0] odly_out;
            wire [(NUM_DLY/2)-1:0] oe_out;

            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(SDATA_IN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUFT # (
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUFT_inst (
                    .I(odly_out[i]),
                    .T(oe_out[i]),
                    .O(SDATA_OUT_ODLY[i])
                );

            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(SDATA_IN_IDLY[i+(NUM_DLY/2)]),
                    .I_P(SDATA_IN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUFT_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUFT_DS (
                    .I(odly_out[i]),
                    .T(oe_out[i]),
                    .O_P(SDATA_OUT_ODLY[i]),
                    .O_N(SDATA_OUT_ODLY[i+(NUM_DLY/2)])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+0]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(idly_out[i])
            );

            I_SERDES # (
                .DATA_RATE(DATA_RATE),
                .WIDTH(WIDTH),
                .DPA_MODE(DPA_MODE)
            )
            I_SERDES_inst (
                .D(idly_out[i]),
                .RST(~RESET),
                .BITSLIP_ADJ(BITSLIP_ADJ[i]),
                .EN(EN[i]),
                .CLK_IN(serdes_clk_out[i]),
                .CLK_OUT(serdes_clk_out[i]),
                .Q(PDATA_OUT_ISERDES[(i*WIDTH) +:WIDTH]),
                .DATA_VALID(DATA_VALID_ISERDES[i]),
                .DPA_LOCK(DPA_LOCK[i]),
                .DPA_ERROR(DPA_ERROR[i]),
                .PLL_LOCK(lock),
                .PLL_CLK(clk_in)
            );
            assign CLK_OUT[i] = serdes_clk_out[i];

            O_SERDES #(
                .DATA_RATE(DATA_RATE),
                .WIDTH(WIDTH)
            )
            O_SERDES_inst (
                .D(PDATA_IN_OSERDES[(i*WIDTH) +:WIDTH]),
                .RST(~RESET),
                .DATA_VALID(DATA_VALID_OSERDES[i]),
                .CLK_IN(FAB_CLK_IN),
                .OE_IN(OE_IN[i]),
                .OE_OUT(oe_out[i]),
                .Q(serdes_out[i]),
                .CHANNEL_BOND_SYNC_IN(),
                .CHANNEL_BOND_SYNC_OUT(),
                .PLL_LOCK(lock),
                .PLL_CLK(clk_in)
            );
            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(serdes_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );

        `elsif I_DELAY_I_DDR_O_DELAY_O_DDR
            wire [(NUM_DLY/2)-1:0] idly_out;
            wire [(NUM_DLY/2)-1:0] oddr_out;
            wire [(NUM_DLY/2)-1:0] odly_out;
            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(SD_IN_IDDR[i]),
                    .O(i_buf_out[i])
                );

                O_BUF # (
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUF_inst (
                    .I(odly_out[i]),
                    .O(SD_OUT_ODDR[i])
                );
            
            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(SD_IN_IDDR[i+(NUM_DLY/2)]),
                    .I_P(SD_IN_IDDR[i]),
                    .O(i_buf_out[i])
                );

                O_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUF_DS (
                    .I(odly_out[i]),
                    .O_P(SD_OUT_ODDR[i]),
                    .O_N(SD_OUT_ODDR[i+(NUM_DLY/2)])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+0]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(idly_out[i])
            );
            I_DDR I_DDR_inst (
                .D(idly_out[i]),
                .R(RESET),
                .E(EN_IDDR[i]),
                .C(clk_in),
                .Q(DD_OUT_IDDR[(i*2) +:2])
            );
        
            O_DDR O_DDR_inst (
                .D(DD_IN_ODDR[(i*2) +:2]),
                .R(RESET),
                .E(EN_ODDR[i]),
                .C(clk_in),
                .Q(oddr_out[i])
            );
            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(oddr_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );

        `elsif I_DELAY_O_DELAY_O_SERDES
            wire [(NUM_DLY/2)-1:0] serdes_out;
            wire [(NUM_DLY/2)-1:0] odly_out;
            wire [(NUM_DLY/2)-1:0] oe_out;
            
            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(DIN_IDLY[i]),
                    .O(i_buf_out[i])
                );
                O_BUFT # (
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUFT_inst (
                    .I(odly_out[i]),
                    .T(oe_out[i]),
                    .O(SDATA_OUT_ODLY[i])
                );
                
            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(DIN_IDLY[i+(NUM_DLY/2)]),
                    .I_P(DIN_IDLY[i]),
                    .O(i_buf_out[i])
                );
                O_BUFT_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUFT_DS (
                    .I(odly_out[i]),
                    .T(oe_out[i]),
                    .O_P(SDATA_OUT_ODLY[i]),
                    .O_N(SDATA_OUT_ODLY[i+(NUM_DLY/2)])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(DOUT_IDLY[i])
            );

            O_SERDES #(
                .DATA_RATE(DATA_RATE),
                .WIDTH(WIDTH)
            )
            O_SERDES_inst (
                .D(PDATA_IN_OSERDES[(i*WIDTH) +:WIDTH]),
                .RST(~RESET),
                .DATA_VALID(DATA_VALID_OSERDES[i]),
                .CLK_IN(FAB_CLK_IN),
                .OE_IN(OE_IN[i]),
                .OE_OUT(oe_out[i]),
                .Q(serdes_out[i]),
                .CHANNEL_BOND_SYNC_IN(),
                .CHANNEL_BOND_SYNC_OUT(),
                .PLL_LOCK(lock),
                .PLL_CLK(clk_in)
            );
            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(serdes_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );

        `elsif I_DELAY_O_DELAY_O_DDR
            wire [(NUM_DLY/2)-1:0] oddr_out;
            wire [(NUM_DLY/2)-1:0] odly_out;

            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(DIN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUF # (
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUF_inst (
                    .I(odly_out[i]),
                    .O(SD_OUT_ODDR[i])
                );

            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(DIN_IDLY[i+(NUM_DLY/2)]),
                    .I_P(DIN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUF_DS (
                    .I(odly_out[i]),
                    .O_P(SD_OUT_ODDR[i]),
                    .O_N(SD_OUT_ODDR[i+(NUM_DLY/2)])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+0]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(DOUT_IDLY[i])
            );

            O_DDR O_DDR_inst (
                .D(DD_IN_ODDR[(i*2) +:2]),
                .R(RESET),
                .E(EN_ODDR[i]),
                .C(clk_in),
                .Q(oddr_out[i])
            );
            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(oddr_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );

        `elsif I_DELAY_I_SERDES_O_DELAY
            wire [(NUM_DLY/2)-1:0] odly_out;
            wire [(NUM_DLY/2)-1:0] idly_out;
            wire [(NUM_DLY/2)-1:0] serdes_clk_out;

            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(SDATA_IN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUF # (
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUF_inst (
                    .I(odly_out[i]),
                    .O(DOUT_ODLY[i])
                );

            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(SDATA_IN_IDLY[i+(NUM_DLY/2)]),
                    .I_P(SDATA_IN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUF_DS (
                    .I(odly_out[i]),
                    .O_P(DOUT_ODLY[i]),
                    .O_N(DOUT_ODLY[i+(NUM_DLY/2)])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+0]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(idly_out[i])
            );

            I_SERDES # (
                .DATA_RATE(DATA_RATE),
                .WIDTH(WIDTH),
                .DPA_MODE(DPA_MODE)
            )
            I_SERDES_inst (
                .D(idly_out[i]),
                .RST(~RESET),
                .BITSLIP_ADJ(BITSLIP_ADJ[i]),
                .EN(EN_ISERDES[i]),
                .CLK_IN(serdes_clk_out[i]),
                .CLK_OUT(serdes_clk_out[i]),
                .Q(PDATA_OUT_ISERDES[(i*WIDTH) +:WIDTH]),
                .DATA_VALID(DATA_VALID_ISERDES[i]),
                .DPA_LOCK(DPA_LOCK[i]),
                .DPA_ERROR(DPA_ERROR[i]),
                .PLL_LOCK(lock),
                .PLL_CLK(clk_in)
            );
            assign CLK_OUT[i] = serdes_clk_out[i];

            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(DIN_ODLY[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );
        
        `elsif I_DELAY_I_SERDES_O_DELAY_O_DDR
            wire [(NUM_DLY/2)-1:0] serdes_clk_out;
            wire [(NUM_DLY/2)-1:0] odly_out;
            wire [(NUM_DLY/2)-1:0] oddr_out;
            wire [(NUM_DLY/2)-1:0] idly_out;

            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(SDATA_IN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUF # (
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUF_inst (
                    .I(odly_out[i]),
                    .O(SD_OUT_ODDR[i])
                );
            
            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(SDATA_IN_IDLY[i+(NUM_DLY/2)]),
                    .I_P(SDATA_IN_IDLY[i]),
                    .O(i_buf_out[i])
                );

                O_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUF_DS (
                    .I(odly_out[i]),
                    .O_P(SD_OUT_ODDR[i]),
                    .O_N(SD_OUT_ODDR[i+(NUM_DLY/2)])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+0]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(idly_out[i])
            );

            I_SERDES # (
                .DATA_RATE(DATA_RATE),
                .WIDTH(WIDTH),
                .DPA_MODE(DPA_MODE)
            )
            I_SERDES_inst (
                .D(idly_out[i]),
                .RST(~RESET),
                .BITSLIP_ADJ(BITSLIP_ADJ[i]),
                .EN(EN_ISERDES[i]),
                .CLK_IN(serdes_clk_out[i]),
                .CLK_OUT(serdes_clk_out[i]),
                .Q(PDATA_OUT_ISERDES[(i*WIDTH) +:WIDTH]),
                .DATA_VALID(DATA_VALID_ISERDES[i]),
                .DPA_LOCK(DPA_LOCK[i]),
                .DPA_ERROR(DPA_ERROR[i]),
                .PLL_LOCK(lock),
                .PLL_CLK(clk_in)
            );
            assign CLK_OUT[i] = serdes_clk_out[i];

            O_DDR O_DDR_inst (
                .D(DD_IN_ODDR[(i*2) +:2]),
                .R(RESET),
                .E(EN_ODDR[i]),
                .C(clk_in),
                .Q(oddr_out[i])
            );
            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(oddr_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );
        
        `elsif I_DELAY_I_DDR_O_DELAY
            wire  [(NUM_DLY/2)-1:0] idly_out;
            wire  [(NUM_DLY/2)-1:0] odly_out;
            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(SD_IN_IDDR[i]),
                    .O(i_buf_out[i])
                );

                O_BUF # (
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUF_inst (
                    .I(odly_out[i]),
                    .O(DOUT_ODLY[i])
                );
            
            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(SD_IN_IDDR[i+(NUM_DLY/2)]),
                    .I_P(SD_IN_IDDR[i]),
                    .O(i_buf_out[i])
                );

                O_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUF_DS (
                    .I(odly_out[i]),
                    .O_P(DOUT_ODLY[i]),
                    .O_N(DOUT_ODLY[i+(NUM_DLY/2)])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+0]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(idly_out[i])
            );
            I_DDR I_DDR_inst (
                .D(idly_out[i]),
                .R(RESET),
                .E(EN_IDDR[i]),
                .C(clk_in),
                .Q(DD_OUT_IDDR[(i*2) +:2])
            );

            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(DIN_ODLY[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );

        `elsif I_DELAY_I_DDR_O_DELAY_O_SERDES
            wire  [(NUM_DLY/2)-1:0] idly_out;
            wire  [(NUM_DLY/2)-1:0] odly_out;
            wire  [(NUM_DLY/2)-1:0] serdes_out;
            wire  [(NUM_DLY/2)-1:0] oe_out;

            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(SD_IN_IDDR[i]),
                    .O(i_buf_out[i])
                );

                O_BUFT # (
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD),
                    .DRIVE_STRENGTH(DRIVE_STRENGTH),
                    .SLEW_RATE(SLEW_RATE)
                )
                O_BUFT_inst (
                    .I(odly_out[i]),
                    .T(oe_out[i]),
                    .O(SDATA_OUT_ODLY[i])
                );

            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(SD_IN_IDDR[i+(NUM_DLY/2)]),
                    .I_P(SD_IN_IDDR[i]),
                    .O(i_buf_out[i])
                );

                O_BUFT_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) O_BUFT_DS (
                    .I(odly_out[i]),
                    .T(oe_out[i]),
                    .O_P(SDATA_OUT_ODLY[i]),
                    .O_N(SDATA_OUT_ODLY[i+(NUM_DLY/2)])
                );
            `endif
            
            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+0]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+0]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+0]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+0]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+0] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(idly_out[i])
            );
            I_DDR I_DDR_inst (
                .D(idly_out[i]),
                .R(RESET),
                .E(EN_IDDR[i]),
                .C(clk_in),
                .Q(DD_OUT_IDDR[(i*2) +:2])
            );

            O_SERDES #(
                .DATA_RATE(DATA_RATE),
                .WIDTH(WIDTH)
            )
            O_SERDES_inst (
                .D(PDATA_IN_OSERDES[(i*WIDTH) +:WIDTH]),
                .RST(~RESET),
                .DATA_VALID(DATA_VALID_OSERDES[i]),
                .CLK_IN(FAB_CLK_IN),
                .OE_IN(OE_IN[i]),
                .OE_OUT(oe_out[i]),
                .Q(serdes_out[i]),
                .CHANNEL_BOND_SYNC_IN(),
                .CHANNEL_BOND_SYNC_OUT(),
                .PLL_LOCK(lock),
                .PLL_CLK(clk_in)
            );
            O_DELAY #(
                .DELAY(DELAY)
            ) O_DELAY_inst (
                .CLK_IN(clk_in),
                .I(serdes_out[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[(i*2)+1]]),
                .DLY_ADJ(delay_adj[dly_site_addr[(i*2)+1]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[(i*2)+1]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[(i*2)+1]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[(i*2)+1] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(odly_out[i])
            );

        `endif
    end
endgenerate

`elsif unidirectional
wire  [NUM_DLY-1:0] i_buf_dout;
generate
    for(genvar i = 0; i < NUM_DLY; i = i + 1) begin
        // --------------------------------------------------------- //
        `ifdef I_DELAY
            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(DATA_IN[i]),
                    .O(i_buf_dout[i])
                );
            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(DATA_IN[i+NUM_DLY]),
                    .I_P(DATA_IN[i]),
                    .O(i_buf_dout[i])
                );
            `endif

            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_dout[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[i]]),
                .DLY_ADJ(delay_adj[dly_site_addr[i]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[i]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[i]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[i] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(DATA_OUT[i])
            );

        // --------------------------------------------------------- //
        `elsif I_DELAY_I_SERDES
            wire [NUM_DLY-1:0] dly_out;
            wire [NUM_DLY-1:0] serdes_clk_out;
            `ifdef SINGLE_ENDED
                I_BUF #(
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .IOSTANDARD(IOSTANDARD)
                ) I_BUF_data (
                    .EN(1'd1),
                    .I(SDATA_IN[i]),
                    .O(i_buf_dout[i])
                );
            `elsif DIFFERENTIAL
                I_BUF_DS #(
                    .IOSTANDARD(IOSTANDARD),
                    .WEAK_KEEPER(WEAK_KEEPER),
                    .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                ) I_BUF_DS (
                    .EN(1'd1),
                    .I_N(SDATA_IN[i+NUM_DLY]),
                    .I_P(SDATA_IN[i]),
                    .O(i_buf_dout[i])
                );
            `endif
            
            I_DELAY #(
                .DELAY(DELAY)
            ) I_DELAY_inst (
                .CLK_IN(clk_in),
                .I(i_buf_dout[i]),
                .DLY_LOAD(delay_ld_dec_out[dly_site_addr[i]]),
                .DLY_ADJ(delay_adj[dly_site_addr[i]]),
                .DLY_INCDEC(delay_incdec[dly_site_addr[i]]),
                .DLY_TAP_VALUE(dly_tap_val_reg[i]),
                // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[i] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                .O(dly_out[i])
            );
            I_SERDES # (
                .DATA_RATE(DATA_RATE),
                .WIDTH(WIDTH),
                .DPA_MODE(DPA_MODE)
            )
            I_SERDES_inst (
                .D(dly_out[i]),
                .RST(~RESET),
                .BITSLIP_ADJ(BITSLIP_ADJ[i]),
                .EN(EN[i]),
                .CLK_IN(serdes_clk_out[i]),
                .CLK_OUT(serdes_clk_out[i]),
                .Q(PDATA_OUT[(i*WIDTH) +:WIDTH]),
                .DATA_VALID(DATA_VALID[i]),
                .DPA_LOCK(DPA_LOCK[i]),
                .DPA_ERROR(DPA_ERROR[i]),
                .PLL_LOCK(lock),
                .PLL_CLK(clk_in)
            );
            assign CLK_OUT[i] = serdes_clk_out[i];

            // --------------------------------------------------------- //
            `elsif I_DELAY_I_DDR
                wire [NUM_DLY-1:0] dly_out;
                wire [NUM_DLY-1:0] serdes_clk_out;
                `ifdef SINGLE_ENDED
                    I_BUF #(
                        .WEAK_KEEPER(WEAK_KEEPER),
                        .IOSTANDARD(IOSTANDARD)
                    ) I_BUF_data (
                        .EN(1'd1),
                        .I(SD_IN[i]),
                        .O(i_buf_dout[i])
                    );
                `elsif DIFFERENTIAL
                    I_BUF_DS #(
                        .IOSTANDARD(IOSTANDARD),
                        .WEAK_KEEPER(WEAK_KEEPER),
                        .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                    ) I_BUF_DS (
                        .EN(1'd1),
                        .I_N(SD_IN[i+NUM_DLY]),
                        .I_P(SD_IN[i]),
                        .O(i_buf_dout[i])
                    );
                `endif
                
                I_DELAY #(
                    .DELAY(DELAY)
                ) I_DELAY_inst (
                    .CLK_IN(clk_in),
                    .I(i_buf_dout[i]),
                    .DLY_LOAD(delay_ld_dec_out[dly_site_addr[i]]),
                    .DLY_ADJ(delay_adj[dly_site_addr[i]]),
                    .DLY_INCDEC(delay_incdec[dly_site_addr[i]]),
                    .DLY_TAP_VALUE(dly_tap_val_reg[i]),
                    // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[i] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                    .O(dly_out[i])
                );
                I_DDR I_DDR_inst (
                    .D(dly_out[i]),
                    .R(RESET),
                    .E(EN[i]),
                    .C(clk_in),
                    .Q(DD_OUT[(i*2) +:2])
                );
            
            // --------------------------------------------------------- //
            `elsif O_DELAY
                wire [NUM_DLY-1:0] dly_out;
                O_DELAY #(
                    .DELAY(DELAY)
                ) O_DELAY_inst (
                    .CLK_IN(clk_in),
                    .I(DATA_IN[i]),
                    .DLY_LOAD(delay_ld_dec_out[dly_site_addr[i]]),
                    .DLY_ADJ(delay_adj[dly_site_addr[i]]),
                    .DLY_INCDEC(delay_incdec[dly_site_addr[i]]),
                    .DLY_TAP_VALUE(dly_tap_val_reg[i]),
                    // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[i] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                    .O(dly_out[i])
                );

                `ifdef SINGLE_ENDED
                    O_BUF # (
                        .IOSTANDARD(IOSTANDARD),
                        .DRIVE_STRENGTH(DRIVE_STRENGTH),
                        .SLEW_RATE(SLEW_RATE)
                    )
                    O_BUF_inst (
                        .I(dly_out[i]),
                        .O(DATA_OUT[i])
                    );
                `elsif DIFFERENTIAL
                    O_BUF_DS #(
                        .IOSTANDARD(IOSTANDARD),
                        .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                    ) O_BUF_DS (
                        .I(dly_out[i]),
                        .O_P(DATA_OUT[i]),
                        .O_N(DATA_OUT[i+NUM_DLY])
                    );
                `endif
            
            // --------------------------------------------------------- //
            `elsif O_SERDES_O_DELAY
                wire [NUM_DLY-1:0] serdes_out;
                wire [NUM_DLY-1:0] odly_out;
                wire [NUM_DLY-1:0] oe_out;

                O_SERDES #(
                    .DATA_RATE(DATA_RATE),
                    .WIDTH(WIDTH)
                )
                O_SERDES_inst (
                    .D(PDATA_IN[(i*WIDTH) +:WIDTH]),
                    .RST(~RESET),
                    .DATA_VALID(DATA_VALID[i]),
                    .CLK_IN(FAB_CLK_IN),
                    .OE_IN(OE_IN[i]),
                    .OE_OUT(oe_out[i]),
                    .Q(serdes_out[i]),
                    .CHANNEL_BOND_SYNC_IN(),
                    .CHANNEL_BOND_SYNC_OUT(),
                    .PLL_LOCK(lock),
                    .PLL_CLK(clk_in)
                );
                O_DELAY #(
                    .DELAY(DELAY)
                ) O_DELAY_inst (
                    .CLK_IN(clk_in),
                    .I(serdes_out[i]),
                    .DLY_LOAD(delay_ld_dec_out[dly_site_addr[i]]),
                    .DLY_ADJ(delay_adj[dly_site_addr[i]]),
                    .DLY_INCDEC(delay_incdec[dly_site_addr[i]]),
                    .DLY_TAP_VALUE(dly_tap_val_reg[i]),
                    // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[i] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                    .O(odly_out[i])
                );
                `ifdef SINGLE_ENDED
                    O_BUFT # (
                        .WEAK_KEEPER(WEAK_KEEPER),
                        .IOSTANDARD(IOSTANDARD),
                        .DRIVE_STRENGTH(DRIVE_STRENGTH),
                        .SLEW_RATE(SLEW_RATE)
                    )
                    O_BUFT_inst (
                        .I(odly_out[i]),
                        .T(oe_out[i]),
                        .O(SDATA_OUT[i])
                    );
                `elsif DIFFERENTIAL
                    O_BUFT_DS #(
                        .IOSTANDARD(IOSTANDARD),
                        .WEAK_KEEPER(WEAK_KEEPER),
                        .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                    ) O_BUFT_DS (
                        .I(odly_out[i]),
                        .T(oe_out[i]),
                        .O_P(SDATA_OUT[i]),
                        .O_N(SDATA_OUT[i+NUM_DLY])
                    );
                `endif
            
            // --------------------------------------------------------- //
            `elsif O_DDR_O_DELAY
                wire [NUM_DLY-1:0] oddr_out;
                wire [NUM_DLY-1:0] odly_out;
                O_DDR O_DDR_inst (
                    .D(DD_IN[(i*2) +:2]),
                    .R(RESET),
                    .E(EN[i]),
                    .C(clk_in),
                    .Q(oddr_out[i])
                );
                O_DELAY #(
                    .DELAY(DELAY)
                ) O_DELAY_inst (
                    .CLK_IN(clk_in),
                    .I(oddr_out[i]),
                    .DLY_LOAD(delay_ld_dec_out[dly_site_addr[i]]),
                    .DLY_ADJ(delay_adj[dly_site_addr[i]]),
                    .DLY_INCDEC(delay_incdec[dly_site_addr[i]]),
                    .DLY_TAP_VALUE(dly_tap_val_reg[i]),
                    // .DLY_TAP_VALUE(dly_tap_value[(dly_site_addr[i] * DLY_TAP_WIDTH) +: DLY_TAP_WIDTH]),
                    .O(odly_out[i])
                );
                `ifdef SINGLE_ENDED
                    O_BUF # (
                        .IOSTANDARD(IOSTANDARD),
                        .DRIVE_STRENGTH(DRIVE_STRENGTH),
                        .SLEW_RATE(SLEW_RATE)
                    )
                    O_BUF_inst (
                        .I(odly_out[i]),
                        .O(SD_OUT[i])
                    );
                `elsif DIFFERENTIAL
                    O_BUF_DS #(
                        .IOSTANDARD(IOSTANDARD),
                        .DIFFERENTIAL_TERMINATION(DIFFERENTIAL_TERMINATION)
                    ) O_BUF_DS (
                        .I(odly_out[i]),
                        .O_P(SD_OUT[i]),
                        .O_N(SD_OUT[i+NUM_DLY])
                    );
                `endif
        `endif
    end
endgenerate
`endif

endmodule