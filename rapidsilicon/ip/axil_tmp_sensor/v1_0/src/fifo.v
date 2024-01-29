`timescale 1 ns / 1 ps

module afifo #(
	/* Defining depth of fifo */
	parameter	ADDRSIZE = 3,
	//
	// WIDTH is the number of data bits in each entry
	parameter	DATASIZE  = 32,
	//
	/* Total number of syn stages. The number of stages can be greater than 2 but not less than 2 */
	parameter	SYNC_STAGES    = 2,
	/* For BRAM set MEM_TYPE=1, while for Distributed memory set MEM_TYPE=0 */
	parameter MEM_TYPE = 0

	) 
	(
	
    input   wire                  wclk, 
    input   wire                  wr_reset, 
    input   wire                  wr,
    input   wire [DATASIZE-1:0]   wr_data,
    output                        wr_full,
    input   wire                  rclk,
    input   wire                  rd_reset,
    input   wire                  rd,
    output       [DATASIZE-1:0]   rd_data,
    output  reg                   rd_empty

    );

    reg     [ADDRSIZE:0]          rd_addr;
    reg     [ADDRSIZE:0]          wr_addr;
    wire    [ADDRSIZE:0]          rd_wgray;
    wire    [ADDRSIZE:0]          wr_rgray;
    wire    [ADDRSIZE:0]          next_rd_addr;
    wire    [ADDRSIZE:0]          next_wr_addr;
    reg     [ADDRSIZE:0]          rgray, wgray;
    wire                          ren;
    wire                          read_empty;


    /* increment write pointer when wr signal goes high and fifo is not full */
    assign	next_wr_addr = wr_addr + 1;
    always @(posedge wclk )
    if (wr_reset)
    begin
        wr_addr <= 0;
        wgray   <= 0;
    end else if (wr && !wr_full)
    begin
        wr_addr <= next_wr_addr;
        /* Binary to Gray code conversion */
        wgray   <= next_wr_addr ^ (next_wr_addr >> 1);
    end
    
    /* increment read pointer when rd signal goes high and fifo is not empty */
    assign	next_rd_addr = rd_addr + 1;
    always @(posedge rclk)
    if (rd_reset)
    begin
        rd_addr <= 0;
        rgray   <= 0;
    end else if (ren && !read_empty)
    begin
        rd_addr <= next_rd_addr;
        /* Binary to Gray code conversion */
        rgray   <= next_rd_addr ^ (next_rd_addr >> 1);
    end


	/* wr_full signal goes high if fifo is full */
	assign 	wr_full = (wr_rgray == { ~wgray[ADDRSIZE:ADDRSIZE-1], wgray[ADDRSIZE-2:0] });

	/* this signal goes high if fifo is empty */
	assign  read_empty = (rd_wgray == rgray);
		
	assign  ren = (rd_empty || rd);

        
    always @(posedge rclk )
        if (rd_reset)
            rd_empty <= 1'b1;
         else if (ren)
            rd_empty <= read_empty;

	
    synchronizer # (.SYNC_STAGES(SYNC_STAGES),
                    .ADDRSIZE   (ADDRSIZE))
    synchronizer(
                .wptr_reg    (wr_rgray),
                .rptr_reg    (rd_wgray),
                .wr_clk      (wclk),
                .rd_clk      (rclk),
                .wr_rst      (wr_reset),
                .rd_rst      (rd_reset),
                .wptr        (wgray),
                .rptr        (rgray)
                );
	
   dual_port_ram # (.DATASIZE(DATASIZE),
                    .ADDRSIZE (ADDRSIZE)
                    )
   dual_port_ram(
                 .rdata  (rd_data),
                 .wr_clk (wclk),
                 .rd_clk (rclk),
                 .wen    (wr && !wr_full),
                 .ren    (ren),
                 .wdata  (wr_data),
                 .waddr  (wr_addr),
                 .raddr  (rd_addr)
                 );

endmodule

module dual_port_ram #(
    /* Define width of memory */
    parameter DATASIZE = 32,
    /* Define depth of memory */
    parameter ADDRSIZE = 4
)
(
    output reg [DATASIZE-1:0]   rdata,
    input                       wr_clk,
    input                       rd_clk,
    input                       wen,
    input                       ren,
    input      [DATASIZE-1:0]   wdata,
    input      [ADDRSIZE:0]     waddr,
    input      [ADDRSIZE:0]     raddr
);
   
   /* Inferring Block memory as Dual Port RAM */
   
       reg [DATASIZE-1:0] mem	[(1<<ADDRSIZE)-1:0];

        always @(posedge rd_clk) begin
            if (ren) begin
                rdata   <= mem[raddr[ADDRSIZE-1:0]];
            end
        end

        always @(posedge wr_clk) begin
            if (wen) 
            mem[waddr[ADDRSIZE-1:0]]  <=  wdata;
        end
    
endmodule

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

    always @(posedge wr_clk) begin
        if (wr_rst) begin
            wr_sync_register[0] <= 0;
        end
        else begin
            wr_sync_register[0] <= rptr;
        end   
    end

    always @(posedge rd_clk) begin
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
            always@(posedge wr_clk ) begin
                if(wr_rst) begin
                    wr_sync_register[i+1] <= 0;
                end
                else begin
                    wr_sync_register[i+1] <= wr_sync_register[i];
                end
            end     
            always @(posedge rd_clk ) begin
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