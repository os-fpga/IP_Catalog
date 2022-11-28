#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXIS's axis_switch.v

import os
import logging

from migen import *

from litex.soc.interconnect.axi import *

logging.basicConfig(level=logging.INFO)

# AXIS_SWITCH ---------------------------------------------------------------------------------------
class AXISTREAMSWITCH(Module):
    def __init__(self, platform, s_axis, m_axis,
        s_count, 
        m_count,  
        keep_enable, 
        keep_width, 
        id_enable,
        s_id_width,
        m_id_width,
        m_dest_width,
        s_dest_width,
        user_enable,
        user_width,
        m_base,
        m_top,
        update_tid,
        s_reg_type,
        m_reg_type,
        arb_type_round_robin,
        arb_lsb_high_priority,
        m_connect
    ):
        self.logger = logging.getLogger("AXI_STREAM_SWITCH")
        self.logger.propagate = False
        
        # Data Width
        data_width = len(s_axis[0].data)
        self.logger.info(f"DATA_WIDTH       : {data_width}")

        # User Width
        self.logger.info(f"USER_ENABLE      : {user_enable}")
        user_width = len(s_axis[0].user)
        self.logger.info(f"USER_WIDTH       : {user_width}")

        # Destination Width
        self.logger.info(f"M_DEST_WIDTH     : {m_dest_width}")
        
        # Module Instance.
        # ----------------
        self.specials += Instance("axis_switch",
            # Parameters.
            # -----------
            # Global.
            p_S_COUNT                   = Instance.PreformattedParam(len(s_axis)), 
            p_M_COUNT                   = Instance.PreformattedParam(len(m_axis)),
            p_DATA_WIDTH                = Instance.PreformattedParam(data_width),
            p_USER_WIDTH                = Instance.PreformattedParam(user_width),
            p_KEEP_ENABLE               = Instance.PreformattedParam(keep_enable), 
            p_KEEP_WIDTH                = Instance.PreformattedParam(keep_width), 
            p_S_ID_WIDTH                = Instance.PreformattedParam(s_id_width),
            p_M_ID_WIDTH                = Instance.PreformattedParam(m_id_width),
            p_M_DEST_WIDTH              = Instance.PreformattedParam(m_dest_width),
            p_S_DEST_WIDTH              = Instance.PreformattedParam(s_dest_width),
            p_S_REG_TYPE                = Instance.PreformattedParam(s_reg_type),
            p_M_REG_TYPE                = Instance.PreformattedParam(m_reg_type),
            p_M_CONNECT                 = Instance.PreformattedParam(m_connect),
            p_ID_ENABLE                 = id_enable,
            p_USER_ENABLE               = user_enable,
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
            o_m_axis_tuser              = Cat(*[m_axis.user     for m_axis in m_axis])
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axis_switch.v"))