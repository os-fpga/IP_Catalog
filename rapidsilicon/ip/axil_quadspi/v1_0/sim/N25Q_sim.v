module N25Q_sim
  #(parameter NUM_ADDR_BITS=25,
    parameter FILENAME="axil_quadspi_mem.init")
  (
   input  sclk,
   inout  mosi,
   input  csb,
   output miso,
   inout  wp,
   inout  holdb
   );

//`define DEBUG

   reg [2:0] rpos;
   reg [3:0] rstate, next_rstate;
   parameter STATE_RX_CMD = 0, STATE_SEND=1, STATE_RCV=2, STATE_RCV_NV_CONFIG=3, STATE_WRITE=4, STATE_READ=5, STATE_RCV_WRITE=6, STATE_SUBSECTOR_ERASE=7;
   reg [7:0] srin;
   wire [7:0] next_srin = { srin[6:0], mosi };
   reg 	      write_enable;
   reg [4:0]  status_dont_care;
   reg 	      write_enable_latch;
   reg 	      write_in_progress;
   reg 	     four_byte_addr_mode;
   
   wire [7:0] status = { write_enable, status_dont_care, write_enable_latch, write_in_progress };

   reg resetb = 0;
   always @(negedge sclk) begin
      resetb <= 1;
   end

   reg [7:0] sro_buf[0:(1<<NUM_ADDR_BITS)-1];
   reg [7:0] sri_buf[0:256];
   reg [7:0] mem_data[0:(1<<NUM_ADDR_BITS)-1];
   reg [8:0] rcv_count;
   reg [3:0] offset;
   wire [31:0] addr = (four_byte_addr_mode) ? 
	       {sri_buf[3], sri_buf[2], sri_buf[1], next_srin } :
	       {8'b0, sri_buf[2], sri_buf[1], next_srin };	       
   reg [31:0] waddr;

   initial begin
		$readmemh(FILENAME, mem_data);
	end
   
//    _WRITE_STATUS      = 0x01
//    _READ_LOCK         = 0xE8
//    _WRITE_LOCK        = 0xE5
//    _READ_FLAG_STATUS  = (0x70, 1)
//    _CLEAR_FLAG_STATUS = 0x50
   reg 	     bulk_erase_in_progress, event_bulk_erase;
   reg [9:0] bulk_erase_counter;
   integer   j;
   reg [15:0] nv_config;
   reg 	      mode_quad;
   
   always @(posedge sclk or posedge csb or negedge resetb) begin
      if(!resetb) begin
	 rpos   <= 0;
	 rstate <= STATE_RX_CMD;
	 srin   <= 0;
	 write_enable <= 1;
	 write_enable_latch <= 0;
	 status_dont_care <= 0;
	 write_in_progress <= 0;
	 offset <= 0;
	 event_bulk_erase <= 0;
	 bulk_erase_in_progress <= 0;
	 bulk_erase_counter <= 0;
	 four_byte_addr_mode <= 0;
	 next_rstate <= 0;
	 nv_config <= 16'hFFFF;
	 rcv_count <= 0;
	 waddr <= 0;
	 mode_quad <= 0;
      end else if(csb) begin
	 rpos   <= 0;
	 rstate <= STATE_RX_CMD;
	 srin   <= 0;
	 offset <= 0;
	 next_rstate <= 0;
	 mode_quad <= 0;
      end else begin
	 srin <= next_srin;
	 rpos <= rpos + 1;
	 write_in_progress <= bulk_erase_in_progress;
	 if(bulk_erase_counter == 1) begin
	    write_enable_latch <= 0;
	 end
	 
	 if(rstate == STATE_RX_CMD) begin
	    if(rpos == 7) begin
`ifdef DEBUG
	       $display("N25Q FLASH MEM: RX CMD 0x%02h", next_srin);
`endif
	       case(next_srin)
		 8'h02: begin
`ifdef DEBUG
		    $display("  WRITE_PAGE CMD RECEIVED.");
`endif
		    next_rstate <= STATE_WRITE;
		    rcv_count <= (four_byte_addr_mode) ? 4 : 3;
		    rstate <= STATE_RCV;
		 end

		 8'h03: begin
`ifdef DEBUG
		    $display("  READ CMD RECEIVED.");
`endif
		    next_rstate <= STATE_READ;
		    rcv_count <= (four_byte_addr_mode) ? 4 : 3;
		    rstate <= STATE_RCV;
		 end

		 8'h04: begin
`ifdef DEBUG
		    $display("  WRITE_DISABLE CMD RECEIVED.");
`endif
		    write_enable_latch <= 0;
		    rstate <= STATE_SEND;
		 end

		 8'h05: begin
`ifdef DEBUG
		    $display("  READ STATUS CMD RECEIVED. Status = 0x%02x", status);
`endif
		    sro_buf[0] <= status;
		    offset <= 1;
		    rstate <= STATE_SEND;
		 end

		 8'h06: begin
`ifdef DEBUG
		    $display("  WRITE_ENABLE CMD RECEIVED.");
`endif
		    write_enable_latch <= 1;
		    rstate <= STATE_SEND;
		 end

		 8'h20: begin
`ifdef DEBUG
		    $display("  SUBSECTOR ERASE CMD RECEIVED.");
`endif
		    rstate <= STATE_RCV;
		    rcv_count <= (four_byte_addr_mode) ? 4 : 3;
		    next_rstate <= STATE_SUBSECTOR_ERASE;
		 end
		 
		 8'h6B: begin
`ifdef DEBUG
		    $display("  QUAD READ CMD RECEIVED.");
`endif
		    mode_quad <= 1;
		    next_rstate <= STATE_READ;
		    rcv_count <= (four_byte_addr_mode) ? 5 : 4; // add 8 dummy bits. TO DO: make number of dummy bits programmable.
		    rstate <= STATE_RCV;
		 end

		 8'hB1: begin
`ifdef DEBUG
		    $display("  WRITE_NV_CONFIG CMD RECEIVED.");
`endif
		    rstate <= STATE_RCV;
		    rcv_count <= 2;
		    next_rstate <= STATE_RCV_NV_CONFIG;
		 end

		 8'hB5: begin
`ifdef DEBUG
		    $display("  READ_NV_CONFIG CMD RECEIVED. nv_config=0x%x", nv_config);
`endif
		    offset <= 1;
		    sro_buf[0] <= nv_config[7:0];
		    sro_buf[1] <= nv_config[15:8];
		    rstate <= STATE_SEND;
		 end

		 8'hB7: begin
`ifdef DEBUG
		    $display("  ENTER 4 BYTE ADDRESS MODE CMD RECEIVED");
`endif
		    four_byte_addr_mode <= 1;
		    rstate <= STATE_SEND;
		 end

		 8'hC7: begin
`ifdef DEBUG
		    $display("  BULK ERASE CMD RECEIVED.");
`endif
		    if(write_enable_latch == 1 && wp) begin
		       event_bulk_erase <= 1;
		    end else begin
		       $display("  CAN'T BULK ERASE. WRITE NOT ENABLED");
		    end
		    rstate <= STATE_SEND;
		 end

		 8'h9e: begin
`ifdef DEBUG
		    $display("  READ ID CMD RECEIVED.");
`endif
		    offset <= 1;
		    sro_buf[0] <= 8'h20;
		    sro_buf[1] <= 8'hBA;
 		    sro_buf[2] <= NUM_ADDR_BITS;
		    for(j=3; j<20; j=j+1) begin
		       sro_buf[j] <= 8'h00;
		    end
		    rstate <= STATE_SEND;
		 end
		 
		 default: begin
`ifdef DEBUG
		    $display("  UNKNOWN CMD RECEIVED. Returning garbage.");
`endif
		    rstate <= STATE_SEND;
		 end
	       endcase
	    end else begin
	       event_bulk_erase <= 0;
	    end

	 end else if(rstate == STATE_RCV) begin // if (rstate == STATE_RX_CMD)
	    if(rpos == 7) begin
	       if(mode_quad) begin
		  sri_buf[rcv_count-2] <= next_srin;
	       end else begin
		  sri_buf[rcv_count-1] <= next_srin;
	       end
	       rcv_count <= rcv_count - 1;
	       if (rcv_count == 1) begin
		  rstate <= STATE_SEND;
	       end

	       if(rcv_count == 1 || (rcv_count == 2 && mode_quad)) begin
		  if(mode_quad) begin
		     offset <= (four_byte_addr_mode) ? 6 : 5; // dummy bits. To Do: make programmable 
		  end else begin
		     offset <= (four_byte_addr_mode) ? 5 : 4;
		  end

		  if(next_rstate == STATE_RCV_NV_CONFIG) begin
		     nv_config <= { next_srin, sri_buf[1] };
		  end else if(next_rstate == STATE_READ) begin
		     if((rcv_count == 1 && !mode_quad) || (rcv_count == 2 && mode_quad)) begin
`ifdef DEBUG
			$display("   FLASH READ FROM ADDR=0x%x", addr);
`endif
			for(j=addr; j<1<<NUM_ADDR_BITS; j=j+1) begin
			   sro_buf[j-addr] = mem_data[j];
			end
		     end
		  end else if(next_rstate == STATE_WRITE) begin
		     waddr <= addr;
		     rstate <= STATE_RCV_WRITE;
		  end else if(next_rstate == STATE_SUBSECTOR_ERASE) begin
		     for(j=0; j<4096; j=j+1) begin
			mem_data[(addr & 32'hFFFFF000) + j] = 8'hff;
		     end
		  end
	       end
	    end
	 end else if(rstate == STATE_RCV_WRITE) begin
	    if(rpos == 7) begin
	       waddr[7:0] <= waddr[7:0] + 1;
	       mem_data[waddr] <= next_srin;
	    end
	 end
	 
	 if(event_bulk_erase) begin
	    bulk_erase_counter <= 10'h3FF;
	    bulk_erase_in_progress <= 1;
	 end else if(bulk_erase_counter > 0) begin
	    bulk_erase_counter <= bulk_erase_counter - 1;
	    if(bulk_erase_counter == 1) begin
	       for(j=0; j<1<<NUM_ADDR_BITS; j=j+1) begin
		  mem_data[j] = 8'hff;
	       end
	    end 
	 end else begin
	    bulk_erase_in_progress <= 0;
	 end
      end // else: !if(csb)
      
	 
   end


   reg [2:0] spos;
   wire [2:0] next_spos = (mode_quad && rstate == STATE_SEND && (spos==0 || spos == 4)) ? spos + 4 : spos + 1;
   reg [24:0] saddr;
   /* verilator lint_off WIDTH */
   wire [7:0] sro = sro_buf[saddr-offset];
   /* verilator lint_on WIDTH */
   assign mosi  = (mode_quad && rstate == STATE_SEND) ? sro[4-spos] : 1'bz;
   assign miso  = (mode_quad && rstate == STATE_SEND) ? sro[5-spos] : sro[7-spos];
   assign wp    = (mode_quad && rstate == STATE_SEND) ? sro[6-spos] : 1'bz;
   assign holdb = (mode_quad && rstate == STATE_SEND) ? sro[7-spos] : 1'bz;

   wire       dq0 = spos[4-spos];
   wire       dq1 = spos[5-spos];
   wire       dq2 = spos[6-spos];
   wire       dq3 = spos[7-spos];
   
   
   always @(negedge sclk or posedge csb or negedge resetb) begin
      if(!resetb) begin
	 spos <= 0;
	 saddr <= 0;
      end else if(csb) begin
	 spos <= 0;
	 saddr <= 0;
      end else begin
	 if(next_spos == 0) begin
	    saddr <= saddr + 1;
	 end
	 spos <= next_spos;
      end
   end

endmodule
