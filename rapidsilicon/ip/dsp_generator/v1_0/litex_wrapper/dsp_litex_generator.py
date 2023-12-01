#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned ):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")

        # Input A.
        self.logger.info(f"INPUT_A      : {a_width}")

        # Input B.
        self.logger.info(f"INPUT_B      : {b_width}")
        
        # Registered Input.
        self.logger.info(f"REG_IN       : {reg_in}")
        
        # Registered Output.
        self.logger.info(f"REG_OUT      : {reg_out}")
        
        # Unsigned Input A.
        self.logger.info(f"UNSIGNED     : {unsigned}")

        # Equation.
        self.logger.info(f"EQUATION     : {equation}")
        
        self.logger.info(f"===================================================")
        
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
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN   =  "FALSE",
                p_INPUT_REG_EN    =  "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )
            
        elif (reg_in == 0 and reg_out == 1):
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )
            
        elif (reg_in == 1 and reg_out == 1):
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )
            
        else:
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT_ABCD(Module):
    def __init__(self, a_width, b_width, c_width, d_width, equation, reg_in, reg_out, unsigned ):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK               = ClockSignal(),
                i_RESET            = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK               = ClockSignal(),
                i_RESET            = ResetSignal(),

                # IOs
                i_A             = self.c,
                i_B             = self.d,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )
            
        elif (reg_in == 0 and reg_out == 1):
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                
                # Reset
                i_CLK               = ClockSignal(),
                i_RESET            = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                
                # Reset
                i_CLK               = ClockSignal(),
                i_RESET            = ResetSignal(),

                # IOs
                i_A             = self.c,
                i_B             = self.d,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )
            
        elif (reg_in == 1 and reg_out == 1):
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.c,
                i_B             = self.d,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )
            
        else:
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",

                # IOs
                i_A             = self.c,
                i_B             = self.d,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned,
            )
            
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT_ABCDEFGH(Module):
    def __init__(self, a_width, b_width, c_width, d_width, e_width, f_width, g_width, h_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.c,
                i_B             = self.d,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.e,
                i_B             = self.f,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.g,
                i_B             = self.h,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
        elif (reg_in == 0 and reg_out == 1):
            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.c,
                i_B             = self.d,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.e,
                i_B             = self.f,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.g,
                i_B             = self.h,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
        elif (reg_in == 1 and reg_out == 1):
            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.c,
                i_B             = self.d,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.e,
                i_B             = self.f,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),

                # IOs
                i_A             = self.g,
                i_B             = self.h,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
        else:
            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",

                # IOs
                i_A             = self.a,
                i_B             = self.b,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",

                # IOs
                i_A             = self.c,
                i_B             = self.d,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )
            
            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",

                # IOs
                i_A             = self.e,
                i_B             = self.f,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )

            self.specials += Instance("DSP38",

                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",

                # IOs
                i_A             = self.g,
                i_B             = self.h,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = unsigned,
                i_UNSIGNED_B    = unsigned
            )


# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT20(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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
        
        a0_sign = 1
        a1_sign = 1
        b0_sign = 1
        b1_sign = 1

        if (a_width > k and a_width <= k*2):
            self.a0 = Cat(self.a3[0:k], Replicate(0,2))
            if(unsigned):
                self.a1 = Cat(self.a3[k:a_width], Replicate(0,k*2-a_width+1))
            else:
                a1_sign = 0
                self.a1 = Cat(self.a3[k:a_width], Replicate(self.a3[a_width - 1],k*2-a_width+2))
        if (a_width <= k):
            self.a1 =  Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a3[0:a_width], Replicate(0,k-a_width+1))
            else:
                self.a0 = Cat(self.a3[0:a_width],  Replicate(self.a3[a_width - 1],k-a_width+2))
                a0_sign = 0
        else:
            self.a0 = Signal()
            self.a1 = Signal()
              
        if (b_width > k and b_width <= k*2):
            self.b0 = self.b3[0:k]
            if(unsigned):
                self.b1 = Cat(self.b3[k:b_width], Replicate(0,k*2-b_width+1))
            else:
                b1_sign = 0
                self.b1 = Cat(self.b3[k:b_width], Replicate(self.b3[b_width - 1],k*2-b_width+2))
        if (b_width <= k):
            self.b1 =  Replicate(0,18)
            if(unsigned):
                self.b0 = Cat(self.b3[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b0 = Cat(self.b3[0:b_width],  Replicate(self.b3[b_width - 1],k-b_width+2))
                b0_sign = 0
        else:
            self.b0 = Signal()
            self.b1 = Signal()

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
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            
        elif (reg_in == 1 and reg_out == 1):

            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            
        # Registered Input
        elif (reg_in == 1 and reg_out == 0):
            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
        
        else:
            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            
# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT36(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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
  
        if(a_width > k*2 and a_width <= k*3):
            self.a0 = Cat(self.a3[0:k], Replicate(0,2))
            self.a1 = Cat(self.a3[k:k*2], Replicate(0,2))
            if (unsigned):
                self.a2 = Cat(self.a3[k*2:a_width], Replicate(0,k*3-a_width+1))
            else:
                a2_sign = 0
                self.a2 = Cat(self.a3[k*2:a_width], Replicate(self.a3[a_width - 1],k*3-a_width+2))
        elif (a_width > k and a_width <= k*2):
            self.a2 =  Replicate(0,20)
            self.a0 = Cat(self.a3[0:k], Replicate(0,2))
            if(unsigned):
                self.a1 = Cat(self.a3[k:a_width], Replicate(0,k*2-a_width+1))
            else:
                a1_sign = 0
                self.a1 = Cat(self.a3[k:a_width], Replicate(self.a3[a_width - 1],k*2-a_width+2))
        elif (a_width <= k):
            self.a1 =  Replicate(0,20)
            self.a2 =  Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a3[0:a_width], Replicate(0,k-a_width+1))
            else:
                self.a0 = Cat(self.a3[0:a_width],  Replicate(self.a3[a_width - 1],k-a_width+2))
                a0_sign = 0
        else:
            self.a0 = Signal()
            self.a1 = Signal()
            self.a2 = Signal()

        if(b_width > k*2 and b_width <= k*3):
            self.b0 = self.b3[0:k]
            self.b1 = self.b3[k:k*2]
            if (unsigned):
                self.b2 = Cat(self.b3[k*2:b_width], Replicate(0,k*3-b_width+1))
            else:
                b2_sign = 0
                self.b2 = Cat(self.b3[k*2:b_width], Replicate(self.b3[b_width - 1],k*3-b_width))
        elif (b_width > k and b_width <= k*2):
            self.b2 = Replicate(0,18)
            self.b0 = self.b3[0:k]
            if(unsigned):
                self.b1 = Cat(self.b3[k:b_width], Replicate(0,k*2-b_width+1))
            else:
                b1_sign = 0
                self.b1 = Cat(self.b3[k:b_width], Replicate(self.b3[b_width - 1],k*2-b_width))
        elif (b_width <= k):
            self.b1 =  Replicate(0,18)
            self.b2 =  Replicate(0,18)
            if(unsigned):
                self.b0 = Cat(self.b3[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b0 = Cat(self.b3[0:b_width],  Replicate(self.b3[b_width - 1],k-b_width))
                b0_sign = 0
        else:
            self.b0 = Signal()
            self.b1 = Signal()
            self.b2 = Signal()
        

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
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b0,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b1,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b2,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
        elif (reg_in == 1 and reg_out == 1):
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b0,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b1,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b2,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
        elif (reg_in == 1 and reg_out == 0):
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b0,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b1,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b2,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
        else:
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b0,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b1,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b2,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT54(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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
        a3_sign = 1
        b0_sign = 1
        b1_sign = 1
        b2_sign = 1
        b3_sign = 1     
        
        if(a_width > k*3 and a_width <= k*4):
            self.a0 = Cat(self.a3[0:k], Replicate(0,2))
            self.a1 = Cat(self.a3[k:k*2], Replicate(0,2))
            self.a2 = Cat(self.a3[k*2:k*3], Replicate(0,2))
            if (unsigned):
                self.a4 = Cat(self.a3[k*3:a_width], Replicate(0,k*4-a_width+1))
            else:
                a3_sign = 0
                self.a4 = Cat(self.a3[k*3:a_width], Replicate(self.a3[a_width - 1],k*4-a_width+2))
        elif(a_width > k*2 and a_width <= k*3):
            self.a0 = Cat(self.a3[0:k],  Replicate(0,2))
            self.a1 = Cat(self.a3[k:k*2], Replicate(0,2))
            self.a4 = Replicate(0,20)
            if (unsigned):
                self.a2 = Cat(self.a3[k*2:a_width], Replicate(0,k*3-a_width+1))
            else:
                a2_sign = 0
                self.a2 = Cat(self.a3[k*2:a_width], Replicate(self.a3[a_width - 1],k*3-a_width+2))
        elif (a_width > k and a_width <= k*2):
            self.a2 =  Replicate(0,20)
            self.a4 = Replicate(0,20)
            self.a0 = Cat(self.a3[0:k],  Replicate(0,2))
            if(unsigned):
                self.a1 = Cat(self.a3[k:a_width], Replicate(0,k*2-a_width+1))
            else:
                a1_sign = 0
                self.a1 = Cat(self.a3[k:a_width], Replicate(self.a3[a_width - 1],k*2-a_width+2))
        elif (a_width <= k):
            self.a1 =  Replicate(0,20)
            self.a2 =  Replicate(0,20)
            self.a4 = Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a3[0:a_width], Replicate(0,k-a_width+1))
            else:
                self.a0 = Cat(self.a3[0:a_width],  Replicate(self.a3[a_width - 1],k-a_width+2))
                a0_sign = 0
        else:
            self.a0 = Signal()
            self.a1 = Signal()
            self.a2 = Signal()
            self.a4 = Signal()

        if(b_width > k*3 and b_width <= k*4):
            self.b0 = self.b3[0:k]
            self.b1 = self.b3[k:k*2]
            self.b2 = self.b3[k*2:k*3]
            if (unsigned):
                self.b4 = Cat(self.b3[k*3:b_width], Replicate(0,k*4-b_width+1))
            else:
                b3_sign = 0
                self.b4 = Cat(self.b3[k*3:b_width], Replicate(self.b3[b_width - 1],k*4-b_width))
        elif(b_width > k*2 and b_width <= k*3):
            self.b0 = self.b3[0:k]
            self.b1 = self.b3[k:k*2]
            self.b4 = Replicate(0,18)
            if (unsigned):
                self.b2 = Cat(self.b3[k*2:b_width], Replicate(0,k*3-b_width+1))
            else:
                b2_sign = 0
                self.b2 = Cat(self.b3[k*2:b_width], Replicate(self.b3[b_width - 1],k*3-b_width))
        elif (b_width > k and b_width <= k*2):
            self.b2 =  Replicate(0,18)
            self.b4 = Replicate(0,18)
            self.b0 = self.b3[0:k]
            if(unsigned):
                self.b1 = Cat(self.b3[k:b_width], Replicate(0,k*2-b_width+1))
            else:
                b1_sign = 0
                self.b1 = Cat(self.b3[k:b_width], Replicate(self.b3[b_width - 1],k*2-b_width))
        elif (b_width <= k):
            self.b1 =  Replicate(0,18)
            self.b2 =  Replicate(0,18)
            self.b4 = Replicate(0,18)
            if(unsigned):
                self.b0 = Cat(self.b3[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b0 = Cat(self.b3[0:b_width],  Replicate(self.b3[b_width - 1],k-b_width))
                b0_sign = 0
        else:
            self.b0 = Signal()
            self.b1 = Signal()
            self.b2 = Signal()
            self.b4 = Signal()

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
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b0,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b0,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b1,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b2,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b4,
                o_Z             = self.z10,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b1,
                o_Z             = self.z11,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b1_sign
            )
            
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z12,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b4,
                o_Z             = self.z13,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b2,
                o_Z             = self.z14,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b4,
                o_Z             = self.z15,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b4,
                o_Z             = self.z16,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b3_sign
            )
            
        elif (reg_in == 1 and reg_out == 1):
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b0,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b0,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b1,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b2,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b4,
                o_Z             = self.z10,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b1,
                o_Z             = self.z11,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b1_sign
            )
            
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z12,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b4,
                o_Z             = self.z13,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b2,
                o_Z             = self.z14,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b4,
                o_Z             = self.z15,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b4,
                o_Z             = self.z16,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b3_sign
            )
            
        elif (reg_in == 1 and reg_out == 0):
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b0,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b0,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b1,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b2,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b4,
                o_Z             = self.z10,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b1,
                o_Z             = self.z11,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z12,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b4,
                o_Z             = self.z13,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b2,
                o_Z             = self.z14,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b4,
                o_Z             = self.z15,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b4,
                o_Z             = self.z16,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b3_sign
            )
        else:
            self.specials += Instance("DSP38",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_DSP_MODE     =  "MULTIPLY",
                    p_OUTPUT_REG_EN = "FALSE",
                    p_INPUT_REG_EN = "FALSE",
                    # IOs
                    i_A             = self.a0,
                    i_B             = self.b0,
                    o_Z             = self.z1,  
                    i_FEEDBACK      = 0,
                    i_UNSIGNED_A    = a0_sign,
                    i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b0,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b0,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a4,
                i_B             = self.b0,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b1,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b2,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b4,
                o_Z             = self.z10,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a4,
                i_B             = self.b1,
                o_Z             = self.z11,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z12,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b4,
                o_Z             = self.z13,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a4,
                i_B             = self.b2,
                o_Z             = self.z14,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b4,
                o_Z             = self.z15,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a4,
                i_B             = self.b4,
                o_Z             = self.z16,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b3_sign
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT20_pipeline(Module):
    def __init__(self, a_width, b_width, equation, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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

        a0_sign = 1
        a1_sign = 1
        b0_sign = 1
        b1_sign = 1

        if (a_width > k and a_width <= k*2):
          if(unsigned):
              self.a0 = Cat(self.a[0:k], Replicate(0, 2))
              self.a1 = Cat(self.a[k:a_width], Replicate(0,k*2-a_width+1))
          else:
              self.a0 = Cat(self.a[0:k], Replicate(0, 3))
              a1_sign = 0
              self.a1 = Cat(self.a[k:a_width], Replicate(self.a[a_width - 1],k*2-a_width+3))
        if (a_width <= k):
            self.a1 =  Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a[0:a_width], Replicate(0,k-a_width+1))
            else:
                self.a0 = Cat(self.a[0:a_width],  Replicate(self.a[a_width - 1],k-a_width+3))
                a0_sign = 0
        else:
            self.a0 = Signal()
            self.a1 = Signal()
              
        if (b_width > k and b_width <= k*2):
          if(unsigned):
              self.b0 = self.b[0:k]
              self.b1 = Cat(self.b[k:b_width], Replicate(0,k*2-b_width+1))
          else:
              self.b0 = Cat(self.b[0:k], Replicate(0,1))
              b1_sign = 0
              self.b1 = Cat(self.b[k:b_width], Replicate(self.b[b_width - 1],k*2-b_width+1))
        if (b_width <= k):
            self.b1 =  Replicate(0,18)
            if(unsigned):
                self.b0 = Cat(self.b[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b0 = Cat(self.b[0:b_width],  Replicate(self.b[b_width - 1],k-b_width+1))
                b0_sign = 0
        else:
            self.b0 = Signal()
            self.b1 = Signal()
        
        self.a3 = Signal(bits_sign=(19,True))
        self.b3 = Signal(bits_sign=(19,True))
        self.comb += self.a3.eq(Mux(self.sum != 2, self.a0, self.a1))
        self.comb += self.b3.eq(Mux(self.sum != 2, self.b1, self.b0))
        self.unsigneda = Signal(1)
        self.unsignedb = Signal(1)
        self.comb += self.unsigneda.eq(Mux(self.sum != 2, a0_sign, a1_sign))
        self.comb += self.unsignedb.eq(Mux(self.sum != 2, b1_sign, b0_sign))

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
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY",
            p_OUTPUT_REG_EN = "TRUE",
            p_INPUT_REG_EN  = "TRUE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a0,
            i_B             = self.b0,
            o_Z             = self.z1,  
            i_FEEDBACK      = 0,
            i_UNSIGNED_A    = a0_sign,
            i_UNSIGNED_B    = b0_sign
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a3,
            i_B             = self.b3,
            o_Z             = self.z3,  
            i_FEEDBACK      = self.fb,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.unsigneda,
            i_UNSIGNED_B    = self.unsignedb,
            i_SUBTRACT      = 0
        )
        # Module instance.
        # ----------------
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY",
            p_OUTPUT_REG_EN = "TRUE",
            p_INPUT_REG_EN  = "TRUE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a1,
            i_B             = self.b1,
            o_Z             = self.z2,  
            i_FEEDBACK      = 0,
            i_UNSIGNED_A    = a1_sign,
            i_UNSIGNED_B    = b1_sign
        )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT36_pipeline(Module):
    def __init__(self, a_width, b_width, equation,unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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
        
        a0_sign = 1
        a1_sign = 1
        a2_sign = 1
        b0_sign = 1
        b1_sign = 1
        b2_sign = 1
  
        if(a_width > k*2 and a_width <= k*3):
            if (unsigned):
                self.a1 = Cat(self.a[0:k], Replicate(0,2))
                self.a2 = Cat(self.a[k:k*2], Replicate(0,2))
                self.a3 = Cat(self.a[k*2:a_width], Replicate(0,k*3-a_width+1))
            else:
                self.a1 = Cat(self.a[0:k], Replicate(0,3))
                self.a2 = Cat(self.a[k:k*2], Replicate(0,3))
                a2_sign = 0
                self.a3 = Cat(self.a[k*2:a_width], Replicate(self.a[a_width - 1],k*3-a_width+3))
        elif (a_width > k and a_width <= k*2):
            self.a3 =  Replicate(0,20)
            if(unsigned):
                self.a1 = Cat(self.a[0:k], Replicate(0,2))
                self.a2 = Cat(self.a[k:a_width], Replicate(0,k*2-a_width+1))
            else:
                self.a1 = Cat(self.a[0:k], Replicate(0,3))
                a1_sign = 0
                self.a2 = Cat(self.a[k:a_width], Replicate(self.a[a_width - 1],k*2-a_width+3))
        elif (a_width <= k):
            self.a2 =  Replicate(0,20)
            self.a3 =  Replicate(0,20)
            if(unsigned):
                self.a1 = Cat(self.a[0:a_width], Replicate(0,k-a_width+1))
            else:
                self.a1 = Cat(self.a[0:a_width],  Replicate(self.a[a_width - 1],k-a_width+3))
                a0_sign = 0
        else:
            self.a1 = Signal()
            self.a2 = Signal()
            self.a3 = Signal()
        
        if(b_width > k*2 and b_width <= k*3):
            if (unsigned):
                self.b1 = self.b[0:k]
                self.b2 = self.b[k:k*2]
                self.b3 = Cat(self.b[k*2:b_width], Replicate(0,k*3-b_width+1))
            else:
                self.b1 = Cat(self.b[0:k], Replicate (0, 1))
                self.b2 = Cat(self.b[k:k*2], Replicate (0, 1))
                b2_sign = 0
                self.b3 = Cat(self.b[k*2:b_width], Replicate(self.b[b_width - 1],k*3-b_width+1))
        elif (b_width > k and b_width <= k*2):
            self.b3 = Replicate(0,20)
            if(unsigned):
                self.b1 = self.b[0:k]
                self.b2 = Cat(self.b[k:b_width], Replicate(0,k*2-b_width+1))
            else:
                self.b1 = Cat(self.b[0:k], Replicate(0 , 1))
                b1_sign = 0
                self.b2 = Cat(self.b[k:b_width], Replicate(self.b[b_width - 1],k*2-b_width+1))
        elif (b_width <= k):
            self.b2 =  Replicate(0,18)
            self.b3 =  Replicate(0,18)
            if(unsigned):
                self.b1 = Cat(self.b[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b1 = Cat(self.b[0:b_width],  Replicate(self.b[b_width - 1],k-b_width+1))
                b0_sign = 0
        else:
            self.b1 = Signal()
            self.b2 = Signal()
            self.b3 = Signal()

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
        
        self.a_2_sign = Signal(1, reset = 1)
        self.a_2 = Signal(bits_sign=(k+1,True))
        self.comb += self.a_2.eq(Mux(self.sum == 3, self.a1, self.a2))
        self.comb += self.a_2_sign.eq(Mux(self.sum == 3, a0_sign, a1_sign))
        self.b_2 = Signal(bits_sign=(k+1,True))
        self.b_2_sign = Signal(1, reset = 1)
        self.comb += self.b_2.eq(Mux(self.sum == 3, self.b2, self.b1))
        self.comb += self.b_2_sign.eq(Mux(self.sum == 3, b1_sign, b0_sign))
        self.a_4 = Signal(bits_sign=(k+1,True))
        self.comb += self.a_4.eq(Mux(self.sum == 3, self.a2, self.a3))
        self.b_4 = Signal(bits_sign=(k+1,True))
        self.comb += self.b_4.eq(Mux(self.sum == 3, self.b3, self.b2))
        self.comb += self.fb_del.eq(Mux(self.sum != 3, 1, 0))
        self.a_3 = Signal(bits_sign=(k+1,True))
        self.b_3 = Signal(bits_sign=(k+1,True))

        
        self.unsigneda_3 = Signal(1, reset = 1)
        self.unsignedb_3 = Signal(1, reset = 1)
        self.unsigneda_4 = Signal(1, reset = 1)
        self.unsignedb_4 = Signal(1, reset = 1)
        self.comb += self.unsigneda_4.eq(Mux(self.sum == 3, a1_sign, a2_sign))
        self.comb += self.unsignedb_4.eq(Mux(self.sum == 3, b2_sign, b1_sign))
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
                self.unsigneda_3.eq(a0_sign),
                self.b_3.eq(self.b3),
                self.unsignedb_3.eq(b2_sign),
            ).Elif(self.sum == 4,
                self.a_3.eq(self.a1),
                self.unsigneda_3.eq(a0_sign),
                self.b_3.eq(self.b3),
                self.unsignedb_3.eq(b2_sign),
            ).Elif(self.sum == 2,
                self.a_3.eq(self.a2),
                self.unsigneda_3.eq(a1_sign),
                self.b_3.eq(self.b2),
                self.unsignedb_3.eq(b1_sign),
            ).Else(
                self.a_3.eq(self.a3),
                self.unsigneda_3.eq(a2_sign),
                self.b_3.eq(self.b1),
                self.unsignedb_3.eq(b0_sign),
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
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY",
            p_OUTPUT_REG_EN = "TRUE",
            p_INPUT_REG_EN  = "TRUE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a1,
            i_B             = self.b1,
            o_Z             = self.z1,  
            i_FEEDBACK      = 0,
            i_UNSIGNED_A    = a0_sign,
            i_UNSIGNED_B    = b0_sign
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a_2,
            i_B             = self.b_2,
            o_Z             = self.z2,  
            i_FEEDBACK      = self.fb_del,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.a_2_sign,
            i_UNSIGNED_B    = self.b_2_sign,
            i_SUBTRACT      = 0
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a_3,
            i_B             = self.b_3,
            o_Z             = self.z3,  
            i_FEEDBACK      = self.fb,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.unsigneda_3,
            i_UNSIGNED_B    = self.unsignedb_3,
            i_SUBTRACT      = 0
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a_4,
            i_B             = self.b_4,
            o_Z             = self.z4,  
            i_FEEDBACK      = self.fb_del,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.unsigneda_4,
            i_UNSIGNED_B    = self.unsignedb_4,
            i_SUBTRACT      = 0
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY",
            p_OUTPUT_REG_EN = "TRUE",
            p_INPUT_REG_EN  = "TRUE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a3,
            i_B             = self.b3,
            o_Z             = self.z5,  
            i_FEEDBACK      = 0,
            i_UNSIGNED_A    = a2_sign,
            i_UNSIGNED_B    = b2_sign
        )
        

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT54_pipeline(Module):
    def __init__(self, a_width, b_width, equation, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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

        a0_sign = 1
        a1_sign = 1
        a2_sign = 1
        a3_sign = 1
        b0_sign = 1
        b1_sign = 1
        b2_sign = 1
        b3_sign = 1     
        
        if(a_width > k*3 and a_width <= k*4):
            if (unsigned):
                self.a0 = Cat(self.a[0:k], Replicate (0, 2))
                self.a1 = Cat(self.a[k:k*2], Replicate (0, 2))
                self.a2 = Cat(self.a[k*2:k*3], Replicate (0, 2))
                self.a3 = Cat(self.a[k*3:a_width], Replicate(0,k*4-a_width+1))
            else:
                self.a0 = Cat(self.a[0:k], Replicate (0, 3))
                self.a1 = Cat(self.a[k:k*2], Replicate (0, 3))
                self.a2 = Cat(self.a[k*2:k*3], Replicate (0, 3))
                a3_sign = 0
                self.a3 = Cat(self.a[k*3:a_width], Replicate(self.a[a_width - 1],k*4-a_width+3))
        elif(a_width > k*2 and a_width <= k*3):
            self.a3 = Replicate(0,20)
            if (unsigned):
                self.a0 = Cat(self.a[0:k], Replicate(0, 2))
                self.a1 = Cat(self.a[k:k*2], Replicate(0, 2))
                self.a2 = Cat(self.a[k*2:a_width], Replicate(0,k*3-a_width+1))
            else:
                self.a0 = Cat(self.a[0:k], Replicate(0, 3))
                self.a1 = Cat(self.a[k:k*2], Replicate(0, 3))
                a2_sign = 0
                self.a2 = Cat(self.a[k*2:a_width], Replicate(self.a[a_width - 1],k*3-a_width+3))
        elif (a_width > k and a_width <= k*2):
            self.a2 =  Replicate(0,20)
            self.a3 = Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a[0:k], Replicate(0 ,2))
                self.a1 = Cat(self.a[k:a_width], Replicate(0,k*2-a_width+1))
            else:
                self.a0 = Cat(self.a[0:k], Replicate(0 ,3))
                a1_sign = 0
                self.a1 = Cat(self.a[k:a_width], Replicate(self.a[a_width - 1],k*2-a_width+3))
        elif (a_width <= k):
            self.a1 =  Replicate(0,20)
            self.a2 =  Replicate(0,20)
            self.a3 = Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a[0:a_width], Replicate(0,k-a_width+1))
            else:
                self.a0 = Cat(self.a[0:a_width],  Replicate(self.a[a_width - 1],k-a_width+3))
                a0_sign = 0
        else:
            self.a0 = Signal()
            self.a1 = Signal()
            self.a2 = Signal()
            self.a3 = Signal()

        if(b_width > k*3 and b_width <= k*4):
            if (unsigned):
                self.b0 = self.b[0:k]
                self.b1 = self.b[k:k*2]
                self.b2 = self.b[k*2:k*3]
                self.b3 = Cat(self.b[k*3:b_width], Replicate(0,k*4-b_width+1))
            else:
                self.b0 = Cat(self.b[0:k], Replicate(0, 1))
                self.b1 = Cat(self.b[k:k*2], Replicate(0, 1))
                self.b2 = Cat(self.b[k*2:k*3], Replicate(0, 1))
                b3_sign = 0
                self.b3 = Cat(self.b[k*3:b_width], Replicate(self.b[b_width - 1],k*4-b_width+1))
        elif(b_width > k*2 and b_width <= k*3):
            self.b3 = Replicate(0,18)
            if (unsigned):
                self.b0 = self.b[0:k]
                self.b1 = self.b[k:k*2]
                self.b2 = Cat(self.b[k*2:b_width], Replicate(0,k*3-b_width+1))
            else:
                self.b0 = Cat(self.b[0:k], Replicate (0, 1))
                self.b1 = Cat(self.b[k:k*2], Replicate (0, 1))
                b2_sign = 0
                self.b2 = Cat(self.b[k*2:b_width], Replicate(self.b[b_width - 1],k*3-b_width+1))
        elif (b_width > k and b_width <= k*2):
          self.b2 =  Replicate(0,18)
          self.b3 = Replicate(0,18)
          if(unsigned):
              self.b0 = self.b[0:k]
              self.b1 = Cat(self.b[k:b_width], Replicate(0,k*2-b_width+1))
          else:
              self.b0 = Cat(self.b[0:k], Replicate(0 ,1))
              b1_sign = 0
              self.b1 = Cat(self.b[k:b_width], Replicate(self.b[b_width - 1],k*2-b_width+1))
        elif (b_width <= k):
            self.b1 =  Replicate(0,18)
            self.b2 =  Replicate(0,18)
            self.b3 = Replicate(0,18)
            if(unsigned):
                self.b0 = Cat(self.b[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b0 = Cat(self.b[0:b_width],  Replicate(self.b[b_width - 1],k-b_width+1))
                b0_sign = 0
        else:
            self.b0 = Signal()
            self.b1 = Signal()
            self.b2 = Signal()
            self.b3 = Signal()

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
        self.a_2_sign = Signal(1, reset = 1)
        self.comb += self.a_2_sign.eq(Mux(self.sum < 4, a1_sign, a0_sign))
        self.b_2 = Signal(bits_sign=(k+1,True))
        self.comb += self.b_2.eq(Mux(self.sum < 4, self.b0, self.b1))
        self.b_2_sign = Signal(1, reset = 1)
        self.comb += self.b_2_sign.eq(Mux(self.sum < 4, b0_sign, b1_sign))
        self.a_6 = Signal(bits_sign=(k+1,True))
        self.comb += self.a_6.eq(Mux(self.sum < 4, self.a2, self.a3))
        self.b_6 = Signal(bits_sign=(k+1,True))
        self.unsigned_a4 = Signal(1, reset = 1)
        self.unsigned_a5 = Signal(1, reset = 1)
        self.unsigned_b4 = Signal(1, reset = 1)
        self.unsigned_b5 = Signal(1, reset = 1)
        self.unsigned_a6 = Signal(1, reset = 1)
        self.comb += self.unsigned_a6.eq(Mux(self.sum < 4, a2_sign, a3_sign))
        self.unsigned_b6 = Signal(1, reset = 1)
        self.comb += self.unsigned_b6.eq(Mux(self.sum < 4, b3_sign, b2_sign))
        self.comb += self.b_6.eq(Mux(self.sum < 4, self.b3, self.b2))
        self.a_3 = Signal(bits_sign=(k+1,True))
        self.b_3 = Signal(bits_sign=(k+1,True))
        self.a_4 = Signal(bits_sign=(k+1,True))
        self.b_4 = Signal(bits_sign=(k+1,True))
        self.a_5 = Signal(bits_sign=(k+1,True))
        self.b_5 = Signal(bits_sign=(k+1,True))
        self.a_3_sign = Signal(1, reset = 1)
        self.b_3_sign = Signal(1, reset = 1)
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
                self.a_3_sign.eq(a0_sign),
                self.b_3.eq(self.b2),
                self.b_3_sign.eq(b2_sign),
                self.a_5.eq(self.a1),
                self.b_5.eq(self.b3),
                self.unsigned_b5.eq(b3_sign),
                self.unsigned_a5.eq(a1_sign)
            ).Elif(self.sum == 3,
                self.a_3.eq(self.a1),
                self.b_3.eq(self.b1),
                self.a_3_sign.eq(a1_sign),
                self.b_3_sign.eq(b1_sign),
                self.a_5.eq(self.a2),
                self.b_5.eq(self.b2),
                self.unsigned_b5.eq(b2_sign),
                self.unsigned_a5.eq(a2_sign)
            ).Else(
                self.a_3.eq(self.a2),
                self.a_3_sign.eq(a2_sign),
                self.b_3.eq(self.b0),
                self.b_3_sign.eq(b0_sign),
                self.a_5.eq(self.a3),
                self.b_5.eq(self.b1),
                self.unsigned_b5.eq(b1_sign),
                self.unsigned_a5.eq(a3_sign)
            ),If(self.sum < 2,
                self.a_4.eq(self.a0),
                self.b_4.eq(self.b3),
                self.unsigned_a4.eq(a0_sign),
                self.unsigned_b4.eq(b3_sign)
            ).Elif(self.sum == 5,
                self.a_4.eq(self.a0),
                self.b_4.eq(self.b3),
                self.unsigned_a4.eq(a0_sign),
                self.unsigned_b4.eq(b3_sign)
            ).Elif(self.sum == 2,
                self.a_4.eq(self.a1),
                self.b_4.eq(self.b2),
                self.unsigned_a4.eq(a1_sign),
                self.unsigned_b4.eq(b2_sign)
            ).Elif(self.sum == 3,
                self.a_4.eq(self.a2),
                self.b_4.eq(self.b1),
                self.unsigned_a4.eq(a2_sign),
                self.unsigned_b4.eq(b1_sign)
            ).Else(
                self.a_4.eq(self.a3),
                self.b_4.eq(self.b0),
                self.unsigned_a4.eq(a3_sign),
                self.unsigned_b4.eq(b0_sign)
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
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY",
            p_OUTPUT_REG_EN = "TRUE",
            p_INPUT_REG_EN  = "TRUE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a0,
            i_B             = self.b0,
            o_Z             = self.z1,  
            i_FEEDBACK      = 0,
            i_UNSIGNED_A    = a0_sign,
            i_UNSIGNED_B    = b0_sign
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a_2,
            i_B             = self.b_2,
            o_Z             = self.z2,  
            i_FEEDBACK      = self.fb2,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.a_2_sign,
            i_UNSIGNED_B    = self.b_2_sign,
            i_SUBTRACT      = 0
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a_3,
            i_B             = self.b_3,
            o_Z             = self.z3,  
            i_FEEDBACK      = self.fb1,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.a_3_sign,
            i_UNSIGNED_B    = self.b_3_sign,
            i_SUBTRACT      = 0
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a_4,
            i_B             = self.b_4,
            o_Z             = self.z4,  
            i_FEEDBACK      = self.fb,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.unsigned_a4,
            i_UNSIGNED_B    = self.unsigned_b4,
            i_SUBTRACT      = 0
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a_5,
            i_B             = self.b_5,
            o_Z             = self.z5,  
            i_FEEDBACK      = self.fb1,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.unsigned_a5,
            i_UNSIGNED_B    = self.unsigned_b5,
            i_SUBTRACT      = 0
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY_ACCUMULATE",
            p_OUTPUT_REG_EN = "FALSE",
            p_INPUT_REG_EN  = "FALSE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a_6,
            i_B             = self.b_6,
            o_Z             = self.z6,  
            i_FEEDBACK      = self.fb2,
            i_LOAD_ACC      = 1,
            i_ROUND         = 0,
            i_SATURATE      = 0,
            i_SHIFT_RIGHT   = 0,
            i_UNSIGNED_A    = self.unsigned_a6,
            i_UNSIGNED_B    = self.unsigned_b6,
            i_SUBTRACT      = 0
        )
        self.specials += Instance("DSP38",
            # Parameters.
            # -----------
            # Mode Bits to configure DSP 
            p_DSP_MODE      =  "MULTIPLY",
            p_OUTPUT_REG_EN = "TRUE",
            p_INPUT_REG_EN  = "TRUE",
            # Reset
            i_CLK           = ClockSignal(),
            i_RESET        = ResetSignal(),
            # IOs
            i_A             = self.a3,
            i_B             = self.b3,
            o_Z             = self.z7,  
            i_FEEDBACK      = 0,
            i_UNSIGNED_A    = a3_sign,
            i_UNSIGNED_B    = b3_sign
        )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT20_enhance(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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

        a0_sign = 1
        a1_sign = 1
        b0_sign = 1
        b1_sign = 1

        if (a_width > k and a_width <= k*2):
          if(unsigned):
              self.a0 = Cat(self.a[0:k], Replicate(0,3))
              self.a1 = Cat(self.a[k:a_width], Replicate(0,k*2-a_width+3))
          else:
              self.a0 = Cat(self.a[0:k], Replicate(0,4))
              a1_sign = 0
              self.a1 = Cat(self.a[k:a_width], Replicate(self.a[a_width - 1],k*2-a_width+4))
        if (a_width <= k):
            self.a1 =  Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a[0:a_width], Replicate(0,k-a_width+1))
            else:
                self.a0 = Cat(self.a[0:a_width],  Replicate(self.a[a_width - 1],k-a_width+4))
                a0_sign = 0
        else:
            self.a0 = Signal()
            self.a1 = Signal()
              
        if (b_width > k and b_width <= k*2):
          if(unsigned):
              self.b0 = Cat(self.b[0:k], Replicate(0, 1))
              self.b1 = Cat(self.b[k:b_width], Replicate(0,k*2-b_width+1))
          else:
              b1_sign = 0
              self.b0 = Cat(self.b[0:k], Replicate(0, 2))
              self.b1 = Cat(self.b[k:b_width], Replicate(self.b[b_width - 1],k*2-b_width+2))
        if (b_width <= k):
            self.b1 =  Replicate(0,18)
            if(unsigned):
                self.b0 = Cat(self.b[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b0 = Cat(self.b[0:b_width],  Replicate(self.b[b_width - 1],k-b_width+2))
                b0_sign = 0
        else:
            self.b0 = Signal()
            self.b1 = Signal()
        
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
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx, Replicate(self.dx[17], 2)),
                i_B             = self.dy,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
        elif (reg_in == 1 and reg_out == 1):
            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx, Replicate(self.dx[17], 2)),
                i_B             = self.dy,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
        # Registered Input
        elif (reg_in == 1 and reg_out == 0):
            
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx, Replicate(self.dx[17], 2)),
                i_B             = self.dy,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
        else:
             # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx, Replicate(self.dx[17], 2)),
                i_B             = self.dy,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            # Module instance.
            # ----------------
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )

# RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT36_enhance(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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
        
        a0_sign = 1
        a1_sign = 1
        a2_sign = 1
        b0_sign = 1
        b1_sign = 1
        b2_sign = 1
  
        if(a_width > k*2 and a_width <= k*3):
            if (unsigned):
                self.a0 = Cat(self.a[0:k], Replicate(0,3))
                self.a1 = Cat(self.a[k:k*2], Replicate(0,3))
                self.a2 = Cat(self.a[k*2:a_width], Replicate(0,k*3-a_width+3))
            else:
                self.a0 = Cat(self.a[0:k], Replicate(0,4))
                self.a1 = Cat(self.a[k:k*2], Replicate(0,4))
                a2_sign = 0
                self.a2 = Cat(self.a[k*2:a_width], Replicate(self.a[a_width - 1],k*3-a_width+4))
        elif (a_width > k and a_width <= k*2):
            self.a2 =  Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a[0:k], Replicate(0,3))
                self.a1 = Cat(self.a[k:a_width], Replicate(0,k*2-a_width+3))
            else:
                self.a0 = Cat(self.a[0:k], Replicate(0,4))
                a1_sign = 0
                self.a1 = Cat(self.a[k:a_width], Replicate(self.a[a_width - 1],k*2-a_width+4))
        elif (a_width <= k):
            self.a1 =  Replicate(0,20)
            self.a2 =  Replicate(0,20)
            if(unsigned):
                self.a0 = Cat(self.a[0:a_width], Replicate(0,k-a_width+3))
            else:
                self.a0 = Cat(self.a[0:a_width],  Replicate(self.a[a_width - 1],k-a_width+4))
                a0_sign = 0
        else:
            self.a0 = Signal()
            self.a1 = Signal()
            self.a2 = Signal()
        
        if(b_width > k*2 and b_width <= k*3):
            if (unsigned):
                self.b0 = Cat(self.b[0:k], Replicate(0, 1))
                self.b1 = Cat(self.b[k:k*2], Replicate(0, 1))
                self.b2 = Cat(self.b[k*2:b_width], Replicate(0,k*3-b_width+1))
            else:
                self.b0 = Cat(self.b[0:k], Replicate(0, 2))
                self.b1 = Cat(self.b[k:k*2], Replicate(0, 2))
                b2_sign = 0
                self.b2 = Cat(self.b[k*2:b_width], Replicate(self.b[b_width - 1],k*3-b_width+2))
        elif (b_width > k and b_width <= k*2):
            self.b2 = Replicate(0,18)
            if(unsigned):
                self.b0 = Cat(self.b[0:k], Replicate(0,1))
                self.b1 = Cat(self.b[k:b_width], Replicate(0,k*2-b_width+1))
            else:
                self.b0 = Cat(self.b[0:k], Replicate(0,2))
                b1_sign = 0
                self.b1 = Cat(self.b[k:b_width], Replicate(self.b[b_width - 1],k*2-b_width+2))
        elif (b_width <= k):
            self.b1 =  Replicate(0,18)
            self.b2 =  Replicate(0,18)
            if(unsigned):
                self.b0 = Cat(self.b[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b0 = Cat(self.b[0:b_width],  Replicate(self.b[b_width - 1],k-b_width+2))
                b0_sign = 0
        else:
            self.b0 = Signal()
            self.b1 = Signal()
            self.b2 = Signal()

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

        self.comb += self.dx1.eq(self.a2 - self.a1)
        self.comb += self.dx2.eq(self.a1 - self.a0)
        self.comb += self.dx3.eq(self.a2 - self.a0)

        self.comb += self.dy1.eq(self.b2 - self.b1)
        self.comb += self.dy2.eq(self.b1 - self.b0)
        self.comb += self.dy3.eq(self.b2 - self.b0)

        self.z = Signal(a_width + b_width)


        self.comb += self.z.eq((self.z3 << 4*k) + ((self.z3 + self.z2 - self.z4) << 3*k) + 
        ((self.z3 + self.z2 + self.z1 - self.z6) << 2*k) + ((self.z2 + self.z1 - self.z5) << k) + self.z1)

        # Module instance.
        # ----------------
        if (reg_in == 0 and reg_out == 1):
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_B             = self.dy1,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_B             = self.dy2,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_B             = self.dy3,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
        elif (reg_in == 1 and reg_out == 1):
            self.specials += Instance("DSP38",
               # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_B             = self.dy1,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_B             = self.dy2,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_B             = self.dy3,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
        elif (reg_in == 1 and reg_out == 0):
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_B             = self.dy1,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_B             = self.dy2,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_B             = self.dy3,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
        else:
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a0,
                i_B             = self.b0,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z3,
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits tcdo configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_B             = self.dy1,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_B             = self.dy2,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_B             = self.dy3,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )

# # RS_DSP_MULT ---------------------------------------------------------------------------------------
class RS_DSP_MULT54_enhance(Module):
    def __init__(self, a_width, b_width, equation, reg_in, reg_out, unsigned, ):

        # Get Parameters.
        # ---------------------        
        self.logger = logging.getLogger("\tDSP38")
        
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
        
        a0_sign = 1
        a1_sign = 1
        a2_sign = 1
        a3_sign = 1
        b0_sign = 1
        b1_sign = 1
        b2_sign = 1
        b3_sign = 1     
        
        if(a_width > k*3 and a_width <= k*4):
            if (unsigned):
                self.a1 = Cat(self.a[0:k], Replicate(0,3))
                self.a2 = Cat(self.a[k:k*2], Replicate(0,3))
                self.a3 = Cat(self.a[k*2:k*3], Replicate(0,3))
                self.a4 = Cat(self.a[k*3:a_width], Replicate(0,k*4-a_width+3))
            else:
                self.a1 = Cat(self.a[0:k], Replicate(0,4))
                self.a2 = Cat(self.a[k:k*2], Replicate(0,4))
                self.a3 = Cat(self.a[k*2:k*3], Replicate(0,4))
                a3_sign = 0
                self.a4 = Cat(self.a[k*3:a_width], Replicate(self.a[a_width - 1],k*4-a_width+4))
        elif(a_width > k*2 and a_width <= k*3):
            self.a4 = Replicate(0,20)
            if (unsigned):
                self.a1 = Cat(self.a[0:k],  Replicate(0,3))
                self.a2 = Cat(self.a[k:k*2], Replicate(0,3))
                self.a3 = Cat(self.a[k*2:a_width], Replicate(0,k*3-a_width+3))
            else:
                self.a1 = Cat(self.a[0:k],  Replicate(0,4))
                self.a2 = Cat(self.a[k:k*2], Replicate(0,4))
                a2_sign = 0
                self.a3 = Cat(self.a[k*2:a_width], Replicate(self.a[a_width - 1],k*3-a_width+4))
        elif (a_width > k and a_width <= k*2):
            self.a3 =  Replicate(0,20)
            self.a4 = Replicate(0,20)
            if(unsigned):
                self.a1 = Cat(self.a[0:k],  Replicate(0,3))
                self.a2 = Cat(self.a[k:a_width], Replicate(0,k*2-a_width+3))
            else:
                self.a1 = Cat(self.a[0:k],  Replicate(0,4))
                a1_sign = 0
                self.a2 = Cat(self.a[k:a_width], Replicate(self.a[a_width - 1],k*2-a_width+4))
        elif (a_width <= k):
            self.a2 =  Replicate(0,20)
            self.a3 =  Replicate(0,20)
            self.a4 = Replicate(0,20)
            if(unsigned):
                self.a1 = Cat(self.a[0:a_width], Replicate(0,k-a_width+3))
            else:
                self.a1 = Cat(self.a[0:a_width],  Replicate(self.a[a_width - 1],k-a_width+4))
                a0_sign = 0
        else:
            self.a1 = Signal()
            self.a2 = Signal()
            self.a3 = Signal()
            self.a4 = Signal()

        if(b_width > k*3 and b_width <= k*4):
            if (unsigned):
                self.b1 = Cat(self.b[0:k], Replicate(0, 1))
                self.b2 = Cat(self.b[k:k*2], Replicate(0, 1))
                self.b3 = Cat(self.b[k*2:k*3], Replicate(0, 1))
                self.b4 = Cat(self.b[k*3:b_width], Replicate(0,k*4-b_width+1))
            else:
                self.b1 = Cat(self.b[0:k], Replicate(0, 2))
                self.b2 = Cat(self.b[k:k*2], Replicate(0, 2))
                self.b3 = Cat(self.b[k*2:k*3], Replicate(0, 2))
                b3_sign = 0
                self.b4 = Cat(self.b[k*3:b_width], Replicate(self.b[b_width - 1],k*4-b_width+2))
        elif(b_width > k*2 and b_width <= k*3):
            self.b4 = Replicate(0,18)
            if (unsigned):
                self.b1 = Cat(self.b[0:k], Replicate(0, 1))
                self.b2 = Cat(self.b[k:k*2], Replicate(0, 1))
                self.b3 = Cat(self.b[k*2:b_width], Replicate(0,k*3-b_width+1))
            else:
                self.b1 = Cat(self.b[0:k], Replicate(0, 1))
                self.b2 = Cat(self.b[k:k*2], Replicate(0, 1))
                b2_sign = 0
                self.b3 = Cat(self.b[k*2:b_width], Replicate(self.b[b_width - 1],k*3-b_width+2))
        elif (b_width > k and b_width <= k*2):
            self.b3 =  Replicate(0,18)
            self.b4 = Replicate(0,18)
            if(unsigned):
                self.b1 = Cat(self.b[0:k], Replicate(0, 1))
                self.b2 = Cat(self.b[k:b_width], Replicate(0,k*2-b_width+1))
            else:
                self.b1 = Cat(self.b[0:k], Replicate(0, 2))
                b1_sign = 0
                self.b2 = Cat(self.b[k:b_width], Replicate(self.b[b_width - 1],k*2-b_width+2))
        elif (b_width <= k):
            self.b2 =  Replicate(0,18)
            self.b3 =  Replicate(0,18)
            self.b4 = Replicate(0,18)
            if(unsigned):
                self.b1 = Cat(self.b[0:b_width], Replicate(0,k-b_width+1))
            else:
                self.b1 = Cat(self.b[0:b_width],  Replicate(self.b[b_width - 1],k-b_width+2))
                b0_sign = 0
        else:
            self.b1 = Signal()
            self.b2 = Signal()
            self.b3 = Signal()
            self.b4 = Signal()

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
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a3,
                i_B             = self.b3,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b4,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx1,
                i_B             = self.dy1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx2,
                i_B             = self.dy2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx3,
                i_B             = self.dy3,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx4,
                i_B             = self.dy4,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0 
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx5,
                i_B             = self.dy5,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "FALSE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx6,
                i_B             = self.dy6,
                o_Z             = self.z10,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
        elif (reg_in == 1 and reg_out == 1):
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a3,
                i_B             = self.b3,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b4,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx1,
                i_B             = self.dy1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx2,
                i_B             = self.dy2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx3,
                i_B             = self.dy3,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx4,
                i_B             = self.dy4,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx5,
                i_B             = self.dy5,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "TRUE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx6,
                i_B             = self.dy6,
                o_Z             = self.z10,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
        elif (reg_in == 1 and reg_out == 0):
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a1,
                i_B             = self.b1,
                o_Z             = self.z1,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a0_sign,
                i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a3,
                i_B             = self.b3,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.a4,
                i_B             = self.b4,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx1,
                i_B             = self.dy1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx2,
                i_B             = self.dy2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx3,
                i_B             = self.dy3,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx4,
                i_B             = self.dy4,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx5,
                i_B             = self.dy5,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "TRUE",
                # Reset
                i_CLK           = ClockSignal(),
                i_RESET        = ResetSignal(),
                # IOs
                i_A             = self.dx6,
                i_B             = self.dy6,
                o_Z             = self.z10,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
        else:
            self.specials += Instance("DSP38",
                    # Parameters.
                    # -----------
                    # Mode Bits to configure DSP 
                    p_DSP_MODE     =  "MULTIPLY",
                    p_OUTPUT_REG_EN = "FALSE",
                    p_INPUT_REG_EN = "FALSE",
                    # IOs
                    i_A             = self.a1,
                    i_B             = self.b1,
                    o_Z             = self.z1,  
                    i_FEEDBACK      = 0,
                    i_UNSIGNED_A    = a0_sign,
                    i_UNSIGNED_B    = b0_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a2,
                i_B             = self.b2,
                o_Z             = self.z2,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a1_sign,
                i_UNSIGNED_B    = b1_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a3,
                i_B             = self.b3,
                o_Z             = self.z3,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a2_sign,
                i_UNSIGNED_B    = b2_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = self.a4,
                i_B             = self.b4,
                o_Z             = self.z4,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = a3_sign,
                i_UNSIGNED_B    = b3_sign
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx1, Replicate(self.dx1[17], 2)),
                i_B             = self.dy1,
                o_Z             = self.z5,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx2, Replicate(self.dx2[17], 2)),
                i_B             = self.dy2,
                o_Z             = self.z6,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx3, Replicate(self.dx3[17], 2)),
                i_B             = self.dy3,
                o_Z             = self.z7,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx4, Replicate(self.dx4[17], 2)),
                i_B             = self.dy4,
                o_Z             = self.z8,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx5, Replicate(self.dx5[17], 2)),
                i_B             = self.dy5,
                o_Z             = self.z9,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            self.specials += Instance("DSP38",
                # Parameters.
                # -----------
                # Mode Bits to configure DSP 
                p_DSP_MODE     =  "MULTIPLY",
                p_OUTPUT_REG_EN = "FALSE",
                p_INPUT_REG_EN = "FALSE",
                # IOs
                i_A             = Cat(self.dx6, Replicate(self.dx6[17], 2)),
                i_B             = self.dy6,
                o_Z             = self.z10,  
                i_FEEDBACK      = 0,
                i_UNSIGNED_A    = 0,
                i_UNSIGNED_B    = 0
            )
            
