module fifo #(
    parameter DATASIZE      = 32,
    parameter DEPTH         = 8,
    parameter ADDRSIZE      = $clog2(DEPTH),
    parameter SYNC_STAGES   = 2
)
(
    output  [DATASIZE-1:0]      rd_data,
    output                      rd_empty,
    output                      wr_full,
    input                       wr_clk,
    input                       rd_clk,
    input                       wr_rst,
    input                       rd_rst,
    input                       wr,
    input   [DATASIZE-1:0]      wr_data,
    input                       rd


);
    wire                        wen;
    wire                        ren;          
    wire    [ADDRSIZE:0]        wr_gray_code;
    wire    [ADDRSIZE:0]        wr_binary_value;
    wire    [ADDRSIZE:0]        rptr_reg;
    reg                         wr_full;
    reg     [ADDRSIZE:0]        wptr;
    reg     [ADDRSIZE:0]        wr_cnt;
    wire    [ADDRSIZE-1:0]      waddr;

    wire    [ADDRSIZE:0]        rd_gray_code;
    wire    [ADDRSIZE:0]        rd_binary_value;
    wire    [ADDRSIZE:0]        wptr_reg;
    reg                         rd_empty;
    reg     [ADDRSIZE:0]        rptr;
    reg     [ADDRSIZE:0]        rd_cnt;
    wire    [ADDRSIZE-1:0]      rdaddr;

    /* write data to memory when wr is high and fifo is not full */
    assign wen              =   wr && (!wr_full);
    assign ren              =   rd && (!rd_empty);

    /* write counter will increment only when their is a write operation request and fifo is not 
    full. Read counter will increment only when their is a request for read operation and fifo is 
    not empty */
    assign wr_binary_value  =   wr_cnt + wen;
    assign rd_binary_value  =   rd_cnt + (rd && ~rd_empty);


    /* Binary to Gray code conversion */
    assign wr_gray_code    =   (wr_binary_value >> 1) ^ wr_binary_value;
    assign rd_gray_code    =   (rd_binary_value >> 1) ^ rd_binary_value;

    /* Memory address for write/read operation */
    assign waddr            =   wr_cnt[ADDRSIZE-1:0];
    assign rdaddr           =   rd_cnt[ADDRSIZE-1:0];

    /* Checking condition for fifo full & empty */
    assign fifo_full  = (wr_gray_code == {~rptr_reg[ADDRSIZE:ADDRSIZE-1],rptr_reg[ADDRSIZE-2 : 0]});
    assign fifo_empty = (rd_gray_code == wptr_reg);

    always @(posedge wr_clk or posedge wr_rst) begin
        if (wr_rst) begin
            wptr    <= 0;
            wr_cnt  <= 0;
            wr_full <= 0;
        end
        else begin
            wptr    <= wr_gray_code;
            wr_cnt  <= wr_binary_value;
            wr_full <= fifo_full;
        end  
    end

    always @(posedge rd_clk or posedge rd_rst) begin
        if (rd_rst) begin
            rptr    <= 0;
            rd_cnt  <= 0;
            rd_empty <= 0;
        end
        else begin
            rptr    <= rd_gray_code;
            rd_cnt  <= rd_binary_value;
            rd_empty <= fifo_empty;
        end  
    end    


    dual_port_ram # (.DATASIZE(DATASIZE),
                     .ADDRSIZE (ADDRSIZE))
    dual_port_ram(
                .rdata  (rd_data),
                .wr_clk (wr_clk),
                .rd_clk (rd_clk),
                .wen    (wen),
                .ren    (ren),
                .wdata  (wr_data),
                .waddr  (waddr),
                .raddr  (rdaddr)
    );

    synchronizer # (.SYNC_STAGES(SYNC_STAGES),
                    .ADDRSIZE   (ADDRSIZE))
    synchronizer(
                .wptr_reg    (wptr_reg),
                .rptr_reg    (rptr_reg),
                .wr_clk      (wr_clk),
                .rd_clk      (rd_clk),
                .wr_rst      (wr_rst),
                .rd_rst      (rd_rst),
                .wptr        (wptr),
                .rptr        (rptr)

   );
endmodule