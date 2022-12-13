//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer:
//
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: OCLA Controller
// Module Name: OCLA Controller
// Project Name: OCLA IP Core Development
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

/* verilator lint_off WIDTH */

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
  assign rpntr_mv = (trigger_mode == 2'b10 | trigger_mode == 2'b11);

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
              if (wptr_bin > nosamples) rd_cnt <= wptr_bin - nosamples;
              else rd_cnt <= rd_binary_value;
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
              if (wptr_bin > nosamples) rd_cnt <=  wptr_bin - nosamples;
              else rd_cnt <=  (MEM_DEPTH + wptr_bin) - nosamples;
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
