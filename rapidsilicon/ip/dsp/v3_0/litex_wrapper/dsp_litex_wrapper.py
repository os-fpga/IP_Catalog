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
    def __init__(self, a_width, b_width, feature, reg_in, reg_out, unsigned):

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
        
        if (unsigned == True):
            k = 17
        else:
            k = 16
        
        self.a = Signal(bits_sign=(a_width, True))
        self.b = Signal(bits_sign=(b_width, True))

        self.a0 = self.a[0:k]
        if (a_width > k):
            self.a1 = self.a[k:k*2]
        else:
            self.a1 = Replicate(0,20)
        self.b0 = self.b[0:k]
        if (b_width > k):
            self.b1 = self.b[k:k*2]
        else:
            self.b1 = Replicate (0,18)
        
        self.dx = Signal(bits_sign=(18,True))
        self.dy = Signal(bits_sign=(18,True))

        if(not unsigned):
            self.a__1 = Signal(bits_sign=(17, True))
            self.b__1 = Signal(bits_sign=(17, True))
            self.a__0 = Signal(bits_sign=(17, True))
            self.b__0 = Signal(bits_sign=(17, True))

            self.comb += self.a__1.eq(Cat(self.a1, Replicate(self.a[a_width - 1], 1)))
            self.comb += self.b__1.eq(Cat(self.b1, Replicate(self.b[b_width - 1], 1)))
            self.comb += self.a__0.eq(Cat(self.a0, Replicate(0,1)))
            self.comb += self.b__0.eq(Cat(self.b0, Replicate(0,1)))

            self.comb += self.dx.eq(self.a__1 - self.a__0)
            self.comb += self.dy.eq(self.b__1 - self.b__0)
        else:
            self.comb += self.dx.eq(self.a1 - self.a0)
            self.comb += self.dy.eq(self.b1 - self.b0)

        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.z = Signal(a_width + b_width)
        
        self.comb += self.z.eq((self.z3 << 2*k) + self.z1 + ((self.z3 + self.z1 - self.z2) << k))
        # Registered Output
        if (reg_in == 0 and reg_out == 1):            
            # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT_REGOUT",
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
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = Cat(self.dx, Replicate(self.dx[17], 2)),
                i_b             = self.dy,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            if (not unsigned):
                # Module instance.
                # ----------------
                self.specials += Instance("RS_DSP_MULT_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = Cat(self.a1, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b1, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                # Module instance.
                # ----------------
                self.specials += Instance("RS_DSP_MULT_REGOUT",
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
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
        elif (reg_in == 1 and reg_out == 1):
            
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_a             = Cat(self.dx, Replicate(self.dx[17], 2)),
                i_b             = self.dy,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            if(not unsigned):
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
                    i_a             = Cat(self.a1, Replicate(self.a[31], 4)),
                    i_b             = Cat(self.b1, Replicate(self.b[31], 2)),
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
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
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
        # Registered Input
        elif (reg_in == 1 and reg_out == 0):
            
            # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT_REGIN",
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = Cat(self.dx, Replicate(self.dx[17], 2)),
                i_b             = self.dy,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            if(not unsigned):
                # Module instance.
                # ----------------
                self.specials += Instance("RS_DSP_MULT_REGIN",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = Cat(self.a1, Replicate(self.a[31], 4)),
                    i_b             = Cat(self.b1, Replicate(self.b[31], 2)),
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                # Module instance.
                # ----------------
                self.specials += Instance("RS_DSP_MULT_REGIN",
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
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
        else:
            
             # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.a0,
                i_b             = self.b0,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx, Replicate(self.dx[17], 2)),
                i_b             = self.dy,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            if (not unsigned):
                # Module instance.
                # ----------------
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = Cat(self.a1, Replicate(self.a[31], 4)),
                    i_b             = Cat(self.b1, Replicate(self.b[31], 2)),
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                # Module instance.
                # ----------------
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a1,
                    i_b             = self.b1,
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT36(Module):
    def __init__(self, a_width, b_width, feature, reg_in, reg_out, unsigned):

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
        if(unsigned == True):
            k = 17
        else:
            k = 16

        self.a = Signal(bits_sign=(a_width, True))
        self.b = Signal(bits_sign=(b_width, True))
        
        self.a0 = self.a[0:k]
        if (a_width > k):
            self.a1 = self.a[k:k*2]
        else:
            self.a1 = Replicate(0,18)
        if (a_width > k*2):
            self.a2 = self.a[k*2:k*3]
        else:
            self.a2 = Replicate (0,18)
        self.b0 = self.b[0:k]
        if (b_width > k):
            self.b1 = self.b[k:k*2]
        else:
            self.b1 = Replicate (0,18)
        if (b_width > k*2):
            self.b2 = self.b[k*2:k*3]
        else:
            self.b2 = Replicate(0,18)

        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.z4 = Signal(bits_sign=(38,True))
        self.z5 = Signal(bits_sign=(38,True))
        self.z6 = Signal(bits_sign=(38,True))
        
        self.dx1 = Signal(bits_sign=(18,True))
        self.dx2 = Signal(bits_sign=(18,True))
        self.dx3 = Signal(bits_sign=(18,True))
        self.dy1 = Signal(bits_sign=(18,True))
        self.dy2 = Signal(bits_sign=(18,True))
        self.dy3 = Signal(bits_sign=(18,True))

        if (unsigned):
            self.comb += self.dx1.eq(self.a2 - self.a1)
            self.comb += self.dx2.eq(self.a1 - self.a0)
            self.comb += self.dx3.eq(self.a2 - self.a0)

            self.comb += self.dy1.eq(self.b2 - self.b1)
            self.comb += self.dy2.eq(self.b1 - self.b0)
            self.comb += self.dy3.eq(self.b2 - self.b0)
        else:
            self.a__2 = Signal(bits_sign=(17, True))
            self.b__2 = Signal(bits_sign=(17, True))
            self.a__1 = Signal(bits_sign=(17, True))
            self.b__1 = Signal(bits_sign=(17, True))
            self.a__0 = Signal(bits_sign=(17, True))
            self.b__0 = Signal(bits_sign=(17, True))

            self.comb += self.a__2.eq(Cat(self.a2, Replicate(self.a[a_width - 1], 1)))
            self.comb += self.b__2.eq(Cat(self.b2, Replicate(self.b[b_width - 1], 1)))
            self.comb += self.a__1.eq(Cat(self.a1, Replicate(0,1)))
            self.comb += self.b__1.eq(Cat(self.b1, Replicate(0,1)))
            self.comb += self.a__0.eq(Cat(self.a0, Replicate(0,1)))
            self.comb += self.b__0.eq(Cat(self.b0, Replicate(0,1)))

            self.comb += self.dx1.eq(self.a__2 - self.a__1)
            self.comb += self.dx2.eq(self.a__1 - self.a__0)
            self.comb += self.dx3.eq(self.a__2 - self.a__0)

            self.comb += self.dy1.eq(self.b__2 - self.b__1)
            self.comb += self.dy2.eq(self.b__1 - self.b__0)
            self.comb += self.dy3.eq(self.b__2 - self.b__0)

        self.z = Signal(a_width + b_width)


        self.comb += self.z.eq((self.z3 << 4*k) + ((self.z3 + self.z2 - self.z4) << 3*k) + 
        ((self.z3 + self.z2 + self.z1 - self.z6) << 2*k) + ((self.z2 + self.z1 - self.z5) << k) + self.z1)

        # Module instance.
        # ----------------
        if (reg_in == 0 and reg_out == 1):
            self.specials += Instance("RS_DSP_MULT_REGOUT",
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
            self.specials += Instance("RS_DSP_MULT_REGOUT",
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
            if(unsigned == 0):
                self.specials += Instance("RS_DSP_MULT_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = Cat(self.a2, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b2, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                self.specials += Instance("RS_DSP_MULT_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b2,
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_b             = self.dy1,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_b             = self.dy2,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_b             = self.dy3,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
        elif (reg_in == 1 and reg_out == 1):
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
            if(unsigned == 0):
                self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = Cat(self.a2, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b2, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b2,
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                i_a             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_b             = self.dy1,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
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
                i_a             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_b             = self.dy2,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
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
                i_a             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_b             = self.dy3,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
        elif (reg_in == 1 and reg_out == 0):
            self.specials += Instance("RS_DSP_MULT_REGIN",
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
            self.specials += Instance("RS_DSP_MULT_REGIN",
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
            if(unsigned == 0):
                self.specials += Instance("RS_DSP_MULT_REGIN",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = Cat(self.a2, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b2, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                self.specials += Instance("RS_DSP_MULT_REGIN",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b2,
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_b             = self.dy1,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_b             = self.dy2,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_b             = self.dy3,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
        else:
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.a0,
                i_b             = self.b0,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if(unsigned == 0):
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = Cat(self.a2, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b2, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z3,
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b2,
                    o_z             = self.z3,
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits tcdo configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_b             = self.dy1,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_b             = self.dy2,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_b             = self.dy3,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )

# # RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT54(Module):
    def __init__(self, a_width, b_width, feature, reg_in, reg_out, unsigned, ):

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
        
        if(unsigned == True):
            k = 17
        else:
            k = 16

        self.a = Signal(a_width)
        self.b = Signal(b_width)
        
        self.a1 = self.a[0:k]
        if (a_width > k):
            self.a2 = self.a[k:k*2]
        else:
            self.a2 = Replicate(0,18)
        if (a_width > k*2):
            self.a3 = self.a[k*2:k*3]
        else:
            self.a3 = Replicate (0,18)
        if (a_width > k*3):
            self.a4 = self.a[k*3:k*4]
        else:
            self.a4 = Replicate(0,18)
        self.b1 = self.b[0:k]
        if (b_width > k):
            self.b2 = self.b[k:k*2]
        else:
            self.b2 = Replicate (0,18)
        if (b_width > k*2):
            self.b3 = self.b[k*2:k*3]
        else:
            self.b3 = Replicate(0,18)
        if (b_width > k*3):
            self.b4 = self.b[k*3:k*4]
        else:
            self.b4 = Replicate(0,18)

        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.z4 = Signal(bits_sign=(38,True))
        self.z5 = Signal(bits_sign=(38,True))
        self.z6 = Signal(bits_sign=(38,True))
        self.z7 = Signal(bits_sign=(38,True))
        self.z8 = Signal(bits_sign=(38,True))
        self.z9 = Signal(bits_sign=(38,True))
        self.z10 = Signal(bits_sign=(38,True))

        self.dx1 = Signal(bits_sign=(18,True))
        self.dx2 = Signal(bits_sign=(18,True))
        self.dx3 = Signal(bits_sign=(18,True))
        self.dx4 = Signal(bits_sign=(18,True))
        self.dx5 = Signal(bits_sign=(18,True))
        self.dx6 = Signal(bits_sign=(18,True))
        self.dy1 = Signal(bits_sign=(18,True))
        self.dy2 = Signal(bits_sign=(18,True))
        self.dy3 = Signal(bits_sign=(18,True))
        self.dy4 = Signal(bits_sign=(18,True))
        self.dy5 = Signal(bits_sign=(18,True))
        self.dy6 = Signal(bits_sign=(18,True))

        self.z = Signal(a_width + b_width)

        if(unsigned):
            self.comb += self.dx1.eq(self.a2 - self.a1)
            self.comb += self.dx2.eq(self.a3 - self.a1)
            self.comb += self.dx3.eq(self.a4 - self.a1)
            self.comb += self.dx4.eq(self.a3 - self.a2)
            self.comb += self.dx5.eq(self.a4 - self.a2)
            self.comb += self.dx6.eq(self.a4 - self.a3)
            self.comb += self.dy1.eq(self.b2 - self.b1)
            self.comb += self.dy2.eq(self.b3 - self.b1)
            self.comb += self.dy3.eq(self.b4 - self.b1)
            self.comb += self.dy4.eq(self.b3 - self.b2)
            self.comb += self.dy5.eq(self.b4 - self.b2)
            self.comb += self.dy6.eq(self.b4 - self.b3)
        else:
            self.a__1 = Signal(bits_sign=(17, True))
            self.b__1 = Signal(bits_sign=(17, True))
            self.a__2 = Signal(bits_sign=(17, True))
            self.b__2 = Signal(bits_sign=(17, True))
            self.a__3 = Signal(bits_sign=(17, True))
            self.b__3 = Signal(bits_sign=(17, True))
            self.a__4 = Signal(bits_sign=(17, True))
            self.b__4 = Signal(bits_sign=(17, True))

            self.comb += self.a__4.eq(Cat(self.a4, Replicate(self.a[a_width - 1], 1)))
            self.comb += self.b__4.eq(Cat(self.b4, Replicate(self.b[b_width - 1], 1)))
            self.comb += self.a__3.eq(Cat(self.a3, Replicate(0,1)))
            self.comb += self.b__3.eq(Cat(self.b3, Replicate(0,1)))
            self.comb += self.a__2.eq(Cat(self.a2, Replicate(0,1)))
            self.comb += self.b__2.eq(Cat(self.b2, Replicate(0,1)))
            self.comb += self.a__1.eq(Cat(self.a1, Replicate(0,1)))
            self.comb += self.b__1.eq(Cat(self.b1, Replicate(0,1)))

            self.comb += self.dx1.eq(self.a__2 - self.a__1)
            self.comb += self.dx2.eq(self.a__3 - self.a__1)
            self.comb += self.dx3.eq(self.a__4 - self.a__1)
            self.comb += self.dx4.eq(self.a__3 - self.a__2)
            self.comb += self.dx5.eq(self.a__4 - self.a__2)
            self.comb += self.dx6.eq(self.a__4 - self.a__3)
            self.comb += self.dy1.eq(self.b__2 - self.b__1)
            self.comb += self.dy2.eq(self.b__3 - self.b__1)
            self.comb += self.dy3.eq(self.b__4 - self.b__1)
            self.comb += self.dy4.eq(self.b__3 - self.b__2)
            self.comb += self.dy5.eq(self.b__4 - self.b__2)
            self.comb += self.dy6.eq(self.b__4 - self.b__3)

        self.comb += self.z.eq((self.z4 << 6*k) + ((self.z4 + self.z3 - self.z10) << 5*k) + 
        ((self.z4 + self.z3 + self.z2 - self.z9) << 4*k) + ((self.z4 + self.z3 + self.z2 + self.z1 - self.z7 - self.z8) << 3*k) +
        ((self.z3 + self.z2 + self.z1 - self.z6) << 2*k) + ((self.z2 + self.z1 - self.z5) << k) + self.z1)

        # Module instance.
        # ----------------
        if (reg_in == 0 and reg_out == 1):
            self.specials += Instance("RS_DSP_MULT_REGOUT",
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
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a2,
                i_b             = self.b2,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
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
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if(unsigned == 0):
                self.specials += Instance("RS_DSP_MULT_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = Cat(self.a4, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b4, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                self.specials += Instance("RS_DSP_MULT_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx1,
                i_b             = self.dy1,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx2,
                i_b             = self.dy2,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx3,
                i_b             = self.dy3,
                o_z             = self.z7,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx4,
                i_b             = self.dy4,
                o_z             = self.z8,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0 
            )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx5,
                i_b             = self.dy5,
                o_z             = self.z9,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx6,
                i_b             = self.dy6,
                o_z             = self.z10,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
        elif (reg_in == 1 and reg_out == 1):
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
            self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a2,
                i_b             = self.b2,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
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
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if(unsigned == 0):
                self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = Cat(self.a4, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b4, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                self.specials += Instance("RS_DSP_MULT_REGIN_REGOUT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                i_a             = self.dx1,
                i_b             = self.dy1,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
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
                i_a             = self.dx2,
                i_b             = self.dy2,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
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
                i_a             = self.dx3,
                i_b             = self.dy3,
                o_z             = self.z7,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
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
                i_a             = self.dx4,
                i_b             = self.dy4,
                o_z             = self.z8,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
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
                i_a             = self.dx5,
                i_b             = self.dy5,
                o_z             = self.z9,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
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
                i_a             = self.dx6,
                i_b             = self.dy6,
                o_z             = self.z10,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
        elif (reg_in == 1 and reg_out == 0):
            self.specials += Instance("RS_DSP_MULT_REGIN",
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
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.a2,
                i_b             = self.b2,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
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
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if(unsigned == 0):
                self.specials += Instance("RS_DSP_MULT_REGIN",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = Cat(self.a4, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b4, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                self.specials += Instance("RS_DSP_MULT_REGIN",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # Reset
                    i_clk           = ClockSignal(),
                    i_lreset        = ResetSignal(),
                    # IOs
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx1,
                i_b             = self.dy1,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx2,
                i_b             = self.dy2,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx3,
                i_b             = self.dy3,
                o_z             = self.z7,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx4,
                i_b             = self.dy4,
                o_z             = self.z8,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx5,
                i_b             = self.dy5,
                o_z             = self.z9,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT_REGIN",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),
                # IOs
                i_a             = self.dx6,
                i_b             = self.dy6,
                o_z             = self.z10,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
        else:
            self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a1,
                    i_b             = self.b1,
                    o_z             = self.z1,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.a2,
                i_b             = self.b2,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.a3,
                i_b             = self.b3,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if(unsigned == 0):
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = Cat(self.a4, Replicate(self.a[a_width - 1], 4)),
                    i_b             = Cat(self.b4, Replicate(self.b[b_width - 1], 2)),
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 0
                )
            else:
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_b             = self.dy1,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_b             = self.dy2,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_b             = self.dy3,
                o_z             = self.z7,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx4, Replicate(self.dx4[17], 2)),
                i_b             = self.dy4,
                o_z             = self.z8,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx5, Replicate(self.dx5[17], 2)),
                i_b             = self.dy5,
                o_z             = self.z9,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = Cat(self.dx6, Replicate(self.dx6[17], 2)),
                i_b             = self.dy6,
                o_z             = self.z10,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )

