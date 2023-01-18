// ---------------------------------------------------------------
// User specified macros
// ---------------------------------------------------------------
`define NUM_OF_PROBES  28
`define MEMORY_DEPTH  1024
`define NUM_OF_TRIGGER_INPUTS  1
`define PROBE_WIDHT_BITS 1
`define TRIGGER_INPUTS  
// ---------------------------------------------------------------
// Common 
// ---------------------------------------------------------------

// `define NUM_OF_PROBES 32                              // number of probes


// ---------------------------------------------------------------
// OCLA TOP
// ---------------------------------------------------------------

//`define TRIGGER_INPUTS                                // to enable
//`define NUM_OF_TRIGGER_INPUTS 1                       // Number of trigger inputs
`define AXI_LITE_INTF                                    // axi lite interface enable


// ---------------------------------------------------------------
// Trigger Control Unit 
// ---------------------------------------------------------------

// `define ADVANCE_TRIGGER                              // to enable multi trigger capture mode
`define WIDTH 32                                        // data WIDTH
//`define TRIGGER_SIGNAL_SELECT_RANGE `NUM_OF_PROBES > 32 ? 32:`NUM_OF_PROBES              // range of trigger signals from probes 
`define TRIGGER_SIGNAL_SELECT_RANGE 32
`define SELECT_MUX_WIDTH `NUM_OF_PROBES <= 1 ? 1 : $clog2(`TRIGGER_SIGNAL_SELECT_RANGE)  // mux select line WIDTH to select trigger signal
// `define VALUE_COMPARE_TRIGGER                        // to enable value compare mode of trigger
// `define PROBE_WIDHT_BITS 4                           // probe WIDTH for value compare



// ---------------------------------------------------------------
// OCLA Controller 
// ---------------------------------------------------------------

`define MEMORY_DEPTH_HALF `MEMORY_DEPTH/2
`define SAMPLE_COUNTER_WIDTH `COUNTER_WIDHT



// ---------------------------------------------------------------
// OCLA Memory Controller
// ---------------------------------------------------------------

// `define MEMORY_DEPTH 1024                            // memory depth of the FIFO
`define SYNC_STAGES 2                                   // synchronizer flops 
`define COUNTER_WIDHT $clog2(`MEMORY_DEPTH)             // counter WIDTH




// ---------------------------------------------------------------
// Sampler buffer 
// ---------------------------------------------------------------

`define BUFFER_STAGES 4                                 // Buffer registers   



// ---------------------------------------------------------------
// Stream Out Buffer 
// ---------------------------------------------------------------

`define REM_BITS  `NUM_OF_PROBES < 32 ? 32 - `NUM_OF_PROBES : (`NUM_OF_PROBES - ($floor(`NUM_OF_PROBES / 32) * 32))== 0 ? 0 : 32 -  (`NUM_OF_PROBES - ($floor(`NUM_OF_PROBES / 32) * 32)) 
                                                        // in case number of probe is not a multiple of 32
`define WORD_CHUNKS `NUM_OF_PROBES > 32 ? (`NUM_OF_PROBES / 32) +((`NUM_OF_PROBES - $floor(`NUM_OF_PROBES / 32) * 32 )== 0 ? 0:1):1  
                                                        // number of 32 bit words in which probes can be divided
`define PROBE_BITS 32 - int'(`REM_BITS) 
`define WORD_CHUNK_CNTR_WIDTH `WORD_CHUNKS > 1? int'($clog2(`WORD_CHUNKS)):1 
							// number of bits required to count number of word chunks



// ---------------------------------------------------------------
// AXI Slave Interface
// ---------------------------------------------------------------
`define S_AXI_DATA_WIDTH 32                              // axi data WIDTH
`define S_AXI_ADDR_WIDTH 32                              // axi address WIDTH



// ---------------------------------------------------------------
// Dual Synchronizer flop
// ---------------------------------------------------------------

`define REG_WIDTH 1                                      // Dual synchronizer width

