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
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned ):

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
        self.logger.info(f"equation      : {equation}")
        if (unsigned == 0):
            self.a = Signal(bits_sign=(a_width, True))
            self.b = Signal(bits_sign=(b_width, True))
        else:
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
    def __init__(self, a_width, b_width, c_width, d_width, equation, reg_in, reg_out, unsigned ):

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
        self.logger.info(f"equation  : {equation}")

        if ((a_width + b_width) > (c_width + d_width)):
            z_width = a_width + b_width + 1
        else:
            z_width = c_width + d_width + 1
        if(unsigned == 1):
            self.a  = Signal(a_width)
            self.b  = Signal(b_width)
            self.c  = Signal(c_width)
            self.d  = Signal(d_width)

            self.z1 = Signal(a_width + b_width)
            self.z2 = Signal(c_width + d_width)
        else:
            self.a  = Signal(bits_sign=(a_width, True))
            self.b  = Signal(bits_sign=(b_width, True))
            self.c  = Signal(bits_sign=(c_width, True))
            self.d  = Signal(bits_sign=(d_width, True))

            self.z1 = Signal(bits_sign=(a_width + b_width, True))
            self.z2 = Signal(bits_sign=(c_width + d_width, True))
        
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
    def __init__(self, a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, equation, reg_in, reg_out, unsigned):

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
        self.logger.info(f"equation  : {equation}")
        if (unsigned):
            self.a  = Signal(a_width)
            self.b  = Signal(b_width)
            self.c  = Signal(c_width)
            self.d  = Signal(d_width)

            self.e  = Signal(e_width)
            self.f  = Signal(f_width)
            self.g  = Signal(g_width)
            self.h  = Signal(h_width)

            self.z1 = Signal(a_width + b_width)
            self.z2 = Signal(c_width + d_width)
            self.z3 = Signal(e_width + f_width)
            self.z4 = Signal(g_width + h_width)
        else:
            self.a  = Signal(bits_sign=(a_width, True))
            self.b  = Signal(bits_sign=(b_width, True))
            self.c  = Signal(bits_sign=(c_width, True))
            self.d  = Signal(bits_sign=(d_width, True))
            self.e  = Signal(bits_sign=(e_width, True))
            self.f  = Signal(bits_sign=(f_width, True))
            self.g  = Signal(bits_sign=(g_width, True))
            self.h  = Signal(bits_sign=(h_width, True))
        
            self.z1 = Signal(bits_sign=(a_width + b_width, True))
            self.z2 = Signal(bits_sign=(c_width + d_width, True))
            self.z3 = Signal(bits_sign=(e_width + f_width, True))
            self.z4 = Signal(bits_sign=(g_width + h_width, True))
        
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
        self.z  = Signal(z_width + 1)
        self.comb += self.z.eq(self.z1 + self.z2 + self.z3 + self.z4)
        
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
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"equation  : {equation}")
        
        k = 18
        
        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))
        self.a3 = Signal(bits_sign=(36,True))
        self.b3 = Signal(bits_sign=(36,True))
        
        self.comb += self.a3.eq(self.a)
        self.comb += self.b3.eq(self.b)
        
        self.a0 = Cat(self.a3[0:k],  Replicate(0,2))
        if (a_width > k):
            if (unsigned == 1):
                self.a1 = self.a3[k:a_width]
            else:
                self.a1 = Cat(self.a3[k:a_width], Replicate(self.a3[a_width-1], k*2-a_width+2))
        elif (a_width == k):
            if(unsigned == 0):
                self.a1 = Cat(self.a3[a_width-1], Replicate(self.a3[(a_width)-1], k*2-a_width+1))
            else:
                self.a1 = self.a3[a_width-1]
        else:
            self.a1 = Replicate(0,20)
        
        self.b0 = self.b3[0:k]
        if (b_width > k):
            if(unsigned == 1):
                self.b1 = self.b3[k:b_width]
            else:
                self.b1 = Cat(self.b3[k:b_width], Replicate(self.b3[(b_width)-1], k*2-b_width))
        elif (b_width == k):
            if(unsigned == 0):
                self.b1 = Cat(self.b3[b_width-1], Replicate(self.b3[(b_width)-1], k*2-b_width+1))
            else:
                self.b1 = self.b3[b_width-1]
        else:
            self.b1 = Replicate(0,18)

        self.z1 = Signal(bits_sign=(38,True))
        self.z2 = Signal(bits_sign=(38,True))
        self.z3 = Signal(bits_sign=(38,True))
        self.z4 = Signal(bits_sign=(38,True))
        
        self.mult2 = Signal(bits_sign=(39,True))
        self.mult3 = Signal(bits_sign=(39+k,True))
        self.mult4 = Signal(bits_sign=(a_width + b_width,True))
        self.z = Signal(a_width + b_width)


        self.comb += self.mult4.eq(self.z4 << 36)
        self.comb += self.mult2.eq(self.z2 + self.z3)
        self.comb += self.mult3.eq(self.mult2 << 18)
        self.comb += self.z.eq(self.mult4 + self.mult3 + self.z1)
        
        
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
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"equation  : {equation}")
        
        k = 18

        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))
        self.a3 = Signal(bits_sign=(a_width,True))
        self.b3 = Signal(bits_sign=(b_width,True))
        
        self.comb += self.a3.eq(self.a)
        self.comb += self.b3.eq(self.b)

        a0_sign = 1
        a1_sign = 1
        a2_sign = 1
        b0_sign = 1
        b1_sign = 1
        b2_sign = 1

        if (a_width <= k):
            self.a1 =  Replicate(0,20)
            self.a2 =  Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a3[0:a_width],  Replicate(0,2))
            else:
                self.a0 = Cat(self.a3[0:a_width],  Replicate(self.a3[a_width - 1],k-a_width+2))
                a0_sign = 0
        if (a_width > k and a_width < k*2):
          self.a2 =  Replicate(0,20)
          self.a0 = Cat(self.a3[0:k],  Replicate(0,2))
          if(unsigned):
              self.a1 = Cat(self.a3[k:a_width], Replicate(0,2))
          else:
              a1_sign = 0
              self.a1 = Cat(self.a3[k:a_width], Replicate(self.a3[a_width - 1],k*2-a_width+2))
        if (a_width == k*2):
          self.a0 = Cat(self.a3[0:k],  Replicate(0,2))
          self.a1 = Cat(self.a3[k:k*2], Replicate(0,2))
          if(unsigned == 0):
              a2_sign = 0
              self.a2 = Cat(self.a3[a_width-1], Replicate(self.a3[(a_width)-1], k*3-a_width+1))
          else:
              self.a2 = self.a3[a_width-1]
        if(a_width > k and a_width > k*2):
          self.a0 = Cat(self.a3[0:k],  Replicate(0,2))
          self.a1 = Cat(self.a3[k:k*2], Replicate(0,2))
          if (unsigned):
              self.a2 = Cat(self.a3[k*2:a_width], Replicate(0,2))
          else:
              a2_sign = 0
              self.a2 = Cat(self.a3[k*2:a_width], Replicate(self.a3[a_width - 1],k*3-a_width+2))
        if (a_width == k*3):
            self.a0 = Cat(self.a3[0:k],  Replicate(0,2))
            self.a1 = Cat(self.a3[k:k*2], Replicate(0,2))
            if(unsigned == 0):
                a2_sign = 0
                self.a2 = Cat(self.a3[a_width-1], Replicate(self.a3[(a_width)-1], k*4-a_width+1))
            else:
                self.a2 = self.a3[a_width-1]
        


        if (b_width <= k):
            self.b1 =  Replicate(0,20)
            self.b2 =  Replicate(0,20)
            if(unsigned):
                self.b0 = Cat(self.b3[0:b_width],  Replicate(0,2))
            else:
                self.b0 = Cat(self.b3[0:b_width],  Replicate(self.b3[b_width - 1],k-b_width+2))
                b0_sign = 0
        if (b_width > k and b_width < k*2):
          self.b2 =  Replicate(0,20)
          self.b0 = Cat(self.b3[0:k],  Replicate(0,2))
          if(unsigned):
              self.b1 = Cat(self.b3[k:b_width], Replicate(0,2))
          else:
              b1_sign = 0
              self.b1 = Cat(self.b3[k:b_width], Replicate(self.b3[b_width - 1],k*2-b_width+2))
        if (b_width == k*2):
          self.b0 = Cat(self.b3[0:k],  Replicate(0,2))
          self.b1 = Cat(self.b3[k:k*2], Replicate(0,2))
          if(unsigned == 0):
              b2_sign = 0
              self.b2 = Cat(self.b3[b_width-1], Replicate(self.b3[(b_width)-1], k*3-b_width+1))
          else:
              self.b2 = self.b3[b_width-1]
        if(b_width > k and b_width > k*2):
          self.b0 = Cat(self.b3[0:k],  Replicate(0,2))
          self.b1 = Cat(self.b3[k:k*2], Replicate(0,2))
          if (unsigned):
              self.b2 = Cat(self.b3[k*2:b_width], Replicate(0,2))
          else:
              b2_sign = 0
              self.b2 = Cat(self.b3[k*2:b_width], Replicate(self.b3[b_width - 1],k*3-b_width+2))
        if (b_width == k*3):
            self.b0 = Cat(self.b3[0:k],  Replicate(0,2))
            self.b1 = Cat(self.b3[k:k*2], Replicate(0,2))
            if(unsigned == 0):
                b2_sign = 0
                self.b2 = Cat(self.b3[b_width-1], Replicate(self.b3[(b_width)-1], k*4-b_width+1))
            else:
                self.b2 = self.b3[b_width-1]
        

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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b0_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a0_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b1_sign
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
                i_unsigned_a    = a1_sign,
                i_unsigned_b    = b2_sign
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
                i_unsigned_a    = a2_sign,
                i_unsigned_b    = b2_sign
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT54(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"equation  : {equation}")
        
        k = 18

        self.a = Signal(bits_sign=(a_width,True))
        self.b = Signal(bits_sign=(b_width,True))
        self.a3 = Signal(bits_sign=(a_width,True))
        self.b3 = Signal(bits_sign=(b_width,True))
        
        self.comb += self.a3.eq(self.a)
        self.comb += self.b3.eq(self.b)
        
        self.a0 = Cat(self.a3[0:k],  Replicate(0,2))
        self.a1 = Cat(self.a3[k:k*2], Replicate(0,2))
        self.a2 = Cat(self.a3[k*2:k*3], Replicate(0,2))
        if (a_width > k*3):
            if (unsigned == 1):
                self.a4 = Cat(self.a3[k*3:k*4], Replicate(0,2))
            else:
                self.a4 = Cat(self.a3[k*3:a_width], Replicate(self.a3[a_width-1], k*4-a_width+2))
        elif (a_width == k*3):
            if(unsigned == 0):
                self.a4 = Cat(self.a3[a_width-1], Replicate(self.a3[(a_width)-1], k*4-a_width+1))
            else:
                self.a4 = self.a3[a_width-1]
        else:
            self.a4 = Replicate(0,20)

        self.b0 = self.b3[0:k]
        self.b1 = self.b3[k:k*2]
        self.b2 = self.b3[k*2:k*3]
        if (b_width > k*3):
            if(unsigned == 1):
                self.b4 = self.b3[k*3:k*4]
            else:
                self.b4 = Cat(self.b3[k*3:b_width], Replicate(self.b3[(b_width)-1], k*4-b_width))
        elif (b_width == k*3):
            if (unsigned == 0):
                self.b4 = Cat(self.b3[b_width-1], Replicate(self.b3[(b_width)-1], k*4-b_width-1))
            else:
                self.b4 = self.b3[b_width-1]
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

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT20_pipeline(Module):
    def __init__(self, a_width, b_width, equation, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"EQUATION  : {equation}")
        
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
                self.a1 = Cat(self.a[k:a_width], Replicate(self.a[(a_width)-1], k*2-a_width+3))
        elif (a_width == k):
            if(unsigned == 0):
                self.a1 = Cat(self.a[a_width-1], Replicate(self.a[(a_width)-1], k*2-a_width+2))
            else:
                self.a1 = self.a[a_width-1]
        else:
            self.a1 = Replicate(0,18)

        self.b0 = self.b[0:k]
        if (b_width > k):
            if (unsigned == 1):
                self.b1 = self.b[k:k*2]
            else:
                self.b1 = Cat(self.b[k:b_width], Replicate(self.b[(b_width)-1], k*2-b_width+1))
        elif (b_width == k):
            if(unsigned == 0):
                self.b1 = Cat(self.b[b_width-1], Replicate(self.b[(b_width)-1], k*2-b_width+2))
            else:
                self.b1 = self.b[b_width-1]
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
class RS_DSP_MULT36_pipeline(Module):
    def __init__(self, a_width, b_width, equation,unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"EQUATION  : {equation}")
        
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
        self.a2 = self.a[k:k*2]
        if (a_width > k*2):
            if(unsigned == 1):
                self.a3 = self.a[k*2:k*3]
            else:
                self.a3 = Cat(self.a[k*2:a_width], Replicate(self.a[(a_width)-1], k*3-a_width+3))
        elif (a_width == k*2):
            if(unsigned == 0):
                self.a3 = Cat(self.a[a_width-1], Replicate(self.a[(a_width)-1], k*3-a_width+2))
            else:
                self.a3 = self.a[a_width-1]
        else:
            self.a3 = Replicate (0,18)

        self.b1 = self.b[0:k]
        self.b2 = self.b[k:k*2]
        if (b_width > k*2):
            if (unsigned == 1):
                self.b3 = self.b[k*2:k*3]
            else:
                self.b3 = Cat(self.b[k*2:b_width], Replicate(self.b[(b_width)-1], k*3-b_width+1))
        elif (b_width == k*2):
            if(unsigned == 0):
                self.b3 = Cat(self.b[b_width-1], Replicate(self.b[(b_width)-1], k*3-b_width+2))
            else:
                self.b3 = self.b[b_width-1]
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
class RS_DSP_MULT54_pipeline(Module):
    def __init__(self, a_width, b_width, equation, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"EQUATION  : {equation}")
        
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
        self.a1 = self.a[k:k*2]
        self.a2 = self.a[k*2:k*3]
        if (a_width > k*3):
            if (unsigned == 1):
                self.a3 = self.a[k*3:k*4]
            else:
                self.a3 = Cat(self.a[k*3:a_width], Replicate(self.a[(a_width)-1], k*4-a_width+3))
        elif (a_width == k*3):
            if(unsigned == 0):
                self.a3 = Cat(self.a[a_width-1], Replicate(self.a[(a_width)-1], k*4-a_width+2))
            else:
                self.a3 = self.a[a_width-1]
        else:
            self.a3 = Replicate(0,18)

        self.b0 = self.b[0:k]
        self.b1 = self.b[k:k*2]
        self.b2 = self.b[k*2:k*3]
        if (b_width > k*3):
            if (unsigned == 1):
                self.b3 = self.b[k*3:k*4]
            else:
                self.b3 = Cat(self.b[k*3:b_width], Replicate(self.b[(b_width)-1], k*4-b_width+1))
        elif (b_width == k*3):
            if(unsigned == 0):
                self.b3 = Cat(self.b[b_width-1], Replicate(self.b[(b_width)-1], k*4-b_width+2))
            else:
                self.b3 = self.b[b_width-1]
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

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT20_enhance(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"EQUATION  : {equation}")
        
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

            self.comb += self.a__1.eq(Cat(self.a1, Replicate(self.a[a_width - 1], k*2-a_width+1)))
            if (b_width != k):
                self.comb += self.b__1.eq(Cat(self.b1, Replicate(self.b[b_width - 1], k*2-b_width+1)))
                self.comb += self.b__0.eq(Cat(self.b0, Replicate(0,1)))
            else:
                self.comb += self.b__1.eq(self.b1)
                self.comb += self.b__0.eq(Cat(self.b0, Replicate(self.b[b_width - 1],1)))
            self.comb += self.a__0.eq(Cat(self.a0, Replicate(0,1)))
            

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
                    i_a             = Cat(self.a1, Replicate(self.a[a_width - 1], k*2-a_width+4)),
                    i_b             = Cat(self.b1, Replicate(self.b[b_width - 1], k*2-b_width+2)),
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
                    i_a             = Cat(self.a1, Replicate(self.a[a_width - 1], k*2-a_width+4)),
                    i_b             = Cat(self.b1, Replicate(self.b[b_width - 1], k*2-b_width+2)),
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
                    i_a             = Cat(self.a1, Replicate(self.a[a_width - 1], k*2-a_width+4)),
                    i_b             = Cat(self.b1, Replicate(self.b[b_width - 1], k*2-b_width+2)),
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
                i_b             = self.b__0,
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
                    i_a             = Cat(self.a__1, Replicate(self.a__1[len(self.a__1)-1], k*2-a_width+4)),
                    i_b             = Cat(self.b__1, Replicate(self.b__1[b_width - 1], k*2-b_width+2)),
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
class RS_DSP_MULT36_enhance(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"EQUATION  : {equation}")
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

            self.comb += self.a__2.eq(Cat(self.a2, Replicate(self.a[a_width - 1], k*3-a_width+1)))
            self.comb += self.b__2.eq(Cat(self.b2, Replicate(self.b[b_width - 1], k*3-b_width+1)))
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
                    i_a             = Cat(self.a2, Replicate(self.a[a_width - 1], k*3-a_width+4)),
                    i_b             = Cat(self.b2, Replicate(self.b[b_width - 1], k*3-b_width+2)),
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
                    i_a             = Cat(self.a2, Replicate(self.a[a_width - 1], k*3-a_width+4)),
                    i_b             = Cat(self.b2, Replicate(self.b[b_width - 1], k*3-b_width+2)),
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
                    i_a             = Cat(self.a2, Replicate(self.a[a_width - 1], k*3-a_width+4)),
                    i_b             = Cat(self.b2, Replicate(self.b[b_width - 1], k*3-b_width+2)),
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
                    i_a             = Cat(self.a2, Replicate(self.a[a_width - 1], k*3-a_width+4)),
                    i_b             = Cat(self.b2, Replicate(self.b[b_width - 1], k*3-b_width+2)),
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
class RS_DSP_MULT54_enhance(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned, ):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tRS_DSP_MULT")
        
        self.logger.propagate = False

        # Input A.
        self.logger.info(f"INPUT_A  : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B  : {b_width}")

        # Equation.
        self.logger.info(f"EQUATION  : {equation}")
        
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

            self.comb += self.a__4.eq(Cat(self.a4, Replicate(self.a[a_width - 1], k*4-a_width+1)))
            self.comb += self.b__4.eq(Cat(self.b4, Replicate(self.b[b_width - 1], k*4-b_width+1)))
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
                    i_a             = Cat(self.a4, Replicate(self.a[a_width - 1], k*4-a_width+4)),
                    i_b             = Cat(self.b4, Replicate(self.b[b_width - 1], k*4-b_width+2)),
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
                    i_a             = Cat(self.a4, Replicate(self.a[a_width - 1], k*4-a_width+4)),
                    i_b             = Cat(self.b4, Replicate(self.b[b_width - 1], k*4-b_width+2)),
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
                    i_a             = Cat(self.a4, Replicate(self.a[a_width - 1], k*4-a_width+4)),
                    i_b             = Cat(self.b4, Replicate(self.b[b_width - 1], k*4-b_width+2)),
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
                    i_a             = Cat(self.a4, Replicate(self.a[a_width - 1], k*4-a_width+4)),
                    i_b             = Cat(self.b4, Replicate(self.b[b_width - 1], k*4-b_width+2)),
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

