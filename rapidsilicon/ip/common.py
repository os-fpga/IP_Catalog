#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import shutil

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


    def build(self, platform, module, build_name, dst_path):
        build_path     = "litex_build"
        build_filename = os.path.join(build_path, build_name) + ".v"

        # Build LiteX module.
        platform.build(module,
            build_dir    = build_path,
            build_name   = build_name,
            run          = False,
            regular_comb = False
        )

        # Insert header.
        self.add_verilog_header(build_filename)

        # Copy files to destination.
        shutil.copy(build_filename, dst_path)

        # Remove build files.
        shutil.rmtree(build_path)
