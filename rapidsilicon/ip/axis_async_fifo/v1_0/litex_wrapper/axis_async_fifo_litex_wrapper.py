#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#
# LiteX wrapper around Alex Forencich Verilog-AXIS's axis_async_fifo.v

import os
import datetime
import logging

from migen import *

from litex.soc.interconnect.axi import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')

# AXIS_ASYNC_FIFO ---------------------------------------------------------------------------------------
class AXISASYNCFIFO(Module):
    def __init__(self, platform, s_axis, m_axis, 
        depth           = 4096,
        last_en         = 1,
        id_en           = 0,
        dest_en         = 0,
        user_en         = 1,
        ram_pipeline         = 1,
        out_fifo_en     = 0,
        bad_frame_value = 1,
        bad_frame_mask  = 1,
        frame_fifo      = 0,
        drop_bad_frame  = 0,
        drop_when_full  = 0        
    ):
        
        self.logger = logging.getLogger("AXI_STREAM_ASYNCHRONUS_FIFO")
        
        self.logger.propagate = True
        
        self.logger.info(f"=================== PARAMETERS ====================")

        # Depth
        self.logger.info(f"DEPTH                : {depth}")

        # Data Width
        data_width = len(s_axis.data)
        self.logger.info(f"DATA_WIDTH           : {data_width}")
        self.logger.info(f"LAST_ENABLE          : {last_en}")
        
        # ID Width
        self.logger.info(f"ID_ENABLE            : {id_en}")
        id_width = len(s_axis.id)
        self.logger.info(f"ID Width             : {id_width}")
        
        # Destination Width
        self.logger.info(f"DEST_ENABLE          : {dest_en}")
        dest_width = len(s_axis.dest)
        self.logger.info(f"DEST_WIDTH           : {dest_width}")
        
        # User Width
        self.logger.info(f"USER_ENABLE          : {user_en}")
        user_width = len(s_axis.user)
        self.logger.info(f"USER_WIDTH           : {user_width}")
        
        # Other
        self.logger.info(f"RAM_PIPELINE         : {ram_pipeline}")
        self.logger.info(f"FRAME_FIFO           : {frame_fifo}")
        self.logger.info(f"OUTPUT_FIFO_ENABLE   : {out_fifo_en}")
        self.logger.info(f"USER_BAD_FRAME_VALUE : {bad_frame_value}")
        self.logger.info(f"USER_BAD_FRAME_MASK  : {bad_frame_mask}")
        self.logger.info(f"DROP_BAD_FRAME       : {drop_bad_frame}")
        self.logger.info(f"DROP_WHEN_FULL       : {drop_when_full}")
        
        self.logger.info(f"===================================================")
        
        # Status Signals
        self.s_status_overflow     = Signal()
        self.s_status_bad_frame    = Signal()
        self.s_status_good_frame   = Signal()
        self.m_status_overflow     = Signal()
        self.m_status_bad_frame    = Signal()
        self.m_status_good_frame   = Signal()

        # Clock/Reset Signals
        self.m_clk                 = Signal()
        self.m_rst                 = Signal()
        self.s_clk                 = Signal()
        self.s_rst                 = Signal()
        
        # Module instance.
        # ----------------
        self.specials += Instance("axis_async_fifo",
            # Parameters.
            # -----------
            # IP Parameters
            p_IP_TYPE               = Instance.PreformattedParam("IP_TYPE"),
            p_IP_ID                 = Instance.PreformattedParam("IP_ID"),
            p_IP_VERSION            = Instance.PreformattedParam("IP_VERSION"),
            # Global.
            p_DEPTH                 = Instance.PreformattedParam(depth),
            p_DATA_WIDTH            = Instance.PreformattedParam(data_width),
            p_KEEP_WIDTH            = Instance.PreformattedParam(int((data_width+7)/8)),
            p_ID_WIDTH              = Instance.PreformattedParam(id_width),
            p_DEST_WIDTH            = Instance.PreformattedParam(dest_width),
            p_USER_WIDTH            = Instance.PreformattedParam(user_width),
            p_RAM_PIPELINE          = ram_pipeline,
            p_KEEP_ENABLE           = data_width>8,
            p_LAST_ENABLE           = last_en,
            p_ID_ENABLE             = id_en,
            p_DEST_ENABLE           = dest_en,
            p_USER_ENABLE           = user_en,
            p_OUTPUT_FIFO_ENABLE    = out_fifo_en,
            p_USER_BAD_FRAME_VALUE  = bad_frame_value,
            p_USER_BAD_FRAME_MASK   = bad_frame_mask,
            p_FRAME_FIFO            = frame_fifo,
            p_DROP_BAD_FRAME        = drop_bad_frame,
            p_DROP_WHEN_FULL        = drop_when_full,

            # Clk / Rst.
            # ----------
            i_m_clk                 = self.m_clk,
            i_m_rst                 = self.m_rst,
            i_s_clk                 = self.s_clk,
            i_s_rst                 = self.s_rst,

            # AXI Input
            # --------------------
            i_s_axis_tdata          = s_axis.data,
            i_s_axis_tkeep          = s_axis.keep,
            i_s_axis_tvalid         = s_axis.valid,
            o_s_axis_tready         = s_axis.ready,
            i_s_axis_tlast          = s_axis.last,
            i_s_axis_tid            = s_axis.id,
            i_s_axis_tdest          = s_axis.dest,
            i_s_axis_tuser          = s_axis.user,

            # AXI Output
            o_m_axis_tdata          = m_axis.data,
            o_m_axis_tkeep          = m_axis.keep,
            o_m_axis_tvalid         = m_axis.valid,
            i_m_axis_tready         = m_axis.ready,
            o_m_axis_tlast          = m_axis.last,
            o_m_axis_tid            = m_axis.id,
            o_m_axis_tdest          = m_axis.dest,
            o_m_axis_tuser          = m_axis.user,
            
            # Status
            o_s_status_overflow     = self.s_status_overflow,
            o_s_status_bad_frame    = self.s_status_bad_frame,
            o_s_status_good_frame   = self.s_status_good_frame,
            o_m_status_overflow     = self.m_status_overflow,
            o_m_status_bad_frame    = self.m_status_bad_frame,
            o_m_status_good_frame   = self.m_status_good_frame
        )

        # Add Sources.
        # ------------
        self.add_sources(platform)

    @staticmethod
    def add_sources(platform):
        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
        platform.add_source(os.path.join(rtl_dir, "axis_async_fifo.v"))
