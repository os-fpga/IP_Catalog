# This file is Copyright (c) 2022 RapidSilicon.
# SPDX-License-Identifier: TBD.

import os

from migen import *

from litex.soc.interconnect import axi

from litex.soc.integration.soc import *
from litex.soc.integration.doc import AutoDoc, ModuleDoc
from litex.soc.integration.soc import SoCRegion

# Helpers ------------------------------------------------------------------------------------------

class Open(Signal): pass

# AXI RAM -----------------------------------------------------------------------------------------

class AXIRAM(Module, AutoDoc, AutoCSR):
    """LiteX Verilog RTL-based Axi_ram"""
    def __init__(self, platform, pads, default_enable=0):
        self.intro = ModuleDoc("""AXIRAM: A verilog RTL-based AXI RAM wrapped from Alex Forenchich's Verilog AXI library.""")

        self.bus  = bus = axi.AXILiteInterface(data_width=32)

        # # #

        # Verilog-RTL Instance.
        self.specials += Instance("axi_ram",
            # Clk/Rst.
            i_clk           = ClockSignal("sys"),
            i_rst           = ResetSignal("sys"),

            # AW AXI-Lite Channel.
            i_s_axi_awid    = 0,
            i_s_axi_awaddr  = bus.aw.addr,
            i_s_axi_awlen   = 0,
            i_s_axi_awsize  = 0,
            i_s_axi_awburst = 0,
            i_s_axi_awlock  = 0,
            i_s_axi_awcache = 0,
            i_s_axi_awprot  = 0,
            i_s_axi_awvalid = bus.aw.valid,
            o_s_axi_awready = bus.aw.ready,

            # W AXI-Lite Channel.
            i_s_axi_wdata   = bus.w.data,
            i_s_axi_wstrb   = bus.w.strb,
            i_s_axi_wlast   = 0,
            i_s_axi_wvalid  = bus.w.valid,
            o_s_axi_wready  = bus.w.ready,

            # B AXI-Lite Channel.
            o_s_axi_bid     = Open(),
            o_s_axi_bresp   = bus.b.resp,
            o_s_axi_bvalid  = bus.b.valid,
            i_s_axi_bready  = bus.b.ready,
            i_s_axi_arid    = 0,

            # AR AXI-Lite Channel.
            i_s_axi_araddr  = bus.ar.addr,
            i_s_axi_arlen   = 0,
            i_s_axi_arsize  = 0,
            i_s_axi_arburst = 0,
            i_s_axi_arlock  = 0,
            i_s_axi_arcache = 0,
            i_s_axi_arprot  = 0,
            i_s_axi_arvalid = bus.ar.valid,
            o_s_axi_arready = bus.ar.ready,

            # R AXI-Lite Channel.
            o_s_axi_rid     = Open(),
            o_s_axi_rdata   = bus.r.data,
            o_s_axi_rresp   = bus.r.resp,
            o_s_axi_rlast   = Open(),
            o_s_axi_rvalid  = bus.r.valid,
            i_s_axi_rready  = bus.r.ready,
        )
        
        # Add Verilog-RTL Sources.
        self.add_sources(platform)

    def add_sources(self, platform):
        rtl_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "./../rtl")
        platform.add_source(os.path.join(rtl_path, "axi_ram.v"))
