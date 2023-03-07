#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import logging
import math

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)


# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT20(Module):
    def __init__(self, a_width, b_width, feature, unsigned ):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"FEATURE  : {feature}")
        
        if(unsigned == 1):
            k = 18
        else:
            k = 17
        
        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))
        self.sum = Signal(3, reset=2)
        self.fb = Signal(3)
        
        self.comb += self.fb.eq(Mux(self.sum != 2, 0b001, 0b000))

        self.a0 = self.a[0:k]
        if (a_width > k):
            if (unsigned == 1):
                self.a1 = self.a[k:k*2]
            else:
                self.a1 = Cat(self.a[k:k*2], Replicate(self.a[(a_width)-1], 3))
        else:
            self.a1 = Replicate(0,18)
        self.b0 = self.b[0:k]
        if (b_width > k):
            if (unsigned == 1):
                self.b1 = self.b[k:k*2]
            else:
                self.b3 = Cat(self.b[k:k*2], Replicate(self.b[(b_width)-1], 1))
        else:
            self.b1 = Replicate (0,18)
        
        self.a3 = Signal(bits_sign=(19,True))
        self.b3 = Signal(bits_sign=(19,True))
        self.comb += self.a3.eq(Mux(self.sum != 2, self.a0, self.a1))
        self.comb += self.b3.eq(Mux(self.sum != 2, self.b1, self.b0))
        if (unsigned == 0):
            self.unsigneda = Signal(1)
            self.unsignedb = Signal(1)
            self.comb += self.unsigneda.eq(Mux(self.sum != 2, 1, 0))
            self.comb += self.unsignedb.eq(Mux(self.sum != 2, 0, 1))

        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.result = Signal (38)
        self.z = Signal(a_width + b_width)
        self.z_2 = Signal(a_width + b_width)
        self.comb += self.z.eq(Mux(self.sum == 3, (self.z3 << k) + self.z1 + (self.z2 << 2*k), self.z_2))
        sum_reg = Signal(3, reset=1)
        self.sync += [
            sum_reg.eq(sum_reg + 1),
            If(sum_reg == 3,
                sum_reg.eq(2)
            )
        ]
        self.comb += [
            self.sum.eq(sum_reg),
            self.z_2.eq(self.z)
        ]
         # Module instance.
        # ----------------
        self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_MODE_BITS     =  0,
            # Reset
            i_clk           = ClockSignal(),
            i_lreset        = ResetSignal(),
            # IOs
            i_a             = self.a0,
            i_b             = self.b0,
            o_z             = self.z1,  
            i_feedback      = 0,
            i_unsigned_a    = 1,
            i_unsigned_b    = 1
        )
        if(unsigned == 0):
            self.specials += Instance("RS_DSP_MULTACC",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_MODE_BITS     =  0,
            # Reset
            i_clk           = ClockSignal(),
            i_lreset        = ResetSignal(),
            # IOs
            i_a             = self.a3,
            i_b             = self.b3,
            o_z             = self.z3,  
            i_feedback      = self.fb,
            i_load_acc      = 1,
            i_round         = 0,
            i_saturate_enable = 0,
            i_shift_right   = 0,
            i_unsigned_a    = self.unsigneda,
            i_unsigned_b    = self.unsignedb,
            i_subtract      = 0
            )
        
            # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
        else:
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a3,
                i_b             = self.b3,
                o_z             = self.z3,  
                i_feedback      = self.fb,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
                i_subtract      = 0
            )

            # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT36(Module):
    def __init__(self, a_width, b_width, feature,unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"FEATURE  : {feature}")
        
        if (unsigned == False):
            k = 17
        else:
            k = 18

        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))

        self.a1 = Signal(k)
        self.b1 = Signal(k)
        self.a2 = Signal(k)
        self.b2 = Signal(k)
        self.a3 = Signal(k)
        self.b3 = Signal(k)

        self.sum = Signal(3, reset=2)
        self.fb = Signal(3, reset = 1)
        self.fb_del = Signal(3)
        
        self.a1 = self.a[0:k]
        if (a_width > k):
            self.a2 = self.a[k:k*2]
        else:
            self.a2 = Replicate(0,18)
        if (a_width > k*2):
            if(unsigned == 1):
                self.a3 = self.a[k*2:k*3]
            else:
                self.a3 = Cat(self.a[k*2:k*3], Replicate(self.a[(a_width)-1], 3))
        else:
            self.a3 = Replicate (0,18)
        self.b1 = self.b[0:k]
        if (b_width > k):
            self.b2 = self.b[k:k*2]
        else:
            self.b2 = Replicate (0,18)
        if (b_width > k*3):
            if (unsigned == 1):
                self.b3 = self.b[k*2:k*3]
            else:
                self.b3 = Cat(self.b[k*2:k*3], Replicate(self.b[(b_width)-1], 1))
        else:
            self.b3 = Replicate(0,18)

        if (unsigned == 0):
            self.z1 = Signal(bits_sign=(38,True))
            self.z2 = Signal(bits_sign=(38,True))
            self.z3 = Signal(bits_sign=(38,True))
            self.z4 = Signal(bits_sign=(38,True))
            self.z5 = Signal(bits_sign=(38,True))
        else:
            self.z1 = Signal(38)
            self.z2 = Signal(38)
            self.z3 = Signal(38)
            self.z4 = Signal(38)
            self.z5 = Signal(38)
        
        self.a_2 = Signal(bits_sign=(k+1,True))
        self.comb += self.a_2.eq(Mux(self.sum == 3, self.a1, self.a2))
        self.b_2 = Signal(bits_sign=(k+1,True))
        self.comb += self.b_2.eq(Mux(self.sum == 3, self.b2, self.b1))
        self.a_4 = Signal(bits_sign=(k+1,True))
        self.comb += self.a_4.eq(Mux(self.sum == 3, self.a2, self.a3))
        self.b_4 = Signal(bits_sign=(k+1,True))
        self.comb += self.b_4.eq(Mux(self.sum == 3, self.b3, self.b2))
        self.comb += self.fb_del.eq(Mux(self.sum != 3, 1, 0))
        self.a_3 = Signal(bits_sign=(k+1,True))
        self.b_3 = Signal(bits_sign=(k+1,True))

        if (unsigned == 0):
            self.unsigneda_3 = Signal(1, reset = 1)
            self.unsignedb_3 = Signal(1, reset = 1)

            self.unsigneda_4 = Signal(1, reset = 1)
            self.unsignedb_4 = Signal(1, reset = 1)
            self.comb += self.unsigneda_4.eq(Mux(self.sum == 3, 1, 0))
            self.comb += self.unsignedb_4.eq(Mux(self.sum == 3, 0, 1))
        if (unsigned == 1):
            self.comb += [
                If(self.sum == 4,
                    self.fb.eq(1)
                ).Elif(self.sum == 1,
                    self.fb.eq(1)
                ).Else(
                    self.fb.eq(0)
                ),
                If(self.sum < 2,
                    self.a_3.eq(self.a1),
                    self.b_3.eq(self.b3),
                ).Elif(self.sum == 4,
                    self.a_3.eq(self.a1),
                    self.b_3.eq(self.b3),
                ).Elif(self.sum == 2,
                    self.a_3.eq(self.a2),
                    self.b_3.eq(self.b2),
                ).Else(
                    self.a_3.eq(self.a3),
                    self.b_3.eq(self.b1),
                )
            ]
        else:
            self.comb += [
                If(self.sum == 4,
                    self.fb.eq(1)
                ).Elif(self.sum == 1,
                    self.fb.eq(1)
                ).Else(
                    self.fb.eq(0)
                ),
                If(self.sum < 2,
                    self.a_3.eq(self.a1),
                    self.unsigneda_3.eq(1),
                    self.b_3.eq(self.b3),
                    self.unsignedb_3.eq(0),
                ).Elif(self.sum == 4,
                    self.a_3.eq(self.a1),
                    self.unsigneda_3.eq(1),
                    self.b_3.eq(self.b3),
                    self.unsignedb_3.eq(0),
                ).Elif(self.sum == 2,
                    self.a_3.eq(self.a2),
                    self.unsigneda_3.eq(1),
                    self.b_3.eq(self.b2),
                    self.unsignedb_3.eq(1),
                ).Else(
                    self.a_3.eq(self.a3),
                    self.unsigneda_3.eq(0),
                    self.b_3.eq(self.b1),
                    self.unsignedb_3.eq(1),
                )
            ]


        self.z = Signal(a_width + b_width)
        if (unsigned == 1):
            self.z_2 = Signal(a_width + b_width)
        else:
            self.z_2 = Signal(bits_sign=(a_width + b_width,True))
        self.comb += self.z.eq(Mux(self.sum == 4,(self.z5 << 4*k) + (self.z4 << 3*k)  + (self.z3 << 2*k)
                                                + (self.z2 << k) + self.z1, self.z_2))
        sum_reg = Signal(3, reset=1)
        self.sync += [
            sum_reg.eq(sum_reg + 1),
            If(sum_reg == 4,
                sum_reg.eq(2)
            )
        ]
        self.comb += [
            self.sum.eq(sum_reg),
            self.z_2.eq(self.z)
        ]

        # Module instance.
        # ----------------
        self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_MODE_BITS     =  0,
            # Reset
            i_clk           = ClockSignal(),
            i_lreset        = ResetSignal(),
            # IOs
            i_a             = self.a1,
            i_b             = self.b1,
            o_z             = self.z1,  
            i_feedback      = 0,
            i_unsigned_a    = 1,
            i_unsigned_b    = 1
        )
        self.specials += Instance("RS_DSP_MULTACC",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_MODE_BITS     =  0,
            # Reset
            i_clk           = ClockSignal(),
            i_lreset        = ResetSignal(),
            # IOs
            i_a             = self.a_2,
            i_b             = self.b_2,
            o_z             = self.z2,  
            i_feedback      = self.fb_del,
            i_load_acc      = 1,
            i_round         = 0,
            i_saturate_enable = 0,
            i_shift_right   = 0,
            i_unsigned_a    = 1,
            i_unsigned_b    = 1,
            i_subtract      = 0
        )
        if (unsigned == 0):
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_3,
                i_b             = self.b_3,
                o_z             = self.z3,  
                i_feedback      = self.fb,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = self.unsigneda_3,
                i_unsigned_b    = self.unsignedb_3,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_4,
                i_b             = self.b_4,
                o_z             = self.z4,  
                i_feedback      = self.fb_del,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = self.unsigneda_4,
                i_unsigned_b    = self.unsignedb_4,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a3,
                i_b             = self.b3,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
        else:
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_3,
                i_b             = self.b_3,
                o_z             = self.z3,  
                i_feedback      = self.fb,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_4,
                i_b             = self.b_4,
                o_z             = self.z4,  
                i_feedback      = self.fb_del,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a3,
                i_b             = self.b3,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT54(Module):
    def __init__(self, a_width, b_width, feature, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"FEATURE  : {feature}")
        
        if(unsigned == False):
            k = 17
        else:
            k = 18

        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))
        
        self.sum = Signal(3, reset=2)
        self.fb = Signal(3, reset = 1)
        self.fb1 = Signal(3)
        self.fb2 = Signal(3)
        self.comb += self.fb2.eq(Mux(self.sum != 4, 1, 0))

        self.a0 = self.a[0:k]
        if (a_width > k):
            self.a1 = self.a[k:k*2]
        else:
            self.a1 = Replicate(0,18)
        if (a_width > k*2):
            self.a2 = self.a[k*2:k*3]
        else:
            self.a2 = Replicate (0,18)
        if (a_width > k*3):
            if (unsigned == 1):
                self.a3 = self.a[k*3:k*4]
            else:
                self.a3 = Cat(self.a[k*3:k*4], Replicate(self.a[(a_width)-1], 3))
        else:
            self.a3 = Replicate(0,18)
        self.b0 = self.b[0:k]
        if (b_width > k):
            self.b1 = self.b[k:k*2]
        else:
            self.b1 = Replicate (0,18)
        if (b_width > k*2):
            self.b2 = self.b[k*2:k*3]
        else:
            self.b2 = Replicate(0,18)
        if (b_width > k*3):
            if (unsigned == 1):
                self.b3 = self.b[k*3:k*4]
            else:
                self.b3 = Cat(self.b[k*3:k*4], Replicate(self.b[(b_width)-1], 1))
        else:
            self.b3 = Replicate(0,18)

        if (unsigned == 1):
            self.z1 = Signal(38)
            self.z2 = Signal(38)
            self.z3 = Signal(38)
            self.z4 = Signal(38)
            self.z5 = Signal(38)
            self.z6 = Signal(38)
            self.z7 = Signal(38)
        else:
            self.z1 = Signal(bits_sign=(38,True))
            self.z2 = Signal(bits_sign=(38,True))
            self.z3 = Signal(bits_sign=(38,True))
            self.z4 = Signal(bits_sign=(38,True))
            self.z5 = Signal(bits_sign=(38,True))
            self.z6 = Signal(bits_sign=(38,True))
            self.z7 = Signal(bits_sign=(38,True))

        self.a_2 = Signal(bits_sign=(k+1,True))
        self.comb += self.a_2.eq(Mux(self.sum < 4, self.a1, self.a0))
        self.b_2 = Signal(bits_sign=(k+1,True))
        self.comb += self.b_2.eq(Mux(self.sum < 4, self.b0, self.b1))
        self.a_6 = Signal(bits_sign=(k+1,True))
        self.comb += self.a_6.eq(Mux(self.sum < 4, self.a2, self.a3))
        self.b_6 = Signal(bits_sign=(k+1,True))
        if(unsigned == 0):
            self.unsigned_a4 = Signal(1, reset = 1)
            self.unsigned_a5 = Signal(1, reset = 1)
            self.unsigned_b4 = Signal(1, reset = 1)
            self.unsigned_b5 = Signal(1, reset = 1)
            self.unsigned_a6 = Signal(1, reset = 1)
            self.comb += self.unsigned_a6.eq(Mux(self.sum < 4, 1, 0))
            self.unsigned_b6 = Signal(1, reset = 1)
            self.comb += self.unsigned_b6.eq(Mux(self.sum < 4, 0, 1))
        self.comb += self.b_6.eq(Mux(self.sum < 4, self.b3, self.b2))
        self.a_3 = Signal(bits_sign=(k+1,True))
        self.b_3 = Signal(bits_sign=(k+1,True))
        self.a_4 = Signal(bits_sign=(k+1,True))
        self.b_4 = Signal(bits_sign=(k+1,True))
        self.a_5 = Signal(bits_sign=(k+1,True))
        self.b_5 = Signal(bits_sign=(k+1,True))
        if (unsigned == 1):
            self.comb += [
                If(self.sum == 5,
                    self.fb.eq(1)
                ).Elif(self.sum == 1,
                    self.fb.eq(1)
                ).Else(
                    self.fb.eq(0)
                ),If(self.sum != 3,
                    If(self.sum != 4,
                        self.fb1.eq(1))
                ).Else(
                    self.fb1.eq(0)
                ),If(self.sum < 3,
                    self.a_3.eq(self.a0),
                    self.b_3.eq(self.b2),
                    self.a_5.eq(self.a1),
                    self.b_5.eq(self.b3)
                ).Elif(self.sum == 3,
                    self.a_3.eq(self.a1),
                    self.b_3.eq(self.b1),
                    self.a_5.eq(self.a2),
                    self.b_5.eq(self.b2)
                ).Else(
                    self.a_3.eq(self.a2),
                    self.b_3.eq(self.b0),
                    self.a_5.eq(self.a3),
                    self.b_5.eq(self.b1)
                ),If(self.sum < 2,
                    self.a_4.eq(self.a0),
                    self.b_4.eq(self.b3)
                ).Elif(self.sum == 5,
                    self.a_4.eq(self.a0),
                    self.b_4.eq(self.b3)
                ).Elif(self.sum == 2,
                    self.a_4.eq(self.a1),
                    self.b_4.eq(self.b2)
                ).Elif(self.sum == 3,
                    self.a_4.eq(self.a2),
                    self.b_4.eq(self.b1)
                ).Else(
                    self.a_4.eq(self.a3),
                    self.b_4.eq(self.b0)
                )
            ]
        else:
            self.comb += [
                If(self.sum == 5,
                    self.fb.eq(1)
                ).Elif(self.sum == 1,
                    self.fb.eq(1)
                ).Else(
                    self.fb.eq(0)
                ),If(self.sum != 3,
                    If(self.sum != 4,
                        self.fb1.eq(1))
                ).Else(
                    self.fb1.eq(0)
                ),If(self.sum < 3,
                    self.a_3.eq(self.a0),
                    self.b_3.eq(self.b2),
                    self.a_5.eq(self.a1),
                    self.b_5.eq(self.b3),
                    self.unsigned_b5.eq(0),
                    self.unsigned_a5.eq(1)
                ).Elif(self.sum == 3,
                    self.a_3.eq(self.a1),
                    self.b_3.eq(self.b1),
                    self.a_5.eq(self.a2),
                    self.b_5.eq(self.b2),
                    self.unsigned_b5.eq(1),
                    self.unsigned_a5.eq(1)
                ).Else(
                    self.a_3.eq(self.a2),
                    self.b_3.eq(self.b0),
                    self.a_5.eq(self.a3),
                    self.b_5.eq(self.b1),
                    self.unsigned_b5.eq(1),
                    self.unsigned_a5.eq(0)
                ),If(self.sum < 2,
                    self.a_4.eq(self.a0),
                    self.b_4.eq(self.b3),
                    self.unsigned_a4.eq(1),
                    self.unsigned_b4.eq(0)
                ).Elif(self.sum == 5,
                    self.a_4.eq(self.a0),
                    self.b_4.eq(self.b3),
                    self.unsigned_a4.eq(1),
                    self.unsigned_b4.eq(0)
                ).Elif(self.sum == 2,
                    self.a_4.eq(self.a1),
                    self.b_4.eq(self.b2),
                    self.unsigned_a4.eq(1),
                    self.unsigned_b4.eq(1)
                ).Elif(self.sum == 3,
                    self.a_4.eq(self.a2),
                    self.b_4.eq(self.b1),
                    self.unsigned_a4.eq(1),
                    self.unsigned_b4.eq(1)
                ).Else(
                    self.a_4.eq(self.a3),
                    self.b_4.eq(self.b0),
                    self.unsigned_a4.eq(0),
                    self.unsigned_b4.eq(1)
                )
            ]

        self.z = Signal(a_width + b_width)
        if (unsigned == 1):
            self.z_2 = Signal(a_width + b_width)
        else:
            self.z_2 = Signal(bits_sign=(a_width + b_width,True))

        self.comb += self.z.eq(Mux(self.sum == 5, (self.z7 << 6*k) + (self.z6 << 5*k) + (self.z5 << 4*k) + 
                    (self.z4 << 3*k) + (self.z3 << 2*k) + (self.z2 << k) + self.z1, self.z_2))
        sum_reg = Signal(3, reset=1)
        self.sync += [
            sum_reg.eq(sum_reg + 1),
            If(sum_reg == 5,
                sum_reg.eq(2)
            )
        ]
        self.comb += [
            self.sum.eq(sum_reg),
            self.z_2.eq(self.z)
        ]
        # Module instance.
        # ----------------
        self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_MODE_BITS     =  0,
            # Reset
            i_clk           = ClockSignal(),
            i_lreset        = ResetSignal(),
            # IOs
            i_a             = self.a0,
            i_b             = self.b0,
            o_z             = self.z1,  
            i_feedback      = 0,
            i_unsigned_a    = 1,
            i_unsigned_b    = 1
        )
        self.specials += Instance("RS_DSP_MULTACC",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_MODE_BITS     =  0,
            # Reset
            i_clk           = ClockSignal(),
            i_lreset        = ResetSignal(),
            # IOs
            i_a             = self.a_2,
            i_b             = self.b_2,
            o_z             = self.z2,  
            i_feedback      = self.fb2,
            i_load_acc      = 1,
            i_round         = 0,
            i_saturate_enable = 0,
            i_shift_right   = 0,
            i_unsigned_a    = 1,
            i_unsigned_b    = 1,
            i_subtract      = 0
        )
        self.specials += Instance("RS_DSP_MULTACC",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_MODE_BITS     =  0,
            # Reset
            i_clk           = ClockSignal(),
            i_lreset        = ResetSignal(),
            # IOs
            i_a             = self.a_3,
            i_b             = self.b_3,
            o_z             = self.z3,  
            i_feedback      = self.fb1,
            i_load_acc      = 1,
            i_round         = 0,
            i_saturate_enable = 0,
            i_shift_right   = 0,
            i_unsigned_a    = 1,
            i_unsigned_b    = 1,
            i_subtract      = 0
        )
        if (unsigned == 0):
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_4,
                i_b             = self.b_4,
                o_z             = self.z4,  
                i_feedback      = self.fb,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = self.unsigned_a4,
                i_unsigned_b    = self.unsigned_b4,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_5,
                i_b             = self.b_5,
                o_z             = self.z5,  
                i_feedback      = self.fb1,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = self.unsigned_a5,
                i_unsigned_b    = self.unsigned_b5,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_6,
                i_b             = self.b_6,
                o_z             = self.z6,  
                i_feedback      = self.fb2,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = self.unsigned_a6,
                i_unsigned_b    = self.unsigned_b6,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a3,
                i_b             = self.b3,
                o_z             = self.z7,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
        else:
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_4,
                i_b             = self.b_4,
                o_z             = self.z4,  
                i_feedback      = self.fb,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_5,
                i_b             = self.b_5,
                o_z             = self.z5,  
                i_feedback      = self.fb1,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULTACC",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a_6,
                i_b             = self.b_6,
                o_z             = self.z6,  
                i_feedback      = self.fb2,
                i_load_acc      = 1,
                i_round         = 0,
                i_saturate_enable = 0,
                i_shift_right   = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
                i_subtract      = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a3,
                i_b             = self.b3,
                o_z             = self.z7,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )

