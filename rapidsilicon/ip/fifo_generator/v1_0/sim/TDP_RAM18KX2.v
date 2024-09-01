`timescale 1ns/1ps
`celldefine
//
// TDP_RAM18KX2 simulation model
// Dual 18Kb True-dual-port RAM
//
// Copyright (c) 2023 Rapid Silicon, Inc.  All rights reserved.
//

module TDP_RAM18KX2 #(
 /* verilator lint_off WIDTHCONCAT */
  parameter [16383:0] INIT1 = {16384{1'b0}}, // Initial Contents of data memory, RAM 1
 /* verilator lint_on WIDTHCONCAT */
  parameter [2047:0] INIT1_PARITY = {2048{1'b0}}, // Initial Contents of parity memory, RAM 1
  parameter WRITE_WIDTH_A1 = 18, // Write data width on port A, RAM 1 (1, 2, 4, 9, 18)
  parameter WRITE_WIDTH_B1 = 18, // Write data width on port B, RAM 1 (1, 2, 4, 9, 18)
  parameter READ_WIDTH_A1 = 18, // Read data width on port A, RAM 1 (1, 2, 4, 9, 18)
  parameter READ_WIDTH_B1 = 18, // Read data width on port B, RAM 1 (1, 2, 4, 9, 18)
 /* verilator lint_off WIDTHCONCAT */
  parameter [16383:0] INIT2 = {16384{1'b0}}, // Initial Contents of memory, RAM 2
 /* verilator lint_on WIDTHCONCAT */
  parameter [2047:0] INIT2_PARITY = {2048{1'b0}}, // Initial Contents of memory, RAM 2
  parameter WRITE_WIDTH_A2 = 18, // Write data width on port A, RAM 2 (1, 2, 4, 9, 18)
  parameter WRITE_WIDTH_B2 = 18, // Write data width on port B, RAM 2 (1, 2, 4, 9, 18)
  parameter READ_WIDTH_A2 = 18, // Read data width on port A, RAM 2 (1, 2, 4, 9, 18)
  parameter READ_WIDTH_B2 = 18 // Read data width on port B, RAM 2 (1, 2, 4, 9, 18)
) (
  input WEN_A1, // Write-enable port A, RAM 1
  input WEN_B1, // Write-enable port B, RAM 1
  input REN_A1, // Read-enable port A, RAM 1
  input REN_B1, // Read-enable port B, RAM 1
  input CLK_A1, // Clock port A, RAM 1
  input CLK_B1, // Clock port B, RAM 1
  input [1:0] BE_A1, // Byte-write enable port A, RAM 1
  input [1:0] BE_B1, // Byte-write enable port B, RAM 1
  input [13:0] ADDR_A1, // Address port A, RAM 1
  input [13:0] ADDR_B1, // Address port B, RAM 1
  input [15:0] WDATA_A1, // Write data port A, RAM 1
  input [1:0] WPARITY_A1, // Write parity port A, RAM 1
  input [15:0] WDATA_B1, // Write data port B, RAM 1
  input [1:0] WPARITY_B1, // Write parity port B, RAM 1
  output reg [15:0] RDATA_A1 = {16{1'b0}}, // Read data port A, RAM 1
  output reg [1:0] RPARITY_A1 = {2{1'b0}}, // Read parity port A, RAM 1
  output reg [15:0] RDATA_B1 = {16{1'b0}}, // Read data port B, RAM 1
  output reg [1:0] RPARITY_B1 = {2{1'b0}}, // Read parity port B, RAM 1
  input WEN_A2, // Write-enable port A, RAM 2
  input WEN_B2, // Write-enable port B, RAM 2
  input REN_A2, // Read-enable port A, RAM 2
  input REN_B2, // Read-enable port B, RAM 2
  input CLK_A2, // Clock port A, RAM 2
  input CLK_B2, // Clock port B, RAM 2
  input [1:0] BE_A2, // Byte-write enable port A, RAM 2
  input [1:0] BE_B2, // Byte-write enable port B, RAM 2
  input [13:0] ADDR_A2, // Address port A, RAM 2
  input [13:0] ADDR_B2, // Address port B, RAM 2
  input [15:0] WDATA_A2, // Write data port A, RAM 2
  input [1:0] WPARITY_A2, // Write parity port A, RAM 2
  input [15:0] WDATA_B2, // Write data port B, RAM 2
  input [1:0] WPARITY_B2, // Write parity port B, RAM 2
  output reg [15:0] RDATA_A2 = {16{1'b0}}, // Read data port A, RAM 2
  output reg [1:0] RPARITY_A2 = {2{1'b0}}, // Read parity port A, RAM 2
  output reg [15:0] RDATA_B2 = {16{1'b0}}, // Read data port B, RAM 2
  output reg [1:0] RPARITY_B2 = {2{1'b0}} // Read parity port B, RAM 2
);
	
	
	//RAM1
	localparam A1_DATA_WRITE_WIDTH = calc_data_width(WRITE_WIDTH_A1);
  localparam A1_WRITE_ADDR_WIDTH = calc_depth(A1_DATA_WRITE_WIDTH);
  localparam A1_DATA_READ_WIDTH = calc_data_width(READ_WIDTH_A1);
  localparam A1_READ_ADDR_WIDTH = calc_depth(A1_DATA_READ_WIDTH);
  localparam A1_DATA_WIDTH = (A1_DATA_WRITE_WIDTH > A1_DATA_READ_WIDTH) ? A1_DATA_WRITE_WIDTH : A1_DATA_READ_WIDTH;

  localparam A1_PARITY_WRITE_WIDTH = calc_parity_width(WRITE_WIDTH_A1);
  localparam A1_PARITY_READ_WIDTH = calc_parity_width(READ_WIDTH_A1);
  localparam A1_PARITY_WIDTH = (A1_PARITY_WRITE_WIDTH > A1_PARITY_READ_WIDTH) ? A1_PARITY_WRITE_WIDTH : A1_PARITY_READ_WIDTH;
  
  localparam B1_DATA_WRITE_WIDTH = calc_data_width(WRITE_WIDTH_B1);
  localparam B1_WRITE_ADDR_WIDTH = calc_depth(B1_DATA_WRITE_WIDTH);
  localparam B1_DATA_READ_WIDTH = calc_data_width(READ_WIDTH_B1);
  localparam B1_READ_ADDR_WIDTH = calc_depth(B1_DATA_READ_WIDTH);
  localparam B1_DATA_WIDTH = (B1_DATA_WRITE_WIDTH > B1_DATA_READ_WIDTH) ? B1_DATA_WRITE_WIDTH : B1_DATA_READ_WIDTH;

  localparam B1_PARITY_WRITE_WIDTH = calc_parity_width(WRITE_WIDTH_B1);
  localparam B1_PARITY_READ_WIDTH = calc_parity_width(READ_WIDTH_B1);
  localparam B1_PARITY_WIDTH = (B1_PARITY_WRITE_WIDTH > B1_PARITY_READ_WIDTH) ? B1_PARITY_WRITE_WIDTH : B1_PARITY_READ_WIDTH;

  localparam RAM1_DATA_WIDTH = (A1_DATA_WIDTH > B1_DATA_WIDTH) ? A1_DATA_WIDTH : B1_DATA_WIDTH;
  localparam RAM1_PARITY_WIDTH = (A1_PARITY_WIDTH > B1_PARITY_WIDTH) ? A1_PARITY_WIDTH : B1_PARITY_WIDTH;
  localparam RAM1_ADDR_WIDTH = calc_depth(RAM1_DATA_WIDTH);

	integer f, g, h, i, j, k, m;
  
  reg collision_window = 1;
  reg collision_a_write_flag = 0;                                   
  reg collision_b_write_flag = 0;                                   
  reg collision_a_read_flag = 0;                                   
  reg collision_b_read_flag = 0;                                   
  reg [RAM1_ADDR_WIDTH-1:0] collision_a_address = {RAM1_ADDR_WIDTH{1'b0}};                                   
  reg [RAM1_ADDR_WIDTH-1:0] collision_b_address = {RAM1_ADDR_WIDTH{1'b0}};

	wire [RAM1_ADDR_WIDTH-1:0] a1_addr = ADDR_A1[13:14-RAM1_ADDR_WIDTH];                                 
  wire [RAM1_ADDR_WIDTH-1:0] b1_addr = ADDR_B1[13:14-RAM1_ADDR_WIDTH];                                  
  
  reg [RAM1_DATA_WIDTH-1:0] RAM1_DATA [2**RAM1_ADDR_WIDTH-1:0];

  /* verilator lint_off LITENDIAN */
  reg [RAM1_PARITY_WIDTH-1:0] temp_WPARITY_A1;
  reg [RAM1_PARITY_WIDTH-1:0] temp_WPARITY_B1;
  /* verilator lint_on LITENDIAN */
  reg [RAM1_DATA_WIDTH-1:0] temp_WDATA_A1;
  reg [RAM1_DATA_WIDTH-1:0] temp_WDATA_B1;

  generate
    if (RAM1_PARITY_WIDTH > 0) begin: parity_RAM1
      reg [RAM1_PARITY_WIDTH-1:0] RAM1_PARITY [2**RAM1_ADDR_WIDTH-1:0];

      integer f_p, g_p, h_p, i_p, j_p, k_p, m_p;

      // Initialize Parity RAM contents
      initial begin
        f_p = 0;
        for (g_p = 0; g_p < 2**RAM1_ADDR_WIDTH; g_p = g_p + 1)
          for (h_p = 0; h_p < RAM1_PARITY_WIDTH; h_p = h_p + 1) begin
            `ifdef SIM_VERILATOR
              RAM1_PARITY[g_p][h_p] = INIT1_PARITY[f_p];
            `else
              RAM1_PARITY[g_p][h_p] <= INIT1_PARITY[f_p];
            `endif
            f_p = f_p + 1;
          end
      end

      always @(posedge CLK_A1)
        if (WEN_A1) begin
          for (i_p = find_a1_write_index(ADDR_A1)*A1_PARITY_WRITE_WIDTH; i_p < find_a1_write_index(ADDR_A1)*A1_PARITY_WRITE_WIDTH+A1_PARITY_WRITE_WIDTH; i_p = i_p + 1) begin
            if (A1_PARITY_WRITE_WIDTH > 1) begin
              if (BE_A1[i_p/1] == 1'b1) begin
                `ifdef SIM_VERILATOR
                  /* verilator lint_off WIDTH */
                RAM1_PARITY[a1_addr][i_p] = WPARITY_A1[i_p-(find_a1_write_index(ADDR_A1)*A1_PARITY_WRITE_WIDTH)];
                  /* verilator lint_on WIDTH */
                `else
                  RAM1_PARITY[a1_addr][i_p] <= WPARITY_A1[i_p-(find_a1_write_index(ADDR_A1)*A1_PARITY_WRITE_WIDTH)];
                `endif
              end
            end
            else begin
              `ifdef SIM_VERILATOR
              /* verilator lint_off WIDTH */
              RAM1_PARITY[a1_addr][i_p] = WPARITY_A1[i_p-(find_a1_write_index(ADDR_A1)*A1_PARITY_WRITE_WIDTH)];
              /* verilator lint_on WIDTH */
            `else
              RAM1_PARITY[a1_addr][i_p] <= WPARITY_A1[i_p-(find_a1_write_index(ADDR_A1)*A1_PARITY_WRITE_WIDTH)];
              //$display("i_p: %0h, [i_p/1] %0h", i_p, i_p/2,$time);
            `endif
            end
          end
        end      

      always @(posedge CLK_A1)
        if (REN_A1) begin
          for (j_p = find_a1_read_index(ADDR_A1)*A1_PARITY_READ_WIDTH; j_p < find_a1_read_index(ADDR_A1)*A1_PARITY_READ_WIDTH+A1_PARITY_READ_WIDTH; j_p = j_p + 1) begin
            `ifdef SIM_VERILATOR
              RPARITY_A1[j_p-(find_a1_read_index(ADDR_A1)*A1_PARITY_READ_WIDTH)] = RAM1_PARITY[a1_addr][j_p];
            `else
              RPARITY_A1[j_p-(find_a1_read_index(ADDR_A1)*A1_PARITY_READ_WIDTH)] <= RAM1_PARITY[a1_addr][j_p];
            `endif
          end
        end
        else
          `ifndef FIFO
            // verilator lint_off BLKANDNBLK
            RPARITY_A1 <= 2'bx;
            // verilator lint_on BLKANDNBLK
          `endif

      always @(posedge CLK_B1)
        if (WEN_B1) begin
          for (k_p = find_b1_write_index(ADDR_B1)*B1_PARITY_WRITE_WIDTH; k_p < find_b1_write_index(ADDR_B1)*B1_PARITY_WRITE_WIDTH+B1_PARITY_WRITE_WIDTH; k_p = k_p + 1) begin
            if (B1_PARITY_WRITE_WIDTH > 1) begin
              if (BE_B1[k_p/1] == 1'b1) begin
                `ifdef SIM_VERILATOR
                  /* verilator lint_off WIDTH */
                  RAM1_PARITY[b1_addr][k_p] = WPARITY_B1[k_p-(find_b1_write_index(ADDR_B1)*B1_PARITY_WRITE_WIDTH)];
                  /* verilator lint_on WIDTH */
                `else
                  RAM1_PARITY[b1_addr][k_p] <= WPARITY_B1[k_p-(find_b1_write_index(ADDR_B1)*B1_PARITY_WRITE_WIDTH)];
                `endif
              end
            end
            else begin
              `ifdef SIM_VERILATOR
                /* verilator lint_off WIDTH */
                RAM1_PARITY[b1_addr][k_p] = WPARITY_B1[k_p-(find_b1_write_index(ADDR_B1)*B1_PARITY_WRITE_WIDTH)];
                /* verilator lint_on WIDTH */
              `else
                RAM1_PARITY[b1_addr][k_p] <= WPARITY_B1[k_p-(find_b1_write_index(ADDR_B1)*B1_PARITY_WRITE_WIDTH)];
              `endif
            end
          end
        end

      always @(posedge CLK_B1)
        if (REN_B1) begin
          for (m_p = find_b1_read_index(ADDR_B1)*B1_PARITY_READ_WIDTH; m_p < find_b1_read_index(ADDR_B1)*B1_PARITY_READ_WIDTH+B1_PARITY_READ_WIDTH; m_p = m_p + 1) begin
            `ifdef SIM_VERILATOR
              RPARITY_B1[m_p-(find_b1_read_index(ADDR_B1)*B1_PARITY_READ_WIDTH)] = RAM1_PARITY[b1_addr][m_p];
            `else
              RPARITY_B1[m_p-(find_b1_read_index(ADDR_B1)*B1_PARITY_READ_WIDTH)] <= RAM1_PARITY[b1_addr][m_p];
            `endif
          end
        end
        else
          `ifndef FIFO
            // verilator lint_off BLKANDNBLK
            RPARITY_B1 <= 2'bx;
            // verilator lint_on BLKANDNBLK
          `endif
    end
  endgenerate

	// Initialize Base RAM contents
  initial begin
    f = 0;
    for (g = 0; g < 2**RAM1_ADDR_WIDTH; g = g + 1)
      for (h = 0; h < RAM1_DATA_WIDTH; h = h + 1) begin
        `ifdef SIM_VERILATOR
          RAM1_DATA[g][h] = INIT1[f];
        `else
          RAM1_DATA[g][h] <= INIT1[f];
        `endif
        f = f + 1;
      end
  end
  
 // Base RAM read/write functionality
  always @(posedge CLK_A1)
    if (WEN_A1) begin
      //$display("AADR_A: %b   index: %d", ADDR_A1, find_a1_write_index(ADDR_A1)*8);
      for (i = find_a1_write_index(ADDR_A1)*A1_DATA_WRITE_WIDTH; i < find_a1_write_index(ADDR_A1)*A1_DATA_WRITE_WIDTH+A1_DATA_WRITE_WIDTH; i = i + 1) begin
        if (A1_DATA_WRITE_WIDTH > 9) begin
          if (BE_A1[i/8] == 1'b1) begin
            `ifdef SIM_VERILATOR
              /* verilator lint_off WIDTH */
              RAM1_DATA[a1_addr][i] = WDATA_A1[i-(find_a1_write_index(ADDR_A1)*A1_DATA_WRITE_WIDTH)];
              /* verilator lint_on WIDTH */
            `else
              RAM1_DATA[a1_addr][i] <= WDATA_A1[i-(find_a1_write_index(ADDR_A1)*A1_DATA_WRITE_WIDTH)];
            `endif
          end
        end
        else begin
          `ifdef SIM_VERILATOR
            /* verilator lint_off WIDTH */
            RAM1_DATA[a1_addr][i] = WDATA_A1[i-(find_a1_write_index(ADDR_A1)*A1_DATA_WRITE_WIDTH)];
            /* verilator lint_on WIDTH */
          `else
            RAM1_DATA[a1_addr][i] <= WDATA_A1[i-(find_a1_write_index(ADDR_A1)*A1_DATA_WRITE_WIDTH)];
          `endif
        end
      end
      collision_a_address = a1_addr;
      collision_a_write_flag = 1;
      #collision_window;
      collision_a_write_flag = 0;
    end      

  always @(posedge CLK_A1)
    if (REN_A1) begin
      for (j = find_a1_read_index(ADDR_A1)*A1_DATA_READ_WIDTH; j < find_a1_read_index(ADDR_A1)*A1_DATA_READ_WIDTH+A1_DATA_READ_WIDTH; j = j + 1) begin
        `ifdef SIM_VERILATOR
          RDATA_A1[j-(find_a1_read_index(ADDR_A1)*A1_DATA_READ_WIDTH)] = RAM1_DATA[a1_addr][j];
        `else
          RDATA_A1[j-(find_a1_read_index(ADDR_A1)*A1_DATA_READ_WIDTH)] <= RAM1_DATA[a1_addr][j];
        `endif
      end
      collision_a_address = a1_addr;
      collision_a_read_flag = 1;
      #collision_window;
      collision_a_read_flag = 0;
    end
    else
      `ifndef FIFO
        // verilator lint_off BLKANDNBLK
        RDATA_A1 <= 16'bx;
        // verilator lint_on BLKANDNBLK
      `endif

  always @(posedge CLK_B1)
    if (WEN_B1) begin
      for (k = find_b1_write_index(ADDR_B1)*B1_DATA_WRITE_WIDTH; k < find_b1_write_index(ADDR_B1)*B1_DATA_WRITE_WIDTH+B1_DATA_WRITE_WIDTH; k = k + 1) begin
        if (B1_DATA_WRITE_WIDTH > 9) begin
          if (BE_B1[k/8] == 1'b1) begin
            `ifdef SIM_VERILATOR
              /* verilator lint_off WIDTH */
              RAM1_DATA[b1_addr][k] = WDATA_B1[k-(find_b1_write_index(ADDR_B1)*B1_DATA_WRITE_WIDTH)];
              /* verilator lint_on WIDTH */
            `else
              RAM1_DATA[b1_addr][k] <= WDATA_B1[k-(find_b1_write_index(ADDR_B1)*B1_DATA_WRITE_WIDTH)];
            `endif
          end
        end
        else begin
          `ifdef SIM_VERILATOR
            /* verilator lint_off WIDTH */
            RAM1_DATA[b1_addr][k] = WDATA_B1[k-(find_b1_write_index(ADDR_B1)*B1_DATA_WRITE_WIDTH)];
            /* verilator lint_on WIDTH */
          `else
            RAM1_DATA[b1_addr][k] <= WDATA_B1[k-(find_b1_write_index(ADDR_B1)*B1_DATA_WRITE_WIDTH)];
          `endif
        end
        
      end
      collision_b_address = b1_addr;
      collision_b_write_flag = 1;
      #collision_window;
      collision_b_write_flag = 0;
    end

  always @(posedge CLK_B1)
    if (REN_B1) begin
      //$display("index: %d  b1_addr: %h ADDR_B1: %h", find_b1_read_index(ADDR_B1), b1_addr, ADDR_B1);
      for (m = find_b1_read_index(ADDR_B1)*B1_DATA_READ_WIDTH; m < find_b1_read_index(ADDR_B1)*B1_DATA_READ_WIDTH+B1_DATA_READ_WIDTH; m = m + 1) begin
        `ifdef SIM_VERILATOR
          RDATA_B1[m-(find_b1_read_index(ADDR_B1)*B1_DATA_READ_WIDTH)] = RAM1_DATA[b1_addr][m];
        `else
          RDATA_B1[m-(find_b1_read_index(ADDR_B1)*B1_DATA_READ_WIDTH)] <= RAM1_DATA[b1_addr][m];
        `endif
      end
      collision_b_address = b1_addr;
      collision_b_read_flag = 1;
      #collision_window;
      collision_b_read_flag = 0;
    end
    else
      `ifndef FIFO
        // verilator lint_off BLKANDNBLK
        RDATA_B1 <= 16'bx;
        // verilator lint_on BLKANDNBLK
      `endif

  // Collision checking
    always @(posedge collision_a_write_flag) begin
      if (collision_b_write_flag && (collision_a_address == collision_b_address)) begin
        $display("ERROR: Write collision occured on TDP_RAM18K instance %m at time %t where port A1 is writing to the same address, %h, as port B1.\n       The write data may not be valid.", $realtime, collision_a_address);
        collision_a_write_flag = 0;
      end
      if (collision_b_read_flag && (collision_a_address == collision_b_address)) begin
        $display("ERROR: Memory collision occured on TDP_RAM18K instance %m at time %t where port A1 is writing to the same address, %h, as port B1 is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b_address);
        collision_a_write_flag = 0;
      end
    end
     
    always @(posedge collision_a_read_flag) begin
      if (collision_b_write_flag && (collision_a_address == collision_b_address))
        $display("ERROR: Memory collision occured on TDP_RAM18K instance %m at time %t where port B1 is writing to the same address, %h, as port A1 is reading.\n       The write data is valid but the read data is not.", $realtime, collision_a_address);
        collision_a_read_flag = 0;
      end
      
    always @(posedge collision_b_write_flag) begin
      if (collision_a_write_flag && (collision_a_address == collision_b_address)) begin
        $display("ERROR: Write collision occured on TDP_RAM18K instance %m at time %t where port B1 is writing to the same address, %h, as port A1.\n       The write data may not be valid.", $realtime, collision_b_address);
        collision_b_write_flag = 0;   
      end
      if (collision_a_read_flag && (collision_a_address == collision_b_address)) begin
        $display("ERROR: Memory collision occured on TDP_RAM18K instance %m at time %t where port B1 is writing to the same address, %h, as port A1 is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b_address);
        collision_b_write_flag = 0;
      end
    end
  
    always @(posedge collision_b_read_flag) begin
      if (collision_a_write_flag && (collision_a_address == collision_b_address)) begin
        $display("ERROR: Memory collision occured on TDP_RAM18K instance %m at time %t where port A1 is writing to the same address, %h, as port B1 is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b_address);
        collision_b_read_flag = 0;
      end
    end

  //RAM2
  localparam A2_DATA_WRITE_WIDTH = calc_data_width(WRITE_WIDTH_A2);
  localparam A2_WRITE_ADDR_WIDTH = calc_depth(A2_DATA_WRITE_WIDTH);
  localparam A2_DATA_READ_WIDTH = calc_data_width(READ_WIDTH_A2);
  localparam A2_READ_ADDR_WIDTH = calc_depth(A2_DATA_READ_WIDTH);
  localparam A2_DATA_WIDTH = (A2_DATA_WRITE_WIDTH > A2_DATA_READ_WIDTH) ? A2_DATA_WRITE_WIDTH : A2_DATA_READ_WIDTH;

  localparam A2_PARITY_WRITE_WIDTH = calc_parity_width(WRITE_WIDTH_A2);
  localparam A2_PARITY_READ_WIDTH = calc_parity_width(READ_WIDTH_A2);
  localparam A2_PARITY_WIDTH = (A2_PARITY_WRITE_WIDTH > A2_PARITY_READ_WIDTH) ? A2_PARITY_WRITE_WIDTH : A2_PARITY_READ_WIDTH;
  
  localparam B2_DATA_WRITE_WIDTH = calc_data_width(WRITE_WIDTH_B2);
  localparam B2_WRITE_ADDR_WIDTH = calc_depth(B2_DATA_WRITE_WIDTH);
  localparam B2_DATA_READ_WIDTH = calc_data_width(READ_WIDTH_B2);
  localparam B2_READ_ADDR_WIDTH = calc_depth(B2_DATA_READ_WIDTH);
  localparam B2_DATA_WIDTH = (B2_DATA_WRITE_WIDTH > B2_DATA_READ_WIDTH) ? B2_DATA_WRITE_WIDTH : B2_DATA_READ_WIDTH;

  localparam B2_PARITY_WRITE_WIDTH = calc_parity_width(WRITE_WIDTH_B2);
  localparam B2_PARITY_READ_WIDTH = calc_parity_width(READ_WIDTH_B2);
  localparam B2_PARITY_WIDTH = (B2_PARITY_WRITE_WIDTH > B2_PARITY_READ_WIDTH) ? B2_PARITY_WRITE_WIDTH : B2_PARITY_READ_WIDTH;

  localparam RAM2_DATA_WIDTH = (A2_DATA_WIDTH > B2_DATA_WIDTH) ? A2_DATA_WIDTH : B2_DATA_WIDTH;
  localparam RAM2_PARITY_WIDTH = (A2_PARITY_WIDTH > B2_PARITY_WIDTH) ? A2_PARITY_WIDTH : B2_PARITY_WIDTH;
  localparam RAM2_ADDR_WIDTH = calc_depth(RAM2_DATA_WIDTH);

	integer a, b, c, l, n, p, r;
  
  reg collision_a2_write_flag = 0;                                   
  reg collision_b2_write_flag = 0;                                   
  reg collision_a2_read_flag = 0;                                   
  reg collision_b2_read_flag = 0;                                   
  reg [RAM2_ADDR_WIDTH-1:0] collision_a2_address = {RAM2_ADDR_WIDTH{1'b0}};                                   
  reg [RAM2_ADDR_WIDTH-1:0] collision_b2_address = {RAM2_ADDR_WIDTH{1'b0}};

	wire [RAM2_ADDR_WIDTH-1:0] a2_addr = ADDR_A2[13:14-RAM2_ADDR_WIDTH];                                 
  wire [RAM2_ADDR_WIDTH-1:0] b2_addr = ADDR_B2[13:14-RAM2_ADDR_WIDTH];                                  
  
  reg [RAM2_DATA_WIDTH-1:0] RAM2_DATA [2**RAM2_ADDR_WIDTH-1:0];

  /* verilator lint_off LITENDIAN */
  reg [RAM2_PARITY_WIDTH-1:0] temp_WPARITY_A2;
  reg [RAM2_PARITY_WIDTH-1:0] temp_WPARITY_B2;
  /* verilator lint_on LITENDIAN */
  reg [RAM2_DATA_WIDTH-1:0] temp_WDATA_A2;
  reg [RAM2_DATA_WIDTH-1:0] temp_WDATA_B2;

  generate
    if (RAM2_PARITY_WIDTH > 0) begin: parity_RAM2
      reg [RAM2_PARITY_WIDTH-1:0] RAM2_PARITY [2**RAM2_ADDR_WIDTH-1:0];

      integer f_p2, g_p2, h_p2, i_p2, j_p2, k_p2, m_p2;

      // Initialize Parity RAM contents
      initial begin
        f_p2 = 0;
        for (g_p2 = 0; g_p2 < 2**RAM2_ADDR_WIDTH; g_p2 = g_p2 + 1)
          for (h_p2 = 0; h_p2 < RAM2_PARITY_WIDTH; h_p2 = h_p2 + 1) begin
            `ifdef SIM_VERILATOR
              RAM2_PARITY[g_p2][h_p2] = INIT2_PARITY[f_p2];
            `else
              RAM2_PARITY[g_p2][h_p2] <= INIT2_PARITY[f_p2];
            `endif
            f_p2 = f_p2 + 1;
          end
      end

      always @(posedge CLK_A2)
        if (WEN_A2) begin
          for (i_p2 = find_a2_write_index(ADDR_A2)*A2_PARITY_WRITE_WIDTH; i_p2 < find_a2_write_index(ADDR_A2)*A2_PARITY_WRITE_WIDTH+A2_PARITY_WRITE_WIDTH; i_p2 = i_p2 + 1) begin
            if (A2_PARITY_WRITE_WIDTH > 1) begin
              if (BE_A2[i_p2/1] == 1'b1) begin
                `ifdef SIM_VERILATOR
                  /* verilator lint_off WIDTH */
                  RAM2_PARITY[a2_addr][i_p2] = WPARITY_A2[i_p2-(find_a2_write_index(ADDR_A2)*A2_PARITY_WRITE_WIDTH)];
                  /* verilator lint_on WIDTH */
                `else
                  RAM2_PARITY[a2_addr][i_p2] <= WPARITY_A2[i_p2-(find_a2_write_index(ADDR_A2)*A2_PARITY_WRITE_WIDTH)];
                `endif
              end
            end
            else begin
              `ifdef SIM_VERILATOR
                /* verilator lint_off WIDTH */
                RAM2_PARITY[a2_addr][i_p2] = WPARITY_A2[i_p2-(find_a2_write_index(ADDR_A2)*A2_PARITY_WRITE_WIDTH)];
                /* verilator lint_on WIDTH */
              `else
                RAM2_PARITY[a2_addr][i_p2] <= WPARITY_A2[i_p2-(find_a2_write_index(ADDR_A2)*A2_PARITY_WRITE_WIDTH)];
                //$display("i_p2: %0h, [i_p2/1] %0h", i_p2, i_p2/2,$time);
              `endif
            end
          end
        end      

      always @(posedge CLK_A2)
        if (REN_A2) begin
          for (j_p2 = find_a2_read_index(ADDR_A2)*A2_PARITY_READ_WIDTH; j_p2 < find_a2_read_index(ADDR_A2)*A2_PARITY_READ_WIDTH+A2_PARITY_READ_WIDTH; j_p2 = j_p2 + 1) begin
            `ifdef SIM_VERILATOR
              RPARITY_A2[j_p2-(find_a2_read_index(ADDR_A2)*A2_PARITY_READ_WIDTH)] = RAM2_PARITY[a2_addr][j_p2];
            `else
              RPARITY_A2[j_p2-(find_a2_read_index(ADDR_A2)*A2_PARITY_READ_WIDTH)] <= RAM2_PARITY[a2_addr][j_p2];
            `endif
          end
        end
        else
          `ifndef FIFO
            // verilator lint_off BLKANDNBLK
            RPARITY_A2 <= 2'bx;
            // verilator lint_on BLKANDNBLK
          `endif

      always @(posedge CLK_B2)
        if (WEN_B2) begin
          for (k_p2 = find_b2_write_index(ADDR_B2)*B2_PARITY_WRITE_WIDTH; k_p2 < find_b2_write_index(ADDR_B2)*B2_PARITY_WRITE_WIDTH+B2_PARITY_WRITE_WIDTH; k_p2 = k_p2 + 1) begin
            if (B2_PARITY_WRITE_WIDTH > 1) begin
              if (BE_B2[k_p2/1] == 1'b1) begin
                `ifdef SIM_VERILATOR
                  /* verilator lint_off WIDTH */
                  RAM2_PARITY[b2_addr][k_p2] = WPARITY_B2[k_p2-(find_b2_write_index(ADDR_B2)*B2_PARITY_WRITE_WIDTH)];
                  /* verilator lint_on WIDTH */
                `else
                  RAM2_PARITY[b2_addr][k_p2] <= WPARITY_B2[k_p2-(find_b2_write_index(ADDR_B2)*B2_PARITY_WRITE_WIDTH)];
                `endif
              end
            end
            else begin
              `ifdef SIM_VERILATOR
                /* verilator lint_off WIDTH */
                RAM2_PARITY[b2_addr][k_p2] = WPARITY_B2[k_p2-(find_b2_write_index(ADDR_B2)*B2_PARITY_WRITE_WIDTH)];
                /* verilator lint_on WIDTH */
              `else
                RAM2_PARITY[b2_addr][k_p2] <= WPARITY_B2[k_p2-(find_b2_write_index(ADDR_B2)*B2_PARITY_WRITE_WIDTH)];
              `endif
            end
          end
        end      

      always @(posedge CLK_B2)
        if (REN_B2) begin
          for (m_p2 = find_b2_read_index(ADDR_B2)*B2_PARITY_READ_WIDTH; m_p2 < find_b2_read_index(ADDR_B2)*B2_PARITY_READ_WIDTH+B2_PARITY_READ_WIDTH; m_p2 = m_p2 + 1) begin
            `ifdef SIM_VERILATOR
              RPARITY_B2[m_p2-(find_b2_read_index(ADDR_B2)*B2_PARITY_READ_WIDTH)] = RAM2_PARITY[b2_addr][m_p2];
            `else
              RPARITY_B2[m_p2-(find_b2_read_index(ADDR_B2)*B2_PARITY_READ_WIDTH)] <= RAM2_PARITY[b2_addr][m_p2];
            `endif
          end
        end
        else
          `ifndef FIFO
            // verilator lint_off BLKANDNBLK
            RPARITY_B2 <= 2'bx;
            // verilator lint_on BLKANDNBLK
          `endif
    end
  endgenerate

	// Initialize Base RAM contents
  initial begin
    a = 0;
    for (b = 0; b < 2**RAM2_ADDR_WIDTH; b = b + 1)
      for (c = 0; c < RAM2_DATA_WIDTH; c = c + 1) begin
        `ifdef SIM_VERILATOR
          RAM2_DATA[b][c] = INIT2[a];
        `else
          RAM2_DATA[b][c] <= INIT2[a];
        `endif
        a = a + 1;
      end
  end

 // Base RAM read/write functionality
  always @(posedge CLK_A2)
    if (WEN_A2) begin
      //$display("AADR_A: %b   index: %d", ADDR_A2, find_a2_write_index(ADDR_A2)*8);
      for (l = find_a2_write_index(ADDR_A2)*A2_DATA_WRITE_WIDTH; l < find_a2_write_index(ADDR_A2)*A2_DATA_WRITE_WIDTH+A2_DATA_WRITE_WIDTH; l = l + 1) begin
        if (A2_DATA_WRITE_WIDTH > 9) begin
          if (BE_A2[l/8] == 1'b1) begin
            `ifdef SIM_VERILATOR
              /* verilator lint_off WIDTH */
              RAM2_DATA[a2_addr][l] = WDATA_A2[l-(find_a2_write_index(ADDR_A2)*A2_DATA_WRITE_WIDTH)];
              /* verilator lint_on WIDTH */
            `else
              RAM2_DATA[a2_addr][l] <= WDATA_A2[l-(find_a2_write_index(ADDR_A2)*A2_DATA_WRITE_WIDTH)];
            `endif
          end
        end
        else begin
          `ifdef SIM_VERILATOR
            /* verilator lint_off WIDTH */
            RAM2_DATA[a2_addr][l] = WDATA_A2[l-(find_a2_write_index(ADDR_A2)*A2_DATA_WRITE_WIDTH)];
            /* verilator lint_on WIDTH */
          `else
            RAM2_DATA[a2_addr][l] <= WDATA_A2[l-(find_a2_write_index(ADDR_A2)*A2_DATA_WRITE_WIDTH)];
          `endif
        end
      end
      collision_a2_address = a2_addr;
      collision_a2_write_flag = 1;
      #collision_window;
      collision_a2_write_flag = 0;
    end      

  always @(posedge CLK_A2)
    if (REN_A2) begin
      for (l = find_a2_read_index(ADDR_A2)*A2_DATA_READ_WIDTH; l < find_a2_read_index(ADDR_A2)*A2_DATA_READ_WIDTH+A2_DATA_READ_WIDTH; l = l + 1) begin
        `ifdef SIM_VERILATOR
          RDATA_A2[l-(find_a2_read_index(ADDR_A2)*A2_DATA_READ_WIDTH)] = RAM2_DATA[a2_addr][l];
        `else
          RDATA_A2[l-(find_a2_read_index(ADDR_A2)*A2_DATA_READ_WIDTH)] <= RAM2_DATA[a2_addr][l];
        `endif
      end
      collision_a2_address = a2_addr;
      collision_a2_read_flag = 1;
      #collision_window;
      collision_a2_read_flag = 0;
    end
    else
      `ifndef FIFO
        // verilator lint_off BLKANDNBLK
        RDATA_A2 <= 16'bx;
        // verilator lint_on BLKANDNBLK
      `endif

  always @(posedge CLK_B2)
    if (WEN_B2) begin
      for (p = find_b2_write_index(ADDR_B2)*B2_DATA_WRITE_WIDTH; p < find_b2_write_index(ADDR_B2)*B2_DATA_WRITE_WIDTH+B2_DATA_WRITE_WIDTH; p = p + 1) begin
        if (B2_DATA_WRITE_WIDTH > 9) begin
          if (BE_B2[p/8] == 1'b1) begin
            `ifdef SIM_VERILATOR
              /* verilator lint_off WIDTH */
              RAM2_DATA[b2_addr][p] = WDATA_B2[p-(find_b2_write_index(ADDR_B2)*B2_DATA_WRITE_WIDTH)];
              /* verilator lint_on WIDTH */
            `else
              RAM2_DATA[b2_addr][p] <= WDATA_B2[p-(find_b2_write_index(ADDR_B2)*B2_DATA_WRITE_WIDTH)];
            `endif
          end
        end
        else begin
          `ifdef SIM_VERILATOR
            /* verilator lint_off WIDTH */
            RAM2_DATA[b2_addr][p] = WDATA_B2[p-(find_b2_write_index(ADDR_B2)*B2_DATA_WRITE_WIDTH)];
             /* verilator lint_on WIDTH */
          `else
            RAM2_DATA[b2_addr][p] <= WDATA_B2[p-(find_b2_write_index(ADDR_B2)*B2_DATA_WRITE_WIDTH)];
          `endif
        end   
        
      end
      collision_b2_address = b2_addr;
      collision_b2_write_flag = 1;
      #collision_window;
      collision_b2_write_flag = 0;
    end      

  always @(posedge CLK_B2)
    if (REN_B2) begin
      //$display("index: %d  b2_addr: %h ADDR_B2: %h", find_b2_read_index(ADDR_B2), b2_addr, ADDR_B2);
      for (r = find_b2_read_index(ADDR_B2)*B2_DATA_READ_WIDTH; r < find_b2_read_index(ADDR_B2)*B2_DATA_READ_WIDTH+B2_DATA_READ_WIDTH; r = r + 1) begin
        `ifdef SIM_VERILATOR
          RDATA_B2[r-(find_b2_read_index(ADDR_B2)*B2_DATA_READ_WIDTH)] = RAM2_DATA[b2_addr][r];
        `else
          RDATA_B2[r-(find_b2_read_index(ADDR_B2)*B2_DATA_READ_WIDTH)] <= RAM2_DATA[b2_addr][r];
        `endif
      end
      collision_b2_address = b2_addr;
      collision_b2_read_flag = 1;
      #collision_window;
      collision_b2_read_flag = 0;
    end
    else
      `ifndef FIFO
        // verilator lint_off BLKANDNBLK
        RDATA_B2 <= 16'bx;
        // verilator lint_on BLKANDNBLK
      `endif

    // Collision checking
    always @(posedge collision_a2_write_flag) begin
      if (collision_b2_write_flag && (collision_a2_address == collision_b2_address)) begin
        $display("ERROR: Write collision occured on TDP_RAM18K instance %m at time %t where port A2 is writing to the same address, %h, as port B2.\n       The write data may not be valid.", $realtime, collision_a2_address);
        collision_a2_write_flag = 0;
      end
      if (collision_b2_read_flag && (collision_a2_address == collision_b2_address)) begin
        $display("ERROR: Memory collision occured on TDP_RAM18K instance %m at time %t where port A2 is writing to the same address, %h, as port B2 is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b2_address);
        collision_a2_write_flag = 0;
      end
    end
     
    always @(posedge collision_a2_read_flag) begin
      if (collision_b2_write_flag && (collision_a2_address == collision_b2_address))
        $display("ERROR: Memory collision occured on TDP_RAM18K instance %m at time %t where port B2 is writing to the same address, %h, as port A2 is reading.\n       The write data is valid but the read data is not.", $realtime, collision_a2_address);
        collision_a2_read_flag = 0;
      end
      
    always @(posedge collision_b2_write_flag) begin
      if (collision_a2_write_flag && (collision_a2_address == collision_b2_address)) begin
        $display("ERROR: Write collision occured on TDP_RAM18K instance %m at time %t where port B2 is writing to the same address, %h, as port A2.\n       The write data may not be valid.", $realtime, collision_b2_address);
        collision_b2_write_flag = 0;   
      end
      if (collision_a2_read_flag && (collision_a2_address == collision_b2_address)) begin
        $display("ERROR: Memory collision occured on TDP_RAM18K instance %m at time %t where port B2 is writing to the same address, %h, as port A2 is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b2_address);
        collision_b2_write_flag = 0;
      end
    end
  
    always @(posedge collision_b2_read_flag) begin
      if (collision_a2_write_flag && (collision_a2_address == collision_b2_address)) begin
        $display("ERROR: Memory collision occured on TDP_RAM18K instance %m at time %t where port A2 is writing to the same address, %h, as port B2 is reading.\n       The write data is valid but the read data is not.", $realtime, collision_b2_address);
        collision_b2_read_flag = 0;
      end
    end

	function integer find_a1_write_index;
    input [13:0] addr;
    
    if (RAM1_ADDR_WIDTH == A1_WRITE_ADDR_WIDTH)
      find_a1_write_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */
      find_a1_write_index = ADDR_A1[13-RAM1_ADDR_WIDTH:14-A1_WRITE_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_a1_read_index;
    input [13:0] addr;
    
    if (RAM1_ADDR_WIDTH == A1_READ_ADDR_WIDTH)
      find_a1_read_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */   
      find_a1_read_index = ADDR_A1[13-RAM1_ADDR_WIDTH:14-A1_READ_ADDR_WIDTH]; 
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_b1_write_index;
    input [13:0] addr;
    
    if (RAM1_ADDR_WIDTH == B1_WRITE_ADDR_WIDTH)
      find_b1_write_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */ 
      find_b1_write_index = ADDR_B1[13-RAM1_ADDR_WIDTH:14-B1_WRITE_ADDR_WIDTH];
       /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_b1_read_index;
    input [13:0] addr;
    
    if (RAM1_ADDR_WIDTH == B1_READ_ADDR_WIDTH)
      find_b1_read_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */ 
      find_b1_read_index = ADDR_B1[13-RAM1_ADDR_WIDTH:14-B1_READ_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_a2_write_index;
    input [13:0] addr;
    
    if (RAM2_ADDR_WIDTH == A2_WRITE_ADDR_WIDTH)
      find_a2_write_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */ 
      find_a2_write_index = ADDR_A2[13-RAM2_ADDR_WIDTH:14-A2_WRITE_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_a2_read_index;
    input [13:0] addr;
    
    if (RAM2_ADDR_WIDTH == A2_READ_ADDR_WIDTH)
      find_a2_read_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */  
      find_a2_read_index = ADDR_A2[13-RAM2_ADDR_WIDTH:14-A2_READ_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_b2_write_index;
    input [13:0] addr;
    
    if (RAM2_ADDR_WIDTH == B2_WRITE_ADDR_WIDTH)
      find_b2_write_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */ 
      find_b2_write_index = ADDR_B2[13-RAM2_ADDR_WIDTH:14-B2_WRITE_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

  function integer find_b2_read_index;
    input [13:0] addr;
    
    if (RAM2_ADDR_WIDTH == B2_READ_ADDR_WIDTH)
      find_b2_read_index = 0;
    else
      /* verilator lint_off SELRANGE */
      /* verilator lint_off WIDTH */ 
      find_b2_read_index = ADDR_B2[13-RAM2_ADDR_WIDTH:14-B2_READ_ADDR_WIDTH];
      /* verilator lint_on SELRANGE */
      /* verilator lint_on WIDTH */

  endfunction

	function integer calc_data_width;
    input integer width;
    if (width==9)
      calc_data_width = 8;
    else if (width==18) 
      calc_data_width = 16;
    else
      calc_data_width = width;
  endfunction

  function integer calc_parity_width;
    input integer width;
    if (width==9)
      calc_parity_width = 1;
    else if (width==18) 
      calc_parity_width = 2;
    else
      calc_parity_width = 0;
  endfunction

  function integer calc_depth;
    input integer width;
    if (width<=1)
      calc_depth = 14;
    else if (width<=2) 
      calc_depth = 13;
    else if (width<=4) 
      calc_depth = 12;
    else if (width<=9) 
      calc_depth = 11;
    else if (width<=18) 
      calc_depth = 10;
    else
      calc_depth = 0;
  endfunction

  initial
    $timeformat(-9,0," ns", 5); initial begin
    case(WRITE_WIDTH_A1)
      1 ,
      2 ,
      4 ,
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: TDP_RAM18KX2 instance %m has parameter WRITE_WIDTH_A1 set to %d.  Valid values are 1, 2, 4, 9, 18\n", WRITE_WIDTH_A1);
      end
    endcase
    case(WRITE_WIDTH_B1)
      1 ,
      2 ,
      4 ,
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: TDP_RAM18KX2 instance %m has parameter WRITE_WIDTH_B1 set to %d.  Valid values are 1, 2, 4, 9, 18\n", WRITE_WIDTH_B1);
      end
    endcase
    case(READ_WIDTH_A1)
      1 ,
      2 ,
      4 ,
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: TDP_RAM18KX2 instance %m has parameter READ_WIDTH_A1 set to %d.  Valid values are 1, 2, 4, 9, 18\n", READ_WIDTH_A1);
      end
    endcase
    case(READ_WIDTH_B1)
      1 ,
      2 ,
      4 ,
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: TDP_RAM18KX2 instance %m has parameter READ_WIDTH_B1 set to %d.  Valid values are 1, 2, 4, 9, 18\n", READ_WIDTH_B1);
      end
    endcase
    case(WRITE_WIDTH_A2)
      1 ,
      2 ,
      4 ,
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: TDP_RAM18KX2 instance %m has parameter WRITE_WIDTH_A2 set to %d.  Valid values are 1, 2, 4, 9, 18\n", WRITE_WIDTH_A2);
      end
    endcase
    case(WRITE_WIDTH_B2)
      1 ,
      2 ,
      4 ,
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: TDP_RAM18KX2 instance %m has parameter WRITE_WIDTH_B2 set to %d.  Valid values are 1, 2, 4, 9, 18\n", WRITE_WIDTH_B2);
      end
    endcase
    case(READ_WIDTH_A2)
      1 ,
      2 ,
      4 ,
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: TDP_RAM18KX2 instance %m has parameter READ_WIDTH_A2 set to %d.  Valid values are 1, 2, 4, 9, 18\n", READ_WIDTH_A2);
      end
    endcase
    case(READ_WIDTH_B2)
      1 ,
      2 ,
      4 ,
      9 ,
      18: begin end
      default: begin
        $fatal(1,"\nError: TDP_RAM18KX2 instance %m has parameter READ_WIDTH_B2 set to %d.  Valid values are 1, 2, 4, 9, 18\n", READ_WIDTH_B2);
      end
    endcase

  end

endmodule
`endcelldefine