//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer: Fawad Ahmad
// 
// Create Date: 11/02/2022 05:47:37 PM
// Design Name: JTAG-to-AXI
// Module Name: jtag_to_axi_top
// Project Name: 
// Target Devices: RS Gemini devices
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
`default_nettype	wire

module jtag_to_axi_top #(
                         parameter integer C_S_AXI_ID_WIDTH      = 4,
                         parameter integer C_S_AXI_DATA_WIDTH    = 32,
                         parameter integer C_S_AXI_ADDR_WIDTH    = 32,
                         parameter integer C_S_AXI_AWUSER_WIDTH  = 0,
                         parameter integer C_S_AXI_ARUSER_WIDTH  = 0,
                         parameter integer C_S_AXI_WUSER_WIDTH   = 0,
                         parameter integer C_S_AXI_RUSER_WIDTH   = 0,
                         parameter integer C_S_AXI_BUSER_WIDTH   = 0
                        ) 
                        (
                         // AXI-Master interface
                         input ACLK,                        // 50-100MHz variable
                         input ARESETN,
                         // AXI_BUS.Master axi_m_jtag,
                         
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
                         output logic        [C_S_AXI_ID_WIDTH-1 : 0] r_id,
                         input  logic      [C_S_AXI_DATA_WIDTH-1 : 0] r_data,
                         input  logic                                 r_last,
                         input  logic                                 r_valid,
                         input  logic                           [1:0] r_resp,
                         output logic                                 r_ready,
                         input  logic     [C_S_AXI_RUSER_WIDTH-1 : 0] r_user,
                          
                         // write response channel
                         output logic        [C_S_AXI_ID_WIDTH-1 : 0] b_id,
                         input  logic                           [1:0] b_resp,
                         input  logic                                 b_valid,
                         output logic                                 b_ready,
                         input  logic     [C_S_AXI_BUSER_WIDTH-1 : 0] b_user,
                                                 
                         // JTAG interface
                         input      JTAG_TCK,        // 30MHz max.
                         input      JTAG_TMS,
                         input      JTAG_TDI,
                         output reg JTAG_TDO,
                         input      JTAG_TRST                       
                        );
                        
    localparam idle      = 3'b000;
    localparam request   = 3'b001;
    localparam readdata  = 3'b010;
    localparam storedata = 3'b011;
    localparam ack       = 3'b100;      
    
    localparam REG_AXI_IN_LENGTH   = C_S_AXI_DATA_WIDTH + C_S_AXI_ADDR_WIDTH + 4;
    localparam REG_AXI_OUT_LENGTH  = C_S_AXI_DATA_WIDTH + 2;              
                        
    // top level FSM states
    typedef enum    logic [2:0]    {IDLE, WAIT_AND_STORE, STORE_IN_JTAG_REG, GENERATE_TRIGGER, STORE_DATA_RESP} TopFSMState;
    TopFSMState  top_state;
    
    logic [2:0] axi_state;                      
                        
    // TAP controller signals for AXI registers
    logic tapc_shiftdr;
    logic tapc_capturedr;
    logic tapc_updatedr;
    logic tapc_tdo;
    
    // TAP controller signals for AXI registers
    logic tapc_axi_in_sel;
    logic tapc_axi_out_sel;    
    logic tapc_axi_in_cta;
    logic tapc_axi_out_cta;
    
    // synchronized cta and update signals for AXI clock domain
    logic sync_tapc_axi_in_cta;
    logic sync_tapc_axi_out_cta;
    
    logic sync_tapc_axi_in_sel;
    logic sync_tapc_axi_out_sel;
    
    logic sync_tapc_updatedr;
    
    // TAP controller inputs from AXI registers
    logic tapc_axi_in_tdo;
    logic tapc_axi_out_tdo;
    
    // AXI read data from slave
    wire  [(C_S_AXI_DATA_WIDTH + 2) - 1 : 0] axi_slave_dat;
    wire                                     axi_m_trans_trig;
    
    // parallel input/output for AXI registers
    reg     [REG_AXI_IN_LENGTH - 1 : 0]  pi_axi_data_in;
    reg    [REG_AXI_OUT_LENGTH - 1 : 0]  pi_axi_data_out;
    wire    [REG_AXI_IN_LENGTH - 1 : 0]  po_axi_data_in;
    wire   [REG_AXI_OUT_LENGTH - 1 : 0]  po_axi_data_out;
    
    // contents of the AXI registers
    reg    [REG_AXI_IN_LENGTH - 1 : 0] axi_data_in_dat;
    reg   [REG_AXI_OUT_LENGTH - 1 : 0] axi_data_out_dat;
    
    // mode selects for AXI registers
    reg mode_axi_in  = 1'b1;
    reg mode_axi_out = 1'b1;
    
    // misc.
    wire                              updatedr_falling;
    wire                              sync_updatedr_falling;
    reg  [REG_AXI_OUT_LENGTH - 1 : 0] pi_axi_data_out_temp;
    reg                               first_read_done;
    
    wire                      [1:0] burst_type;
    wire [C_S_AXI_DATA_WIDTH-1 : 0] jtag_to_axi_data;
    
    assign        burst_type = po_axi_data_in[REG_AXI_IN_LENGTH-1 : REG_AXI_IN_LENGTH-2];
    assign  jtag_to_axi_data = po_axi_data_in[(C_S_AXI_DATA_WIDTH+34)-1 : 34];
    
    // AXI-Master trigger gen    
    wire      axi_m_trans_trig_edge;
    reg       axi_m_trans_trig_prev;
    wire      axi_rw;
    reg [2:0] axi_state_prev;
    wire      axi_trans_done_detect;
    reg       trig;
    wire      axi_master_update_trigger;

    wire      axi_out_read;
    reg       axi_out_read_prev;
    wire      axi_out_read_edge;
    
    // ---------------------------------------- assigns ---------------------------------------
    // transaction trigger: generate as soon as the axi_in register is updated (to initiate the r/w transaction)
    assign axi_m_trans_trig          =  sync_updatedr_falling & sync_tapc_axi_in_sel;
    // trigger edge detector: keep track of rising edge of axi transaction trigger, the 'trig' is manual trigger generated in the "GENERATE_TRIGGER" state
    assign axi_m_trans_trig_edge     =  ((axi_m_trans_trig_prev == 0) & (axi_m_trans_trig == 1)) | trig;
    assign axi_rw                    =  po_axi_data_in[1];
    assign axi_trans_done_detect     =  (axi_state == idle) & ((axi_state_prev == ack) | (axi_state_prev == readdata));
    assign axi_master_update_trigger =  axi_m_trans_trig_edge & sync_tapc_axi_in_cta;
    
    assign axi_out_read              =  sync_updatedr_falling & sync_tapc_axi_out_sel;
    assign axi_out_read_edge         =  (axi_out_read_prev == 0) & (axi_out_read == 1);
    
    // address selection for axi master
    reg    [C_S_AXI_ADDR_WIDTH - 1 : 0] axi_generated_addr;
    wire   [C_S_AXI_ADDR_WIDTH - 1 : 0] axi_read_address;
    assign    axi_read_address = ((burst_type == 2'b10) & (top_state != IDLE)) ? axi_generated_addr : po_axi_data_in[33:2];
    
    // -------------------------------------- TAP instance --------------------------------------
    tap_top JTAG_TAP(
                     // jtag
                     .tms_i   (JTAG_TMS),
                     .tck_i   (JTAG_TCK),
                     .rst_ni  (JTAG_TRST),
                     .td_i    (JTAG_TDI),
                     .td_o    (JTAG_TDO),
                          
                     // tap states
                     .shift_dr_o   (tapc_shiftdr),
                     .update_dr_o  (tapc_updatedr),
                     .capture_dr_o (tapc_capturedr),
                      
                     // tdo signal connected to tdi of sub modules
                     .scan_in_o(tapc_tdo),
                          
                     // select signals for boundary scan or mbist
                     .axi_data_in_sel_o  (tapc_axi_in_sel),
                     .axi_data_out_sel_o (tapc_axi_out_sel),
                         
                     // tdi signals from sub modules
                     .axi_data_in_tdo  (tapc_axi_in_tdo),
                     .axi_data_out_tdo (tapc_axi_out_tdo),
                     
                     .axi_in_cta  (tapc_axi_in_cta),
                     .axi_out_cta (tapc_axi_out_cta),
                     
                     .updatedr_fedge(updatedr_falling)
                    );
 
    // -------------------------------------- AXI-MASTER instance --------------------------------------               
    jtag_axi_wrap # (
                     .C_S_AXI_ID_WIDTH     (C_S_AXI_ID_WIDTH), 
                     .C_S_AXI_DATA_WIDTH   (C_S_AXI_DATA_WIDTH), 
                     .C_S_AXI_ADDR_WIDTH   (C_S_AXI_ADDR_WIDTH), 
                     .C_S_AXI_AWUSER_WIDTH (C_S_AXI_AWUSER_WIDTH), 
                     .C_S_AXI_ARUSER_WIDTH (C_S_AXI_ARUSER_WIDTH), 
                     .C_S_AXI_WUSER_WIDTH  (C_S_AXI_WUSER_WIDTH), 
                     .C_S_AXI_RUSER_WIDTH  (C_S_AXI_RUSER_WIDTH), 
                     .C_S_AXI_BUSER_WIDTH  (C_S_AXI_BUSER_WIDTH) 
                    )
                    AXI_M_INTF
                    (
                     // inputs
                     .update        (axi_master_update_trigger),
                     .axireg_i      ({po_axi_data_in[(C_S_AXI_DATA_WIDTH+34)-1 : 34], axi_read_address, po_axi_data_in[1:0]}),  
                     .aclk          (ACLK),
                     .aresetn       (ARESETN),
                    
                     .state_axi_fsm (axi_state),
                     .axireg_o      (axi_slave_dat),
                     // .jtag_master   (axi_m_jtag)
                     
                     .aw_id     (aw_id),
                     .aw_addr   (aw_addr),
                     .aw_lock   (aw_lock),
                     .aw_cache  (aw_cache),
                     .aw_prot   (aw_prot),
                     .aw_region (aw_region),
                     .aw_user   (aw_user),
                     .aw_qos    (aw_qos),
                     .aw_valid  (aw_valid),
                     .aw_ready  (aw_ready),
                     .aw_burst  (aw_burst),
                     .aw_size   (aw_size),
                     .aw_len    (aw_len),
                     
                     // read address channel
                     .ar_id     (ar_id),
                     .ar_addr   (ar_addr),
                     .ar_lock   (ar_lock),
                     .ar_cache  (ar_cache),
                     .ar_prot   (ar_prot),
                     .ar_region (ar_region),
                     .ar_user   (ar_user),
                     .ar_qos    (ar_qos),
                     .ar_valid  (ar_valid),
                     .ar_ready  (ar_ready),
                     .ar_burst  (ar_burst),
                     .ar_size   (ar_size),
                     .ar_len    (ar_len),
                     
                     // write data channel
                     .w_data  (w_data),
                     .w_strb  (w_strb),
                     .w_last  (w_last),
                     .w_user  (w_user),
                     .w_valid (w_valid),
                     .w_ready (w_ready),
                     
                     // read data channel
                     .r_data  (r_data),
                     .r_last  (r_last),
                     .r_valid (r_valid),
                     .r_resp  (r_resp),
                     .r_ready (r_ready),
                     .r_user  (r_user),
                      
                     // write response channel
                     .b_resp  (b_resp),
                     .b_valid (b_valid),
                     .b_ready (b_ready),
                     .b_user  (b_user)
                    );

    // -------------------------------------- AXI Data-in Reg --------------------------------------
    jtagreg #(
              .JTAGREGSIZE(REG_AXI_IN_LENGTH),  // 1 bit for r/w, 2 bits for incr burst, fixed burst and no burst
              .SYNC(0)
             ) 
    AXI_DATA_IN_REG 
             (
              .clk_i         (JTAG_TCK),
              .rst_ni        (JTAG_TRST),
              .enable_i      (tapc_axi_in_sel),
              .capture_dr_i  (tapc_capturedr),
              .shift_dr_i    (tapc_shiftdr),
              .update_dr_i   (tapc_updatedr),
              .jtagreg_in_i  (pi_axi_data_in),
              .mode_i        (mode_axi_in),
              .scan_in_i     (tapc_tdo),
              .scan_out_o    (tapc_axi_in_tdo),
              .jtagreg_out_o (po_axi_data_in)
             );
 
     // -------------------------------------- AXI Data-out Reg --------------------------------------            
    jtagreg #(
              .JTAGREGSIZE(REG_AXI_OUT_LENGTH),  
              .SYNC(0)
             ) 
    AXI_DATA_OUT_REG 
             (
              .clk_i         (JTAG_TCK),
              .rst_ni        (JTAG_TRST),
              .enable_i      (tapc_axi_out_sel),
              .capture_dr_i  (tapc_capturedr),
              .shift_dr_i    (tapc_shiftdr),
              .update_dr_i   (tapc_updatedr),
              .jtagreg_in_i  (pi_axi_data_out),
              .mode_i        (mode_axi_out),
              .scan_in_i     (1'b0),
              .scan_out_o    (tapc_axi_out_tdo),
              .jtagreg_out_o (po_axi_data_out)
             );
             
    // -------------------------------------- Synchronizers --------------------------------------             
    ff_sync axi_in_cta_synchronizer(
                                    .destination_clk  (ACLK),
                                    .destination_rstn (ARESETN),                                    
                                    .async_data_in    (tapc_axi_in_cta),
                                    .sync_data_out    (sync_tapc_axi_in_cta)
                                   );
                                   
    ff_sync axi_out_cta_synchronizer(
                                     .destination_clk  (ACLK),
                                     .destination_rstn (ARESETN),                                    
                                     .async_data_in    (tapc_axi_out_cta),
                                     .sync_data_out    (sync_tapc_axi_out_cta)
                                    );
                                    
    ff_sync axi_in_updatedr_synchronizer(
                                         .destination_clk  (ACLK),
                                         .destination_rstn (ARESETN),                                    
                                         .async_data_in    (updatedr_falling),
                                         .sync_data_out    (sync_updatedr_falling)
                                        );

    ff_sync axi_in_sel_synchronizer(
                                    .destination_clk  (ACLK),
                                    .destination_rstn (ARESETN),                                    
                                    .async_data_in    (tapc_axi_in_sel),
                                    .sync_data_out    (sync_tapc_axi_in_sel)
                                   );

    ff_sync axi_out_sel_synchronizer(
                                     .destination_clk  (ACLK),
                                     .destination_rstn (ARESETN),                                    
                                     .async_data_in    (tapc_axi_out_sel),
                                     .sync_data_out    (sync_tapc_axi_out_sel)
                                    );                                       
                                       

    //******************************************************************************************//
    //                                                                                          //
    //                      JTAG and AXI-M data sync and exchange logic                         //
    //                                                                                          //
    //******************************************************************************************//

    always @ (posedge ACLK or negedge ARESETN)
    begin
        if(!ARESETN)
        begin
            axi_m_trans_trig_prev <= 1'b0;
            axi_state_prev        <= 3'b000;
            axi_out_read_prev     <= 1'b0;
        end
        else
        begin
            axi_m_trans_trig_prev <= axi_m_trans_trig;
            axi_state_prev        <= axi_state;
            axi_out_read_prev     <= axi_out_read;
        end
    end    
    
    // Top FSM
    
    always @ (posedge ACLK or negedge ARESETN)
    begin
        if(!ARESETN)
        begin
            pi_axi_data_in  <= {REG_AXI_IN_LENGTH{1'b0}};
            pi_axi_data_out <= {REG_AXI_OUT_LENGTH{1'b0}};
            first_read_done <= 1'b0;
            
            axi_data_in_dat  <= {REG_AXI_IN_LENGTH{1'b0}};
            axi_data_out_dat <= {REG_AXI_OUT_LENGTH{1'b0}};
            
            axi_generated_addr <= {C_S_AXI_ADDR_WIDTH{1'b0}};
            
            pi_axi_data_out_temp <= {REG_AXI_OUT_LENGTH{1'b0}};
            trig                 <= 0;
            
            top_state <= IDLE;
        end
        else
        begin
            case (top_state)
                // idling, no transaction underway
                IDLE:
                begin
                    if (axi_state == request)
                    begin
                        axi_generated_addr <= po_axi_data_in[33:2];
                        top_state          <= WAIT_AND_STORE;
                    end
                    else
                    begin
                        top_state <= IDLE;
                    end
                end

                // waiting for an ongoing transaction to finish
                WAIT_AND_STORE:
                begin
                    trig <= 0;
                    
                    if (!sync_tapc_axi_in_cta)   // if axi-in is being accessed externally
                    begin
                        top_state <= IDLE;
                    end
                    else if (axi_trans_done_detect)   // wait till the ongoing axi transaction completes 
                    begin
                        top_state       <= STORE_IN_JTAG_REG;  
                                                                    
                        if (!axi_rw)    // if read op                         
                            pi_axi_data_out_temp  <=  axi_slave_dat;    // store received read data and response in temp register                        
                        else           // if write op                       
                            pi_axi_data_out_temp  <=  {{axi_slave_dat[(C_S_AXI_DATA_WIDTH + 2) - 1 : (C_S_AXI_DATA_WIDTH + 2) - 2]}, {C_S_AXI_DATA_WIDTH{1'b0}}};   // store write data and response in temp register
                    end
                    else            
                        top_state <= WAIT_AND_STORE;                    
                end      
                
                // storing the read data/response when axi_out is clear to access
                STORE_IN_JTAG_REG:
                begin
                    pi_axi_data_out  <=  pi_axi_data_out_temp;   // :mod_n2:
                    if(!sync_tapc_axi_in_cta | axi_rw)   // if write op or axi-in is being externally accessed
                    begin
                        top_state <= IDLE;
                    end
                    // if a read op on axi-out has been made through jtag -OR- first read has not been done -OR- there is not burst mode selected 
//                    else if((sync_tapc_axi_out_cta & axi_out_read_edge) | (first_read_done == 1'b0) | (burst_type == 2'b00 | burst_type == 2'b11))   // :mod_o1:
                    else if((sync_tapc_axi_out_cta & axi_out_read_edge) | (burst_type == 2'b00 | burst_type == 2'b11))   // :mod_n1:
                    begin
                        // store the temporary value from temp to axi-out register
//                        pi_axi_data_out  <=  pi_axi_data_out_temp;    // :mod_o2:
                        top_state        <=  GENERATE_TRIGGER;  
                    end
                    else            
                        top_state        <=  STORE_IN_JTAG_REG;
                end
                
                // forcing a trigger to start another read in case of burst
                GENERATE_TRIGGER:
                begin
                    if(!axi_rw & sync_tapc_axi_in_cta)    // if read op and axi-in reg is not being accessed by JTAG
                    begin
                        if(burst_type == 3'b00 | burst_type == 3'b11) // if no burst
                        begin
                            top_state        <=  IDLE;
                        end
                        else if(burst_type == 3'b01)     // if fixed burst
                        begin
                            trig      <= 1;
                            top_state <= WAIT_AND_STORE;
                            first_read_done    <= 1'b1;
                        end
                        else                             // if incremental burst
                        begin
                            trig               <= 1;
                            top_state          <= WAIT_AND_STORE;
                            axi_generated_addr <= axi_generated_addr + {{1'b1}, {(C_S_AXI_DATA_WIDTH/32 + 1){1'b0}}};
                            first_read_done    <= 1'b1;
                        end
                    end
                    else           // if write op
                    begin                        
                        top_state <= IDLE;
                    end                  
                end
                
                default: 
                begin
                    top_state <= IDLE;
                end
            endcase
        end
    end
    

endmodule
