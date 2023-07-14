// Copyright (C) 2022 RapidSilicon
//11/11/2022
// In Genesis3, parameters MODE_BITS vectors have been reversed
// in order to match big endian behavior used by the fabric
// primitives DSP/BRAM (CASTORIP-121)

module TDP_BRAM18 (
    (* clkbuf_sink *)
    input wire CLOCKA,
    (* clkbuf_sink *)
    input wire CLOCKB,
    input wire READENABLEA,
    input wire READENABLEB,
    input wire [13:0] ADDRA,
    input wire [13:0] ADDRB,
    input wire [15:0] WRITEDATAA,
    input wire [15:0] WRITEDATAB,
    input wire [1:0] WRITEDATAAP,
    input wire [1:0] WRITEDATABP,
    input wire WRITEENABLEA,
    input wire WRITEENABLEB,
    input wire [1:0] BYTEENABLEA,
    input wire [1:0] BYTEENABLEB,
    //input [2:0] WRITEDATAWIDTHA,
    //input [2:0] WRITEDATAWIDTHB,
    //input [2:0] READDATAWIDTHA,
    //input [2:0] READDATAWIDTHB,
    output wire [15:0] READDATAA,
    output wire [15:0] READDATAB,
    output wire [1:0] READDATAAP,
    output wire [1:0] READDATABP
);
    parameter INITP_00 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INITP_01 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INITP_02 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INITP_03 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INITP_04 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INITP_05 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INITP_06 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INITP_07 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_00 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_01 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_02 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_03 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_04 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_05 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_06 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_07 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_08 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_09 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_0A = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_0B = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_0C = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_0D = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_0E = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_0F = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_10 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_11 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_12 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_13 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_14 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_15 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_16 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_17 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_18 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_19 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_1A = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_1B = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_1C = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_1D = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_1E = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_1F = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_20 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_21 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_22 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_23 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_24 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_25 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_26 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_27 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_28 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_29 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_2A = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_2B = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_2C = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_2D = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_2E = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_2F = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_30 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_31 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_32 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_33 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_34 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_35 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_36 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_37 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_38 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_39 = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_3A = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_3B = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_3C = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_3D = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_3E = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter INIT_3F = 256'h0000000000000000000000000000000000000000000000000000000000000000;
    parameter integer READ_WIDTH_A = 0;
    parameter integer READ_WIDTH_B = 0;
    parameter integer WRITE_WIDTH_A = 0;
    parameter integer WRITE_WIDTH_B = 0;

endmodule

`default_nettype wire
module RS_TDP36K (
//    RESET_n,
    WEN_A1,
    WEN_B1,
    REN_A1,
    REN_B1,
    CLK_A1,
    CLK_B1,
    BE_A1,
    BE_B1,
    ADDR_A1,
    ADDR_B1,
    WDATA_A1,
    WDATA_B1,
    RDATA_A1,
    RDATA_B1,
    FLUSH1,
    WEN_A2,
    WEN_B2,
    REN_A2,
    REN_B2,
    CLK_A2,
    CLK_B2,
    BE_A2,
    BE_B2,
    ADDR_A2,
    ADDR_B2,
    WDATA_A2,
    WDATA_B2,
    RDATA_A2,
    RDATA_B2,
    FLUSH2
);
    parameter [0:80] MODE_BITS = 81'd0;

    // First 18K RAMFIFO (41 bits)
    localparam [0:0] SYNC_FIFO1_i  = MODE_BITS[0];
    localparam [0:2] RMODE_A1_i    = MODE_BITS[1:3];
    localparam [0:2] RMODE_B1_i    = MODE_BITS[4:6];
    localparam [0:2] WMODE_A1_i    = MODE_BITS[7:9];
    localparam [0:2] WMODE_B1_i    = MODE_BITS[10:12];
    localparam [0:0] FMODE1_i      = MODE_BITS[13];
    localparam [0:0] POWERDN1_i    = MODE_BITS[14];
    localparam [0:0] SLEEP1_i      = MODE_BITS[15];
    localparam [0:0] PROTECT1_i    = MODE_BITS[16];
    localparam [0:11] UPAE1_i       = MODE_BITS[17:28];
    localparam [0:11] UPAF1_i       = MODE_BITS[29:40];

    // Second 18K RAMFIFO (39 bits)
    localparam [0:0] SYNC_FIFO2_i  = MODE_BITS[41];
    localparam [0:2] RMODE_A2_i    = MODE_BITS[42:44];
    localparam [0:2] RMODE_B2_i    = MODE_BITS[45:47];
    localparam [0:2] WMODE_A2_i    = MODE_BITS[48:50];
    localparam [0:2] WMODE_B2_i    = MODE_BITS[51:53];
    localparam [0:0] FMODE2_i      = MODE_BITS[54];
    localparam [0:0] POWERDN2_i    = MODE_BITS[55];
    localparam [0:0] SLEEP2_i      = MODE_BITS[56];
    localparam [0:0] PROTECT2_i    = MODE_BITS[57];
    localparam [0:10] UPAE2_i       = MODE_BITS[58:68];
    localparam [0:10] UPAF2_i       = MODE_BITS[69:79];

    // Split (1 bit)
    localparam [0:0] SPLIT_i       = MODE_BITS[80];

    parameter [36863:0] INIT_i = 36864'h0;

 //   input wire RESET_n;

    input wire WEN_A1;
    input wire WEN_B1;
    input wire REN_A1;
    input wire REN_B1;
    (* clkbuf_sink *)
    input wire CLK_A1;
    (* clkbuf_sink *)
    input wire CLK_B1;
    input wire [1:0] BE_A1;
    input wire [1:0] BE_B1;
    input wire [14:0] ADDR_A1;
    input wire [14:0] ADDR_B1;
    input wire [17:0] WDATA_A1;
    input wire [17:0] WDATA_B1;
    output reg [17:0] RDATA_A1;
    output reg [17:0] RDATA_B1;
    input wire FLUSH1;
    input wire WEN_A2;
    input wire WEN_B2;
    input wire REN_A2;
    input wire REN_B2;
    (* clkbuf_sink *)
    input wire CLK_A2;
    (* clkbuf_sink *)
    input wire CLK_B2;
    input wire [1:0] BE_A2;
    input wire [1:0] BE_B2;
    input wire [13:0] ADDR_A2;
    input wire [13:0] ADDR_B2;
    input wire [17:0] WDATA_A2;
    input wire [17:0] WDATA_B2;
    output reg [17:0] RDATA_A2;
    output reg [17:0] RDATA_B2;
    input wire FLUSH2;
    wire EMPTY2;
    wire EPO2;
    wire EWM2;
    wire FULL2;
    wire FMO2;
    wire FWM2;
    wire EMPTY1;
    wire EPO1;
    wire EWM1;
    wire FULL1;
    wire FMO1;
    wire FWM1;
    wire UNDERRUN1;
    wire OVERRUN1;
    wire UNDERRUN2;
    wire OVERRUN2;
    wire UNDERRUN3;
    wire OVERRUN3;
    wire EMPTY3;
    wire EPO3;
    wire EWM3;
    wire FULL3;
    wire FMO3;
    wire FWM3;
    wire ram_fmode1;
    wire ram_fmode2;
    wire [17:0] ram_rdata_a1;
    wire [17:0] ram_rdata_b1;
    wire [17:0] ram_rdata_a2;
    wire [17:0] ram_rdata_b2;
    reg [17:0] ram_wdata_a1;
    reg [17:0] ram_wdata_b1;
    reg [17:0] ram_wdata_a2;
    reg [17:0] ram_wdata_b2;
    reg [14:0] laddr_a1;
    reg [14:0] laddr_b1;
    wire [13:0] ram_addr_a1;
    wire [13:0] ram_addr_b1;
    wire [13:0] ram_addr_a2;
    wire [13:0] ram_addr_b2;
    wire smux_clk_a1;
    wire smux_clk_b1;
    wire smux_clk_a2;
    wire smux_clk_b2;
    reg [1:0] ram_be_a1;
    reg [1:0] ram_be_a2;
    reg [1:0] ram_be_b1;
    reg [1:0] ram_be_b2;
    wire [2:0] ram_rmode_a1;
    wire [2:0] ram_wmode_a1;
    wire [2:0] ram_rmode_b1;
    wire [2:0] ram_wmode_b1;
    wire [2:0] ram_rmode_a2;
    wire [2:0] ram_wmode_a2;
    wire [2:0] ram_rmode_b2;
    wire [2:0] ram_wmode_b2;
    wire ram_ren_a1;
    wire ram_ren_b1;
    wire ram_ren_a2;
    wire ram_ren_b2;
    wire ram_wen_a1;
    wire ram_wen_b1;
    wire ram_wen_a2;
    wire ram_wen_b2;
    wire ren_o;
    wire [11:0] ff_raddr;
    wire [11:0] ff_waddr;
    reg [35:0] fifo_rdata;
    wire [1:0] fifo_rmode;
    wire [1:0] fifo_wmode;
    wire [1:0] bwl;
    wire [17:0] pl_dout0;
    wire [17:0] pl_dout1;
    wire sclk_a1;
    wire sclk_b1;
    wire sclk_a2;
    wire sclk_b2;
    wire sreset;
    wire flush1;
    wire flush2;
    reg RESET_n_i;
    
   //Avinash - Delay for initial global reset 
    initial begin
      RESET_n_i = 1'b0;
     #1   //laddr_a1 & laddr_b1 registers are taking that much delay then get reset
      RESET_n_i = 1'b1;
    end

    
    localparam MODE_36 = 3'b110;
    assign sreset = RESET_n_i;
    assign flush1 = ~FLUSH1;
    assign flush2 = ~FLUSH2;
    assign ram_fmode1 = FMODE1_i & SPLIT_i;
    assign ram_fmode2 = FMODE2_i & SPLIT_i;
    assign smux_clk_a1 = CLK_A1;
    assign smux_clk_b1 = (FMODE1_i ? (SYNC_FIFO1_i ? CLK_A1 : CLK_B1) : CLK_B1);
    assign smux_clk_a2 = (SPLIT_i ? CLK_A2 : CLK_A1);
    assign smux_clk_b2 = (SPLIT_i ? (FMODE2_i ? (SYNC_FIFO2_i ? CLK_A2 : CLK_B2) : CLK_B2) : (FMODE1_i ? (SYNC_FIFO1_i ? CLK_A1 : CLK_B1) : CLK_B1));
    assign sclk_a1 = smux_clk_a1;
    assign sclk_a2 = smux_clk_a2;
    assign sclk_b1 = smux_clk_b1;
    assign sclk_b2 = smux_clk_b2;
    assign ram_ren_a1 = (SPLIT_i ? REN_A1 : (FMODE1_i ? 0 : (RMODE_A1_i == MODE_36 ? REN_A1 : REN_A1 & ~ADDR_A1[4]) ));
    assign ram_ren_a2 = (SPLIT_i ? REN_A2 : (FMODE1_i ? 0 : (RMODE_A1_i == MODE_36 ? REN_A1 : REN_A1 & ADDR_A1[4]) ));
    assign ram_ren_b1 = (SPLIT_i ? REN_B1 : (FMODE1_i ? ren_o : REN_B1));
    assign ram_ren_b2 = (SPLIT_i ? REN_B2 : (FMODE1_i ? ren_o : REN_B1));
   
    //assign ram_wen_a1 = (SPLIT_i ? WEN_A1 : (FMODE1_i ? ~FULL3 & WEN_A1 : (WMODE_A1_i == MODE_36 ? WEN_A1 : WEN_A1 & ~ADDR_A1[4])));
    assign ram_wen_a1 = (SPLIT_i ? WEN_A1 : (FMODE1_i ? WEN_A1 : (WMODE_A1_i == MODE_36 ? WEN_A1 : WEN_A1 & ~ADDR_A1[4])));
    assign ram_wen_a2 = (SPLIT_i ? WEN_A2 : (FMODE1_i ? ~FULL3 & WEN_A1 : (WMODE_A1_i == MODE_36 ? WEN_A1 : WEN_A1 & ADDR_A1[4])));
    assign ram_wen_b1 = (SPLIT_i ? WEN_B1 : (WMODE_B1_i == MODE_36 ? WEN_B1 : WEN_B1 & ~ADDR_B1[4]));
    assign ram_wen_b2 = (SPLIT_i ? WEN_B2 : (WMODE_B1_i == MODE_36 ? WEN_B1 : WEN_B1 & ADDR_B1[4]));
    assign ram_addr_a1 = (SPLIT_i ? ADDR_A1[13:0] : (FMODE1_i ? {ff_waddr[11:2], ff_waddr[0], 3'b000} : {ADDR_A1[14:5], ADDR_A1[3:0]}));
    assign ram_addr_b1 = (SPLIT_i ? ADDR_B1[13:0] : (FMODE1_i ? {ff_raddr[11:2], ff_raddr[0], 3'b000} : {ADDR_B1[14:5], ADDR_B1[3:0]}));
    assign ram_addr_a2 = (SPLIT_i ? ADDR_A2[13:0] : (FMODE1_i ? {ff_waddr[11:2], ff_waddr[0], 3'b000} : {ADDR_A1[14:5], ADDR_A1[3:0]}));
    assign ram_addr_b2 = (SPLIT_i ? ADDR_B2[13:0] : (FMODE1_i ? {ff_raddr[11:2], ff_raddr[0], 3'b000} : {ADDR_B1[14:5], ADDR_B1[3:0]}));
    assign bwl = (SPLIT_i ? ADDR_A1[4:3] : (FMODE1_i ? ff_waddr[1:0] : ADDR_A1[4:3]));
    localparam MODE_18 = 3'b010;
    localparam MODE_9 = 3'b100;
    always @(*) begin : WDATA_SEL
        case (SPLIT_i)
            1: begin
                ram_wdata_a1 = WDATA_A1;
                ram_wdata_a2 = WDATA_A2;
                ram_wdata_b1 = WDATA_B1;
                ram_wdata_b2 = WDATA_B2;
                ram_be_a2 = BE_A2;
                ram_be_b2 = BE_B2;
                ram_be_a1 = BE_A1;
                ram_be_b1 = BE_B1;
            end
            0: begin
                case (WMODE_A1_i)
                    MODE_36: begin
                        ram_wdata_a1 = WDATA_A1;
                        ram_wdata_a2 = WDATA_A2;
                        ram_be_a2 = (FMODE1_i ? 2'b11 : BE_A2);
                        ram_be_a1 = (FMODE1_i ? 2'b11 : BE_A1);
                    end
                    MODE_18: begin
                        ram_wdata_a1 = WDATA_A1;
                        ram_wdata_a2 = WDATA_A1;
                        ram_be_a1 = (FMODE1_i ? (ff_waddr[1] ? 2'b00 : 2'b11) : BE_A1);
                        ram_be_a2 = (FMODE1_i ? (ff_waddr[1] ? 2'b11 : 2'b00) : BE_A1);
                    end
                    MODE_9: begin
                        ram_wdata_a1[7:0] = WDATA_A1[7:0];
                        ram_wdata_a1[16] = WDATA_A1[16];
                        ram_wdata_a1[15:8] = WDATA_A1[7:0];
                        ram_wdata_a1[17] = WDATA_A1[16];
                        ram_wdata_a2[7:0] = WDATA_A1[7:0];
                        ram_wdata_a2[16] = WDATA_A1[16];
                        ram_wdata_a2[15:8] = WDATA_A1[7:0];
                        ram_wdata_a2[17] = WDATA_A1[16];
                        case (bwl)
                            0: {ram_be_a2, ram_be_a1} = 4'b0001;
                            1: {ram_be_a2, ram_be_a1} = 4'b0010;
                            2: {ram_be_a2, ram_be_a1} = 4'b0100;
                            3: {ram_be_a2, ram_be_a1} = 4'b1000;
                        endcase
                    end
                    default: begin
                        ram_wdata_a1 = WDATA_A1;
                        ram_wdata_a2 = WDATA_A1;
                        ram_be_a2 = (FMODE1_i ? 2'b11 : BE_A1);
                        ram_be_a1 = (FMODE1_i ? 2'b11 : BE_A1);
                    end
                endcase
                case (WMODE_B1_i)
                    MODE_36: begin
                        ram_wdata_b1 = (FMODE1_i ? 18'b000000000000000000 : WDATA_B1);
                        ram_wdata_b2 = (FMODE1_i ? 18'b000000000000000000 : WDATA_B2);
                        ram_be_b2 = BE_B2;
                        ram_be_b1 = BE_B1;
                    end
                    MODE_18: begin
                        ram_wdata_b1 = (FMODE1_i ? 18'b000000000000000000 : WDATA_B1);
                        ram_wdata_b2 = (FMODE1_i ? 18'b000000000000000000 : WDATA_B1);
                        ram_be_b1 = BE_B1;
                        ram_be_b2 = BE_B1;
                    end
                    MODE_9: begin
                        ram_wdata_b1[7:0] = WDATA_B1[7:0];
                        ram_wdata_b1[16] = WDATA_B1[16];
                        ram_wdata_b1[15:8] = WDATA_B1[7:0];
                        ram_wdata_b1[17] = WDATA_B1[16];
                        ram_wdata_b2[7:0] = WDATA_B1[7:0];
                        ram_wdata_b2[16] = WDATA_B1[16];
                        ram_wdata_b2[15:8] = WDATA_B1[7:0];
                        ram_wdata_b2[17] = WDATA_B1[16];
                        case (ADDR_B1[4:3])
                            0: {ram_be_b2, ram_be_b1} = 4'b0001;
                            1: {ram_be_b2, ram_be_b1} = 4'b0010;
                            2: {ram_be_b2, ram_be_b1} = 4'b0100;
                            3: {ram_be_b2, ram_be_b1} = 4'b1000;
                        endcase
                    end
                    default: begin
                        ram_wdata_b1 = (FMODE1_i ? 18'b000000000000000000 : WDATA_B1);
                        ram_wdata_b2 = (FMODE1_i ? 18'b000000000000000000 : WDATA_B1);
                        ram_be_b2 = BE_B1;
                        ram_be_b1 = BE_B1;
                    end
                endcase
            end
        endcase
    end
    assign ram_rmode_a1 = (SPLIT_i ? (RMODE_A1_i == MODE_36 ? MODE_18 : RMODE_A1_i) : (RMODE_A1_i == MODE_36 ? MODE_18 : RMODE_A1_i));
    assign ram_rmode_a2 = (SPLIT_i ? (RMODE_A2_i == MODE_36 ? MODE_18 : RMODE_A2_i) : (RMODE_A1_i == MODE_36 ? MODE_18 : RMODE_A1_i));
    assign ram_wmode_a1 = (SPLIT_i ? (WMODE_A1_i == MODE_36 ? MODE_18 : WMODE_A1_i) : (WMODE_A1_i == MODE_36 ? MODE_18 : (FMODE1_i ? MODE_18 : WMODE_A1_i)));
    assign ram_wmode_a2 = (SPLIT_i ? (WMODE_A2_i == MODE_36 ? MODE_18 : WMODE_A2_i) : (WMODE_A1_i == MODE_36 ? MODE_18 : (FMODE1_i ? MODE_18 : WMODE_A1_i)));
    assign ram_rmode_b1 = (SPLIT_i ? (RMODE_B1_i == MODE_36 ? MODE_18 : RMODE_B1_i) : (RMODE_B1_i == MODE_36 ? MODE_18 : (FMODE1_i ? MODE_18 : RMODE_B1_i)));
    assign ram_rmode_b2 = (SPLIT_i ? (RMODE_B2_i == MODE_36 ? MODE_18 : RMODE_B2_i) : (RMODE_B1_i == MODE_36 ? MODE_18 : (FMODE1_i ? MODE_18 : RMODE_B1_i)));
    assign ram_wmode_b1 = (SPLIT_i ? (WMODE_B1_i == MODE_36 ? MODE_18 : WMODE_B1_i) : (WMODE_B1_i == MODE_36 ? MODE_18 : WMODE_B1_i));
    assign ram_wmode_b2 = (SPLIT_i ? (WMODE_B2_i == MODE_36 ? MODE_18 : WMODE_B2_i) : (WMODE_B1_i == MODE_36 ? MODE_18 : WMODE_B1_i));
    always @(*) begin : FIFO_READ_SEL
        case (RMODE_B1_i)
            MODE_36: fifo_rdata = {ram_rdata_b2[17:16], ram_rdata_b1[17:16], ram_rdata_b2[15:0], ram_rdata_b1[15:0]};
            MODE_18: fifo_rdata = (ff_raddr[1] ? {18'b000000000000000000, ram_rdata_b2} : {18'b000000000000000000, ram_rdata_b1});
            MODE_9:
                case (ff_raddr[1:0])
                    0: fifo_rdata = {19'b0000000000000000000, ram_rdata_b1[16], 8'b00000000, ram_rdata_b1[7:0]};
                    1: fifo_rdata = {19'b0000000000000000000, ram_rdata_b1[17], 8'b00000000, ram_rdata_b1[15:8]};
                    2: fifo_rdata = {19'b0000000000000000000, ram_rdata_b2[16], 8'b00000000, ram_rdata_b2[7:0]};
                    3: fifo_rdata = {19'b0000000000000000000, ram_rdata_b2[17], 8'b00000000, ram_rdata_b2[15:8]};
                endcase
            default: fifo_rdata = {ram_rdata_b2, ram_rdata_b1};
        endcase
    end
    localparam MODE_1 = 3'b101;
    localparam MODE_2 = 3'b011;
    localparam MODE_4 = 3'b001;
    always @(*) begin : RDATA_SEL
        case (SPLIT_i)
            1: begin
                RDATA_A1 = (FMODE1_i ? {10'b0000000000, EMPTY1, EPO1, EWM1, UNDERRUN1, FULL1, FMO1, FWM1, OVERRUN1} : ram_rdata_a1);
                RDATA_B1 = ram_rdata_b1;
                RDATA_A2 = (FMODE2_i ? {10'b0000000000, EMPTY2, EPO2, EWM2, UNDERRUN2, FULL2, FMO2, FWM2, OVERRUN2} : ram_rdata_a2);
                RDATA_B2 = ram_rdata_b2;
            end
            0: begin
                if (FMODE1_i) begin
                    RDATA_A1 = {10'b0000000000, EMPTY3, EPO3, EWM3, UNDERRUN3, FULL3, FMO3, FWM3, OVERRUN3};
                    RDATA_A2 = 18'b000000000000000000;
                end
                else
                    case (RMODE_A1_i)
                        MODE_36: begin
                            RDATA_A1 = {ram_rdata_a1[17:0]};
                            RDATA_A2 = {ram_rdata_a2[17:0]};
                        end
                        MODE_18: begin
                            RDATA_A1 = (laddr_a1[4] ? ram_rdata_a2 : ram_rdata_a1);
                            RDATA_A2 = 18'b000000000000000000;
                        end
                        MODE_9: begin
                            RDATA_A1 = (laddr_a1[4] ? {{2 {ram_rdata_a2[16]}}, {2 {ram_rdata_a2[7:0]}}} : {{2 {ram_rdata_a1[16]}}, {2 {ram_rdata_a1[7:0]}}});
                            RDATA_A2 = 18'b000000000000000000;
                        end
                        MODE_4: begin
                            RDATA_A2 = 18'b000000000000000000;
                            RDATA_A1[17:4] = 14'b00000000000000;
                            RDATA_A1[3:0] = (laddr_a1[4] ? ram_rdata_a2[3:0] : ram_rdata_a1[3:0]);
                        end
                        MODE_2: begin
                            RDATA_A2 = 18'b000000000000000000;
                            RDATA_A1[17:2] = 16'b0000000000000000;
                            RDATA_A1[1:0] = (laddr_a1[4] ? ram_rdata_a2[1:0] : ram_rdata_a1[1:0]);
                        end
                        MODE_1: begin
                            RDATA_A2 = 18'b000000000000000000;
                            RDATA_A1[17:1] = 17'b00000000000000000;
                            RDATA_A1[0] = (laddr_a1[4] ? ram_rdata_a2[0] : ram_rdata_a1[0]);
                        end
                        default: begin
                            RDATA_A1 = {ram_rdata_a2[1:0], ram_rdata_a1[15:0]};
                            RDATA_A2 = {ram_rdata_a2[17:16], ram_rdata_a1[17:16], ram_rdata_a2[15:2]};
                        end
                    endcase
                case (RMODE_B1_i)
                    MODE_36: begin
                        RDATA_B1 = {ram_rdata_b1};
                        RDATA_B2 = {ram_rdata_b2};
                    end
                    MODE_18: begin
                        RDATA_B1 = (FMODE1_i ? fifo_rdata[17:0] : (laddr_b1[4] ? ram_rdata_b2 : ram_rdata_b1));
                        RDATA_B2 = 18'b000000000000000000;
                    end
                    MODE_9: begin
                        RDATA_B1 = (FMODE1_i ? {fifo_rdata[17:0]} : (laddr_b1[4] ? {1'b0, ram_rdata_b2[16], 8'b00000000, ram_rdata_b2[7:0]} : {1'b0, ram_rdata_b1[16], 8'b00000000, ram_rdata_b1[7:0]}));
                        RDATA_B2 = 18'b000000000000000000;
                    end
                    MODE_4: begin
                        RDATA_B2 = 18'b000000000000000000;
                        RDATA_B1[17:4] = 14'b00000000000000;
                        RDATA_B1[3:0] = (laddr_b1[4] ? ram_rdata_b2[3:0] : ram_rdata_b1[3:0]);
                    end
                    MODE_2: begin
                        RDATA_B2 = 18'b000000000000000000;
                        RDATA_B1[17:2] = 16'b0000000000000000;
                        RDATA_B1[1:0] = (laddr_b1[4] ? ram_rdata_b2[1:0] : ram_rdata_b1[1:0]);
                    end
                    MODE_1: begin
                        RDATA_B2 = 18'b000000000000000000;
                        RDATA_B1[17:1] = 17'b00000000000000000;
                        RDATA_B1[0] = (laddr_b1[4] ? ram_rdata_b2[0] : ram_rdata_b1[0]);
                    end
                    default: begin
                        RDATA_B1 = ram_rdata_b1;
                        RDATA_B2 = ram_rdata_b2;
                    end
                endcase
            end
        endcase
    end
    always @(posedge sclk_a1 or negedge sreset)
        if (sreset == 0)
            laddr_a1 <= 1'sb0;
        else
            laddr_a1 <= REN_A1?ADDR_A1:laddr_a1;
    always @(posedge sclk_b1 or negedge sreset)
        if (sreset == 0)
            laddr_b1 <= 1'sb0;
        else
            laddr_b1 <= REN_B1?ADDR_B1:laddr_b1;
    assign fifo_wmode = ((WMODE_A1_i == MODE_36) ? 2'b00 : ((WMODE_A1_i == MODE_18) ? 2'b01 : ((WMODE_A1_i == MODE_9) ? 2'b10 : 2'b00)));
    assign fifo_rmode = ((RMODE_B1_i == MODE_36) ? 2'b00 : ((RMODE_B1_i == MODE_18) ? 2'b01 : ((RMODE_B1_i == MODE_9) ? 2'b10 : 2'b00)));
    fifo_ctl #(
        .ADDR_WIDTH(12),
        .FIFO_WIDTH(3'd4),
        .DEPTH(7)
    ) fifo36_ctl(
        .rclk(sclk_b1),
        .rst_R_n(flush1),
        .wclk(sclk_a1),
        .rst_W_n(flush1),
        .ren(REN_B1),
        .wen(ram_wen_a1),
        .sync(SYNC_FIFO1_i),
        .rmode(fifo_rmode),
        .wmode(fifo_wmode),
        .ren_o(ren_o),
        .fflags({FULL3, FMO3, FWM3, OVERRUN3, EMPTY3, EPO3, EWM3, UNDERRUN3}),
        .raddr(ff_raddr),
        .waddr(ff_waddr),
        .upaf(UPAF1_i),
        .upae(UPAE1_i)
    );
    TDP18K_FIFO #(
        .UPAF_i(UPAF1_i[0:10]),
        .UPAE_i(UPAE1_i[0:10]),
        .SYNC_FIFO_i(SYNC_FIFO1_i),
        .POWERDN_i(POWERDN1_i),
        .SLEEP_i(SLEEP1_i),
        .PROTECT_i(PROTECT1_i),
        .INIT_t_i(INIT_i[0*18432+:18432])
    )u1(
        .RMODE_A_i(ram_rmode_a1),
        .RMODE_B_i(ram_rmode_b1),
        .WMODE_A_i(ram_wmode_a1),
        .WMODE_B_i(ram_wmode_b1),
        .WEN_A_i(ram_wen_a1),
        .WEN_B_i(ram_wen_b1),
        .REN_A_i(ram_ren_a1),
        .REN_B_i(ram_ren_b1),
        .CLK_A_i(sclk_a1),
        .CLK_B_i(sclk_b1),
        .BE_A_i(ram_be_a1),
        .BE_B_i(ram_be_b1),
        .ADDR_A_i(ram_addr_a1),
        .ADDR_B_i(ram_addr_b1),
        .WDATA_A_i(ram_wdata_a1),
        .WDATA_B_i(ram_wdata_b1),
        .RDATA_A_o(ram_rdata_a1),
        .RDATA_B_o(ram_rdata_b1),
        .EMPTY_o(EMPTY1),
        .EPO_o(EPO1),
        .EWM_o(EWM1),
        .UNDERRUN_o(UNDERRUN1),
        .FULL_o(FULL1),
        .FMO_o(FMO1),
        .FWM_o(FWM1),
        .OVERRUN_o(OVERRUN1),
        .FLUSH_ni(flush1),
        .FMODE_i(ram_fmode1)
    );
    TDP18K_FIFO #(
        .UPAF_i(UPAF2_i),
        .UPAE_i(UPAE2_i),
        .SYNC_FIFO_i(SYNC_FIFO2_i),
        .POWERDN_i(POWERDN2_i),
        .SLEEP_i(SLEEP2_i),
        .PROTECT_i(PROTECT2_i),
        .INIT_t_i(INIT_i[1*18432+:18432])
    )u2(
        .RMODE_A_i(ram_rmode_a2),
        .RMODE_B_i(ram_rmode_b2),
        .WMODE_A_i(ram_wmode_a2),
        .WMODE_B_i(ram_wmode_b2),
        .WEN_A_i(ram_wen_a2),
        .WEN_B_i(ram_wen_b2),
        .REN_A_i(ram_ren_a2),
        .REN_B_i(ram_ren_b2),
        .CLK_A_i(sclk_a2),
        .CLK_B_i(sclk_b2),
        .BE_A_i(ram_be_a2),
        .BE_B_i(ram_be_b2),
        .ADDR_A_i(ram_addr_a2),
        .ADDR_B_i(ram_addr_b2),
        .WDATA_A_i(ram_wdata_a2),
        .WDATA_B_i(ram_wdata_b2),
        .RDATA_A_o(ram_rdata_a2),
        .RDATA_B_o(ram_rdata_b2),
        .EMPTY_o(EMPTY2),
        .EPO_o(EPO2),
        .EWM_o(EWM2),
        .UNDERRUN_o(UNDERRUN2),
        .FULL_o(FULL2),
        .FMO_o(FMO2),
        .FWM_o(FWM2),
        .OVERRUN_o(OVERRUN2),
        .FLUSH_ni(flush2),
        .FMODE_i(ram_fmode2)
    );
endmodule
module BRAM2x18_TDP (A1ADDR, A1DATA, A1EN, B1ADDR, B1DATA, B1EN, B1BE, C1ADDR, C1DATA, C1EN, CLK1, CLK2, CLK3, CLK4, D1ADDR, D1DATA, D1EN, D1BE, E1ADDR, E1DATA, E1EN, F1ADDR, F1DATA, F1EN, F1BE, G1ADDR, G1DATA, G1EN, H1ADDR, H1DATA, H1EN, H1BE);
    parameter CFG_ABITS = 11;
    parameter CFG_DBITS = 18;
    parameter CFG_ENABLE_B = 2;
    parameter CFG_ENABLE_D = 2;
    parameter CFG_ENABLE_F = 2;
    parameter CFG_ENABLE_H = 2;

    parameter CLKPOL2 = 1;
    parameter CLKPOL3 = 1;
    parameter [18431:0] INIT0 = 18432'bx;
    parameter [18431:0] INIT1 = 18432'bx;

    localparam MODE_36 = 3'b110;    // 36 or 32-bit
    localparam MODE_18 = 3'b010;    // 18 or 16-bit
    localparam MODE_9  = 3'b100;    // 9 or 8-bit
    localparam MODE_4  = 3'b001;    // 4-bit
    localparam MODE_2  = 3'b011;    // 32-bit
    localparam MODE_1  = 3'b101;    // 32-bit

    input CLK1;
    input CLK2;
    input CLK3;
    input CLK4;

    input [CFG_ABITS-1:0] A1ADDR;
    output [CFG_DBITS-1:0] A1DATA;
    input A1EN;

    input [CFG_ABITS-1:0] B1ADDR;
    input [CFG_DBITS-1:0] B1DATA;
    input B1EN;
    input [CFG_ENABLE_B-1:0] B1BE;

    input [CFG_ABITS-1:0] C1ADDR;
    output [CFG_DBITS-1:0] C1DATA;
    input C1EN;

    input [CFG_ABITS-1:0] D1ADDR;
    input [CFG_DBITS-1:0] D1DATA;
    input D1EN;
    input [CFG_ENABLE_D-1:0] D1BE;

    input [CFG_ABITS-1:0] E1ADDR;
    output [CFG_DBITS-1:0] E1DATA;
    input E1EN;

    input [CFG_ABITS-1:0] F1ADDR;
    input [CFG_DBITS-1:0] F1DATA;
    input F1EN;
    input [CFG_ENABLE_F-1:0] F1BE;

    input [CFG_ABITS-1:0] G1ADDR;
    output [CFG_DBITS-1:0] G1DATA;
    input G1EN;

    input [CFG_ABITS-1:0] H1ADDR;
    input [CFG_DBITS-1:0] H1DATA;
    input H1EN;
    input [CFG_ENABLE_H-1:0] H1BE;

    wire FLUSH1;
    wire FLUSH2;
    wire SPLIT;

    wire [13:CFG_ABITS] A1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] B1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] C1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] D1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] E1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] F1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] G1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] H1ADDR_CMPL = {14-CFG_ABITS{1'b0}};

    wire [13:0] A1ADDR_TOTAL = {A1ADDR_CMPL, A1ADDR};
    wire [13:0] B1ADDR_TOTAL = {B1ADDR_CMPL, B1ADDR};
    wire [13:0] C1ADDR_TOTAL = {C1ADDR_CMPL, C1ADDR};
    wire [13:0] D1ADDR_TOTAL = {D1ADDR_CMPL, D1ADDR};
    wire [13:0] E1ADDR_TOTAL = {E1ADDR_CMPL, E1ADDR};
    wire [13:0] F1ADDR_TOTAL = {F1ADDR_CMPL, F1ADDR};
    wire [13:0] G1ADDR_TOTAL = {G1ADDR_CMPL, G1ADDR};
    wire [13:0] H1ADDR_TOTAL = {H1ADDR_CMPL, H1ADDR};

    wire [17:CFG_DBITS] A1_RDATA_CMPL;
    wire [17:CFG_DBITS] C1_RDATA_CMPL;
    wire [17:CFG_DBITS] E1_RDATA_CMPL;
    wire [17:CFG_DBITS] G1_RDATA_CMPL;

    wire [17:CFG_DBITS] B1_WDATA_CMPL;
    wire [17:CFG_DBITS] D1_WDATA_CMPL;
    wire [17:CFG_DBITS] F1_WDATA_CMPL;
    wire [17:CFG_DBITS] H1_WDATA_CMPL;

    wire [13:0] PORT_A1_ADDR;
    wire [13:0] PORT_A2_ADDR;
    wire [13:0] PORT_B1_ADDR;
    wire [13:0] PORT_B2_ADDR;

    assign FLUSH1 = 1'b0;
    assign FLUSH2 = 1'b0;

    wire [17:0] PORT_A1_RDATA = {A1_RDATA_CMPL, A1DATA};
    wire [17:0] PORT_B1_RDATA = {C1_RDATA_CMPL, C1DATA};
    wire [17:0] PORT_A2_RDATA = {E1_RDATA_CMPL, E1DATA};
    wire [17:0] PORT_B2_RDATA = {G1_RDATA_CMPL, G1DATA};

    wire [17:0] PORT_A1_WDATA = {B1_WDATA_CMPL, B1DATA};
    wire [17:0] PORT_B1_WDATA = {D1_WDATA_CMPL, D1DATA};
    wire [17:0] PORT_A2_WDATA = {F1_WDATA_CMPL, F1DATA};
    wire [17:0] PORT_B2_WDATA = {H1_WDATA_CMPL, H1DATA};

    wire PORT_A1_CLK = CLK1;
    wire PORT_A2_CLK = CLK3;
    wire PORT_B1_CLK = CLK2;
    wire PORT_B2_CLK = CLK4;

    wire PORT_A1_REN = A1EN;
    wire PORT_A1_WEN = B1EN;
    wire [CFG_ENABLE_B-1:0] PORT_A1_BE = B1BE;

    wire PORT_A2_REN = E1EN;
    wire PORT_A2_WEN = F1EN;
    wire [CFG_ENABLE_F-1:0] PORT_A2_BE = F1BE;

    wire PORT_B1_REN = C1EN;
    wire PORT_B1_WEN = D1EN;
    wire [CFG_ENABLE_D-1:0] PORT_B1_BE = D1BE;

    wire PORT_B2_REN = G1EN;
    wire PORT_B2_WEN = H1EN;
    wire [CFG_ENABLE_H-1:0] PORT_B2_BE = H1BE;

    case (CFG_DBITS)
        1: begin
            assign PORT_A1_ADDR = A1EN ? A1ADDR_TOTAL : (B1EN ? B1ADDR_TOTAL : 14'd0);
            assign PORT_B1_ADDR = C1EN ? C1ADDR_TOTAL : (D1EN ? D1ADDR_TOTAL : 14'd0);
            assign PORT_A2_ADDR = E1EN ? E1ADDR_TOTAL : (F1EN ? F1ADDR_TOTAL : 14'd0);
            assign PORT_B2_ADDR = G1EN ? G1ADDR_TOTAL : (H1EN ? H1ADDR_TOTAL : 14'd0);

            RS_TDP36K #(
                .MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_1, MODE_1, MODE_1, MODE_1, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_1, MODE_1, MODE_1, MODE_1, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),
        
                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),
        
                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),
        
                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        2: begin
            assign PORT_A1_ADDR = A1EN ? (A1ADDR_TOTAL << 1) : (B1EN ? (B1ADDR_TOTAL << 1) : 14'd0);
            assign PORT_B1_ADDR = C1EN ? (C1ADDR_TOTAL << 1) : (D1EN ? (D1ADDR_TOTAL << 1) : 14'd0);
            assign PORT_A2_ADDR = E1EN ? (E1ADDR_TOTAL << 1) : (F1EN ? (F1ADDR_TOTAL << 1) : 14'd0);
            assign PORT_B2_ADDR = G1EN ? (G1ADDR_TOTAL << 1) : (H1EN ? (H1ADDR_TOTAL << 1) : 14'd0);
            RS_TDP36K #(
                .MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_2, MODE_2, MODE_2, MODE_2, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_2, MODE_2, MODE_2, MODE_2, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),
        
                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),
        
                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),
        
                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        4: begin
            assign PORT_A1_ADDR = A1EN ? (A1ADDR_TOTAL << 2) : (B1EN ? (B1ADDR_TOTAL << 2) : 14'd0);
            assign PORT_B1_ADDR = C1EN ? (C1ADDR_TOTAL << 2) : (D1EN ? (D1ADDR_TOTAL << 2) : 14'd0);
            assign PORT_A2_ADDR = E1EN ? (E1ADDR_TOTAL << 2) : (F1EN ? (F1ADDR_TOTAL << 2) : 14'd0);
            assign PORT_B2_ADDR = G1EN ? (G1ADDR_TOTAL << 2) : (H1EN ? (H1ADDR_TOTAL << 2) : 14'd0);
            RS_TDP36K #(
                .MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_4, MODE_4, MODE_4, MODE_4, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_4, MODE_4, MODE_4, MODE_4, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),
        
                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),
        
                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),
        
                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        8, 9: begin
            assign PORT_A1_ADDR = A1EN ? (A1ADDR_TOTAL << 3) : (B1EN ? (B1ADDR_TOTAL << 3) : 14'd0);
            assign PORT_B1_ADDR = C1EN ? (C1ADDR_TOTAL << 3) : (D1EN ? (D1ADDR_TOTAL << 3) : 14'd0);
            assign PORT_A2_ADDR = E1EN ? (E1ADDR_TOTAL << 3) : (F1EN ? (F1ADDR_TOTAL << 3) : 14'd0);
            assign PORT_B2_ADDR = G1EN ? (G1ADDR_TOTAL << 3) : (H1EN ? (H1ADDR_TOTAL << 3) : 14'd0);
            RS_TDP36K #(
                .MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_9, MODE_9, MODE_9, MODE_9, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_9, MODE_9, MODE_9, MODE_9, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),
        
                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),
        
                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),
        
                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        16, 18: begin
            assign PORT_A1_ADDR = A1EN ? (A1ADDR_TOTAL << 4) : (B1EN ? (B1ADDR_TOTAL << 4) : 14'd0);
            assign PORT_B1_ADDR = C1EN ? (C1ADDR_TOTAL << 4) : (D1EN ? (D1ADDR_TOTAL << 4) : 14'd0);
            assign PORT_A2_ADDR = E1EN ? (E1ADDR_TOTAL << 4) : (F1EN ? (F1ADDR_TOTAL << 4) : 14'd0);
            assign PORT_B2_ADDR = G1EN ? (G1ADDR_TOTAL << 4) : (H1EN ? (H1ADDR_TOTAL << 4) : 14'd0);
            RS_TDP36K #(
                .MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_18, MODE_18, MODE_18, MODE_18, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_18, MODE_18, MODE_18, MODE_18, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),
        
                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),
        
                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),
        
                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        default: begin
            assign PORT_A1_ADDR = A1EN ? A1ADDR_TOTAL : (B1EN ? B1ADDR_TOTAL : 14'd0);
            assign PORT_B1_ADDR = C1EN ? C1ADDR_TOTAL : (D1EN ? D1ADDR_TOTAL : 14'd0);
            assign PORT_A2_ADDR = E1EN ? E1ADDR_TOTAL : (F1EN ? F1ADDR_TOTAL : 14'd0);
            assign PORT_B2_ADDR = G1EN ? G1ADDR_TOTAL : (H1EN ? H1ADDR_TOTAL : 14'd0);
            RS_TDP36K #(
                .MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_36, MODE_36, MODE_36, MODE_36, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_36, MODE_36, MODE_36, MODE_36, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),
        
                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),
        
                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),
        
                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end
    endcase
endmodule

module BRAM2x18_SDP (A1ADDR, A1DATA, A1EN, B1ADDR, B1DATA, B1EN, B1BE, C1ADDR, C1DATA, C1EN, CLK1, CLK2, D1ADDR, D1DATA, D1EN, D1BE);
    parameter CFG_ABITS = 11;
    parameter CFG_DBITS = 18;
    parameter CFG_ENABLE_B = 2;
    parameter CFG_ENABLE_D = 2;

    parameter CLKPOL2 = 1;
    parameter CLKPOL3 = 1;
    parameter [18431:0] INIT0 = 18432'bx;
    parameter [18431:0] INIT1 = 18432'bx;

    localparam MODE_36 = 3'b110;    // 36 or 32-bit
    localparam MODE_18 = 3'b010;    // 18 or 16-bit
    localparam MODE_9  = 3'b100;    // 9 or 8-bit
    localparam MODE_4  = 3'b001;    // 4-bit
    localparam MODE_2  = 3'b011;    // 32-bit
    localparam MODE_1  = 3'b101;    // 32-bit

    input CLK1;
    input CLK2;

    input [CFG_ABITS-1:0] A1ADDR;
    output [CFG_DBITS-1:0] A1DATA;
    input A1EN;

    input [CFG_ABITS-1:0] B1ADDR;
    input [CFG_DBITS-1:0] B1DATA;
    input B1EN;
    input [CFG_ENABLE_B-1:0] B1BE;

    input [CFG_ABITS-1:0] C1ADDR;
    output [CFG_DBITS-1:0] C1DATA;
    input C1EN;

    input [CFG_ABITS-1:0] D1ADDR;
    input [CFG_DBITS-1:0] D1DATA;
    input D1EN;
    input [CFG_ENABLE_D-1:0] D1BE;

    wire FLUSH1;
    wire FLUSH2;

    wire [13:CFG_ABITS] A1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] B1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] C1ADDR_CMPL = {14-CFG_ABITS{1'b0}};
    wire [13:CFG_ABITS] D1ADDR_CMPL = {14-CFG_ABITS{1'b0}};

    wire [13:0] A1ADDR_TOTAL = {A1ADDR_CMPL, A1ADDR};
    wire [13:0] B1ADDR_TOTAL = {B1ADDR_CMPL, B1ADDR};
    wire [13:0] C1ADDR_TOTAL = {C1ADDR_CMPL, C1ADDR};
    wire [13:0] D1ADDR_TOTAL = {D1ADDR_CMPL, D1ADDR};

    wire [17:CFG_DBITS] A1_RDATA_CMPL;
    wire [17:CFG_DBITS] C1_RDATA_CMPL;

    wire [17:CFG_DBITS] B1_WDATA_CMPL;
    wire [17:CFG_DBITS] D1_WDATA_CMPL;

    wire [13:0] PORT_A1_ADDR;
    wire [13:0] PORT_A2_ADDR;
    wire [13:0] PORT_B1_ADDR;
    wire [13:0] PORT_B2_ADDR;

    assign FLUSH1 = 1'b0;
    assign FLUSH2 = 1'b0;

    wire [17:0] PORT_A1_RDATA;
    wire [17:0] PORT_B1_RDATA;
    wire [17:0] PORT_A2_RDATA;
    wire [17:0] PORT_B2_RDATA;

    wire [17:0] PORT_A1_WDATA;
    wire [17:0] PORT_B1_WDATA;
    wire [17:0] PORT_A2_WDATA;
    wire [17:0] PORT_B2_WDATA;

    // Assign read/write data - handle special case for 9bit mode
    // parity bit for 9bit mode is placed in R/W port on bit #16
    case (CFG_DBITS)
        9: begin
            assign A1DATA = {PORT_A1_RDATA[16], PORT_A1_RDATA[7:0]};
            assign C1DATA = {PORT_A2_RDATA[16], PORT_A2_RDATA[7:0]};
            assign PORT_A1_WDATA = {18{1'b0}};
            assign PORT_B1_WDATA = {B1_WDATA_CMPL[17], B1DATA[8], B1_WDATA_CMPL[16:9], B1DATA[7:0]};
            assign PORT_A2_WDATA = {18{1'b0}};
            assign PORT_B2_WDATA = {D1_WDATA_CMPL[17], D1DATA[8], D1_WDATA_CMPL[16:9], D1DATA[7:0]};
        end
        default: begin
            assign A1DATA = PORT_A1_RDATA[CFG_DBITS-1:0];
            assign C1DATA = PORT_A2_RDATA[CFG_DBITS-1:0];
            assign PORT_A1_WDATA = {18{1'b1}};
            assign PORT_B1_WDATA = {B1_WDATA_CMPL, B1DATA};
            assign PORT_A2_WDATA = {18{1'b1}};
            assign PORT_B2_WDATA = {D1_WDATA_CMPL, D1DATA};

        end
    endcase

    wire PORT_A1_CLK = CLK1;
    wire PORT_A2_CLK = CLK2;
    wire PORT_B1_CLK = CLK1;
    wire PORT_B2_CLK = CLK2;

    wire PORT_A1_REN = A1EN;
    wire PORT_A1_WEN = 1'b0;
    wire [CFG_ENABLE_B-1:0] PORT_A1_BE = {PORT_A1_WEN,PORT_A1_WEN};

    wire PORT_A2_REN = C1EN;
    wire PORT_A2_WEN = 1'b0;
    wire [CFG_ENABLE_D-1:0] PORT_A2_BE = {PORT_A2_WEN,PORT_A2_WEN};

    wire PORT_B1_REN = 1'b0;
    wire PORT_B1_WEN = B1EN;
    wire [CFG_ENABLE_B-1:0] PORT_B1_BE = B1BE;

    wire PORT_B2_REN = 1'b0;
    wire PORT_B2_WEN = D1EN;
    wire [CFG_ENABLE_D-1:0] PORT_B2_BE = D1BE;

    case (CFG_DBITS)
        1: begin
            assign PORT_A1_ADDR = A1ADDR_TOTAL;
            assign PORT_B1_ADDR = B1ADDR_TOTAL;
            assign PORT_A2_ADDR = C1ADDR_TOTAL;
            assign PORT_B2_ADDR = D1ADDR_TOTAL;
            RS_TDP36K #(.MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_1, MODE_1, MODE_1, MODE_1, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_1, MODE_1, MODE_1, MODE_1, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),

                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),

                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),

                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),

                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        2: begin
            assign PORT_A1_ADDR = A1ADDR_TOTAL << 1;
            assign PORT_B1_ADDR = B1ADDR_TOTAL << 1;
            assign PORT_A2_ADDR = C1ADDR_TOTAL << 1;
            assign PORT_B2_ADDR = D1ADDR_TOTAL << 1;
            RS_TDP36K #(.MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_2, MODE_2, MODE_2, MODE_2, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_2, MODE_2, MODE_2, MODE_2, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),

                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),

                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),

                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),

                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        4: begin
            assign PORT_A1_ADDR = A1ADDR_TOTAL << 2;
            assign PORT_B1_ADDR = B1ADDR_TOTAL << 2;
            assign PORT_A2_ADDR = C1ADDR_TOTAL << 2;
            assign PORT_B2_ADDR = D1ADDR_TOTAL << 2;
            RS_TDP36K #(.MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_4, MODE_4, MODE_4, MODE_4, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_4, MODE_4, MODE_4, MODE_4, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),

                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),

                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),

                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),

                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        8, 9: begin
            assign PORT_A1_ADDR = A1ADDR_TOTAL << 3;
            assign PORT_B1_ADDR = B1ADDR_TOTAL << 3;
            assign PORT_A2_ADDR = C1ADDR_TOTAL << 3;
            assign PORT_B2_ADDR = D1ADDR_TOTAL << 3;
            RS_TDP36K #(.MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_9, MODE_9, MODE_9, MODE_9, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_9, MODE_9, MODE_9, MODE_9, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),

                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),

                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),

                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),

                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        16, 18: begin
            assign PORT_A1_ADDR = A1ADDR_TOTAL << 4;
            assign PORT_B1_ADDR = B1ADDR_TOTAL << 4;
            assign PORT_A2_ADDR = C1ADDR_TOTAL << 4;
            assign PORT_B2_ADDR = D1ADDR_TOTAL << 4;
            RS_TDP36K #(.MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_18, MODE_18, MODE_18, MODE_18, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_18, MODE_18, MODE_18, MODE_18, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),

                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),

                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),

                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),

                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        default: begin
            assign PORT_A1_ADDR = A1ADDR_TOTAL;
            assign PORT_B1_ADDR = B1ADDR_TOTAL;
            assign PORT_A2_ADDR = D1ADDR_TOTAL;
            assign PORT_B2_ADDR = C1ADDR_TOTAL;
            RS_TDP36K #(.MODE_BITS({ 1'b1,
                11'd10, 11'd10, 4'd0, MODE_36, MODE_36, MODE_36, MODE_36, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_36, MODE_36, MODE_36, MODE_36, 1'd0
                }),
                .INIT_i({INIT0[0*18432+:18432],INIT1[0*18432+:18432]})
            )bram_2x18k(
                .WDATA_A1(PORT_A1_WDATA),
                .RDATA_A1(PORT_A1_RDATA),
                .ADDR_A1(PORT_A1_ADDR),
                .CLK_A1(PORT_A1_CLK),
                .REN_A1(PORT_A1_REN),
                .WEN_A1(PORT_A1_WEN),
                .BE_A1(PORT_A1_BE),

                .WDATA_A2(PORT_A2_WDATA),
                .RDATA_A2(PORT_A2_RDATA),
                .ADDR_A2(PORT_A2_ADDR),
                .CLK_A2(PORT_A2_CLK),
                .REN_A2(PORT_A2_REN),
                .WEN_A2(PORT_A2_WEN),
                .BE_A2(PORT_A2_BE),

                .WDATA_B1(PORT_B1_WDATA),
                .RDATA_B1(PORT_B1_RDATA),
                .ADDR_B1(PORT_B1_ADDR),
                .CLK_B1(PORT_B1_CLK),
                .REN_B1(PORT_B1_REN),
                .WEN_B1(PORT_B1_WEN),
                .BE_B1(PORT_B1_BE),

                .WDATA_B2(PORT_B2_WDATA),
                .RDATA_B2(PORT_B2_RDATA),
                .ADDR_B2(PORT_B2_ADDR),
                .CLK_B2(PORT_B2_CLK),
                .REN_B2(PORT_B2_REN),
                .WEN_B2(PORT_B2_WEN),
                .BE_B2(PORT_B2_BE),

                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end
    endcase

endmodule

module \_$_mem_v2_asymmetric (RD_ADDR, RD_ARST, RD_CLK, RD_DATA, RD_EN, RD_SRST, WR_ADDR, WR_CLK, WR_DATA, WR_EN);
    parameter CFG_ABITS = 10;
    parameter CFG_DBITS = 36;
    parameter CFG_ENABLE_B = 4;

    localparam CLKPOL2 = 1;
    localparam CLKPOL3 = 1;

    parameter READ_ADDR_WIDTH = 11;
    parameter READ_DATA_WIDTH = 16;
    parameter WRITE_ADDR_WIDTH = 10;
    parameter WRITE_DATA_WIDTH = 32;
    parameter ABITS = 0;
    parameter MEMID = 0;
    parameter [36863:0] INIT = 36864'bx;
    parameter OFFSET = 0;
    parameter RD_ARST_VALUE = 0;
    parameter RD_CE_OVER_SRST = 0;
    parameter RD_CLK_ENABLE = 0;
    parameter RD_CLK_POLARITY = 0;
    parameter RD_COLLISION_X_MASK = 0;
    parameter RD_PORTS = 0;
    parameter RD_SRST_VALUE = 0;
    parameter RD_TRANSPARENCY_MASK = 0;
    parameter RD_WIDE_CONTINUATION = 0;
    parameter SIZE = 0;
    parameter WIDTH = 0;
    parameter WR_CLK_ENABLE = 0;
    parameter WR_CLK_POLARITY = 0;
    parameter WR_PORTS = 0;
    parameter WR_PRIORITY_MASK = 0;
    parameter WR_WIDE_CONTINUATION = 0;

    localparam MODE_36  = 3'b111;   // 36 or 32-bit
    localparam MODE_18  = 3'b110;   // 18 or 16-bit
    localparam MODE_9   = 3'b101;   // 9 or 8-bit
    localparam MODE_4   = 3'b100;   // 4-bit
    localparam MODE_2   = 3'b010;   // 32-bit
    localparam MODE_1   = 3'b001;   // 32-bit

    input RD_CLK;
    input WR_CLK;
    input RD_ARST;
    input RD_SRST;

    input [CFG_ABITS-1:0] RD_ADDR;
    output [CFG_DBITS-1:0] RD_DATA;
    input RD_EN;

    input [CFG_ABITS-1:0] WR_ADDR;
    input [CFG_DBITS-1:0] WR_DATA;
    input [CFG_ENABLE_B-1:0] WR_EN;

    wire [14:0] RD_ADDR_15;
    wire [14:0] WR_ADDR_15;

    wire [35:0] DOBDO;

    wire [14:CFG_ABITS] RD_ADDR_CMPL;
    wire [14:CFG_ABITS] WR_ADDR_CMPL;
    wire [35:CFG_DBITS] RD_DATA_CMPL;
    wire [35:CFG_DBITS] WR_DATA_CMPL;

    wire [14:0] RD_ADDR_TOTAL;
    wire [14:0] WR_ADDR_TOTAL;
    wire [35:0] RD_DATA_TOTAL;
    wire [35:0] WR_DATA_TOTAL;

    wire FLUSH1;
    wire FLUSH2;

    assign RD_ADDR_CMPL = {15-CFG_ABITS{1'b0}};
    assign WR_ADDR_CMPL = {15-CFG_ABITS{1'b0}};

    assign RD_ADDR_TOTAL = {RD_ADDR_CMPL, RD_ADDR};
    assign WR_ADDR_TOTAL = {WR_ADDR_CMPL, WR_ADDR};

    assign RD_DATA_TOTAL = {RD_DATA_CMPL, RD_DATA};
    assign WR_DATA_TOTAL = {WR_DATA_CMPL, WR_DATA};

    assign FLUSH1 = 1'b0;
    assign FLUSH2 = 1'b0;

    case (CFG_DBITS)
        1: begin
            assign RD_ADDR_15 = RD_ADDR_TOTAL;
            assign WR_ADDR_15 = WR_ADDR_TOTAL;
            RS_TDP36K #(
                .MODE_BITS({ 1'b0,
                11'd10, 11'd10, 4'd0, MODE_1, MODE_1, MODE_1, MODE_1, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_1, MODE_1, MODE_1, MODE_1, 1'd0
                }),
                .INIT_i(INIT[0*36864+:36864])
            )bram_asymmetric(
              //  .RESET_n(1'b1),
                .WDATA_A1(18'h3FFFF),
                .WDATA_A2(18'h3FFFF),
                .RDATA_A1(RD_DATA_TOTAL[17:0]),
                .RDATA_A2(RD_DATA_TOTAL[35:18]),
                .ADDR_A1(RD_ADDR_15),
                .ADDR_A2(RD_ADDR_15),
                .CLK_A1(RD_CLK),
                .CLK_A2(RD_CLK),
                .REN_A1(RD_EN),
                .REN_A2(RD_EN),
                .WEN_A1(1'b0),
                .WEN_A2(1'b0),
                .BE_A1({RD_EN, RD_EN}),
                .BE_A2({RD_EN, RD_EN}),
        
                .WDATA_B1(WR_DATA[17:0]),
                .WDATA_B2(WR_DATA[35:18]),
                .RDATA_B1(DOBDO[17:0]),
                .RDATA_B2(DOBDO[35:18]),
                .ADDR_B1(WR_ADDR_15),
                .ADDR_B2(WR_ADDR_15),
                .CLK_B1(WR_CLK),
                .CLK_B2(WR_CLK),
                .REN_B1(1'b0),
                .REN_B2(1'b0),
                .WEN_B1(WR_EN[0]),
                .WEN_B2(WR_EN[0]),
                .BE_B1(WR_EN[1:0]),
                .BE_B2(WR_EN[3:2]),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        2: begin
            assign RD_ADDR_15 = RD_ADDR_TOTAL << 1;
            assign WR_ADDR_15 = WR_ADDR_TOTAL << 1;
            RS_TDP36K #(
                .MODE_BITS({ 1'b0,
                11'd10, 11'd10, 4'd0, MODE_2, MODE_2, MODE_2, MODE_2, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_2, MODE_2, MODE_2, MODE_2, 1'd0
                }),
                .INIT_i(INIT[0*36864+:36864])
            )bram_asymmetric(
               // .RESET_n(1'b1),
                .WDATA_A1(18'h3FFFF),
                .WDATA_A2(18'h3FFFF),
                .RDATA_A1(RD_DATA_TOTAL[17:0]),
                .RDATA_A2(RD_DATA_TOTAL[35:18]),
                .ADDR_A1(RD_ADDR_15),
                .ADDR_A2(RD_ADDR_15),
                .CLK_A1(RD_CLK),
                .CLK_A2(RD_CLK),
                .REN_A1(RD_EN),
                .REN_A2(RD_EN),
                .WEN_A1(1'b0),
                .WEN_A2(1'b0),
                .BE_A1({RD_EN, RD_EN}),
                .BE_A2({RD_EN, RD_EN}),
        
                .WDATA_B1(WR_DATA[17:0]),
                .WDATA_B2(WR_DATA[35:18]),
                .RDATA_B1(DOBDO[17:0]),
                .RDATA_B2(DOBDO[35:18]),
                .ADDR_B1(WR_ADDR_15),
                .ADDR_B2(WR_ADDR_15),
                .CLK_B1(WR_CLK),
                .CLK_B2(WR_CLK),
                .REN_B1(1'b0),
                .REN_B2(1'b0),
                .WEN_B1(WR_EN[0]),
                .WEN_B2(WR_EN[0]),
                .BE_B1(WR_EN[1:0]),
                .BE_B2(WR_EN[3:2]),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        4: begin
            assign RD_ADDR_15 = RD_ADDR_TOTAL << 2;
            assign WR_ADDR_15 = WR_ADDR_TOTAL << 2;
            RS_TDP36K #(
                .MODE_BITS({ 1'b0,
                11'd10, 11'd10, 4'd0, MODE_4, MODE_4, MODE_4, MODE_4, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_4, MODE_4, MODE_4, MODE_4, 1'd0
                }),
                .INIT_i(INIT[0*36864+:36864])
            )bram_asymmetric(
               // .RESET_n(1'b1),
                .WDATA_A1(18'h3FFFF),
                .WDATA_A2(18'h3FFFF),
                .RDATA_A1(RD_DATA_TOTAL[17:0]),
                .RDATA_A2(RD_DATA_TOTAL[35:18]),
                .ADDR_A1(RD_ADDR_15),
                .ADDR_A2(RD_ADDR_15),
                .CLK_A1(RD_CLK),
                .CLK_A2(RD_CLK),
                .REN_A1(RD_EN),
                .REN_A2(RD_EN),
                .WEN_A1(1'b0),
                .WEN_A2(1'b0),
                .BE_A1({RD_EN, RD_EN}),
                .BE_A2({RD_EN, RD_EN}),
        
                .WDATA_B1(WR_DATA[17:0]),
                .WDATA_B2(WR_DATA[35:18]),
                .RDATA_B1(DOBDO[17:0]),
                .RDATA_B2(DOBDO[35:18]),
                .ADDR_B1(WR_ADDR_15),
                .ADDR_B2(WR_ADDR_15),
                .CLK_B1(WR_CLK),
                .CLK_B2(WR_CLK),
                .REN_B1(1'b0),
                .REN_B2(1'b0),
                .WEN_B1(WR_EN[0]),
                .WEN_B2(WR_EN[0]),
                .BE_B1(WR_EN[1:0]),
                .BE_B2(WR_EN[3:2]),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end
        8, 9: begin
            assign RD_ADDR_15 = RD_ADDR_TOTAL << 3;
            assign WR_ADDR_15 = WR_ADDR_TOTAL << 3;
            RS_TDP36K #(
                .MODE_BITS({ 1'b0,
                11'd10, 11'd10, 4'd0, MODE_9, MODE_9, MODE_9, MODE_9, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_9, MODE_9, MODE_9, MODE_9, 1'd0
                }),
                .INIT_i(INIT[0*36864+:36864])
            )bram_asymmetric(
               // .RESET_n(1'b1),
                .WDATA_A1(18'h3FFFF),
                .WDATA_A2(18'h3FFFF),
                .RDATA_A1(RD_DATA_TOTAL[17:0]),
                .RDATA_A2(RD_DATA_TOTAL[35:18]),
                .ADDR_A1(RD_ADDR_15),
                .ADDR_A2(RD_ADDR_15),
                .CLK_A1(RD_CLK),
                .CLK_A2(RD_CLK),
                .REN_A1(RD_EN),
                .REN_A2(RD_EN),
                .WEN_A1(1'b0),
                .WEN_A2(1'b0),
                .BE_A1({RD_EN, RD_EN}),
                .BE_A2({RD_EN, RD_EN}),
        
                .WDATA_B1(WR_DATA[17:0]),
                .WDATA_B2(WR_DATA[35:18]),
                .RDATA_B1(DOBDO[17:0]),
                .RDATA_B2(DOBDO[35:18]),
                .ADDR_B1(WR_ADDR_15),
                .ADDR_B2(WR_ADDR_15),
                .CLK_B1(WR_CLK),
                .CLK_B2(WR_CLK),
                .REN_B1(1'b0),
                .REN_B2(1'b0),
                .WEN_B1(WR_EN[0]),
                .WEN_B2(WR_EN[0]),
                .BE_B1(WR_EN[1:0]),
                .BE_B2(WR_EN[3:2]),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end

        16, 18: begin
            assign RD_ADDR_15 = RD_ADDR_TOTAL << 4;
            assign WR_ADDR_15 = WR_ADDR_TOTAL << 4;
            RS_TDP36K #(
                .MODE_BITS({ 1'b0,
                11'd10, 11'd10, 4'd0, MODE_18, MODE_18, MODE_18, MODE_18, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_18, MODE_18, MODE_18, MODE_18, 1'd0
                }),
                .INIT_i(INIT[0*36864+:36864])
            )bram_asymmetric(
               // .RESET_n(1'b1),
                .WDATA_A1(18'h3FFFF),
                .WDATA_A2(18'h3FFFF),
                .RDATA_A1(RD_DATA_TOTAL[17:0]),
                .RDATA_A2(RD_DATA_TOTAL[35:18]),
                .ADDR_A1(RD_ADDR_15),
                .ADDR_A2(RD_ADDR_15),
                .CLK_A1(RD_CLK),
                .CLK_A2(RD_CLK),
                .REN_A1(RD_EN),
                .REN_A2(RD_EN),
                .WEN_A1(1'b0),
                .WEN_A2(1'b0),
                .BE_A1({RD_EN, RD_EN}),
                .BE_A2({RD_EN, RD_EN}),
        
                .WDATA_B1(WR_DATA[17:0]),
                .WDATA_B2(WR_DATA[35:18]),
                .RDATA_B1(DOBDO[17:0]),
                .RDATA_B2(DOBDO[35:18]),
                .ADDR_B1(WR_ADDR_15),
                .ADDR_B2(WR_ADDR_15),
                .CLK_B1(WR_CLK),
                .CLK_B2(WR_CLK),
                .REN_B1(1'b0),
                .REN_B2(1'b0),
                .WEN_B1(WR_EN[0]),
                .WEN_B2(WR_EN[0]),
                .BE_B1(WR_EN[1:0]),
                .BE_B2(WR_EN[3:2]),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end
        32, 36: begin
            assign RD_ADDR_15 = RD_ADDR_TOTAL << 5;
            assign WR_ADDR_15 = WR_ADDR_TOTAL << 5;
            RS_TDP36K #(
                .MODE_BITS({ 1'b0,
                11'd10, 11'd10, 4'd0, MODE_36, MODE_36, MODE_36, MODE_36, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_36, MODE_36, MODE_36, MODE_36, 1'd0
                }),
                .INIT_i(INIT[0*36864+:36864])
            )bram_asymmetric(
               // .RESET_n(1'b1),
                .WDATA_A1(18'h3FFFF),
                .WDATA_A2(18'h3FFFF),
                .RDATA_A1(RD_DATA_TOTAL[17:0]),
                .RDATA_A2(RD_DATA_TOTAL[35:18]),
                .ADDR_A1(RD_ADDR_15),
                .ADDR_A2(RD_ADDR_15),
                .CLK_A1(RD_CLK),
                .CLK_A2(RD_CLK),
                .REN_A1(RD_EN),
                .REN_A2(RD_EN),
                .WEN_A1(1'b0),
                .WEN_A2(1'b0),
                .BE_A1({RD_EN, RD_EN}),
                .BE_A2({RD_EN, RD_EN}),
        
                .WDATA_B1(WR_DATA[17:0]),
                .WDATA_B2(WR_DATA[35:18]),
                .RDATA_B1(DOBDO[17:0]),
                .RDATA_B2(DOBDO[35:18]),
                .ADDR_B1(WR_ADDR_15),
                .ADDR_B2(WR_ADDR_15),
                .CLK_B1(WR_CLK),
                .CLK_B2(WR_CLK),
                .REN_B1(1'b0),
                .REN_B2(1'b0),
                .WEN_B1(WR_EN[0]),
                .WEN_B2(WR_EN[0]),
                .BE_B1(WR_EN[1:0]),
                .BE_B2(WR_EN[3:2]),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end
        default: begin
            assign RD_ADDR_15 = RD_ADDR_TOTAL;
            assign WR_ADDR_15 = WR_ADDR_TOTAL;
            RS_TDP36K #(
                .MODE_BITS({ 1'b0,
                11'd10, 11'd10, 4'd0, MODE_36, MODE_36, MODE_36, MODE_36, 1'd0,
                12'd10, 12'd10, 4'd0, MODE_36, MODE_36, MODE_36, MODE_36, 1'd0
                }),
                .INIT_i(INIT[0*36864+:36864])
            )bram_asymmetric(
               // .RESET_n(1'b1),
                .WDATA_A1(18'h3FFFF),
                .WDATA_A2(18'h3FFFF),
                .RDATA_A1(RD_DATA_TOTAL[17:0]),
                .RDATA_A2(RD_DATA_TOTAL[35:18]),
                .ADDR_A1(RD_ADDR_15),
                .ADDR_A2(RD_ADDR_15),
                .CLK_A1(RD_CLK),
                .CLK_A2(RD_CLK),
                .REN_A1(RD_EN),
                .REN_A2(RD_EN),
                .WEN_A1(1'b0),
                .WEN_A2(1'b0),
                .BE_A1({RD_EN, RD_EN}),
                .BE_A2({RD_EN, RD_EN}),
        
                .WDATA_B1(WR_DATA[17:0]),
                .WDATA_B2(WR_DATA[35:18]),
                .RDATA_B1(DOBDO[17:0]),
                .RDATA_B2(DOBDO[35:18]),
                .ADDR_B1(WR_ADDR_15),
                .ADDR_B2(WR_ADDR_15),
                .CLK_B1(WR_CLK),
                .CLK_B2(WR_CLK),
                .REN_B1(1'b0),
                .REN_B2(1'b0),
                .WEN_B1(WR_EN[0]),
                .WEN_B2(WR_EN[0]),
                .BE_B1(WR_EN[1:0]),
                .BE_B2(WR_EN[3:2]),
        
                .FLUSH1(FLUSH1),
                .FLUSH2(FLUSH2)
            );
        end
    endcase
endmodule