 #
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXIS's axis_ram_switch.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# AXIS_RAM_SWITCH ---------------------------------------------------------------------------------------
class AXISTREAMRAMSWITCH(Module):
    def __init__(self, platform, s_axis, m_axis,
        fifo_depth, cmd_fifo_depth, speedup, s_count, 
        m_count, s_data_width, s_keep_enable, s_keep_width,
        m_data_width, m_keep_enable, m_keep_width, 
        id_enable, s_id_width, m_id_width, m_dest_width,
        s_dest_width, user_enable, user_width,
        user_bad_frame_value, user_bad_frame_mask,
        drop_bad_frame, drop_when_full, m_base, m_top,
        update_tid, arb_type_round_robin, arb_lsb_high_priority,
        m_connect, ram_pipeline
    ):
        
        self.logger = logging.getLogger("AXI_STREAM_RAM_SWITCH")
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")
        
        # Data Width
        data_width = len(s_axis[0].data)
        self.logger.info(f"DATA_WIDTH       : {data_width}")

        # User Width
        self.logger.info(f"USER_ENABLE      : {user_enable}")
        
        # user_width = len(s_axis[0].user)
        self.logger.info(f"USER_WIDTH       : {user_width}")
        
        # Number of Slave Interfaces
        s_count = len(s_axis)
        self.logger.info(f"S_COUNT          : {s_count}")
        
        # Number of Master Interfaces
        m_count = len(m_axis)
        self.logger.info(f"M_COUNT          : {m_count}")

        # Destination Width
        self.logger.info(f"M_DEST_WIDTH     : {m_dest_width}")
        
        self.logger.info(f"===================================================")
        
        # Status Signals
        self.status_overflow            = Signal()
        self.status_bad_frame           = Signal()
        self.status_good_frame          = Signal()

        # Module Instance.
        # ----------------
        self.specials += Instance("axis_ram_switch",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE                   = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID                     = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION                = Instance.PreformattedParam("IP_VERSION"),
            # Global.
            p_FIFO_DEPTH                = Instance.PreformattedParam(fifo_depth),
            p_CMD_FIFO_DEPTH            = Instance.PreformattedParam(cmd_fifo_depth),
            p_SPEEDUP                   = Instance.PreformattedParam(speedup),
            p_S_COUNT                   = Instance.PreformattedParam(len(s_axis)), 
            p_M_COUNT                   = Instance.PreformattedParam(len(m_axis)),
            p_S_DATA_WIDTH              = Instance.PreformattedParam(s_data_width),
            p_S_KEEP_WIDTH              = Instance.PreformattedParam(s_keep_width),
            p_M_DATA_WIDTH              = Instance.PreformattedParam(m_data_width),
            p_M_KEEP_WIDTH              = Instance.PreformattedParam(m_keep_width),
            p_S_ID_WIDTH                = Instance.PreformattedParam(s_id_width),
            p_M_ID_WIDTH                = Instance.PreformattedParam(m_id_width),
            p_M_DEST_WIDTH              = Instance.PreformattedParam(m_dest_width),
            p_S_DEST_WIDTH              = Instance.PreformattedParam(s_dest_width),
            p_USER_BAD_FRAME_VALUE      = Instance.PreformattedParam(user_bad_frame_value),
            p_USER_BAD_FRAME_MASK       = Instance.PreformattedParam(user_bad_frame_mask),
            p_M_CONNECT                 = Instance.PreformattedParam(m_connect),
            p_RAM_PIPELINE              = Instance.PreformattedParam(ram_pipeline),
            p_USER_WIDTH                = user_width,
            p_S_KEEP_ENABLE             = s_keep_enable,
            p_M_KEEP_ENABLE             = m_keep_enable,
            p_ID_ENABLE                 = id_enable,
            p_USER_ENABLE               = user_enable,
            p_DROP_BAD_FRAME            = drop_bad_frame,
            p_DROP_WHEN_FULL            = drop_when_full,
            p_M_BASE                    = C(m_base, len(s_axis)*s_dest_width),
            p_M_TOP                     = C(m_top, len(m_axis)*s_dest_width),
            p_UPDATE_TID                = update_tid,
            p_ARB_TYPE_ROUND_ROBIN      = arb_type_round_robin,
            p_ARB_LSB_HIGH_PRIORITY     = arb_lsb_high_priority,

            # Clk / Rst.
            # ----------
            i_clk                       = ClockSignal(),
            i_rst                       = ResetSignal(),

            # AXI Input
            # -----------------
            i_s_axis_tdata              = Cat(*[s_axis.data     for s_axis in s_axis]),
            i_s_axis_tkeep              = Cat(*[s_axis.keep     for s_axis in s_axis]),
            i_s_axis_tvalid             = Cat(*[s_axis.valid    for s_axis in s_axis]),
            o_s_axis_tready             = Cat(*[s_axis.ready    for s_axis in s_axis]),
            i_s_axis_tlast              = Cat(*[s_axis.last     for s_axis in s_axis]),
            i_s_axis_tid                = Cat(*[s_axis.id       for s_axis in s_axis]),
            i_s_axis_tdest              = Cat(*[s_axis.dest     for s_axis in s_axis]),
            i_s_axis_tuser              = Cat(*[s_axis.user     for s_axis in s_axis]),

            # AXI Output        
            o_m_axis_tdata              = Cat(*[m_axis.data     for m_axis in m_axis]),
            o_m_axis_tkeep              = Cat(*[m_axis.keep     for m_axis in m_axis]),
            o_m_axis_tvalid             = Cat(*[m_axis.valid    for m_axis in m_axis]),
            i_m_axis_tready             = Cat(*[m_axis.ready    for m_axis in m_axis]),
            o_m_axis_tlast              = Cat(*[m_axis.last     for m_axis in m_axis]),
            o_m_axis_tid                = Cat(*[m_axis.id       for m_axis in m_axis]),
            o_m_axis_tdest              = Cat(*[m_axis.dest     for m_axis in m_axis]),
            o_m_axis_tuser              = Cat(*[m_axis.user     for m_axis in m_axis]),

            # Status
            o_status_overflow           = self.status_overflow,
            o_status_bad_frame          = self.status_bad_frame,
            o_status_good_frame         = self.status_good_frame
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axis_ram_switch.v"))
