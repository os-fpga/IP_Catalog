//`define AXI4FULL 


module axi_cdc #(
	/* ID width for master and slave interface */
	parameter	AXI_ID_WIDTH	= 	8,
	/* Data width of axi bus */
	parameter  	AXI_DATA_WIDTH	= 	32,
	/* Address width of axi bus */
	parameter  	AXI_ADDR_WIDTH	= 	32,
	 /* Total number of synchronization stages, to handle metastaibility. This value can be greater but minimum value is 2 */
	parameter	SYNC_STAGES 	= 	2,
	/* The log value of total number of entries in FIFO */
	parameter	FIFO_LOG        = 	3,
	/* For BRAM set MEM_TYPE=1, while for Distributed memory set MEM_TYPE=0 */
    parameter   MEM_TYPE = 0
		
) 
(


    input   wire                            S_AXI_ACLK,
    input   wire                            S_AXI_ARESET,
    input   wire                            M_AXI_ACLK,
    input   wire                            M_AXI_ARESET,
    `ifdef AXI4FULL
    /* Address write channel */
    input   wire [AXI_ID_WIDTH-1 : 0]       S_AXI_AWID,
    input   wire [AXI_ADDR_WIDTH-1 : 0]     S_AXI_AWADDR,
    input   wire [7 : 0]                    S_AXI_AWLEN,
    input   wire [2 : 0]                    S_AXI_AWSIZE,
    input   wire [1 : 0]                    S_AXI_AWBURST,
    input   wire [1 : 0]                    S_AXI_AWLOCK,
    input   wire [3 : 0]                    S_AXI_AWCACHE,
    input   wire [2 : 0]                    S_AXI_AWPROT,
    input   wire [3 : 0]                    S_AXI_AWQOS,
    input   wire                            S_AXI_AWVALID,
    output  wire                            S_AXI_AWREADY,
    /* Data write channel */
    input   wire [AXI_DATA_WIDTH-1 : 0]     S_AXI_WDATA,
    input   wire [(AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
    input   wire                            S_AXI_WLAST,
    input   wire                            S_AXI_WVALID,
    output  wire                            S_AXI_WREADY,
    /* Write response channel */	
    output  wire [AXI_ID_WIDTH-1 : 0]       S_AXI_BID,
    output  wire [1 : 0]                    S_AXI_BRESP,
    output  wire                            S_AXI_BVALID,
    input   wire                            S_AXI_BREADY,
    /* Address read channel */
    input	wire [AXI_ID_WIDTH-1 : 0]       S_AXI_ARID,
    input	wire [AXI_ADDR_WIDTH-1 : 0]     S_AXI_ARADDR,
    input	wire [7 : 0]                    S_AXI_ARLEN,
    input	wire [2 : 0]                    S_AXI_ARSIZE,
    input	wire [1 : 0]                    S_AXI_ARBURST,
    input	wire [1 : 0]                    S_AXI_ARLOCK,
    input	wire [3 : 0]                    S_AXI_ARCACHE,
    input	wire [2 : 0]                    S_AXI_ARPROT,
    input	wire [3 : 0]                    S_AXI_ARQOS,
    input   wire                            S_AXI_ARVALID,
    output  wire                            S_AXI_ARREADY,
    /* Read response channe   */                 
    output  wire [AXI_ID_WIDTH-1 : 0]       S_AXI_RID,
    output  wire [AXI_DATA_WIDTH-1 : 0]     S_AXI_RDATA,
    output  wire [1 : 0]                    S_AXI_RRESP,
    output  wire                            S_AXI_RLAST,
    output  wire                            S_AXI_RVALID,
    input   wire                            S_AXI_RREADY,

	

    /* Address write channel */ 
    output  wire [AXI_ID_WIDTH-1 : 0]       M_AXI_AWID,
    output  wire [AXI_ADDR_WIDTH-1 : 0]     M_AXI_AWADDR,
    output  wire [7 : 0]                    M_AXI_AWLEN,
    output  wire [2 : 0]                    M_AXI_AWSIZE,
    output  wire [1 : 0]                    M_AXI_AWBURST,
    output  wire [1 : 0]                    M_AXI_AWLOCK,
    output  wire [3 : 0]                    M_AXI_AWCACHE,
    output  wire [2 : 0]                    M_AXI_AWPROT,
    output  wire [3 : 0]                    M_AXI_AWQOS,
    output  wire                            M_AXI_AWVALID,
    input   wire                            M_AXI_AWREADY,
    /* Data write channel */
    output  wire [AXI_DATA_WIDTH-1 : 0]     M_AXI_WDATA,
    output  wire [(AXI_DATA_WIDTH/8)-1 : 0] M_AXI_WSTRB,
    output  wire                            M_AXI_WLAST,
    output  wire                            M_AXI_WVALID,
    input   wire                            M_AXI_WREADY,
    /* Write response channel */
    input   wire [AXI_ID_WIDTH-1 : 0]       M_AXI_BID,
    input   wire [1 : 0]                    M_AXI_BRESP,
    input   wire                            M_AXI_BVALID,
    output  wire                            M_AXI_BREADY,
    /* Address read channel */
    output  wire [AXI_ID_WIDTH-1 : 0]       M_AXI_ARID,
    output  wire [AXI_ADDR_WIDTH-1 : 0]     M_AXI_ARADDR,
    output  wire [7 : 0]                    M_AXI_ARLEN,
    output  wire [2 : 0]                    M_AXI_ARSIZE,
    output  wire [1 : 0]                    M_AXI_ARBURST,
    output  wire [1 : 0]                    M_AXI_ARLOCK,
    output  wire [3 : 0]                    M_AXI_ARCACHE,
    output  wire [2 : 0]                    M_AXI_ARPROT,
    output  wire [3 : 0]                    M_AXI_ARQOS,
    output  wire                            M_AXI_ARVALID,
    input   wire                            M_AXI_ARREADY,
    /* Read response channel */	
    input   wire [AXI_ID_WIDTH-1 : 0]       M_AXI_RID,
    input   wire [AXI_DATA_WIDTH-1 : 0]     M_AXI_RDATA,
    input   wire [1 : 0]                    M_AXI_RRESP,
    input   wire                            M_AXI_RLAST,
    input   wire                            M_AXI_RVALID,
    output  wire                            M_AXI_RREADY,   
    `else
    /*  AXI4 LITE slave interface */
    /* Address read channel */
    input    wire [AXI_ADDR_WIDTH-1 : 0]     S_AXI_ARADDR,
    input    wire [2 : 0]                    S_AXI_ARPROT,
    output   wire                            S_AXI_ARREADY,
    input    wire                            S_AXI_ARVALID,
    /* Address write channel */
    input    wire [AXI_ADDR_WIDTH-1 : 0]     S_AXI_AWADDR,
    input    wire [2 : 0]                    S_AXI_AWPROT,
    output   wire                            S_AXI_AWREADY,
    input    wire                            S_AXI_AWVALID,
      
    /* Write response channel */
    input    wire                            S_AXI_BREADY,
    output   wire [1 : 0]                    S_AXI_BRESP,
    output   wire                            S_AXI_BVALID,
      
    /* Read response channel */
    output   wire [AXI_DATA_WIDTH-1 : 0]     S_AXI_RDATA,
    input    wire                            S_AXI_RREADY,
    output   wire [1 : 0]                    S_AXI_RRESP,
    output   wire                            S_AXI_RVALID,
        
    /* Data write channel */
    input    wire [AXI_DATA_WIDTH-1 : 0]     S_AXI_WDATA,
    output   wire                            S_AXI_WREADY,
    input    wire [(AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
    input    wire                            S_AXI_WVALID,
    
    
     /*  AXI4 LITE  master interface  */
    
     /* Address write channel */ 
    output   wire [AXI_ADDR_WIDTH-1 : 0]     M_AXI_AWADDR,
    output   wire [2 : 0]                    M_AXI_AWPROT,
    output   wire                            M_AXI_AWVALID,
    input    wire                            M_AXI_AWREADY,
    /* Data write channel */
    output   wire [AXI_DATA_WIDTH-1 : 0]     M_AXI_WDATA,
    output   wire [(AXI_DATA_WIDTH/8)-1 : 0] M_AXI_WSTRB,
    output   wire                            M_AXI_WVALID,
    input    wire                            M_AXI_WREADY,
    /* Write response channel */
    input    wire [1 : 0]                    M_AXI_BRESP,
    input    wire                            M_AXI_BVALID,
    output   wire                            M_AXI_BREADY,
    /* Address read channel */
    output   wire [AXI_ADDR_WIDTH-1 : 0]     M_AXI_ARADDR,
    output   wire [2 : 0]                    M_AXI_ARPROT,
    output   wire                            M_AXI_ARVALID,
    input    wire                            M_AXI_ARREADY,
    /* Read response channel */
    input    wire [AXI_DATA_WIDTH-1 : 0]     M_AXI_RDATA,
    input    wire [1 : 0]                    M_AXI_RRESP,
    input    wire                            M_AXI_RVALID,
    output   wire                            M_AXI_RREADY,

    `endif AXI4FULL	



);

    wire  awfull, awempty, wfull, wempty, bfull, bempty,arfull, arempty, rfull, rempty;
    
    `ifdef AXI4FULL
    
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (AXI_ID_WIDTH + AXI_ADDR_WIDTH+ 8 + 3 + 2 + 2 + 4 + 3 + 4),
    .MEM_TYPE(MEM_TYPE)
    )
    awfifo(
        .wclk(S_AXI_ACLK),
        .wr_reset(S_AXI_ARESET),
        .wr(S_AXI_AWVALID && S_AXI_AWREADY),
        .wr_data({ S_AXI_AWID, S_AXI_AWADDR,
                     S_AXI_AWLEN, S_AXI_AWSIZE, S_AXI_AWBURST,
                     S_AXI_AWLOCK,S_AXI_AWCACHE, S_AXI_AWPROT, S_AXI_AWQOS }),
        .wr_full(awfull),
        .rclk(M_AXI_ACLK),
        .rd_reset(M_AXI_ARESET),
        .rd(M_AXI_AWREADY),
        .rd_data({ M_AXI_AWID, M_AXI_AWADDR,
                     M_AXI_AWLEN, M_AXI_AWSIZE, M_AXI_AWBURST,
                     M_AXI_AWLOCK,M_AXI_AWCACHE, M_AXI_AWPROT, M_AXI_AWQOS }),
        .rd_empty(awempty)
    );
    
    assign M_AXI_AWVALID = !awempty;
    assign S_AXI_AWREADY = !awfull;
    
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (AXI_DATA_WIDTH + AXI_DATA_WIDTH/8 + 1),
    .MEM_TYPE(MEM_TYPE)
    )
    wfifo(
        .wclk(S_AXI_ACLK),
        .wr_reset(S_AXI_ARESET),
        .wr(S_AXI_WVALID&& S_AXI_WREADY),
        .wr_data({ S_AXI_WDATA, S_AXI_WSTRB, S_AXI_WLAST }),
        .wr_full(wfull),
        .rclk(M_AXI_ACLK),
        .rd_reset(M_AXI_ARESET),
        .rd(M_AXI_WREADY),
        .rd_data({ M_AXI_WDATA, M_AXI_WSTRB, M_AXI_WLAST }),
        .rd_empty(wempty)
        );
    
    assign	M_AXI_WVALID = !wempty;
    assign	S_AXI_WREADY = !wfull;
    
    
    
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (AXI_ID_WIDTH + 2),
    .MEM_TYPE(MEM_TYPE)
    )
    bfifo(
        .wclk(M_AXI_ACLK),
        .wr_reset(M_AXI_ARESET),
        .wr(M_AXI_BVALID&& M_AXI_BREADY),
        .wr_data({ M_AXI_BID, M_AXI_BRESP }),
        .wr_full(bfull),
        .rclk(S_AXI_ACLK),
        .rd_reset(S_AXI_ARESET),
        .rd(S_AXI_BREADY),
        .rd_data({ S_AXI_BID, S_AXI_BRESP }),
        .rd_empty(bempty)
        );
    
    assign	S_AXI_BVALID = !bempty;
    assign	M_AXI_BREADY = !bfull;
        
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (AXI_ID_WIDTH + AXI_ADDR_WIDTH + 8 + 3 + 2 + 2 + 4 + 3 + 4),
    .MEM_TYPE(MEM_TYPE)
    )
    
    arfifo(
        .wclk(S_AXI_ACLK),
        .wr_reset(S_AXI_ARESET),
        .wr(S_AXI_ARVALID&& S_AXI_ARREADY),
        .wr_data({ S_AXI_ARID, S_AXI_ARADDR,
                     S_AXI_ARLEN, S_AXI_ARSIZE, S_AXI_ARBURST,
                     S_AXI_ARLOCK,S_AXI_ARCACHE, S_AXI_ARPROT, S_AXI_ARQOS }),
        .wr_full(arfull),
        .rclk(M_AXI_ACLK),
        .rd_reset(M_AXI_ARESET),
        .rd(M_AXI_ARREADY),
        .rd_data({ M_AXI_ARID, M_AXI_ARADDR,
                     M_AXI_ARLEN, M_AXI_ARSIZE, M_AXI_ARBURST,
                     M_AXI_ARLOCK,M_AXI_ARCACHE, M_AXI_ARPROT, M_AXI_ARQOS }),
        .rd_empty(arempty)
        );
    
    assign	M_AXI_ARVALID = !arempty;
    assign	S_AXI_ARREADY = !arfull;
    
    
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (AXI_ID_WIDTH + AXI_DATA_WIDTH+3),
    .MEM_TYPE(MEM_TYPE)
    )
    
    rfifo(
        .wclk(M_AXI_ACLK),
        .wr_reset(M_AXI_ARESET),
        .wr(M_AXI_RVALID&& M_AXI_RREADY),
        .wr_data({ M_AXI_RID, M_AXI_RDATA, M_AXI_RLAST, M_AXI_RRESP }),
        .wr_full(rfull),
        .rclk(S_AXI_ACLK),
        .rd_reset(S_AXI_ARESET),
        .rd(S_AXI_RREADY),
        .rd_data({ S_AXI_RID, S_AXI_RDATA, S_AXI_RLAST, S_AXI_RRESP }),
        .rd_empty(rempty)
        );
    
    assign	S_AXI_RVALID = !rempty;
    assign	M_AXI_RREADY = !rfull;
    
    `else
    
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (AXI_ADDR_WIDTH + 3),
    .MEM_TYPE(MEM_TYPE)
    )
    awfifo(
        .wclk(S_AXI_ACLK),
        .wr_reset(S_AXI_ARESET),
        .wr(S_AXI_AWVALID && S_AXI_AWREADY),
        .wr_data({S_AXI_AWADDR,S_AXI_AWPROT}),
        .wr_full(awfull),
        .rclk(M_AXI_ACLK),
        .rd_reset(M_AXI_ARESET),
        .rd(M_AXI_AWREADY),
        .rd_data({M_AXI_AWADDR,M_AXI_AWPROT}),
        .rd_empty(awempty)
    );
    
    assign    M_AXI_AWVALID = !awempty;
    assign    S_AXI_AWREADY = !awfull;
    
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (AXI_DATA_WIDTH + AXI_DATA_WIDTH/8),
    .MEM_TYPE(MEM_TYPE)
    )
    wfifo(
        .wclk(S_AXI_ACLK),
        .wr_reset(S_AXI_ARESET),
        .wr(S_AXI_WVALID&& S_AXI_WREADY),
        .wr_data({S_AXI_WDATA, S_AXI_WSTRB}),
        .wr_full(wfull),
        .rclk(M_AXI_ACLK),
        .rd_reset(M_AXI_ARESET),
        .rd(M_AXI_WREADY),
        .rd_data({M_AXI_WDATA, M_AXI_WSTRB}),
        .rd_empty(wempty)
        );
    
    assign    M_AXI_WVALID = !wempty;
    assign    S_AXI_WREADY = !wfull;
    
    
    
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (2),
    .MEM_TYPE(MEM_TYPE)
    )
    bfifo(
        .wclk(M_AXI_ACLK),
        .wr_reset(M_AXI_ARESET),
        .wr(M_AXI_BVALID&& M_AXI_BREADY),
        .wr_data({ M_AXI_BRESP}),
        .wr_full(bfull),
        .rclk(S_AXI_ACLK),
        .rd_reset(S_AXI_ARESET),
        .rd(S_AXI_BREADY),
        .rd_data({ S_AXI_BRESP}),
        .rd_empty(bempty)
        );
    
    assign    S_AXI_BVALID = !bempty;
    assign    M_AXI_BREADY = !bfull;
        
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE ( AXI_ADDR_WIDTH + 3),
    .MEM_TYPE(MEM_TYPE)
    )
    
    arfifo(
        .wclk(S_AXI_ACLK),
        .wr_reset(S_AXI_ARESET),
        .wr(S_AXI_ARVALID&& S_AXI_ARREADY),
        .wr_data({S_AXI_ARADDR,S_AXI_ARPROT}),
        .wr_full(arfull),
        .rclk(M_AXI_ACLK),
        .rd_reset(M_AXI_ARESET),
        .rd(M_AXI_ARREADY),
        .rd_data({M_AXI_ARADDR,M_AXI_ARPROT}),
        .rd_empty(arempty)
        );
    
    assign    M_AXI_ARVALID = !arempty;
    assign    S_AXI_ARREADY = !arfull;
    
    
    afifo #(
    .ADDRSIZE (FIFO_LOG),
    .SYNC_STAGES (SYNC_STAGES),
    .DATASIZE (AXI_DATA_WIDTH + 2),
    .MEM_TYPE(MEM_TYPE)
    )
    
    rfifo(
        .wclk(M_AXI_ACLK),
        .wr_reset(M_AXI_ARESET),
        .wr(M_AXI_RVALID&& M_AXI_RREADY),
        .wr_data({M_AXI_RDATA,M_AXI_RRESP}),
        .wr_full(rfull),
        .rclk(S_AXI_ACLK),
        .rd_reset(S_AXI_ARESET),
        .rd(S_AXI_RREADY),
        .rd_data({S_AXI_RDATA, S_AXI_RRESP}),
        .rd_empty(rempty)
        );

    assign	S_AXI_RVALID = !rempty;
    assign	M_AXI_RREADY = !rfull;
        
       `endif

endmodule
