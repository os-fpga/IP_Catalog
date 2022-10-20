#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os

# RapidSilicon IP Catalog Builder ------------------------------------------------------------------

class RapidSiliconIPCatalogBuilder:
    @staticmethod
    def add_verilog_text(filename, text, line):
        # Read Verilog content and add text.
        f = open(filename, "r")
        content = f.readlines()
        content.insert(line, text)
        f.close()

        #  Write Verilog content.
        f = open(filename, "w")
        f.write("".join(content))
        f.close()

    def add_verilog_header(self, filename):
        header = []
        header.append("// This file is Copyright (c) 2022 RapidSilicon")
        header.append(f"//{'-'*80}")
        header.append("")
        header.append("`timescale 1ns / 1ps")
        header = "\n".join(header)
        self.add_verilog_text(filename, header, 13)
