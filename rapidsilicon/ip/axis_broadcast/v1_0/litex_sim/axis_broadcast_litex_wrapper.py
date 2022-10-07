#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXIS's axis_broadcast.v

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXIS_BROADCAST ---------------------------------------------------------------------------------------
class AXISBROADCAST(Module):
    def __init__(self, platform, s_axis, m_axis, m_count, last_en, id_en, dest_en, user_en):
        
        self.logger = logging.getLogger("AXIS_BROADCAST")
        
        self.logger.propagate = False

        # Master Interfaces
        m_count = len(m_axis)
        self.logger.info(f"M_COUNT          : {m_count}")
        
        # Data
        data_width = len(s_axis.data)
        self.logger.info(f"DATA_WIDTH       : {data_width}")
        self.logger.info(f"LAST_ENABLE      : {last_en}")
        
        # ID 
        self.logger.info(f"ID_ENABLE        : {id_en}")
        id_width = len(s_axis.id)
        self.logger.info(f"ID Width         : {id_width}")
        
        # Destination
        self.logger.info(f"DEST_ENABLE      : {dest_en}")
        dest_width = len(s_axis.dest)
        self.logger.info(f"DEST_WIDTH       : {dest_width}")
        
        # User
        self.logger.info(f"USER_ENABLE      : {user_en}")
        user_width = len(s_axis.user)
        self.logger.info(f"USER_WIDTH       : {user_width}")
        

        # Module instance.
        # ----------------
        self.specials += Instance("axis_broadcast",
            # Parameters.
            # -----------
            # Global.
            p_M_COUNT           = len(m_axis),
            p_DATA_WIDTH        = data_width,
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
            i_s_axis_tdata      = s_axis.data,
            i_s_axis_tkeep      = s_axis.keep,
            i_s_axis_tvalid     = s_axis.valid,
            o_s_axis_tready     = s_axis.ready,
            i_s_axis_tlast      = s_axis.last,
            i_s_axis_tid        = s_axis.id,
            i_s_axis_tdest      = s_axis.dest,
            i_s_axis_tuser      = s_axis.user,

            # AXI Output
            o_m_axis_tdata      = Cat(*[m_axis.data     for m_axis in m_axis]),
            o_m_axis_tkeep      = Cat(*[m_axis.keep     for m_axis in m_axis]),
            o_m_axis_tvalid     = Cat(*[m_axis.valid    for m_axis in m_axis]),
            i_m_axis_tready     = Cat(*[m_axis.ready    for m_axis in m_axis]),
            o_m_axis_tlast      = Cat(*[m_axis.last     for m_axis in m_axis]),
            o_m_axis_tid        = Cat(*[m_axis.id       for m_axis in m_axis]),
            o_m_axis_tdest      = Cat(*[m_axis.dest     for m_axis in m_axis]),
            o_m_axis_tuser      = Cat(*[m_axis.user     for m_axis in m_axis]),
            
        )
        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axis_broadcast.v"))
