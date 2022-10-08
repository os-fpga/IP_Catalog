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


module axrdch #
(
  // width of data bus in bits
  parameter DATA_WIDTH = 32,
  // width of address bus in bits
  parameter ADDR_WIDTH = 16
)
(
  input  wire			                  iCLK, 
  input	 wire		                    iRSTN,
  
  input  wire  [ADDR_WIDTH-1:0]		  iARADDR,
  input	 wire		                    iARVALID,
  
  output wire  [DATA_WIDTH-1:0]	   	oRDATA,
  output wire  [1:0]		            oRRESP,
  output wire		                    oRVALID,
  input  wire		        	          iRREADY,
  
  output wire  [7:0]		            oPRADR,
  input  wire  [DATA_WIDTH-1:0]	    iPRDAT,
  input	 wire		                    iPERR    
);


  
  reg [7:0]		                rAddr;
  reg [DATA_WIDTH-1:0]	    	rData;

  reg		          	          rdAct;
  reg [1:0]	          rResp,  rRespQ;
  reg			                    rValid;
  
  parameter[1:0]	OKAY   	= 2'b00,
  			          SLVERR 	= 2'b10;
  
  parameter	    	SET	    = 1'b1,
  		          	RESET	  = 1'b0;
  
  // to AXI
  assign oRDATA		= iPRDAT; //rData;
  assign oRRESP  	= (iPERR & rdAct) ? SLVERR : rRespQ;
  assign oRVALID	= rValid;
  
  // to register block
  assign oPRADR		= rAddr;

  // signals to register block
  always @(posedge iCLK or negedge iRSTN) begin
    if (~iRSTN) begin
      rAddr <= 8'h0;
    end
    else begin
      rAddr <= iARVALID ? iARADDR[7:0] : 8'h0;
    end 
  end

  // signals to AXI
  always @(posedge iCLK or negedge iRSTN) begin
    if (~iRSTN) begin
      rdAct  <= RESET;
      rData  <= 32'h0;
      rRespQ <= OKAY;
      rValid <= RESET;
    end
    else begin
      if (~rdAct) begin
        rdAct <= iARVALID;
      end
      else begin        
        if (iRREADY & rValid) begin
          rData  <= 32'h0;
          rRespQ <= OKAY;
          rValid <= RESET;
          rdAct  <= RESET;
        end
        else begin
          rData	 <= iPRDAT;
          rRespQ <= iPERR ? SLVERR : OKAY;
          rValid <= SET;
          rdAct  <= SET;
        end
      end
    end 
  end
  
endmodule