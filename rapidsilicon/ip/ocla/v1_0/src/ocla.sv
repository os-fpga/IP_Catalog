//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
//
//
// Copyright (c) 2022 RapidSilicon
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is furnished
// to do so, subject to the following conditions: The above copyright notice and
// this permission notice shall be included in all copies or substantial portions
// of the Software.
//
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PAR-
// TICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
// OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
// SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//
//////////////////////////////////////////////////////////////////////////////////

/* verilator lint_off DECLFILENAME */
// ---------------------------------------------------------------
// Common
// ---------------------------------------------------------------
// `define NUM_OF_PROBES 32                              // number of probes
// ---------------------------------------------------------------
// OCLA TOP
// ---------------------------------------------------------------


module ocla #(
    parameter IP_TYPE = "OCLA",
    parameter IP_VERSION = 32'h1,
    parameter IP_ID = 32'h3881734,
    parameter NO_OF_PROBES = 1024,
    parameter MEM_DEPTH = 1024,
    parameter AXI_DATA_WIDTH = 32,
    parameter AXI_ADDR_WIDTH = 32,
    parameter INDEX = 1

  ) (
    input   logic sample_clk,
    input   logic rstn,
    input   logic S_AXI_ACLK,
    input   logic S_AXI_ARESETN,

    input   logic [AXI_ADDR_WIDTH-1 : 0] S_AXI_AWADDR,
    input   logic [2 : 0] S_AXI_AWPROT,
    input   logic S_AXI_AWVALID,
    output  logic S_AXI_AWREADY,

    input   logic [AXI_DATA_WIDTH-1 : 0] S_AXI_WDATA,
    input   logic [(AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
    input   logic S_AXI_WVALID,
    output  logic S_AXI_WREADY,

    output  logic [1 : 0] S_AXI_BRESP,
    output  logic S_AXI_BVALID,
    input   logic S_AXI_BREADY,

    input   logic [AXI_ADDR_WIDTH-1 : 0] S_AXI_ARADDR,
    input   logic [2 : 0] S_AXI_ARPROT,
    input   logic S_AXI_ARVALID,
    output  logic S_AXI_ARREADY,

    output  logic [AXI_DATA_WIDTH-1 : 0] S_AXI_RDATA,
    output  logic [1 : 0] S_AXI_RRESP,
    output  logic S_AXI_RVALID,
    input   logic S_AXI_RREADY,
    input   logic [NO_OF_PROBES-1:0] probes,

    input logic   in_cross_trig1,
    input logic   in_cross_trig2,
    input logic   in_cross_trig3,
    input logic   in_cross_trig4,
    output logic  out_cross_trig1,
    output logic  out_cross_trig2,
    output logic  out_cross_trig3,
    output logic  out_cross_trig4,
    output logic [7:0] self_trigger_status,

    input logic [7:0] cross_trigger_status,
    output logic self_start_core,
    input logic cross_start_core
  );



  // ---------------------------------------------------------------
  // Stream Out Buffer
  // ---------------------------------------------------------------

  localparam REM_BITS = NO_OF_PROBES < 32 ? 32 - NO_OF_PROBES : ((NO_OF_PROBES - ($floor(NO_OF_PROBES / 32) * 32))== 0 )? 0 : 32 -  (NO_OF_PROBES - ($floor(NO_OF_PROBES / 32) * 32));
  // in case number of probe is not a multiple of 32
  localparam WORD_CHUNKS = NO_OF_PROBES > 32 ? (NO_OF_PROBES / 32) +((NO_OF_PROBES - $floor(NO_OF_PROBES / 32) * 32 )== 0 ? 0:1):1;
  // number of 32 bit words in which probes can be divided
  //localparam PROBE_BITS = 32 - int'(REM_BITS);
  localparam [31:0] PROBE_BITS = 32 - REM_BITS;
  //localparam WORD_CHUNK_CNTR_WIDTH = WORD_CHUNKS> 1? int'($clog2(WORD_CHUNKS)):1;

  localparam WORD_CHUNK_CNTR_WIDTH = WORD_CHUNKS> 1? ($clog2(WORD_CHUNKS)):1;

  // ---------------------------------------------------------------
  // Dual Synchronizer flop
  // ---------------------------------------------------------------

  localparam REG_WIDTH = 1;                                      // Dual synchronizer width

  // ---------------------------------------------------------------
  // Sampler buffer
  // ---------------------------------------------------------------

  localparam BUFFER_STAGES = 4;                                 // Buffer registers


  // ---------------------------------------------------------------
  // OCLA Memory Controller
  // ---------------------------------------------------------------

  localparam SYNC_STAGES = 2;                                   // synchronizer flops
  localparam COUNTER_WIDHT = $clog2(MEM_DEPTH);             // counter WIDTH

  // ---------------------------------------------------------------
  // OCLA Controller
  // ---------------------------------------------------------------

  localparam MEMORY_DEPTH_HALF = MEM_DEPTH/2;
  localparam SAMPLE_COUNTER_WIDTH = COUNTER_WIDHT;

  // ---------------------------------------------------------------
  // Trigger Control Unit
  // ---------------------------------------------------------------

  localparam TRIGGER_SIGNAL_SELECT_RANGE = NO_OF_PROBES;
  localparam SELECT_MUX_WIDTH = NO_OF_PROBES <= 1 ? 1 : $clog2(TRIGGER_SIGNAL_SELECT_RANGE);  // mux select line WIDTH to select trigger signal


  // ---------------------------------------------------------------

  logic sampling_en;
  logic trigger_event;
  logic data_wen;
  logic wr_full;
  logic [NO_OF_PROBES-1:0] data_accumulate;
  logic [NO_OF_PROBES-1:0] read_accumulated_data;
  logic mem_read;
  logic mem_empty;


  logic [AXI_DATA_WIDTH-1:0] TMTR_OUT;
  logic [AXI_DATA_WIDTH-1:0] OCCR_OUT;
  logic [AXI_DATA_WIDTH-1:0] TBDR_IN;

  logic [AXI_DATA_WIDTH-1:0] TSSR0_OUT;
  logic [AXI_DATA_WIDTH-1:0] TSSR1_OUT;
  logic [AXI_DATA_WIDTH-1:0] TSSR2_OUT;
  logic [AXI_DATA_WIDTH-1:0] TSSR3_OUT;

  logic [AXI_DATA_WIDTH-1:0] TCUR0_OUT;
  logic [AXI_DATA_WIDTH-1:0] TCUR1_OUT;
  logic [AXI_DATA_WIDTH-1:0] TCUR2_OUT;
  logic [AXI_DATA_WIDTH-1:0] TCUR3_OUT;

  logic [AXI_DATA_WIDTH-1:0] TDCR0_OUT;
  logic [AXI_DATA_WIDTH-1:0] TDCR1_OUT;
  logic [AXI_DATA_WIDTH-1:0] TDCR2_OUT;
  logic [AXI_DATA_WIDTH-1:0] TDCR3_OUT;


  logic [AXI_DATA_WIDTH-1:0] MASK0_OUT;
  logic [AXI_DATA_WIDTH-1:0] MASK1_OUT;
  logic [AXI_DATA_WIDTH-1:0] MASK2_OUT;
  logic [AXI_DATA_WIDTH-1:0] MASK3_OUT;



  logic read_trace_mem_en;

  logic mem_empty_sync;
  logic mem_valid_data;
  logic reset_fifo_pntr;
  logic reset_fifo_wr_pntr_sync;
  logic start_process;
  logic TMTR_REG_port_strt_bit_sync;

  logic sampling_done_ff;
  logic done_sampling_ff_sync;
  logic intrn_rst_force;

  assign self_start_core = OCCR_OUT[0];
  // ---------------------------------------------------------------//
  // Synchronizer flop instance for                                 //
  // for sampling done signal from sampling clock domain            //
  // to axi clock domain                                            //
  // ---------------------------------------------------------------//

  ddff_sync #(
              .REG_WIDTH(REG_WIDTH)
            ) data_available_inmem (
              .clk(S_AXI_ACLK),
              .rstn(S_AXI_ARESETN),
              .D(sampling_done_ff),
              .Q(done_sampling_ff_sync)
            );

  // ---------------------------------------------------------------//
  // Sampler buffer module instance                                 //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//

  sampler_buffer #(
                   .PROBE_DATA_WIDTH(NO_OF_PROBES),
                   .BUFFERS(BUFFER_STAGES)
                 ) sampler_buffer_inst (
                   .sample_clk(sample_clk),
                   .rstn(rstn),
                   .probes(probes),
                   .sampling_en(sampling_en),
                   .data_wen(data_wen),
                   .data_accumulate(data_accumulate)
                 );

  // ---------------------------------------------------------------//
  // Synchronizer flop instance for                                 //
  // for memory empty signal from axi clock domain                  //
  // to sampling clock domain                                       //
  // ---------------------------------------------------------------//

  ddff_sync #(
              .REG_WIDTH(REG_WIDTH)
            ) synchronizer_flop (
              .clk(sample_clk),
              .rstn(rstn),
              .D(mem_empty),
              .Q(mem_empty_sync)
            );


  // ---------------------------------------------------------------//
  // Synchronizer flop instance for                                 //
  // for TMTR_REG register data from axi clock domain                   //
  // to sampling clock domain                                       //
  // ---------------------------------------------------------------//

  ddff_sync #(
              .REG_WIDTH(1)
            ) TMTR_REG_bits_sync (
              .clk(sample_clk),
              .rstn(rstn),
              .D(OCCR_OUT[0] | cross_start_core),
              .Q(TMTR_REG_port_strt_bit_sync)
            );

  // ---------------------------------------------------------------//
  // On chip logic analyzer controller's instance                   //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//


  ocla_controller #(
                    .SAMPLE_CNTER_WIDTH(SAMPLE_COUNTER_WIDTH),
                    .MEM_DPTH_HALF(MEMORY_DEPTH_HALF)
                  ) ocla_controller_inst (
                    .sample_clk(sample_clk),
                    .rstn(rstn ),
                    .trigger_event(trigger_event),
                    .trigger_mode(TMTR_OUT[1:0]),
                    .mem_full(wr_full),
                    .start_process(TMTR_REG_port_strt_bit_sync),
                    .fixnosamples_en(TMTR_OUT[4]),
                    //.noofsamples({'b0,TMTR_REG_port[4+:(SAMPLE_COUNTER_WIDTH>10?10:SAMPLE_COUNTER_WIDTH)]}),
                    .noofsamples({1'b0,TMTR_OUT[12+:(SAMPLE_COUNTER_WIDTH>10?10:SAMPLE_COUNTER_WIDTH)]}),
                    .sampling_done_ff(sampling_done_ff),
                    .mem_empty(mem_empty_sync),
                    .sample_again(reset_fifo_wr_pntr_sync),
                    .sampling_en(sampling_en)
                  );

  // ---------------------------------------------------------------//
  // Trigger control unit instance                                  //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//
  logic start_cap;
  assign self_trigger_status = {TCUR3_OUT[1:0],TCUR2_OUT[1:0],TCUR1_OUT[1:0],TCUR0_OUT[1:0]};
  trigger_control_unit #(
                         .NPROBES(NO_OF_PROBES),
                         .SELECT_MUX_WIDTH(SELECT_MUX_WIDTH),
                         .TRIGGER_SIGNAL_SELECT_RANGE(TRIGGER_SIGNAL_SELECT_RANGE)
                       ) trig_control_unit_inst (
                         .sample_clk(sample_clk),
                         .rstn(rstn),
                         .in_signals(probes),
                         //.in_signals(probes),
                         .config_bits({TCUR3_OUT,TCUR2_OUT,TCUR1_OUT,TCUR0_OUT}),
                         .boolean_operator(TMTR_OUT[3:2]),
                         .probe_selector0(TSSR0_OUT),
                         .probe_selector1(TSSR1_OUT),
                         .probe_selector2(TSSR2_OUT),
                         .probe_selector3(TSSR3_OUT),
                         .compare_value0(TDCR0_OUT),
                         .compare_value1(TDCR1_OUT),
                         .compare_value2(TDCR2_OUT),
                         .compare_value3(TDCR3_OUT),
                         .mask0(MASK0_OUT),
                         .mask1(MASK1_OUT),
                         .mask2(MASK2_OUT),
                         .mask3(MASK3_OUT),
                         .start_cap(OCCR_OUT[0] | cross_start_core),
                         .trigger_event(trigger_event),
                         .in_cross_trig1(in_cross_trig1),
                         .in_cross_trig2(in_cross_trig2),
                         .in_cross_trig3(in_cross_trig3),
                         .in_cross_trig4(in_cross_trig4),
                         .out_cross_trig1(out_cross_trig1),
                         .out_cross_trig2(out_cross_trig2),
                         .out_cross_trig3(out_cross_trig3),
                         .out_cross_trig4(out_cross_trig4),
                         .trigger_status({cross_trigger_status,self_trigger_status})
                       );

  // ---------------------------------------------------------------//
  // Synchronizer flop instance for                                 //
  // for sampling done signal from axi clock domain                 //
  // to sampling clock domain                                       //
  // ---------------------------------------------------------------//

  ddff_sync #(
              .REG_WIDTH(REG_WIDTH)
            ) rst_cntrl_signal_synchronizer_flop (
              .clk(sample_clk),
              .rstn(rstn),
              .D(reset_fifo_pntr),
              .Q(reset_fifo_wr_pntr_sync)
            );

  // ---------------------------------------------------------------//
  // OCLA sampling memory controller instance                       //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//

  ocla_mem_controller #(
                        .DATASIZE(NO_OF_PROBES),
                        .ADDRSIZE(COUNTER_WIDHT),
                        .NOSAMPLE_WIDTH(SAMPLE_COUNTER_WIDTH),
                        .MEM_DEPTH(MEM_DEPTH),
                        .SYNC_STAGES(SYNC_STAGES)
                      ) ocla_mem_controller_inst (
                        .rd_data(read_accumulated_data),
                        .rd_empty(mem_empty),
                        .wr_full(wr_full),
                        .wr_clk(sample_clk),
                        .rd_clk(S_AXI_ACLK),
                        .wr_rstn(rstn & !reset_fifo_wr_pntr_sync),
                        .rd_rstn(S_AXI_ARESETN & !reset_fifo_pntr),
                        .wr(data_wen),
                        .wr_data(data_accumulate),
                        .trigger_mode(TMTR_OUT[1:0]),
                        .rd(mem_read),
                        .nosamples(TMTR_OUT[12+:SAMPLE_COUNTER_WIDTH]),
                        .fixnosamples_en(TMTR_OUT[4]),
                        .sampling_done_ff(done_sampling_ff_sync)
                      );

  // ---------------------------------------------------------------//
  // stream_out_buffer instance                                     //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//

  stream_out_buffer #(
                      .WORD_CHUNK_COUNTER_WIDTH(WORD_CHUNK_CNTR_WIDTH),
                      .NUM_OFPROBES(NO_OF_PROBES),
                      .NUM_OF_WORD_CHUNKS(WORD_CHUNKS),
                      .PROBE_BITS(PROBE_BITS),
                      .AXI_DATA_WIDTH(AXI_DATA_WIDTH)
                    ) stream_out_buffer_inst (
                      .S_AXI_ACLK(S_AXI_ACLK),
                      .S_AXI_ARESETN(S_AXI_ARESETN),
                      .read_accumulated_data(read_accumulated_data),
                      .mem_empty(mem_empty),
                      .read_data_en(read_trace_mem_en),
                      .mem_read(mem_read),
                      .read_ready(S_AXI_RREADY),
                      .read_valid(mem_valid_data),
                      .read_data(TBDR_IN)
                    );


  // ---------------------------------------------------------------//
  // Axi Lite Slave instance                                        //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//
  axi_slv_lite # (
                 .IP_TYPE(IP_TYPE),
                 .IP_VERSION(IP_VERSION),
                 .IP_ID(IP_ID),
                 .NO_OF_PROBES(NO_OF_PROBES),
                 .MEM_DEPTH(MEM_DEPTH),
                 .C_S_AXI_DATA_WIDTH(32),
                 .C_S_AXI_ADDR_WIDTH(32)
               )
               axi_slv_lite_inst (
                 .TBDR_IN(TBDR_IN),
                 .mem_valid_data(mem_valid_data),
                 .mem_empty(mem_empty),
                 .data_avaible_inmem(done_sampling_ff_sync),
                 .read_trace_mem_en(read_trace_mem_en),
                 .TMTR_OUT(TMTR_OUT),
                 .OCCR_OUT(OCCR_OUT),
                 .TSSR0_OUT(TSSR0_OUT),
                 .TSSR1_OUT(TSSR1_OUT),
                 .TSSR2_OUT(TSSR2_OUT),
                 .TSSR3_OUT(TSSR3_OUT),
                 .TCUR0_OUT(TCUR0_OUT),
                 .TCUR1_OUT(TCUR1_OUT),
                 .TCUR2_OUT(TCUR2_OUT),
                 .TCUR3_OUT(TCUR3_OUT),
                 .TDCR0_OUT(TDCR0_OUT),
                 .TDCR1_OUT(TDCR1_OUT),
                 .TDCR2_OUT(TDCR2_OUT),
                 .TDCR3_OUT(TDCR3_OUT),
                 .MASK0_OUT(MASK0_OUT),
                 .MASK1_OUT(MASK1_OUT),
                 .MASK2_OUT(MASK2_OUT),
                 .MASK3_OUT(MASK3_OUT),
                 .reset_fifo_wr_pntr(reset_fifo_pntr),
                 .S_AXI_ACLK(S_AXI_ACLK),
                 .S_AXI_ARESETN(S_AXI_ARESETN ),
                 .S_AXI_AWADDR(S_AXI_AWADDR),
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
                 .S_AXI_ARADDR(S_AXI_ARADDR),
                 .S_AXI_ARPROT(S_AXI_ARPROT),
                 .S_AXI_ARVALID(S_AXI_ARVALID),
                 .S_AXI_ARREADY(S_AXI_ARREADY),
                 .S_AXI_RDATA(S_AXI_RDATA),
                 .S_AXI_RRESP(S_AXI_RRESP),
                 .S_AXI_RVALID(S_AXI_RVALID),
                 .S_AXI_RREADY(S_AXI_RREADY),
                 .intrn_rst_force(intrn_rst_force)
               );



endmodule


// *****************************************************************
// Dual Flop Synchronizer module
//
//
// *****************************************************************

module ddff_sync #(
    parameter REG_WIDTH = 1
  ) (
    input logic clk,
    input logic rstn,
    input logic [REG_WIDTH-1:0] D,
    output logic [REG_WIDTH-1:0] Q
  );

  localparam stages = 2;
  logic [REG_WIDTH-1:0] sync[stages-1:0];

  assign Q = sync[stages-1];

  always @(posedge clk or negedge rstn)
  begin
    if (!rstn)
    begin
      sync[0] <= 0;
    end
    else
    begin
      sync[0] <= D;
    end
  end

  genvar a;

  generate
    for (a = 0; a < (stages - 1); a = a + 1)
    begin
      always @(posedge clk or negedge rstn)
      begin
        if (!rstn)
        begin
          sync[a+1] <= 0;
        end
        else
        begin
          sync[a+1] <= sync[a];
        end
      end
    end
  endgenerate

endmodule

// *****************************************************************
// Trigger Control Unit
//
//
// *****************************************************************
module trigger_control_unit #(
    parameter NPROBES = 32,
    parameter SELECT_MUX_WIDTH = 10,
    parameter TRIGGER_SIGNAL_SELECT_RANGE = 32 ) (
      input logic sample_clk,
      input logic rstn,

      input logic [(NPROBES)-1:0] in_signals,
      //input logic [(NPROBES)-1:0] in_signals,
      input logic [127:0] config_bits, // config bits from both tcur registers.
      input logic [1:0] boolean_operator,
      input logic [31:0]probe_selector0,
      input logic [31:0]probe_selector1,
      input logic [31:0]probe_selector2,
      input logic [31:0]probe_selector3,


      input logic [32-1:0] compare_value0,
      input logic [32-1:0] compare_value1,
      input logic [32-1:0] compare_value2,
      input logic [32-1:0] compare_value3,

      input logic [32-1:0] mask0,
      input logic [32-1:0] mask1,
      input logic [32-1:0] mask2,
      input logic [32-1:0] mask3,

      input logic start_cap,
      output logic trigger_event,
      input logic in_cross_trig1,
      input logic in_cross_trig2,
      input logic in_cross_trig3,
      input logic in_cross_trig4,

      output logic out_cross_trig1,
      output logic out_cross_trig2,
      output logic out_cross_trig3,
      output logic out_cross_trig4,

      input logic [15:0] trigger_status

    );

  assign out_cross_trig1 = out_trig1;
  assign out_cross_trig2 = out_trig2;
  assign out_cross_trig3 = out_trig3;
  assign out_cross_trig4 = out_trig4;

  logic out_trig1;

  logic [32-1:0] compare_in0;
  logic [32-1:0] compare_in1;
  logic [32-1:0] compare_in2;
  logic [32-1:0] compare_in3;

  logic [31:0] tcur0_reg;
  logic [31:0] tcur1_reg;
  logic [31:0] tcur2_reg;
  logic [31:0] tcur3_reg;

  logic [31:0] tssr0_reg;
  logic [31:0] tssr1_reg;
  logic [31:0] tssr2_reg;
  logic [31:0] tssr3_reg;


  logic [TRIGGER_SIGNAL_SELECT_RANGE-1:0] trigger_select;
  assign trigger_select = in_signals[TRIGGER_SIGNAL_SELECT_RANGE-1:0];

  always @(posedge sample_clk or negedge rstn)
  begin
    if (!rstn)
    begin
      tcur0_reg <= 'b0;
      tcur1_reg <= 'b0;
      tcur2_reg <= 'b0;
      tcur3_reg <= 'b0;
      tssr0_reg <= 'b0;
      tssr1_reg <= 'b0;
      tssr2_reg <= 'b0;
      tssr3_reg <= 'b0;

      // compare_in0 <= 'b0;
      // compare_in1 <= 'b0;
      // compare_in2 <= 'b0;
      // compare_in3 <= 'b0;

    end
    else
    begin
      tcur0_reg <= config_bits[31:0];
      tcur1_reg <= config_bits[63:32];
      tcur2_reg <= config_bits[95:64];
      tcur3_reg <= config_bits[127:94];

      tssr0_reg <= probe_selector0;
      tssr1_reg <= probe_selector1;
      tssr2_reg <= probe_selector2;
      tssr3_reg <= probe_selector3;

      /*  compare_in0 <= compare_in0;
       compare_in1 <= compare_in1;
       compare_in2 <= compare_in2;
       compare_in3 <= compare_in3; */

    end
  end

  logic in_sig0;
  always @(*)
  begin
    case(tssr0_reg[28:24])
      5'd0:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 1];
      5'd1:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 2];
      5'd2:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 3];
      5'd3:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 4];
      5'd4:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 5];
      5'd5:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 6];
      5'd6:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 7];
      5'd7:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 8];
      5'd8:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 9];
      5'd9:
        compare_in0 = trigger_select[tssr0_reg[9:0] +:10];
      5'd10:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 11];
      5'd11:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 12];
      5'd12:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 13];
      5'd13:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 14];
      5'd14:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 15];
      5'd15:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 16];
      5'd16:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 17];
      5'd17:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 18];
      5'd18:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 19];
      5'd19:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 20];
      5'd20:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 21];
      5'd21:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 22];
      5'd22:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 23];
      5'd23:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 24];
      5'd24:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 25];
      5'd25:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 26];
      5'd26:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 27];
      5'd27:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 28];
      5'd28:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 29];
      5'd29:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 30];
      5'd30:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 31];
      8'd31:
        compare_in0 = trigger_select[tssr0_reg[9:0] +: 32];
      default:
        compare_in0 = 32'd0;

    endcase
  end
  logic [32-1:0] mask0_result;

  assign mask0_result = compare_in0 & mask0;
  assign in_sig0 = trigger_select[tssr0_reg[9:0]];

  trigger_unit trig_unit_a_inst (
                 .sample_clk(sample_clk),
                 .rstn(rstn),
                 .in_sig(in_sig0),
                 .bits_size(tssr0_reg[28:24]),
                 .config_bits(tcur0_reg),
                 .compare_in_signal(mask0_result),
                 .compare_value(compare_value0),
                 .start_cap(start_cap),
                 .trigger_event(out_trig1)
               );


  logic out_trig2;
  logic out_trig_bool;

  always @(*)
  begin
    case(tssr1_reg[28:24])
      5'd0:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 1];
      5'd1:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 2];
      5'd2:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 3];
      5'd3:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 4];
      5'd4:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 5];
      5'd5:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 6];
      5'd6:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 7];
      5'd7:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 8];
      5'd8:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 9];
      5'd9:
        compare_in1 = trigger_select[tssr1_reg[9:0] +:10];
      5'd10:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 11];
      5'd11:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 12];
      5'd12:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 13];
      5'd13:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 14];
      5'd14:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 15];
      5'd15:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 16];
      5'd16:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 17];
      5'd17:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 18];
      5'd18:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 19];
      5'd19:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 20];
      5'd20:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 21];
      5'd21:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 22];
      5'd22:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 23];
      5'd23:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 24];
      5'd24:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 25];
      5'd25:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 26];
      5'd26:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 27];
      5'd27:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 28];
      5'd28:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 29];
      5'd29:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 30];
      5'd30:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 31];
      5'd31:
        compare_in1 = trigger_select[tssr1_reg[9:0] +: 32];
      default:
        compare_in1 = 32'd0;


    endcase
  end

  logic [32-1:0] mask1_result;

  assign mask1_result = compare_in1 & mask1;
  logic in_sig1;
  assign in_sig1 = trigger_select[tssr1_reg[9:0]];

  trigger_unit trig_unit_b_inst (
                 .sample_clk(sample_clk),
                 .rstn(rstn),
                 .in_sig(in_sig1),
                 .bits_size(tssr1_reg[28:24]),
                 .config_bits(tcur1_reg),
                 .compare_in_signal(mask1_result),
                 .compare_value(compare_value1),
                 .start_cap(start_cap),
                 .trigger_event(out_trig2)
               );


  /**********************************************/
  logic in_sig3;
  logic out_trig3,out_trig4;

  always @(*)
  begin
    case(tssr2_reg[28:24])
      5'd0:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 1];
      5'd1:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 2];
      5'd2:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 3];
      5'd3:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 4];
      5'd4:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 5];
      5'd5:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 6];
      5'd6:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 7];
      5'd7:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 8];
      5'd8:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 9];
      5'd9:
        compare_in2 = trigger_select[tssr2_reg[9:0] +:10];
      5'd10:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 11];
      5'd11:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 12];
      5'd12:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 13];
      5'd13:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 14];
      5'd14:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 15];
      5'd15:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 16];
      5'd16:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 17];
      5'd17:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 18];
      5'd18:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 19];
      5'd19:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 20];
      5'd20:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 21];
      5'd21:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 22];
      5'd22:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 23];
      5'd23:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 24];
      5'd24:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 25];
      5'd25:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 26];
      5'd26:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 27];
      5'd27:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 28];
      5'd28:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 29];
      5'd29:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 30];
      5'd30:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 31];
      5'd31:
        compare_in2 = trigger_select[tssr2_reg[9:0] +: 32];
      default:
        compare_in2 = 32'd0;


    endcase
  end
  logic in_sig2;
  assign in_sig2 = trigger_select[tssr2_reg[9:0]];

  always @(*)
  begin
    case(tssr3_reg[28:24])
      5'd0:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 1];
      5'd1:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 2];
      5'd2:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 3];
      5'd3:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 4];
      5'd4:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 5];
      5'd5:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 6];
      5'd6:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 7];
      5'd7:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 8];
      5'd8:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 9];
      5'd9:
        compare_in3 = trigger_select[tssr3_reg[9:0] +:10];
      5'd10:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 11];
      5'd11:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 12];
      5'd12:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 13];
      5'd13:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 14];
      5'd14:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 15];
      5'd15:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 16];
      5'd16:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 17];
      5'd17:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 18];
      5'd18:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 19];
      5'd19:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 20];
      5'd20:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 21];
      5'd21:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 22];
      5'd22:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 23];
      5'd23:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 24];
      5'd24:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 25];
      5'd25:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 26];
      5'd26:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 27];
      5'd27:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 28];
      5'd28:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 29];
      5'd29:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 30];
      5'd30:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 31];
      5'd31:
        compare_in3 = trigger_select[tssr3_reg[9:0] +: 32];
      default:
        compare_in3 = 32'd0;


    endcase
  end

  logic [32-1:0] mask2_result;
  assign mask2_result = compare_in2 & mask2;

  logic [32-1:0] mask3_result;
  assign mask3_result = compare_in3 & mask3;

  assign in_sig3 = trigger_select[tcur3_reg[9:0]];


  trigger_unit trig_unit_c_inst (
                 .sample_clk(sample_clk),
                 .rstn(rstn),
                 .in_sig(in_sig2),
                 .bits_size(tssr2_reg[28:24]),
                 .config_bits(tcur2_reg),
                 .compare_in_signal(mask2_result),
                 .compare_value(compare_value2),
                 .start_cap(start_cap),
                 .trigger_event(out_trig3)
               );


  trigger_unit trig_unit_d_inst (
                 .sample_clk(sample_clk),
                 .rstn(rstn),
                 .in_sig(in_sig3),
                 .bits_size(tssr3_reg[28:24]),
                 .config_bits(tcur3_reg),
                 .compare_in_signal(mask3_result),
                 .compare_value(compare_value3),
                 .start_cap(start_cap),
                 .trigger_event(out_trig4)
               );


  /*********************************************/

  boolean_comparator bool_comp (
                       .in_sig1(out_trig1),
                       .in_sig2(out_trig2),
                       .in_sig3(out_trig3),
                       .in_sig4(out_trig4),
                       //.config_bits(config_bits_ff[16:15]),
                       .config_bits(boolean_operator),
                       .trigger_status(trigger_status),
                       .trigger_event(out_trig_bool),
                       .in_cross_trig1(in_cross_trig1),
                       .in_cross_trig2(in_cross_trig2),
                       .in_cross_trig3(in_cross_trig3),
                       .in_cross_trig4(in_cross_trig4)
                     );

  assign trigger_event = out_trig_bool;
  // assign trigger_event = config_bits_ff[0] ? out_trig_bool : (out_trig1 | out_trig2 | out_trig3 | out_trig4);
  // assign trigger_event = out_trig1;

endmodule

// *****************************************************************
// Boolean Compare
//
//
// *****************************************************************
module boolean_comparator (

    input logic in_sig1,
    input logic in_sig2,
    input logic in_sig3,
    input logic in_sig4,

    //input logic [1:0] config_bits,
    input logic [1:0] config_bits,
    input logic [15:0] trigger_status,   // tirgger status for each trigger unit. 2 bits represent one trigger unit
    output logic trigger_event,
    input logic in_cross_trig1,
    input logic in_cross_trig2,
    input logic in_cross_trig3,
    input logic in_cross_trig4
  );

  logic [3:0] self_trigger_bits;
  logic [3:0] cross_trigger_bits;

  logic in_sig_ff;
  logic out_sig;
  logic self_out_sig;
  logic cross_out_sig;


  assign self_trigger_bits[0] = trigger_status[0] | trigger_status[1];
  assign self_trigger_bits[1] = trigger_status[2] | trigger_status[3];
  assign self_trigger_bits[2] = trigger_status[4] | trigger_status[5];
  assign self_trigger_bits[3] = trigger_status[6] | trigger_status[7];
  assign cross_trigger_bits[0] = trigger_status[8] | trigger_status[9];
  assign cross_trigger_bits[1] = trigger_status[10] | trigger_status[11];
  assign cross_trigger_bits[2] = trigger_status[12] | trigger_status[13];
  assign cross_trigger_bits[3] = trigger_status[14] | trigger_status[15];


  always @(*)
  begin
    case (self_trigger_bits)
      4'd0: self_out_sig = 0;
      4'd1: self_out_sig = in_sig1;
      4'd2: self_out_sig = in_sig2;
      4'd3: self_out_sig = in_sig1 & in_sig2;
      4'd4: self_out_sig = in_sig3;
      4'd5: self_out_sig = in_sig1 & in_sig3;
      4'd6: self_out_sig = in_sig2 & in_sig3;
      4'd7: self_out_sig = in_sig1 & in_sig2 & in_sig3;
      4'd8: self_out_sig = in_sig4;
      4'd9: self_out_sig = in_sig1 & in_sig4;
      4'd10: self_out_sig = in_sig2 & in_sig4;
      4'd11: self_out_sig = in_sig1 & in_sig2 & in_sig4;
      4'd12: self_out_sig = in_sig3 & in_sig4;
      4'd13: self_out_sig = in_sig1 & in_sig3 & in_sig4;
      4'd14: self_out_sig = in_sig2 & in_sig3 & in_sig4;
      4'd15: self_out_sig = in_sig1 & in_sig2 & in_sig3 & in_sig4; 
      endcase
  end


  always @(*)
  begin
    case (cross_trigger_bits)
      4'd0: cross_out_sig = 0;
      4'd1: cross_out_sig = in_cross_trig1;
      4'd2: cross_out_sig = in_cross_trig2;
      4'd3: cross_out_sig = in_cross_trig1 & in_cross_trig2;
      4'd4: cross_out_sig = in_cross_trig3;
      4'd5: cross_out_sig = in_cross_trig1 & in_cross_trig3;
      4'd6: cross_out_sig = in_cross_trig2 & in_cross_trig3;
      4'd7: cross_out_sig = in_cross_trig1 & in_cross_trig2 & in_cross_trig3;
      4'd8: cross_out_sig = in_cross_trig4;
      4'd9: cross_out_sig = in_cross_trig1 & in_cross_trig4;
      4'd10: cross_out_sig = in_cross_trig2 & in_cross_trig4;
      4'd11: cross_out_sig = in_cross_trig1 & in_cross_trig2 & in_cross_trig4;
      4'd12: cross_out_sig = in_cross_trig3 & in_cross_trig4;
      4'd13: cross_out_sig = in_cross_trig1 & in_cross_trig3 & in_cross_trig4;
      4'd14: cross_out_sig = in_cross_trig2 & in_cross_trig3 & in_cross_trig4;
      4'd15: cross_out_sig = in_cross_trig1 & in_cross_trig2 & in_cross_trig3 & in_cross_trig4; 
      endcase
  end
  assign trigger_event = out_sig;

  //always_comb begin
  always @(*)
  begin
    case (config_bits)
      2'b00:
        out_sig = in_sig1 || in_sig2 || in_sig3 || in_sig4 || in_cross_trig1 || in_cross_trig2 || in_cross_trig3 || in_cross_trig4 ;  // Global OR
      2'b01:
      begin

        if(trigger_status[7:0] == 0  && trigger_status[15:8] == 0)
          out_sig = 0;
        else if (trigger_status[7:0] != 0  && trigger_status[15:8] == 0)
          out_sig =self_out_sig;

        else if (trigger_status[7:0] == 0  && trigger_status[15:8] != 0)

          out_sig = cross_out_sig;
        else
          out_sig = self_out_sig & cross_out_sig;
      end


      2'b10:
        out_sig = in_sig1 || in_sig2 || in_sig3 || in_sig4 || in_cross_trig1 || in_cross_trig2 || in_cross_trig3 || in_cross_trig4 ;  // Global OR
      2'b11:
        out_sig = in_sig1 ^ in_sig2 ^ in_sig3 ^ in_sig4;     // Global XOR
      default:
        out_sig = 1'b0;  // default
    endcase
  end

endmodule

// *****************************************************************
// Trigger Unit
//
//
// *****************************************************************
module trigger_unit (

    input logic sample_clk,
    input logic rstn,
    input logic in_sig,
    input logic [4:0]bits_size,
    input logic [31:0] config_bits,
    input logic [32-1:0] compare_in_signal,
    input logic [32-1:0] compare_value,
    input logic       start_cap,
    output logic trigger_event

  );

  logic trigger_event_ed;

  logic trigger_event_vc;
  logic trigger_event_lvl;
  logic out_sig;

  dflop dff_out_sig (
          .sample_clk(sample_clk),
          .rstn(rstn),
          .D(out_sig),
          .Q(trigger_event)
        );

  // always_comb begin
  always @(*)
  begin
    case (config_bits[1:0])
      2'b00:
        out_sig = 1'b0;  // no trigger
      2'b01:
        out_sig = trigger_event_ed;  //  edge detect
      2'b10:
        out_sig = trigger_event_lvl;  // level detect
      2'b11:
        out_sig = trigger_event_vc;  // value compare
      default:
        out_sig = 1'b0;  // default
    endcase
  end

  edge_detector ed (
                  .sample_clk(sample_clk),
                  .rstn(rstn),
                  .en(config_bits[1:0] == 2'b01),
                  .in_sig(in_sig),
                  .config_bits(config_bits[3:2]),
                  .edge_trigger_event(trigger_event_ed)
                );
  level_detect lvld (
                 .sample_clk(sample_clk),

                 .rstn(rstn),
                 .in_sig(in_sig),
                 .en(config_bits[1:0] == 2'b10),
                 .config_bits(config_bits[5:4]),
                 .start_cap(start_cap),
                 .lvl_trigger_event(trigger_event_lvl)
               );
  value_compare vc (
                  .sample_clk(sample_clk),
                  .rstn(rstn),
                  .en(config_bits[1:0] == 2'b11),
                  .bits_size(bits_size),
                  .in_sig(compare_in_signal),
                  .reg_value(compare_value),
                  .config_bits(config_bits[7:6]),
                  .vc_trigger_event(trigger_event_vc)
                );

endmodule

module edge_detector (
    input logic sample_clk,
    input logic rstn,
    input logic en,
    input logic in_sig,
    input logic [1:0] config_bits,
    output logic edge_trigger_event
  );

  logic in_sig_ff;
  logic out_sig;

  dflop dff_in_sig (
          .sample_clk(sample_clk),
          .rstn(rstn),
          .D(in_sig),
          .Q(in_sig_ff)
        );
  dflop dff_out_sig (
          .sample_clk(sample_clk),
          .rstn(rstn),
          .D(out_sig),
          .Q(edge_trigger_event)
        );

  always_comb
  begin
    if (en)
    begin
      case (config_bits)
        2'b00:
          out_sig = 1'b0;  // no trigger
        2'b01:
          out_sig = in_sig & !(in_sig_ff);  // rising edge detect
        2'b10:
          out_sig = !(in_sig) & in_sig_ff;  // falling edge detect
        2'b11:
          out_sig = in_sig ^ in_sig_ff;  // either edge detec
        default:
          out_sig = 1'b0;  // default
      endcase
    end
    else
      out_sig = 1'b0;
  end

endmodule


// *****************************************************************
// Value Compare Module
//
//
// *****************************************************************
module value_compare  (
    input logic sample_clk,
    input logic rstn,
    input logic en,
    input logic [4:0] bits_size,
    input logic [32-1:0] in_sig,
    input logic [32-1:0] reg_value,
    input logic [1:0] config_bits,
    output logic vc_trigger_event
  );

  logic out_sig0, out_sig1, out_sig2, out_sig3;

  // dflop dff_out_sig (.sample_clk(sample_clk),.rstn(rstn),.D(out_sig),.Q(vc_trigger_event));

  //always_comb
  always@(*)
  begin
    if (en)
    begin
      case (config_bits)
        2'b00:
        begin // no trigger
          out_sig0 = 1'b0;
          out_sig1 = 1'b0;
          out_sig2 = 1'b0;
          out_sig3 = 1'b0;
        end

        2'b01:    // equal to detect
        case(bits_size)
          5'd0:
          begin
            out_sig1 = reg_value[0] == in_sig[0];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd1:
          begin
            out_sig1 = reg_value[0+:2] == in_sig[0+:2];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd2:
          begin
            out_sig1 = reg_value[0+:3] == in_sig[0+:3];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd3:
          begin
            out_sig1 = reg_value[0+:4] == in_sig[0+:4];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd4:
          begin
            out_sig1 = reg_value[0+:5] == in_sig[0+:5];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd5:
          begin
            out_sig1 = reg_value[0+:6] == in_sig[0+:6];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd6:
          begin
            out_sig1 = reg_value[0+:7] == in_sig[0+:7];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd7:
          begin
            out_sig1 = reg_value[0+:8] == in_sig[0+:8];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd8:
          begin
            out_sig1 = reg_value[0+:9] == in_sig[0+:9];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd9:
          begin
            out_sig1 = reg_value[0+:10] == in_sig[0+:10];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd10:
          begin
            out_sig1 = reg_value[0+:11] == in_sig[0+:11];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd11:
          begin
            out_sig1 = reg_value[0+:12] == in_sig[0+:12];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd12:
          begin
            out_sig1 = reg_value[0+:13] == in_sig[0+:13];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd13:
          begin
            out_sig1 = reg_value[0+:14] == in_sig[0+:14];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd14:
          begin
            out_sig1 = reg_value[0+:15] == in_sig[0+:15];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd15:
          begin
            out_sig1 = reg_value[0+:16] == in_sig[0+:16];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd16:
          begin
            out_sig1 = reg_value[0+:17] == in_sig[0+:17];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd17:
          begin
            out_sig1 = reg_value[0+:18] == in_sig[0+:18];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd18:
          begin
            out_sig1 = reg_value[0+:19] == in_sig[0+:19];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd19:
          begin
            out_sig1 = reg_value[0+:20] == in_sig[0+:20];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd20:
          begin
            out_sig1 = reg_value[0+:21] == in_sig[0+:21];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd21:
          begin
            out_sig1 = reg_value[0+:22] == in_sig[0+:22];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd22:
          begin
            out_sig1 = reg_value[0+:23] == in_sig[0+:23];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd23:
          begin
            out_sig1 = reg_value[0+:24] == in_sig[0+:24];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd24:
          begin
            out_sig1 = reg_value[0+:25] == in_sig[0+:25];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd25:
          begin
            out_sig1 = reg_value[0+:26] == in_sig[0+:26];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd26:
          begin
            out_sig1 = reg_value[0+:27] == in_sig[0+:27];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd27:
          begin
            out_sig1 = reg_value[0+:28] == in_sig[0+:28];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd28:
          begin
            out_sig1 = reg_value[0+:29] == in_sig[0+:29];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd29:
          begin
            out_sig1 = reg_value[0+:30] == in_sig[0+:30];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd30:
          begin
            out_sig1 = reg_value[0+:31] == in_sig[0+:31];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd31:
          begin
            out_sig1 = reg_value[0+:32] == in_sig[0+:32];
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end
          default:
          begin
            out_sig1 = 1'b0;
            out_sig0 = 1'b0;
            out_sig2 = 1'b0;
            out_sig3 = 1'b0;
          end // default

        endcase

        2'b10:     // less than detect
        case(bits_size)
          5'd0:
          begin
            out_sig2 = reg_value[0] > in_sig[0];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd1:
          begin
            out_sig2 = reg_value[0+:2] > in_sig[0+:2];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd2:
          begin
            out_sig2 = reg_value[0+:3] > in_sig[0+:3];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd3:
          begin
            out_sig2 = reg_value[0+:4] > in_sig[0+:4];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd4:
          begin
            out_sig2 = reg_value[0+:5] > in_sig[0+:5];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd5:
          begin
            out_sig2 = reg_value[0+:6] > in_sig[0+:6];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd6:
          begin
            out_sig2 = reg_value[0+:7] > in_sig[0+:7];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd7:
          begin
            out_sig2 = reg_value[0+:8] > in_sig[0+:8];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd8:
          begin
            out_sig2 = reg_value[0+:9] > in_sig[0+:9];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd9:
          begin
            out_sig2 = reg_value[0+:10] > in_sig[0+:10];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd10:
          begin
            out_sig2 = reg_value[0+:11] > in_sig[0+:11];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd11:
          begin
            out_sig2 = reg_value[0+:12] > in_sig[0+:12];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd12:
          begin
            out_sig2 = reg_value[0+:13] > in_sig[0+:13];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd13:
          begin
            out_sig2 = reg_value[0+:14] > in_sig[0+:14];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd14:
          begin
            out_sig2 = reg_value[0+:15] > in_sig[0+:15];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd15:
          begin
            out_sig2 = reg_value[0+:16] > in_sig[0+:16];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd16:
          begin
            out_sig2 = reg_value[0+:17] > in_sig[0+:17];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd17:
          begin
            out_sig2 = reg_value[0+:18] > in_sig[0+:18];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd18:
          begin
            out_sig2 = reg_value[0+:19] > in_sig[0+:19];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd19:
          begin
            out_sig2 = reg_value[0+:20] > in_sig[0+:20];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd20:
          begin
            out_sig2 = reg_value[0+:21] > in_sig[0+:21];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd21:
          begin
            out_sig2 = reg_value[0+:22] > in_sig[0+:22];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd22:
          begin
            out_sig2 = reg_value[0+:23] > in_sig[0+:23];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd23:
          begin
            out_sig2 = reg_value[0+:24] > in_sig[0+:24];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd24:
          begin
            out_sig2 = reg_value[0+:25] > in_sig[0+:25];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd25:
          begin
            out_sig2 = reg_value[0+:26] > in_sig[0+:26];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd26:
          begin
            out_sig2 = reg_value[0+:27] > in_sig[0+:27];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd27:
          begin
            out_sig2 = reg_value[0+:28] > in_sig[0+:28];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd28:
          begin
            out_sig2 = reg_value[0+:29] > in_sig[0+:29];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd29:
          begin
            out_sig2 = reg_value[0+:30] > in_sig[0+:30];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd30:
          begin
            out_sig2 = reg_value[0+:31] > in_sig[0+:31];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          5'd31:
          begin
            out_sig2 = reg_value[0+:32] > in_sig[0+:32];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end
          default:
          begin
            out_sig2 = 1'b0;
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig3 = 1'b0;
          end// default
        endcase

        2'b11: // greater than detect

        case(bits_size)
          5'd0:
          begin
            out_sig3 = reg_value[0] < in_sig[0];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd1:
          begin
            out_sig3 = reg_value[0+:2] < in_sig[0+:2];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd2:
          begin
            out_sig3 = reg_value[0+:3] < in_sig[0+:3];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd3:
          begin
            out_sig3 = reg_value[0+:4] < in_sig[0+:4];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd4:
          begin
            out_sig3 = reg_value[0+:5] < in_sig[0+:5];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd5:
          begin
            out_sig3 = reg_value[0+:6] < in_sig[0+:6];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd6:
          begin
            out_sig3 = reg_value[0+:7] < in_sig[0+:7];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd7:
          begin
            out_sig3 = reg_value[0+:8] < in_sig[0+:8];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd8:
          begin
            out_sig3 = reg_value[0+:9] < in_sig[0+:9];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd9:
          begin
            out_sig3 = reg_value[0+:10] < in_sig[0+:10];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd10:
          begin
            out_sig3 = reg_value[0+:11] < in_sig[0+:11];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd11:
          begin
            out_sig3 = reg_value[0+:12] < in_sig[0+:12];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd12:
          begin
            out_sig3 = reg_value[0+:13] < in_sig[0+:13];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd13:
          begin
            out_sig3 = reg_value[0+:14] < in_sig[0+:14];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd14:
          begin
            out_sig3 = reg_value[0+:15] < in_sig[0+:15];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd15:
          begin
            out_sig3 = reg_value[0+:16] < in_sig[0+:16];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd16:
          begin
            out_sig3 = reg_value[0+:17] < in_sig[0+:17];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd17:
          begin
            out_sig3 = reg_value[0+:18] < in_sig[0+:18];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd18:
          begin
            out_sig3 = reg_value[0+:19] < in_sig[0+:19];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd19:
          begin
            out_sig3 = reg_value[0+:20] < in_sig[0+:20];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd20:
          begin
            out_sig3 = reg_value[0+:21] < in_sig[0+:21];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd21:
          begin
            out_sig3 = reg_value[0+:22] < in_sig[0+:22];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd22:
          begin
            out_sig3 = reg_value[0+:23] < in_sig[0+:23];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd23:
          begin
            out_sig3 = reg_value[0+:24] < in_sig[0+:24];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd24:
          begin
            out_sig3 = reg_value[0+:25] < in_sig[0+:25];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd25:
          begin
            out_sig3 = reg_value[0+:26] < in_sig[0+:26];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd26:
          begin
            out_sig3 = reg_value[0+:27] < in_sig[0+:27];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd27:
          begin
            out_sig3 = reg_value[0+:28] < in_sig[0+:28];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd28:
          begin
            out_sig3 = reg_value[0+:29] < in_sig[0+:29];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd29:
          begin
            out_sig3 = reg_value[0+:30] < in_sig[0+:30];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd30:
          begin
            out_sig3 = reg_value[0+:31] < in_sig[0+:31];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          5'd31:
          begin
            out_sig3 = reg_value[0+:32] < in_sig[0+:32];
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end
          default:
          begin
            out_sig3 = 1'b0;
            out_sig0 = 1'b0;
            out_sig1 = 1'b0;
            out_sig2 = 1'b0;
          end// default
        endcase
        default:
        begin
          out_sig3 = 1'b0;
          out_sig0 = 1'b0;
          out_sig1 = 1'b0;
          out_sig2 = 1'b0;
        end // default
      endcase
    end
    else
    begin
      out_sig0 = 1'b0;
      out_sig1 = 1'b0;
      out_sig2 = 1'b0;

      out_sig3 = 1'b0;

    end
  end



  lvl2pulse level2pulse (
              .sample_clk(sample_clk),
              .rstn(rstn),
              .in_sig (out_sig0 | out_sig1 | out_sig2 | out_sig3),
              // .in_sig (1'b1),
              .out_sig(vc_trigger_event)
            );

endmodule

// *****************************************************************
// Level Detector
//
//
// *****************************************************************
module level_detect (
    input  logic sample_clk,
    input  logic rstn,
    input  logic en,
    input  logic in_sig,
    input  logic [1:0]config_bits,
    input  logic start_cap,
    output logic lvl_trigger_event
  );

  logic in_sig_ff;
  logic out_sig;

  //dflop dff_out_sig (.sample_clk(sample_clk),.rstn(rstn),.D(out_sig),.Q(trigger_event));
  always_comb
  begin
    if (en & start_cap)
    begin
      case (config_bits)
        2'b00:
          out_sig = !in_sig;  // low level
        2'b01:
          out_sig = in_sig;  // high level
        default:
          out_sig = 1'b0;  // default
      endcase
    end
    else
      out_sig = 1'b0;
  end

  lvl2pulse level2pulse (
              .sample_clk(sample_clk),
              .rstn(rstn),
              .in_sig (out_sig),
              .start_cap(start_cap),
              .out_sig(lvl_trigger_event)
            );
endmodule

// *****************************************************************
// DFF
//
//
// *****************************************************************
module dflop(
    input  logic sample_clk,
    input  logic rstn,
    input  logic D,
    output logic Q
  );

  always @(posedge sample_clk or negedge rstn)
  begin
    if (!rstn)
      Q <= 1'b0;
    else
      Q <= D;
  end
endmodule

// *****************************************************************
// Level to Pulse
//
//
// *****************************************************************
module lvl2pulse (
    input  logic sample_clk,
    input logic rstn,
    input  logic in_sig,
    input  logic start_cap,
    output logic out_sig
  );
  logic r1, r2, r3;

  always @(posedge sample_clk or negedge rstn)
  begin
    if (!rstn)
    begin
      r1 <= 1'b0;
      r2 <= 1'b0;
      r3 <= 1'b0;

    end
    else
    begin
      r1 <= in_sig;  // first reg in synchronizer
      r2 <= r1;  // second reg in synchronizer, output is in sync!
      r3 <= r2;  // remembers previous state of button
    end
  end
  // rising edge = old value is 0, new value is 1
  // assign out_sig = ~r3 & r2;
  assign out_sig = r2;
endmodule

// *****************************************************************
// AXI Slave Interface
//
//
// *****************************************************************

module axi_slv_lite #(
    // Users to add parameters here

    // User parameters ends
    // Do not modify the parameters beyond this line

    // IP Type parameters

    parameter IP_TYPE = "ocla",
    parameter IP_VERSION = 32'h1,
    parameter IP_ID = 32'h3881734,
    parameter NO_OF_PROBES = 32'd32,
    parameter MEM_DEPTH =32,

    // WIDTH of S_AXI data bus
    parameter integer C_S_AXI_DATA_WIDTH = 32,
    // WIDTH of S_AXI address bus
    parameter integer C_S_AXI_ADDR_WIDTH = 32
  ) (
    // Users to add ports here
    input wire [C_S_AXI_DATA_WIDTH-1:0] TBDR_IN,
    input wire mem_valid_data,
    input wire mem_empty,
    input wire data_avaible_inmem,
    output wire read_trace_mem_en,

    output wire [C_S_AXI_DATA_WIDTH-1:0] TMTR_OUT,

    output wire [C_S_AXI_DATA_WIDTH-1:0] OCCR_OUT,

    output wire [C_S_AXI_DATA_WIDTH-1:0] TSSR0_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TSSR1_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TSSR2_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TSSR3_OUT,

    output wire [C_S_AXI_DATA_WIDTH-1:0] TCUR0_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TCUR1_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TCUR2_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TCUR3_OUT,

    output wire [C_S_AXI_DATA_WIDTH-1:0] TDCR0_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TDCR1_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TDCR2_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] TDCR3_OUT,


    output wire [C_S_AXI_DATA_WIDTH-1:0] MASK0_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] MASK1_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] MASK2_OUT,
    output wire [C_S_AXI_DATA_WIDTH-1:0] MASK3_OUT,

    output wire reset_fifo_wr_pntr,


    // User ports ends
    // Do not modify the ports beyond this line

    // Global Clock Signal
    input wire S_AXI_ACLK,
    // Global Reset Signal. This Signal is Active LOW
    input wire S_AXI_ARESETN,
    // Write address (issued by master, acceped by Slave)
    input wire [C_S_AXI_ADDR_WIDTH-1 : 0] S_AXI_AWADDR,
    // Write channel Protection type. This signal indicates the
    // privilege and security level of the transaction, and whether
    // the transaction is a data access or an instruction access.
    input wire [2 : 0] S_AXI_AWPROT,
    // Write address valid. This signal indicates that the master signaling
    // valid write address and control information.
    input wire S_AXI_AWVALID,
    // Write address ready. This signal indicates that the slave is ready
    // to accept an address and associated control signals.
    output wire S_AXI_AWREADY,
    // Write data (issued by master, acceped by Slave)
    input wire [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_WDATA,
    // Write strobes. This signal indicates which byte lanes hold
    // valid data. There is one write strobe bit for each eight
    // bits of the write data bus.
    input wire [(C_S_AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
    // Write valid. This signal indicates that valid write
    // data and strobes are available.
    input wire S_AXI_WVALID,
    // Write ready. This signal indicates that the slave
    // can accept the write data.
    output wire S_AXI_WREADY,
    // Write response. This signal indicates the status
    // of the write transaction.
    output wire [1 : 0] S_AXI_BRESP,
    // Write response valid. This signal indicates that the channel
    // is signaling a valid write response.
    output wire S_AXI_BVALID,
    // Response ready. This signal indicates that the master
    // can accept a write response.
    input wire S_AXI_BREADY,
    // Read address (issued by master, acceped by Slave)
    input wire [C_S_AXI_ADDR_WIDTH-1 : 0] S_AXI_ARADDR,
    // Protection type. This signal indicates the privilege
    // and security level of the transaction, and whether the
    // transaction is a data access or an instruction access.
    input wire [2 : 0] S_AXI_ARPROT,
    // Read address valid. This signal indicates that the channel
    // is signaling valid read address and control information.
    input wire S_AXI_ARVALID,
    // Read address ready. This signal indicates that the slave is
    // ready to accept an address and associated control signals.
    output wire S_AXI_ARREADY,
    // Read data (issued by slave)
    output wire [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_RDATA,
    // Read response. This signal indicates the status of the
    // read transfer.
    output wire [1 : 0] S_AXI_RRESP,
    // Read valid. This signal indicates that the channel is
    // signaling the required read data.
    output wire S_AXI_RVALID,
    // Read ready. This signal indicates that the master can
    // accept the read data and response information.
    input wire S_AXI_RREADY,

    // force reset through command

    output intrn_rst_force
  );

  typedef enum    logic [5:0]  {IP_TYPE_REG_ADDR, IP_VERSION_REG_ADDR, IP_ID_REG_ADDR, RESERVED0,RESERVED1,
                                UDIP0_ADDR, UDIP1_ADDR, UDIP2_ADDR, OCSR_REG_ADDR,TMTR_REG_ADDR,
                                TBDR_ADDR, OCCR_REG_ADDR, TSSR0_REG_ADDR, TCUR0_REG_ADDR, TDCR0_REG_ADDR, MASK0_REG_ADDR,
                                TSSR1_REG_ADDR=24, TCUR1_REG_ADDR, TDCR1_REG_ADDR,MASK1_REG_ADDR, TSSR2_REG_ADDR=36, TCUR2_REG_ADDR,
                                TDCR2_REG_ADDR, MASK2_REG_ADDR, TSSR3_REG_ADDR=48, TCUR3_REG_ADDR, TDCR3_REG_ADDR, MASK3_REG_ADDR} Config_Registers_Addr;

  // AXI4LITE signals
  reg [C_S_AXI_ADDR_WIDTH-1 : 0] axi_awaddr;
  reg axi_awready;
  reg axi_wready;
  reg [1 : 0] axi_bresp;
  reg axi_bvalid;
  reg [C_S_AXI_ADDR_WIDTH-1 : 0] axi_araddr;
  reg axi_arready;
  reg [C_S_AXI_DATA_WIDTH-1 : 0] axi_rdata;
  reg [1 : 0] axi_rresp;
  reg axi_rvalid;

  // Example-specific design signals
  // local parameter for addressing 32 bit / 64 bit C_S_AXI_DATA_WIDTH
  // ADDR_LSB is used for addressing 32/64 bit registers/memories
  // ADDR_LSB = 2 for 32 bits (n downto 2)
  // ADDR_LSB = 3 for 64 bits (n downto 3)
  localparam integer ADDR_LSB = (C_S_AXI_DATA_WIDTH / 32) + 1;
  localparam integer OPT_MEM_ADDR_BITS = 5;
  //----------------------------------------------
  //-- Signals for user logic register space example
  //------------------------------------------------
  //-- Number of Slave Registers 4

  reg [C_S_AXI_DATA_WIDTH-1:0]	IP_TYPE_REG;       // offset = 0x00 : Access "RO" : IP Type "ocla"
  reg [C_S_AXI_DATA_WIDTH-1:0]	IP_VERSION_REG;    // offset = 0x04 : Access "RO" : IP Version "0x00000001"
  reg [C_S_AXI_DATA_WIDTH-1:0]	IP_ID_REG;         // offset = 0x08 : Access "RO" : IP ID generated by IP configurator
  reg [C_S_AXI_DATA_WIDTH-1:0]	OCSR_REG;          // offset = 0x0C : Access "RO" : OCLA Status Register
  reg [C_S_AXI_DATA_WIDTH-1:0]	UIDP0_REG;         // offset = 0x0C : Access "RO" : OCLA Status Register
  reg [C_S_AXI_DATA_WIDTH-1:0]	UIDP1_REG;         // offset = 0x0C : Access "RO" : OCLA Status Register
  reg [C_S_AXI_DATA_WIDTH-1:0]	UIDP2_REG;         // offset = 0x0C : Access "RO" : OCLA Status Register

  reg [C_S_AXI_DATA_WIDTH-1:0]	TMTR_REG;          // offset = 0x10 : Access "RW" : Trigger Mode Type  Register
  //reg [C_S_AXI_DATA_WIDTH-1:0]	TBDR;            // offset = 0x14 : Access "RO" : Trace Buffer Data Register
  reg [C_S_AXI_DATA_WIDTH-1:0]	OCCR_REG;          // offset = 0x18 : Access "RW" : OCLA Controll Register

  //------Trigger Source Selection Registers-----------//

  reg [C_S_AXI_DATA_WIDTH-1:0]	TSSR0_REG;         // offset = 0x1C : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TSSR1_REG;         // offset = 0x20 : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TSSR2_REG;         // offset = 0x24 : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TSSR3_REG;         // offset = 0x28 : Access "RW"

  //------Trigger Controll Unit Registers-----------//

  reg [C_S_AXI_DATA_WIDTH-1:0]	TCUR0_REG;         // offset = 0x2C : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TCUR1_REG;         // offset = 0x30 : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TCUR2_REG;         // offset = 0x34 : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TCUR3_REG;         // offset = 0x38 : Access "RW"

  //------Trigger Data Compare Registers-----------//

  reg [C_S_AXI_DATA_WIDTH-1:0]	TDCR0_REG;         // offset = 0x3C : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TDCR1_REG;         // offset = 0x40 : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TDCR2_REG;         // offset = 0x44 : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	TDCR3_REG;         // offset = 0x48 : Access "RW"


  reg [C_S_AXI_DATA_WIDTH-1:0]	MASK0_REG;         // offset = 0x3C : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	MASK1_REG;         // offset = 0x40 : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	MASK2_REG;         // offset = 0x44 : Access "RW"
  reg [C_S_AXI_DATA_WIDTH-1:0]	MASK3_REG;         // offset = 0x48 : Access "RW"


  wire slv_reg_rden;
  wire slv_reg_wren;
  reg [C_S_AXI_DATA_WIDTH-1:0] reg_data_out;
  integer byte_index;
  reg aw_en;


  // I/O Connections assignments

  assign S_AXI_AWREADY = axi_awready;
  assign S_AXI_WREADY = axi_wready;
  assign S_AXI_BRESP = axi_bresp;
  assign S_AXI_BVALID = axi_bvalid;
  assign S_AXI_ARREADY = axi_arready;
  assign S_AXI_RDATA = axi_rdata;
  assign S_AXI_RRESP = axi_rresp;
  assign S_AXI_RVALID = axi_rvalid;

  assign TMTR_OUT = TMTR_REG;

  assign OCCR_OUT = OCCR_REG;

  assign TSSR0_OUT = TSSR0_REG;
  assign TSSR1_OUT = TSSR1_REG;
  assign TSSR2_OUT = TSSR2_REG;
  assign TSSR3_OUT = TSSR3_REG;

  assign TCUR0_OUT = TCUR0_REG;
  assign TCUR1_OUT = TCUR1_REG;
  assign TCUR2_OUT = TCUR2_REG;
  assign TCUR3_OUT = TCUR3_REG;

  assign TDCR0_OUT = TDCR0_REG;
  assign TDCR1_OUT = TDCR1_REG;
  assign TDCR2_OUT = TDCR2_REG;
  assign TDCR3_OUT = TDCR3_REG;


  assign MASK0_OUT = MASK0_REG;
  assign MASK1_OUT = MASK1_REG;
  assign MASK2_OUT = MASK2_REG;
  assign MASK3_OUT = MASK3_REG;

  assign reset_fifo_wr_pntr = axi_bvalid;
  assign intrn_rst_force = OCCR_REG[1];

  initial
  begin
    UIDP0_REG       = MEM_DEPTH;
    UIDP1_REG       = NO_OF_PROBES;
    IP_TYPE_REG     = IP_TYPE;
    IP_VERSION_REG  = IP_VERSION;
    IP_ID_REG       = IP_ID;
  end

  // Implement axi_awready generation
  // axi_awready is asserted for one S_AXI_ACLK clock cycle when both
  // S_AXI_AWVALID and S_AXI_WVALID are asserted. axi_awready is
  // de-asserted when reset is low.

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
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

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
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

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin
      axi_wready <= 1'b0;
    end
    else
    begin
      if (~axi_wready && S_AXI_WVALID && S_AXI_AWVALID && aw_en)
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


  assign slv_reg_wren = axi_wready && S_AXI_WVALID && axi_awready && S_AXI_AWVALID;
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin
      OCSR_REG <= 0;
    end
    else
    begin
      if(reset_fifo_wr_pntr || mem_empty )
        OCSR_REG <= {3'd0,5'd3,23'd0,1'b0};
      else
        OCSR_REG <= {3'd0,5'd3,23'd0,data_avaible_inmem};
    end
  end

  // Implement memory mapped register select and write logic generation
  // The write data is accepted and written to memory mapped registers when
  // axi_awready, S_AXI_WVALID, axi_wready and S_AXI_WVALID are asserted. Write strobes are used to
  // select byte enables of slave registers while writing.
  // These registers are cleared when reset (active low) is applied.
  // Slave register write enable is asserted when valid address and data are available
  // and the slave is ready to accept the write address and write data.

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin

      TMTR_REG  <= 0;
      OCCR_REG  <= 0;

      TSSR0_REG <= 0;
      TSSR1_REG <= 0;
      TSSR2_REG <= 0;
      TSSR3_REG <= 0;

      TCUR0_REG <= 0;
      TCUR1_REG <= 0;
      TCUR2_REG <= 0;
      TCUR3_REG <= 0;

      TDCR0_REG <= 0;
      TDCR1_REG <= 0;
      TDCR2_REG <= 0;
      TDCR3_REG <= 0;

      MASK0_REG <= 32'hFFFFFFFF;
      MASK1_REG <= 32'hFFFFFFFF;
      MASK2_REG <= 32'hFFFFFFFF;
      MASK3_REG <= 32'hFFFFFFFF;


    end
    else
    begin
      if (slv_reg_wren)
      begin
        case (axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB])

          TMTR_REG_ADDR:
            for (byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1;byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TMTR_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          OCCR_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                OCCR_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TSSR0_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TSSR0_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TCUR0_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TCUR0_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TDCR0_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TDCR0_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end


          MASK0_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                MASK0_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TSSR1_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TSSR1_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TCUR1_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TCUR1_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TDCR1_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TDCR1_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          MASK1_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                MASK1_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TSSR2_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TSSR2_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TCUR2_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TCUR2_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TDCR2_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TDCR2_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          MASK2_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                MASK2_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TSSR3_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TSSR3_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TCUR3_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TCUR3_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          TDCR3_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                TDCR3_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          MASK3_REG_ADDR:
            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
              if ( S_AXI_WSTRB[byte_index] == 1 )
              begin
                MASK3_REG[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end

          default:
          begin
            TMTR_REG  <= TMTR_REG;
            OCCR_REG  <= OCCR_REG;

            TSSR0_REG <= TSSR0_REG;
            TSSR1_REG <= TSSR1_REG;
            TSSR2_REG <= TSSR2_REG;
            TSSR3_REG <= TSSR3_REG;

            TCUR0_REG <= TCUR0_REG;
            TCUR1_REG <= TCUR1_REG;
            TCUR2_REG <= TCUR2_REG;
            TCUR3_REG <= TCUR3_REG;

            TDCR0_REG <= TDCR0_REG;
            TDCR1_REG <= TDCR1_REG;
            TDCR2_REG <= TDCR2_REG;
            TDCR3_REG <= TDCR3_REG;

            MASK0_REG <= MASK0_REG;
            MASK1_REG <= MASK1_REG;
            MASK2_REG <= MASK2_REG;
            MASK3_REG <= MASK3_REG;

          end
        endcase
      end
      else
      begin
        OCCR_REG[0] <=  !OCSR_REG[0]? OCCR_REG[0]:1'b0;
        OCCR_REG[1] <=  !OCSR_REG[1]? OCCR_REG[1]:1'b0;

      end
      //////////////////////
      // ADD LOGIC HERE
      //////////////////////
    end
  end

  // Implement write response logic generation
  // The write response and response valid signals are asserted by the slave
  // when axi_wready, S_AXI_WVALID, axi_wready and S_AXI_WVALID are asserted.
  // This marks the acceptance of address and indicates the status of
  // write transaction.

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin
      axi_bvalid <= 0;
      axi_bresp  <= 2'b0;
    end
    else
    begin
      if (axi_awready && S_AXI_AWVALID && ~axi_bvalid && axi_wready && S_AXI_WVALID)
      begin
        // indicates a valid write response is available
        axi_bvalid <= 1'b1;
        axi_bresp  <= 2'b0;  // 'OKAY' response
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

  reg read_trace_mem_en_ff;
  assign read_trace_mem_en = (S_AXI_ARADDR[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] == TBDR_ADDR) && S_AXI_ARVALID;
  always  @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin
      read_trace_mem_en_ff <= 0;
    end
    else
    begin
      if(~read_trace_mem_en_ff && ~mem_valid_data)
        read_trace_mem_en_ff = read_trace_mem_en ;
      else if (axi_rvalid)
        read_trace_mem_en_ff = 1'b0;
    end
  end

  // Implement axi_arready generation
  // axi_arready is asserted for one S_AXI_ACLK clock cycle when
  // S_AXI_ARVALID is asserted. axi_awready is
  // de-asserted when reset (active low) is asserted.
  // The read address is also latched when S_AXI_ARVALID is
  // asserted. axi_araddr is reset to zero on reset assertion.


  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin
      axi_arready <= 1'b0;
      axi_araddr  <= 32'b0;
    end
    else
    begin
      // if (~axi_arready && S_AXI_ARVALID && ((read_trace_mem_en) ? mem_valid_data || mem_empty: 1)) begin
      if ((~axi_arready && S_AXI_ARVALID) || read_trace_mem_en_ff)
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
  reg mem_empty_ff;
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin
      mem_empty_ff <= 1'b0;
    end
    else
    begin
      mem_empty_ff <= mem_empty;
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
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin
      axi_rvalid <= 0;
      axi_rresp  <= 0;
    end
    else
    begin
      // if (axi_arready && S_AXI_ARVALID && ~axi_rvalid && ((read_trace_mem_en)? mem_valid_data || mem_empty:1)) begin
      if (axi_arready && ~axi_rvalid && ((read_trace_mem_en_ff)? mem_valid_data || mem_empty_ff :1))
      begin
        // Valid read data is available at the read data bus
        axi_rvalid <= 1'b1;
        axi_rresp  <= 2'b0;  // 'OKAY' response
      end
      else if (axi_rvalid && S_AXI_RREADY)
      begin
        // Read data is accepted by the master
        axi_rvalid <= 1'b0;
      end
      else
      begin
        axi_rvalid <= 1'b0;
      end
    end
  end

  // Implement memory mapped register select and read logic generation
  // Slave register read enable is asserted when valid address is available
  // and the slave is ready to accept the read address.
  assign slv_reg_rden = axi_arready & S_AXI_ARVALID & ~axi_rvalid || mem_valid_data;


  always @(*)
  begin
    // Address decoding for reading registers
    case (axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB])

      IP_TYPE_REG_ADDR    :
        reg_data_out = IP_TYPE_REG;
      IP_VERSION_REG_ADDR :
        reg_data_out = IP_VERSION_REG;
      IP_ID_REG_ADDR      :
        reg_data_out = IP_ID_REG;
      UDIP0_ADDR          :
        reg_data_out = UIDP0_REG;
      UDIP1_ADDR          :
        reg_data_out = UIDP1_REG;
      OCSR_REG_ADDR       :
        reg_data_out = OCSR_REG;
      TMTR_REG_ADDR       :
        reg_data_out = TMTR_REG;
      TBDR_ADDR           :
        reg_data_out = TBDR_IN;
      OCCR_REG_ADDR       :
        reg_data_out = OCCR_REG;
      TSSR0_REG_ADDR      :
        reg_data_out = TSSR0_REG;
      TCUR0_REG_ADDR      :
        reg_data_out = TCUR0_REG;
      TDCR0_REG_ADDR      :
        reg_data_out = TDCR0_REG;
      MASK0_REG_ADDR      :
        reg_data_out = MASK0_REG;
      TSSR1_REG_ADDR      :
        reg_data_out = TSSR1_REG;
      TCUR1_REG_ADDR      :
        reg_data_out = TCUR1_REG;
      TDCR1_REG_ADDR      :
        reg_data_out = TDCR1_REG;
      MASK1_REG_ADDR      :
        reg_data_out = MASK1_REG;
      TSSR2_REG_ADDR      :
        reg_data_out = TSSR2_REG;
      TCUR2_REG_ADDR      :
        reg_data_out = TCUR2_REG;
      TDCR2_REG_ADDR      :
        reg_data_out = TDCR2_REG;
      MASK2_REG_ADDR      :
        reg_data_out = MASK2_REG;
      TSSR3_REG_ADDR      :
        reg_data_out = TSSR3_REG;
      TCUR3_REG_ADDR      :
        reg_data_out = TCUR3_REG;
      TDCR3_REG_ADDR      :
        reg_data_out = TDCR3_REG;
      MASK3_REG_ADDR      :
        reg_data_out = MASK3_REG;
      default             :
        reg_data_out = 0;
    endcase
  end


  // Output register or memory read data
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (S_AXI_ARESETN == 1'b0)
    begin
      axi_rdata <= 0;
    end
    else
    begin
      // When there is a valid read address (S_AXI_ARVALID) with
      // acceptance of read address by the slave (axi_arready),
      // output the read dada
      if (slv_reg_rden)
      begin
        axi_rdata <= reg_data_out;  // register read data
      end
    end
  end


endmodule

// *****************************************************************
// OCLA Memory Controller
//
//
// *****************************************************************


module ocla_mem_controller #(
    parameter DATASIZE    = 32,
    parameter ADDRSIZE    = 8,
    parameter NOSAMPLE_WIDTH = 10,
    parameter MEM_DEPTH = 256,
    parameter SYNC_STAGES = 2
  ) (
    output     [DATASIZE-1:0] rd_data,
    output reg                rd_empty,
    output reg                wr_full,
    input                     wr_clk,
    input                     rd_clk,
    input                     wr_rstn,
    input                     rd_rstn,
    input                     wr,
    input      [DATASIZE-1:0] wr_data,
    input                     rd,

    input [NOSAMPLE_WIDTH-1:0] nosamples,  // to move the read pointer to the specified location
    input fixnosamples_en,  // indicates fix number of samples sampling mode is enabled
    input [1:0] trigger_mode,  // decides whether read pointer needs to be moved or not
    input sampling_done_ff  // indicates sampling is done


  );
  wire                wen;
  wire                ren;
  wire [  ADDRSIZE:0] wr_gray_code;
  wire [  ADDRSIZE:0] wr_binary_value;
  wire [  ADDRSIZE:0] rptr_reg;
  // reg                         wr_full;
  reg  [  ADDRSIZE:0] wptr;
  reg  [  ADDRSIZE:0] wr_cnt;
  wire [ADDRSIZE-1:0] waddr;

  wire [  ADDRSIZE:0] rd_gray_code;
  wire [  ADDRSIZE:0] rd_binary_value;
  wire [  ADDRSIZE:0] wptr_reg;
  //reg                         rd_empty;
  reg  [  ADDRSIZE:0] rptr;
  reg  [  ADDRSIZE:0] rd_cnt;
  wire [ADDRSIZE-1:0] rdaddr;

  wire [  ADDRSIZE:0] wptr_bin;

  wire                fifo_full;
  reg                 fifo_full_ff;
  reg                 rd_pntr_mvd;
  wire                fifo_empty;

  wire                rpntr_mv;

  reg                 rd_ff;
  /* write data to memory when wr is high  */
  //assign wen              =   wr && (!wr_full);
  assign wen = rpntr_mv ? wr && (!sampling_done_ff) : wr && (!wr_full);
  assign ren = rd && (!rd_empty);

  /* write counter will increment only when their is a write operation request and fifo is not
    full. Read counter will increment only when their is a request for read operation and fifo is 
    not empty */
  assign wr_binary_value = wr_cnt + wen;
  assign rd_binary_value = rd_cnt + (rd && ~rd_empty);


  /* Binary to Gray code conversion */
  assign wr_gray_code = (wr_binary_value >> 1) ^ wr_binary_value;
  assign rd_gray_code = (rd_binary_value >> 1) ^ rd_binary_value;

  /* Memory address for write/read operation */
  assign waddr = wr_cnt[ADDRSIZE-1:0];
  assign rdaddr = rd_cnt[ADDRSIZE-1:0];

  /* Checking condition for fifo full & empty */
  assign fifo_full = rd_pntr_mvd? 1'b0:(wr_gray_code == {~rptr_reg[ADDRSIZE:ADDRSIZE-1], rptr_reg[ADDRSIZE-2 : 0]});
  assign fifo_empty = fifo_full_ff? 1'b0: (rd_pntr_mvd & !rd_ff) ? 1'b0: (rd_gray_code == wptr_reg);

  always @(posedge wr_clk or negedge wr_rstn)
  begin
    if (!wr_rstn)
    begin
      wptr    <= 0;
      wr_cnt  <= 0;
      wr_full <= 0;
    end
    else
    begin
      wptr    <= wr_gray_code;
      wr_cnt  <= wr_binary_value;
      wr_full <= fifo_full;
    end
  end

  always @(posedge rd_clk or negedge rd_rstn)
  begin
    if (!rd_rstn)
    begin
      rptr    <= 0;
      rd_empty <= 0;
    end
    else
    begin
      rptr <= rd_gray_code;
      rd_empty <= fifo_empty;
    end
  end


  // to indicate trigger mode is post triggered or centered triggered
  assign rpntr_mv = (trigger_mode == 2'b10 || trigger_mode == 2'b11);

  // Read pointer relocation logic
  always @(posedge rd_clk or negedge rd_rstn)
  begin
    if (!rd_rstn)
    begin
      rd_cnt <= 0;
      rd_pntr_mvd <= 0;
    end
    else
    begin
      if (sampling_done_ff & rpntr_mv & !rd_pntr_mvd)
      begin
        case ({
                  fifo_full_ff, fixnosamples_en
                })
          2'b00:
          begin
            rd_cnt <= rd_binary_value;
            rd_pntr_mvd <= 0;
          end
          2'b01:
          begin
            if (trigger_mode == 2'b10)
            begin                                          // data sampling till trigger event occurs
              if (wptr_bin > nosamples)
                rd_cnt <= (wptr_bin - nosamples);
              else
                rd_cnt <= rd_binary_value ;
            end
            else
            begin                                                            // center triggered condition
              if (wptr_bin > 2 * nosamples)
                rd_cnt <= wptr_bin - (2 * nosamples);
              else
                rd_cnt <= rd_binary_value;
            end
            rd_pntr_mvd <= 1;
          end
          2'b10:
          begin
            rd_cnt <= wptr_bin + 1'b1;
            rd_pntr_mvd <= 1;
          end
          2'b11:
          begin
            if (trigger_mode == 2'b10)
            begin
              if (wptr_bin > nosamples)
                rd_cnt <=  (wptr_bin - nosamples) ;
              else
                rd_cnt <=  ((MEM_DEPTH + wptr_bin) - nosamples );
            end
            else
            begin
              if (wptr_bin > 2 * nosamples)
                rd_cnt <= wptr_bin - (2 * nosamples);
              else
                rd_cnt <=  (MEM_DEPTH + wptr_bin) - (2 * nosamples);
            end
            rd_pntr_mvd <= 1;
          end
          default:
          begin
            rd_cnt <= rd_binary_value;
            rd_pntr_mvd <= 0;
          end

        endcase
      end
      else
      begin
        rd_cnt <= rd_binary_value;
        if(!sampling_done_ff)
          rd_pntr_mvd <= 0;
      end
    end
  end


  // Registered fifo full condition
  always @(posedge rd_clk or negedge rd_rstn)
  begin
    if (!rd_rstn)
    begin
      fifo_full_ff <= 0;
    end
    else
    begin
      if (fifo_full & ~fifo_full_ff)
      begin
        fifo_full_ff <= 1'b1;
      end
      else if (rd_pntr_mvd)
      begin
        fifo_full_ff <= 1'b0;
      end

    end
  end

  // Read operation started
  always @(posedge rd_clk or negedge rd_rstn)
  begin
    if (!rd_rstn)
    begin
      rd_ff <= 0;
    end
    else
    begin
      if (rd_pntr_mvd & !rd_ff & rd)
      begin
        rd_ff <= rd;
      end
      // end else if (fifo_empty) begin
      //   rd_ff <= 1'b0;
      // end

    end
  end

  dual_port_ram #(
                  .DATASIZE(DATASIZE),
                  .ADDRSIZE(ADDRSIZE),
                  .DEPTH(MEM_DEPTH)
                ) dual_port_ram (
                  .rdata (rd_data),
                  .wr_clk(wr_clk),
                  .rd_clk(rd_clk),
                  .wen   (wen),
                  .ren   (ren),
                  .wdata (wr_data),
                  .waddr (waddr),
                  .raddr (rdaddr)
                );

  synchronizer #(
                 .SYNC_STAGES(SYNC_STAGES),
                 .ADDRSIZE   (ADDRSIZE)
               ) synchronizer (
                 .wptr_reg(wptr_reg),
                 .rptr_reg(rptr_reg),
                 .wr_clk  (wr_clk),
                 .rd_clk  (rd_clk),
                 .wr_rstn (wr_rstn),
                 .rd_rstn (rd_rstn),
                 .wptr    (wptr),
                 .rptr    (rptr)

               );

  gray2binary #(
                .DATA_WIDTH(ADDRSIZE)
              ) gray2binary_inst (
                .clk(rd_clk),
                .rstn(rd_rstn),
                //.enable(sampling_done_ff ),
                .gray(wptr_reg),
                .binary(wptr_bin)
              );

endmodule

// *****************************************************************
// OCLA Controller
//
//
// *****************************************************************


module ocla_controller #(
    parameter SAMPLE_CNTER_WIDTH = 2,
    parameter MEM_DPTH_HALF = 2

  ) (

    input logic sample_clk,
    input logic rstn,

    input logic trigger_event,
    input logic [1:0] trigger_mode,
    input logic start_process,
    input logic fixnosamples_en,
    input logic [SAMPLE_CNTER_WIDTH-1:0] noofsamples,

    input logic mem_full,
    input logic mem_empty,

    input logic sample_again,

    output logic sampling_en,
    output logic sampling_done_ff

  );

  logic [SAMPLE_CNTER_WIDTH-1:0] samples_count;

  logic triggered_occured_ff;
  logic trigger_event_ff;
  logic sampling_done;


  // sampling is done and data is availale
  always @(posedge sample_clk or negedge rstn)
  begin
    if (!rstn)
      sampling_done_ff <= 1'b0;
    else
    begin
      if (sampling_done)
        sampling_done_ff <= 1'b1;
      else if (sample_again || mem_empty)
        sampling_done_ff <= 1'b0;
    end
  end


  // handles the trigger modes
  always @(posedge sample_clk or negedge rstn)
  begin
    if (!rstn)
    begin
      sampling_en   <= 1'b0;
      samples_count <= 'b0;
    end
    else
    begin
      if (!start_process || sample_again)
      begin
        sampling_en   <= 1'b0;
        samples_count <= 'b0;
      end
      else
      begin
        case (trigger_mode)
          2'b00:
          begin  // countinous
            if (fixnosamples_en)
            begin
              samples_count <= samples_count + 1'b1;
            end
            sampling_en <= !sampling_done_ff & !sampling_done;

          end

          2'b01:
          begin  // pre trigger
            if ((trigger_event || triggered_occured_ff) & !sampling_done)
            begin
              sampling_en <= !sampling_done_ff & !sampling_done;
              if (fixnosamples_en)
              begin
                samples_count <= samples_count + 1'b1;
              end
              else
              begin
                samples_count <= 'b0;
              end
            end
            else
            begin
              sampling_en <= 1'b0;
            end
          end
          2'b10:
          begin  // post trigger
            if (trigger_event_ff)
            begin
              sampling_en <= 1'b0;
            end
            else
            begin
              sampling_en <= !sampling_done_ff & !sampling_done;
            end
          end
          2'b11:
          begin  // center trigger
            if (trigger_event || triggered_occured_ff)
            begin
              sampling_en   <= !sampling_done_ff & !sampling_done;
              samples_count <= samples_count + 1'b1;
            end
            else
            begin
              sampling_en   <= !sampling_done_ff & !sampling_done;
              samples_count <= 'b0;
            end
          end

          default:
          begin  // default
            sampling_en   <= 1'b0;
            samples_count <= 'b0;
          end

        endcase
      end
    end
  end


  // to generate sampling done signal
  always_comb
  begin
    case (trigger_mode)
      2'b00:
      begin
        sampling_done = (mem_full) || (fixnosamples_en? (samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]):1'b0);
        //if (mem_full || fixnosamples_en?samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]:1'b0 ) begin
        //  sampling_done = 1'b1;
        //end else begin
        //  sampling_done = 1'b0;
        //end
      end
      2'b01:
      begin
        if (mem_full || fixnosamples_en?samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]:1'b0)
          sampling_done = 1'b1;
        else
          sampling_done = 1'b0;
      end
      2'b10:
      begin
        if (trigger_event_ff)
          sampling_done = 1'b1;
        else
        begin
          sampling_done = 1'b0;
        end
      end
      2'b11:
      begin
        if (fixnosamples_en)
        begin
          if (samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0])
            sampling_done = 1'b1;
          else
            sampling_done = 1'b0;
        end
        else
        begin
          if (samples_count == MEM_DPTH_HALF)
            sampling_done = 1'b1;
          else
            sampling_done = 1'b0;
        end
      end
      default:
        sampling_done = 1'b0;
    endcase
  end

  always @(posedge sample_clk or negedge rstn)
  begin
    if (!rstn)
      trigger_event_ff <= 1'b0;
    else
      trigger_event_ff <= trigger_event;
  end
  // flopped trigger event pulse
  always @(posedge sample_clk or negedge rstn)
  begin
    if (!rstn)
      triggered_occured_ff <= 1'b0;
    else
    begin
      if (!start_process || sample_again || sampling_done_ff)
        triggered_occured_ff <= 1'b0;
      else if (trigger_event & trigger_mode != 2'b10)
        triggered_occured_ff <= 1'b1;
    end
  end

endmodule

// *****************************************************************
// Dual Port Ram
//
//
// *****************************************************************

module dual_port_ram #(
    parameter DATASIZE = 32,
    parameter ADDRSIZE = 8,
    parameter DEPTH = 256
  )
  (
    output reg [DATASIZE-1:0]  rdata,
    input                  wr_clk,
    input                  rd_clk,
    input                  wen,
    input                  ren,
    input  [DATASIZE-1:0]  wdata,
    input  [ADDRSIZE-1:0]  waddr,
    input  [ADDRSIZE-1:0]  raddr
  );
  reg [DATASIZE-1:0] mem [0:DEPTH-1];

  always @(posedge rd_clk)
  begin
    if (ren)
    begin
      rdata   <= mem[raddr];
    end
  end

  always @(posedge wr_clk)
  begin
    if (wen)
    begin
      mem[waddr]  <=  wdata;
    end
  end



endmodule


// *****************************************************************
// Gray to Binary Convertor
//
//
// *****************************************************************
module gray2binary #(
    parameter DATA_WIDTH = 4
  ) (
    input wire clk,
    input wire rstn,
    input  wire [DATA_WIDTH:0] gray,
    // input wire enable,
    output reg [DATA_WIDTH:0] binary
  );
  wire [DATA_WIDTH-1:0] binary_in;
  genvar i;
  generate
    for (i = 0; i < DATA_WIDTH; i = i + 1)
    begin
      //assign binary_in[i] = enable ? ^gray[DATA_WIDTH-1:i] : 'b0;
      assign binary_in[i] = ^(gray >> i);

    end
  endgenerate

  always @(posedge clk or negedge rstn  )
  begin
    if(!rstn)
    begin
      binary <= 'b0;
    end
    else
    begin
      // if (enable)
      binary <= {1'b0,binary_in};
      // else
      //   binary <= binary;
    end
  end

endmodule



// *****************************************************************
// Sampler Buffer
//
//
// *****************************************************************
module sampler_buffer #(
    parameter PROBE_DATA_WIDTH = 32,
    parameter BUFFERS =  4
  )(
    input logic sample_clk,
    input logic rstn,
    input logic [PROBE_DATA_WIDTH-1:0] probes,
    input logic sampling_en,
    output logic data_wen,
    output logic [PROBE_DATA_WIDTH-1:0] data_accumulate

  );

  logic [PROBE_DATA_WIDTH-1:0] sync_register[0:BUFFERS-1];


  assign data_accumulate = sync_register[BUFFERS-1];
  //assign data_wen = sync_register[`BUFFER_STAGES-1][NO_OF_PROBES];
  assign data_wen = sampling_en;
  // first buffer register
  always @(posedge sample_clk or negedge rstn)
  begin
    if (!rstn)
    begin
      sync_register[0] <= 'b0;
    end
    else
    begin
      //  sync_register[0] <= {sampling_en, probes};
      sync_register[0] <= probes;
    end

  end

  // buffer registers stages
  genvar b;
  generate
    for (b = 0; b < (BUFFERS - 1); b = b + 1)
    begin
      always @(posedge sample_clk or negedge rstn)
      begin
        if (!rstn)
        begin
          sync_register[b+1] <= 0;
        end
        else
        begin
          sync_register[b+1] <= sync_register[b];
        end
      end
    end
  endgenerate

endmodule


// *****************************************************************
// Stream Out Buffer
//
//
// *****************************************************************

module stream_out_buffer #(
    parameter NUM_OFPROBES =2,
    parameter WORD_CHUNK_COUNTER_WIDTH =2,
    parameter NUM_OF_WORD_CHUNKS =2,
    parameter PROBE_BITS =2,
    parameter AXI_DATA_WIDTH = 32

  ) (
    input logic S_AXI_ACLK,
    input logic S_AXI_ARESETN,
    input logic [NUM_OFPROBES-1:0] read_accumulated_data,
    input logic mem_empty,
    input logic read_data_en,
    input logic read_ready,
    output logic mem_read,
    output logic read_valid,

    output logic [AXI_DATA_WIDTH-1:0] read_data

  );
  localparam mem_access = 1'b0;  // mem access state
  localparam data_out = 1'b1;    // data out state
  localparam PROBES_WORDS_WIDTH = NUM_OFPROBES <= 32 ? AXI_DATA_WIDTH :  NUM_OF_WORD_CHUNKS * AXI_DATA_WIDTH;

  reg                            fetch_data;  // fetch data from mem
  reg                            state;       // state variable
  reg [WORD_CHUNK_COUNTER_WIDTH:0] word_count;  //  word chunk counter


  reg [       PROBES_WORDS_WIDTH-1:0] mem_accumulated_data_reg;  // mem data hold registor
  reg                            mem_read_ff;

  // simple state machine to handle data fetch from memory and send word chunks to the axi slave interface
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
    if (!S_AXI_ARESETN)
    begin
      state <= mem_access;
      mem_read <= 1'b0;
      mem_read_ff <= 1'b0;
    end
    else
    begin
      mem_read_ff <= mem_read;
      case (state)
        mem_access:
        begin
          if (read_data_en && !mem_empty)
          begin
            if (mem_read)
              state <= data_out;
            mem_read <= ~mem_read;
          end
          else
          begin
            state <= mem_access;
            mem_read <= 1'b0;
          end
        end
        data_out:
        begin
          if (!read_data_en & fetch_data)
          begin
            state <= mem_access;
          end
          else
          begin
            state <= data_out;
          end
          mem_read <= 1'b0;

        end
        default:
        begin  // Fault Recovery
          state <= mem_access;
        end
      endcase
    end

  // this part handles word chunks transfer to the axi slave interface for read transactions
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (!S_AXI_ARESETN)
    begin
      read_data  <= 'b0;
      word_count <= 'b0;
      read_valid <= 'b0;
      fetch_data <= 'b0;
    end
    else
    begin
      if (state == data_out)
      begin
        if (word_count == 'b0 && !fetch_data)
        begin
          read_data  <= read_accumulated_data;
          //$display("PROBE_BITS chunk %d, %d, %d", NUM_OF_WORD_CHUNKS, PROBE_BITS,`REM_BITS );
          read_valid <= 'b1;
          if (read_ready)
            word_count <= word_count + 'b1;
          if (word_count >= ((NUM_OF_WORD_CHUNKS) - 1))
            fetch_data <= 'b1;
          else
            fetch_data <= 'b0;
        end
        else if (word_count >= ((NUM_OF_WORD_CHUNKS) - 1) )
        begin
          if (read_data_en && !mem_empty && !read_valid && !fetch_data)
          begin
            read_data  <= mem_accumulated_data_reg[32*word_count+:PROBE_BITS];
            read_valid <= 'b1;
            word_count <= 'b0;
            fetch_data <= 'b1;
            // $display("word chunk %d, %d", NUM_OF_WORD_CHUNKS, word_count);
          end
          else
          begin
            if (read_ready)
              read_valid <= 'b0;
            fetch_data <= 'b0;
          end
        end
        else
        begin
          if ((read_data_en && !mem_empty && !read_valid ))
          begin
            word_count <= word_count + 'b1;
            read_data  <= mem_accumulated_data_reg[32*word_count+:AXI_DATA_WIDTH];
            read_valid <= 'b1;
            fetch_data <= 'b0;
          end
          else
          begin
            if (read_ready)
              read_valid <= 'b0;
          end
        end
      end
      else
      begin
        word_count <= 'b0;
        if (read_ready )
          read_data <= 'b0;
        read_valid <= 'b0;
        fetch_data <= 'b0;
      end
    end
  end

  // memory fetched data hold register
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
  begin
    if (!S_AXI_ARESETN)
    begin
      mem_accumulated_data_reg <= 'b0;
    end
    else
    begin
      if (mem_read_ff)
        mem_accumulated_data_reg <= read_accumulated_data;
      // mem_accumulated_data_reg <= 'hAAAAAA32BBBBBB31ABCDEF39ABCDEF38ABCDEF37ABCDEF36ABCDEF35ABCDEF34ABCDEF33ABCDEF32ABCDEF31ABCDEF30ABCDEF29ABCDEF28ABCDEF27ABCDEF26ABCDEF25ABCDEF24ABCDEF23ABCDEF22ABCDEF22ABCDEF20ABCDEF19ABCDEF18ABCDEF17ABCDEF16ABCDEF15ABCDEF14ABCDEF13ABCDEF12ABCDEF11ABCDEF10;
    end
  end

endmodule

// *****************************************************************
// Stream Out Buffer
//
//
// *****************************************************************

module synchronizer #(
    parameter SYNC_STAGES   = 2,
    parameter ADDRSIZE      = 4
  )
  (
    output  [ADDRSIZE:0]    wptr_reg,
    output  [ADDRSIZE:0]    rptr_reg,
    input                   wr_clk,
    input                   rd_clk,
    input                   wr_rstn,
    input                   rd_rstn,
    input   [ADDRSIZE:0]    wptr,
    input   [ADDRSIZE:0]    rptr

  );

  reg [ADDRSIZE:0] wr_sync_register[0:SYNC_STAGES-1];
  reg [ADDRSIZE:0] rd_sync_register[0:SYNC_STAGES-1];


  assign wptr_reg = wr_sync_register[SYNC_STAGES-1];
  assign rptr_reg = rd_sync_register[SYNC_STAGES-1];

  always @(posedge rd_clk or negedge rd_rstn)
  begin
    if (!rd_rstn)
    begin
      wr_sync_register[0] <= 0;
    end
    else
    begin
      wr_sync_register[0] <= wptr;
    end
  end

  always @(posedge wr_clk or negedge wr_rstn)
  begin
    if (!wr_rstn)
    begin
      rd_sync_register[0] <= 0;
    end
    else
    begin
      rd_sync_register[0] <= rptr;
    end

  end

  genvar i;

  generate
    for(i=0; i<(SYNC_STAGES-1); i = i+1)
    begin
      always@(posedge rd_clk or negedge rd_rstn)
      begin
        if(!rd_rstn)
        begin
          wr_sync_register[i+1] <= 0;

        end
        else
        begin
          wr_sync_register[i+1] <= wr_sync_register[i];
        end
      end
      always @(posedge wr_clk or negedge wr_rstn)
      begin
        if (!wr_rstn)
        begin
          rd_sync_register[i+1] <= 0;
        end
        else
        begin
          rd_sync_register[i+1] <= rd_sync_register[i];
        end
      end
    end
  endgenerate
endmodule
