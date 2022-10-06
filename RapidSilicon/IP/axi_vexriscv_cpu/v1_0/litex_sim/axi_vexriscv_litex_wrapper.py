#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around SPinalHDL VexRiscvAxi4.v

import os

from migen import *

class VexRiscv(Module):
    def __init__(self, platform, ibus, dbus, variant="standard"):
        self.platform         = platform
        self.variant          = variant
        self.human_name       = "VexRiscv"
        self.external_variant = None
        self.ibus             = ibus
        self.dbus             = dbus
        self.reset            = Signal()
        self.interrupt        = Signal(32)

        # Jtag Signals
        self.jtag_tms         = Signal()
        self.jtag_tdi         = Signal()
        self.jtag_tdo         = Signal()
        self.jtag_tck         = Signal()

        # Other IOs
        self.timerInterrupt   = Signal()
        self.externalInterrupt= Signal()
        self.softwareInterrupt= Signal()
        self.debugReset       = Signal()
        self.debug_resetOut   = Signal()    


        # CPU Instance.
        self.cpu_params = dict(

            # Clk / Rst.
            # ----------
            i_clk                    = ClockSignal("sys"),
            i_reset                  = ResetSignal("sys") | self.reset,

            #Interrupts/Debug
            i_externalInterrupt     = self.timerInterrupt,
            i_timerInterrupt        = self.externalInterrupt,
            i_softwareInterrupt     = self.softwareInterrupt,
            i_debugReset            = self.debugReset,
            o_debug_resetOut        = self.debug_resetOut,  

            # IBUS AXI-FULL   
            # -------------
            # AR.
            o_iBusAxi_ar_valid          = self.ibus.ar.valid,
            i_iBusAxi_ar_ready          = self.ibus.ar.ready,
            o_iBusAxi_ar_payload_addr   = self.ibus.ar.addr,
            o_iBusAxi_ar_payload_id     = self.ibus.ar.id,
            o_iBusAxi_ar_payload_region = self.ibus.ar.region,
            o_iBusAxi_ar_payload_len    = self.ibus.ar.len,
            o_iBusAxi_ar_payload_size   = self.ibus.ar.size,
            o_iBusAxi_ar_payload_burst  = self.ibus.ar.burst,
            o_iBusAxi_ar_payload_lock   = self.ibus.ar.lock,
            o_iBusAxi_ar_payload_cache  = self.ibus.ar.cache,
            o_iBusAxi_ar_payload_qos    = self.ibus.ar.qos,
            o_iBusAxi_ar_payload_prot   = self.ibus.ar.prot,

            # R.
            i_iBusAxi_r_valid           = self.ibus.r.valid,
            o_iBusAxi_r_ready           = self.ibus.r.ready,
            i_iBusAxi_r_payload_data    = self.ibus.r.data,
            i_iBusAxi_r_payload_id      = self.ibus.r.id,
            i_iBusAxi_r_payload_resp    = self.ibus.r.resp,
            i_iBusAxi_r_payload_last    = self.ibus.r.last,

            # DBUS AXI-FULL
            # -------------
            # AW.
            o_dBusAxi_aw_valid          = self.dbus.aw.valid,
            i_dBusAxi_aw_ready          = self.dbus.aw.ready,
            o_dBusAxi_aw_payload_addr   = self.dbus.aw.addr,
            o_dBusAxi_aw_payload_id     = self.dbus.aw.id,
            o_dBusAxi_aw_payload_region = self.dbus.aw.region,
            o_dBusAxi_aw_payload_len    = self.dbus.aw.len,
            o_dBusAxi_aw_payload_size   = self.dbus.aw.size,
            o_dBusAxi_aw_payload_burst  = self.dbus.aw.burst,
            o_dBusAxi_aw_payload_lock   = self.dbus.aw.lock,
            o_dBusAxi_aw_payload_cache  = self.dbus.aw.cache,
            o_dBusAxi_aw_payload_qos    = self.dbus.aw.qos,
            o_dBusAxi_aw_payload_prot   = self.dbus.aw.prot,
            
            # W.
            o_dBusAxi_w_valid           = self.dbus.w.valid,
            i_dBusAxi_w_ready           = self.dbus.w.ready,
            o_dBusAxi_w_payload_data    = self.dbus.w.data,
            o_dBusAxi_w_payload_strb    = self.dbus.w.strb,
            o_dBusAxi_w_payload_last    = self.dbus.w.last,
            
            # B.
            i_dBusAxi_b_valid           = self.dbus.b.valid,
            o_dBusAxi_b_ready           = self.dbus.b.ready,
            i_dBusAxi_b_payload_id      = self.dbus.b.id,
            i_dBusAxi_b_payload_resp    = self.dbus.b.resp,

            # AR.
            o_dBusAxi_ar_valid          = self.dbus.ar.valid,
            i_dBusAxi_ar_ready          = self.dbus.ar.ready,
            o_dBusAxi_ar_payload_addr   = self.dbus.ar.addr,
            o_dBusAxi_ar_payload_id     = self.dbus.ar.id,
            o_dBusAxi_ar_payload_region = self.dbus.ar.region,
            o_dBusAxi_ar_payload_len    = self.dbus.ar.len,
            o_dBusAxi_ar_payload_size   = self.dbus.ar.size,
            o_dBusAxi_ar_payload_burst  = self.dbus.ar.burst,
            o_dBusAxi_ar_payload_lock   = self.dbus.ar.lock,
            o_dBusAxi_ar_payload_cache  = self.dbus.ar.cache,
            o_dBusAxi_ar_payload_qos    = self.dbus.ar.qos,
            o_dBusAxi_ar_payload_prot   = self.dbus.ar.prot,
            
            # R.
            i_dBusAxi_r_valid           = self.dbus.r.valid,
            o_dBusAxi_r_ready           = self.dbus.r.ready,
            i_dBusAxi_r_payload_data    = self.dbus.r.data,
            i_dBusAxi_r_payload_id      = self.dbus.r.id,
            i_dBusAxi_r_payload_resp    = self.dbus.r.resp,
            i_dBusAxi_r_payload_last    = self.dbus.r.last,

            # JTAG
            i_jtag_tms= self.jtag_tms,
            i_jtag_tdi= self.jtag_tdi,
            o_jtag_tdo= self.jtag_tdo,
            i_jtag_tck= self.jtag_tck,
        )

    def set_reset_address(self, reset_address):
        assert not hasattr(self, "reset_address")
        self.reset_address = reset_address

    @staticmethod
    def add_sources(platform, variant="standard"):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "VexRiscvAxi4.v"))

    def do_finalize(self):
        self.specials += Instance("VexRiscvAxi4", **self.cpu_params)
