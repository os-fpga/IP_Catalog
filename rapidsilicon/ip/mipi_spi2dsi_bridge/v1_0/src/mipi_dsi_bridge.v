`timescale 1ps/1ps

module mipi_dsi_bridge(rst, clk, 
				data_p, 
				data_n, 
				clk_p, 
				clk_n,
				reg_1v8_en, 
				reg_3v0_en, 
				lcd_rst, 
				bl_en, 
				spi_mosi_i, 
				spi_csn_i, 
				spi_clk_i, 
				lcd_test_i);

output reg reg_1v8_en;
output reg reg_3v0_en;
output reg lcd_rst;
output reg bl_en;
output wire data_p ;
output wire data_n ;
output wire clk_p ;
output wire clk_n ;



input wire rst;
input clk; //clock input
input spi_mosi_i;
input spi_csn_i;
input spi_clk_i;
input lcd_test_i;


wire buf_clkout_lp_n_o;
wire buf_clkout_lp_p_o;
wire buf_dout_lp_n_o;
wire buf_dout_lp_p_o;
reg spi_csn_reg1;
reg spi_csn_reg2;
reg spi_csn_reg3;
reg write_cmd;
reg fifo_reset;
reg [7:0]command_r;
reg [2:0] controller_state;
reg [3:0] reset_state;
reg [7:0] spi_cmd;
reg [7:0] line_counter;
reg [32:0] 	delay_counter; 

wire [7:0]fifo_out;
wire pll_clk_spi;
wire reset_i;
wire pll_clk_p ,pll_clk_p_1,SERDES_FAST_CLK;
reg  pll_clk_s = 0;
reg  pll_clk_s2, pll_clk_s2_1;
wire ready;
wire sclk;
wire lock;
wire fifo_full;
wire fifo_empty_w;
wire fifo_almost_full;
wire almost_empty;
wire fifo_read_en_w;
wire spi_byte_clock;
wire fifo_write_en_r;
wire [7:0]spi_rxdata;
wire tx_finish_w;
wire hs_data_o, hs_clock_o, mipi_data_n;


assign  reset_i = !rst;

assign pll_clk_spi  = pll_clk_s2;

assign data_p = (!buf_dout_lp_p_o & !buf_dout_lp_n_o) ? hs_data_o : buf_dout_lp_p_o;
assign data_n = (!buf_dout_lp_p_o & !buf_dout_lp_n_o) ? mipi_data_n : buf_dout_lp_n_o;

assign clk_p = (!buf_clkout_lp_p_o & !buf_clkout_lp_n_o) ? hs_clock_o : buf_clkout_lp_p_o;
assign clk_n = (!buf_clkout_lp_p_o & !buf_clkout_lp_n_o) ? hs_clock_o : buf_clkout_lp_n_o;


PLL #(
  .DIVIDE_CLK_IN_BY_2("FALSE"),
  .PLL_MULT(16),
  .PLL_DIV(2), 
  .PLL_POST_DIV(2) 
) PLL_ins(
  .PLL_EN(1'b1), 		
  .CLK_IN(clk), 		
  .CLK_OUT(),
  .CLK_OUT_DIV2(pll_clk_s2), 
  .CLK_OUT_DIV3(), 
  .CLK_OUT_DIV4(), 
  .SERDES_FAST_CLK(pll_clk_p), 
  .LOCK(lock)
);



FIFo fifo_module( 	.Reset(fifo_reset),
					.RPReset(1'b0),
					.Data(spi_rxdata),
					.Q(fifo_out),
					.WrEn(fifo_write_en_r),
					.RdEn(fifo_read_en_w),
					.WrClock(spi_byte_clock),
					.RdClock(byte_clock_o),
					.Full(fifo_full),
					.AlmostFull(fifo_almost_full), 
					.AlmostEmpty(almost_empty),
					.Empty(fifo_empty_w)
					);
					
DPHY_TX_FRAME dphy_tx_frame(
						.reset_i(reset_i),							//reset active high
						.command_i(command_r),
						.write_cmd_i(write_cmd),
						.clockp_fast_data_i(pll_clk_p),				//fast clokc input for mipi data
						.clocks_fast_clk_i(pll_clk_s),				//fast clock input for mipi clok
						.clock_slow_sync_i(pll_clk_s2),					//slow clock for sync
						.lock_chk_i(1'b1),							//pll lock check
						.fifo_almost_empty(almost_empty),
						.fifo_empty(fifo_empty_w),
						.data_i(fifo_out),							//mipi data input from FIFO			
						
						.finish_o(tx_finish_w),
						.fifo_read_en(fifo_read_en_w),
						.buf_clkout_lp_p_o(buf_clkout_lp_p_o),		//mipi clock lp0 out
						.buf_clkout_lp_n_o(buf_clkout_lp_n_o),		//mipi clock lp1 out
						.buf_dout_lp_p_o(buf_dout_lp_p_o),  		//data lp0 out
						.buf_dout_lp_n_o(buf_dout_lp_n_o),			//data lp1 out
						.byte_clock_o(byte_clock_o),				//byte clock out
						.hs_data_o(hs_data_o),						//mipi data out
						.hs_clock_o(hs_clock_o),					//mipi clock out	
						.mipi_data_n(mipi_data_n));					//mipi clock out	



SPI_SLAVE spi_slave_inst1 ( .clk_i(pll_clk_spi),
							.rst_i(reset_i),
							.rx_data_o(spi_rxdata),
							.byte_clock_o(spi_byte_clock),
							.spi_clk_i(spi_clk_i),
							.spi_mosi_i(spi_mosi_i),
							.spi_csn_i(spi_csn_i)
							);						



parameter controller_state_reset_lcd 		= 3'h0;
parameter controller_state_idle 			= 3'h1;
parameter controller_state_cmd_received  	= 3'h2;
parameter controller_state_cmd_busy 		= 3'h3;
parameter controller_state_wait_cs  		= 3'h4;


parameter state_lcd_activate_vee		= 4'h0;
parameter state_lcd_reset_active		= 4'h1;
parameter state_lcd_reset_wait			= 4'h2;
parameter state_lcd_reset_wait_for_vdd	= 4'h3;
parameter state_lcd_reset_send_cmd_init	= 4'h4;
parameter state_lcd_reset_wait_cmd 		= 4'h5;
parameter state_lcd_reset_wait_init		= 4'h6;
parameter state_lcd_reset_tp_write		= 4'h7;
parameter state_lcd_reset_tp_wait		= 4'h8;


//reset sequence delay timing as per mipi specs
//parameter delay_reset_deactivated 	=  32'h1071B00; //250ms @ 46Mhz
parameter delay_reset_deactivated 	=  32'h0001B00; //250ms @ 46Mhz
parameter delay_reset_ativated  	= 32'h6A980;		//5ms @ 12Mhz
//parameter delay_reset_ativated  	= 32'h180;		//5ms @ 12Mhz
parameter delay_reset_wait_vdd		= 32'h10B80;		//1ms
parameter delay_wait_for_vdd		= 32'h6A980;		//5ms
parameter delay_wait_init			= 32'h6A980;		//5ms


parameter CMD_LCD_INIT = 8'h89; 		//from ROM 13th line
parameter CMD_LCD_TP_FIRST = 8'hCF; 	//line 17
parameter CMD_LCD_TP_NEXT = 8'hD9;		//line 18
parameter DISPLAY_LINE_MAX = 8'd240;
parameter CLK_PERIOD = 4000;



 reg counter = 1'b0;

initial begin
	#(CLK_PERIOD/32)
    forever #(CLK_PERIOD/16) pll_clk_s = ~pll_clk_s;

end

always @(posedge reset_i or posedge byte_clock_o) //must be slower than ddr_byte_clock
begin

if (reset_i)
	begin
		 controller_state <= controller_state_reset_lcd;
		 reset_state <= state_lcd_activate_vee;
		 lcd_rst    <= 1'h0; //reset active
		 reg_1v8_en <= 1'h0;	//reg inactive
		 reg_3v0_en <= 1'h0;	//reg inactive 
		 line_counter <= 8'h0;
	end
	else
	begin
		
		case (controller_state)
			controller_state_reset_lcd: begin
				if (delay_counter)
				begin
					delay_counter <= delay_counter - 1'b1;
				end
				else
				begin
				case (reset_state)
						state_lcd_activate_vee:begin
							reg_1v8_en <= 1'h1; //activate 1v8
							lcd_rst    <= 1'h1; //reset inactive
							bl_en <= 1'h1; //enable BL
							fifo_reset <= 1;
							write_cmd <= 1'b0;
							
							delay_counter <= delay_reset_deactivated;
							reset_state <= state_lcd_reset_active;
							end
							
						state_lcd_reset_active:begin
							fifo_reset <= 1'b0;
							lcd_rst    <= 1'h0; //reset active
							delay_counter <= delay_reset_ativated;
							reset_state <= state_lcd_reset_wait;
							end
							
						state_lcd_reset_wait:begin
							fifo_reset <= 1'b1;
							lcd_rst    <= 1'h1; //reset inactive
							delay_counter <= delay_reset_wait_vdd;
							reset_state <= state_lcd_reset_wait_for_vdd;
							end
							
						state_lcd_reset_wait_for_vdd:begin
							fifo_reset <= 1'b0;
							reg_3v0_en <= 1'h1;	//reg acitve
							delay_counter <= delay_wait_for_vdd;
							reset_state <= state_lcd_reset_send_cmd_init;
							end
							
						state_lcd_reset_send_cmd_init:begin
							write_cmd <= 1'b1; 
							command_r <= CMD_LCD_INIT;
							delay_counter <= 0;
							reset_state <= state_lcd_reset_wait_cmd;
							end
							
						state_lcd_reset_wait_cmd:begin		//lcd take quite some time to process some commands
							if(tx_finish_w)
								begin
									delay_counter <= delay_wait_init;
									reset_state <= state_lcd_reset_wait_init;
								end
								else
								begin
									write_cmd <= 1'b0; 
								end
							end
							
						state_lcd_reset_wait_init:begin
								reset_state <= state_lcd_activate_vee;	//reset, reset state machine
								
								if (lcd_test_i)
								begin
									reset_state <= state_lcd_reset_tp_write;	
									line_counter <= 8'h0;
								end
								else
								begin
									controller_state <= controller_state_idle;
								end
							end
							
						state_lcd_reset_tp_write:begin
							write_cmd <= 1'b1;
							line_counter <= line_counter + 1'b1;
							if (line_counter == 8'h0)
								begin
									command_r <= CMD_LCD_TP_FIRST;
								end
								else
								begin
									command_r <= CMD_LCD_TP_NEXT;
								end
							
							delay_counter <= 0;
							reset_state <= state_lcd_reset_tp_wait;
							end
							
						state_lcd_reset_tp_wait:begin
							if (tx_finish_w)
								begin
									if (line_counter < DISPLAY_LINE_MAX)
									begin
										reset_state <= state_lcd_reset_tp_write;
									end
									else
									begin
										reset_state <= state_lcd_activate_vee;	//reset reset_state
										controller_state <= controller_state_wait_cs;
									end
								end
								else
								begin
									write_cmd <= 1'b0; 
								end

							end
							
						default:begin
								reset_state <= state_lcd_activate_vee;
							end
					endcase

				end
			end
			controller_state_idle: begin
					spi_csn_reg1 <= spi_csn_i;
					spi_csn_reg2 <= spi_csn_reg1;
					spi_csn_reg3 <= spi_csn_reg2;
					if (!spi_csn_reg3 & spi_csn_reg2)
					begin
						write_cmd <= spi_csn_i; 
						command_r <= spi_cmd;
						controller_state <= controller_state_cmd_received;				
					end
				end
			controller_state_cmd_received: begin					
					controller_state <= controller_state_cmd_busy;				
				end
			controller_state_cmd_busy: begin
				if(tx_finish_w)
				begin
					controller_state <= controller_state_wait_cs;
				end
				else
				begin
					write_cmd <= 1'b0; 
				end
				end
			controller_state_wait_cs: begin
				if (!spi_csn_i) //wait till spi_csn_i goes idle
				begin
					controller_state <= controller_state_idle;
				end
				end
			default: begin
				controller_state <= controller_state_idle;
				end 
		endcase
	end
	
end

reg first_byte;

assign fifo_write_en_r = !spi_csn_i;
always @(posedge reset_i or posedge spi_byte_clock or posedge spi_csn_i)
begin
	
	if (reset_i)
	begin
		first_byte <= 1'b0;
		spi_cmd <= 8'b0;
	end
	else 
	begin
		if (spi_csn_i)
		begin
				first_byte <= 1'b0;
		end
		else
		begin
			
			if (first_byte == 1'b0)
			begin
					first_byte <= 1'b1;
					spi_cmd <= spi_rxdata;
			end
		end
	end
end


endmodule
