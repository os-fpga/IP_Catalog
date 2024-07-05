`timescale 1ns/1ps
`celldefine
//
// TDP_RAM36K simulation model
// 36Kb True-dual-port RAM
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module TDP_RAM36K #(
 /* verilator lint_off WIDTHCONCAT */
  parameter [32767:0] INIT = {32768{1'b0}}, // Initial Contents of memory
 /* verilator lint_on WIDTHCONCAT */
  parameter [4095:0] INIT_PARITY = {4096{1'b0}}, // Initial Contents of memory
  parameter WRITE_WIDTH_A = 36, // Write data width on port A (1, 2, 4, 9, 18, 36)
  parameter READ_WIDTH_A = WRITE_WIDTH_A, // Read data width on port A (1, 2, 4, 9, 18, 36)
  parameter WRITE_WIDTH_B = WRITE_WIDTH_A, // Write data width on port B (1, 2, 4, 9, 18, 36)
  parameter READ_WIDTH_B = READ_WIDTH_A // Read data width on port B (1, 2, 4, 9, 18, 36)
) (
  input WEN_A, // Write-enable port A
  input WEN_B, // Write-enable port B
  input REN_A, // Read-enable port A
  input REN_B, // Read-enable port B
  input CLK_A, // Clock port A
  input CLK_B, // Clock port B
  input [3:0] BE_A, // Byte-write enable port A
  input [3:0] BE_B, // Byte-write enable port B
  input [14:0] ADDR_A, // Address port A, align MSBs and connect unused MSBs to logic 0
  input [14:0] ADDR_B, // Address port B, align MSBs and connect unused MSBs to logic 0
  input [31:0] WDATA_A, // Write data port A
  input [3:0] WPARITY_A, // Write parity data port A
  input [31:0] WDATA_B, // Write data port B
  input [3:0] WPARITY_B, // Write parity port B
  output reg [31:0] RDATA_A = {32{1'b0}}, // Read data port A
  output reg [3:0] RPARITY_A = 4'h0, // Read parity port A
  output reg [31:0] RDATA_B = {32{1'b0}}, // Read data port B
  output reg [3:0] RPARITY_B = 4'h0 // Read parity port B
);

  localparam A_DATA_WRITE_WIDTH = calc_data_width(WRITE_WIDTH_A);
  localparam A_WRITE_ADDR_WIDTH = calc_depth(A_DATA_WRITE_WIDTH);
  localparam A_DATA_READ_WIDTH = calc_data_width(READ_WIDTH_A);
  localparam A_READ_ADDR_WIDTH = calc_depth(A_DATA_READ_WIDTH);
  localparam A_DATA_WIDTH = (A_DATA_WRITE_WIDTH > A_DATA_READ_WIDTH) ? A_DATA_WRITE_WIDTH : A_DATA_READ_WIDTH;

  localparam A_PARITY_WRITE_WIDTH = calc_parity_width(WRITE_WIDTH_A);
  localparam A_PARITY_READ_WIDTH = calc_parity_width(READ_WIDTH_A);
  localparam A_PARITY_WIDTH = (A_PARITY_WRITE_WIDTH > A_PARITY_READ_WIDTH) ? A_PARITY_WRITE_WIDTH : A_PARITY_READ_WIDTH;
  
  localparam B_DATA_WRITE_WIDTH = calc_data_width(WRITE_WIDTH_B);
  localparam B_WRITE_ADDR_WIDTH = calc_depth(B_DATA_WRITE_WIDTH);
  localparam B_DATA_READ_WIDTH = calc_data_width(READ_WIDTH_B);
  localparam B_READ_ADDR_WIDTH = calc_depth(B_DATA_READ_WIDTH);
  localparam B_DATA_WIDTH = (B_DATA_WRITE_WIDTH > B_DATA_READ_WIDTH) ? B_DATA_WRITE_WIDTH : B_DATA_READ_WIDTH;

  localparam B_PARITY_WRITE_WIDTH = calc_parity_width(WRITE_WIDTH_B);
  localparam B_PARITY_READ_WIDTH = calc_parity_width(READ_WIDTH_B);
  localparam B_PARITY_WIDTH = (B_PARITY_WRITE_WIDTH > B_PARITY_READ_WIDTH) ? B_PARITY_WRITE_WIDTH : B_PARITY_READ_WIDTH;

  localparam RAM_DATA_WIDTH = (A_DATA_WIDTH > B_DATA_WIDTH) ? A_DATA_WIDTH : B_DATA_WIDTH;
  localparam RAM_PARITY_WIDTH = (A_PARITY_WIDTH > B_PARITY_WIDTH) ? A_PARITY_WIDTH : B_PARITY_WIDTH;
  localparam RAM_ADDR_WIDTH = calc_depth(RAM_DATA_WIDTH);

  integer f, g, h, i, j, k, m;
  
  reg collision_window = 1;
  reg collision_a_write_flag = 0;                                   
  reg collision_b_write_flag = 0;                                   
  reg collision_a_read_flag = 0;                                   
  reg collision_b_read_flag = 0;                                   
  reg [RAM_ADDR_WIDTH-1:0] collision_a_address = {RAM_ADDR_WIDTH{1'b0}};                                   
  reg [RAM_ADDR_WIDTH-1:0] collision_b_address = {RAM_ADDR_WIDTH{1'b0}};
  
  wire [RAM_ADDR_WIDTH-1:0] a_addr = ADDR_A[14:15-RAM_ADDR_WIDTH];                                   
  wire [RAM_ADDR_WIDTH-1:0] b_addr = ADDR_B[14:15-RAM_ADDR_WIDTH];                                   
  
  reg [RAM_DATA_WIDTH-1:0] RAM_DATA [2**RAM_ADDR_WIDTH-1:0];

  /* verilator lint_off LITENDIAN */
  reg [RAM_PARITY_WIDTH-1:0] temp_WPARITY_A;
  reg [RAM_PARITY_WIDTH-1:0] temp_WPARITY_B;
  /* verilator lint_on LITENDIAN */
  reg [RAM_DATA_WIDTH-1:0] temp_WDATA_A;
  reg [RAM_DATA_WIDTH-1:0] temp_WDATA_B;
  
  generate
    if (RAM_PARITY_WIDTH > 0) begin: parity
      reg [RAM_PARITY_WIDTH-1:0] RAM_PARITY [2**RAM_ADDR_WIDTH-1:0];

      integer f_p, g_p, h_p, i_p, j_p, k_p, m_p;

      // Initialize PARITY RAM Contents
      initial begin
        f_p = 0;
        for (g_p = 0; g_p < 2**RAM_ADDR_WIDTH; g_p = g_p + 1)
          for (h_p = 0; h_p < RAM_PARITY_WIDTH; h_p = h_p + 1) begin
            `ifdef SIM_VERILATOR
              RAM_PARITY[g_p][h_p] = INIT_PARITY[f_p];
            `else
              RAM_PARITY[g_p][h_p] <= INIT_PARITY[f_p];
            `endif
            f_p = f_p + 1;
          end
      end

      always @(posedge CLK_A)
        if (WEN_A) begin
          for (i_p = find_a_write_index(ADDR_A)*A_PARITY_WRITE_WIDTH; i_p < find_a_write_index(ADDR_A)*A_PARITY_WRITE_WIDTH+A_PARITY_WRITE_WIDTH; i_p = i_p + 1) begin
            if (A_PARITY_WRITE_WIDTH > 1) begin
              //if (BE_A[i_p/8] == 1'b1)
              if (BE_A[i_p%5] == 1'b1) begin
                `ifdef SIM_VERILATOR
                  /* verilator lint_off WIDTH */
                  RAM_PARITY[a_addr][i_p] = WPARITY_A[i_p-(find_a_write_index(ADDR_A)*A_PARITY_WRITE_WIDTH)];
                  /* verilator lint_on WIDTH */
                `else
                  RAM_PARITY[a_addr][i_p] <= WPARITY_A[i_p-(find_a_write_index(ADDR_A)*A_PARITY_WRITE_WIDTH)];
                `endif
              end
            end
            else begin
              `ifdef SIM_VERILATOR
                /* verilator lint_off WIDTH */
                RAM_PARITY[a_addr][i_p] = WPARITY_A[i_p-(find_a_write_index(ADDR_A)*A_PARITY_WRITE_WIDTH)];
                /* verilator lint_on WIDTH */
              `else
                RAM_PARITY[a_addr][i_p] <= WPARITY_A[i_p-(find_a_write_index(ADDR_A)*A_PARITY_WRITE_WIDTH)];
              `endif
            end
          end
        end      

      always @(posedge CLK_A)
        if (REN_A) begin
          for (j_p = find_a_read_index(ADDR_A)*A_PARITY_READ_WIDTH; j_p < find_a_read_index(ADDR_A)*A_PARITY_READ_WIDTH+A_PARITY_READ_WIDTH; j_p = j_p + 1) begin
            `ifdef SIM_VERILATOR
              RPARITY_A[j_p-(find_a_read_index(ADDR_A)*A_PARITY_READ_WIDTH)] = RAM_PARITY[a_addr][j_p];
            `else
              RPARITY_A[j_p-(find_a_read_index(ADDR_A)*A_PARITY_READ_WIDTH)] <= RAM_PARITY[a_addr][j_p];
            `endif
          end
        end
        else begin
          `ifdef SIM_VERILATOR
            RPARITY_A = 4'bx;
          `else
            RPARITY_A <= 4'bx;
          `endif
        end

      always @(posedge CLK_B)
        if (WEN_B) begin
          for (k_p = find_b_write_index(ADDR_B)*B_PARITY_WRITE_WIDTH; k_p < find_b_write_index(ADDR_B)*B_PARITY_WRITE_WIDTH+B_PARITY_WRITE_WIDTH; k_p = k_p + 1) begin
            if (B_PARITY_WRITE_WIDTH > 1) begin
              //if (BE_B[k_p/8] == 1'b1)
              if (BE_B[k_p%5] == 1'b1) begin
                `ifdef SIM_VERILATOR
                  /* verilator lint_off WIDTH */
                  RAM_PARITY[b_addr][k_p] = WPARITY_B[k_p-(find_b_write_index(ADDR_B)*B_PARITY_WRITE_WIDTH)];
                  /* verilator lint_on WIDTH */
                `else
                  RAM_PARITY[b_addr][k_p] <= WPARITY_B[k_p-(find_b_write_index(ADDR_B)*B_PARITY_WRITE_WIDTH)];
                `endif
              end
            end
            else begin
              `ifdef SIM_VERILATOR
                /* verilator lint_off WIDTH */
                RAM_PARITY[b_addr][k_p] = WPARITY_B[k_p-(find_b_write_index(ADDR_B)*B_PARITY_WRITE_WIDTH)];
                /* verilator lint_on WIDTH */
              `else
                RAM_PARITY[b_addr][k_p] <= WPARITY_B[k_p-(find_b_write_index(ADDR_B)*B_PARITY_WRITE_WIDTH)];
              `endif
            end
          end
        end      

      always @(posedge CLK_B)
        if (REN_B) begin
          for (m_p = find_b_read_index(ADDR_B)*B_PARITY_READ_WIDTH; m_p < find_b_read_index(ADDR_B)*B_PARITY_READ_WIDTH+B_PARITY_READ_WIDTH; m_p = m_p + 1) begin
            `ifdef SIM_VERILATOR
              RPARITY_B[m_p-(find_b_read_index(ADDR_B)*B_PARITY_READ_WIDTH)] = RAM_PARITY[b_addr][m_p];
            `else
              RPARITY_B[m_p-(find_b_read_index(ADDR_B)*B_PARITY_READ_WIDTH)] <= RAM_PARITY[b_addr][m_p];
            `endif
          end
        end
        else begin
          `ifdef SIM_VERILATOR
            RPARITY_B = 4'bx;
          `else
            RPARITY_B <= 4'bx;
          `endif
        end

    end
  endgenerate

  // Initialize RAM contents
  initial begin
    f = 0;
    for (g = 0; g < 2**RAM_ADDR_WIDTH; g = g + 1)
      for (h = 0; h < RAM_DATA_WIDTH; h = h + 1) begin
        `ifdef SIM_VERILATOR
          RAM_DATA[g][h] = INIT[f];
        `else
          RAM_DATA[g][h] <= INIT[f];
        `endif
        f = f + 1;
      end
  end
  
 // Base RAM read/write functionality
  always @(posedge CLK_A)
    if (WEN_A) begin
      //$display("AADR_A: %b   index: %d", ADDR_A, find_a_write_index(ADDR_A)*8);
      for (i = find_a_write_index(ADDR_A)*A_DATA_WRITE_WIDTH; i < find_a_write_index(ADDR_A)*A_DATA_WRITE_WIDTH+A_DATA_WRITE_WIDTH; i = i + 1)
        if (A_DATA_WRITE_WIDTH > 9) begin
          if (BE_A[i/8] == 1'b1) begin
            `ifdef SIM_VERILATOR
              /* verilator lint_off WIDTH */
              RAM_DATA[a_addr][i] = WDATA_A[i-(find_a_write_index(ADDR_A)*A_DATA_WRITE_WIDTH)];
              /* verilator lint_on WIDTH */
            `else
              RAM_DATA[a_addr][i] <= WDATA_A[i-(find_a_write_index(ADDR_A)*A_DATA_WRITE_WIDTH)];
            `endif
          end
        end
        else begin
          `ifdef SIM_VERILATOR
            /* verilator lint_off WIDTH */
            RAM_DATA[a_addr][i] = WDATA_A[i-(find_a_write_index(ADDR_A)*A_DATA_WRITE_WIDTH)];
            /* verilator lint_on WIDTH */
          `else
            RAM_DATA[a_addr][i] <= WDATA_A[i-(find_a_write_index(ADDR_A)*A_DATA_WRITE_WIDTH)];
          `endif
        end
      collision_a_address = a_addr;
      collision_a_write_flag = 1;
      #collision_window;
      collision_a_write_flag = 0;
    end      

  always @(posedge CLK_A)
    if (REN_A) begin
      for (j = find_a_read_index(ADDR_A)*A_DATA_READ_WIDTH; j < find_a_read_index(ADDR_A)*A_DATA_READ_WIDTH+A_DATA_READ_WIDTH; j = j + 1) begin
        `ifdef SIM_VERILATOR
          RDATA_A[j-(find_a_read_index(ADDR_A)*A_DATA_READ_WIDTH)] = RAM_DATA[a_addr][j];
        `else
          RDATA_A[j-(find_a_read_index(ADDR_A)*A_DATA_READ_WIDTH)] <= RAM_DATA[a_addr][j];
        `endif
      end
      collision_a_address = a_addr;
      collision_a_read_flag = 1;
      #collision_window;
      collision_a_read_flag = 0;
    end
    else begin
      `ifdef SIM_VERILATOR
        RDATA_A = 32'bx;
      `else
        RDATA_A <= 32'bx;
      `endif
    end

  always @(posedge CLK_B)
    if (WEN_B) begin
      for (k = find_b_write_index(ADDR_B)*B_DATA_WRITE_WIDTH; k < find_b_write_index(ADDR_B)*B_DATA_WRITE_WIDTH+B_DATA_WRITE_WIDTH; k = k + 1)
      if (B_DATA_WRITE_WIDTH > 9) begin
        if (BE_B[k/8] == 1'b1) begin
          `ifdef SIM_VERILATOR
            /* verilator lint_off WIDTH */
            RAM_DATA[b_addr][k] = WDATA_B[k-(find_b_write_index(ADDR_B)*B_DATA_WRITE_WIDTH)];
            /* verilator lint_on WIDTH */
          `else
            RAM_DATA[b_addr][k] <= WDATA_B[k-(find_b_write_index(ADDR_B)*B_DATA_WRITE_WIDTH)];
          `endif
        end
      end
      else begin
        `ifdef SIM_VERILATOR
          /* verilator lint_off WIDTH */
          RAM_DATA[b_addr][k] = WDATA_B[k-(find_b_write_index(ADDR_B)*B_DATA_WRITE_WIDTH)];
          /* verilator lint_on WIDTH */
        `else
          RAM_DATA[b_addr][k] <= WDATA_B[k-(find_b_write_index(ADDR_B)*B_DATA_WRITE_WIDTH)];
        `endif
      end
      collision_b_address = b_addr;
      collision_b_write_flag = 1;
      #collision_window;
      collision_b_write_flag = 0;
    end      

  always @(posedge CLK_B)
    if (REN_B) begin
      //$display("index: %d  b_addr: %h ADDR_B: %h", find_b_read_index(ADDR_B), b_addr, ADDR_B);
      for (m = find_b_read_index(ADDR_B)*B_DATA_READ_WIDTH; m < find_b_read_index(ADDR_B)*B_DATA_READ_WIDTH+B_DATA_READ_WIDTH; m = m + 1) begin
        `ifdef SIM_VERILATOR
          RDATA_B[m-(find_b_read_index(ADDR_B)*B_DATA_READ_WIDTH)] = RAM_DATA[b_addr][m];
        `else
          RDATA_B[m-(find_b_read_index(ADDR_B)*B_DATA_READ_WIDTH)] <= RAM_DATA[b_addr][m];
        `endif
      end
      collision_b_address = b_addr;
      collision_b_read_flag = 1;
      #collision_window;
      collision_b_read_flag = 0;
    end
    else begin
      `ifdef SIM_VERILATOR
        RDATA_B = 32'bx;
      `else
        RDATA_B <= 32'bx;
      `endif
    end


/*
  always @(posedge CLK_B)
    if (WEN_B) begin
      //$display("AADR_B: %b   index: %d", ADDR_B, find_b_write_index(ADDR_B));
      for (k = find_b_write_index(ADDR_B); k < find_b_write_index(ADDR_B)+WRITE_WIDTH_B; k = k + 1)
        if (BE_B[k/9] == 1'b1)
          RAM[b_addr][k] <= WDATA_B[k-find_b_write_index(ADDR_B)];
      collision_b_address = b_addr;
      collision_b_write_flag = 1;
      #collision_window;
      collision_b_write_flag = 0;
    end      

  always @(posedge CLK_B)
    if (REN_B) begin
      for (m = find_b_read_index(ADDR_B); m < find_b_read_index(ADDR_B)+READ_WIDTH_B; m = m + 1)
        RDATA_B[m-find_b_read_index(ADDR_B)] <= RAM[b_addr][m];
      collision_b_address = b_addr;
      collision_b_read_flag = 1;
      #collision_window;
      collision_b_read_flag = 0;
    end      
 */
 
  // Collision checking
  always @(posedge collision_a_write_flag) begin
    if (collision_b_write_flag && (collision_a_address == collision_b_address)) begin
      $display("ERROR: Write collision occured on TDP_RAM36K instance %m at time %t where port A is writing to the same address, %h, as port B.\n       The write data may not be valid.", $realtime, collision_a_address);
      collision_a_write_flag = 0;
    end
    if (collision_b_read_flag && (collision_a_address == collision_b_address)) begin
      $display("ERROR: Memory collision occured on TDP_RAM36K instance %m at time %t where port A is writing to the same address, %h, as port B is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b_address);
      collision_a_write_flag = 0;
    end
  end
   
  always @(posedge collision_a_read_flag) begin
    if (collision_b_write_flag && (collision_a_address == collision_b_address))
      $display("ERROR: Memory collision occured on TDP_RAM36K instance %m at time %t where port B is writing to the same address, %h, as port A is reading.\n       The write data is valid but the read data is not.", $realtime, collision_a_address);
      collision_a_read_flag = 0;
    end
    
  always @(posedge collision_b_write_flag) begin
    if (collision_a_write_flag && (collision_a_address == collision_b_address)) begin
      $display("ERROR: Write collision occured on TDP_RAM36K instance %m at time %t where port B is writing to the same address, %h, as port A.\n       The write data may not be valid.", $realtime, collision_b_address);
      collision_b_write_flag = 0;   
    end
    if (collision_a_read_flag && (collision_a_address == collision_b_address)) begin
      $display("ERROR: Memory collision occured on TDP_RAM36K instance %m at time %t where port B is writing to the same address, %h, as port A is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b_address);
      collision_b_write_flag = 0;
    end
  end

  always @(posedge collision_b_read_flag) begin
    if (collision_a_write_flag && (collision_a_address == collision_b_address)) begin
      $display("ERROR: Memory collision occured on TDP_RAM36K instance %m at time %t where port A is writing to the same address, %h, as port B is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b_address);
      collision_b_read_flag = 0;
    end
  end



  function integer find_a_write_index;
    input [14:0] addr;
    
    if (RAM_ADDR_WIDTH == A_WRITE_ADDR_WIDTH)
      find_a_write_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */
      find_a_write_index = ADDR_A[14-RAM_ADDR_WIDTH:15-A_WRITE_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_a_read_index;
    input [14:0] addr;
    
    if (RAM_ADDR_WIDTH == A_READ_ADDR_WIDTH)
      find_a_read_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */
      find_a_read_index = ADDR_A[14-RAM_ADDR_WIDTH:15-A_READ_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_b_write_index;
    input [14:0] addr;
    
    if (RAM_ADDR_WIDTH == B_WRITE_ADDR_WIDTH)
      find_b_write_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */
      find_b_write_index = ADDR_B[14-RAM_ADDR_WIDTH:15-B_WRITE_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_b_read_index;
    input [14:0] addr;
    
    if (RAM_ADDR_WIDTH == B_READ_ADDR_WIDTH)
      find_b_read_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */
      find_b_read_index = ADDR_B[14-RAM_ADDR_WIDTH:15-B_READ_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer calc_data_width;
    input integer width;
    if (width==9)
      calc_data_width = 8;
    else if (width==18) 
      calc_data_width = 16;
    else if (width==27) 
      calc_data_width = 24;
    else if (width==36) 
      calc_data_width = 32;
    else
      calc_data_width = width;
  endfunction

  function integer calc_parity_width;
    input integer width;
    if (width==9)
      calc_parity_width = 1;
    else if (width==18) 
      calc_parity_width = 2;
    else if (width==27) 
      calc_parity_width = 3;
    else if (width==36) 
      calc_parity_width = 4;
    else
      calc_parity_width = 0;
  endfunction

  function integer calc_depth;
    input integer width;
    if (width<=1)
      calc_depth = 15;
    else if (width<=2) 
      calc_depth = 14;
    else if (width<=4) 
      calc_depth = 13;
    else if (width<=9) 
      calc_depth = 12;
    else if (width<=18) 
      calc_depth = 11;
    else if (width<=36) 
      calc_depth = 10;
    else
      calc_depth = 0;
  endfunction

  initial
    $timeformat(-9,0," ns", 5);

     initial begin
    case(WRITE_WIDTH_A)
      1 ,
      2 ,
      4 ,
      9 ,
      18 ,
      36: begin end
      default: begin
        $display("\nError: TDP_RAM36K instance %m has parameter WRITE_WIDTH_A set to %d.  Valid values are 1, 2, 4, 9, 18, 36\n", WRITE_WIDTH_A);
        #1 $stop ;
      end
    endcase
    case(READ_WIDTH_A)
      1 ,
      2 ,
      4 ,
      9 ,
      18 ,
      36: begin end
      default: begin
        $display("\nError: TDP_RAM36K instance %m has parameter READ_WIDTH_A set to %d.  Valid values are 1, 2, 4, 9, 18, 36\n", READ_WIDTH_A);
        #1 $stop ;
      end
    endcase
    case(WRITE_WIDTH_B)
      1 ,
      2 ,
      4 ,
      9 ,
      18 ,
      36: begin end
      default: begin
        $display("\nError: TDP_RAM36K instance %m has parameter WRITE_WIDTH_B set to %d.  Valid values are 1, 2, 4, 9, 18, 36\n", WRITE_WIDTH_B);
        #1 $stop ;
      end
    endcase
    case(READ_WIDTH_B)
      1 ,
      2 ,
      4 ,
      9 ,
      18 ,
      36: begin end
      default: begin
        $display("\nError: TDP_RAM36K instance %m has parameter READ_WIDTH_B set to %d.  Valid values are 1, 2, 4, 9, 18, 36\n", READ_WIDTH_B);
        #1 $stop ;
      end
    endcase

  end

endmodule
`endcelldefine