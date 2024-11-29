`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/16/2024 03:49:07 PM
// Design Name: 
// Module Name: DLY_ADDR_CNTRL
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module DLY_ADDR_CNTRL #(parameter                    NUM_GB_SITES  = 20,
                        parameter [NUM_GB_SITES-1:0] DLY_LOC       = 'h0_C117,
                        parameter                    NUM_DLY       = 5,   //Minimum of 1 and maximum of 20 I_DELAY or O_DELAY  
                        parameter                    DLY_TAP_WIDTH = 6,
                        parameter                    ADDR_WIDTH    = 5
					  )
                    (input       rst,  
                     input [5:0] cntrl_dly_tap_value,							// Input to fabric from GearBox. I_DELAY TAP Value MUXED Output from GBox
                     input [20-1: 0] usr_dly_incdec,						// Input from user to control I_DELAY
	                 input [20-1: 0] usr_dly_ld,							// Input from user to control I_DELAY. Only one signal should be active at any time
	                 input [20-1: 0] usr_dly_adj,							// Input from user to control I_DELAY
	                 input [20-1: 0] usr_rd_dly_value,						// Input from user to read the I_DELAY output port for TAP Value
	                 output [ADDR_WIDTH-1:0] f2g_dly_addr,						// Address bus to GBox. Selects the I_DELAY
                     output cntrl_dly_incdec,									// Drive the selected I_DELAY INCDEC signal based upon the active user_dly_ld signal
                     output cntrl_dly_ld,										// Drive the selected I_DELAY LD siganl based upon the active user_dly_ld signal
                     output cntrl_dly_adj,										// Drive the selected I_DELAY ADJ siganl based upon the active user_dly_adj signal
                     output [(20*DLY_TAP_WIDTH)-1:0] usr_dly_tap_value_out   // DLY TAP Value out for user. Concatenated value
                    );

integer ACT_IDLY_CNT;
integer active_idelay_cnt;
reg [NUM_DLY:0]                  delay_location_index [NUM_GB_SITES-1:0];
reg [ADDR_WIDTH-1:0]             dly_site_addr [NUM_DLY-1:0];
wire [(ADDR_WIDTH*20)-1:0]  dly_site_addr_bus;
wire [19:0]               usr_dly_ld_en;
reg [5:0] last_dly_sly;
wire [5:0] cntrl_dly_adj_wire, cntrl_dly_incdec_wire, cntrl_dly_ld_wire;

assign cntrl_dly_adj = cntrl_dly_adj_wire[0];
assign cntrl_dly_incdec = cntrl_dly_incdec_wire[0];
assign cntrl_dly_ld = cntrl_dly_ld_wire[0];

	// Count one to assign DELAY to each address
	// Total number of GB_SITES are needed to asign address
    function integer act_dly_cnt (input [NUM_GB_SITES-1:0] valid_sites);
    integer i;
    begin
        act_dly_cnt = 0;
        active_idelay_cnt = 0;
        for (i = 0 ; i<NUM_GB_SITES ; i=i+1)
        begin
             delay_location_index[i] = NUM_DLY;
            if (DLY_LOC[i] == 1'b1) begin
                dly_site_addr[act_dly_cnt] = i;
                active_idelay_cnt = active_idelay_cnt + 1;
                delay_location_index[i] = act_dly_cnt;
                `ifdef SIM
                // $display("time=%t, act_dly_cnt=%0d, active_idelay_cnt=%d, delay_location_index[0x%h]=0x%h, dly_site_addr[%0d]=0x%h", $time, act_dly_cnt, active_idelay_cnt, i, delay_location_index[i], act_dly_cnt, dly_site_addr[act_dly_cnt]);
                `endif
                act_dly_cnt = act_dly_cnt+1;  // order is important for counting
            end
        end   // for loop
    end // function
    endfunction
    
	// Count one
    // function integer count_ones (input [NUM_DLY-1:0] valid_sites);
    // integer i;
    // begin
    //     count_ones = 0;
    //     for (i = 0 ; i<NUM_DLY ; i=i+1)
    //     begin
    //         if (DLY_LOC[i] == 1'b1) begin
    //             count_ones = count_ones+1;  // order is important for counting
    //         end
    //     end   // for loop
    // end // function
    // endfunction    

reg [4:0] usr_dly_adj_binary, usr_dly_ld_binary, usr_dly_ld_en_binary_or;
wire [19:0] or_wire;
integer i;
always @(*) begin
   usr_dly_adj_binary = 0;  // Initialize to 0
   usr_dly_ld_en_binary_or = 0;
   usr_dly_ld_binary = 0;
    for (i = 0; i < 20; i = i + 1) begin
        if (usr_dly_adj[i]) begin
            usr_dly_adj_binary = i;
        end
        if (usr_dly_ld[i]) begin
            usr_dly_ld_binary = i;
        end
        if (or_wire[i]) begin
            usr_dly_ld_en_binary_or = i;
        end
    end
end


DLY_VALUE_MUX MUXP_INST_INCDEC (
    .DLY_ADDR(usr_dly_adj_binary),
    .DLY_TAP_VALUE(cntrl_dly_incdec_wire),
    .DLY_TAP0_VAL({5'b00000, usr_dly_incdec[0]}),
    .DLY_TAP1_VAL({5'b00000, usr_dly_incdec[1]}),
    .DLY_TAP2_VAL({5'b00000, usr_dly_incdec[2]}),
    .DLY_TAP3_VAL({5'b00000, usr_dly_incdec[3]}),
    .DLY_TAP4_VAL({5'b00000, usr_dly_incdec[4]}),
    .DLY_TAP5_VAL({5'b00000, usr_dly_incdec[5]}),
    .DLY_TAP6_VAL({5'b00000, usr_dly_incdec[6]}),
    .DLY_TAP7_VAL({5'b00000, usr_dly_incdec[7]}),
    .DLY_TAP8_VAL({5'b00000, usr_dly_incdec[8]}),
    .DLY_TAP9_VAL({5'b00000, usr_dly_incdec[9]}),
    .DLY_TAP10_VAL({5'b00000, usr_dly_incdec[10]}),
    .DLY_TAP11_VAL({5'b00000, usr_dly_incdec[11]}),
    .DLY_TAP12_VAL({5'b00000, usr_dly_incdec[12]}),
    .DLY_TAP13_VAL({5'b00000, usr_dly_incdec[13]}),
    .DLY_TAP14_VAL({5'b00000, usr_dly_incdec[14]}),
    .DLY_TAP15_VAL({5'b00000, usr_dly_incdec[15]}),
    .DLY_TAP16_VAL({5'b00000, usr_dly_incdec[16]}),
    .DLY_TAP17_VAL({5'b00000, usr_dly_incdec[17]}),
    .DLY_TAP18_VAL({5'b00000, usr_dly_incdec[18]}),
    .DLY_TAP19_VAL({5'b00000, usr_dly_incdec[19]})
);


DLY_VALUE_MUX MUXP_INST_ADJ (
    .DLY_ADDR(usr_dly_adj_binary),
    .DLY_TAP_VALUE(cntrl_dly_adj_wire),
    .DLY_TAP0_VAL({5'b00000, usr_dly_adj[0]}),
    .DLY_TAP1_VAL({5'b00000, usr_dly_adj[1]}),
    .DLY_TAP2_VAL({5'b00000, usr_dly_adj[2]}),
    .DLY_TAP3_VAL({5'b00000, usr_dly_adj[3]}),
    .DLY_TAP4_VAL({5'b00000, usr_dly_adj[4]}),
    .DLY_TAP5_VAL({5'b00000, usr_dly_adj[5]}),
    .DLY_TAP6_VAL({5'b00000, usr_dly_adj[6]}),
    .DLY_TAP7_VAL({5'b00000, usr_dly_adj[7]}),
    .DLY_TAP8_VAL({5'b00000, usr_dly_adj[8]}),
    .DLY_TAP9_VAL({5'b00000, usr_dly_adj[9]}),
    .DLY_TAP10_VAL({5'b00000, usr_dly_adj[10]}),
    .DLY_TAP11_VAL({5'b00000, usr_dly_adj[11]}),
    .DLY_TAP12_VAL({5'b00000, usr_dly_adj[12]}),
    .DLY_TAP13_VAL({5'b00000, usr_dly_adj[13]}),
    .DLY_TAP14_VAL({5'b00000, usr_dly_adj[14]}),
    .DLY_TAP15_VAL({5'b00000, usr_dly_adj[15]}),
    .DLY_TAP16_VAL({5'b00000, usr_dly_adj[16]}),
    .DLY_TAP17_VAL({5'b00000, usr_dly_adj[17]}),
    .DLY_TAP18_VAL({5'b00000, usr_dly_adj[18]}),
    .DLY_TAP19_VAL({5'b00000, usr_dly_adj[19]})
);

DLY_VALUE_MUX MUXP_INST_LD (
    .DLY_ADDR(usr_dly_ld_binary),
    .DLY_TAP_VALUE(cntrl_dly_ld_wire),
    .DLY_TAP0_VAL({5'b00000, usr_dly_ld[0]}),
    .DLY_TAP1_VAL({5'b00000, usr_dly_ld[1]}),
    .DLY_TAP2_VAL({5'b00000, usr_dly_ld[2]}),
    .DLY_TAP3_VAL({5'b00000, usr_dly_ld[3]}),
    .DLY_TAP4_VAL({5'b00000, usr_dly_ld[4]}),
    .DLY_TAP5_VAL({5'b00000, usr_dly_ld[5]}),
    .DLY_TAP6_VAL({5'b00000, usr_dly_ld[6]}),
    .DLY_TAP7_VAL({5'b00000, usr_dly_ld[7]}),
    .DLY_TAP8_VAL({5'b00000, usr_dly_ld[8]}),
    .DLY_TAP9_VAL({5'b00000, usr_dly_ld[9]}),
    .DLY_TAP10_VAL({5'b00000, usr_dly_ld[10]}),
    .DLY_TAP11_VAL({5'b00000, usr_dly_ld[11]}),
    .DLY_TAP12_VAL({5'b00000, usr_dly_ld[12]}),
    .DLY_TAP13_VAL({5'b00000, usr_dly_ld[13]}),
    .DLY_TAP14_VAL({5'b00000, usr_dly_ld[14]}),
    .DLY_TAP15_VAL({5'b00000, usr_dly_ld[15]}),
    .DLY_TAP16_VAL({5'b00000, usr_dly_ld[16]}),
    .DLY_TAP17_VAL({5'b00000, usr_dly_ld[17]}),
    .DLY_TAP18_VAL({5'b00000, usr_dly_ld[18]}),
    .DLY_TAP19_VAL({5'b00000, usr_dly_ld[19]})
);   

DLY_VALUE_MUX MUXP_INST_ADDR (
    .DLY_ADDR(usr_dly_ld_binary | usr_dly_adj_binary),
    .DLY_TAP_VALUE(f2g_dly_addr),
    .DLY_TAP0_VAL(dly_site_addr_bus[(ADDR_WIDTH*1)-1 : ADDR_WIDTH*0]),
    .DLY_TAP1_VAL(dly_site_addr_bus[(ADDR_WIDTH*2)-1 : ADDR_WIDTH*1]),
    .DLY_TAP2_VAL(dly_site_addr_bus[(ADDR_WIDTH*3)-1 : ADDR_WIDTH*2]),
    .DLY_TAP3_VAL(dly_site_addr_bus[(ADDR_WIDTH*4)-1 : ADDR_WIDTH*3]),
    .DLY_TAP4_VAL(dly_site_addr_bus[(ADDR_WIDTH*5)-1 : ADDR_WIDTH*4]),
    .DLY_TAP5_VAL(dly_site_addr_bus[(ADDR_WIDTH*6)-1 : ADDR_WIDTH*5]),
    .DLY_TAP6_VAL(dly_site_addr_bus[(ADDR_WIDTH*7)-1 : ADDR_WIDTH*6]),
    .DLY_TAP7_VAL(dly_site_addr_bus[(ADDR_WIDTH*8)-1 : ADDR_WIDTH*7]),
    .DLY_TAP8_VAL(dly_site_addr_bus[(ADDR_WIDTH*9)-1 : ADDR_WIDTH*8]),
    .DLY_TAP9_VAL(dly_site_addr_bus[(ADDR_WIDTH*10)-1 : ADDR_WIDTH*9]),
    .DLY_TAP10_VAL(dly_site_addr_bus[(ADDR_WIDTH*11)-1 : ADDR_WIDTH*10]),
    .DLY_TAP11_VAL(dly_site_addr_bus[(ADDR_WIDTH*12)-1 : ADDR_WIDTH*11]),
    .DLY_TAP12_VAL(dly_site_addr_bus[(ADDR_WIDTH*13)-1 : ADDR_WIDTH*12]),
    .DLY_TAP13_VAL(dly_site_addr_bus[(ADDR_WIDTH*14)-1 : ADDR_WIDTH*13]),
    .DLY_TAP14_VAL(dly_site_addr_bus[(ADDR_WIDTH*15)-1 : ADDR_WIDTH*14]),
    .DLY_TAP15_VAL(dly_site_addr_bus[(ADDR_WIDTH*16)-1 : ADDR_WIDTH*15]),
    .DLY_TAP16_VAL(dly_site_addr_bus[(ADDR_WIDTH*17)-1 : ADDR_WIDTH*16]),
    .DLY_TAP17_VAL(dly_site_addr_bus[(ADDR_WIDTH*18)-1 : ADDR_WIDTH*17]),
    .DLY_TAP18_VAL(dly_site_addr_bus[(ADDR_WIDTH*19)-1 : ADDR_WIDTH*18]),
    .DLY_TAP19_VAL(dly_site_addr_bus[(ADDR_WIDTH*20)-1 : ADDR_WIDTH*19])
    );  

DLY_SEL_DECODER DECODER_INST1(
    .DLY_ADDR(usr_dly_ld_en_binary_or),
    .DLY_LOAD(cntrl_dly_tap_value[2]),
    .DLY_ADJ(cntrl_dly_tap_value[1]),
    .DLY_INCDEC(cntrl_dly_tap_value[0]),
    .DLY0_CNTRL(usr_dly_tap_value_out[2:0]),
    .DLY1_CNTRL(usr_dly_tap_value_out[8:6]),
    .DLY2_CNTRL(usr_dly_tap_value_out[14:12]),
    .DLY3_CNTRL(usr_dly_tap_value_out[20:18]),
    .DLY4_CNTRL(usr_dly_tap_value_out[26:24]),
	.DLY5_CNTRL(usr_dly_tap_value_out[32:30]),
	.DLY6_CNTRL(usr_dly_tap_value_out[38:36]),
	.DLY7_CNTRL(usr_dly_tap_value_out[44:42]),
	.DLY8_CNTRL(usr_dly_tap_value_out[50:48]),
	.DLY9_CNTRL(usr_dly_tap_value_out[56:54]),
	.DLY10_CNTRL(usr_dly_tap_value_out[62:60]),
	.DLY11_CNTRL(usr_dly_tap_value_out[68:66]),
	.DLY12_CNTRL(usr_dly_tap_value_out[74:72]),
	.DLY13_CNTRL(usr_dly_tap_value_out[80:78]),
	.DLY14_CNTRL(usr_dly_tap_value_out[86:84]),
	.DLY15_CNTRL(usr_dly_tap_value_out[92:90]),
	.DLY16_CNTRL(usr_dly_tap_value_out[98:96]),
	.DLY17_CNTRL(usr_dly_tap_value_out[104:102]),
	.DLY18_CNTRL(usr_dly_tap_value_out[110:108]),
	.DLY19_CNTRL(usr_dly_tap_value_out[116:114])
);


DLY_SEL_DECODER DECODER_INST2(
    .DLY_ADDR(usr_dly_ld_en_binary_or),
    .DLY_LOAD(cntrl_dly_tap_value[5]),
    .DLY_ADJ(cntrl_dly_tap_value[4]),
    .DLY_INCDEC(cntrl_dly_tap_value[3]),
    .DLY0_CNTRL(usr_dly_tap_value_out[5:3]),
    .DLY1_CNTRL(usr_dly_tap_value_out[11:9]),
    .DLY2_CNTRL(usr_dly_tap_value_out[17:15]),
    .DLY3_CNTRL(usr_dly_tap_value_out[23:21]),
    .DLY4_CNTRL(usr_dly_tap_value_out[29:27]),
	.DLY5_CNTRL(usr_dly_tap_value_out[35:33]),
	.DLY6_CNTRL(usr_dly_tap_value_out[41:39]),
	.DLY7_CNTRL(usr_dly_tap_value_out[47:45]),
	.DLY8_CNTRL(usr_dly_tap_value_out[53:51]),
	.DLY9_CNTRL(usr_dly_tap_value_out[59:57]),
	.DLY10_CNTRL(usr_dly_tap_value_out[65:63]),
	.DLY11_CNTRL(usr_dly_tap_value_out[71:69]),
	.DLY12_CNTRL(usr_dly_tap_value_out[77:75]),
	.DLY13_CNTRL(usr_dly_tap_value_out[83:81]),
	.DLY14_CNTRL(usr_dly_tap_value_out[89:87]),
	.DLY15_CNTRL(usr_dly_tap_value_out[95:93]),
	.DLY16_CNTRL(usr_dly_tap_value_out[101:99]),
	.DLY17_CNTRL(usr_dly_tap_value_out[107:105]),
	.DLY18_CNTRL(usr_dly_tap_value_out[113:111]),
	.DLY19_CNTRL(usr_dly_tap_value_out[119:117])
);
                        
assign usr_dly_ld_en = usr_rd_dly_value ^ usr_dly_ld;

assign or_wire = usr_dly_ld_en | usr_dly_adj;
    
// This generates the assign delay site address concatenated as a bus
generate
for (genvar i=0; i<NUM_DLY; i=i+1) begin : GEN_ADDR_CONCAT   
     assign dly_site_addr_bus[((ADDR_WIDTH*(i+1))-1):ADDR_WIDTH*i] = dly_site_addr[i]; 
end
endgenerate
  
                
always @(rst or usr_dly_ld)
    if (!rst) begin
        ACT_IDLY_CNT <= act_dly_cnt(NUM_GB_SITES);
 //       dly_site_addr_reg = dly_site_addr_tmp;
    end else begin
        ACT_IDLY_CNT <= 0;
    end
    //else begin
    //    if (count_ones(usr_dly_ld) > 1) begin
    //        $error("More then one delay load signals are active: usr_dly_ld = %0x0h", usr_dly_ld);
    //    end
    //end
//        dly_site_addr_reg <= dly_site_addr_tmp;
        //$display("time1=%t, dly_site_addr_reg = 0x%0h", $time, dly_site_addr_reg);
    //end
    
endmodule 