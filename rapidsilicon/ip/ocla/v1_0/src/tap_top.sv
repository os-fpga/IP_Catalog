// start of the code

// Length of the Instruction register
`define	IR_LENGTH	5

// Supported Instructions
// no EXTEST support?
`define IDCODE          5'b00010
`define REG1            5'b00100
`define REG2            5'b01000
`define BYPASS          5'b11111    // JTAG's standard requires all bits in IR to be 1

// Top module
module tap_top 
    #(
      // manufacturer = PULP Platform, part number = 0, version = 1
      parameter IDCODE_VALUE = 32'h10000db3
     )
     (
       // JTAG pins
       input       tms_i,      // JTAG test mode select pad
       input       tck_i,      // JTAG test clock pad
       input       rst_ni,     // JTAG test reset pad (actually ~trst), since trst is active low, 
       input       td_i,       // JTAG test data input pad
       output  reg td_o,       // JTAG test data output pad
       //output  tdo_padoe_o     // Output enable for JTAG test data output pad
    
       // TAP states
       output  shift_dr_o,
       output  update_dr_o,
       output  capture_dr_o,
    
       // TDO signal that is connected to TDI of sub-modules.
       output  scan_in_o,
    
       // Select signals for boundary scan or mbist
       output  axi_data_in_sel_o,
       output  axi_data_out_sel_o,
    
       // TDI signals from sub-modules
       input   axi_data_in_tdo,      // from reg1 module
       input   axi_data_out_tdo,        // from reg2 module
       
       // CTA signals for AXI registers
       output  axi_in_cta,
       output  axi_out_cta,
       
       // update edge detectors
       output  updatedr_fedge
     );    
    
    // TAPC FSM state registers
    reg     test_logic_reset;    // FSM state
    reg     run_test_idle;       // FSM state
    reg     sel_dr_scan;         // FSM state
    reg     capture_dr;          // FSM state
    reg     shift_dr;            // FSM state
    reg     exit1_dr;            // FSM state
    reg     pause_dr;            // FSM state
    reg     exit2_dr;            // FSM state
    reg     update_dr;           // FSM state
    reg     sel_ir_scan;         // FSM state
    reg     capture_ir;          // FSM state
    reg     shift_ir;            // FSM state
    reg     shift_ir_neg;    
    reg     exit1_ir;            // FSM state
    reg     pause_ir;            // FSM state
    reg     exit2_ir;            // FSM state
    reg     update_ir;           // FSM state
    
    // registers
    reg     idcode_sel;          
    reg     axi_data_in_sel;
    reg     axi_data_out_sel;
    reg     bypass_sel;
    
    reg     updatedr_fe;
    
    reg     tdo_comb;
    reg     tms_q1, tms_q2, tms_q3, tms_q4;
    wire    tms_reset;
    
    assign scan_in_o    = td_i;
    assign shift_dr_o   = shift_dr;
    assign update_dr_o  = update_dr;
    assign capture_dr_o = capture_dr;
    
    assign axi_data_in_sel_o = axi_data_in_sel;
    assign axi_data_out_sel_o = axi_data_out_sel;    
    
    assign updatedr_fedge = ((updatedr_fe == 1) & (update_dr == 0));
    
    always @ (posedge tck_i)
    begin
      tms_q1 <=  tms_i;
      tms_q2 <=  tms_q1;
      tms_q3 <=  tms_q2;
      tms_q4 <=  tms_q3;
    end
    
    always @ (posedge tck_i)
    begin
      updatedr_fe <= update_dr;
    end
    
    // the 5-TMS-ticks reset
    assign tms_reset = tms_q1 & tms_q2 & tms_q3 & tms_q4 & tms_i;    // 5 consecutive TMS=1 causes reset
    
    /**********************************************************************************
    *                                                                                 *
    *   TAP State Machine: Fully JTAG compliant                                       *
    *                                                                                 *
    **********************************************************************************/
    
    // Not exactly how I thought one would implement an FSM but this is pretty straightforward as well
    
    // test_logic_reset state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        test_logic_reset <= 1'b1;  
      else if (tms_reset)
        test_logic_reset <= 1'b1;
      else
        begin
          if(tms_i & (test_logic_reset | sel_ir_scan))
            test_logic_reset <= 1'b1;
          else
            test_logic_reset <= 1'b0;
        end
    end
    
    // run_test_idle state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        run_test_idle<= 1'b0;
      else if (tms_reset)
        run_test_idle<= 1'b0;
      else
      if(~tms_i & (test_logic_reset | run_test_idle | update_dr | update_ir))
        run_test_idle<= 1'b1;
      else
        run_test_idle<= 1'b0;
    end
    
    // sel_dr_scan state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        sel_dr_scan<= 1'b0;
      else if (tms_reset)
        sel_dr_scan<= 1'b0;
      else
      if(tms_i & (run_test_idle | update_dr | update_ir))
        sel_dr_scan<= 1'b1;
      else
        sel_dr_scan<= 1'b0;
    end
    
    // capture_dr state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        capture_dr<= 1'b0;
      else if (tms_reset)
        capture_dr<= 1'b0;
      else
      if(~tms_i & sel_dr_scan)
        capture_dr<= 1'b1;
      else
        capture_dr<= 1'b0;
    end
    
    // shift_dr state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        shift_dr<= 1'b0;
      else if (tms_reset)
        shift_dr<= 1'b0;
      else
      if(~tms_i & (capture_dr | shift_dr | exit2_dr))
        shift_dr<= 1'b1;
      else
        shift_dr<= 1'b0;
    end
    
    // exit1_dr state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        exit1_dr<= 1'b0;
      else if (tms_reset)
        exit1_dr<= 1'b0;
      else
      if(tms_i & (capture_dr | shift_dr))
        exit1_dr<= 1'b1;
      else
        exit1_dr<= 1'b0;
    end
    
    // pause_dr state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        pause_dr<= 1'b0;
      else if (tms_reset)
        pause_dr<= 1'b0;
      else
      if(~tms_i & (exit1_dr | pause_dr))
        pause_dr<= 1'b1;
      else
        pause_dr<= 1'b0;
    end
    
    // exit2_dr state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        exit2_dr<= 1'b0;
      else if (tms_reset)
        exit2_dr<= 1'b0;
      else
      if(tms_i & pause_dr)
        exit2_dr<= 1'b1;
      else
        exit2_dr<= 1'b0;
    end
    
    // update_dr state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        update_dr<= 1'b0;
      else if (tms_reset)
        update_dr<= 1'b0;
      else
      if(tms_i & (exit1_dr | exit2_dr))
        update_dr<= 1'b1;
      else
        update_dr<= 1'b0;
    end
    
    // sel_ir_scan state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        sel_ir_scan<= 1'b0;
      else if (tms_reset)
        sel_ir_scan<= 1'b0;
      else
      if(tms_i & sel_dr_scan)
        sel_ir_scan<= 1'b1;
      else
        sel_ir_scan<= 1'b0;
    end
    
    // capture_ir state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        capture_ir<= 1'b0;
      else if (tms_reset)
        capture_ir<= 1'b0;
      else
      if(~tms_i & sel_ir_scan)
        capture_ir<= 1'b1;
      else
        capture_ir<= 1'b0;
    end
    
    // shift_ir state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        shift_ir<= 1'b0;
      else if (tms_reset)
        shift_ir<= 1'b0;
      else
      if(~tms_i & (capture_ir | shift_ir | exit2_ir))
        shift_ir<= 1'b1;
      else
        shift_ir<= 1'b0;
    end
    
    // exit1_ir state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        exit1_ir<= 1'b0;
      else if (tms_reset)
        exit1_ir<= 1'b0;
      else
      if(tms_i & (capture_ir | shift_ir))
        exit1_ir<= 1'b1;
      else
        exit1_ir<= 1'b0;
    end
    
    // pause_ir state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        pause_ir<= 1'b0;
      else if (tms_reset)
        pause_ir<= 1'b0;
      else
      if(~tms_i & (exit1_ir | pause_ir))
        pause_ir<= 1'b1;
      else
        pause_ir<= 1'b0;
    end
    
    // exit2_ir state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        exit2_ir<= 1'b0;
      else if (tms_reset)
        exit2_ir<= 1'b0;
      else
      if(tms_i & pause_ir)
        exit2_ir<= 1'b1;
      else
        exit2_ir<= 1'b0;
    end
    
    // update_ir state
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        update_ir<= 1'b0;
      else if (tms_reset)
        update_ir<= 1'b0;
      else
      if(tms_i & (exit1_ir | exit2_ir))
        update_ir<= 1'b1;
      else
        update_ir<= 1'b0;
    end
    
    /**********************************************************************************
    *                                                                                 *
    *   End: TAP State Machine                                                        *
    *                                                                                 *
    **********************************************************************************/
    
    
    
    /**********************************************************************************
    *                                                                                 *
    *   jtag_ir:  JTAG Instruction Register                                           *
    *                                                                                 *
    **********************************************************************************/
    reg [`IR_LENGTH-1:0]  jtag_ir;          // Instruction register
    reg [`IR_LENGTH-1:0]  latched_jtag_ir, latched_jtag_ir_neg;
    wire                  instruction_tdo;
    
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        jtag_ir[`IR_LENGTH-1:0] <=  `IR_LENGTH'b0;
      else if(capture_ir)
        jtag_ir <=  5'b00101;          // This value is fixed for easier fault detection
      else if(shift_ir)
        jtag_ir[`IR_LENGTH-1:0] <=  {td_i, jtag_ir[`IR_LENGTH-1:1]};
    end
    
    assign  instruction_tdo =  jtag_ir[0];    // the shift-out line that does the magic
    /**********************************************************************************
    *                                                                                 *
    *   End: jtag_ir                                                                  *
    *                                                                                 *
    **********************************************************************************/
    
    
    
    /**********************************************************************************
    *                                                                                 *
    *   idcode logic                                                                  *
    *                                                                                 *
    **********************************************************************************/
    reg [31:0] idcode_reg;
    wire       idcode_tdo;
    
    always @ (posedge tck_i  or negedge rst_ni)
    begin
      if (~rst_ni)
        idcode_reg <=  IDCODE_VALUE;
      else if(idcode_sel & shift_dr)
        idcode_reg <=  {td_i, idcode_reg[31:1]};
      else if(idcode_sel & (capture_dr | exit1_dr))
        idcode_reg <=  IDCODE_VALUE;
    end
    
    assign idcode_tdo = idcode_reg[0];
    
    /**********************************************************************************
    *                                                                                 *
    *   End: idcode logic                                                             *
    *                                                                                 *
    **********************************************************************************/
    
    
    /**********************************************************************************
    *                                                                                 *
    *   Bypass logic                                                                  *
    *                                                                                 *
    **********************************************************************************/
    wire bypassed_tdo;
    reg  bypass_reg;
    
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if (~rst_ni)
        bypass_reg <= 1'b0;
      else if(shift_dr)
        bypass_reg <= td_i;
    end
    
    assign bypassed_tdo = bypass_reg;
    /**********************************************************************************
    *                                                                                 *
    *   End: Bypass logic                                                             *
    *                                                                                 *
    **********************************************************************************/
    
    
    /**********************************************************************************
    *                                                                                 *
    *   Activating Instructions                                                       *
    *                                                                                 *
    **********************************************************************************/
    // Updating jtag_ir (Instruction Register)
    always @ (posedge tck_i or negedge rst_ni)
    begin
      if(~rst_ni)
        latched_jtag_ir <= `IDCODE;   // IDCODE seled after reset
      else if (tms_reset)
        latched_jtag_ir <= `IDCODE;   // IDCODE seled after reset
      else if(update_ir)
        latched_jtag_ir <= jtag_ir;
    end
    
    /**********************************************************************************
    *                                                                                 *
    *   End: Activating Instructions                                                  *
    *                                                                                 *
    **********************************************************************************/
    
    
    // Updating jtag_ir (Instruction Register)
    always @ (latched_jtag_ir)
    begin
      idcode_sel         = 1'b0;
      axi_data_in_sel    = 1'b0;
      axi_data_out_sel   = 1'b0;
      bypass_sel         = 1'b0;

      // only works after the update_ir is detected on a +edge of tck
      case(latched_jtag_ir)    /* synthesis parallel_case */
        `IDCODE:            idcode_sel           = 1'b1;    // ID Code
        `REG1:              axi_data_in_sel      = 1'b1;    // REG1
        `REG2:              axi_data_out_sel     = 1'b1;    // REG2
        default:            bypass_sel           = 1'b1;    // BYPASS
      endcase
    end
        
    /**********************************************************************************
    *                                                                                 *
    *   Multiplexing TDO data                                                         *
    *                                                                                 *
    **********************************************************************************/
    always @ (*)
    begin
      if(shift_ir_neg)
        tdo_comb = instruction_tdo;      // Instruction register 
      else
        begin
          case(latched_jtag_ir_neg)    // synthesis parallel_case
            `IDCODE:            tdo_comb = idcode_tdo;          // Reading ID code
            `REG1:              tdo_comb = axi_data_in_tdo;     // REG1
            `REG2:              tdo_comb = axi_data_out_tdo;    // REG2
            `BYPASS:            tdo_comb = bypassed_tdo;        // BYPASS
            
            default:            tdo_comb = bypassed_tdo;        // BYPASS instruction
          endcase
        end
    end
    
    
    // Tristate control for td_o pin
    always @ (negedge tck_i)
    begin
      td_o   <=  tdo_comb;
    //  tdo_padoe_o <=  shift_ir | shift_dr;
    end
    /**********************************************************************************
    *                                                                                 *
    *   End: Multiplexing TDO data                                                    *
    *                                                                                 *
    **********************************************************************************/

    always @ (negedge tck_i)
    begin
      shift_ir_neg <=  shift_ir;
      latched_jtag_ir_neg <=  latched_jtag_ir;
    end
    
    /**********************************************************************************
    *                                                                                 *
    *   Generating selects for AXI registers                                          *
    *                                                                                 *
    **********************************************************************************/   

    // CTA signals: Clear to Access meaning the JTAG is not reading/writing a particulat register

    assign axi_in_cta  = !(axi_data_in_sel  && (capture_dr | shift_dr | exit1_dr | pause_dr | exit2_dr | update_dr));
    assign axi_out_cta = !(axi_data_out_sel && (capture_dr | shift_dr | exit1_dr | pause_dr | exit2_dr | update_dr));

endmodule
