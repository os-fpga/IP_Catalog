module synchronizer #(

     /* Total number of synchronization stages, to handle metastaibility. This value can be greater but minimum value is 2 */
    parameter SYNC_STAGES   = 2,
    parameter ADDRSIZE      = 4
)
(
    output  [ADDRSIZE:0]    wptr_reg,
    output  [ADDRSIZE:0]    rptr_reg,
    input                   wr_clk,
    input                   rd_clk,
    input                   wr_rst,
    input                   rd_rst,
    input   [ADDRSIZE:0]    wptr,
    input   [ADDRSIZE:0]    rptr

);
    
    reg [ADDRSIZE:0] wr_sync_register[0:SYNC_STAGES-1];
    reg [ADDRSIZE:0] rd_sync_register[0:SYNC_STAGES-1];


    assign wptr_reg = wr_sync_register[SYNC_STAGES-1];
    assign rptr_reg = rd_sync_register[SYNC_STAGES-1];

    always @(posedge wr_clk or posedge wr_rst) begin
        if (wr_rst) begin
            wr_sync_register[0] <= 0;
        end
        else begin
            wr_sync_register[0] <= rptr;
        end   
    end

    always @(posedge rd_clk or posedge rd_rst) begin
        if (rd_rst) begin
            rd_sync_register[0] <= 0;
        end
        else begin
            rd_sync_register[0] <= wptr;
        end
        
    end
    
    genvar i;

    generate
        for(i=0; i<(SYNC_STAGES-1); i = i+1)begin
            always@(posedge wr_clk or posedge wr_rst) begin
                if(wr_rst) begin
                    wr_sync_register[i+1] <= 0;
                end
                else begin
                    wr_sync_register[i+1] <= wr_sync_register[i];
                end
            end     
            always @(posedge rd_clk or posedge rd_rst) begin
                if (rd_rst) begin
                    rd_sync_register[i+1] <= 0;
                end
                else begin
                    rd_sync_register[i+1] <= rd_sync_register[i];
                end    
            end
        end
    endgenerate


endmodule
