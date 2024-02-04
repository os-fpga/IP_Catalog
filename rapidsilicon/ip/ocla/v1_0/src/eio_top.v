//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer: Fawad Ahmad
//
// Create Date: 11/29/2022 03:59:03 PM
// Design Name: Emulate-IO
// Module Name: eio_top
// Project Name: Soft IP Development
// Target Devices: Gemini
// Tool Versions: Raptor
// Description: This IP emulates inputs and outputs ports that can be used in FPGA design without actually consuming on-chip IO pins.
//
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments: In progress.
//
//////////////////////////////////////////////////////////////////////////////////
 
module eio_top #
(
parameter IP_TYPE    = "EIO",
parameter IP_VERSION   = 32'h1,
parameter IP_ID    = 32'h2591655,
 
// AXI-L related parameters
parameter integer C_S_AXI_DATA_WIDTH = 32,
parameter integer C_S_AXI_ADDR_WIDTH    = 32,
// width of in and out probes (max 512 probes each)
parameter integer INPUT_PROBE_WIDTH     = 100,
parameter integer OUTPUT_PROBE_WIDTH    = 100,
// whether the in/out clocks are synced with AXI clock or not
parameter AXI_IN_CLOCKS_SYNCED          = 0,
parameter AXI_OUT_CLOCKS_SYNCED         = 0
)
(
// Design clock
input wire  IP_CLK,
input wire  OP_CLK,
 
// AXIL clock and reset
input wire  S_AXI_ACLK,
input wire  S_AXI_ARESETN,
 
// AXIL write address channel
input  wire     [16-1 : 0] S_AXI_AWADDR,
input  wire                        [2 : 0] S_AXI_AWPROT,
input  wire                                S_AXI_AWVALID,
output wire                                S_AXI_AWREADY,
// AXIL write data channel
input  wire     [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_WDATA,
input  wire [(C_S_AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
input  wire                                S_AXI_WVALID,
output wire                                S_AXI_WREADY,
// AXIL write response channel
output wire                        [1 : 0] S_AXI_BRESP,
output wire                                S_AXI_BVALID,
input  wire                                S_AXI_BREADY,
// AXIL read address channel
input  wire     [16-1 : 0] S_AXI_ARADDR,
input  wire                        [2 : 0] S_AXI_ARPROT,
input  wire                                S_AXI_ARVALID,
output wire                                S_AXI_ARREADY,
// AXIL read data channel
output wire     [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_RDATA,
output wire                        [1 : 0] S_AXI_RRESP,
output wire                                S_AXI_RVALID,
input  wire                                S_AXI_RREADY,
 
// input and output probes
input       [INPUT_PROBE_WIDTH-1 : 0] probe_in,
output     [OUTPUT_PROBE_WIDTH-1 : 0] probe_out
);
 
// paramters           
localparam  NO_OF_IN_PROBE_REGS = (INPUT_PROBE_WIDTH)/C_S_AXI_DATA_WIDTH + ((INPUT_PROBE_WIDTH % C_S_AXI_DATA_WIDTH) != 0);
localparam NO_OF_OUT_PROBE_REGS = (OUTPUT_PROBE_WIDTH)/C_S_AXI_DATA_WIDTH + ((OUTPUT_PROBE_WIDTH % C_S_AXI_DATA_WIDTH) != 0);    
localparam             ADDR_LSB = (C_S_AXI_DATA_WIDTH/32) + 1;
localparam  ADDR_MSB = $clog2(NO_OF_IN_PROBE_REGS) + 2 ; //Added 2 for catering IP type, name version registers
localparam  spare_input_probes = (INPUT_PROBE_WIDTH % C_S_AXI_DATA_WIDTH)  == 0 ? C_S_AXI_DATA_WIDTH : INPUT_PROBE_WIDTH % C_S_AXI_DATA_WIDTH;
localparam  spare_output_probes = OUTPUT_PROBE_WIDTH % C_S_AXI_DATA_WIDTH;
localparam  output_probe_addr_width = $clog2(NO_OF_OUT_PROBE_REGS)  ;
 
// calculation for no. of registers
reg  [C_S_AXI_DATA_WIDTH-1 : 0]  input_probe_reg_i [NO_OF_IN_PROBE_REGS-1 : 0];     // 32/64-bit input registers
reg  [C_S_AXI_DATA_WIDTH-1 : 0]  input_probe_reg_o [NO_OF_IN_PROBE_REGS-1 : 0];   
reg  [C_S_AXI_DATA_WIDTH-1 : 0]  output_probe_reg [NO_OF_OUT_PROBE_REGS-1 : 0];    // 32/64-bit output registers
wire [INPUT_PROBE_WIDTH-1 : 0]  probe_in_tmp;
 
// AXIL-S interal signals
wire                             AXI_WREN;
wire                             AXI_RDEN;
reg   [C_S_AXI_DATA_WIDTH-1 : 0] AXI_DAT_IN = {C_S_AXI_DATA_WIDTH{1'b0}};
reg   [C_S_AXI_DATA_WIDTH-1 : 0] CONTROL_REG;
 
reg [C_S_AXI_DATA_WIDTH-1 : 0] ip_type    = IP_TYPE;      // 0x4
reg [C_S_AXI_DATA_WIDTH-1 : 0] ip_version = IP_VERSION;   // 0x8
reg [C_S_AXI_DATA_WIDTH-1 : 0] ip_id      = IP_ID;        // 0xC
reg [output_probe_addr_width-1:0] output_probe_addr;
 
integer strb_index = 0;
integer probe_index;
integer t_index;
 
/**********************************************************************************
*                                                                                 *
*   AXI-Slave instantiation                                                       *
*                                                                                 *
**********************************************************************************/
axil_slave # (
   .C_S_AXI_DATA_WIDTH   (C_S_AXI_DATA_WIDTH),
   .C_S_AXI_ADDR_WIDTH   (16),
   .NO_OF_IN_PROBE_REGS  (NO_OF_IN_PROBE_REGS),
   .NO_OF_OUT_PROBE_REGS (NO_OF_OUT_PROBE_REGS)
  )
  EIO_AXIL_INTF
  (
   // AXIL clock and reset
   .S_AXI_ACLK     (S_AXI_ACLK),
   .S_AXI_ARESETN  (S_AXI_ARESETN),
  
   // AXIL write address channel
   .S_AXI_AWADDR   (S_AXI_AWADDR),
   .S_AXI_AWPROT   (S_AXI_AWPROT),
   .S_AXI_AWVALID  (S_AXI_AWVALID),
   .S_AXI_AWREADY  (S_AXI_AWREADY),
   // AXIL write data channel
   .S_AXI_WDATA    (S_AXI_WDATA),
   .S_AXI_WSTRB    (S_AXI_WSTRB),
   .S_AXI_WVALID   (S_AXI_WVALID),
   .S_AXI_WREADY   (S_AXI_WREADY),
   // AXIL write response channel
   .S_AXI_BRESP    (S_AXI_BRESP),
   .S_AXI_BVALID   (S_AXI_BVALID),
   .S_AXI_BREADY   (S_AXI_BREADY),
   // AXIL read address channel
   .S_AXI_ARADDR   (S_AXI_ARADDR),
   .S_AXI_ARPROT   (S_AXI_ARPROT),
   .S_AXI_ARVALID  (S_AXI_ARVALID),
   .S_AXI_ARREADY  (S_AXI_ARREADY),
   // AXIL read data channel
   .S_AXI_RDATA    (S_AXI_RDATA),
   .S_AXI_RRESP    (S_AXI_RRESP),
   .S_AXI_RVALID   (S_AXI_RVALID),
   .S_AXI_RREADY   (S_AXI_RREADY),
   
   .AXI_WREN       (AXI_WREN),
   .AXI_RDEN       (AXI_RDEN),
   .AXI_DAT_IN     (AXI_DAT_IN)
  );
  
/**********************************************************************************
*                                                                                 *
*   Synchronizers                                                                 *
*                                                                                 *
**********************************************************************************/    
// ------------ outputs ------------
genvar odfs_index;
generate
for (odfs_index = 0 ; odfs_index < NO_OF_OUT_PROBE_REGS ; odfs_index = odfs_index+1)
begin
if (odfs_index == (NO_OF_OUT_PROBE_REGS-1) && (spare_output_probes != 0))
begin
 
ff_sync_eio #
(
  .DATA_SIZE (spare_output_probes),
  .SYNC      (!AXI_OUT_CLOCKS_SYNCED)
)
  out_probe_synchronizer
(
  .destination_clk  (OP_CLK),
  .destination_rstn (S_AXI_ARESETN),                                    
  .async_data_in    (output_probe_reg[odfs_index][spare_output_probes-1 : 0]),
  .sync_data_out    (probe_out[odfs_index*C_S_AXI_DATA_WIDTH +: spare_output_probes])
);
end
else
begin
ff_sync_eio #
(
  .DATA_SIZE (C_S_AXI_DATA_WIDTH),
  .SYNC      (!AXI_OUT_CLOCKS_SYNCED)
)
  out_probe_synchronizer
(
  .destination_clk  (OP_CLK),
  .destination_rstn (S_AXI_ARESETN),                                    
  .async_data_in    (output_probe_reg[odfs_index]),
  .sync_data_out    (probe_out[odfs_index*C_S_AXI_DATA_WIDTH +: C_S_AXI_DATA_WIDTH])
);
end
end
endgenerate
 
// ----------- inputs ------------
genvar idfs_index;
generate
for (idfs_index = 0 ; idfs_index < NO_OF_IN_PROBE_REGS ; idfs_index = idfs_index+1)
begin
if (idfs_index == (NO_OF_IN_PROBE_REGS-1) && (spare_input_probes != 0))
begin
ff_sync_eio #
(
  .DATA_SIZE (spare_input_probes),
  .SYNC      (!AXI_IN_CLOCKS_SYNCED)
)
  in_probe_synchronizer
(
  .destination_clk  (S_AXI_ACLK),
  .destination_rstn (S_AXI_ARESETN),                                    
  .async_data_in    (input_probe_reg_i[idfs_index][spare_input_probes-1 : 0]),
  .sync_data_out    (probe_in_tmp[idfs_index*C_S_AXI_DATA_WIDTH +: spare_input_probes])
);                
end
else
begin
ff_sync_eio #
(
  .DATA_SIZE (C_S_AXI_DATA_WIDTH),
  .SYNC      (!AXI_IN_CLOCKS_SYNCED)
)
  in_probe_synchronizer
(
  .destination_clk  (S_AXI_ACLK),
  .destination_rstn (S_AXI_ARESETN),                                    
  .async_data_in    (input_probe_reg_i[idfs_index]),
  .sync_data_out    (probe_in_tmp[idfs_index*C_S_AXI_DATA_WIDTH +: C_S_AXI_DATA_WIDTH])
);
end
end
endgenerate
 
/**********************************************************************************
*                                                                                 *
*   Reading registers through AXI                                                 *
*                                                                                 *
**********************************************************************************/
 
always @ (*)
begin
    case (S_AXI_ARADDR[(ADDR_LSB+ADDR_MSB) : ADDR_LSB])
        2'h0    :   AXI_DAT_IN <= CONTROL_REG;   
        2'h1    :   AXI_DAT_IN <= ip_type;
        2'h2    :   AXI_DAT_IN <= ip_version;
        2'h3    :   AXI_DAT_IN <= ip_id;
        default :  begin
         AXI_DAT_IN <= input_probe_reg_o[((S_AXI_ARADDR - 32'h00000010) >> ADDR_LSB)];     
        end
    endcase
end
 
/**********************************************************************************
*                                                                                 *
*   Writing registers through AXI                                                 *
*                                                                                 *
**********************************************************************************/
        
 
always @( posedge S_AXI_ACLK or negedge S_AXI_ARESETN )
begin
  if (!S_AXI_ARESETN)
    begin
      CONTROL_REG <= 0;
    end
  else begin
    if (AXI_WREN)
      begin
        case ( S_AXI_AWADDR[ADDR_LSB + ADDR_MSB:ADDR_LSB] )
          2'h0:
                for (strb_index = 0 ; strb_index <= (C_S_AXI_DATA_WIDTH/8)-1 ; strb_index = strb_index+1)
                begin
                    if (S_AXI_WSTRB[strb_index] == 1)
                        CONTROL_REG[(strb_index*8) +: 8] <= S_AXI_WDATA[(strb_index*8) +: 8];
                end
         2'h1: ip_type = ip_type;
         2'h2: ip_version = ip_version;
         2'h3: ip_id = ip_id;
          default : begin
            output_probe_addr = (S_AXI_AWADDR - 32'h10) >> ADDR_LSB;
             for (strb_index = 0 ; strb_index <= (C_S_AXI_DATA_WIDTH/8)-1 ; strb_index = strb_index+1)
                begin
                     if (S_AXI_WSTRB[strb_index] == 1)
                         output_probe_reg[((output_probe_addr[output_probe_addr_width-1 : 0]))][(strb_index*8) +: 8] <= S_AXI_WDATA[(strb_index*8) +: 8];
                end end
        endcase
      end
  end
end    
 
 
 
 
 
/**********************************************************************************
*                                                                                 *
*   Sampling inputs non-stop on input-clock                                       *
*                                                                                 *
**********************************************************************************/    
always @ (posedge IP_CLK or negedge S_AXI_ARESETN)
begin
if(!S_AXI_ARESETN)
begin
for (probe_index = 0 ; probe_index <= NO_OF_IN_PROBE_REGS-1 ; probe_index = probe_index+1)
input_probe_reg_i[probe_index] <= {C_S_AXI_DATA_WIDTH{1'b0}};
end
else
begin
for (probe_index = 0 ; probe_index <= NO_OF_IN_PROBE_REGS-1 ; probe_index = probe_index+1)
begin
if (probe_index == (NO_OF_IN_PROBE_REGS-1))
     input_probe_reg_i[probe_index] <= probe_in[(probe_index*C_S_AXI_DATA_WIDTH) +: spare_input_probes]; // here
else
     input_probe_reg_i[probe_index] <= probe_in[(probe_index*C_S_AXI_DATA_WIDTH) +: C_S_AXI_DATA_WIDTH];
end
end
end
 
/**********************************************************************************
*                                                                                 *
*   Syncing and copying inputs to AXI memory mapped registers                     *
*                                                                                 *
**********************************************************************************/    
always @ (posedge S_AXI_ACLK or negedge S_AXI_ARESETN)
begin
if(!S_AXI_ARESETN)
begin                
for (probe_index = 0 ; probe_index <= NO_OF_IN_PROBE_REGS-1 ; probe_index = probe_index+1)
input_probe_reg_o[probe_index]  <= {C_S_AXI_DATA_WIDTH{1'b0}};
end
else
begin
for (probe_index = 0 ; probe_index <= NO_OF_IN_PROBE_REGS-1 ; probe_index = probe_index+1)
begin
if (probe_index == (NO_OF_IN_PROBE_REGS-1))
     input_probe_reg_o[probe_index]  <= probe_in_tmp[(probe_index*C_S_AXI_DATA_WIDTH) +: spare_input_probes]; // here
else
     input_probe_reg_o[probe_index]  <= probe_in_tmp[(probe_index*C_S_AXI_DATA_WIDTH) +: C_S_AXI_DATA_WIDTH];            
end
end
end
 
endmodule
 