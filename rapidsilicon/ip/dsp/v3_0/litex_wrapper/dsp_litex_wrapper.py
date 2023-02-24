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
class RS_DSP_MULT(Module):
    def __init__(self, a_width, b_width, feature, reg_in, reg_out, unsigned_a, unsigned_b):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A      : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B      : {b_width}")
        
        # Registered Input.
        self.logger.info(f"REG_IN       : {reg_in}")
        
        # Registered Output.
        self.logger.info(f"REG_OUT      : {reg_out}")
        
        # Unsigned Input A.
        self.logger.info(f"UNSIGNED_A   : {unsigned_a}")
        
        # Unsigned Input B.
        self.logger.info(f"UNSIGNED_B   : {unsigned_b}")

        # Equation.
        self.logger.info(f"FEATURE      : {feature}")

        self.a = Signal(a_width)
        self.b = Signal(b_width)
        self.z = Signal(a_width + b_width)
        
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b,
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
                i_clk           = ClockSignal(),
                i_lreset        = ResetSignal(),

                # IOs
                i_a             = self.a,
                i_b             = self.b,
                o_z             = self.z,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b,
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b,
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b,
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT_ABCD(Module):
    def __init__(self, a_width, b_width, c_width, d_width, feature, reg_in, reg_out, unsigned_a, unsigned_b, unsigned_c, unsigned_d):

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

        if ((a_width + b_width) > (c_width + d_width)):
            z_width = a_width + b_width + 1
        else:
            z_width = c_width + d_width + 1
        
        self.a  = Signal(a_width)
        self.b  = Signal(b_width)
        self.c  = Signal(c_width)
        self.d  = Signal(d_width)
        self.z1 = Signal(a_width + b_width + 1)
        self.z2 = Signal(c_width + d_width + 1)
        self.z  = Signal(z_width)
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b,
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
                i_unsigned_a    = unsigned_c,
                i_unsigned_b    = unsigned_d,
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b,
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
                i_unsigned_a    = unsigned_c,
                i_unsigned_b    = unsigned_d,
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b,
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
                i_unsigned_a    = unsigned_c,
                i_unsigned_b    = unsigned_d,
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b,
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
                i_unsigned_a    = unsigned_c,
                i_unsigned_b    = unsigned_d,
            )
            
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT_ABCDEFGH(Module):
    def __init__(self, a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, feature, reg_in, reg_out, unsigned_a, unsigned_b, unsigned_c, unsigned_d, unsigned_e, unsigned_f, unsigned_g, unsigned_h):

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
        
        self.z1 = Signal(a_width + b_width + 1)
        self.z2 = Signal(c_width + d_width + 1)
        self.z3 = Signal(e_width + f_width + 1)
        self.z4 = Signal(g_width + h_width + 1)
        
        if ((a_width + b_width) > (c_width + d_width)):
            z12_width = a_width + b_width + 1
        else:
            z12_width = c_width + d_width + 1
        
        if ((e_width + f_width) > (g_width + h_width)):
            z34_width = e_width + f_width + 1
        else:
            z34_width = g_width + h_width + 1
        
        if (z12_width > z34_width):
            z_width = z12_width
        else:
            z_width = z34_width
        
        self.z12 = Signal(z12_width)
        self.z34 = Signal(z34_width)
        self.z  = Signal(z_width)
        
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_c,
                i_unsigned_b    = unsigned_d
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
                i_unsigned_a    = unsigned_e,
                i_unsigned_b    = unsigned_f
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
                i_unsigned_a    = unsigned_g,
                i_unsigned_b    = unsigned_h
            )
            
        elif (reg_in == 0 and reg_out == 1):
            
            self.comb += self.z12.eq(self.z1 + self.z2)
            self.comb += self.z34.eq(self.z3 + self.z4)
            self.comb += self.z.eq(self.z12 + self.z34)
            
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_c,
                i_unsigned_b    = unsigned_d
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
                i_unsigned_a    = unsigned_e,
                i_unsigned_b    = unsigned_f
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
                i_unsigned_a    = unsigned_g,
                i_unsigned_b    = unsigned_h
            )
            
        elif (reg_in == 1 and reg_out == 1):
            
            self.comb += self.z12.eq(self.z1 + self.z2)
            self.comb += self.z34.eq(self.z3 + self.z4)
            self.comb += self.z.eq(self.z12 + self.z34)
            
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_c,
                i_unsigned_b    = unsigned_d
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
                i_unsigned_a    = unsigned_e,
                i_unsigned_b    = unsigned_f
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
                i_unsigned_a    = unsigned_g,
                i_unsigned_b    = unsigned_h
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_c,
                i_unsigned_b    = unsigned_d
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
                i_unsigned_a    = unsigned_e,
                i_unsigned_b    = unsigned_f
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
                i_unsigned_a    = unsigned_g,
                i_unsigned_b    = unsigned_h
            )


# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT20(Module):
    def __init__(self, a_width, b_width, feature, reg_in, reg_out, unsigned_a, unsigned_b):

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
        
        k = 17
        
        self.a = Signal(a_width - 2)
        self.b = Signal(b_width - 2)

        self.a0 = self.a[0:17]
        if (a_width > 18):
            self.a1 = self.a[17:34]
        else:
            self.a1 = Replicate(0,18)
        self.b0 = self.b[0:17]
        if (b_width > 18):
            self.b1 = self.b[17:34]
        else:
            self.b1 = Replicate (0,18)
        
        self.dx = Signal(bits_sign=(20,True))
        self.dy = Signal(bits_sign=(18,True))
        self.comb += self.dx.eq(self.a1 - self.a0)
        self.comb += self.dy.eq(self.b1 - self.b0)

        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.z = Signal(a_width + b_width - 6)
        
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_a             = self.dx,
                i_b             = self.dy,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
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
                i_b             = self.b1,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_a             = self.dx,
                i_b             = self.dy,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
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
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_a             = self.dx,
                i_b             = self.dy,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
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
                i_b             = self.b1,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx,
                i_b             = self.dy,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = 0,
                i_unsigned_b    = 0
            )
            
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
            )
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT36(Module):
    def __init__(self, a_width, b_width, feature, reg_in, reg_out, unsigned_a, unsigned_b):

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
        
        k = 17

        self.a = Signal(a_width - 3)
        self.b = Signal(b_width - 3)
        
        self.a0 = self.a[0:17]
        if (a_width > 18):
            self.a1 = self.a[17:34]
        else:
            self.a1 = Replicate(0,18)
        if (a_width > 36):
            self.a2 = self.a[34:51]
        else:
            self.a2 = Replicate (0,24)
        self.b0 = self.b[0:17]
        if (b_width > 18):
            self.b1 = self.b[17:34]
        else:
            self.b1 = Replicate (0,18)
        if (b_width > 36):
            self.b2 = self.b[34:51]
        else:
            self.b2 = Replicate(0,18)

        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.z4 = Signal(bits_sign=(38,True))
        self.z5 = Signal(bits_sign=(38,True))
        self.z6 = Signal(bits_sign=(38,True))
        
        self.dx1 = Signal(bits_sign=(20,True))
        self.dx2 = Signal(bits_sign=(20,True))
        self.dx3 = Signal(bits_sign=(20,True))
        self.dy1 = Signal(bits_sign=(18,True))
        self.dy2 = Signal(bits_sign=(18,True))
        self.dy3 = Signal(bits_sign=(18,True))

        self.comb += self.dx1.eq(self.a2 - self.a1)
        self.comb += self.dx2.eq(self.a1 - self.a0)
        self.comb += self.dx3.eq(self.a2 - self.a0)

        self.comb += self.dy1.eq(self.b2 - self.b1)
        self.comb += self.dy2.eq(self.b1 - self.b0)
        self.comb += self.dy3.eq(self.b2 - self.b0)

        self.z = Signal(a_width + b_width - 6)


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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
            )
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits tcdo configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx1,
                i_b             = self.dy1,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx2,
                i_b             = self.dy2,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx3,
                i_b             = self.dy3,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT54(Module):
    def __init__(self, a_width, b_width, feature, reg_in, reg_out, unsigned_a, unsigned_b):

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
        
        k = 17

        self.a = Signal(a_width - 4)
        self.b = Signal(b_width - 4)
        
        self.a1 = self.a[0:17]
        if (a_width > 18):
            self.a2 = self.a[17:34]
        else:
            self.a2 = Replicate(0,18)
        if (a_width > 36):
            self.a3 = self.a[34:51]
        else:
            self.a3 = Replicate (0,18)
        if (a_width > 54):
            self.a4 = self.a[51:68]
        else:
            self.a4 = Replicate(0,18)
        self.b1 = self.b[0:17]
        if (b_width > 18):
            self.b2 = self.b[17:34]
        else:
            self.b2 = Replicate (0,18)
        if (b_width > 36):
            self.b3 = self.b[34:51]
        else:
            self.b3 = Replicate(0,18)
        if (b_width > 54):
            self.b4 = self.b[51:68]
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

        self.dx1 = Signal(bits_sign=(20,True))
        self.dx2 = Signal(bits_sign=(20,True))
        self.dx3 = Signal(bits_sign=(20,True))
        self.dx4 = Signal(bits_sign=(20,True))
        self.dx5 = Signal(bits_sign=(20,True))
        self.dx6 = Signal(bits_sign=(20,True))
        self.dy1 = Signal(bits_sign=(18,True))
        self.dy2 = Signal(bits_sign=(18,True))
        self.dy3 = Signal(bits_sign=(18,True))
        self.dy4 = Signal(bits_sign=(18,True))
        self.dy5 = Signal(bits_sign=(18,True))
        self.dy6 = Signal(bits_sign=(18,True))

        self.z = Signal(a_width + b_width - 8)

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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_a             = self.a4,
                i_b             = self.b4,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_a             = self.a4,
                i_b             = self.b4,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_a             = self.a4,
                i_b             = self.b4,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
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
                    i_unsigned_a    = unsigned_a,
                    i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
            )
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
                i_unsigned_a    = unsigned_a,
                i_unsigned_b    = unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx1,
                i_b             = self.dy1,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx2,
                i_b             = self.dy2,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx3,
                i_b             = self.dy3,
                o_z             = self.z7,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx4,
                i_b             = self.dy4,
                o_z             = self.z8,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx5,
                i_b             = self.dy5,
                o_z             = self.z9,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )
            self.specials += Instance("RS_DSP_MULT",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_MODE_BITS     =  0,
                # IOs
                i_a             = self.dx6,
                i_b             = self.dy6,
                o_z             = self.z10,  
                i_feedback      = 0,
                i_unsigned_a    = not unsigned_a,
                i_unsigned_b    = not unsigned_b
            )

