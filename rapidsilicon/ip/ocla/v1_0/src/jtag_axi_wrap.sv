// Copyright 2018 ETH Zurich and University of Bologna.
// Copyright and related rights are licensed under the Solderpad Hardware
// License, Version 0.51 (the "License"); you may not use this file except in
// compliance with the License.  You may obtain a copy of the License at
// http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
// or agreed to in writing, software, hardware and materials distributed under
// this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.


//typedef enum        logic [2:0]       {idle, request, readdata, storedata, ack} FSMState;

module jtag_axi_wrap #
  (
   parameter integer C_S_AXI_ID_WIDTH      = 4,
   parameter integer C_S_AXI_DATA_WIDTH    = 64,
   parameter integer C_S_AXI_ADDR_WIDTH    = 32,
   parameter integer C_S_AXI_AWUSER_WIDTH  = 4,
   parameter integer C_S_AXI_ARUSER_WIDTH  = 4,
   parameter integer C_S_AXI_WUSER_WIDTH   = 4,
   parameter integer C_S_AXI_RUSER_WIDTH   = 4,
   parameter integer C_S_AXI_BUSER_WIDTH   = 4
  )                          
  (
   // inputs
   input logic 	                                               update,
   input logic [(C_S_AXI_DATA_WIDTH + C_S_AXI_ADDR_WIDTH + 2) - 1 : 0] axireg_i,  // doesn't include other signals yet
   input logic 	                                               aclk,
   input logic 	                                               aresetn,

   output logic                              [2:0] state_axi_fsm,
   output logic [(C_S_AXI_DATA_WIDTH + 2) - 1 : 0] axireg_o,
   // AXI_BUS.Master      jtag_master 
   
   // write address channel
   output logic        [C_S_AXI_ID_WIDTH-1 : 0] aw_id,
   output logic      [C_S_AXI_ADDR_WIDTH-1 : 0] aw_addr,
   output logic                                 aw_lock,
   output logic                           [3:0] aw_cache,
   output logic                           [2:0] aw_prot,
   output logic                           [3:0] aw_region,
   output logic    [C_S_AXI_AWUSER_WIDTH-1 : 0] aw_user,
   output logic                           [3:0] aw_qos,
   output logic                                 aw_valid,
   input  logic                                 aw_ready,
   output logic                           [1:0] aw_burst,
   output logic                           [2:0] aw_size,
   output logic                           [7:0] aw_len,
   
   // read address channel
   output logic        [C_S_AXI_ID_WIDTH-1 : 0] ar_id,
   output logic      [C_S_AXI_ADDR_WIDTH-1 : 0] ar_addr,
   output logic                                 ar_lock,
   output logic                           [3:0] ar_cache,
   output logic                           [2:0] ar_prot,
   output logic                           [3:0] ar_region,
   output logic    [C_S_AXI_ARUSER_WIDTH-1 : 0] ar_user,
   output logic                           [3:0] ar_qos,
   output logic                                 ar_valid,
   input  logic                                 ar_ready,
   output logic                           [1:0] ar_burst,
   output logic                           [2:0] ar_size,
   output logic                           [7:0] ar_len,
   
   // write data channel
   output logic      [C_S_AXI_DATA_WIDTH-1 : 0] w_data,
   output logic  [(C_S_AXI_DATA_WIDTH/8)-1 : 0] w_strb,
   output logic                                 w_last,
   output logic     [C_S_AXI_WUSER_WIDTH-1 : 0] w_user,
   output logic                                 w_valid,
   input  logic                                 w_ready,
   
   // read data channel
   input  logic      [C_S_AXI_DATA_WIDTH-1 : 0] r_data,
   input  logic                                 r_last,
   input  logic                                 r_valid,
   input  logic                           [1:0] r_resp,
   output logic                                 r_ready,
   input  logic     [C_S_AXI_RUSER_WIDTH-1 : 0] r_user,
    
   // write response channel
   input  logic                          [1:0]  b_resp,
   input  logic                                 b_valid,
   output logic                                 b_ready,
   input  logic     [C_S_AXI_BUSER_WIDTH-1 : 0] b_user
  );

   localparam idle      = 3'b000;
   localparam request   = 3'b001;
   localparam readdata  = 3'b010;
   localparam storedata = 3'b011;
   localparam ack       = 3'b100;

   logic                              [2:0] state_dp, state_dn;
   logic [(C_S_AXI_DATA_WIDTH + 2) - 1 : 0] axireg_n, axireg_p;

   logic 	       axi_request;
   logic 	       loadstore;
   logic     [1:0] burst_type;

   assign state_axi_fsm = state_dp;
   assign axi_request = axireg_i[0];
   assign loadstore   = axireg_i[1];   // set for write, clear for read

   always_comb 
   begin
      state_dn = state_dp;

      axireg_n = axireg_p;
      axireg_o = axireg_p;

      // default assignments
      aw_id     = '0;  // write address ID. set to 0
      aw_addr   = '0;  // write address
      aw_lock   = '0;  // write lock type (00 for normal access)
      aw_cache  = '0;  // write attributes for caching (0000 for noncacheable and nunbufferable)
      aw_prot   = '0;  // no idea
      aw_region = '0;  // optional 000
      aw_user   = '0;  // dunno
      aw_qos    = '0;  // dunno
      aw_valid  = '0;  // write address valid

      ar_id     = '0;
      ar_addr   = '0;
      ar_lock   = '0;
      ar_cache  = '0;
      ar_prot   = '0;
      ar_region = '0;
      ar_user   = '0;
      ar_qos    = '0;
      ar_valid  = '0;

      w_data    = '0;
      w_strb    = '0;
      w_last    = '0;
      w_user    = '0;
      w_valid   = '0;

      // constant signals
      aw_burst = 1'b0;  // incremental burst           // modified
      ar_burst = 1'b0;  // incremental burst           // modified
      aw_size  = (C_S_AXI_DATA_WIDTH == 'd64) ? 3'b011 : 3'b010; // store 8 bytes
      ar_size  = (C_S_AXI_DATA_WIDTH == 'd64) ? 3'b011 : 3'b010; // read 8 bytes
      aw_len   = 4'b0;    // single burst
      ar_len   = 4'b0;    // single burst

      b_ready = 1'b1;   // master can accept resp. information
      r_ready   = '0; // read ready. 1 master ready/ 0 master not ready

      case (state_dp)
    	idle: 
    	  begin
	        if (update)
	          state_dn = request;
	      end

        // Write/Read Address State
	    request: 
        begin
          if (axi_request) 
	      begin
	        if (loadstore)      // 1: write, 0: read
	        begin // store data
//	          aw_addr  = {axireg_i[33:4] , 2'b0};
              aw_addr  = {axireg_i[33 : (C_S_AXI_DATA_WIDTH/32 + 1 + 2)] , {(C_S_AXI_DATA_WIDTH/32 + 1){1'b0}}};
	          aw_valid = 1'b1;
		       
		      if (aw_ready)
		        state_dn = storedata;
		      else
		        state_dn = request;
	        end
	        else 
	        begin // read data
//		      ar_addr = {axireg_i[33:4] , 2'b0};
              ar_addr = {axireg_i[33 : (C_S_AXI_DATA_WIDTH/32 + 1 + 2)] , {(C_S_AXI_DATA_WIDTH/32 + 1){1'b0}}};
		      ar_valid = 1'b1;
          
              if (ar_ready)
		        state_dn = readdata;
		      else
		        state_dn = request;
	        end
	      end
	      else
	        state_dn = idle;         // nothing to send or receive
        end

        // Read Data State
        readdata: 
          begin
	        r_ready = 1'b1;

	        if (r_valid & r_last) 
	        begin
	          axireg_n[C_S_AXI_DATA_WIDTH-1 : 0]  = r_data;
	          axireg_n[(C_S_AXI_DATA_WIDTH+1):(C_S_AXI_DATA_WIDTH)] = r_resp;
	          state_dn = idle;
	        end
	        else
	          state_dn = readdata;
	      end
        
        // Write Data State 
        storedata: 
          begin
	        w_data  = axireg_i[(C_S_AXI_DATA_WIDTH+34)-1 : 34];
	        w_valid = 1'b1;
	        w_last  = 1'b1;
	        w_strb  = 8'hff;

	        if (w_ready)
	          state_dn = ack;
	        else
	          state_dn = storedata;
          end

        // Write Response State
        ack: 
          begin
	        if (b_valid)
	        begin
	          state_dn        = idle;
	          axireg_n[(C_S_AXI_DATA_WIDTH+1):(C_S_AXI_DATA_WIDTH)] = b_resp;
	        end
	        else
	          state_dn = ack;
	      end
	      
      endcase // case (state_dp)
   end

   always_ff @ (posedge aclk, negedge aresetn) 
   begin
     if (~aresetn) 
     begin
	   state_dp <= idle;
	   axireg_p <= {{2'b0}, {C_S_AXI_DATA_WIDTH{1'b0}}};
     end
     else 
     begin
	   state_dp <= state_dn;
	   axireg_p <= axireg_n;
     end
   end


endmodule // jtag_axi_wrap
