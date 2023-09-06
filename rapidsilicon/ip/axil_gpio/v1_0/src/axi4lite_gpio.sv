////////////////////////////////////////////////////////////////////////////////
//
// MIT License
//
// Copyright (c) 2017 Smartfox Data Solutions Inc.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in 
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
////////////////////////////////////////////////////////////////////////////////

module axi4lite_gpio #
(
  parameter IP_TYPE 		= "GPIO",
	parameter IP_VERSION 	= 32'h1, 
	parameter IP_ID 		  = 32'h2591754,
  
  // width of data bus in bits
  parameter DATA_WIDTH = 32,
  // width of address bus in bits
  parameter ADDR_WIDTH = 16,
  // width of strobe signal
  parameter STRB_WIDTH = (DATA_WIDTH/8)
)

(
  input  wire                         CLK, 
  input  wire			                    RSTN, 
  input  wire  [DATA_WIDTH-1:0]    		GPIN,                 
  output wire  [DATA_WIDTH-1:0]    		GPOUT,                 
  output wire		                      INT,
  
  // write address channel
  input  wire  [ADDR_WIDTH-1:0]    		AWADDR,
  input  wire  [2:0]     		          AWPROT,
  input  wire			                    AWVALID,
  output wire           		          AWREADY,
  
  // write data channel
  input  wire  [DATA_WIDTH-1:0]		    WDATA,
  input  wire  [STRB_WIDTH-1:0]		    WSTRB,
  input  wire			                    WVALID,
  output wire 		                    WREADY,
  
  // write response channel
  output wire  [1:0]		              BRESP,
  output wire		                      BVALID,
  input  wire			                    BREADY,

  // read address channel
  input  wire  [ADDR_WIDTH-1:0]		    ARADDR,
  input  wire  [2:0]		              ARPROT,
  input  wire                    			ARVALID,
  output wire		                      ARREADY,

  // read data channel
  output wire  [DATA_WIDTH-1:0]		    RDATA,
  output wire  [1:0]		              RRESP,
  output wire		                      RVALID,
  input  wire                    			RREADY
);

  wire [7:0]                          PWADR;
  wire [DATA_WIDTH-1:0]               PWDAT;
  wire	   	                          PWRTE;
  wire [7:0]                          PRADR;
  wire [DATA_WIDTH-1:0]               PRDAT;
  wire                                PERR;

  
  axi4liteif #(
    .DATA_WIDTH(DATA_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH)
  ) 
  axi4liteif (
    .iCLK		    (CLK), 
    .iRSTN		  (RSTN),

    .iAWADDR		(AWADDR),
    .iAWPROT		(AWPROT),
    .iAWVALID		(AWVALID),
    .oAWREADY		(AWREADY),

    .iWDATA		  (WDATA),
    .iWSTRB		  (WSTRB),
    .iWVALID		(WVALID),
    .oWREADY		(WREADY),

    .oBRESP		  (BRESP),
    .oBVALID		(BVALID),
    .iBREADY		(BREADY),

    .iARADDR		(ARADDR),
    .iARPROT		(ARPROT),
    .iARVALID		(ARVALID),
    .oARREADY		(ARREADY),

    .oRDATA		  (RDATA),
    .oRRESP		  (RRESP),
    .oRVALID		(RVALID),
    .iRREADY		(RREADY),
    
    .oPWADR		  (PWADR),
    .oPWDAT		  (PWDAT),
    .oPWRTE		  (PWRTE),
    .oPRADR		  (PRADR),
    .iPRDAT		  (PRDAT),
    .iPERR     	(PERR)
  );
  
  gpcore #(
    .DATA_WIDTH(DATA_WIDTH)
  ) 
  gpcore (
    .iCLK		  (CLK), 
    .iRSTN		(RSTN),
    
    .iWADR		(PWADR),
    .iWR		  (PWRTE),
    .iWDAT		(PWDAT),
    .iRADR		(PRADR),
    .oRDAT		(PRDAT),
    .oERR		  (PERR),

    .iGPIN		(GPIN),
    .oGPOUT		(GPOUT),
    .oINT		  (INT)
  );

endmodule
