#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around SpinalHDL VexRiscv

import os

from migen import *

## ----------------VexRiscv Configuration without Cache and MMU----------------------------------------

class vexriscv_nocache_nommu(Module):
    def __init__(self, platform, ibus, dbus):
        self.platform          = platform
        self.human_name        = "vexriscv_nocache_nommu"
        self.external_variant  = None
        self.ibus              = ibus
        self.dbus              = dbus
        self.reset             = Signal()
        self.interrupt         = Signal()

        # Jtag Signals
        self.jtag_tms          = Signal()
        self.jtag_tdi          = Signal()
        self.jtag_tdo          = Signal()
        self.jtag_tck          = Signal()

        # Other IOs
        self.timerInterrupt    = Signal()
        self.externalInterrupt = Signal()
        self.softwareInterrupt = Signal()
        self.debugReset        = Signal()
        self.debug_resetOut    = Signal()    

        # CPU Instance.
        self.specials += Instance("vexriscv_uncached_nommu",
            # Clk / Rst.
            # ----------
            i_clk                       = ClockSignal(),
            i_reset                     = ResetSignal(),

            #Interrupts/Debug
            i_externalInterrupt         = self.timerInterrupt,
            i_timerInterrupt            = self.externalInterrupt,
            i_softwareInterrupt         = self.softwareInterrupt,
            i_debugReset                = self.debugReset,
            o_debug_resetOut            = self.debug_resetOut,  

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
            i_jtag_tms                  = self.jtag_tms,
            i_jtag_tdi                  = self.jtag_tdi,
            o_jtag_tdo                  = self.jtag_tdo,
            i_jtag_tck                  = self.jtag_tck,
        )
        # Add Sources.
        # ------------
        self.add_sources(platform)
    def set_reset_address(self, reset_address):
        assert not hasattr(self, "reset_address")
        self.reset_address = reset_address

    @staticmethod
    def add_sources(platform, variant="standard"):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "vexriscv_uncached_nommu.v"))


## ----------------VexRiscv Configuration with Cache and MMU----------------------------------------

class vexriscv_linux_mmu(Module):
    def __init__(self, platform, ibus, dbus):
        self.platform           = platform
        self.human_name         = "vexriscv_linux_mmu"
        self.external_variant   = None
        self.ibus               = ibus
        self.dbus               = dbus
        self.reset              = Signal()
        self.interrupt          = Signal()

        # Jtag Signals
        self.jtag_tms           = Signal()
        self.jtag_tdi           = Signal()
        self.jtag_tdo           = Signal()
        self.jtag_tck           = Signal()

        # Other IOs 
        self.timerInterrupt     = Signal()
        self.externalInterrupt  = Signal()
        self.softwareInterrupt  = Signal()
        self.debugReset         = Signal()
        self.debug_resetOut     = Signal()    
        self.externalInterruptS = Signal()
        self.utime              = Signal()

        # CPU Instance.
        self.specials += Instance("vexriscv_cached_mmu",
            # Clk / Rst.
            # ----------
            i_clk                       = ClockSignal(),
            i_reset                     = ResetSignal(),

            #Interrupts/Debug
            i_externalInterrupt         = self.timerInterrupt,
            i_timerInterrupt            = self.externalInterrupt,
            i_softwareInterrupt         = self.softwareInterrupt,
            i_debugReset                = self.debugReset,
            o_debug_resetOut            = self.debug_resetOut,
            i_externalInterruptS        = self.externalInterruptS,
            i_utime                     = self.utime,

            # IBUS AXI-FULL   
            # -------------
            # AR.
            o_iBusAxi_arvalid           = self.ibus.ar.valid,
            i_iBusAxi_arready           = self.ibus.ar.ready,
            o_iBusAxi_araddr            = self.ibus.ar.addr,
            o_iBusAxi_arid              = self.ibus.ar.id,
            o_iBusAxi_arregion          = self.ibus.ar.region,
            o_iBusAxi_arlen             = self.ibus.ar.len,
            o_iBusAxi_arsize            = self.ibus.ar.size,
            o_iBusAxi_arburst           = self.ibus.ar.burst,
            o_iBusAxi_arlock            = self.ibus.ar.lock,
            o_iBusAxi_arcache           = self.ibus.ar.cache,
            o_iBusAxi_arqos             = self.ibus.ar.qos,
            o_iBusAxi_arprot            = self.ibus.ar.prot,

            # R.
            i_iBusAxi_rvalid            = self.ibus.r.valid,
            o_iBusAxi_rready            = self.ibus.r.ready,
            i_iBusAxi_rdata             = self.ibus.r.data,
            i_iBusAxi_rid               = self.ibus.r.id,
            i_iBusAxi_rresp             = self.ibus.r.resp,
            i_iBusAxi_rlast             = self.ibus.r.last,

            # DBUS AXI-FULL
            # -------------
            # AW.
            o_dBusAxi_awvalid           = self.dbus.aw.valid,
            i_dBusAxi_awready           = self.dbus.aw.ready,
            o_dBusAxi_awaddr            = self.dbus.aw.addr,
            o_dBusAxi_awid              = self.dbus.aw.id,
            o_dBusAxi_awregion          = self.dbus.aw.region,
            o_dBusAxi_awlen             = self.dbus.aw.len,
            o_dBusAxi_awsize            = self.dbus.aw.size,
            o_dBusAxi_awburst           = self.dbus.aw.burst,
            o_dBusAxi_awlock            = self.dbus.aw.lock,
            o_dBusAxi_awcache           = self.dbus.aw.cache,
            o_dBusAxi_awqos             = self.dbus.aw.qos,
            o_dBusAxi_awprot            = self.dbus.aw.prot,
            
            # W.
            o_dBusAxi_wvalid            = self.dbus.w.valid,
            i_dBusAxi_wready            = self.dbus.w.ready,
            o_dBusAxi_wdata             = self.dbus.w.data,
            o_dBusAxi_wstrb             = self.dbus.w.strb,
            o_dBusAxi_wlast             = self.dbus.w.last,
            
            # B.
            i_dBusAxi_bvalid            = self.dbus.b.valid,
            o_dBusAxi_bready            = self.dbus.b.ready,
            i_dBusAxi_bid               = self.dbus.b.id,
            i_dBusAxi_bresp             = self.dbus.b.resp,

            # AR.
            o_dBusAxi_arvalid           = self.dbus.ar.valid,
            i_dBusAxi_arready           = self.dbus.ar.ready,
            o_dBusAxi_araddr            = self.dbus.ar.addr,
            o_dBusAxi_arid              = self.dbus.ar.id,
            o_dBusAxi_arregion          = self.dbus.ar.region,
            o_dBusAxi_arlen             = self.dbus.ar.len,
            o_dBusAxi_arsize            = self.dbus.ar.size,
            o_dBusAxi_arburst           = self.dbus.ar.burst,
            o_dBusAxi_arlock            = self.dbus.ar.lock,
            o_dBusAxi_arcache           = self.dbus.ar.cache,
            o_dBusAxi_arqos             = self.dbus.ar.qos,
            o_dBusAxi_arprot            = self.dbus.ar.prot,
            
            # R.
            i_dBusAxi_rvalid            = self.dbus.r.valid,
            o_dBusAxi_rready            = self.dbus.r.ready,
            i_dBusAxi_rdata             = self.dbus.r.data,
            i_dBusAxi_rid               = self.dbus.r.id,
            i_dBusAxi_rresp             = self.dbus.r.resp,
            i_dBusAxi_rlast             = self.dbus.r.last,

            # JTAG
            i_jtag_tms                  = self.jtag_tms,
            i_jtag_tdi                  = self.jtag_tdi,
            o_jtag_tdo                  = self.jtag_tdo,
            i_jtag_tck                  = self.jtag_tck,
        )
        # Add Sources.
        # ------------
        self.add_sources(platform)
    def set_reset_address(self, reset_address):
        assert not hasattr(self, "reset_address")
        self.reset_address = reset_address

    @staticmethod
    def add_sources(platform, variant="standard"):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "vexriscv_cached_mmu.v"))


## ----------------VexRiscv Configuration with Cache, MMU, PLIC and CLINT--------------------------------

class vexriscv_plic_clint(Module):
    def __init__(self, platform, ibus, dbus):
        self.platform           = platform
        self.human_name         = "vexriscv_plic_clint"
        self.external_variant   = None
        self.ibus               = ibus
        self.dbus               = dbus
        self.reset              = Signal()
        self.interrupt          = Signal()

        # Jtag Signals
        self.jtag_tms           = Signal()
        self.jtag_tdi           = Signal()
        self.jtag_tdo           = Signal()
        self.jtag_tck           = Signal()

        # Other IOs
        self.debugReset         = Signal()
        self.debug_resetOut     = Signal()

        # PLIC IOs
        self.plic_awvalid       = Signal()
        self.plic_awready       = Signal()
        self.plic_awaddr        = Signal()
        self.plic_awprot        = Signal()
        self.plic_wvalid        = Signal()
        self.plic_wready        = Signal()
        self.plic_wdata         = Signal()
        self.plic_wstrb         = Signal()
        self.plic_bvalid        = Signal()
        self.plic_bready        = Signal()
        self.plic_bresp         = Signal()
        self.plic_arvalid       = Signal()
        self.plic_arready       = Signal()
        self.plic_araddr        = Signal()
        self.plic_arprot        = Signal()
        self.plic_rvalid        = Signal()
        self.plic_rready        = Signal()
        self.plic_rdata         = Signal()
        self.plic_rresp         = Signal()
        self.plicInterrupts     = Signal()

        # CLINT IOs
        self.clint_awvalid      = Signal()
        self.clint_awready      = Signal()
        self.clint_awaddr       = Signal()
        self.clint_awprot       = Signal()
        self.clint_wvalid       = Signal()
        self.clint_wready       = Signal()
        self.clint_wdata        = Signal()
        self.clint_wstrb        = Signal()
        self.clint_bvalid       = Signal()
        self.clint_bready       = Signal()
        self.clint_bresp        = Signal()
        self.clint_arvalid      = Signal()
        self.clint_arready      = Signal()
        self.clint_araddr       = Signal()
        self.clint_arprot       = Signal()
        self.clint_rvalid       = Signal()
        self.clint_rready       = Signal()
        self.clint_rdata        = Signal()
        self.clint_rresp        = Signal()

        # CPU Instance.
        self.specials += Instance("vexriscv_cached_mmu_plic_clint",
            # Clk / Rst.
            # ----------
            i_clk                       = ClockSignal(),
            i_reset                     = ResetSignal(),

            #Interrupts/Debug
            i_debugReset                = self.debugReset,
            o_debug_resetOut            = self.debug_resetOut,  

            # IBUS AXI-FULL   
            # -------------
            # AR.
            o_iBusAxi_arvalid           = self.ibus.ar.valid,
            i_iBusAxi_arready           = self.ibus.ar.ready,
            o_iBusAxi_araddr            = self.ibus.ar.addr,
            o_iBusAxi_arid              = self.ibus.ar.id,
            o_iBusAxi_arregion          = self.ibus.ar.region,
            o_iBusAxi_arlen             = self.ibus.ar.len,
            o_iBusAxi_arsize            = self.ibus.ar.size,
            o_iBusAxi_arburst           = self.ibus.ar.burst,
            o_iBusAxi_arlock            = self.ibus.ar.lock,
            o_iBusAxi_arcache           = self.ibus.ar.cache,
            o_iBusAxi_arqos             = self.ibus.ar.qos,
            o_iBusAxi_arprot            = self.ibus.ar.prot,

            # R.
            i_iBusAxi_rvalid            = self.ibus.r.valid,
            o_iBusAxi_rready            = self.ibus.r.ready,
            i_iBusAxi_rdata             = self.ibus.r.data,
            i_iBusAxi_rid               = self.ibus.r.id,
            i_iBusAxi_rresp             = self.ibus.r.resp,
            i_iBusAxi_rlast             = self.ibus.r.last,

            # DBUS AXI-FULL
            # -------------
            # AW.
            o_dBusAxi_awvalid           = self.dbus.aw.valid,
            i_dBusAxi_awready           = self.dbus.aw.ready,
            o_dBusAxi_awaddr            = self.dbus.aw.addr,
            o_dBusAxi_awid              = self.dbus.aw.id,
            o_dBusAxi_awregion          = self.dbus.aw.region,
            o_dBusAxi_awlen             = self.dbus.aw.len,
            o_dBusAxi_awsize            = self.dbus.aw.size,
            o_dBusAxi_awburst           = self.dbus.aw.burst,
            o_dBusAxi_awlock            = self.dbus.aw.lock,
            o_dBusAxi_awcache           = self.dbus.aw.cache,
            o_dBusAxi_awqos             = self.dbus.aw.qos,
            o_dBusAxi_awprot            = self.dbus.aw.prot,
            
            # W.
            o_dBusAxi_wvalid            = self.dbus.w.valid,
            i_dBusAxi_wready            = self.dbus.w.ready,
            o_dBusAxi_wdata             = self.dbus.w.data,
            o_dBusAxi_wstrb             = self.dbus.w.strb,
            o_dBusAxi_wlast             = self.dbus.w.last,
            
            # B.
            i_dBusAxi_bvalid            = self.dbus.b.valid,
            o_dBusAxi_bready            = self.dbus.b.ready,
            i_dBusAxi_bid               = self.dbus.b.id,
            i_dBusAxi_bresp             = self.dbus.b.resp,

            # AR.
            o_dBusAxi_arvalid           = self.dbus.ar.valid,
            i_dBusAxi_arready           = self.dbus.ar.ready,
            o_dBusAxi_araddr            = self.dbus.ar.addr,
            o_dBusAxi_arid              = self.dbus.ar.id,
            o_dBusAxi_arregion          = self.dbus.ar.region,
            o_dBusAxi_arlen             = self.dbus.ar.len,
            o_dBusAxi_arsize            = self.dbus.ar.size,
            o_dBusAxi_arburst           = self.dbus.ar.burst,
            o_dBusAxi_arlock            = self.dbus.ar.lock,
            o_dBusAxi_arcache           = self.dbus.ar.cache,
            o_dBusAxi_arqos             = self.dbus.ar.qos,
            o_dBusAxi_arprot            = self.dbus.ar.prot,
            
            # R.
            i_dBusAxi_rvalid            = self.dbus.r.valid,
            o_dBusAxi_rready            = self.dbus.r.ready,
            i_dBusAxi_rdata             = self.dbus.r.data,
            i_dBusAxi_rid               = self.dbus.r.id,
            i_dBusAxi_rresp             = self.dbus.r.resp,
            i_dBusAxi_rlast             = self.dbus.r.last,

            # JTAG
            i_jtag_tms                  = self.jtag_tms,
            i_jtag_tdi                  = self.jtag_tdi,
            o_jtag_tdo                  = self.jtag_tdo,
            i_jtag_tck                  = self.jtag_tck,

            # PLIC
            i_plic_awvalid              = self.plic_awvalid,
            o_plic_awready              = self.plic_awready,
            i_plic_awaddr               = self.plic_awaddr,
            i_plic_awprot               = self.plic_awprot,
            i_plic_wvalid               = self.plic_wvalid,
            o_plic_wready               = self.plic_wready,
            i_plic_wdata                = self.plic_wdata,
            i_plic_wstrb                = self.plic_wstrb,
            o_plic_bvalid               = self.plic_bvalid,
            i_plic_bready               = self.plic_bready,
            o_plic_bresp                = self.plic_bresp,
            i_plic_arvalid              = self.plic_arvalid,
            o_plic_arready              = self.plic_arready,
            i_plic_araddr               = self.plic_araddr,
            i_plic_arprot               = self.plic_arprot,
            o_plic_rvalid               = self.plic_rvalid,
            i_plic_rready               = self.plic_rready,
            o_plic_rdata                = self.plic_rdata,
            o_plic_rresp                = self.plic_rresp,
            i_plicInterrupts            = self.plicInterrupts,
            
            # CLINT     
            i_clint_awvalid             = self.clint_awvalid,
            o_clint_awready             = self.clint_awready,
            i_clint_awaddr              = self.clint_awaddr,
            i_clint_awprot              = self.clint_awprot,
            i_clint_wvalid              = self.clint_wvalid,
            o_clint_wready              = self.clint_wready,
            i_clint_wdata               = self.clint_wdata,
            i_clint_wstrb               = self.clint_wstrb,
            o_clint_bvalid              = self.clint_bvalid,
            i_clint_bready              = self.clint_bready,
            o_clint_bresp               = self.clint_bresp,
            i_clint_arvalid             = self.clint_arvalid,
            o_clint_arready             = self.clint_arready,
            i_clint_araddr              = self.clint_araddr,
            i_clint_arprot              = self.clint_arprot,
            o_clint_rvalid              = self.clint_rvalid,
            i_clint_rready              = self.clint_rready,
            o_clint_rdata               = self.clint_rdata,
            o_clint_rresp               = self.clint_rresp
        )
        # Add Sources.
        # ------------
        self.add_sources(platform)
    def set_reset_address(self, reset_address):
        assert not hasattr(self, "reset_address")
        self.reset_address = reset_address

    @staticmethod
    def add_sources(platform, variant="standard"):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "vexriscv_cached_mmu_plic_clint.v"))