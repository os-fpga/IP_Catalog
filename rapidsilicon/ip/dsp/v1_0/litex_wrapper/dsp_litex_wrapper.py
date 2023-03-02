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
    def __init__(self, a_width, b_width, feature, reg_in, reg_out, unsigned, ):

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
        self.logger.info(f"unsigned   : {unsigned}")

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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT_ABCD(Module):
    def __init__(self, a_width, b_width, c_width, d_width, feature, reg_in, reg_out, unsigned ):

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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned,
            )
            
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT_ABCDEFGH(Module):
    def __init__(self, a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, feature, reg_in, reg_out, unsigned):

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
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
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
                i_a             = self.e,
                i_b             = self.f,
                o_z             = self.z3,  
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
                i_a             = self.g,
                i_b             = self.h,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_a             = self.c,
                i_b             = self.d,
                o_z             = self.z2,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_a             = self.g,
                i_b             = self.h,
                o_z             = self.z4,  
                i_feedback      = 0,
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
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
                i_unsigned_a    = unsigned,
                i_unsigned_b    = unsigned
            )


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
        
        k = 18
        
        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))
        self.a3 = Signal(bits_sign=(36,True))
        self.b3 = Signal(bits_sign=(36,True))
        
        self.comb += self.a3.eq(self.a)
        self.comb += self.b3.eq(self.b)
        
        self.a0 = Cat(self.a3[0:18],  Replicate(0,2))
        if (a_width > 18):
            if (unsigned == 1):
                self.a1 = self.a3[18:36]
            else:
                self.a1 = Cat(self.a3[18:36], Replicate(self.a3[35], 2))
        else:
            self.a1 = Replicate(0,22)
        self.b0 = self.b3[0:18]
        if (b_width > 18):
            self.b1 = self.b3[18:36]
        else:
            self.b1 = Replicate (0,18)
        
        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.z4 = Signal(bits_sign=(38,True))
        
        self.mult2 = Signal(bits_sign=(39,True))
        self.mult3 = Signal(bits_sign=(39+k,True))
        self.mult4 = Signal(bits_sign=(a_width + b_width,True))
        self.z = Signal(a_width + b_width)
        
        
        # Registered Output
        if (reg_in == 0 and reg_out == 1):
            self.comb += self.mult4.eq(self.z4 << 36)
            self.comb += self.mult2.eq(self.z2 + self.z3)
            self.comb += self.mult3.eq(self.mult2 << 18)
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
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b0,
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_a             = self.a0,
                    i_b             = self.b1,
                    o_z             = self.z2,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
        elif (reg_in == 1 and reg_out == 1):
            self.comb += self.mult4.eq(self.z4 << 36)
            self.comb += self.mult2.eq(self.z2 + self.z3)
            self.comb += self.mult3.eq(self.mult2 << 18)
            self.comb += self.z.eq(self.mult4 + self.mult3 + self.z1)

            
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
            if (unsigned == 0):
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
                    i_b             = self.b0,
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_a             = self.a0,
                    i_b             = self.b1,
                    o_z             = self.z2,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
            
        # Registered Input
        elif (reg_in == 1 and reg_out == 0):
            self.comb += self.mult4.eq(self.z4 << 36)
            self.comb += self.mult2.eq(self.z2 + self.z3)
            self.comb += self.mult3.eq(self.mult2 << 18)
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
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b0,
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_a             = self.a0,
                    i_b             = self.b1,
                    o_z             = self.z2,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
        
        else:
            self.comb += self.mult4.eq(self.z4 << 36)
            self.comb += self.mult2.eq(self.z2 + self.z3)
            self.comb += self.mult3.eq(self.mult2 << 18)
            self.comb += self.z.eq(self.mult4 + self.mult3 + self.z1)
            
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
            if (unsigned == 0):
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a0,
                    i_b             = self.b1,
                    o_z             = self.z2,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_b             = self.b0,
                    o_z             = self.z3,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_a             = self.a0,
                    i_b             = self.b1,
                    o_z             = self.z2,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                    i_b             = self.b0,
                    o_z             = self.z3,  
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
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT36(Module):
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
        
        k = 18

        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))
        self.a3 = Signal(bits_sign=(a_width,True))
        self.b3 = Signal(bits_sign=(b_width,True))
        
        self.comb += self.a3.eq(self.a)
        self.comb += self.b3.eq(self.b)
        
        self.a0 = Cat(self.a3[0:18],  Replicate(0,2))
        if (a_width > 18):
            self.a1 = Cat(self.a3[18:36], Replicate(0,2))
        else:
            self.a1 = Replicate(0,22)
        if (a_width > 36):
            if (unsigned == 1):
                self.a2 = Cat(self.a3[36:54], Replicate(0,2))
            else:
                self.a2 = Cat(self.a3[36:54], Replicate(self.a3[53], 2))
        else:
            self.a2 = Replicate (0,24)
        self.b0 = self.b3[0:18]
        if (b_width > 18):
            self.b1 = self.b3[18:36]
        else:
            self.b1 = Replicate (0,18)
        if (b_width > 36):
            self.b2 = self.b3[36:54]
        else:
            self.b2 = Replicate(0,18)

        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.z4 = Signal(bits_sign=(38,True))
        self.z5 = Signal(bits_sign=(38,True))
        self.z6 = Signal(bits_sign=(38,True))
        self.z7 = Signal(bits_sign=(38,True))
        self.z8 = Signal(bits_sign=(38,True))
        self.z9 = Signal(bits_sign=(38,True))
        
        self.mult3 = Signal(bits_sign=(39+k,True))
        self.mult4 = Signal(bits_sign=(40+2*k,True))
        self.mult5 = Signal(bits_sign=(39+3*k,True))
        self.mult6 = Signal(bits_sign=(38+4*k,True))
        self.z = Signal(a_width + b_width)

        self.comb += self.mult6.eq(self.z9 << 4*k)
        self.comb += self.mult5.eq((self.z7 + self.z8) << 3*k)
        self.comb += self.mult4.eq((self.z4 + self.z5 + self.z6) << 2*k)
        self.comb += self.mult3.eq((self.z2 + self.z3) << k)
        self.comb += self.z.eq(self.mult6 + self.mult5 + self.mult4 + self.mult3 + self.z1)

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
                i_b             = self.b0,
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
                i_a             = self.a0,
                i_b             = self.b1,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b0,
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_b             = self.b0,
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
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b2,
                    o_z             = self.z6,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a2,
                    i_b             = self.b1,
                    o_z             = self.z7,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_b             = self.b2,
                    o_z             = self.z8,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a2,
                    i_b             = self.b2,
                    o_z             = self.z9,  
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
                    i_a             = self.a0,
                    i_b             = self.b2,
                    o_z             = self.z6,  
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
                    i_b             = self.b1,
                    o_z             = self.z7,  
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
                    i_b             = self.b2,
                    o_z             = self.z8,  
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
                    o_z             = self.z9,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                i_b             = self.b0,
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
                i_a             = self.a0,
                i_b             = self.b1,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b0,
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_b             = self.b0,
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
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b2,
                    o_z             = self.z6,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a2,
                    i_b             = self.b1,
                    o_z             = self.z7,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_b             = self.b2,
                    o_z             = self.z8,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a2,
                    i_b             = self.b2,
                    o_z             = self.z9,  
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
                    i_a             = self.a0,
                    i_b             = self.b2,
                    o_z             = self.z6,  
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
                    i_b             = self.b1,
                    o_z             = self.z7,  
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
                    i_b             = self.b2,
                    o_z             = self.z8,  
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
                    o_z             = self.z9,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                i_b             = self.b0,
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
                i_a             = self.a0,
                i_b             = self.b1,
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
                    i_a             = self.a2,
                    i_b             = self.b0,
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_b             = self.b0,
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
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z5,  
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
                    i_a             = self.a0,
                    i_b             = self.b2,
                    o_z             = self.z6,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a2,
                    i_b             = self.b1,
                    o_z             = self.z7,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_b             = self.b2,
                    o_z             = self.z8,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a2,
                    i_b             = self.b2,
                    o_z             = self.z9,  
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
                    i_a             = self.a0,
                    i_b             = self.b2,
                    o_z             = self.z6,  
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
                    i_b             = self.b1,
                    o_z             = self.z7,  
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
                    i_b             = self.b2,
                    o_z             = self.z8,  
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
                    o_z             = self.z9,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                i_b             = self.b0,
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
                i_a             = self.a0,
                i_b             = self.b1,
                o_z             = self.z3,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b0,
                    o_z             = self.z4,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
                )
            else:
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b0,
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
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z5,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a0,
                    i_b             = self.b2,
                    o_z             = self.z6,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 0
                )
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b1,
                    o_z             = self.z7,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
                )
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a1,
                    i_b             = self.b2,
                    o_z             = self.z8,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 0
                )
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b2,
                    o_z             = self.z9,  
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
                    i_b             = self.b2,
                    o_z             = self.z6,  
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
                    i_b             = self.b1,
                    o_z             = self.z7,  
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
                    i_b             = self.b2,
                    o_z             = self.z8,  
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
                    o_z             = self.z9,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
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
        
        k = 18

        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))
        self.a3 = Signal(bits_sign=(a_width,True))
        self.b3 = Signal(bits_sign=(b_width,True))
        
        self.comb += self.a3.eq(self.a)
        self.comb += self.b3.eq(self.b)
        
        self.a0 = Cat(self.a3[0:18],  Replicate(0,2))
        if (a_width > 18):
            self.a1 = Cat(self.a3[18:36], Replicate(0,2))
        else:
            self.a1 = Replicate(0,22)
        if (a_width > 36):
            self.a2 = Cat(self.a3[36:54], Replicate(0,2))
        else:
            self.a2 = Replicate (0,24)
        if (a_width > 54):
            if (unsigned == 1):
                self.a4 = Cat(self.a3[54:72], Replicate(0,2))
            else:
                self.a4 = Cat(self.a3[54:72], Replicate(self.a3[71], 2))
        else:
            self.a4 = Replicate(0,20)
        self.b0 = self.b3[0:18]
        if (b_width > 18):
            self.b1 = self.b3[18:36]
        else:
            self.b1 = Replicate (0,18)
        if (b_width > 36):
            self.b2 = self.b3[36:54]
        else:
            self.b2 = Replicate(0,18)
        if (b_width > 54):
            self.b4 = self.b3[54:72]
        else:
            self.b4 = Replicate(0,18)

        self.z1  = Signal(bits_sign=(38,True))
        self.z2  = Signal(bits_sign=(38,True))
        self.z3  = Signal(bits_sign=(38,True))
        self.z4  = Signal(bits_sign=(38,True))
        self.z5  = Signal(bits_sign=(38,True))
        self.z6  = Signal(bits_sign=(38,True))
        self.z7  = Signal(bits_sign=(38,True))
        self.z8  = Signal(bits_sign=(38,True))
        self.z9  = Signal(bits_sign=(38,True))
        self.z10 = Signal(bits_sign=(38,True))
        self.z11 = Signal(bits_sign=(38,True))
        self.z12 = Signal(bits_sign=(38,True))
        self.z13 = Signal(bits_sign=(38,True))
        self.z14 = Signal(bits_sign=(38,True))
        self.z15 = Signal(bits_sign=(38,True))
        self.z16 = Signal(bits_sign=(38,True))

        self.z = Signal(a_width + b_width)

        self.mult1 = Signal(bits_sign=(38+6*k,True))
        self.mult2 = Signal(bits_sign=(39+5*k,True))
        self.mult3 = Signal(bits_sign=(40+4*k,True))
        self.mult4 = Signal(bits_sign=(41+3*k,True))
        self.mult5 = Signal(bits_sign=(40+2*k,True))
        self.mult6 = Signal(bits_sign=(39+k,True))

        self.comb += self.mult1.eq(self.z16 << 6*k)
        self.comb += self.mult2.eq((self.z14 + self.z15) << 5*k)
        self.comb += self.mult3.eq((self.z11 + self.z12 + self.z13) << 4*k)
        self.comb += self.mult4.eq((self.z7 + self.z8 + self.z9 + self.z10) << 3*k)
        self.comb += self.mult5.eq((self.z4 + self.z5 + self. z6) << 2*k)
        self.comb += self.mult6.eq((self.z2 + self.z3) << k)
        self.comb += self.z.eq(self.mult1 + self.mult2 + self.mult3 + self.mult4 + self.mult5 + self.mult6 + self.z1)

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
                i_a             = self.a0,
                i_b             = self.b1,
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
                i_a             = self.a1,
                i_b             = self.b0,
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
                i_a             = self.a2,
                i_b             = self.b0,
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
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z5,  
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
                i_a             = self.a0,
                i_b             = self.b2,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b0,
                    o_z             = self.z7,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_b             = self.b0,
                    o_z             = self.z7,  
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
                i_b             = self.b1,
                o_z             = self.z8,  
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
                i_b             = self.b2,
                o_z             = self.z9,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b4,
                    o_z             = self.z10,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b1,
                    o_z             = self.z11,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_a             = self.a0,
                    i_b             = self.b4,
                    o_z             = self.z10,  
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
                    i_a             = self.a4,
                    i_b             = self.b1,
                    o_z             = self.z11,  
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
                o_z             = self.z12,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b4,
                    o_z             = self.z13,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b2,
                    o_z             = self.z14,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_b             = self.b4,
                    o_z             = self.z15,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z16,  
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
                    i_a             = self.a1,
                    i_b             = self.b4,
                    o_z             = self.z13,  
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
                    i_a             = self.a4,
                    i_b             = self.b2,
                    o_z             = self.z14,  
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
                    i_b             = self.b4,
                    o_z             = self.z15,  
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
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z16,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                i_a             = self.a0,
                i_b             = self.b1,
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
                i_a             = self.a1,
                i_b             = self.b0,
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
                i_a             = self.a2,
                i_b             = self.b0,
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
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z5,  
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
                i_a             = self.a0,
                i_b             = self.b2,
                o_z             = self.z6,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b0,
                    o_z             = self.z7,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_b             = self.b0,
                    o_z             = self.z7,  
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
                i_b             = self.b1,
                o_z             = self.z8,  
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
                i_b             = self.b2,
                o_z             = self.z9,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b4,
                    o_z             = self.z10,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b1,
                    o_z             = self.z11,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_a             = self.a0,
                    i_b             = self.b4,
                    o_z             = self.z10,  
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
                    i_a             = self.a4,
                    i_b             = self.b1,
                    o_z             = self.z11,  
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
                o_z             = self.z12,  
                i_feedback      = 0,
                i_unsigned_a    = 1,
                i_unsigned_b    = 1
            )
            if (unsigned == 0):
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
                    i_b             = self.b4,
                    o_z             = self.z13,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b2,
                    o_z             = self.z14,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_b             = self.b4,
                    o_z             = self.z15,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z16,  
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
                    i_a             = self.a1,
                    i_b             = self.b4,
                    o_z             = self.z13,  
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
                    i_a             = self.a4,
                    i_b             = self.b2,
                    o_z             = self.z14,  
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
                    i_b             = self.b4,
                    o_z             = self.z15,  
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
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z16,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                i_a             = self.a0,
                i_b             = self.b1,
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
                i_a             = self.a1,
                i_b             = self.b0,
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
                i_a             = self.a2,
                i_b             = self.b0,
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
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z5,  
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
                i_a             = self.a0,
                i_b             = self.b2,
                o_z             = self.z6,  
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
                    i_a             = self.a4,
                    i_b             = self.b0,
                    o_z             = self.z7,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_b             = self.b0,
                    o_z             = self.z7,  
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
                i_b             = self.b1,
                o_z             = self.z8,  
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
                i_b             = self.b2,
                o_z             = self.z9,  
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
                    i_a             = self.a0,
                    i_b             = self.b4,
                    o_z             = self.z10,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b1,
                    o_z             = self.z11,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
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
                    i_a             = self.a0,
                    i_b             = self.b4,
                    o_z             = self.z10,  
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
                    i_a             = self.a4,
                    i_b             = self.b1,
                    o_z             = self.z11,  
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
                o_z             = self.z12,  
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
                    i_a             = self.a1,
                    i_b             = self.b4,
                    o_z             = self.z13,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b2,
                    o_z             = self.z14,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
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
                    i_b             = self.b4,
                    o_z             = self.z15,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
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
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z16,  
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
                    i_a             = self.a1,
                    i_b             = self.b4,
                    o_z             = self.z13,  
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
                    i_a             = self.a4,
                    i_b             = self.b2,
                    o_z             = self.z14,  
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
                    i_b             = self.b4,
                    o_z             = self.z15,  
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
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z16,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
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
                i_a             = self.a0,
                i_b             = self.b1,
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
                i_a             = self.a1,
                i_b             = self.b0,
                o_z             = self.z3,  
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
                i_b             = self.b0,
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
                i_a             = self.a1,
                i_b             = self.b1,
                o_z             = self.z5,  
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
                i_a             = self.a0,
                i_b             = self.b2,
                o_z             = self.z6,  
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
                    i_a             = self.a4,
                    i_b             = self.b0,
                    o_z             = self.z7,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
                )
            else:
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a4,
                    i_b             = self.b0,
                    o_z             = self.z7,  
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
                i_b             = self.b1,
                o_z             = self.z8,  
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
                i_b             = self.b2,
                o_z             = self.z9,  
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
                    i_a             = self.a0,
                    i_b             = self.b4,
                    o_z             = self.z10,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 0
                )
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a4,
                    i_b             = self.b1,
                    o_z             = self.z11,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
                )
            else:
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a0,
                    i_b             = self.b4,
                    o_z             = self.z10,  
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
                    i_a             = self.a4,
                    i_b             = self.b1,
                    o_z             = self.z11,  
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
                o_z             = self.z12,  
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
                    i_a             = self.a1,
                    i_b             = self.b4,
                    o_z             = self.z13,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 0
                )
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a4,
                    i_b             = self.b2,
                    o_z             = self.z14,  
                    i_feedback      = 0,
                    i_unsigned_a    = 0,
                    i_unsigned_b    = 1
                )
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a2,
                    i_b             = self.b4,
                    o_z             = self.z15,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 0
                )
                self.specials += Instance("RS_DSP_MULT",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_MODE_BITS     =  0,
                    # IOs
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z16,  
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
                    i_b             = self.b4,
                    o_z             = self.z13,  
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
                    i_a             = self.a4,
                    i_b             = self.b2,
                    o_z             = self.z14,  
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
                    i_b             = self.b4,
                    o_z             = self.z15,  
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
                    i_a             = self.a4,
                    i_b             = self.b4,
                    o_z             = self.z16,  
                    i_feedback      = 0,
                    i_unsigned_a    = 1,
                    i_unsigned_b    = 1
                )

