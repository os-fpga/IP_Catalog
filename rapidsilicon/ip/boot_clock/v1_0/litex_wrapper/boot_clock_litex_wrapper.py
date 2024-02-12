#
# This file is part of RapidSilicon's IP_Catalog.
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT
#

import os
import datetime
import logging

from migen import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename="IP.log",filemode="w", level=logging.INFO, format='%(levelname)s: %(message)s\n')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logging.info(f'Log started at {timestamp}')


def colorer(s, color="bright"):
    header  = {
        "bright": "\x1b[1m",
        "green":  "\x1b[32m",
        "cyan":   "\x1b[36m",
        "red":    "\x1b[31m",
        "yellow": "\x1b[33m",
        "underline": "\x1b[4m"}[color]
    trailer = "\x1b[0m"
    return header + str(s) + trailer


class BOOT_CLOCK(Module):
    def __init__(self, platform, period):
        self.logger = logging.getLogger("BOOT_CLOCK")
        self.logger.propagate = True

        self.logger.info("Creating BOOT_CLOCK module.")
        self.logger.info(f"=================== PARAMETERS ====================")
        self.logger.info(f"PERIOD  : {colorer(period)}")

        # Clock output
        self.O = Signal()

        self.specials += Instance("BOOT_CLOCK",
            p_PERIOD=Instance.PreformattedParam(period),
            o_O=self.O
        )

#        self.add_sources(platform)
#
#    @staticmethod
#    def add_sources(platform):
#        rtl_dir = os.path.join(os.path.dirname(__file__), "../src")
#        platform.add_source(os.path.join(rtl_dir, "boot_clock.v"))