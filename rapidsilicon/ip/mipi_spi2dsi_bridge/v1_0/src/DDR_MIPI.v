/* 
 * File:   tb_spi_bridge.v
 * Copyright:  Gaurav Singh
 * website: www.circuitvalley.com 
 * Created on Jan 19, 2020, 1:33 AM
 *	This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *	(at your option) any later version.
 *	This program is distributed in the hope that it will be useful,
 *	but WITHOUT ANY WARRANTY; without even the implied warranty of
 *	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *	GNU General Public License for more details.
 *	You should have received a copy of the GNU General Public License
 *	along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *	Email: gauravsingh@circuitvalley.com
************************************************************************/

`timescale 1 ns / 1 ps
module DDR_MIPI (clkout_lp0_i, buf_clkout_lp0_o,
				clkout_lp1_i, buf_clkout_lp1_o, 
				clock_slow_i, clockp_fast_data_i, 
				clocks_fast_clk_i, mipi_clock_o, 
				lock_chk_i, reset_i, byte_clock_o, 
				tristate_data_i,tristate_clk_i, tx_ready_o, 
				buf_dout_lp0_o, dout_lp0_i, 
				buf_dout_lp1_o, dout_lp1_i, 
				data_i, mipi_data_o,mipi_data_n)
	/* synthesis NGD_DRC_MASK=1 */;
    
	input wire clkout_lp0_i;			//lp link for mipi clkp
    input wire clkout_lp1_i;			//lp line for mipi clkn
    input wire clock_slow_i;			// slow clock for sync
    input wire clockp_fast_data_i;		//fast clokc input for mipi data
    input wire clocks_fast_clk_i;		//fast clock input for mipi clok
    input wire lock_chk_i;				//clock check
    input wire reset_i;					//reset active high
    input wire tristate_data_i;			//controls HS pin tristate active high
	input wire tristate_clk_i;		//controls HS pin tristate active high
    input wire dout_lp0_i;				//lp line mipi datap


    input wire dout_lp1_i;				//lp line mipi datan
    input wire [7:0] data_i;			//mipi data input
    output wire buf_clkout_lp0_o;		//mipi clock lp0 out
    output wire buf_clkout_lp1_o;		//mipi clock lp1 out
    output wire mipi_clock_o;			//mipi clock out	
    output wire byte_clock_o;			//ddr byte clock output
    output wire tx_ready_o;				//After reset,  Indicate completion of reset synchronization
    output wire [0:0] buf_dout_lp0_o;  //data lp0 out
    output wire [0:0] buf_dout_lp1_o;	//data lp1 out
    output wire [0:0] mipi_data_o, mipi_data_n;		//mipi data out


    reg opensync_0;
    reg opensync_1;
    reg opensync_cken;
    reg opensync_2;
    reg buf_clkout;
    wire scuba_vhi;
    wire d70;
    wire d60;
    wire d50;
    wire d40;
    wire d30;
    wire d20;
    wire d10;
    wire d00;
    wire eclkc;
    wire sclk_t, sclk_t2;
    wire cdiv1, cdiv12;
    wire scuba_vlo;
    wire eclkd;
    reg xstop;
    wire xstart;
    reg opensync_3;
    reg tristate_data_o;
    reg tristate_clock_o;
    wire buf_douto0, buf_serdes_out;
    wire [7:0] reversed_data;

//    defparam LUT4_1.initval =  16'h0a78 ;
//    ROM16X1A LUT4_1 (.AD3(opensync_0), .AD2(opensync_3), .AD1(lock_chk_i), 
//        .AD0(scuba_vhi), .DO0(opensync_cken));
//
//    defparam LUT4_0.initval =  16'hfffe ;
//    ROM16X1A LUT4_0 (.AD3(opensync_0), .AD2(opensync_1), .AD1(scuba_vlo), 
//        .AD0(scuba_vlo), .DO0(xstop));
//
//    FD1P3BX FF_3 (.D(opensync_3), .SP(opensync_cken), .CK(clock_slow_i), .PD(reset_i), 
//        .Q(opensync_0))
             /* synthesis GSR="ENABLED" */;


//ROM16x1 Lut 4.0eplacement
  reg [0:15] memory = 16'h0a78; // Example initialization
  wire [3:0] address_l;

   assign address_l = {scuba_vhi, lock_chk_i ,opensync_3 , opensync_0};

  always @* begin
        opensync_cken = memory[address_l];
  end
//ROM16x1 Lut4.1replacement
  reg [0:15] memory1 = 16'hfffe; // Example initialization
  wire [3:0] address_l1;

   assign address_l1 = {scuba_vlo, scuba_vlo ,opensync_1 , opensync_0};

  always @* begin
        xstop = memory[address_l];
  end



    always @(posedge clock_slow_i or posedge reset_i) begin
    if (reset_i) begin
      // Asynchronous reset: Clear the output when reset is active
      opensync_0 <= 1'b1;
      opensync_1 <= 1'b0;
      opensync_2 <= 1'b0;
      opensync_3 <= 1'b0;
    end else if (opensync_cken) begin
      // Clock enable condition
      // Update the output on the positive edge of the clock if clk_enable is active
      opensync_0 <= opensync_3;
      opensync_1 <= opensync_0;
      opensync_2 <= opensync_1;
      opensync_3 <= opensync_2;
    end else begin
      opensync_0 <= opensync_0;
      opensync_1 <= opensync_1;
      opensync_2 <= opensync_2;
      opensync_3 <= opensync_3;
    end
    end


//OFS1P3DX Inst 8
    always @(posedge sclk_t or posedge reset_i) begin
    if (reset_i) begin
      // Asynchronous reset: Clear the output when reset is active
      tristate_clock_o <= 1'b0;
      tristate_data_o <= 1'b0;
    end else if (scuba_vhi) begin
      // Clock enable condition
      // Update the output on the positive edge of the clock if clk_enable is active
      tristate_clock_o <= tristate_clk_i;
      tristate_data_o <= tristate_data_i;end
      else begin
      tristate_clock_o <= tristate_clock_o;
      tristate_data_o <= tristate_data_o; end
    end



//    FD1P3DX FF_2 (.D(opensync_0), .SP(opensync_cken), .CK(clock_slow_i), .CD(reset_i), 
//        .Q(opensync_1))
//             /* synthesis GSR="ENABLED" */;
//
//    FD1P3DX FF_1 (.D(opensync_1), .SP(opensync_cken), .CK(clock_slow_i), .CD(reset_i), 
//        .Q(opensync_2))
//             /* synthesis GSR="ENABLED" */;
//
//    FD1P3DX FF_0 (.D(opensync_2), .SP(opensync_cken), .CK(clock_slow_i), .CD(reset_i), 
//        .Q(opensync_3))
             /* synthesis GSR="ENABLED" */;

//    OB Inst1_OB (.I(clkout_lp1_i), .O(buf_clkout_lp1_o));
//    OB Inst2_OB (.I(clkout_lp0_i), .O(buf_clkout_lp0_o));
//    OB Inst3_OB (.I(dout_lp1_i), .O(buf_dout_lp1_o));
//    OB Inst4_OB (.I(dout_lp0_i), .O(buf_dout_lp0_o));
//

    assign buf_clkout_lp1_o = clkout_lp1_i;
    assign buf_clkout_lp0_o = clkout_lp0_i;
    assign buf_dout_lp1_o = dout_lp1_i;
    assign buf_dout_lp0_o = dout_lp0_i;


//    OFS1P3DX Inst8_OFS1P3DX (.D(tristate_clk_i), .SP(scuba_vhi), .SCLK(sclk_t), 
//        .CD(reset_i), .Q(tristate_clock_o));
//
//    OFS1P3DX Inst9_OFS1P3DX (.D(tristate_data_i), .SP(scuba_vhi), .SCLK(sclk_t), 
//        .CD(reset_i), .Q(tristate_data_o));
		
//    OBZ Inst7_OBZ (.I(buf_clkout), .T(tristate_clock_o), .O(mipi_clock_o))

    assign mipi_clock_o = tristate_clock_o ? 1'bz : buf_clkout;
    assign mipi_data_o = tristate_data_o ? 1'bz : buf_douto0;
    assign mipi_data_n = tristate_data_o ? 1'bz : !buf_douto0;
             /* synthesis IO_TYPE="MIPI" */;

//    VHI scuba_vhi_inst (.Z(scuba_vhi));

    assign scuba_vhi = 1'b1;

//    ODDRX4B Inst6_ODDRX4B (.D0(scuba_vhi), .D1(scuba_vlo), .D2(scuba_vhi), 
//        .D3(scuba_vlo), .D4(scuba_vhi), .D5(scuba_vlo), .D6(scuba_vhi), 
//        .D7(scuba_vlo), .ECLK(eclkc), .SCLK(sclk_t), .RST(reset_i), .Q(buf_clkout));
//
//    ODDRX4B Inst5_ODDRX4B0 (.D0(d00), .D1(d10), .D2(d20), .D3(d30), .D4(d40), 
//        .D5(d50), .D6(d60), .D7(d70), .ECLK(eclkd), .SCLK(sclk_t), .RST(reset_i), 
//        .Q(buf_douto0));

reg check_oe, sync_out, LOAD_WORD;

    always  @(negedge sclk_t)
        LOAD_WORD <=1;
    always    @(posedge eclkd)
        LOAD_WORD <=0;


O_SERDES #(.DATA_RATE("DDR") , .WIDTH(8)) oserdes_data(
  .D({d00,d10,d20,d30,d40,d50,d60,d70}), // D input bus
  .RST(!reset_i), // Active-low, asynchronous reset
  .LOAD_WORD(LOAD_WORD), // Load word input
  .CLK_IN(sclk_t), // Fabric clock input
  .OE_IN(1), // Output tri-state enable input
  .OE_OUT(check_oe), // Output tri-state enable output (conttect to O_BUFT or inferred tri-state signal)
  .Q(buf_douto0), // Data output (Connect to output port, buffer or O_DELAY)
  .CHANNEL_BOND_SYNC_IN(), // Channel bond sync input
  .CHANNEL_BOND_SYNC_OUT(sync_out), // Channel bond sync output
  .PLL_LOCK(1), // PLL lock input
  .PLL_CLK(eclkd) // PLL clock input
);


O_SERDES #(.DATA_RATE("DDR") , .WIDTH(8)) oserdes_clock(
  .D({scuba_vhi,scuba_vlo,scuba_vhi,scuba_vlo,scuba_vhi,scuba_vlo,scuba_vhi,scuba_vlo}), // D input bus
  .RST(!reset_i), // Active-low, asynchronous reset
  .LOAD_WORD(LOAD_WORD), // Load word input
  .CLK_IN(sclk_t), // Fabric clock input
  .OE_IN(1), // Output tri-state enable input
  .OE_OUT(), // Output tri-state enable output (conttect to O_BUFT or inferred tri-state signal)
  .Q(buf_clkout), // Data output (Connect to output port, buffer or O_DELAY)
  .CHANNEL_BOND_SYNC_IN(), // Channel bond sync input
  .CHANNEL_BOND_SYNC_OUT(), // Channel bond sync output
  .PLL_LOCK(1), // PLL lock input
  .PLL_CLK(eclkc) // PLL clock input
);


//    ECLKSYNCA Inst4_ECLKSYNCA (.ECLKI(clocks_fast_clk_i), .STOP(xstop), .ECLKO(eclkc));

//    VLO scuba_vlo_inst (.Z(scuba_vlo));

    assign scuba_vlo = 1'b0;

//    defparam Inst3_CLKDIVC.DIV = "4.0" ;
//    CLKDIVC Inst3_CLKDIVC (.RST(reset_i), .CLKI(eclkd), .ALIGNWD(scuba_vlo), 
//        .CDIV1(cdiv1), .CDIVX(sclk_t));

// clock divider for sclk_t

    reg [2:0] counter = 0;
    reg sclk_t_1 = 0;
     always @(posedge eclkd) begin
       counter <= counter + 1;
       if (counter == 3'b1) begin
         sclk_t_1 <= ~sclk_t_1;
         counter <= 3'b0; // Reset the counter
       end
     end

    assign sclk_t = sclk_t_1;

//    ECLKSYNCA Inst2_ECLKSYNCA (.ECLKI(clockp_fast_data_i), .STOP(xstop), .ECLKO(eclkd));

    assign eclkc = clocks_fast_clk_i;
    assign eclkd = clockp_fast_data_i;

//    OBZ Inst1_OBZ0 (.I(buf_douto0), .T(tristate_data_o), .O(mipi_data_o[0]))
             /* synthesis IO_TYPE="MIPI" */;

    assign byte_clock_o = sclk_t;
    assign d70 = data_i[7];
    assign d60 = data_i[6];
    assign d50 = data_i[5];
    assign d40 = data_i[4];
    assign d30 = data_i[3];
    assign d20 = data_i[2];
    assign d10 = data_i[1];
    assign d00 = data_i[0];
    assign tx_ready_o = xstart;
    assign xstart = opensync_3;

//assign reversed_data = {data_i[0], data_i[1], data_i[2], data_i[3], data_i[4], data_i[5], data_i[6], data_i[7]};

    // exemplar begin
    // exemplar attribute FF_3 GSR ENABLED
    // exemplar attribute FF_2 GSR ENABLED
    // exemplar attribute FF_1 GSR ENABLED
    // exemplar attribute FF_0 GSR ENABLED
    // exemplar attribute Inst12_BB IO_TYPE MIPI_LP
    // exemplar attribute Inst11_BB IO_TYPE MIPI_LP
    // exemplar attribute Inst10_BB0 IO_TYPE MIPI_LP
    // exemplar attribute Inst9_BB0 IO_TYPE MIPI_LP
    // exemplar attribute Inst7_OBZ IO_TYPE MIPI
    // exemplar attribute Inst1_OBZ0 IO_TYPE MIPI
    // exemplar end



endmodule
