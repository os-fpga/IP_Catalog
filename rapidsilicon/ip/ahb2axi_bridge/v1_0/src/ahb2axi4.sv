// SPDX-License-Identifier: Apache-2.0
// Copyright 2019 Western Digital Corporation or its affiliates.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//********************************************************************************
// $Id$
//
// Owner:
// Function: AHB to AXI4 Bridge
// Comments:
//
//********************************************************************************


`define RV_FPGA_OPTIMIZE 1
`define RV_DCCM_SIZE 64
`define RV_DCCM_SADR 32'h76000000        //f0040000
//`define RV_DCCM_EADR 32'h7600ffff               //f004ffff
//`define RV_ICCM_SADR 32'h76000000                      //ee000000
`define RV_ICCM_SIZE 512
//`define ASSERT_ON 
//`define DATAWIDTH 64
//`define CLOCK_PERIOD 100
`define RV_PIC_SIZE 32
`define RV_PIC_BASE_ADDR 32'hf00c0000


module ahb2axi4 #(
  parameter IP_TYPE 		= "ahb2axi",
	parameter IP_VERSION 	= 32'h1, 
	parameter IP_ID 		  = 32'h2591324,
parameter id_width	    = 1,
parameter addr_width    = 32,
parameter data_width    = 32
) 


(
   input                   clk,
   input                   rst_l,

   // AXI signals
   // AXI Write Channels
   output logic            axi_awvalid,
   input  logic            axi_awready,
   output logic [id_width-1:0]  axi_awid,
   output logic [addr_width-1:0]     axi_awaddr,
   output logic [2:0]      axi_awsize,
   output logic [2:0]      axi_awprot,
   output logic [7:0]      axi_awlen,
   output logic [1:0]      axi_awburst,

   output logic            axi_wvalid,
   input  logic            axi_wready,
   output logic [data_width-1:0]     axi_wdata,
   output logic [(data_width/8)-1:0]      axi_wstrb,
   output logic            axi_wlast,

   input  logic            axi_bvalid,
   output logic            axi_bready,
   input  logic [1:0]      axi_bresp,
   input  logic [id_width-1:0]  axi_bid,

   // AXI Read Channels
   output logic            axi_arvalid,
   input  logic            axi_arready,
   output logic [id_width-1:0]  axi_arid,
   output logic [addr_width-1:0]     axi_araddr,
   output logic [2:0]      axi_arsize,
   output logic [2:0]      axi_arprot,
   output logic [7:0]      axi_arlen,
   output logic [1:0]      axi_arburst,

   input  logic            axi_rvalid,
   output logic            axi_rready,
   input  logic [id_width-1:0]  axi_rid,
   input  logic [data_width-1:0]     axi_rdata,
   input  logic [1:0]      axi_rresp,

   // AHB-Lite signals
   input logic [addr_width-1:0]      ahb_haddr,     // ahb bus address
   input logic [2:0]       ahb_hburst,   //support single,INCR,WRAP (4,8,16) 
   input logic             ahb_hmastlock, // tied to 0
   input logic [3:0]       ahb_hprot,     
   input logic [2:0]       ahb_hsize,     // size of bus transaction (possible values 0,1,2,3)
   input logic [1:0]       ahb_htrans,    
   input logic             ahb_hwrite,    // ahb bus write
   input logic [data_width-1:0]      ahb_hwdata,    // ahb bus write data
   input logic             ahb_hsel,      // this slave was selected
   input logic             ahb_hreadyin,  // previous hready was accepted or not
   
   
   input logic             ahb_hnonsec,  //  ahb signal to show secure/nonsecure transfer
   
   

   output logic [data_width-1:0]      ahb_hrdata,      // ahb bus read data
   output logic             ahb_hreadyout,   // slave ready to accept transaction
   output logic             ahb_hresp       // slave response (high indicates erro)

);

   logic [(data_width/8)-1:0]       master_wstrb;

 typedef enum logic [1:0] {   IDLE   = 2'b00,    // Nothing in the buffer. No commands yet recieved
                              WR     = 2'b01,    // Write Command recieved
                              RD     = 2'b10,    // Read Command recieved
                              PEND   = 2'b11     // Waiting on Read Data from core
                            } state_t;
   state_t      buf_state, buf_nxtstate;
   logic        buf_state_en;

   // Buffer signals (one entry buffer)
   logic                    buf_read_error_in, buf_read_error;
   logic [data_width-1:0]             buf_rdata;
   logic [data_width-1:0]             buf_rdata_enb;
   
   
   logic                    scan_mode=0;
   logic                    bus_clk_en=1;
   logic                    clk_override=0;

   logic                    ahb_hready;
   logic                    ahb_hready_q;
   logic [1:0]              ahb_htrans_in, ahb_htrans_q, ahb_htrans_qq, ahb_htrans_qqq;
   logic [2:0]              ahb_hsize_q;
   logic                    ahb_hwrite_q;
   logic [addr_width-1:0]             ahb_haddr_q;
   logic [addr_width-1:0]             ahb_haddr_qq;
   logic [data_width-1:0]             ahb_hwdata_q;
   logic                    ahb_hresp_q;

    //Miscellaneous signals
   logic                    ahb_addr_in_dccm, ahb_addr_in_iccm, ahb_addr_in_pic;
   logic                    ahb_addr_in_dccm_region_nc, ahb_addr_in_iccm_region_nc, ahb_addr_in_pic_region_nc;
   // signals needed for the read data coming back from the core and to block any further commands as AHB is a blocking bus
   logic                    buf_rdata_en;

   logic                    ahb_bus_addr_clk_en, buf_rdata_clk_en;
   logic                    ahb_clk, ahb_addr_clk, buf_rdata_clk;
   // Command buffer is the holding station where we convert to AXI
   logic                    cmdbuf_wr_en, cmdbuf_rst;
   logic                    cmdbuf_full;
   logic                    cmdbuf_vld, cmdbuf_write;
   logic [1:0]              cmdbuf_size;
   logic [(data_width/8)-1:0]              cmdbuf_wstrb;
   logic [addr_width-1:0]             cmdbuf_addr;
   logic [data_width-1:0]             cmdbuf_wdata;
   logic [data_width-1:0]             cmdbuf_wdata_q;

   logic                    bus_clk;
   
   
   logic [addr_width-1:0] addr_base;
   logic [addr_width-1:0] addr_offset;
   logic [addr_width-1:0] axi_address;
   logic axi_valid_reg;
   logic [1:0] burst_type_reg;
   logic [7:0] axi_len;
   logic address_valid;
   logic address_valid_q;
   logic [4:0] count_trans;
   
   
   ///axilen  & axiburst type calculation//
   always @ (posedge clk or posedge rst_l) begin
       if (rst_l) begin
         addr_offset       <= addr_width-1'h0;
         axi_valid_reg     <= 1'b0;
         burst_type_reg    <= 2'b00;
         
       end else begin
         case (ahb_hburst)
           3'b000: begin
             burst_type_reg    <= ahb_hburst;
             axi_len           <= 8'd0;
           end
           3'b001: begin
             burst_type_reg    <= 2'b01;
             axi_len           <= 8'd0;   
           end
           3'b010: begin
             burst_type_reg    <= 2'b10;
             axi_len           <= 8'd3;       
           end
           3'b011: begin
             burst_type_reg    <= 2'b01;
             axi_len           <= 8'd3;       
           end   
           3'b100: begin
             burst_type_reg    <= 2'b10;
             axi_len           <= 8'd7;       
           end      
           3'b101: begin
             burst_type_reg    <= 2'b01;
             axi_len           <= 8'd7;       
           end 
           3'b110: begin
             burst_type_reg    <= 2'b10;
             axi_len           <= 8'd15;       
           end  
           3'b111: begin;
             burst_type_reg    <= 2'b01;
             axi_len           <= 8'd15;       
           end              
         endcase
         end
         end
         
         
  always @ (posedge clk or posedge rst_l) begin
                if (rst_l) begin
                  addr_offset       <= addr_width-1'h0;
                  address_valid     <= 1'b0;
                  count_trans    <= 5'd0;
                  
                end 

                
                else begin
                //logic for burst length will be enabled in required/////////////
                     //       case (ahb_htrans)
//                     //                   2'b10, 2'b11: begin
//                    if(ahb_htrans == 2'b10 | ahb_htrans == 2'b11) begin
//                                        if((ahb_hburst == 2 | ahb_hburst == 3) & count_trans ==3) begin
//                                                count_trans <= 5'd0;
//                                                addr_offset       <= (ahb_haddr_q & (1 << (ahb_hsize_q)))<<2;
//                                                address_valid <= 1'b1;
//                                         end
//                            //            else begin
//                             //                   count_trans <= count_trans + 1'b1;
//                              //                  address_valid <= 1'b0;
//                               //          end
//                                        else if((ahb_hburst == 4 | ahb_hburst == 5) & count_trans ==7) begin
//                                                count_trans <= 5'd0;
//                                                addr_offset       <= (ahb_haddr_q & (1 << (ahb_hsize_q)))<<3;
//                                                address_valid <= 1'b1;
//                                         end
//                             //            else begin
//                             //                   count_trans <= count_trans + 1'b1;
//                              //                  address_valid <= 1'b0;
//                               //          end
//                                        else if((ahb_hburst == 6 | ahb_hburst == 7) & count_trans ==15) begin
//                                                count_trans <= 5'd0;
//                                                addr_offset       <= (ahb_haddr_q & (1 << (ahb_hsize_q)))<<4;
//                                                address_valid <= 1'b1;
//                                         end
//                                 //        else begin
//                                 //               count_trans <= count_trans + 1'b1;
//                                  //              address_valid <= 1'b0;
//                                  //       end
//                                        else if(ahb_hburst == 0 | ahb_hburst == 1) begin
//                                                 addr_offset <= 32'd0;
//                                         end
                                         
//                                        else begin
//                                              count_trans <= count_trans + 1'b1;
//                                              address_valid <= 1'b0;
//                                              end
////                                         else begin
////                                                 addr_offset <= addr_offset;
////                                         end              
//                                     end
//                                //     end
//                              //       2'b00: begin
//                                     else if(ahb_htrans == 0) begin
//                                             count_trans <= 5'd0;
//                                             address_valid <= address_valid;
//                                     end
////                                     2'b01: begin
//                                     else begin
//                                             count_trans <= count_trans;
//                                             address_valid <= address_valid;
//                                     end
//                          //               endcase
//                                         end
//                                         end
// ////////ends/////                                        
                                         
                   if(ahb_htrans == 2'b10)   begin
                       address_valid<=1'b1;
                   end
                   else begin
                       address_valid<=1'b0;  
                   end
                  end
                end
     
            
            
                    
                        
                        
                        
  assign axi_address = address_valid ?  (ahb_haddr_q + addr_offset) : axi_address;

// FSM to control the bus states and when to block the hready and load the command buffer
   always_comb begin
      buf_nxtstate      = IDLE;
      buf_state_en      = 1'b0;
      buf_rdata_en      = 1'b0;              // signal to load the buffer when the core sends read data back
      buf_read_error_in = 1'b0;              // signal indicating that an error came back with the read from the core
      cmdbuf_wr_en      = 1'b0;              // all clear from the gasket to load the buffer with the command for reads, command/dat for writes
      case (buf_state)
         IDLE: begin  // No commands recieved
                 // buf_nxtstate      = ahb_hwrite ? WR : RD;
                  buf_state_en      = ahb_hready & ahb_hsel;                 // only transition on a valid hrtans   
          end
         WR: begin // Write command recieved last cycle
          //        buf_nxtstate      = (ahb_hresp | (ahb_htrans[1:0] == 2'b0) | ~ahb_hsel) ? IDLE : (ahb_hwrite ? WR : RD);
                  buf_state_en      = (~cmdbuf_full | ahb_hresp) ;
                  cmdbuf_wr_en      = ~cmdbuf_full & ~(ahb_hresp | ((ahb_htrans[1:0] == 2'b01) & ahb_hsel));   // Dont send command to the buffer in case of an error or when the master is not ready with the data now.
         end
         RD: begin // Read command recieved last cycle.
            //     buf_nxtstate      = ahb_hresp ? IDLE :PEND;                                          // If error go to idle, else wait for read data PEND
                 buf_state_en      = (~cmdbuf_full | ahb_hresp);                                   // only when command can go, or if its an error
            //     cmdbuf_wr_en      = ~ahb_hresp & ~cmdbuf_full;                                    // send command only when no error
                 cmdbuf_wr_en      = ~cmdbuf_full & ~(ahb_hresp | ((ahb_htrans[1:0] == 2'b01) & ahb_hsel));                                   // send command only when no error
         end
         PEND: begin // Read Command has been sent. Waiting on Data.
                 buf_nxtstate      = IDLE;                                                          // go back for next command and present data next cycle
                 buf_state_en      = axi_rvalid & ~cmdbuf_write;                                    // read data is back
                 buf_rdata_en      = buf_state_en;                                                  // buffer the read data coming back from core
                 buf_read_error_in = buf_state_en & |axi_rresp[1:0];                                // buffer error flag if return has Error ( ECC )
         end
     endcase
   end // always_comb begin
logic data_width32_64;
assign data_width32_64 = (data_width == 64) ? 0 : 1;

   assign master_wstrb[(data_width/8)-1:0]   = data_width32_64 ? (({4{ahb_hsize_q[2:0] == 3'b0}}  & (4'b1    << ahb_haddr_q[1:0])) |
                                            ({4{ahb_hsize_q[2:0] == 3'b1}}  & (4'b11   << ahb_haddr_q[1:0])) |
                                            ({4{ahb_hsize_q[2:0] == 3'b10}}  & (4'b1111))) : (({8{ahb_hsize_q[2:0] == 3'b0}}  & (8'b1    << ahb_haddr_q[2:0])) |
                                            ({8{ahb_hsize_q[2:0] == 3'b1}}  & (8'b11   << ahb_haddr_q[2:0])) |
                                            ({8{ahb_hsize_q[2:0] == 3'b10}} & (8'b1111 << ahb_haddr_q[2:0])) |
                                            ({8{ahb_hsize_q[2:0] == 3'b11}} & 8'b1111_1111));

   assign ahb_hreadyout       = rst_l ? 1 : (ahb_hresp ? (ahb_hresp_q & ~ahb_hready_q) : ahb_hwrite ?  
                                         ((ahb_htrans == 2'b11 | ahb_htrans == 2'b10 | ahb_htrans == 2'b00 | ahb_htrans == 2'b01) & ~buf_read_error) : axi_rvalid | ahb_htrans == 2'b10 | ahb_htrans == 2'b11);    
   assign ahb_hready          = ahb_hreadyout & ahb_hreadyin;
   assign ahb_htrans_in[1:0]  = {2{ahb_hsel}} & ahb_htrans[1:0];
   assign buf_rdata_enb[data_width-1:0] = axi_rvalid ? axi_rdata : buf_rdata_enb;    //buf_rdata
   assign ahb_hrdata[data_width-1:0]    = buf_rdata_enb[data_width-1:0];
   assign ahb_hresp        = ((ahb_htrans_q[1:0] != 2'b0) & (buf_state != IDLE)  &
                             ((~(ahb_addr_in_dccm | ahb_addr_in_iccm)) |                                                                                   // request not for ICCM or DCCM
                             ((ahb_addr_in_iccm | (ahb_addr_in_dccm &  ahb_hwrite_q)) & ~((ahb_hsize_q[1:0] == 2'b10) | (ahb_hsize_q[1:0] == 2'b11))) |    // ICCM Rd/Wr OR DCCM Wr not the right size
                             ((ahb_hsize_q[2:0] == 3'h1) & ahb_haddr_q[0])   |                                                                             // HW size but unaligned
                             ((ahb_hsize_q[2:0] == 3'h2) & (|ahb_haddr_q[1:0])) |                                                                          // W size but unaligned
                             ((ahb_hsize_q[2:0] == 3'h3) & (|ahb_haddr_q[2:0])))) |                                                                        // DW size but unaligned
                             (buf_read_error);      // |                                                                                                      // Read ECC error       



   // All the Master signals are captured before presenting it to the command buffer. We check for Hresp before sending it to the cmd buffer.
   rvdff_fpga  #(.WIDTH(1))    Address_valid_ff  (.din(address_valid),          .dout(address_valid_q),       .clk(ahb_clk),      .clken(bus_clk_en), .rawclk(clk), .*);
   rvdff_fpga  #(.WIDTH(1))    hresp_ff  (.din(ahb_hresp),          .dout(ahb_hresp_q),       .clk(ahb_clk),      .clken(bus_clk_en), .rawclk(clk), .*);
   rvdff_fpga  #(.WIDTH(1))    hready_ff (.din(ahb_hready),         .dout(ahb_hready_q),      .clk(ahb_clk),      .clken(bus_clk_en), .rawclk(clk), .*);
   rvdff_fpga  #(.WIDTH(2))    htrans_ff (.din(ahb_htrans_in[1:0]), .dout(ahb_htrans_q[1:0]), .clk(ahb_clk),      .clken(bus_clk_en), .rawclk(clk), .*);
   rvdff_fpga  #(.WIDTH(2))    htrans_ff_ff (.din(ahb_htrans_q[1:0]), .dout(ahb_htrans_qq[1:0]), .clk(ahb_clk),      .clken(bus_clk_en), .rawclk(clk), .*); 
   rvdff_fpga  #(.WIDTH(2))    htrans_ff_ff_ff(.din(ahb_htrans_qq[1:0]), .dout(ahb_htrans_qqq[1:0]), .clk(ahb_clk),      .clken(bus_clk_en), .rawclk(clk), .*);
   rvdff_fpga  #(.WIDTH(3))    hsize_ff  (.din(ahb_hsize[2:0]),     .dout(ahb_hsize_q[2:0]),  .clk(ahb_addr_clk), .clken(ahb_bus_addr_clk_en), .rawclk(clk), .*);   //ahb_bus_addr_clk_en
   rvdff_fpga  #(.WIDTH(1))    hwrite_ff (.din(ahb_hwrite),         .dout(ahb_hwrite_q),      .clk(ahb_addr_clk), .clken(ahb_bus_addr_clk_en), .rawclk(clk), .*);   //ahb_bus_addr_clk_en
   rvdff_fpga  #(.WIDTH(addr_width))   haddr_ff  (.din(ahb_haddr[addr_width-1:0]),    .dout(ahb_haddr_q[addr_width-1:0]), .clk(ahb_addr_clk), .clken(ahb_bus_addr_clk_en), .rawclk(clk), .*);   //ahb_bus_addr_clk_en
   rvdffs_fpga #($bits(state_t)) state_reg (.din(buf_nxtstate),     .dout({buf_state}), .en(buf_state_en), .clk(ahb_clk), .clken(bus_clk_en),  .rawclk(clk), .*);
   rvdff_fpga  #(.WIDTH(data_width)) buf_rdata_ff  (.din(axi_rdata[data_width-1:0]),  .dout(buf_rdata[data_width-1:0]),   .clk(buf_rdata_clk), .clken(buf_rdata_clk_en),   .rawclk(clk), .*);   //buf_rdata_clk_en
   rvdff_fpga  #(.WIDTH(1))  buf_read_error_ff(.din(buf_read_error_in),  .dout(buf_read_error),.clk(ahb_clk),       .clken(bus_clk_en),        .rawclk(clk), .*);

   // Clock header logic
   assign ahb_bus_addr_clk_en = bus_clk_en & (ahb_htrans[1]);
   assign buf_rdata_clk_en    = bus_clk_en & buf_rdata_en;

`ifdef RV_FPGA_OPTIMIZE
   assign ahb_clk = 1'b0;
   assign ahb_addr_clk = 1'b0;
   assign buf_rdata_clk = 1'b0;
   assign bus_clk = 1'b0;
`else
   rvclkhdr ahb_cgc       (.en(bus_clk_en),          .l1clk(ahb_clk),       .*);  // ifndef FPGA_OPTIMIZE
   rvclkhdr ahb_addr_cgc  (.en(ahb_bus_addr_clk_en), .l1clk(ahb_addr_clk),  .*);  // ifndef FPGA_OPTIMIZE
   rvclkhdr buf_rdata_cgc (.en(buf_rdata_clk_en),    .l1clk(buf_rdata_clk), .*);  // ifndef FPGA_OPTIMIZE
   rvclkhdr bus_cgc        (.en(bus_clk_en),       .l1clk(bus_clk),       .*);    // ifndef FPGA_OPTIMIZE
`endif

   // Address check  dccm
   rangecheck #(.CCM_SADR(`RV_DCCM_SADR),
                  .CCM_SIZE(`RV_DCCM_SIZE)) addr_dccm_rangecheck (
      .addr(ahb_haddr_q[addr_width-1:0]),
      .in_range(ahb_addr_in_dccm),
      .in_region(ahb_addr_in_dccm_region_nc)
   );

   // Address check  iccm
`ifdef RV_ICCM_ENABLE
   rangecheck #(.CCM_SADR(`RV_ICCM_SADR),
                  .CCM_SIZE(`RV_ICCM_SIZE)) addr_iccm_rangecheck (
      .addr(ahb_haddr_q[addr_width-1:0]),
      .in_range(ahb_addr_in_iccm),
      .in_region(ahb_addr_in_iccm_region_nc)
   );
`else
   assign ahb_addr_in_iccm = '0;
   assign ahb_addr_in_iccm_region_nc = '0;
`endif

   // PIC memory address check
 //  rangecheck #(.CCM_SADR(`RV_PIC_BASE_ADDR),
 //                 .CCM_SIZE(`RV_PIC_SIZE)) addr_pic_rangecheck (
 //     .addr(ahb_haddr_q[addr_width-1:0]),
 //     .in_range(ahb_addr_in_pic),
 //     .in_region(ahb_addr_in_pic_region_nc)
 //  );/

   // Command Buffer - Holding for the commands to be sent for the AXI. It will be converted to the AXI signals.
   assign cmdbuf_rst         = (((axi_arvalid & axi_arready)) & ~cmdbuf_wr_en) | (ahb_hresp & ~cmdbuf_write);
   assign cmdbuf_full        = (cmdbuf_vld & ~((axi_awvalid & axi_awready) | (axi_arvalid & axi_arready)));

   rvdffsc_fpga #(.WIDTH(1))   cmdbuf_vldff      (.din(1'b1), .clear(cmdbuf_rst), .dout(cmdbuf_vld),        .en(cmdbuf_wr_en), .clk(bus_clk), .clken(bus_clk_en), .rawclk(clk), .*);
   rvdffs_fpga  #(.WIDTH(1))   cmdbuf_writeff    (.din(ahb_hwrite_q),             .dout(cmdbuf_write),      .en(cmdbuf_wr_en), .clk(bus_clk), .clken(bus_clk_en), .rawclk(clk), .*);
   rvdffs_fpga  #(.WIDTH(2))   cmdbuf_sizeff     (.din(ahb_hsize_q[1:0]),         .dout(cmdbuf_size[1:0]),  .en(cmdbuf_wr_en), .clk(bus_clk), .clken(bus_clk_en), .rawclk(clk), .*);
   rvdffs_fpga  #(.WIDTH((data_width/8)))   cmdbuf_wstrbff    (.din(master_wstrb[(data_width/8)-1:0]),        .dout(cmdbuf_wstrb[(data_width/8)-1:0]), .en(cmdbuf_wr_en), .clk(bus_clk), .clken(bus_clk_en), .rawclk(clk), .*);

// REVIEW : was 2 clock headers

//   rvdffe  #(.WIDTH(32))  cmdbuf_addrff     (.din(ahb_haddr_q[31:0]),   .dout(cmdbuf_addr[31:0]),   .en(cmdbuf_wr_en),   .clk(bus_clk), .*);
//   rvdffe  #(.WIDTH(64))  cmdbuf_wdataff    (.din(ahb_hwdata[63:0]),    .dout(cmdbuf_wdata[63:0]),  .en(cmdbuf_wr_en),   .clk(bus_clk), .*);

   rvdffe  #(.WIDTH(addr_width))  cmdbuf_addrff     (.din(ahb_haddr_q[addr_width-1:0]),   .dout(cmdbuf_addr[addr_width-1:0]),   .en(cmdbuf_wr_en & bus_clk_en), .*);
   rvdffe  #(.WIDTH(data_width))  cmdbuf_wdataff    (.din(ahb_hwdata[data_width-1:0]),    .dout(cmdbuf_wdata[data_width-1:0]),  .en(cmdbuf_wr_en & bus_clk_en), .*);
   rvdffe  #(.WIDTH(data_width))  cmdbuf_wdataff_ff    (.din(cmdbuf_wdata[data_width-1:0]),    .dout(cmdbuf_wdata_q[data_width-1:0]),  .en(cmdbuf_wr_en & bus_clk_en), .*);


   // AXI Write Command Channel
   assign axi_awvalid           = address_valid & ahb_hwrite_q | (axi_awready & address_valid_q);
   assign axi_awid[id_width-1:0]     = '0; 
   assign axi_awaddr[addr_width-1:0]      = address_valid_q ? cmdbuf_addr[addr_width-1:0]: axi_awaddr[addr_width-1:0];
   assign axi_awsize[2:0]       = {1'b0, cmdbuf_size[1:0]};
   assign axi_awprot[2:0]       = {~(ahb_hprot[0]),ahb_hnonsec,ahb_hprot[1]};
   assign axi_awlen[7:0]        = axi_len[7:0];
   assign axi_awburst[1:0]      = burst_type_reg;
   // AXI Write Data Channel - This is tied to the command channel as we only write the command buffer once we have the data.
   assign axi_wvalid            = cmdbuf_vld & cmdbuf_write & (ahb_htrans_qq == 2'b10 | ahb_htrans_qq == 2'b11 | axi_wlast);
   assign axi_wdata[data_width-1:0]       = cmdbuf_wdata[data_width-1:0];
   assign axi_wstrb[(data_width/8)-1:0]        = cmdbuf_wstrb[(data_width/8)-1:0];
   assign axi_wlast             = ~(ahb_hburst == 3'b0 | ahb_hburst == 3'b1) ? (ahb_htrans_qq == 2'b00 & (~ahb_htrans_qqq == 2'b00) & cmdbuf_write) : 1'b1;   //ahb_htrans == 2'b00 & 
  // AXI Write Response - Always ready. AHB does not require a write response.
   assign axi_bready            = 1'b1;
   // AXI Read Channels
   assign axi_arvalid           = address_valid & ~ahb_hwrite_q;
   assign axi_arid[id_width-1:0]     = '0;
   assign axi_araddr[addr_width-1:0]      = address_valid_q ? cmdbuf_addr[addr_width-1:0]: axi_awaddr[addr_width-1:0];
   assign axi_arsize[2:0]       = {1'b0, cmdbuf_size[1:0]};
   assign axi_arprot            = 3'b0;
   assign axi_arlen[7:0]        = axi_len[7:0];      
   assign axi_arburst[1:0]      = burst_type_reg;   
   // AXI Read Response Channel - Always ready as AHB reads are blocking and the the buffer is available for the read coming back always.
   assign axi_rready            = 1'b1;

   // Clock header logic

`ifdef ASSERT_ON
   property ahb_error_protocol;
      @(posedge ahb_clk) (ahb_hready & ahb_hresp) |-> (~$past(ahb_hready) & $past(ahb_hresp));
   endproperty
   assert_ahb_error_protocol: assert property (ahb_error_protocol) else
      $display("Bus Error with hReady isn't preceded with Bus Error without hready");

`endif




endmodule // ahb_to_axi4
