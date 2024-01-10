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

module gpcore #
(
  parameter IP_TYPE 		= "GPIO",
  parameter IP_VERSION 	= 32'h1, 
  parameter IP_ID 		  = 32'h2591754,
  
  // width of data bus in bits
  parameter DATA_WIDTH = 32
)
(
  input  wire			                  iCLK,
  input	 wire		                    iRSTN,
  input  wire [7:0] 		            iWADR,
  input  wire			                  iWR,
  input  wire [DATA_WIDTH-1:0] 		  iWDAT,
  input  wire [7:0] 		            iRADR,
  output wire [DATA_WIDTH-1:0] 		  oRDAT, 

  input  wire [DATA_WIDTH-1:0] 		  iGPIN,
  output wire [DATA_WIDTH-1:0] 		  oGPOUT,
  output wire		                    oINT,
  
  output wire		                    oERR
);
  
  reg  [DATA_WIDTH-1:0]		          rGpDat;
  reg  [DATA_WIDTH-1:0]		          rGpDir;
  reg			                          rGpIen;
  reg			                          rGpInt;
  reg			                          rGpClr;

  reg  [7:0]		                      regAdr;
  reg  [DATA_WIDTH-1:0]		  regDat, regDatQ;
  reg			                   isErr, isErrQ;
  
  wire [DATA_WIDTH-1:0]		          gpInDir;
  reg                                 gpInt;
  
  reg [31:0] reg_TYPE;
  reg [31:0] reg_ID;
  reg [31:0] reg_VERSION;
  
  parameter[7:0]	  GP_TYPE      = 8'h0,
                      GP_VERSION   = 8'h1,
                      GP_ID        = 8'h2,
                      GPDAT        = 8'h3,
  			          GPDIR        = 8'h4,
  			          GPIEN        = 8'h5,
  			          GPINT        = 8'h6;
  
  assign oRDAT 		    = regDatQ;
  assign oERR 		    = isErrQ;
  assign oINT		    = rGpInt;
  assign oGPOUT		    = rGpDat & ~rGpDir;
  assign reg_TYPE       = IP_TYPE;
  assign reg_ID         = IP_ID;
  assign reg_VERSION    = IP_VERSION;

  // interrupt logic
  assign gpInDir 	= rGpDir & iGPIN;
  always @* gpInt	= (rGpIen & |gpInDir);
  always @(posedge iCLK or negedge iRSTN) begin
    if (~iRSTN) begin
      rGpInt <=  1'b0;
    end
    else begin
      if (~rGpInt) begin             
        rGpInt <= gpInt;
      end
      else begin
        rGpInt <= ~rGpClr;
      end      
    end
  end  
  
  // select address
  always @* regAdr = iWR ? iWADR : iRADR;
  
  // write to register
  always @(posedge iCLK or negedge iRSTN) begin
    if (~iRSTN) begin
      rGpDat <= 32'h0;
      rGpDir <= 32'h0;
      rGpIen <=  1'b0;
//      rGpInt <=  1'b0;
      rGpClr <=  1'b0;
    end
    else begin
	  case (regAdr)
        GPDAT: begin
          if (iWR) rGpDat <= iWDAT & ~rGpDir;
        end
        GPDIR: begin
          if (iWR) rGpDir <= iWDAT;
        end
        GPIEN: begin
          if (iWR) rGpIen <= iWDAT[0];
        end
        GPINT: begin
          if (iWR) rGpClr <= iWDAT[0] & rGpInt;
        end
        default: begin
        end
      endcase
    end 
  end  
  
  // register access status
  always @* begin
    isErr = 1'b0;
    case (regAdr)
      GPDAT,
      GPDIR,
      GPIEN,
      GPINT:   isErr = 1'b0;
      default: isErr = iWR;
    endcase
  end
  
  // read from register
  always @* begin
    regDat = 32'h0;
    case (regAdr)
      GP_TYPE:      regDat = reg_TYPE;
      GP_VERSION:   regDat = reg_VERSION;
      GP_ID:        regDat = reg_ID;
      GPDAT:        regDat = rGpDat;
      GPDIR:        regDat = rGpDir;
      GPIEN:        regDat = {31'h0, rGpIen};
      GPINT:        regDat = {31'h0, rGpInt}; 
      default:      regDat = 32'h0;
    endcase
  end
  
  // register outputs
  always @(posedge iCLK or negedge iRSTN) begin
    if (~iRSTN) begin
      isErrQ  <= 1'b0;
      regDatQ <= 32'h0;
    end
    else begin
      isErrQ  <= isErr;
      regDatQ <= regDat;
    end 
  end
  
endmodule
