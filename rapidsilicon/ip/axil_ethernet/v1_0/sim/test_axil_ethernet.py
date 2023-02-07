#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import subprocess
import argparse

from migen import *

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform
from litex.build.sim.config import SimConfig
from litex.build.sim.verilator import verilator_build_args, verilator_build_argdict

from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.interconnect.axi import *

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst.
    ("sys_clk", 0, Pins(1)),
    ("sys_rst", 0, Pins(1)),

    # Serial.
    ("serial", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),

        Subsignal("sink_valid", Pins(1)),
        Subsignal("sink_ready", Pins(1)),
        Subsignal("sink_data",  Pins(8)),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(SimPlatform):
    name = "sim"
    def __init__(self):
        SimPlatform.__init__(self, "SIM", _io)

# AXI Debug ----------------------------------------------------------------------------------------

class AXIAWDebug(Module):
    def __init__(self, axi, name=""):
        sync = getattr(self.sync, axi.clock_domain)
        sync += If(axi.aw.valid & axi.aw.ready,
            Display(f"AXI AW {name}: Addr: 0x%08x",
                axi.aw.addr
            ),
        )

class AXIWDebug(Module):
    def __init__(self, axi, name=""):
        sync = getattr(self.sync, axi.clock_domain)
        sync += If(axi.w.valid & axi.w.ready,
            Display(f"AXI W {name}: Data: 0x%x, Strb: %x",
                axi.w.data,
                axi.w.strb
            ),
        )

class AXIARDebug(Module):
    def __init__(self, axi, name=""):
        sync = getattr(self.sync, axi.clock_domain)
        sync += If(axi.ar.valid & axi.ar.ready,
            Display(f"AXI AR {name}: Addr: 0x%08x",
                axi.ar.addr,
            ),
        )

class AXIRDebug(Module):
    def __init__(self, axi, name=""):
        sync = getattr(self.sync, axi.clock_domain)
        sync += If(axi.r.valid & axi.r.ready,
            Display(f"AXI R {name}: Data: 0x%x",
                axi.r.data,
            ),
        )

# SimSoC -------------------------------------------------------------------------------------------

class SimSoC(SoCCore):
    def __init__(self, firmware=None, loopback_data_debug=False, axil_ethernet_debug=False):
        # Parameters.
        sys_clk_freq = int(100e6)

        # Platform.
        platform = Platform()
        #self.comb += platform.trace.eq(1)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = CRG(platform.request("sys_clk"))

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, uart_name="sim",
            integrated_rom_size      = 0x10000,
            integrated_main_ram_size = 0x10000,
            integrated_main_ram_init = get_mem_data(firmware, endianness="little")
        )
        #self.add_config("BIOS_NO_PROMPT")
        self.add_config("BIOS_NO_DELAYS")
        self.add_constant("ROM_BOOT_ADDRESS", self.bus.regions["main_ram"].origin)

        # AXIL-Ethernet Core generation/integration ------------------------------------------------
        axil_ethernet = AXILiteInterface(data_width=32, address_width=32)

        # Generate Core.
        os.system("cd .. && ./axil_ethernet_gen.py --core_phy=mii --core_ntxslots=2 --core_nrxslots=2 --build")

        # Core Instance.
        class Open(Signal): pass
        self.cd_eth = ClockDomain()
        data        = Signal(4)
        data_en     = Signal()
        self.specials += Instance("axil_ethernet",
            # Clk / Rst.
            # ----------
            i_sys_clock = ClockSignal("sys"),
            i_sys_reset = ResetSignal("sys"),

            # AXI-Lite.
            # ---------
            # AW.
            i_bus_awvalid = axil_ethernet.aw.valid,
            o_bus_awready = axil_ethernet.aw.ready,
            i_bus_awaddr  = axil_ethernet.aw.addr[:28],
            i_bus_awprot  = axil_ethernet.aw.prot,
            # W.
            i_bus_wvalid  = axil_ethernet.w.valid,
            o_bus_wready  = axil_ethernet.w.ready,
            i_bus_wdata   = axil_ethernet.w.data,
            i_bus_wstrb   = axil_ethernet.w.strb,
            # B
            o_bus_bvalid  = axil_ethernet.b.valid,
            i_bus_bready  = axil_ethernet.b.ready,
            o_bus_bresp   = axil_ethernet.b.resp,
            # AR.
            i_bus_arvalid = axil_ethernet.ar.valid,
            o_bus_arready = axil_ethernet.ar.ready,
            i_bus_araddr  = axil_ethernet.ar.addr[:28],
            i_bus_arprot  = axil_ethernet.ar.prot,
            # R.
            o_bus_rvalid  = axil_ethernet.r.valid,
            i_bus_rready  = axil_ethernet.r.ready,
            o_bus_rresp   = axil_ethernet.r.resp,
            o_bus_rdata   = axil_ethernet.r.data,

            # IOs.
            # ----
            i_mii_eth_clocks_tx = self.cd_eth.clk,
            i_mii_eth_clocks_rx = self.cd_eth.clk,
            o_mii_eth_rst_n     = Open(),
            io_mii_eth_mdio     = Open(),
            o_mii_eth_mdc       = Open(),
            i_mii_eth_rx_dv     = data_en,
            i_mii_eth_rx_er     = Open(),
            i_mii_eth_rx_data   = data,
            o_mii_eth_tx_en     = data_en,
            o_mii_eth_tx_data   = data,
            i_mii_eth_col       = 0,
            i_mii_eth_crs       = 0,
        )
        platform.add_source("../src/axil_ethernet.v")
        self.bus.add_slave("axil_ethernet", axil_ethernet, region=SoCRegion(origin=0x3000_0000, size=0x1000_0000))

        # Clk Generation.
        clk_counter = Signal(4)
        self.sync += clk_counter.eq(clk_counter + 1)
        self.comb += self.cd_eth.clk.eq(clk_counter[-1])

        # Debug.
        if loopback_data_debug:
            self.sync.eth += If(data_en,
                Display("data: %02x", data)
            )

        if axil_ethernet_debug:
            self.submodules += AXIAWDebug(axil_ethernet, name="AXIL_ETHERNET")
            self.submodules += AXIWDebug(axil_ethernet,  name="AXIL_ETHERNET")
            self.submodules += AXIARDebug(axil_ethernet, name="AXIL_ETHERNET")
            self.submodules += AXIRDebug(axil_ethernet,  name="AXIL_ETHERNET")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AXIL_ETHERNET  / LiteX simulation.")
    verilator_build_args(parser)
    args = parser.parse_args()
    verilator_build_kwargs = verilator_build_argdict(args)
    sim_config = SimConfig(default_clk="sys_clk")
    sim_config.add_module("serial2console", "serial")

    for n in range(2):
        # Create SoC.
        soc = SimSoC(firmware={
            0 : None,           # First loop with no firmware (to generate SoC's software headers).
            1 : "firmware/firmware.bin" # Second loop with compiled firmware.
        }[n])
        builder = Builder(soc)
        # Build/Run SoC (run only on second loop).
        builder.build(sim_config=sim_config, **verilator_build_kwargs, run=n > 0)

        # Compile firmware on first loop.
        if (n == 0):
            os.system("cd firmware && make clean all")

if __name__ == "__main__":
    main()
