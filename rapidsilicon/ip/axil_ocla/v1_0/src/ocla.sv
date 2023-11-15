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
// `define NUM_OF_PROBES  32
// `define MEMORY_DEPTH  256
// `define NUM_OF_TRIGGER_INPUTS  1
// `define PROBE_WIDHT_BITS 1
// `define TRIGGER_INPUTS 
//`define TRIGGER_INPUTS                                // to enable
//`define NUM_OF_TRIGGER_INPUTS 1                       // Number of trigger inputs

module ocla #(
    parameter IP_TYPE = "ocla",
    parameter IP_VERSION = 32'h1, 
    parameter IP_ID = 32'h3881734,
    parameter NO_OF_PROBES = 32,
    parameter NO_OF_TRIGGER_INPUTS = 0,
    parameter PROBE_WIDHT = 32,
    parameter MEM_DEPTH = 1024,
    parameter AXI_DATA_WIDTH = 32,
    parameter AXI_ADDR_WIDTH = 32

) (
    input logic sample_clk,
    input logic rstn,

    input logic [NO_OF_TRIGGER_INPUTS-1:0] trigger_input,

    input logic S_AXI_ACLK,
    input logic S_AXI_ARESETN,

    input wire [AXI_ADDR_WIDTH-1 : 0] S_AXI_AWADDR,
    input wire [2 : 0] S_AXI_AWPROT,
    input wire S_AXI_AWVALID,
    output wire S_AXI_AWREADY,

    input wire [AXI_DATA_WIDTH-1 : 0] S_AXI_WDATA,
    input wire [(AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
    input wire S_AXI_WVALID,
    output wire S_AXI_WREADY,

    output wire [1 : 0] S_AXI_BRESP,
    output wire S_AXI_BVALID,
    input wire S_AXI_BREADY,

    input wire [AXI_ADDR_WIDTH-1 : 0] S_AXI_ARADDR,
    input wire [2 : 0] S_AXI_ARPROT,
    input wire S_AXI_ARVALID,
    output wire S_AXI_ARREADY,

    output wire [AXI_DATA_WIDTH-1 : 0] S_AXI_RDATA,
    output wire [1 : 0] S_AXI_RRESP,
    output wire S_AXI_RVALID,
    input wire S_AXI_RREADY,
    input logic [NO_OF_PROBES-1:0] probes
);



  // ---------------------------------------------------------------
  // Stream Out Buffer 
  // ---------------------------------------------------------------

  localparam REM_BITS = NO_OF_PROBES < 32 ? 32 - NO_OF_PROBES : ((NO_OF_PROBES - ($floor(NO_OF_PROBES / 32) * 32))== 0 )? 0 : 32 -  (NO_OF_PROBES - ($floor(NO_OF_PROBES / 32) * 32)); 
  																												// in case number of probe is not a multiple of 32
  localparam WORD_CHUNKS = NO_OF_PROBES > 32 ? (NO_OF_PROBES / 32) +((NO_OF_PROBES - $floor(NO_OF_PROBES / 32) * 32 )== 0 ? 0:1):1;  
  																												// number of 32 bit words in which probes can be divided
  localparam PROBE_BITS = 32 - int'(REM_BITS);
  localparam WORD_CHUNK_CNTR_WIDTH = WORD_CHUNKS> 1? int'($clog2(WORD_CHUNKS)):1; 

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

  localparam TRIGGER_SIGNAL_SELECT_RANGE = 32;
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

  logic [AXI_DATA_WIDTH-1:0] tcur1_port;

  logic [AXI_DATA_WIDTH-1:0] tcur_port;
  logic [AXI_DATA_WIDTH-1:0] tdcr_port;
  logic [AXI_DATA_WIDTH-1:0] tbdr_port;
  logic [13:0] tmtr_port;
  logic read_trace_mem_en;

  logic mem_empty_sync;
  logic mem_valid_data;
  logic reset_fifo_pntr;
  logic reset_fifo_wr_pntr_sync;
  logic start_process;
  logic tmtr_port_strt_bit_sync;

  logic sampling_done_ff;
  logic done_sampling_ff_sync;

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
  // for tmtr register data from axi clock domain                   //
  // to sampling clock domain                                       //
  // ---------------------------------------------------------------//

  ddff_sync #(
      .REG_WIDTH(1)
  ) tmtr_bits_sync (
      .clk(sample_clk),
      .rstn(rstn),
      .D(tmtr_port[2]),
      .Q(tmtr_port_strt_bit_sync)
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
      .rstn(rstn),
      .trigger_event(trigger_event),
      .trigger_mode(tmtr_port[1:0]),
      .mem_full(wr_full),
      .start_process(tmtr_port_strt_bit_sync),
      .fixnosamples_en(tmtr_port[3]),
      //.noofsamples({'b0,tmtr_port[4+:(SAMPLE_COUNTER_WIDTH>10?10:SAMPLE_COUNTER_WIDTH)]}),
      .noofsamples({1'b0,tmtr_port[4+:(SAMPLE_COUNTER_WIDTH>10?10:SAMPLE_COUNTER_WIDTH)]}),
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
  trigger_control_unit #(
      .NPROBES(NO_OF_PROBES),
      .PROBE_WIDHT(PROBE_WIDHT),
      .TRIGGER_INPUTS(NO_OF_TRIGGER_INPUTS),
      .SELECT_MUX_WIDTH(SELECT_MUX_WIDTH),
      .TRIGGER_SIGNAL_SELECT_RANGE(TRIGGER_SIGNAL_SELECT_RANGE)
  ) trig_control_unit_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .in_signals({trigger_input[NO_OF_TRIGGER_INPUTS-1:0],probes}),
      //.in_signals(probes),
      .config_bits({tcur1_port,tcur_port}),
      .reg_value(tdcr_port[PROBE_WIDHT-1:0]),
      .start_cap(tmtr_port[2]),
      .trigger_event(trigger_event)
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
      .trigger_mode(tmtr_port[1:0]),
      .rd(mem_read),
      .nosamples(tmtr_port[4+:SAMPLE_COUNTER_WIDTH]),
      .fixnosamples_en(tmtr_port[3]),
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
      .read_data(tbdr_port)
  );


  // ---------------------------------------------------------------//
  // Axi Lite Slave instance                                        //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//

  axi_slv_lite #(
      .IP_TYPE(IP_TYPE),
      .IP_VERSION(IP_VERSION),
      .IP_ID(IP_ID),
      .NO_OF_PROBES(NO_OF_PROBES),
      .MEM_DEPTH(MEM_DEPTH),
      .C_S_AXI_DATA_WIDTH(AXI_DATA_WIDTH),
      .C_S_AXI_ADDR_WIDTH(AXI_ADDR_WIDTH)
  ) axi_slv_lite_inst (
      .tbdr_port(tbdr_port),
      .read_trace_mem_en(read_trace_mem_en),
      .tcur1_port(tcur1_port),
      .tcur_port(tcur_port),
      .tdcr_port(tdcr_port),
      .tmtr_port(tmtr_port),
      .data_avaible_inmem(done_sampling_ff_sync),

      .mem_valid_data(mem_valid_data),
      .reset_fifo_wr_pntr(reset_fifo_pntr),
      .mem_empty(mem_empty),
      .S_AXI_ACLK(S_AXI_ACLK),
      .S_AXI_ARESETN(S_AXI_ARESETN),
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

      .S_AXI_RDATA (S_AXI_RDATA),
      .S_AXI_RRESP (S_AXI_RRESP),
      .S_AXI_RVALID(S_AXI_RVALID),
      .S_AXI_RREADY(S_AXI_RREADY)
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

  always @(posedge clk or negedge rstn) begin
    if (!rstn) begin
      sync[0] <= 0;
    end else begin
      sync[0] <= D;
    end
  end

  genvar a;

  generate
    for (a = 0; a < (stages - 1); a = a + 1) begin
      always @(posedge clk or negedge rstn) begin
        if (!rstn) begin
          sync[a+1] <= 0;
        end else begin
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
  parameter PROBE_WIDHT = 32,
  parameter TRIGGER_INPUTS = 32,
  parameter SELECT_MUX_WIDTH = 10,
  parameter TRIGGER_SIGNAL_SELECT_RANGE = 32 ) (
    input logic sample_clk,
    input logic rstn,

    input logic [(TRIGGER_INPUTS + NPROBES)-1:0] in_signals,
    //input logic [(NPROBES)-1:0] in_signals,
    input logic [63:0] config_bits, // config bits from both tcur registers.

    input logic [PROBE_WIDHT-1:0] reg_value,
    input logic start_cap,
    output logic trigger_event

);

  logic out_trig1;

  logic in_sig1;

  logic [PROBE_WIDHT-1:0] compare_value1;
  logic [31:0] config_bits_ff;
  logic [31:0] config_tcur1_bits_ff;
  logic [TRIGGER_SIGNAL_SELECT_RANGE-1:0] trigger_select;
  assign trigger_select = in_signals[TRIGGER_SIGNAL_SELECT_RANGE-1:0];

  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      config_bits_ff <= 'b0;
      config_tcur1_bits_ff <= 'b0;
    end else begin
      config_bits_ff <= config_bits[31:0];
      config_tcur1_bits_ff <= config_bits[63:32];
    end
  end

  //assign compare_value1 = in_signals[config_bits_ff[17+:`SELECT_MUX_WIDTH]+:`WIDTH];
  //assign in_sig1 = in_signals[config_bits_ff[17+:`SELECT_MUX_WIDTH]];

  assign compare_value1 = trigger_select[config_bits_ff[17+:SELECT_MUX_WIDTH]+:PROBE_WIDHT];
  assign in_sig1 = trigger_select[config_bits_ff[17+:SELECT_MUX_WIDTH]];

  trigger_unit #(.PROBE_WIDHT(PROBE_WIDHT)) trig_unit_a_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .in_sig(in_sig1),
      .config_bits(config_bits_ff[7:1]),
      .reg_value(reg_value),
      .compare_value(compare_value1),
      .start_cap(start_cap),
      .trigger_event(out_trig1)
  );


  logic out_trig2;
  logic in_sig2;
  logic out_trig_bool;

  logic [PROBE_WIDHT-1:0] compare_value2;
  //  assign in_sig2 = in_signals[config_bits_ff[24+:`SELECT_MUX_WIDTH]];
  //  assign compare_value2 = in_signals[config_bits_ff[24+:`SELECT_MUX_WIDTH]+:`WIDTH];
  assign in_sig2 = trigger_select[config_bits_ff[24+:SELECT_MUX_WIDTH]];
  assign compare_value2 = trigger_select[config_bits_ff[24+:SELECT_MUX_WIDTH]+:PROBE_WIDHT];

  trigger_unit #(.PROBE_WIDHT(PROBE_WIDHT))
  trig_unit_b_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .in_sig(in_sig2),
      .config_bits(config_bits_ff[14:8]),
      .reg_value(reg_value),
      .compare_value(compare_value2),
      .start_cap(start_cap),
      .trigger_event(out_trig2)
  );
  
  
  /**********************************************/
  logic in_sig3,in_sig4;
  logic out_trig3,out_trig4;
  logic [PROBE_WIDHT-1:0] compare_value3;
  logic [PROBE_WIDHT-1:0] compare_value4;

  
  assign compare_value3 = trigger_select[config_tcur1_bits_ff[17+:SELECT_MUX_WIDTH]+:PROBE_WIDHT];
  assign in_sig3 = trigger_select[config_tcur1_bits_ff[17+:SELECT_MUX_WIDTH]];
  
  assign compare_value4 = trigger_select[config_tcur1_bits_ff[24+:SELECT_MUX_WIDTH]+:PROBE_WIDHT];
  assign in_sig4 = trigger_select[config_tcur1_bits_ff[24+:SELECT_MUX_WIDTH]];

  
   trigger_unit #(.PROBE_WIDHT(PROBE_WIDHT))
  trig_unit_c_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .in_sig(in_sig3),
      .config_bits(config_tcur1_bits_ff[7:1]),
      .reg_value(reg_value),
      .compare_value(compare_value3),
      .start_cap(start_cap),
      .trigger_event(out_trig3)
  );
  
  
   trigger_unit #(.PROBE_WIDHT(PROBE_WIDHT))
  trig_unit_d_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .in_sig(in_sig4),
      .config_bits(config_tcur1_bits_ff[14:8]),
      .reg_value(reg_value),
      .compare_value(compare_value4),
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
      .config_bits({config_bits_ff[16:15],config_tcur1_bits_ff[16:15]}),
      .trigger_event(out_trig_bool)
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
    input logic [3:0] config_bits,
    output logic trigger_event
);

  logic in_sig_ff;
  logic out_sig;

  assign trigger_event = out_sig;

  //always_comb begin
  always @(*) begin
    case (config_bits)
      4'b0000:   out_sig = in_sig1 || in_sig2 || in_sig3 || in_sig4;  // Global OR
      4'b0101:   out_sig = (in_sig1 & in_sig2 & in_sig3 & in_sig4) || (in_sig1 & in_sig2) || (in_sig1 & in_sig3) || (in_sig1 & in_sig4) || (in_sig2 & in_sig3) || (in_sig2 & in_sig4) || (in_sig3 & in_sig4);     // Global AND
      4'b1010:   out_sig = in_sig1 || in_sig2 || in_sig3 || in_sig4;  // Global OR
      4'b1111:   out_sig = in_sig1 ^ in_sig2 ^ in_sig3 ^ in_sig4;     // Global XOR
      default: out_sig = 1'b0;  // default
    endcase
  end

endmodule

// *****************************************************************
// Trigger Unit
//
//
// *****************************************************************
module trigger_unit #(parameter PROBE_WIDHT = 4 ) (

    input logic sample_clk,
    input logic rstn,
    input logic in_sig,
    input logic [6:0] config_bits,
    input logic [PROBE_WIDHT-1:0] reg_value,
    input logic [PROBE_WIDHT-1:0] compare_value,
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
 always @(*) begin
    case (config_bits[1:0])
      2'b00:   out_sig = 1'b0;  // no trigger
      2'b01:   out_sig = trigger_event_ed;  //  edge detect
      2'b10:   out_sig = trigger_event_lvl;  // level detect
      2'b11:   out_sig = trigger_event_vc;  // value compare
      default: out_sig = 1'b0;  // default
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
      .config_bits(config_bits[4]),
      .start_cap(start_cap),
      .lvl_trigger_event(trigger_event_lvl)
  );
  value_compare #(.PROBE_WIDHT(PROBE_WIDHT))
  vc (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .en(config_bits[1:0] == 2'b11),
      .in_sig(compare_value),
      .reg_value(reg_value),
      .config_bits(config_bits[6:5]),
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

  always_comb begin
    if (en) begin
      case (config_bits)
        2'b00:   out_sig = 1'b0;  // no trigger
        2'b01:   out_sig = in_sig & !(in_sig_ff);  // rising edge detect
        2'b10:   out_sig = !(in_sig) & in_sig_ff;  // falling edge detect
        2'b11:   out_sig = in_sig ^ in_sig_ff;  // either edge detec
        default: out_sig = 1'b0;  // default
      endcase
    end else out_sig = 1'b0;
  end

endmodule


// *****************************************************************
// Value Compare Module
//
//
// *****************************************************************
module value_compare #(parameter PROBE_WIDHT = 4 ) (
    input logic sample_clk,
    input logic rstn,
    input logic en,
    input logic [PROBE_WIDHT-1:0] in_sig,
    input logic [PROBE_WIDHT-1:0] reg_value,
    input logic [1:0] config_bits,
    output logic vc_trigger_event
);

  logic out_sig;

  // dflop dff_out_sig (.sample_clk(sample_clk),.rstn(rstn),.D(out_sig),.Q(vc_trigger_event));

  always_comb begin
    if (en) begin
      case (config_bits)
        2'b00:   out_sig = 1'b0;  // no trigger
        2'b01:   out_sig = reg_value == in_sig;  // equal to detect
        2'b10:   out_sig = in_sig < reg_value;  // less than detect
        2'b11:   out_sig = in_sig > reg_value;  // greater than detect
        default: out_sig = 1'b0;  // default
      endcase
    end else out_sig = 1'b0;

  end

  lvl2pulse level2pulse (
    .sample_clk(sample_clk),
    .rstn(rstn),
    .in_sig (out_sig),
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
    input  logic config_bits,
    input  logic start_cap,
    output logic lvl_trigger_event
);

  logic in_sig_ff;
  logic out_sig;

  //dflop dff_out_sig (.sample_clk(sample_clk),.rstn(rstn),.D(out_sig),.Q(trigger_event));
  always_comb begin
    if (en & start_cap) begin
      case (config_bits)
        1'b0:    out_sig = !in_sig;  // low level
        1'b1:    out_sig = in_sig;  // high level
        default: out_sig = 1'b0;  // default
      endcase
    end 
    else out_sig = 1'b0;
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

  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) Q <= 1'b0;
    else Q <= D;
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

  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      r1 <= 1'b0;
      r2 <= 1'b0;
      r3 <= 1'b0;
      
    end
    else begin
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
    parameter NO_OF_PROBES = 32,
    parameter MEM_DEPTH =32,

    // WIDTH of S_AXI data bus
    parameter integer C_S_AXI_DATA_WIDTH = 32,
    // WIDTH of S_AXI address bus
    parameter integer C_S_AXI_ADDR_WIDTH = 32
) (
    // Users to add ports here
    input wire [C_S_AXI_DATA_WIDTH-1:0] tbdr_port,
    input wire mem_valid_data,
    input wire mem_empty,
    input wire data_avaible_inmem,
    output wire read_trace_mem_en,

    output wire [C_S_AXI_DATA_WIDTH-1:0] tcur1_port,
    output wire [C_S_AXI_DATA_WIDTH-1:0] tcur_port,
    output wire [C_S_AXI_DATA_WIDTH-1:0] tdcr_port,
    output wire [13:0] tmtr_port,

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
    input wire S_AXI_RREADY
);

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
  localparam integer OPT_MEM_ADDR_BITS = 3;
  //----------------------------------------------
  //-- Signals for user logic register space example
  //------------------------------------------------
  //-- Number of Slave Registers 4

  reg [C_S_AXI_DATA_WIDTH-1:0] OCSR;  // 0x00 RO   // OCLA Status Register
  //reg [C_S_AXI_DATA_WIDTH-1:0] TBDR;  // 0x04 RO // Trace Buffer Data Register
  reg [C_S_AXI_DATA_WIDTH-1:0] TCUR;  // 0x08 RW
  reg [C_S_AXI_DATA_WIDTH-1:0] TTCR;  // 0x0C RW
  reg [C_S_AXI_DATA_WIDTH-1:0] TDCR;  // 0x10 RW

  reg [C_S_AXI_DATA_WIDTH-1:0] TCUR1; // 0x14 RW   // Trigger control Unit Register
  
  reg [C_S_AXI_DATA_WIDTH-1:0] IP_TYPE_REG  = IP_TYPE;
  reg [C_S_AXI_DATA_WIDTH-1:0] IP_VERSION_REG = IP_VERSION;
  reg [C_S_AXI_DATA_WIDTH-1:0] IP_ID_REG = IP_ID;
  
  reg [10-1:0] no_probes = NO_OF_PROBES;
  reg [10-1:0] mem_depth = MEM_DEPTH;




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

  assign tcur1_port = TCUR1;
  assign tcur_port = TCUR;
  assign tdcr_port = TDCR;
  assign tmtr_port = TTCR[13:0];

  assign reset_fifo_wr_pntr = axi_bvalid;

  // Implement axi_awready generation
  // axi_awready is asserted for one S_AXI_ACLK clock cycle when both
  // S_AXI_AWVALID and S_AXI_WVALID are asserted. axi_awready is
  // de-asserted when reset is low.

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      axi_awready <= 1'b0;
      aw_en <= 1'b1;
    end else begin
      if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en) begin
        // slave is ready to accept write address when 
        // there is a valid write address and write data
        // on the write address and data bus. This design 
        // expects no outstanding transactions. 
        axi_awready <= 1'b1;
        aw_en <= 1'b0;
      end else if (S_AXI_BREADY && axi_bvalid) begin
        aw_en <= 1'b1;
        axi_awready <= 1'b0;
      end else begin
        axi_awready <= 1'b0;
      end
    end
  end

  // Implement axi_awaddr latching
  // This process is used to latch the address when both 
  // S_AXI_AWVALID and S_AXI_WVALID are valid. 

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      axi_awaddr <= 0;
    end else begin
      if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en) begin
        // Write Address latching 
        axi_awaddr <= S_AXI_AWADDR;
      end
    end
  end

  // Implement axi_wready generation
  // axi_wready is asserted for one S_AXI_ACLK clock cycle when both
  // S_AXI_AWVALID and S_AXI_WVALID are asserted. axi_wready is 
  // de-asserted when reset is low. 

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      axi_wready <= 1'b0;
    end else begin
      if (~axi_wready && S_AXI_WVALID && S_AXI_AWVALID && aw_en) begin
        // slave is ready to accept write data when 
        // there is a valid write address and write data
        // on the write address and data bus. This design 
        // expects no outstanding transactions. 
        axi_wready <= 1'b1;
      end else begin
        axi_wready <= 1'b0;
      end
    end
  end


  assign slv_reg_wren = axi_wready && S_AXI_WVALID && axi_awready && S_AXI_AWVALID;
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      OCSR <= 0;
    end else begin
      if(reset_fifo_wr_pntr || mem_empty )
      OCSR <= {2'b11, 9'b0,mem_depth,no_probes,1'b0};
      else 
       // OCSR <= {2'b11, 29'b0, data_avaible_inmem};
          OCSR <= {2'b11, 9'b0,mem_depth,no_probes ,data_avaible_inmem};
    end
  end

  // Implement memory mapped register select and write logic generation
  // The write data is accepted and written to memory mapped registers when
  // axi_awready, S_AXI_WVALID, axi_wready and S_AXI_WVALID are asserted. Write strobes are used to
  // select byte enables of slave registers while writing.
  // These registers are cleared when reset (active low) is applied.
  // Slave register write enable is asserted when valid address and data are available
  // and the slave is ready to accept the write address and write data.

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      //OCSR <= 0; // OCLA Status Register
      //TBDR <= 0; // Trace Buffer Data Register

      TCUR1 <= 0;  // Trigger Control Unit Register
      TCUR <= 0;  // Trigger Control Unit Register
      TTCR <= 0;  // Trigger Type Configure Register
      TDCR <= 0;  // Trigger Data Compare Register


    end else begin
      if (slv_reg_wren) begin
        case (axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB])
          // 4'h0:
          // for (
          //     byte_index = 0;
          //     byte_index <= (C_S_AXI_DATA_WIDTH / 8) - 1;
          //     byte_index = byte_index + 1
          // )
          //   if (S_AXI_WSTRB[byte_index] == 1) begin
          //     // Respective byte enables are asserted as per write strobes 
          //     // Slave register 0
          //     // OCSR[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
          //   end
          // 4'h1:
          // for (
          //     byte_index = 0;
          //     byte_index <= (C_S_AXI_DATA_WIDTH / 8) - 1;
          //     byte_index = byte_index + 1
          // )
          //   if (S_AXI_WSTRB[byte_index] == 1) begin
          //     // Respective byte enables are asserted as per write strobes 
          //     // Slave register 1
          //     //TBDR[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
          //   end
          4'h2:
          for (
              byte_index = 0;
              byte_index <= (C_S_AXI_DATA_WIDTH / 8) - 1;
              byte_index = byte_index + 1
          )
            if (S_AXI_WSTRB[byte_index] == 1) begin
              // Respective byte enables are asserted as per write strobes 
              // Slave register 2
              TCUR[(byte_index*8)+:8] <= S_AXI_WDATA[(byte_index*8)+:8];
            end
          4'h3:
          for (
              byte_index = 0;
              byte_index <= (C_S_AXI_DATA_WIDTH / 8) - 1;
              byte_index = byte_index + 1
          )
            if (S_AXI_WSTRB[byte_index] == 1) begin
              // Respective byte enables are asserted as per write strobes 
              // Slave register 3
              TTCR[(byte_index*8)+:8] <= S_AXI_WDATA[(byte_index*8)+:8];
            end
          4'h4:
          for (
              byte_index = 0;
              byte_index <= (C_S_AXI_DATA_WIDTH / 8) - 1;
              byte_index = byte_index + 1
          )
            if (S_AXI_WSTRB[byte_index] == 1) begin
              // Respective byte enables are asserted as per write strobes 
              // Slave register 3
              TDCR[(byte_index*8)+:8] <= S_AXI_WDATA[(byte_index*8)+:8];
            end

          3'h5:
          for ( 
              byte_index = 0; 
              byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; 
              byte_index = byte_index+1 
          )
            if ( S_AXI_WSTRB[byte_index] == 1 ) begin
                // Respective byte enables are asserted as per write strobes 
                // Slave register 5
                TCUR1[(byte_index*8) +: 8] <= S_AXI_WDATA[(byte_index*8) +: 8];
              end 



          default: begin
            //OCSR <= OCSR;
            //TBDR <= TBDR;
            TCUR <= TCUR;
            TTCR <= TTCR;
            TCUR1 <= TCUR1;
          end
        endcase
      end
       else begin
         TTCR[2] <=  !OCSR[0]? TTCR[2]:1'b0;
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

  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      axi_bvalid <= 0;
      axi_bresp  <= 2'b0;
    end else begin
      if (axi_awready && S_AXI_AWVALID && ~axi_bvalid && axi_wready && S_AXI_WVALID) begin
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
  assign read_trace_mem_en = (S_AXI_ARADDR[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] == 4'h1) && S_AXI_ARVALID;
  always  @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      read_trace_mem_en_ff <= 0;
  end else begin
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


  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      axi_arready <= 1'b0;
      axi_araddr  <= 32'b0;
    end else begin
    // if (~axi_arready && S_AXI_ARVALID && ((read_trace_mem_en) ? mem_valid_data || mem_empty: 1)) begin
      if ((~axi_arready && S_AXI_ARVALID) || read_trace_mem_en_ff) begin
        // indicates that the slave has acceped the valid read address
        axi_arready <= 1'b1;
        // Read address latching
        axi_araddr  <= S_AXI_ARADDR;
      end else begin
        axi_arready <= 1'b0;
      end
    end
  end
reg mem_empty_ff;
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      mem_empty_ff <= 1'b0;
    end
    else begin
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
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      axi_rvalid <= 0;
      axi_rresp  <= 0;
    end else begin
     // if (axi_arready && S_AXI_ARVALID && ~axi_rvalid && ((read_trace_mem_en)? mem_valid_data || mem_empty:1)) begin
      if (axi_arready && ~axi_rvalid && ((read_trace_mem_en_ff)? mem_valid_data || mem_empty_ff :1)) begin 
      // Valid read data is available at the read data bus
        axi_rvalid <= 1'b1;
        axi_rresp  <= 2'b0;  // 'OKAY' response
      end else if (axi_rvalid && S_AXI_RREADY) begin
        // Read data is accepted by the master
        axi_rvalid <= 1'b0;
      end
      else begin
        axi_rvalid <= 1'b0;
      end
    end
  end

  // Implement memory mapped register select and read logic generation
  // Slave register read enable is asserted when valid address is available
  // and the slave is ready to accept the read address.
  assign slv_reg_rden = axi_arready & S_AXI_ARVALID & ~axi_rvalid || mem_valid_data;


  always @(*) begin
    // Address decoding for reading registers
    case (axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB])
      4'h0: begin
        reg_data_out = OCSR;
      end
      4'h1: begin
        reg_data_out = tbdr_port;
      end
      4'h2: begin
        reg_data_out = TCUR;
      end
      4'h3: begin
        reg_data_out = TTCR;
      end
      4'h4: begin
        reg_data_out = TDCR;
      end
      4'h5: begin
        reg_data_out = TCUR1;
      end   
      4'h6: begin
        reg_data_out = IP_TYPE_REG;
      end
      4'h7: begin
        reg_data_out = IP_VERSION_REG;
      end
      4'h8: begin
        reg_data_out = IP_ID_REG;
      end
      default: begin
        reg_data_out = 0;
      end
    endcase
  end


  // Output register or memory read data
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (S_AXI_ARESETN == 1'b0) begin
      axi_rdata <= 0;
    end else begin
      // When there is a valid read address (S_AXI_ARVALID) with 
      // acceptance of read address by the slave (axi_arready), 
      // output the read dada 
      if (slv_reg_rden) begin
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

  always @(posedge wr_clk or negedge wr_rstn) begin
    if (!wr_rstn) begin
      wptr    <= 0;
      wr_cnt  <= 0;
      wr_full <= 0;
    end else begin
      wptr    <= wr_gray_code;
      wr_cnt  <= wr_binary_value;
      wr_full <= fifo_full;
    end
  end

  always @(posedge rd_clk or negedge rd_rstn) begin
    if (!rd_rstn) begin
      rptr    <= 0;
      rd_empty <= 0;
    end else begin
      rptr <= rd_gray_code;
      rd_empty <= fifo_empty;
    end
  end


  // to indicate trigger mode is post triggered or centered triggered 
  assign rpntr_mv = (trigger_mode == 2'b10 || trigger_mode == 2'b11);

  // Read pointer relocation logic
  always @(posedge rd_clk or negedge rd_rstn) begin
    if (!rd_rstn) begin
      rd_cnt <= 0;
      rd_pntr_mvd <= 0;
    end else begin
      if (sampling_done_ff & rpntr_mv & !rd_pntr_mvd) begin
        case ({
          fifo_full_ff, fixnosamples_en
        })
          2'b00: begin
            rd_cnt <= rd_binary_value;
            rd_pntr_mvd <= 0;
          end
          2'b01: begin 
            if (trigger_mode == 2'b10) begin                                          // data sampling till trigger event occurs 
              if (wptr_bin > nosamples) rd_cnt <= (wptr_bin - nosamples);
              else rd_cnt <= rd_binary_value ;
            end else begin                                                            // center triggered condition
              if (wptr_bin > 2 * nosamples) rd_cnt <= wptr_bin - (2 * nosamples);
              else rd_cnt <= rd_binary_value;
            end
            rd_pntr_mvd <= 1;
          end
          2'b10: begin
            rd_cnt <= wptr_bin + 1'b1;
            rd_pntr_mvd <= 1;
          end
          2'b11: begin
            if (trigger_mode == 2'b10) begin
              if (wptr_bin > nosamples) rd_cnt <=  (wptr_bin - nosamples) ;
              else rd_cnt <=  ((MEM_DEPTH + wptr_bin) - nosamples );
            end else begin                                             
              if (wptr_bin > 2 * nosamples) rd_cnt <= wptr_bin - (2 * nosamples);
              else rd_cnt <=  (MEM_DEPTH + wptr_bin) - (2 * nosamples);
            end
            rd_pntr_mvd <= 1;
          end
          default: begin
            rd_cnt <= rd_binary_value;
            rd_pntr_mvd <= 0;
          end

        endcase
      end else begin
        rd_cnt <= rd_binary_value;
        if(!sampling_done_ff)rd_pntr_mvd <= 0;
      end
    end
  end


  // Registered fifo full condition
  always @(posedge rd_clk or negedge rd_rstn) begin
    if (!rd_rstn) begin
      fifo_full_ff <= 0;
    end else begin
      if (fifo_full & ~fifo_full_ff) begin
        fifo_full_ff <= 1'b1;
      end else if (rd_pntr_mvd) begin
        fifo_full_ff <= 1'b0;
      end

    end
  end

  // Read operation started
  always @(posedge rd_clk or negedge rd_rstn) begin
    if (!rd_rstn) begin
      rd_ff <= 0;
    end else begin
      if (rd_pntr_mvd & !rd_ff & rd) begin
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
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) sampling_done_ff <= 1'b0;
    else begin
      if (sampling_done) sampling_done_ff <= 1'b1;
      else if (sample_again || mem_empty) sampling_done_ff <= 1'b0;
    end
  end


  // handles the trigger modes 
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      sampling_en   <= 1'b0;
      samples_count <= 'b0;
    end else begin
      if (!start_process || sample_again) begin
        sampling_en   <= 1'b0;
        samples_count <= 'b0;
      end else begin
        case (trigger_mode)
          2'b00: begin  // countinous
            if (fixnosamples_en) begin
              samples_count <= samples_count + 1'b1;
            end
            sampling_en <= !sampling_done_ff & !sampling_done;

          end

          2'b01: begin  // pre trigger
            if ((trigger_event || triggered_occured_ff) & !sampling_done) begin
              sampling_en <= !sampling_done_ff & !sampling_done;
              if (fixnosamples_en) begin
                samples_count <= samples_count + 1'b1;
              end else begin
                samples_count <= 'b0;
              end
            end else begin
              sampling_en <= 1'b0;
            end
          end
          2'b10: begin  // post trigger
            if (trigger_event_ff) begin
              sampling_en <= 1'b0;
            end else begin
              sampling_en <= !sampling_done_ff & !sampling_done;
            end
          end
          2'b11: begin  // center trigger
            if (trigger_event || triggered_occured_ff) begin
              sampling_en   <= !sampling_done_ff & !sampling_done;
              samples_count <= samples_count + 1'b1;
            end else begin
              sampling_en   <= !sampling_done_ff & !sampling_done;
              samples_count <= 'b0;
            end
          end

          default: begin  // default
            sampling_en   <= 1'b0;
            samples_count <= 'b0;
          end

        endcase
      end
    end
  end


  // to generate sampling done signal
  always_comb begin
    case (trigger_mode)
      2'b00: begin
      sampling_done = (mem_full) || (fixnosamples_en? (samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]):1'b0);
        //if (mem_full || fixnosamples_en?samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]:1'b0 ) begin
        //  sampling_done = 1'b1;
        //end else begin
        //  sampling_done = 1'b0;
        //end
      end
      2'b01: begin
        if (mem_full || fixnosamples_en?samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]:1'b0)
          sampling_done = 1'b1;
        else sampling_done = 1'b0;
      end
      2'b10: begin
        if (trigger_event_ff) sampling_done = 1'b1;
        else begin
          sampling_done = 1'b0;
        end
      end
      2'b11: begin
        if (fixnosamples_en) begin
          if (samples_count == noofsamples[SAMPLE_CNTER_WIDTH-1:0]) sampling_done = 1'b1;
          else sampling_done = 1'b0;
        end else begin
          if (samples_count == MEM_DPTH_HALF) sampling_done = 1'b1;
          else sampling_done = 1'b0;
        end
      end
      default: sampling_done = 1'b0;
    endcase
  end
  
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) trigger_event_ff <= 1'b0;
    else 
  trigger_event_ff <= trigger_event;
  end
  // flopped trigger event pulse
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) triggered_occured_ff <= 1'b0;
    else begin
      if (!start_process || sample_again || sampling_done_ff) triggered_occured_ff <= 1'b0;
      else if (trigger_event & trigger_mode != 2'b10) triggered_occured_ff <= 1'b1;
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
    
    always @(posedge rd_clk) begin
        if (ren) begin
            rdata   <= mem[raddr];
        end
    end

    always @(posedge wr_clk) begin
        if (wen) begin
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
    for (i = 0; i < DATA_WIDTH; i = i + 1) begin
      //assign binary_in[i] = enable ? ^gray[DATA_WIDTH-1:i] : 'b0;
      assign binary_in[i] = ^(gray >> i);

    end
  endgenerate

  always @(posedge clk or negedge rstn  ) begin
    if(!rstn) begin
      binary <= 'b0;
    end
    else begin
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
  always @(posedge sample_clk or negedge rstn) begin
    if (!rstn) begin
      sync_register[0] <= 'b0;
    end else begin
      //  sync_register[0] <= {sampling_en, probes};
      sync_register[0] <= probes;
    end

  end

  // buffer registers stages
  genvar b;
  generate
    for (b = 0; b < (BUFFERS - 1); b = b + 1) begin
      always @(posedge sample_clk or negedge rstn) begin
        if (!rstn) begin
          sync_register[b+1] <= 0;
        end else begin
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
    if (!S_AXI_ARESETN) begin
      state <= mem_access;
      mem_read <= 1'b0;
      mem_read_ff <= 1'b0;
    end else begin
      mem_read_ff <= mem_read;
      case (state)
        mem_access: begin
          if (read_data_en && !mem_empty) begin
            if (mem_read) state <= data_out;
            mem_read <= ~mem_read;
          end else begin
            state <= mem_access;
            mem_read <= 1'b0;
          end
        end
        data_out: begin
          if (!read_data_en & fetch_data) begin
            state <= mem_access;
          end else begin
            state <= data_out;
          end
          mem_read <= 1'b0;

        end
        default: begin  // Fault Recovery
          state <= mem_access;
        end
      endcase
    end

  // this part handles word chunks transfer to the axi slave interface for read transactions
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (!S_AXI_ARESETN) begin
      read_data  <= 'b0;
      word_count <= 'b0;
      read_valid <= 'b0;
      fetch_data <= 'b0;
    end else begin
      if (state == data_out) begin
        if (word_count == 'b0 && !fetch_data) begin
          read_data  <= read_accumulated_data;
          //$display("PROBE_BITS chunk %d, %d, %d", NUM_OF_WORD_CHUNKS, PROBE_BITS,`REM_BITS );
          read_valid <= 'b1;
          if (read_ready) word_count <= word_count + 'b1;
          if (word_count >= ((NUM_OF_WORD_CHUNKS) - 1)) fetch_data <= 'b1;
          else fetch_data <= 'b0;
        end else if (word_count >= ((NUM_OF_WORD_CHUNKS) - 1) ) begin
          if (read_data_en && !mem_empty && !read_valid && !fetch_data) begin
            read_data  <= mem_accumulated_data_reg[32*word_count+:PROBE_BITS];
            read_valid <= 'b1;
            word_count <= 'b0;
            fetch_data <= 'b1;
            // $display("word chunk %d, %d", NUM_OF_WORD_CHUNKS, word_count);
          end else begin
            if (read_ready) read_valid <= 'b0;
            fetch_data <= 'b0;
          end
        end else begin
          if ((read_data_en && !mem_empty && !read_valid )) begin
            word_count <= word_count + 'b1;
            read_data  <= mem_accumulated_data_reg[32*word_count+:AXI_DATA_WIDTH];
            read_valid <= 'b1;
            fetch_data <= 'b0;
          end else begin
            if (read_ready) read_valid <= 'b0;
          end
        end
      end else begin
        word_count <= 'b0;
        if (read_ready ) read_data <= 'b0;
        read_valid <= 'b0;
        fetch_data <= 'b0;
      end
    end
  end

  // memory fetched data hold register 
  always @(posedge S_AXI_ACLK or negedge S_AXI_ARESETN) begin
    if (!S_AXI_ARESETN) begin
      mem_accumulated_data_reg <= 'b0;
    end else begin
      if (mem_read_ff) mem_accumulated_data_reg <= read_accumulated_data;
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

    always @(posedge rd_clk or negedge rd_rstn) begin
        if (!rd_rstn) begin
            wr_sync_register[0] <= 0;
        end
        else begin
            wr_sync_register[0] <= wptr;
        end   
    end

    always @(posedge wr_clk or negedge wr_rstn) begin
        if (!wr_rstn) begin
            rd_sync_register[0] <= 0;
        end
        else begin
            rd_sync_register[0] <= rptr;
        end
        
    end
    
    genvar i;

    generate
        for(i=0; i<(SYNC_STAGES-1); i = i+1)begin
            always@(posedge rd_clk or negedge rd_rstn) begin
                if(!rd_rstn) begin
                    wr_sync_register[i+1] <= 0;
                
                end
                else begin
                    wr_sync_register[i+1] <= wr_sync_register[i];
                end
            end     
            always @(posedge wr_clk or negedge wr_rstn) begin
                if (!wr_rstn) begin
                    rd_sync_register[i+1] <= 0;
                end
                else begin
                    rd_sync_register[i+1] <= rd_sync_register[i];
                end    
            end
        end
    endgenerate
endmodule

