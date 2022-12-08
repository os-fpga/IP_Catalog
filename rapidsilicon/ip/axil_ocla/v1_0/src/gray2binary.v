
//////////////////////////////////////////////////////////////////////////////////
// Company: Rapid Silicon
// Engineer:
//
// Create Date: 10/17/2022 04:34:13 PM
// Design Name: Gray to Binary
// Module Name: Gray to Binary
// Project Name: OCLA IP Core Development
// Target Devices: Gemini RS-75
// Tool Versions: Raptor
// Description:
// TBA
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////

module gray2binary #(
    parameter DATA_WIDTH = 4
) (
    input wire clk,
    input wire rstn,
    input  wire [DATA_WIDTH:0] gray,
    // input wire enable,
    output reg [DATA_WIDTH:0] binary
);
wire [DATA_WIDTH-1:0] binary_in;
genvar i;
  generate
    for (i = 0; i < DATA_WIDTH; i = i + 1) begin
      //assign binary_in[i] = enable ? ^gray[DATA_WIDTH-1:i] : 'b0;
      assign binary_in[i] = ^(gray >> i);

    end
  endgenerate

  always @(posedge clk or negedge rstn  ) begin
    if(!rstn) begin
      binary <= 'b0;
    end
    else begin
      // if (enable)
      binary <= {1'b0,binary_in};
      // else
      //   binary <= binary;    
  end
end

endmodule
