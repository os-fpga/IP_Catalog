module iverilog_dump();
initial begin
    $dumpfile("ahb2axi4_wrapper.fst");
    $dumpvars(0, ahb2axi4_wrapper);
end
endmodule
