#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXIS's axis_crosspoint.v

import os
import logging
import math

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXIS_INTERCONNECT ---------------------------------------------------------------------------------------
class AXISTREAMINTERCONNECT(Module):
    def __init__(self, platform, s_axis, m_axis, m_count, s_count, last_en, id_en, dest_en, user_en, select_width):
        
        self.logger = logging.getLogger("AXI_STREAM_INTERCONNECT")
        
        self.logger.propagate = False

        # Clock Domain.
        clock_domain = s_axis[0].clock_domain
        self.logger.info(f"CLOCK_DOMAIN     : {clock_domain}")
        
        # AXI Inputs (slave interfaces)
        s_count = len(s_axis)
        self.logger.info(f"S_COUNT          : {s_count}")
        
        # AXI outputs (master interfaces).
        m_count = len(m_axis)
        self.logger.info(f"M_COUNT          : {m_count}")

        # Data Width
        data_width = len(s_axis[0].data)
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        self.logger.info(f"LAST_ENABLE      : {last_en}")
        
        # ID Width
        self.logger.info(f"ID_ENABLE        : {id_en}")
        id_width = len(s_axis[0].id)
        self.logger.info(f"ID Width         : {id_width}")
        
        # Destination Width
        self.logger.info(f"DEST_ENABLE      : {dest_en}")
        dest_width = len(s_axis[0].dest)
        self.logger.info(f"DEST_WIDTH       : {dest_width}")
        
        # User Width
        self.logger.info(f"USER_ENABLE      : {user_en}")
        user_width = len(s_axis[0].user)
        self.logger.info(f"USER_WIDTH       : {user_width}")

        # Control Signal
        self.select = Signal(select_width)
        
        # Module instance.
        # ----------------
        self.specials += Instance("axis_crosspoint",
            # Parameters.
            # -----------
            # Global.
            p_S_COUNT           = len(s_axis),
            p_M_COUNT           = len(m_axis),
            p_DATA_WIDTH        = data_width,
            p_KEEP_ENABLE       = (data_width>8),
            p_KEEP_WIDTH        = math.ceil((data_width+7)/8),
            p_LAST_ENABLE       = last_en,
            p_ID_ENABLE         = id_en,
            p_ID_WIDTH          = id_width,
            p_DEST_ENABLE       = dest_en,
            p_DEST_WIDTH        = dest_width,
            p_USER_ENABLE       = user_en, 
            p_USER_WIDTH        = user_width,

            # Clk / Rst.
            # ----------
            i_clk               = ClockSignal(),
            i_rst               = ResetSignal(),

            # AXI Input
            # --------------------
            i_s_axis_tdata      = Cat(*[s_axis.data      for s_axis in s_axis]),
            i_s_axis_tkeep      = Cat(*[s_axis.keep      for s_axis in s_axis]),
            i_s_axis_tvalid     = Cat(*[s_axis.valid     for s_axis in s_axis]),
            i_s_axis_tlast      = Cat(*[s_axis.last      for s_axis in s_axis]),
            i_s_axis_tid        = Cat(*[s_axis.id        for s_axis in s_axis]),
            i_s_axis_tdest      = Cat(*[s_axis.dest      for s_axis in s_axis]),
            i_s_axis_tuser      = Cat(*[s_axis.user      for s_axis in s_axis]),

            # AXI Output
            o_m_axis_tdata      = Cat(*[m_axis.data      for m_axis in m_axis]),
            o_m_axis_tkeep      = Cat(*[m_axis.keep      for m_axis in m_axis]),
            o_m_axis_tvalid     = Cat(*[m_axis.valid     for m_axis in m_axis]),
            o_m_axis_tlast      = Cat(*[m_axis.last      for m_axis in m_axis]),
            o_m_axis_tid        = Cat(*[m_axis.id        for m_axis in m_axis]),
            o_m_axis_tdest      = Cat(*[m_axis.dest      for m_axis in m_axis]),
            o_m_axis_tuser      = Cat(*[m_axis.user      for m_axis in m_axis]),
            
            # Control
            i_select            = self.select
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axis_crosspoint.v"))
