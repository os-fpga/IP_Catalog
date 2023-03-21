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

// all flops call the rvdff flop


//
`define RV_FPGA_OPTIMIZE 1
`define RV_DCCM_SIZE 64
//`define RV_DCCM_SADR 32'hf0040000
//`define RV_DCCM_EADR 32'hf004ffff
//`define RV_ICCM_SADR 32'hee000000
//`define RV_ICCM_SIZE 512
//`define ASSERT_ON 
//`define DATAWIDTH 64
//`define CLOCK_PERIOD 100
//`define RV_PIC_SIZE 32
//`define RV_PIC_BASE_ADDR 32'hf00c0000
//`define RV_BTB_BTAG_FOLD 1
`define RV_BTB_INDEX2_LO 6
`define RV_BTB_ADDR_LO 4
`define RV_BTB_INDEX3_LO 8
`define RV_BTB_INDEX2_HI 7
`define RV_BTB_BTAG_SIZE 9
`define RV_BTB_INDEX3_HI 9
`define RV_BTB_INDEX1_HI 5
`define RV_BTB_ADDR_HI 5
`define RV_BTB_INDEX1_LO 4
`define RV_BHT_ADDR_HI 7
`define RV_BHT_GHR_RANGE 4:0
`define RV_BHT_HASH_STRING {ghr[3:2] ^ {ghr[3+1], {4-1-2{1'b0} } },hashin[5:4]^ghr[2-1:0]}
`define RV_BHT_ADDR_LO 4



module rvdff #( parameter WIDTH=1 )
   (
     input logic [WIDTH-1:0] din,
     input logic           clk,
 //    input logic           en,
     input logic                   rst_l,

     output logic [WIDTH-1:0] dout
     );

`ifdef CLOCKGATE
   always @(posedge tb_top.clk) begin
      #0 $strobe("CG: %0t %m din %x dout %x clk %b width %d",$time,din,dout,clk,WIDTH);
   end
`endif

   always_ff @(posedge clk or posedge rst_l) begin    //changed by me from active low to high  negedge
      if (rst_l == 1)
        dout[WIDTH-1:0] <= 32'd0;
      else if(rst_l == 0)
        dout[WIDTH-1:0] <= din[WIDTH-1:0];
       else
       dout[WIDTH-1:0] <= dout[WIDTH-1:0];
   end


endmodule

// rvdff with 2:1 input mux to flop din iff sel==1
module rvdffs #( parameter WIDTH=1 )
   (
     input logic [WIDTH-1:0] din,
     input logic             en,
     input logic           clk,
     input logic                   rst_l,
     output logic [WIDTH-1:0] dout
     );

   //rvdff #(WIDTH) dffs (.din((en) ? din[WIDTH-1:0] : dout[WIDTH-1:0]), .*);
   rvdff #(WIDTH) dffs (.din(din), .*);

endmodule



// versions with clock enables .clken to assist in RV_FPGA_OPTIMIZE
module rvdff_fpga #( parameter WIDTH=1 )
   (
     input logic [WIDTH-1:0] din,
     input logic           clk,
     input logic           clken,
     input logic           rawclk,
     input logic           rst_l,
     input logic           scan_mode,

     output logic [WIDTH-1:0] dout
     );

`ifdef RV_FPGA_OPTIMIZE
    rvdffs #(WIDTH) dffs (.clk(rawclk), .en(clken), .*);
`else
    rvdff #(WIDTH)  dff (.*);
`endif



endmodule

// rvdff with 2:1 input mux to flop din iff sel==1
module rvdffs_fpga #( parameter WIDTH=1 )
   (
     input logic [WIDTH-1:0] din,
     input logic             en,
     input logic           clk,
     input logic           clken,
     input logic           rawclk,
     input logic           rst_l,
     input logic           scan_mode,
     output logic [WIDTH-1:0] dout
     );

`ifdef RV_FPGA_OPTIMIZE
   rvdffs #(WIDTH)   dffs (.clk(rawclk), .en(clken), .*);     //en coment by me
`else
   rvdffs #(WIDTH)   dffs (.*);
`endif

endmodule

// rvdff with en and clear
module rvdffsc_fpga #( parameter WIDTH=1 )
   (
     input logic [WIDTH-1:0] din,
     input logic             en,
     input logic             clear,
     input logic             clk,
     input logic             clken,
     input logic             rawclk,
     input logic             rst_l,
     input logic             scan_mode,
     output logic [WIDTH-1:0] dout
     );

`ifdef RV_FPGA_OPTIMIZE
   rvdffs  #(WIDTH)   dffs  (.clk(rawclk), .din(din[WIDTH-1:0] & {WIDTH{~clear}}),.en((en | clear) & clken), .*);
`else
   rvdffsc #(WIDTH)   dffsc (.*);
`endif

endmodule


`ifndef RV_FPGA_OPTIMIZE
module rvclkhdr
  (
   input  logic en,
   input  logic clk,
   input  logic scan_mode,
   output logic l1clk
   );

   logic        TE;
   assign       TE = scan_mode;

   abc clkhdr ( .*, .E(en), .CP(clk), .Q(l1clk));   //by me TEC_RV_ICG to abc

endmodule // rvclkhdr
`endif


module rvdffe #( parameter WIDTH=1, parameter OVERRIDE=0 )
   (
     input  logic [WIDTH-1:0] din,
     input  logic           en,
     input  logic           clk,
     input  logic           rst_l,
     input  logic             scan_mode,
     output logic [WIDTH-1:0] dout
     );

   logic                      l1clk;


`ifndef PHYSICAL
   if (WIDTH >= 8 || OVERRIDE==1) begin: genblock
`endif

`ifdef RV_FPGA_OPTIMIZE
      rvdffs #(WIDTH) dff ( .* );
`else
      rvclkhdr clkhdr ( .* );
      rvdff #(WIDTH) dff (.*, .clk(l1clk));
`endif

//`ifndef PHYSICAL
   end
//   else
//      $error("%m: rvdffe width must be >= 8");
//`endif


endmodule // rvdffe

// Check if the S_ADDR <= addr < E_ADDR
module rangecheck  #(parameter CCM_SADR = 32'h0, parameter CCM_SIZE  = 128) 
(
   input  logic [31:0]   addr,                             // Address to be checked for range
   output logic          in_range,                            // S_ADDR <= start_addr < E_ADDR
   output logic          in_region
);

   localparam REGION_BITS = 4;
   localparam MASK_BITS = 10 + $clog2(CCM_SIZE);

   logic [31:0]          start_addr;
   logic [3:0]           region;

   assign start_addr[31:0]        = CCM_SADR;
   assign region[REGION_BITS-1:0] = start_addr[31:(32-REGION_BITS)];

   assign in_region = (addr[31:(32-REGION_BITS)] == region[REGION_BITS-1:0]);
   if (CCM_SIZE  == 48)
    assign in_range  = (addr[31:MASK_BITS] == start_addr[31:MASK_BITS]) & ~(&addr[MASK_BITS-1 : MASK_BITS-2]);
   else
    assign in_range  = (addr[31:MASK_BITS] == start_addr[31:MASK_BITS]);

endmodule  // rvrangechecker



