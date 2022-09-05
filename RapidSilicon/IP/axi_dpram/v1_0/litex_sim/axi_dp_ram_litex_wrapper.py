#
# This file is part of LiteX-Verilog-AXI-Test
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# LiteX wrapper around Alex Forencich Verilog-AXI's axi_dp_ram.v.

import os
import logging
import math

from migen import *

from litex.soc.interconnect.axi import *


logging.basicConfig(level=logging.INFO)

# AXI DP RAM ---------------------------------------------------------------------------------------

class AXIDPRAM(Module):
    def __init__(self, platform, s_axi_a, s_axi_b, size=0x1000,
        a_pipeline_output = False,
        a_interleave      = False,
        b_pipeline_output = False,
        b_interleave      = False,
    ):
        self.logger = logging.getLogger("AXIDPRAM")

        # Get/Check Parameters.
        # ---------------------

        # Clock Domain.
        self.logger.info(f"Clock Domain A: {s_axi_a.clock_domain}")
        self.logger.info(f"Clock Domain B: {s_axi_b.clock_domain}")

        # Address width.
        address_width = len(s_axi_a.aw.addr)
        self.logger.info(f"Address Width: {address_width}")

        # Data width.
        data_width = len(s_axi_a.w.data)
        self.logger.info(f"Data Width: {data_width}")

        # ID width.
        id_width = len(s_axi_a.aw.id)
        self.logger.info(f"ID Width: {id_width}")

        # Size.
        self.logger.info(f"Size: {size}bytes")

        # Pipeline/Interleave.
        self.logger.info(f"A Pipeline Output: {a_pipeline_output}")
        self.logger.info(f"A Interleave R/W:  {a_interleave}")
        self.logger.info(f"B Pipeline Output: {b_pipeline_output}")
        self.logger.info(f"B Interleave R/W:  {b_interleave}")

        # Module instance.
        # ----------------

        self.specials += Instance("axi_dp_ram",
            # Parameters.
            # -----------
            # Global.
            p_DATA_WIDTH = data_width,
            p_ADDR_WIDTH = math.ceil(math.log2(size)),
            p_ID_WIDTH   = id_width,

            # Pipeline/Interleave.
            p_A_PIPELINE_OUTPUT = a_pipeline_output,
            p_A_INTERLEAVE      = a_interleave,
            p_B_PIPELINE_OUTPUT = b_pipeline_output,
            p_B_INTERLEAVE      = b_interleave,

            # Clk / Rst.
            # ----------
            i_a_clk = ClockSignal(s_axi_a.clock_domain),
            i_a_rst = ResetSignal(s_axi_a.clock_domain),
            i_b_clk = ClockSignal(s_axi_b.clock_domain),
            i_b_rst = ResetSignal(s_axi_b.clock_domain),

            # AXI A Slave Interface.
            # --------------------
            # AW.
            i_s_axi_a_awid     = s_axi_a.aw.id,
            i_s_axi_a_awaddr   = s_axi_a.aw.addr,
            i_s_axi_a_awlen    = s_axi_a.aw.len,
            i_s_axi_a_awsize   = s_axi_a.aw.size,
            i_s_axi_a_awburst  = s_axi_a.aw.burst,
            i_s_axi_a_awlock   = s_axi_a.aw.lock,
            i_s_axi_a_awcache  = s_axi_a.aw.cache,
            i_s_axi_a_awprot   = s_axi_a.aw.prot,
            i_s_axi_a_awvalid  = s_axi_a.aw.valid,
            o_s_axi_a_awready  = s_axi_a.aw.ready,

            # W.
            i_s_axi_a_wdata    = s_axi_a.w.data,
            i_s_axi_a_wstrb    = s_axi_a.w.strb,
            i_s_axi_a_wlast    = s_axi_a.w.last,
            i_s_axi_a_wvalid   = s_axi_a.w.valid,
            o_s_axi_a_wready   = s_axi_a.w.ready,

            # B.
            o_s_axi_a_bid      = s_axi_a.b.id,
            o_s_axi_a_bresp    = s_axi_a.b.resp,
            o_s_axi_a_bvalid   = s_axi_a.b.valid,
            i_s_axi_a_bready   = s_axi_a.b.ready,

            # AR.
            i_s_axi_a_arid     = s_axi_a.ar.id,
            i_s_axi_a_araddr   = s_axi_a.ar.addr,
            i_s_axi_a_arlen    = s_axi_a.ar.len,
            i_s_axi_a_arsize   = s_axi_a.ar.size,
            i_s_axi_a_arburst  = s_axi_a.ar.burst,
            i_s_axi_a_arlock   = s_axi_a.ar.lock,
            i_s_axi_a_arcache  = s_axi_a.ar.cache,
            i_s_axi_a_arprot   = s_axi_a.ar.prot,
            i_s_axi_a_arvalid  = s_axi_a.ar.valid,
            o_s_axi_a_arready  = s_axi_a.ar.ready,

            # R.
            o_s_axi_a_rid      = s_axi_a.r.id,
            o_s_axi_a_rdata    = s_axi_a.r.data,
            o_s_axi_a_rresp    = s_axi_a.r.resp,
            o_s_axi_a_rlast    = s_axi_a.r.last,
            o_s_axi_a_rvalid   = s_axi_a.r.valid,
            i_s_axi_a_rready   = s_axi_a.r.ready,

            # AXI B Slave Interface.
            # --------------------
            # AW.
            i_s_axi_b_awid     = s_axi_b.aw.id,
            i_s_axi_b_awaddr   = s_axi_b.aw.addr,
            i_s_axi_b_awlen    = s_axi_b.aw.len,
            i_s_axi_b_awsize   = s_axi_b.aw.size,
            i_s_axi_b_awburst  = s_axi_b.aw.burst,
            i_s_axi_b_awlock   = s_axi_b.aw.lock,
            i_s_axi_b_awcache  = s_axi_b.aw.cache,
            i_s_axi_b_awprot   = s_axi_b.aw.prot,
            i_s_axi_b_awvalid  = s_axi_b.aw.valid,
            o_s_axi_b_awready  = s_axi_b.aw.ready,

            # W.
            i_s_axi_b_wdata    = s_axi_b.w.data,
            i_s_axi_b_wstrb    = s_axi_b.w.strb,
            i_s_axi_b_wlast    = s_axi_b.w.last,
            i_s_axi_b_wvalid   = s_axi_b.w.valid,
            o_s_axi_b_wready   = s_axi_b.w.ready,

            # B.
            o_s_axi_b_bid      = s_axi_b.b.id,
            o_s_axi_b_bresp    = s_axi_b.b.resp,
            o_s_axi_b_bvalid   = s_axi_b.b.valid,
            i_s_axi_b_bready   = s_axi_b.b.ready,

            # AR.
            i_s_axi_b_arid     = s_axi_b.ar.id,
            i_s_axi_b_araddr   = s_axi_b.ar.addr,
            i_s_axi_b_arlen    = s_axi_b.ar.len,
            i_s_axi_b_arsize   = s_axi_b.ar.size,
            i_s_axi_b_arburst  = s_axi_b.ar.burst,
            i_s_axi_b_arlock   = s_axi_b.ar.lock,
            i_s_axi_b_arcache  = s_axi_b.ar.cache,
            i_s_axi_b_arprot   = s_axi_b.ar.prot,
            i_s_axi_b_arvalid  = s_axi_b.ar.valid,
            o_s_axi_b_arready  = s_axi_b.ar.ready,

            # R.
            o_s_axi_b_rid      = s_axi_b.r.id,
            o_s_axi_b_rdata    = s_axi_b.r.data,
            o_s_axi_b_rresp    = s_axi_b.r.resp,
            o_s_axi_b_rlast    = s_axi_b.r.last,
            o_s_axi_b_rvalid   = s_axi_b.r.valid,
            i_s_axi_b_rready   = s_axi_b.r.ready,
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axi_ram_wr_if.v"))
        platform.add_source(os.path.join(rtl_dir, "axi_ram_rd_if.v"))
        platform.add_source(os.path.join(rtl_dir, "axi_ram_wr_rd_if.v"))
        platform.add_source(os.path.join(rtl_dir, "axi_dp_ram.v"))
