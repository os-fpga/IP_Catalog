// start of the code

module axil_slave #
        (
            parameter integer C_S_AXI_DATA_WIDTH	= 32,
            parameter integer C_S_AXI_ADDR_WIDTH	= 7, 
            parameter integer NO_OF_IN_PROBE_REGS   = 4,
            parameter integer NO_OF_OUT_PROBE_REGS  = 4
        )
        (
            input wire  S_AXI_ACLK,
            input wire  S_AXI_ARESETN,
            
            
            input  wire     [C_S_AXI_ADDR_WIDTH-1 : 0] S_AXI_AWADDR,
            input  wire                        [2 : 0] S_AXI_AWPROT,
            input  wire                                S_AXI_AWVALID,
            output wire                                S_AXI_AWREADY,
            input  wire     [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_WDATA,
            input  wire [(C_S_AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
            input  wire                                S_AXI_WVALID,
            output wire                                S_AXI_WREADY,
            output wire                        [1 : 0] S_AXI_BRESP,
            output wire                                S_AXI_BVALID,
            input  wire                                S_AXI_BREADY,
            input  wire     [C_S_AXI_ADDR_WIDTH-1 : 0] S_AXI_ARADDR,
            input  wire                        [2 : 0] S_AXI_ARPROT,
            input  wire                                S_AXI_ARVALID,
            output wire                                S_AXI_ARREADY,
            output wire     [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_RDATA,
            output wire                        [1 : 0] S_AXI_RRESP,
            output wire                                S_AXI_RVALID,
            input  wire                                S_AXI_RREADY,
            
            output wire                                AXI_WREN,
            output wire                                AXI_RDEN,
            input  wire       [C_S_AXI_DATA_WIDTH-1:0] AXI_DAT_IN        
        );

	// AXI4LITE signals
	reg [C_S_AXI_ADDR_WIDTH-1 : 0] axi_awaddr;
	reg  	                       axi_awready;
	reg  	                       axi_wready;
	reg                    [1 : 0] axi_bresp;
	reg  	                       axi_bvalid;
	reg [C_S_AXI_ADDR_WIDTH-1 : 0] axi_araddr;
	reg  	                       axi_arready;
	reg [C_S_AXI_DATA_WIDTH-1 : 0] axi_rdata;
	reg                    [1 : 0] axi_rresp;
	reg  	                       axi_rvalid;
	
	reg [C_S_AXI_DATA_WIDTH-1:0]   reg_data_out;
	reg	 aw_en;

    integer	  byte_index;

	assign S_AXI_AWREADY = axi_awready;
	assign S_AXI_WREADY	 = axi_wready;
	assign S_AXI_BRESP	 = axi_bresp;
	assign S_AXI_BVALID	 = axi_bvalid;
	assign S_AXI_ARREADY = axi_arready;
	assign S_AXI_RDATA	 = axi_rdata;
	assign S_AXI_RRESP	 = axi_rresp;
	assign S_AXI_RVALID	 = axi_rvalid;

	always @( posedge S_AXI_ACLK )
	begin
	  if ( S_AXI_ARESETN == 1'b0 )
	    begin
	      axi_awready <= 1'b0;
	      aw_en <= 1'b1;
	    end 
	  else
	    begin    
	      if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en)
	        begin
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

	always @( posedge S_AXI_ACLK )
	begin
	  if ( S_AXI_ARESETN == 1'b0 )
	    begin
	      axi_awaddr <= 0;
	    end 
	  else
	    begin    
	      if (~axi_awready && S_AXI_AWVALID && S_AXI_WVALID && aw_en)
	        begin
	          axi_awaddr <= S_AXI_AWADDR;
	        end
	    end 
	end       

	always @( posedge S_AXI_ACLK )
	begin
	  if ( S_AXI_ARESETN == 1'b0 )
	    begin
	      axi_wready <= 1'b0;
	    end 
	  else
	    begin    
	      if (~axi_wready && S_AXI_WVALID && S_AXI_AWVALID && aw_en )
	        begin
	          axi_wready <= 1'b1;
	        end
	      else
	        begin
	          axi_wready <= 1'b0;
	        end
	    end 
	end       

	assign AXI_WREN = axi_wready && S_AXI_WVALID && axi_awready && S_AXI_AWVALID;

	always @( posedge S_AXI_ACLK )
	begin
	  if ( S_AXI_ARESETN == 1'b0 )
	    begin
	      axi_bvalid  <= 0;
	      axi_bresp   <= 2'b0;
	    end 
	  else
	    begin    
	      if (axi_awready && S_AXI_AWVALID && ~axi_bvalid && axi_wready && S_AXI_WVALID)
	        begin
	          axi_bvalid <= 1'b1;
	          axi_bresp  <= 2'b0; // 'OKAY' response 
	        end                   // work error responses in future
	      else
	        begin
	          if (S_AXI_BREADY && axi_bvalid)   
	            begin
	              axi_bvalid <= 1'b0; 
	            end  
	        end
	    end
	end   

	always @( posedge S_AXI_ACLK )
	begin
	  if ( S_AXI_ARESETN == 1'b0 )
	    begin
	      axi_arready <= 1'b0;
	      axi_araddr  <= 32'b0;
	    end 
	  else
	    begin    
	      if (~axi_arready && S_AXI_ARVALID)
	        begin
	          axi_arready <= 1'b1;
	          axi_araddr  <= S_AXI_ARADDR;
	        end
	      else
	        begin
	          axi_arready <= 1'b0;
	        end
	    end 
	end       

	always @( posedge S_AXI_ACLK )
	begin
	  if ( S_AXI_ARESETN == 1'b0 )
	    begin
	      axi_rvalid <= 0;
	      axi_rresp  <= 0;
	    end 
	  else
	    begin    
	      if (axi_arready && S_AXI_ARVALID && ~axi_rvalid)
	        begin
	          axi_rvalid <= 1'b1;
	          axi_rresp  <= 2'b0; // 'OKAY' response
	        end   
	      else if (axi_rvalid && S_AXI_RREADY)
	        begin
	          axi_rvalid <= 1'b0;
	        end                
	    end
	end    

	assign AXI_RDEN = axi_arready & S_AXI_ARVALID & ~axi_rvalid;

	// Output register or memory read data
	always @( posedge S_AXI_ACLK )
	begin
	  if ( S_AXI_ARESETN == 1'b0 )
	    begin
	      axi_rdata  <= 0;
	    end 
	  else
	    begin    
	      if (AXI_RDEN)
            axi_rdata <= AXI_DAT_IN;     // register read data
          else    
            axi_rdata <= 0;
	    end
	end    

endmodule