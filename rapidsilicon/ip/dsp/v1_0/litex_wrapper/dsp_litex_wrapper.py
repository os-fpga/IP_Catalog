#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT(Module):
    def __init__(self, a_width, b_width, feature, reg_in, reg_out):

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

        self.a = Signal(a_width)
        self.b = Signal(b_width)
        self.z = Signal(38)
        
        if (reg_in == 1 and reg_out == 0):
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
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
        elif (reg_in == 0 and reg_out == 1):
            # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT_REGOUT",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP l
                p_MODE_BITS     =  0,
                
                # Reset
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),

                # IOs
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT_ABCD(Module):
    def __init__(self, a_width, b_width, c_width, d_width, feature, reg_in, reg_out):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")
        
        # Input C.
        self.logger.info(f"INPUT_C  : {c_width}")
        
        # Input D.
        self.logger.info(f"INPUT_D  : {d_width}")

        # Equation.
        self.logger.info(f"FEATURE  : {feature}")

        self.a  = Signal(a_width)
        self.b  = Signal(b_width)
        self.c  = Signal(c_width)
        self.d  = Signal(d_width)
        self.z1 = Signal(38)
        self.z2 = Signal(38)
        self.z  = Signal(38+1)
        self.comb += self.z.eq(self.z1 + self.z2)
        
        if (reg_in == 1 and reg_out == 0):
            # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT_REGIN",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                
                # Reset
                i_clk               = ClockSignal(),
                i_lreset            = ResetSignal(),

                # IOs
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )

            self.specials += Instance("RS_DSP_MULT_REGIN",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                
                # Reset
                i_clk               = ClockSignal(),
                i_lreset            = ResetSignal(),

                # IOs
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
        elif (reg_in == 0 and reg_out == 1):
            # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT_REGOUT",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                
                # Reset
                i_clk               = ClockSignal(),
                i_lreset            = ResetSignal(),

                # IOs
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )

            self.specials += Instance("RS_DSP_MULT_REGOUT",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                
                # Reset
                i_clk               = ClockSignal(),
                i_lreset            = ResetSignal(),

                # IOs
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )

            self.specials += Instance("RS_DSP_MULT",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,

                # IOs
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT_ABCDEFGH(Module):
    def __init__(self, a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, feature, reg_in, reg_out):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")
        
        # Input C.
        self.logger.info(f"INPUT_C  : {c_width}")
        
        # Input D.
        self.logger.info(f"INPUT_D  : {d_width}")
        
        # Input E.
        self.logger.info(f"INPUT_E  : {e_width}")
        
        # Input F.
        self.logger.info(f"INPUT_F  : {f_width}")
        
        # Input G.
        self.logger.info(f"INPUT_G  : {g_width}")
        
        # Input H.
        self.logger.info(f"INPUT_H  : {h_width}")

        # Equation.
        self.logger.info(f"FEATURE  : {feature}")

        self.a  = Signal(a_width)
        self.b  = Signal(b_width)
        self.c  = Signal(c_width)
        self.d  = Signal(d_width)
        
        self.e  = Signal(e_width)
        self.f  = Signal(f_width)
        self.g  = Signal(g_width)
        self.h  = Signal(h_width)
        
        self.z1 = Signal(38)
        self.z2 = Signal(38)
        self.z3 = Signal(38)
        self.z4 = Signal(38)
        
        self.z12 = Signal(38+1)
        self.z34 = Signal(38+1)
        self.z  = Signal(39+1)
        
        if (reg_in == 1 and reg_out == 0):
            
            self.comb += self.z12.eq(self.z1 + self.z2)
            self.comb += self.z34.eq(self.z3 + self.z4)
            self.comb += self.z.eq(self.z12 + self.z34)
            
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
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.e,
                i_b             = self.f,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.g,
                i_b             = self.h,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
        elif (reg_in == 0 and reg_out == 1):
            
            self.sync += self.z12.eq(self.z1 + self.z2)
            self.sync += self.z34.eq(self.z3 + self.z4)
            self.sync += self.z.eq(self.z12 + self.z34)
            
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
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.e,
                i_b             = self.f,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.g,
                i_b             = self.h,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
        elif (reg_in == 1 and reg_out == 1):
            
            self.sync += self.z12.eq(self.z1 + self.z2)
            self.sync += self.z34.eq(self.z3 + self.z4)
            self.sync += self.z.eq(self.z12 + self.z34)
            
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
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.e,
                i_b             = self.f,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.g,
                i_b             = self.h,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
        else:
            
            self.comb += self.z12.eq(self.z1 + self.z2)
            self.comb += self.z34.eq(self.z3 + self.z4)
            self.comb += self.z.eq(self.z12 + self.z34)
            
            # Module instance.
            # ----------------
            self.specials += Instance("RS_DSP_MULT",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,

                # IOs
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z1,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )

            self.specials += Instance("RS_DSP_MULT",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,

                # IOs
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
            self.specials += Instance("RS_DSP_MULT",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,

                # IOs
                i_a             = self.e,
                i_b             = self.f,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )

            self.specials += Instance("RS_DSP_MULT",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,

                # IOs
                i_a             = self.g,
                i_b             = self.h,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT20(Module):
    def __init__(self, a_width, b_width, feature, reg_in, reg_out):

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
        
        if (a_width > b_width):
            k = int(a_width/2)
        else:
            k = int(b_width/2)

        self.a = Signal(a_width)
        self.b = Signal(b_width)
        self.a3 = Signal(36)
        self.b3 = Signal(36)
        
        self.sync += self.a3.eq(self.a)
        self.sync += self.b3.eq(self.b)
        
        self.a0 = Cat(self.a3[0:18],  Replicate(0,2))
        self.a1 = Cat(self.a3[18:36], Replicate(0,4))
        self.b0 = self.b3[0:18]
        self.b1 = self.b3[18:36]
        
        self.z1 = Signal(38)
        self.z2 = Signal(38)
        self.z3 = Signal(38)
        self.z4 = Signal(38)
        
        self.mult2 = Signal(38+1)
        self.mult3 = Signal(39+1+k)
        self.mult4 = Signal(38+1+2*(k))
        self.z = Signal(38+1+2*(k))
        
        # Registered Output
        if (reg_in == 0 and reg_out == 1):
            
            self.sync += self.mult4.eq(self.z4 * (2**(2*(k))))
            self.sync += self.mult2.eq(self.z2 + self.z3)
            self.sync += self.mult3.eq(self.mult2 * (2**k))
            self.comb += self.z.eq(self.mult4 + self.mult3 + self.z1)
            
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
                i_unsigned_b    = 1,
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
                i_a             = self.a0,
                i_b             = self.b1,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
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
                i_b             = self.b0,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
        elif (reg_in == 1 and reg_out == 1):
            
            self.sync += self.mult4.eq(self.z4 * (2**(2*(k))))
            self.sync += self.mult2.eq(self.z2 + self.z3)
            self.sync += self.mult3.eq(self.mult2 * (2**k))
            self.sync += self.z.eq(self.mult4 + self.mult3 + self.z1)
            
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
                i_unsigned_b    = 1,
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
                i_a             = self.a0,
                i_b             = self.b1,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_b             = self.b0,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
        # Registered Input
        else:
            self.comb += self.mult4.eq(self.z4 * (2**(2*(k))))
            self.comb += self.mult2.eq(self.z2 + self.z3)
            self.comb += self.mult3.eq(self.mult2 * (2**k))
            self.comb += self.z.eq(self.mult4 + self.mult3 + self.z1)
            
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
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                i_a             = self.a0,
                i_b             = self.b1,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )
            
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
                i_b             = self.b0,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
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
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1,
            )