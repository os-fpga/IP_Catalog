/* verilator lint_off UNUSED */
/* verilator lint_off IMPLICIT */
/* verilator lint_off DEFPARAM */
//////////////////////////////////
////                           ///   
////  axi4lite_slave.v         ///   
////                           ///   
////                           ///   
////    		        	   ///		      
////  			       		   ///           
////                           ///   
////  To Do:                   ///   
////                           ///   
////                           ///   
////  Author(s):               ///   
////                           ///   
////  Created:                 ///   
//////////////////////////////////


`define OKAY 2'b00
`define EXOKAY 2'b01
`define SLERR 2'b10
`define DECERR 2'b11

`include "./uart_defines.vh"
`include "./timescale.v"
/* verilator lint_off ASSIGNDLY */
/* verilator lint_off UNUSED */
module axi4lite_slave #(
    parameter ADDRESS_WIDTH = 5,
    parameter DATA_WIDTH    = 32,
    parameter PROT_WIDTH    = 3,
    parameter STRB_WIDTH    = (DATA_WIDTH / 8)
) (
    // Global signals
    input wire s_axi_aclk,
    input wire s_axi_aresetn,

    // write address channel
    input  wire                     s_axi_awvalid,
    input  wire [ADDRESS_WIDTH-1:0] s_axi_awaddr,
    input  wire [   PROT_WIDTH-1:0] s_axi_awprot,
    output wire                     s_axi_awready,

    // write data channel
    input  wire                  s_axi_wvalid,
    input  wire [DATA_WIDTH-1:0] s_axi_wdata,
    input  wire [STRB_WIDTH-1:0] s_axi_wstrb,
    output wire                  s_axi_wready,

    // write response channel
    output reg        s_axi_bvalid,
    output reg  [1:0] s_axi_bresp,
    input  wire       s_axi_bready,

    // read address channel
    input  wire                     s_axi_arvalid,
    input  wire [ADDRESS_WIDTH-1:0] s_axi_araddr,
    input  wire [   PROT_WIDTH-1:0] s_axi_arprot,
    output wire                     s_axi_arready,

    // read data channel
    output reg                   s_axi_rvalid,
    output reg  [DATA_WIDTH-1:0] s_axi_rdata,
    output reg  [           1:0] s_axi_rresp,
    input  wire                  s_axi_rready,

    // custom signals
    input wire [DATA_WIDTH-1:0] r_data_in_dbg,
    input wire [         8-1:0] r_data_in,

    output wire [ADDRESS_WIDTH-1:0] addr_in,
    output reg                      re,
    output reg  [              7:0] w_data_in,
    output reg                      we,
    input  wire                     tf_overrun
);

  // enable signals
  wire                     re_dbg;
  // regs
  reg  [ADDRESS_WIDTH-1:0] awaddr;
  reg [DATA_WIDTH-1:0] wdata0, wdata_ff;
  reg  [ADDRESS_WIDTH-1:0] awaddr_ff;

  wire [   DATA_WIDTH-1:0] wdata;
  reg  [ADDRESS_WIDTH-1:0] araddr;
  reg  [ADDRESS_WIDTH-1:0] araddr_ff;

  wire [   DATA_WIDTH-1:0] rdata;
  wire [              1:0] bresp;
  wire [              1:0] rresp;
  wire                     zeroOronehot;
  wire                     onebitact;
  wire                     onebitactchck;
  wire                     waddrss_cond;
  wire                     raddrss_cond;
  wire                     overrn_cond;
  reg  [   STRB_WIDTH-1:0] wstrb;
  reg  [   STRB_WIDTH-1:0] wstrb_ff;

  reg  [   PROT_WIDTH-1:0] awprot;
  reg  [   PROT_WIDTH-1:0] arprot;

  // Declare state register
  reg                      wstate;
  reg                      rstate;
  reg  [              1:0] transcond;

  // Declare states
  localparam [0:0] WRITETRNs = 0;
  localparam [0:0] WRITERESPONSE = 1;
  localparam [0:0] READADDRESS = 0;
  localparam [0:0] READDATA = 1;

  assign s_axi_awready = (transcond != 2'b11) ? 1'b1 : 1'b0;
  assign s_axi_wready = (transcond != 2'b11) ? 1'b1 : 1'b0;

  // logic to be tested
  assign zeroOronehot = ~|(wstrb_ff & (wstrb_ff - 1));
  assign onebitact = |wstrb_ff;
  assign onebitactchck = zeroOronehot & onebitact;

  assign s_axi_arready = s_axi_arvalid;

  assign addr_in = we ? awaddr_ff : araddr_ff;
  assign rdata = re_dbg ? r_data_in_dbg : {24'b0, r_data_in};
  assign re_dbg = re && (araddr == `UART_REG_DBG1) | (araddr == `UART_REG_DBG2);

  assign waddrss_cond   = (awaddr_ff == `UART_REG_TR | awaddr_ff == `UART_REG_IE | awaddr_ff == `UART_REG_LC | awaddr_ff == `UART_REG_FC |  awaddr_ff == `UART_REG_MC ) ;
  assign raddrss_cond	  = (araddr_ff == `UART_REG_DBG1 | araddr_ff == `UART_REG_DBG2 | araddr_ff == `UART_REG_RB | araddr_ff == `UART_REG_IE | araddr_ff == `UART_REG_II | araddr_ff == `UART_REG_LC | araddr_ff == `UART_REG_LS | araddr_ff == `UART_REG_MS | araddr_ff == `UART_REG_DBG  );
  assign overrn_cond = (awaddr_ff == `UART_REG_TR & tf_overrun);
  assign  bresp		  =(waddrss_cond & onebitactchck & ~overrn_cond )?`OKAY : (transcond != 2'b11)?`OKAY :`SLERR;
  assign rresp = (raddrss_cond) ? `OKAY : (rstate != READDATA) ? `OKAY : `SLERR;
  assign wdata = wdata0 | wdata_ff;

  always @(posedge s_axi_aclk or negedge s_axi_aresetn) begin
    if (!s_axi_aresetn) transcond <= 2'b0;
    else begin
    //   if (s_axi_awvalid) transcond[0] <= 1'b1;
    //   if (s_axi_wvalid) transcond[1] <= 1'b1;
      if (s_axi_bready && s_axi_bvalid) transcond <= 2'b0;
	  else transcond <=  {s_axi_wvalid,s_axi_awvalid};
  end
end
  // write fsm
  // Determine the output 	
  always @(*) begin
    case (wstate)
      WRITETRNs: begin
        if (s_axi_awvalid) begin
          awaddr = s_axi_awaddr;
          awprot = s_axi_awprot;
        end else begin
          awaddr = 'b0;
          awprot = 'b0;
        end
        if (s_axi_wvalid) begin
          wdata0 = s_axi_wdata;
          wstrb  = s_axi_wstrb;
        end else begin
          wdata0 = 'b0;
          wstrb  = 'b0;
        end
        s_axi_bvalid = 'b0;
        s_axi_bresp  = `OKAY;
        if (transcond == 2'b11) we = 'b1;
        else we = 'b0;
      end
      WRITERESPONSE: begin
        s_axi_bvalid = 'b1;
        s_axi_bresp  = bresp;
        awprot       = 'b0;
        awaddr       = 'b0;
        wdata0       = 'b0;
        we           = 'b0;
		wstrb        = wstrb_ff;
      end
      default: begin
        awaddr       = 'b0;
        wdata0       = 'b0;
        s_axi_bvalid = 'b0;
        awprot       = 'b0;
        s_axi_bresp  = `OKAY;
        we           = 'b0;
        wstrb        = 'b0;
      end
    endcase
  end

  // write fsm
  // Determine the next state
  always @(posedge s_axi_aclk or negedge s_axi_aresetn) begin
    if (!s_axi_aresetn) wstate <= WRITETRNs;
    else
      case (wstate)
        WRITETRNs:
        if (transcond == 2'b11) wstate <= #1 WRITERESPONSE;
        else wstate <= #1 WRITETRNs;
        WRITERESPONSE:
        if (s_axi_bready) wstate <= #1 WRITETRNs;
        else wstate <= #1 WRITERESPONSE;
        default: wstate <= WRITETRNs;
      endcase
  end

  always @(*) begin
    case (wstrb)
      4'b0001: w_data_in = wdata[7:0];
      4'b0010: w_data_in = wdata[15:8];
      4'b0100: w_data_in = wdata[23:16];
      4'b1000: w_data_in = wdata[31:24];
      default: w_data_in = wdata[7:0];
    endcase
  end


  always @(posedge s_axi_aclk or negedge s_axi_aresetn) begin
    if (!s_axi_aresetn) begin
      awaddr_ff <= #1'b0;
      araddr_ff <= #1'b0;
      wdata_ff  <= #1'b0;
      wstrb_ff  <= #1'b0;
    end else begin
      if (s_axi_awvalid) begin
        awaddr_ff <= #1 awaddr;
      end else if (s_axi_bready) begin
        awaddr_ff <= #1'b0;
      end
      if (s_axi_arready) araddr_ff <= #1 araddr;
      else if (s_axi_rready) araddr_ff <= #1'b0;
      if (s_axi_wvalid) begin
        wdata_ff <= #1 wdata0;
        wstrb_ff <= #1 wstrb;
      end else if (s_axi_bready) begin
        //				wdata_ff   <= #1 'b0;	
        wstrb_ff <= #1'b0;

      end

    end
  end

  // read fsm
  // Determine the output 	
  always @(*) begin
    case (rstate)
      READADDRESS: begin
        araddr       = s_axi_araddr;
        arprot       = s_axi_arprot;
        s_axi_rdata  = 'b0;
        s_axi_rvalid = 'b0;
        re           = 'b0;
        s_axi_rresp  = `OKAY;
      end
      READDATA: begin
        s_axi_rdata  = rdata;
        arprot       = 'b0;
        s_axi_rvalid = 'b1;
        s_axi_rresp  = rresp;
        re           = 'b1;
        araddr       = araddr;
      end
      default: begin
        araddr       = 'b0;
        arprot       = 'b0;
        s_axi_rdata  = 'b0;
        s_axi_rvalid = 'b0;
        re           = 'b0;
        s_axi_rresp  = `OKAY;
      end
    endcase
  end

  // read fsm
  // Determine the next state
  always @(posedge s_axi_aclk or negedge s_axi_aresetn) begin
    if (!s_axi_aresetn) rstate <= #1 READADDRESS;
    else
      case (rstate)
        READADDRESS:
        if (s_axi_arvalid) rstate <= #1 READDATA;
        else rstate <= #1 READADDRESS;
        READDATA:
        if (s_axi_rready) rstate <= #1 READADDRESS;
        else rstate <= #1 READDATA;
      endcase
  end

endmodule
