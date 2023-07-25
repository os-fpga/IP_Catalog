#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXIS's axis_adapter.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# AXIS_ADAPTER ---------------------------------------------------------------------------------------
class AXISADAPTER(Module):
    def __init__(self, platform, s_axis, m_axis, id_en , dest_en, user_en):
        
        self.logger = logging.getLogger("AXIS_ADAPTER")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Data Width
        s_data_width = len(s_axis.data)
        self.logger.info(f"S_DATA_WIDTH     : {s_data_width}")
        
        m_data_width = len(m_axis.data)
        self.logger.info(f"M_DATA_WIDTH     : {m_data_width}")
        
        # ID Width
        self.logger.info(f"ID_ENABLE        : {id_en}")
        id_width = len(s_axis.id)
        self.logger.info(f"ID Width         : {id_width}")
        
        # Destination Width
        self.logger.info(f"DEST_ENABLE      : {dest_en}")
        dest_width = len(s_axis.dest)
        self.logger.info(f"DEST_WIDTH       : {dest_width}")
        
        # User Width
        self.logger.info(f"USER_ENABLE      : {user_en}")
        user_width = len(s_axis.user)
        self.logger.info(f"USER_WIDTH       : {user_width}")
        
        self.logger.info(f"===================================================")
        # Module instance.
        # ----------------
        self.specials += Instance("axis_adapter",
            # Parameters.
            # -----------
            # Global.
            p_S_DATA_WIDTH      = Instance.PreformattedParam(s_data_width),
            p_S_KEEP_WIDTH      = Instance.PreformattedParam(int((s_data_width+7)/8)),
            p_M_DATA_WIDTH      = Instance.PreformattedParam(m_data_width),
            p_ID_WIDTH          = Instance.PreformattedParam(id_width),
            p_DEST_WIDTH        = Instance.PreformattedParam(dest_width),
            p_USER_WIDTH        = Instance.PreformattedParam(user_width),
            p_M_KEEP_WIDTH      = Instance.PreformattedParam(int((m_data_width+7)/8)),
            p_S_KEEP_ENABLE     = s_data_width>8,
            p_M_KEEP_ENABLE     = m_data_width>8,
            p_ID_ENABLE         = id_en,
            p_DEST_ENABLE       = dest_en,
            p_USER_ENABLE       = user_en,
            
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
            o_m_axis_tdata      = m_axis.data,
            o_m_axis_tkeep      = m_axis.keep,
            o_m_axis_tvalid     = m_axis.valid,
            i_m_axis_tready     = m_axis.ready,
            o_m_axis_tlast      = m_axis.last,
            o_m_axis_tid        = m_axis.id,
            o_m_axis_tdest      = m_axis.dest,
            o_m_axis_tuser      = m_axis.user
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axis_adapter.v"))
