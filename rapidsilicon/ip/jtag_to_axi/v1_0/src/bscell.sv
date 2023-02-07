// start of the boundry scan cell code

module bscell
  (
    // inputs 
    input logic 	clk_i,            // clock for flops (??)
    input logic 	rst_ni,           // reset (??)
    input logic 	mode_i,           // Mode
    input logic 	enable_i,         // n/a
    input logic 	shift_dr_i,       // ShiftDR
    input logic 	capture_dr_i,     // 
    input logic 	update_dr_i,      // UpdateDR
    input logic 	scan_in_i,        // From last cell
    input logic 	jtagreg_in_i,     // From system pin
    
    // outputs
    output logic scan_out_o,          // To next cell
    output logic jtagreg_out_o        // To system logic
  );

   logic 	r_dataout;
   logic 	r_datasample;
   logic 	s_datasample_next;

   always_ff @ (negedge rst_ni, posedge clk_i)
   begin
	 if (~rst_ni)
	 begin
	   r_datasample <= 1'b0;
	   r_dataout    <= 1'b0;
	 end
     else
     begin
	   if((shift_dr_i | capture_dr_i) & enable_i)
         r_datasample <= s_datasample_next;
	   if(update_dr_i & enable_i)
         r_dataout <= r_datasample;
	   end
     end

   assign s_datasample_next = (shift_dr_i) ? scan_in_i : jtagreg_in_i;
   assign jtagreg_out_o = (mode_i) ? r_dataout : jtagreg_in_i;
   assign scan_out_o = r_datasample;
//   assign scan_out_o = r_dataout;
endmodule
