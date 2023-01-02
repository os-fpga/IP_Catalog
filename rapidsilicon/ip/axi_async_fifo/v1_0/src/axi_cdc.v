module axi_async_fifo #(
    
    // The size value of total number of entries in FIFO 
    parameter FIFO_DEPTH = 3,
    // Total number of synchronization stages, to handle metastaibility. This value can be greater but minimum value is 2.
    parameter SYNC_STAGES = 2,
    // Width of data bus in bits
    parameter DATA_WIDTH = 32,
    // Width of address bus in bits
    parameter ADDR_WIDTH = 32,
    // Width of strb (width of data bus in words)
    parameter STRB_WIDTH = (DATA_WIDTH/8),
    // Width of ID signal
    parameter ID_WIDTH = 1,
)
(

   input    wire                             S_AXI_ACLK,
   input    wire                             S_AXI_ARESETN,
   input    wire                             M_AXI_ACLK,
   input    wire                             M_AXI_ARESETN,

   /* AXI4 FULL slave interface */
      
    /* Address read channel */
   input    wire [AXI_ADDR_WIDTH-1 : 0]     S_AXI_ARADDR,
   input    wire [1 : 0]                    S_AXI_ARBURST,
   input    wire [3 : 0]                    S_AXI_ARCACHE,
   input    wire [7 : 0]                    S_AXI_ARLEN,
   input    wire                            S_AXI_ARLOCK,
   input    wire [2 : 0]                    S_AXI_ARPROT,
   input    wire [3 : 0]                    S_AXI_ARQOS,
   output   wire                            S_AXI_ARREADY,
   input    wire [AXI_ID_WIDTH-1 : 0]       S_AXI_ARID,
   input    wire [2 : 0]                    S_AXI_ARSIZE,
   input    wire                            S_AXI_ARVALID,

   /* Address write channel */
   input    wire [AXI_ADDR_WIDTH-1 : 0]     S_AXI_AWADDR,
   input    wire [1 : 0]                    S_AXI_AWBURST,
   input    wire [3 : 0]                    S_AXI_AWCACHE,
   input    wire [7 : 0]                    S_AXI_AWLEN,
   input    wire                            S_AXI_AWLOCK,
   input    wire [2 : 0]                    S_AXI_AWPROT,
   input    wire [3 : 0]                    S_AXI_AWQOS,
   output   wire                            S_AXI_AWREADY,
   input    wire [AXI_ID_WIDTH-1 : 0]       S_AXI_AWID,
   input    wire [2 : 0]                    S_AXI_AWSIZE,
   input    wire                            S_AXI_AWVALID,
   
      /* Write response channel */
   input    wire                            S_AXI_BREADY,
   output   wire [1 : 0]                    S_AXI_BRESP,
   output   wire                            S_AXI_BVALID,
   output   wire [AXI_ID_WIDTH-1 : 0]       S_AXI_BID,
   
      /* Read response channel */
   output   wire [AXI_DATA_WIDTH-1 : 0]     S_AXI_RDATA,
   output   wire                            S_AXI_RLAST,
   input    wire                            S_AXI_RREADY,
   output   wire [1 : 0]                    S_AXI_RRESP,
   output   wire                            S_AXI_RVALID,
   output   wire [AXI_ID_WIDTH-1 : 0]       S_AXI_RID,
     
   /* Data write channel */
   input    wire [AXI_DATA_WIDTH-1 : 0]     S_AXI_WDATA,
   input    wire                            S_AXI_WLAST,
   output   wire                            S_AXI_WREADY,
   input    wire [(AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
   input    wire                            S_AXI_WVALID,


  /*  AXI4 FULL master interface  */

   /* Address write channel */ 
   output   wire [AXI_ID_WIDTH-1 : 0]       M_AXI_AWID,
   output   wire [AXI_ADDR_WIDTH-1 : 0]     M_AXI_AWADDR,
   output   wire [7 : 0]                    M_AXI_AWLEN,
   output   wire [2 : 0]                    M_AXI_AWSIZE,
   output   wire [1 : 0]                    M_AXI_AWBURST,
   output   wire                            M_AXI_AWLOCK,
   output   wire [3 : 0]                    M_AXI_AWCACHE,
   output   wire [2 : 0]                    M_AXI_AWPROT,
   output   wire [3 : 0]                    M_AXI_AWQOS,
   output   wire                            M_AXI_AWVALID,
   input    wire                            M_AXI_AWREADY,

   /* Data write channel */
   output   wire [AXI_DATA_WIDTH-1 : 0]     M_AXI_WDATA,
   output   wire [(AXI_DATA_WIDTH/8)-1 : 0] M_AXI_WSTRB,
   output   wire                            M_AXI_WLAST,
   output   wire                            M_AXI_WVALID,
   input    wire                            M_AXI_WREADY,

   /* Write response channel */
   input    wire [AXI_ID_WIDTH-1 : 0]       M_AXI_BID,
   input    wire [1 : 0]                    M_AXI_BRESP,
   input    wire                            M_AXI_BVALID,
   output   wire                            M_AXI_BREADY,

   /* Address read channel */
   output   wire [AXI_ID_WIDTH-1 : 0]       M_AXI_ARID,
   output   wire [AXI_ADDR_WIDTH-1 : 0]     M_AXI_ARADDR,
   output   wire [7 : 0]                    M_AXI_ARLEN,
   output   wire [2 : 0]                    M_AXI_ARSIZE,
   output   wire [1 : 0]                    M_AXI_ARBURST,
   output   wire                            M_AXI_ARLOCK,
   output   wire [3 : 0]                    M_AXI_ARCACHE,
   output   wire [2 : 0]                    M_AXI_ARPROT,
   output   wire [3 : 0]                    M_AXI_ARQOS,
   output   wire                            M_AXI_ARVALID,
   input    wire                            M_AXI_ARREADY,

   /* Read response channel */
   input    wire [AXI_ID_WIDTH-1 : 0]       M_AXI_RID,
   input    wire [AXI_DATA_WIDTH-1 : 0]     M_AXI_RDATA,
   input    wire [1 : 0]                    M_AXI_RRESP,
   input    wire                            M_AXI_RLAST,
   input    wire                            M_AXI_RVALID,
   output   wire                            M_AXI_RREADY);

    wire awfull, awempty, wfull, wempty, bfull, bempty, arfull, arempty, rfull, rempty;



// AW channel fifo
    fifo #(
    .DATASIZE(AXI_ID_WIDTH + AXI_ADDR_WIDTH + 8 + 3 + 2 + 1 + 4 + 3 + 4),
    .ADDRSIZE(FIFO_SIZE ),
    .SYNC_STAGES (SYNC_STAGES )
    )
    awfifo (
    .rd_data  ({M_AXI_AWID, M_AXI_AWADDR,M_AXI_AWLEN, 
                M_AXI_AWSIZE, M_AXI_AWBURST,M_AXI_AWLOCK,
                M_AXI_AWCACHE, M_AXI_AWPROT, M_AXI_AWQOS}),
    .rd_empty (awempty),
    .wr_full  (awfull),
    .wr_clk   (S_AXI_ACLK),
    .rd_clk   (M_AXI_ACLK),
    .wr_rst   (S_AXI_ARESETN),
    .rd_rst   (M_AXI_ARESETN),
    .wr       (S_AXI_AWVALID && S_AXI_AWREADY),
    .wr_data  ({S_AXI_AWID, S_AXI_AWADDR,S_AXI_AWLEN,
                S_AXI_AWSIZE, S_AXI_AWBURST,S_AXI_AWLOCK,
                S_AXI_AWCACHE, S_AXI_AWPROT, S_AXI_AWQOS}),
    .rd       (M_AXI_AWREADY)
    );

    assign S_AXI_AWREADY = ~awfull;
    assign M_AXI_AWVALID = ~awempty;


// W channel fifo

    fifo #(
        .DATASIZE(AXI_DATA_WIDTH + AXI_DATA_WIDTH/8 + 1),
        .ADDRSIZE(FIFO_SIZE ),
        .SYNC_STAGES (SYNC_STAGES )
    )
    wfifo (
    .rd_data  ({M_AXI_WDATA, M_AXI_WSTRB, M_AXI_WLAST }),
    .rd_empty (wempty),
    .wr_full  (wfull),
    .wr_clk   (S_AXI_ACLK),
    .rd_clk   (M_AXI_ACLK),
    .wr_rst   (S_AXI_ARESETN),
    .rd_rst   (M_AXI_ARESETN),
    .wr       (S_AXI_WVALID && S_AXI_WREADY),
    .wr_data  ({S_AXI_WDATA, S_AXI_WSTRB, S_AXI_WLAST }),
    .rd       (M_AXI_WREADY)
    );

    assign S_AXI_WREADY = ~wfull;
    assign M_AXI_WVALID = ~wempty;

// B channel fifo

    fifo #(
        .DATASIZE(AXI_ID_WIDTH + 2),
        .ADDRSIZE(FIFO_SIZE ),
        .SYNC_STAGES (SYNC_STAGES )
    )
    respfifo (
    .rd_data  ({S_AXI_BID, S_AXI_BRESP}),
    .rd_empty (bempty),
    .wr_full  (bfull),
    .wr_clk   (M_AXI_ACLK),
    .rd_clk   (S_AXI_ACLK),
    .wr_rst   (M_AXI_ARESETN),
    .rd_rst   (S_AXI_ARESETN),
    .wr       (M_AXI_BVALID && M_AXI_BREADY),
    .wr_data  ({M_AXI_BID, M_AXI_BRESP  }),
    .rd       (S_AXI_BREADY)
    );    


    assign M_AXI_BREADY = ~bfull;
    assign S_AXI_BVALID = ~bempty;


// AR channel fifo
    fifo #(
        .DATASIZE(AXI_ID_WIDTH + AXI_ADDR_WIDTH + 8 + 3 + 2 + 1 + 4 + 3 + 4),
        .ADDRSIZE(FIFO_SIZE ),
        .SYNC_STAGES (SYNC_STAGES )
    )
    arfifo (
    .rd_data  ({M_AXI_ARID, M_AXI_ARADDR,
                M_AXI_ARLEN, M_AXI_ARSIZE, M_AXI_ARBURST,
                M_AXI_ARLOCK,M_AXI_ARCACHE, M_AXI_ARPROT,
                M_AXI_ARQOS }),
    .rd_empty (arempty),
    .wr_full  (arfull),
    .wr_clk   (S_AXI_ACLK),
    .rd_clk   (M_AXI_ACLK),
    .wr_rst   (S_AXI_ARESETN),
    .rd_rst   (M_AXI_ARESETN),
    .wr       (S_AXI_ARVALID && S_AXI_ARREADY),
    .wr_data  ({S_AXI_ARID, S_AXI_ARADDR,
                S_AXI_ARLEN, S_AXI_ARSIZE, S_AXI_ARBURST,
                S_AXI_ARLOCK,S_AXI_ARCACHE, S_AXI_ARPROT, 
                S_AXI_ARQOS}),
    .rd       (M_AXI_ARREADY)
    );    
    
    assign S_AXI_ARREADY = ~arfull;
    assign M_AXI_ARVALID = ~arempty;


// R channel fifo
    fifo #(
        .DATASIZE(AXI_ID_WIDTH + AXI_DATA_WIDTH + 2 + 1),
        .ADDRSIZE(FIFO_SIZE ),
        .SYNC_STAGES (SYNC_STAGES )
    )
    rfifo (
    .rd_data  ({S_AXI_RID, S_AXI_RDATA, S_AXI_RLAST, S_AXI_RRESP}),
    .rd_empty (rempty),
    .wr_full  (rfull),
    .wr_clk   (M_AXI_ACLK),
    .rd_clk   (S_AXI_ACLK),
    .wr_rst   (M_AXI_ARESETN),
    .rd_rst   (S_AXI_ARESETN),
    .wr       (M_AXI_RVALID && M_AXI_RREADY),
    .wr_data  ({M_AXI_RID, M_AXI_RDATA, M_AXI_RLAST, M_AXI_RRESP}),
    .rd       (S_AXI_RREADY)
    );

    assign M_AXI_RREADY = ~rfull;
    assign S_AXI_RVALID = ~rempty;

endmodule
