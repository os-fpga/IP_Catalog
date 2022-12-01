#!/usr/bin/env python3

import sys
import logging

from migen import *

from litex.gen import *

# Helpers ------------------------------------------------------------------------------------------

class Open(Signal): pass

def colorer(s, color="bright"):
    header  = {
        "bright": "\x1b[1m",
        "green":  "\x1b[32m",
        "cyan":   "\x1b[36m",
        "red":    "\x1b[31m",
        "yellow": "\x1b[33m",
        "underline": "\x1b[4m"}[color]
    trailer = "\x1b[0m"
    return header + str(s) + trailer

# DSP Error ----------------------------------------------------------------------------------------

class DSPError(Exception):
    def __init__(self):
        sys.stderr = None # Error already described, avoid traceback/exception.

# RS DSP Primitive ---------------------------------------------------------------------------------

class _RS_DSP(LiteXModule):
    def __init__(self,
        coeff_0        = 0b0000_0000_0000_0000_0000,
        coeff_1        = 0b0000_0000_0000_0000_0000,
        coeff_2        = 0b0000_0000_0000_0000_0000,
        coeff_3        = 0b0000_0000_0000_0000_0000,
        output_select  = 0b000,
        register_input = 0b0,
    ):
        # Clk/Rst.
        self.clock           = Signal()
        self.reset           = Signal()

        # Control.
        self.feedback        = Signal(3)
        self.load_acc        = Signal()
        self.unsigned_a      = Signal()
        self.unsigned_b      = Signal()

        self.saturate_enable = Signal()
        self.shift_right     = Signal(6)
        self.round           = Signal()
        self.subtract        = Signal()

        # Datapath.
        self.a               = Signal(20)
        self.b               = Signal(18)
        self.acc_fir         = Signal(6)
        self.z               = Signal(38)
        self.dly_b           = Signal(18)

        # # #

        self.specials += Instance("dsp_t1_20x18x64_cfg_ports",
            # Parameters.
            p_COEFF_0         = coeff_0,
            p_COEFF_1         = coeff_1,
            p_COEFF_2         = coeff_2,
            p_COEFF_3         = coeff_3,
            p_OUTPUT_SELECT   = output_select,
            p_REGISTER_INPUTS = register_input,

            # Clk/Rst.
            i_clock_i           = self.clock,
            i_reset_i           = self.reset,

            # Datapath.
            i_a_i               = self.a,
            i_b_i               = self.b,
            i_acc_fir_i         = self.acc_fir,
            o_z_o               = self.z,
            o_dly_b_o           = self.dly_b,

            # Control.
            i_feedback_i        = self.feedback,
            i_load_acc_i        = self.load_acc,
            i_unsigned_a_i      = self.unsigned_a,
            i_unsigned_b_i      = self.unsigned_b,

            # Others.
            i_saturate_enable_i = self.saturate_enable,
            i_shift_right_i     = self.shift_right,
            i_round_i           = self.round,
            i_subtract_i        = self.subtract,
        )

# RS DSP Constants ---------------------------------------------------------------------------------

# List of pre-defined RS_DSP configs.

_RS_DSP_CONFIGS = {
    "RS_DSP_MULT",
    "RS_DSP_MULT_REGIN",
    "RS_DSP_MULT_REGOUT",
    "RS_DSP_MULT_REGIN_REGOUT",
    "RS_DSP_MULTACC",
    "RS_DSP_MULTACC_REGIN",
    "RS_DSP_MULTACC_REGOUT",
    "RS_DSP_MULTACC_REGIN_REGOUT",
    "RS_DSP_MULTADD",
    "RS_DSP_MULTADD_REGIN",
    "RS_DSP_MULTADD_REGOUT",
    "RS_DSP_MULTADD_REGIN_REGOUT",
}

# Multiplier A input selection mux; based on feedback control signal.

_RS_DSP_MULT_A_INPUT = {
    0 : "A",
    1 : "A",
    2 : "A",
    3 : "ACC_ADD",
    4 : "COEFF_0",
    5 : "COEFF_1",
    6 : "COEFF_2",
    7 : "COEFF_3",
}

# Accumulator/Adder input selection mux; based on feedback control signal.

_RS_DSP_ACC_ADD_INPUT = {
    0 : "ZERO",
    1 : "A_SHIFT_ACC_FIR",
    2 : "A_SHIFT_ACC_FIR",
    3 : "A_SHIFT_ACC_FIR",
    4 : "A_SHIFT_ACC_FIR",
    5 : "A_SHIFT_ACC_FIR",
    6 : "A_SHIFT_ACC_FIR",
    7 : "A_SHIFT_ACC_FIR",
}

# DSP Output selection mux; based on output_select control signal.

# COMB : Combinatorial.
# REG  : Registered.
# SRS  : Shifted, Rounded and Saturated.

_RS_DSP_OUTPUT = {
    "A_X_B_COMB"      : 0,
    "ACC_OUT_SRS"     : 1,
    "ACC_IN_SRS"      : 2,
    "ACC_IN_SRS"      : 3,
    "A_X_B_REG"       : 4,
    "ACC_OUT_SRS_REG" : 5,
    "ACC_IN_SRS_REG"  : 6,
    "ACC_IN_SRS_REG"  : 7,
}

# RS_DSP -------------------------------------------------------------------------------------------

class RS_DSP(_RS_DSP):
    def __init__(self, config, a_width, b_width, z_width,
        coeff_0 = 0b0000_0000_0000_0000_0000,
        coeff_1 = 0b0000_0000_0000_0000_0000,
        coeff_2 = 0b0000_0000_0000_0000_0000,
        coeff_3 = 0b0000_0000_0000_0000_0000,
    ):
        self.logger = logging.getLogger("RS_DSP")

        # Check Parameters.
        # -----------------

        # Config.
        if config in _RS_DSP_CONFIGS:
            self.logger.info(f"Creating {colorer(config)}...")
        else:
            msg = f"{colorer(config)} is not a valid config, supported:\n"
            for config in sorted(_RS_DSP_CONFIGS):
                msg += f"-{config}\n"
            self.logger.error(msg)
            raise DSPError()

        # A Width.
        if a_width in range(1, 20 + 1):
            self.logger.info(colorer(f" A:{a_width}-bit"))
        else:
            msg = f"{colorer('A')} width of {colorer(f'{a_width}-bit')} is not valid, should be in {colorer('1..20')}."
            self.logger.error(msg)
            raise DSPError()

        # B Width.
        if b_width in range(1, 18 + 1):
            self.logger.info(colorer(f" B:{b_width}-bit"))
        else:
            msg = f" {colorer('B')} width of {colorer(f'{b_width}-bit')} is not valid, should be in {colorer('1..18')}."
            self.logger.error(msg)
            raise DSPError()

        # Z Width.
        if z_width in range(1, 38 + 1):
            self.logger.info(colorer(f" Z:{z_width}-bit"))
        else:
            msg = f" {colorer('Z')} width of {colorer(f'{z_width}-bit')} is not valid, should be in {colorer('1..38')}."
            self.logger.error(msg)
            raise DSPError()

        # Coeffs.
        for i, coeff in enumerate([coeff_0, coeff_1, coeff_2, coeff_3]):
            if coeff <= (2**20-1):
                self.logger.info(colorer(f" COEFF_{i}:0b{coeff:020b}"))
            else:
                msg = f" {colorer(f'COEFF_{i}')} not in range, should be in {colorer('0..2^20-1')}."
                self.logger.error(msg)
                raise DSPError()

        # Configure DSP.
        # --------------

        # MULT Configs.
        if config in [
            "RS_DSP_MULT",
            "RS_DSP_MULT_REGIN",
            "RS_DSP_MULT_REGOUT",
            "RS_DSP_MULT_REGIN_REGOUT",
        ]:
            regin         = "REGIN"  in config
            regout        = "REGOUT" in config
            output_select = {
                False : _RS_DSP_OUTPUT["A_X_B_COMB"],
                True  : _RS_DSP_OUTPUT["A_X_B_REG"],
            }[regout]
            _RS_DSP.__init__(self, output_select=output_select, register_input=0)
            self.comb += self.feedback.eq(1)

        # MULTACC Configs.
        if config in [
            "RS_DSP_MULTACC",
            "RS_DSP_MULTACC_REGIN",
            "RS_DSP_MULTACC_REGOUT",
            "RS_DSP_MULTACC_REGIN_REGOUT",
        ]:
            raise NotImplementedError

        # MULTADD Configs.
        if config in [
            "RS_DSP_MULTADD",
            "RS_DSP_MULTADD_REGIN",
            "RS_DSP_MULTADD_REGOUT",
            "RS_DSP_MULTADD_REGIN_REGOUT",
        ]:
            raise NotImplementedError

# Self-Test ----------------------------------------------------------------------------------------

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    dsp = RS_DSP(config="RS_DSP_MULT", a_width=20, b_width=16, z_width=38,
        coeff_0=2**20-1,
        coeff_1=2**20-1,
        coeff_2=2**20-1,
        coeff_3=2**20-1,
    )
