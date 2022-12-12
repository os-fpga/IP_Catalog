//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer:
//
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: OCLA Top
// Module Name:
// Project Name:
// Target Devices: Gemini RS-75
// Tool Versions: Raptor
// Description:
// TBA
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////

/* verilator lint_off DECLFILENAME */

`include "defines.sv"

module ocla #(
    parameter NO_OF_PROBES = `NUM_OF_PROBES,
    parameter NO_OF_TRIGGER_INPUTS = `NUM_OF_TRIGGER_INPUTS,
    parameter PROBE_WIDHT = `PROBE_WIDHT_BITS,
    parameter MEM_DEPTH = `MEMORY_DEPTH,
    parameter AXI_DATA_WIDTH = `S_AXI_DATA_WIDTH,
    parameter AXI_ADDR_WIDTH = `S_AXI_ADDR_WIDTH

) (
    input logic sample_clk,
    input logic rstn,


    // AXI_BUS.slv_lite axi_slave /*,

`ifdef TRIGGER_INPUTS
    input logic [NO_OF_TRIGGER_INPUTS-1:0] trigger_input,
`endif

`ifdef trigger_outputs
    input logic [`Nooftriggeroutputs-1:0] trigger_output,
`endif

    input logic S_AXI_ACLK,
    input logic S_AXI_ARESETN,

`ifdef AXI_LITE_INTF


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
`endif
    input logic [NO_OF_PROBES-1:0] probes
);


  logic sampling_en;
  logic trigger_event;
  logic data_wen;
  logic wr_full;
  logic [NO_OF_PROBES-1:0] data_accumulate;
  logic [NO_OF_PROBES-1:0] read_accumulated_data;
  logic mem_read;
  logic mem_empty;
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
      .REG_WIDTH(1)
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
      .BUFFERS(`BUFFER_STAGES)
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
      .REG_WIDTH(1)
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
      .SAMPLE_CNTER_WIDTH(`SAMPLE_COUNTER_WIDTH),
      .MEM_DPTH_HALF(`MEMORY_DEPTH_HALF)
  ) ocla_controller_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
      .trigger_event(trigger_event),
      .trigger_mode(tmtr_port[1:0]),
      .mem_full(wr_full),
      .start_process(tmtr_port_strt_bit_sync),
      .fixnosamples_en(tmtr_port[3]),
      .noofsamples(tmtr_port[4+:`SAMPLE_COUNTER_WIDTH]),
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

  trigger_control_unit #(
      .NPROBES(`NUM_OF_PROBES),
      .PROBE_WIDHT(PROBE_WIDHT),
      .TRIGGER_INPUTS(`NUM_OF_TRIGGER_INPUTS)
  ) trig_control_unit_inst (
      .sample_clk(sample_clk),
      .rstn(rstn),
`ifdef TRIGGER_INPUTS
      .in_signals({probes, trigger_input[NO_OF_TRIGGER_INPUTS-1:0]}),
`else
      .in_signals(probes),
`endif
      .config_bits(tcur_port),
`ifdef value_compare_trigger

      .reg_value(tdcr_port[PROBE_WIDHT-1:0]),
`endif
      .trigger_event(trigger_event)
  );

  // ---------------------------------------------------------------//
  // Synchronizer flop instance for                                 //
  // for sampling done signal from axi clock domain                 //
  // to sampling clock domain                                       //
  // ---------------------------------------------------------------//

  ddff_sync #(
      .REG_WIDTH(1)
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
      .ADDRSIZE(`COUNTER_WIDHT),
      .NOSAMPLE_WIDTH(`SAMPLE_COUNTER_WIDTH),
      .MEM_DEPTH(MEM_DEPTH),
      .SYNC_STAGES(`SYNC_STAGES)
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
      .nosamples(tmtr_port[4+:`SAMPLE_COUNTER_WIDTH]),
      .fixnosamples_en(tmtr_port[3]),
      .sampling_done_ff(done_sampling_ff_sync)
  );

  // ---------------------------------------------------------------//
  // stream_out_buffer instance                                     //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//

  stream_out_buffer #(
      .WORD_CHUNK_COUNTER_WIDTH(`WORD_CHUNK_CNTR_WIDTH),
      .NUM_OFPROBES(NO_OF_PROBES),
      .NUM_OF_WORD_CHUNKS(`WORD_CHUNKS),
      .PROBE_BITS(`PROBE_BITS),
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
`ifdef AXI_LITE_INTF

  axi_slv_lite #(
      .C_S_AXI_DATA_WIDTH(AXI_DATA_WIDTH),
      .C_S_AXI_ADDR_WIDTH(AXI_ADDR_WIDTH)
  ) axi_slv_lite_inst (
      .tbdr_port(tbdr_port),
      .read_trace_mem_en(read_trace_mem_en),
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
`endif
  // ---------------------------------------------------------------//
  // Axi full slave instance                                        //
  //                                                                //
  //                                                                //
  // ---------------------------------------------------------------//

  /*
  axi_slave_intrf #(
      .C_S_AXI_ID_WIDTH(),
      .C_S_AXI_DATA_WIDTH(),BREADY
      .C_S_AXI_ADDR_WIDTH(),
      .C_S_AXI_AWUSER_WIDTH(),
      .C_S_AXI_ARUSER_WIDTH(),
      .C_S_AXI_WUSER_WIDTH(),
      .C_S_AXI_RUSER_WIDTH(),
      .C_S_AXI_BUSER_WIDTH()
  ) axi_slave_intrf_inst (
      .S_AXI_ACLK(S_AXI_ACLK),
      .S_AXI_ARESETN(rstn),
      .S_AXI_AWID(axi_slave.aw_id),
      .S_AXI_AWADDR(axi_slave.aw_addr),
      .S_AXI_AWLEN(axi_slave.aw_len),
      .S_AXI_AWSIZE(axi_slave.aw_size),
      .S_AXI_AWBURST(axi_slave.aw_burst),
      .S_AXI_AWLOCK(axi_slave.aw_lock),
      .S_AXI_AWCACHE(axi_slave.aw_cache),
      .S_AXI_AWPROT(axi_slave.aw_prot),
      .S_AXI_AWQOS(axi_slave.aw_qos),
      .S_AXI_AWREGION(axi_slave.aw_region),
      .S_AXI_AWUSER(axi_slave.aw_user),
      .S_AXI_AWVALID(axi_slave.aw_valid),
      .S_AXI_AWREADY(axi_slave.aw_ready),

      .S_AXI_WDATA(axi_slave.w_data),
      .S_AXI_WSTRB(axi_slave.w_strb),
      .S_AXI_WLAST(axi_slave.w_last),
      .S_AXI_WUSER(axi_slave.w_user),
      .S_AXI_WVALID(axi_slave.w_valid),
      .S_AXI_WREADY(axi_slave.w_ready),

      .S_AXI_BID(axi_slave.b_id),
      .S_AXI_BRESP(axi_slave.b_resp),
      .S_AXI_BUSER(axi_slave.b_user),
      .S_AXI_BVALID(axi_slave.b_valid),
      .S_AXI_BREADY(axi_slave.b_ready),
      .S_AXI_ARID(axi_slave.ar_id),

      .S_AXI_ARADDR(axi_slave.ar_addr),
      .S_AXI_ARLEN(axi_slave.ar_len),
      .S_AXI_ARSIZE(axi_slave.ar_size),
      .S_AXI_ARBURST(axi_slave.ar_burst),
      .S_AXI_ARLOCK(axi_slave.ar_lock),
      .S_AXI_ARCACHE(axi_slave.ar_cache),
      .S_AXI_ARPROT(axi_slave.ar_prot),
      .S_AXI_ARQOS(axi_slave.ar_qos),
      .S_AXI_ARREGION(axi_slave.ar_region),
      .S_AXI_ARUSER(axi_slave.ar_user),
      .S_AXI_ARVALID(axi_slave.ar_valid),
      .S_AXI_ARREADY(axi_slave.ar_ready),

      .S_AXI_RID(axi_slave.r_id),
      .S_AXI_RDATA(axi_slave.r_data),
      .S_AXI_RRESP(axi_slave.r_resp),
      .S_AXI_RLAST(axi_slave.r_last),
      .S_AXI_RUSER(axi_slave.r_user),
      .S_AXI_RVALID(axi_slave.r_valid),
      .S_AXI_RREADY(axi_slave.r_ready)
  );
  */
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
