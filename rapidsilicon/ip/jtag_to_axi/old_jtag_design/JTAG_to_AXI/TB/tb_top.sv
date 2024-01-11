`timescale 1ns / 1ps

module tb_top();

  //  localparam int unsigned JTAG_PERIOD = 1000;
  localparam int unsigned JTAG_PERIOD = 33;   // a 20MHz TCK clock
  localparam int unsigned JTAG_IRLEN = 5;

  localparam IDCODE         = 5'b00010;
  localparam AXI_IN         = 5'b00100;
  localparam AXI_OUT        = 5'b01000;
  localparam BYPASS         = 5'b11111;

  // AXI signals
  logic aclk = 1'b0;
  logic aresetn;
  
  // JTAG signals
  logic jtag_trst;
  logic jtag_tck;
  logic jtag_tms;
  logic jtag_tdi;
  logic jtag_tdo;
  
  localparam C_S_AXI_ID_WIDTH      = 4;
  localparam C_S_AXI_DATA_WIDTH    = 32;
  localparam C_S_AXI_ADDR_WIDTH    = 32;
  localparam C_S_AXI_AWUSER_WIDTH  = 4;
  localparam C_S_AXI_ARUSER_WIDTH  = 4;
  localparam C_S_AXI_WUSER_WIDTH   = 4;
  localparam C_S_AXI_RUSER_WIDTH   = 4;
  localparam C_S_AXI_BUSER_WIDTH   = 4;
  
  localparam int unsigned REG1_SIZE = C_S_AXI_DATA_WIDTH + C_S_AXI_ADDR_WIDTH + 4;
  localparam int unsigned REG2_SIZE = C_S_AXI_DATA_WIDTH + 2;
  
  reg [127:0] dr_out;
  
    logic        [C_S_AXI_ID_WIDTH-1 : 0] aw_id;
    logic      [C_S_AXI_ADDR_WIDTH-1 : 0] aw_addr;
    logic                                 aw_lock;
    logic                           [3:0] aw_cache;
    logic                           [2:0] aw_prot;
    logic                           [3:0] aw_region;
    logic    [C_S_AXI_AWUSER_WIDTH-1 : 0] aw_user;
    logic                           [3:0] aw_qos;
    logic                                 aw_valid;
    logic                                 aw_ready;
    logic                           [1:0] aw_burst;
    logic                           [2:0] aw_size;
    logic                           [7:0] aw_len;
    
    // read address channel
    logic        [C_S_AXI_ID_WIDTH-1 : 0] ar_id;
    logic      [C_S_AXI_ADDR_WIDTH-1 : 0] ar_addr;
    logic                                 ar_lock;
    logic                           [3:0] ar_cache;
    logic                           [2:0] ar_prot;
    logic                           [3:0] ar_region;
    logic    [C_S_AXI_ARUSER_WIDTH-1 : 0] ar_user;
    logic                           [3:0] ar_qos;
    logic                                 ar_valid;
    logic                                 ar_ready;
    logic                           [1:0] ar_burst;
    logic                           [2:0] ar_size;
    logic                           [7:0] ar_len;
    
    // write data channel
    logic      [C_S_AXI_DATA_WIDTH-1 : 0] w_data;
    logic  [(C_S_AXI_DATA_WIDTH/8)-1 : 0] w_strb;
    logic                                 w_last;
    logic     [C_S_AXI_WUSER_WIDTH-1 : 0] w_user;
    logic                                 w_valid;
    logic                                 w_ready;
    
    // read data channel
    logic      [C_S_AXI_DATA_WIDTH-1 : 0] r_data;
    logic                                 r_last;
    logic                                 r_valid;
    logic                           [1:0] r_resp;
    logic                                 r_ready;
    logic     [C_S_AXI_RUSER_WIDTH-1 : 0] r_user;
    logic        [C_S_AXI_ID_WIDTH-1 : 0] r_id;
    
    // write response channel
    logic                          [1:0]  b_resp;
    logic                                 b_valid;
    logic                                 b_ready;
    logic     [C_S_AXI_BUSER_WIDTH-1 : 0] b_user;
    logic        [C_S_AXI_ID_WIDTH-1 : 0] b_id;
                       
  
  // j2a IP instance
  jtag_to_axi_top #(
                    .C_S_AXI_ID_WIDTH      (C_S_AXI_ID_WIDTH),
                    .C_S_AXI_DATA_WIDTH    (C_S_AXI_DATA_WIDTH),
                    .C_S_AXI_ADDR_WIDTH    (C_S_AXI_ADDR_WIDTH),
                    .C_S_AXI_AWUSER_WIDTH  (C_S_AXI_AWUSER_WIDTH),
                    .C_S_AXI_ARUSER_WIDTH  (C_S_AXI_ARUSER_WIDTH),
                    .C_S_AXI_WUSER_WIDTH   (C_S_AXI_WUSER_WIDTH),
                    .C_S_AXI_RUSER_WIDTH   (C_S_AXI_RUSER_WIDTH),
                    .C_S_AXI_BUSER_WIDTH   (C_S_AXI_BUSER_WIDTH)
                   )
            j2a_dut
                   (
                    // AXI interface
                    .ACLK       (aclk),
                    .ARESETN    (aresetn),
//                    .axi_m_jtag (axi_master_tb.Master), 
                    
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
                    .b_user  (b_user),
                    
                    // JTAG interface
                    .JTAG_TCK  (jtag_tck),
                    .JTAG_TMS  (jtag_tms),
                    .JTAG_TDI  (jtag_tdi),
                    .JTAG_TDO  (jtag_tdo),
                    .JTAG_TRST (~jtag_trst)
                   );
                   
  // ------------------------------------ AXI-S -------------------------------------
    axi_slave 
    #(
     .C_S_AXI_ID_WIDTH      (C_S_AXI_ID_WIDTH),
     .C_S_AXI_DATA_WIDTH    (C_S_AXI_DATA_WIDTH),
     .C_S_AXI_ADDR_WIDTH    (C_S_AXI_ADDR_WIDTH),
     .C_S_AXI_AWUSER_WIDTH  (C_S_AXI_AWUSER_WIDTH),
     .C_S_AXI_ARUSER_WIDTH  (C_S_AXI_ARUSER_WIDTH),
     .C_S_AXI_WUSER_WIDTH   (C_S_AXI_WUSER_WIDTH),
     .C_S_AXI_RUSER_WIDTH   (C_S_AXI_RUSER_WIDTH),
     .C_S_AXI_BUSER_WIDTH   (C_S_AXI_BUSER_WIDTH)
    )
    axi_slave_dut 
    (
     .S_AXI_ACLK      (aclk),
     .S_AXI_ARESETN   (aresetn),
     .S_AXI_AWID      (aw_id),
     .S_AXI_AWADDR    (aw_addr),
     .S_AXI_AWLEN     (aw_len),
     .S_AXI_AWSIZE    (aw_size),
     .S_AXI_AWBURST   (aw_burst),
     .S_AXI_AWLOCK    (aw_lock),
     .S_AXI_AWCACHE   (aw_cache),
     .S_AXI_AWPROT    (aw_prot),
     .S_AXI_AWQOS     (aw_qos),
     .S_AXI_AWREGION  (aw_region),
     .S_AXI_AWUSER    (aw_user),
     .S_AXI_AWVALID   (aw_valid),
     .S_AXI_AWREADY   (aw_ready),
     .S_AXI_WDATA     (w_data),
     .S_AXI_WSTRB     (w_strb),
     .S_AXI_WLAST     (w_last),
     .S_AXI_WUSER     (w_user),
     .S_AXI_WVALID    (w_valid),
     .S_AXI_WREADY    (w_ready),
     .S_AXI_BID       (b_id),
     .S_AXI_BRESP     (b_resp),
     .S_AXI_BUSER     (b_user),
     .S_AXI_BVALID    (b_valid),
     .S_AXI_BREADY    (b_ready),
     .S_AXI_ARID      (ar_id),
     .S_AXI_ARADDR    (ar_addr),
     .S_AXI_ARLEN     (ar_len),
     .S_AXI_ARSIZE    (ar_size),
     .S_AXI_ARBURST   (ar_burst),
     .S_AXI_ARLOCK    (ar_lock),
     .S_AXI_ARCACHE   (ar_cache),
     .S_AXI_ARPROT    (ar_prot),
     .S_AXI_ARQOS     (ar_qos),
     .S_AXI_ARREGION  (ar_region),
     .S_AXI_ARUSER    (ar_user),
     .S_AXI_ARVALID   (ar_valid),
     .S_AXI_ARREADY   (ar_ready),
     .S_AXI_RID       (r_id),
     .S_AXI_RDATA     (r_data),
     .S_AXI_RRESP     (r_resp),
     .S_AXI_RLAST     (r_last),
     .S_AXI_RUSER     (r_user),
     .S_AXI_RVALID    (r_valid),
     .S_AXI_RREADY    (r_ready)
    );
                   
    // actual test sequence
    initial 
    begin
        jtag_trst = 1'b0;
        jtag_tdi  = 1'b0;
        jtag_tms  = 1'b0;
        jtag_tck  = 1'b0;
        
        // first thing: a hard reset     
        jtag_hard_rst();
        jtag_rst();        
        
        // ******************** axi-in write *********************
//        jtag_selectir (AXI_IN); 
//        jtag_senddr   (REG1_SIZE, {{2'b10}, {64'hDEADBEEFDEADF00D}, {32'h00000000}, {2'b11}}, dr_out);  
//                                  // burst      // 64-bit Data      // 32-bit Addr   //w/r + request

//        jtag_selectir (AXI_IN); 
//        jtag_senddr   (REG1_SIZE, {{2'b10}, {64'hDEADBEEFDEADF001}, {32'h00000008}, {2'b11}}, dr_out);  
//                                  // burst      // 64-bit Data      // 32-bit Addr   //w/r + request
                                  
//        jtag_selectir (AXI_IN); 
//        jtag_senddr   (REG1_SIZE, {{2'b00}, {64'hDEADBEEFDEADF002}, {32'h00000010}, {2'b11}}, dr_out);  
//                                  // burst      // 64-bit Data      // 32-bit Addr   //w/r + request     
                                                               
//        jtag_selectir (AXI_IN); 
//        jtag_senddr   (REG1_SIZE, {{2'b10}, {64'hDEADBEEFDEADF003}, {32'h00000018}, {2'b11}}, dr_out);  
//                                  // burst      // 64-bit Data      // 32-bit Addr   //w/r + request
                                  
        // -------------- 32bit ---------------------------                          
        jtag_selectir (AXI_IN); 
        jtag_senddr   (REG1_SIZE, {{2'b10}, {32'hDEADF00D}, {32'h00000000}, {2'b11}}, dr_out);  
                                // burst      // 64-bit Data      // 32-bit Addr   //w/r + request

        jtag_selectir (AXI_IN); 
        jtag_senddr   (REG1_SIZE, {{2'b10}, {32'hDEADF001}, {32'h00000004}, {2'b11}}, dr_out);  
                                // burst      // 64-bit Data      // 32-bit Addr   //w/r + request
                                
        jtag_selectir (AXI_IN); 
        jtag_senddr   (REG1_SIZE, {{2'b00}, {32'hDEADF002}, {32'h00000008}, {2'b11}}, dr_out);  
                                // burst      // 64-bit Data      // 32-bit Addr   //w/r + request     
                                                             
        jtag_selectir (AXI_IN); 
        jtag_senddr   (REG1_SIZE, {{2'b10}, {32'hDEADF003}, {32'h0000000C}, {2'b11}}, dr_out);  
                                // burst      // 64-bit Data      // 32-bit Addr   //w/r + request                                  

        // ------------------- reads -------------------                                  
        jtag_selectir (AXI_IN); 
        jtag_senddr   (REG1_SIZE, {{2'b10}, {32'h00000000}, {32'h00000000}, {2'b01}}, dr_out);  
                                  // burst      // 64-bit Data      // 32-bit Addr   //w/r + request      
                                  
        jtag_selectir (AXI_OUT);  
        jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);     
                                 // burst      // 64-bit Data      // 32-bit Addr   //w/r + request                               

        jtag_selectir (AXI_OUT);  
        jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);     
                                  // burst      // 64-bit Data      // 32-bit Addr   //w/r + request  
                                                                        
        jtag_selectir (AXI_OUT);  
        jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);     
                      // burst      // 64-bit Data      // 32-bit Addr   //w/r + request  

        jtag_selectir (AXI_OUT);  
        jtag_senddr   (REG2_SIZE, {REG2_SIZE{1'b0}}, dr_out);     
                      // burst      // 64-bit Data      // 32-bit Addr   //w/r + request                  

//        jtag_selectir (BYPASS);
//        jtag_senddr   (6'd32, 32'hDEADBEEF , dr_out);                          
    
    end        
    
    // 00: no burst
    // 01: fixed burst (address is the same)
    // 10: incr burst (address is incremented)
    // 11: reserved
                   
    always 
    begin
        #5 aclk = ~aclk;   // a 100MHz clock
    end
    
    initial 
    begin
            aresetn = 1'b1;
        #20 aresetn = 1'b0;
        #20 aresetn = 1'b1;
        
        #39960 $finish;
    end
    
  // **************************** reset ****************************
    task jtag_rst;
      integer halfperiod;
      begin
        if ($test$plusargs("debug"))
          $display("%t: rst start", $time);
        halfperiod = JTAG_PERIOD / 2;
        jtag_tck = 1'b0;
        jtag_tms = 1'b0;
        jtag_tck = #halfperiod 1'b1;    // first posedge on tck
        jtag_tck = #halfperiod 1'b0;    // first negedge on tck
        jtag_tms = 1'b1; 
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;
        jtag_tck = #halfperiod 1'b0;
        if ($test$plusargs("debug"))
          $display("%t: rst done", $time);
      end
    endtask
  
    // **************************** hard reset ****************************
    task jtag_hard_rst;
      integer halfperiod;
      begin
        if ($test$plusargs("debug"))
          $display("%t: hard rst start", $time);
  
        halfperiod = JTAG_PERIOD / 2;
        jtag_tck  = 1'b0;
        jtag_trst = 1'b0;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_trst = 1'b1;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_trst = 1'b1;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_trst = 1'b1;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_trst = 1'b1;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_trst = 1'b0;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_trst = 1'b0;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_trst = 1'b0;
        jtag_tck = #halfperiod 1'b0;
        if ($test$plusargs("debug"))
          $display("%t: hard rst end", $time);
  
      end
    endtask
  
    // **************************** select IR ****************************
    task jtag_selectir 
    (
      input [JTAG_IRLEN-1:0] instruction
    );
      integer                 halfperiod;
      integer                 i;
      begin
  //      if ($test$plusargs("debug"))
          $display("%t: select ir start, ir=0x%0h", $time, instruction);
  
        halfperiod = JTAG_PERIOD / 2;
        jtag_tck  = 1'b0; // TODO: buggy?
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;             //selectDR
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;             //selectIR
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //captureIR
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //shiftIR
        
  //      if ($test$plusargs("debug"))
          $display("%t: select ir capture start", $time);
        
        // shifting 5 bits into the IR
        for (i=0 ; i < JTAG_IRLEN ; i=i+1)
          begin
            jtag_tck = #halfperiod 1'b1;
            jtag_tck = #halfperiod 1'b0;
            if (i == (JTAG_IRLEN - 1) )
              jtag_tms = 1'b1;             //exit1IR
            else
              jtag_tms = 1'b0;             //shiftIR
            jtag_tdi = instruction[i];
          end
          
  //      if ($test$plusargs("debug"))
          $display("%t: select ir capture end", $time);
          
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //pauseIR
        jtag_tdi = 1'b0;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;             //exit2IR
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;             //updateIR
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //run-test-idle
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //run-test-idle
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //run-test-idle
  
        jtag_tck = #halfperiod 1'b0;
        
  //      if ($test$plusargs("debug"))
          $display("%t: select ir end", $time);
      end
    endtask
    
      // **************************** send DR ****************************
    task jtag_senddr (
      input integer number,   // input size of reg                    // 10, 11, 12
      input [127:0] data,     // input the data to be sent to DR      // 'h11, 'h22, 'h33
      output [127:0] dr_out   // the data received from DR            // 
      );
      integer       halfperiod;
      integer       i;
      logic [127:0] data_out;
      begin
  //      if ($test$plusargs("debug"))
          $display("%t: select dr start, dr=0x%0h", $time, data);
  
        data_out = 0;
        halfperiod = JTAG_PERIOD / 2;
        jtag_tck  = 1'b0;
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;             //selectDR
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //captureDR
        jtag_tck = #halfperiod 1'b1;
        
        // com/uncom
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //shiftDR
        
        for (i=0 ; i < number ; i=i+1)
          begin
            jtag_tck = #halfperiod 1'b1;
            if (i > 0)
              data_out[i-1] = jtag_tdo;
            jtag_tck = #halfperiod 1'b0;
            if (i == (number - 1) )
              jtag_tms = 1'b1;             //exit1DR
            else
              jtag_tms = 1'b0;             //shiftDR
            jtag_tdi = data[i];
          end
          
        jtag_tck = #halfperiod 1'b1;
        data_out[number-1] = jtag_tdo;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //pauseDR
        jtag_tdi = 1'b0;
        jtag_tck = #halfperiod 1'b1;
        // com/uncom
        
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;             //exit2DR
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b1;             //updateDR
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //run-test-idle
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //run-test-idle
        jtag_tck = #halfperiod 1'b1;
        jtag_tck = #halfperiod 1'b0;
        jtag_tms = 1'b0;             //run-test-idle (his comments not mine)
  
        jtag_tck = #halfperiod 1'b0;
        dr_out = data_out;
  //      if ($test$plusargs("debug"))
          $display("%t: data captured from register: 0x%0h", $time, data_out);
      end
    endtask

endmodule
