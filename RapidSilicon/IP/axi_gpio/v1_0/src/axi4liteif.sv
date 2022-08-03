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

module axi4liteif #
(
  // width of data bus in bits
  parameter DATA_WIDTH = 32,
  // width of address bus in bits
  parameter ADDR_WIDTH = 16,
  // width of strobe signal
  parameter STRB_WIDTH = (DATA_WIDTH/8)
)
(
  input  wire		                    iCLK,
  input  wire			                  iRSTN,
  
  // write address channel
  input  wire [ADDR_WIDTH-1:0]		  iAWADDR,   //AXI4-Lite
  input  wire [2:0]		              iAWPROT,   //AXI4-Lite
  input	 wire                   		iAWVALID,  //AXI4-Lite
  output wire                    		oAWREADY,  //AXI4-Lite
  
  // write data channel
  input  wire [DATA_WIDTH-1:0]		  iWDATA,    //AXI4-Lite
  input  wire [STRB_WIDTH-1:0]      iWSTRB,    //AXI4-Lite
  input  wire			                  iWVALID,   //AXI4-Lite
  output wire		                    oWREADY,   //AXI4-Lite
  
  // write response channel
  output wire [1:0]		              oBRESP,    //AXI4-Lite
  output wire		                    oBVALID,   //AXI4-Lite
  input  wire			                  iBREADY,   //AXI4-Lite
  
  // read address channel
  input  wire [ADDR_WIDTH-1:0]		  iARADDR,   //AXI4-Lite
  input  wire [2:0]		              iARPROT,   //AXI4-Lite
  input	 wire		                    iARVALID,  //AXI4-Lite
  output wire                   		oARREADY,  //AXI4-Lite

  // read data channel
  output wire [DATA_WIDTH-1:0]		  oRDATA,    //AXI4-Lite
  output wire [1:0]		              oRRESP,    //AXI4-Lite
  output wire		                    oRVALID,   //AXI4-Lite
  input  wire			                  iRREADY,   //AXI4-Lite
  
  // interface to register block
  output wire [7:0]		              oPWADR,
  output wire [DATA_WIDTH-1:0]		  oPWDAT,
  output wire                       oPWRTE,
  output wire [7:0]             		oPRADR,
  input  wire [DATA_WIDTH-1:0]		  iPRDAT,
  input  wire			                  iPERR 
  );

  
  //AXI4-Lite
  // - all transactions are of burst lenght 1
  // - all data accesses use the full width of the data bus (32bit or 64bit)
  // - all accesses are non-modifiable, non-bufferable
  // - exclusive accesses are not supported
  axadrchsm #(
    .ADDR_WIDTH(ADDR_WIDTH)
  )
  wradrch (
    .iCLK		    (iCLK), 
    .iRSTN		  (iRSTN),

    .iADDR		  (iAWADDR),
    .iPROT		  (iAWPROT),
    .iVALID		  (iAWVALID),
    .oREADY		  (oAWREADY),
    
    .iBUSY		  (iARVALID & ~iAWVALID)
  );
  
  axwrch #(
    .DATA_WIDTH(DATA_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH)
  ) 
  wrdatch (
    .iCLK		    (iCLK), 
    .iRSTN		  (iRSTN),

    .iAWADDR		(iAWADDR),
    .iWDATA		  (iWDATA),
    .iWSTRB		  (iWSTRB),
    .iWVALID		(iWVALID),
    .oWREADY		(oWREADY),
    
    .iARVALID		(iARVALID),
  
    .oBRESP		  (oBRESP),
    .oBVALID		(oBVALID),
    .iBREADY		(iBREADY),
    
    .oPWADR		  (oPWADR),
    .oPWDAT		  (oPWDAT),
    .oPWRTE		  (oPWRTE),
    .iPERR		  (iPERR)
  );

  axadrchsm #(
    .ADDR_WIDTH(ADDR_WIDTH)
  ) 
  rdadrch (
    .iCLK		    (iCLK), 
    .iRSTN		  (iRSTN),

    .iADDR		  (iARADDR),
    .iPROT		  (iARPROT),
    .iVALID		  (iARVALID),
    .oREADY		  (oARREADY),
    
    .iBUSY		  (iAWVALID)
  );

  axrdch #(
    .DATA_WIDTH(DATA_WIDTH),
    .ADDR_WIDTH(ADDR_WIDTH)
  )
  rddatch(
    .iCLK		    (iCLK), 
    .iRSTN		  (iRSTN),
  
    .iARADDR		(iARADDR),
    .iARVALID		(iARVALID),
  
    .oRDATA		  (oRDATA),
    .oRRESP		  (oRRESP),
    .oRVALID		(oRVALID),
    .iRREADY		(iRREADY),
  
    .oPRADR		  (oPRADR),
    .iPRDAT		  (iPRDAT),
    .iPERR		  (iPERR)
);
  
endmodule
