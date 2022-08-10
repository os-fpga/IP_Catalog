# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os

from migen import *

from litex.soc.interconnect import axi

from litex.soc.integration.soc import *
from litex.soc.integration.doc import AutoDoc, ModuleDoc

# AXI GPIO -----------------------------------------------------------------------------------------

class AXIGPIO(Module, AutoDoc, AutoCSR):
    def __init__(self, platform, pads, default_enable=0):
        self.intro = ModuleDoc("""AXIGPIO: A verilog RTL-based AXI GPIO core wrapped from Xilinx Vivado IP library.""")

        self.bus = bus = axi.AXILiteInterface(address_width=32,data_width=32)
        self.gpin  = Signal(32)
        self.gpout = Signal(32)
        self.int   = Signal()

        # # #

        # Compute Parameters.
        internal = not (hasattr(pads, "o")  and hasattr(pads, "i"))
        nbits    = len(pads) if internal else len(pads.o)
        if internal:
            if isinstance(pads, Record):
                pads = pads.flatten()

        # Verilog-RTL Instance.
        self.specials += Instance("AXI4LITE_GPIO",
            # Clk/Rst.
            i_CLK     =  ClockSignal("sys"),
            i_RSTN    = ~ResetSignal("sys"),

            # GPIOS
            i_GPIN    = self.gpin,
            o_GPOUT   = self.gpout,
            o_INT     = self.int,

            # AW AXI-Lite Channel.
            i_AWADDR  = bus.aw.addr,
            i_AWPROT  = 0,
            i_AWVALID = bus.aw.valid,
            o_AWREADY = bus.aw.ready,

            # W AXI-Lite Channel.
            i_WDATA   = bus.w.data,
            i_WSTRB   = bus.w.strb,
            i_WVALID  = bus.w.valid,
            o_WREADY  = bus.w.ready,

            # B AXI-Lite Channel.
            o_BRESP   = bus.b.resp,
            o_BVALID  = bus.b.valid,
            i_BREADY  = bus.b.ready,

            # AR AXI-Lite Channel.
            i_ARADDR  = bus.ar.addr,
            i_ARPROT  = 0,
            i_ARVALID = bus.ar.valid,
            o_ARREADY = bus.ar.ready,

            # R AXI-Lite Channel.
            o_RDATA   = bus.r.data,
            o_RRESP   = bus.r.resp,
            o_RVALID  = bus.r.valid,
            i_RREADY  = bus.r.ready,
        )

        # Connect Pads.
        nbits = 7 # FIXME: Why is this required, avoid fixed numbers.
        for i in range(nbits):
            self.comb += pads.i[i].eq(self.gpin[i])
            self.comb += pads.o[i].eq(self.gpout[i])

        # Add Verilog-RTL Sources.
        self.add_sources(platform)

    def add_sources(self, platform):
        rtl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "./../rtl")
        platform.add_source_dir(path=rtl_path)
