#!/usr/bin/env python3
#
# This file is Copyright (c) 2022 RapidSilicon.
#
# SPDX-License-Identifier: MIT

import os
import json
import shutil
import argparse

# IP Catalog Builder -------------------------------------------------------------------------------

class IP_Builder:
    def __init__(self, device, ip_name, language):
        self.device   = device
        self.ip_name  = ip_name
        self.language = language
        self.prepared = False

    @staticmethod
    def add_wrapper_text(filename, text, line):
        # Read Verilog content and add text.
        f = open(filename, "r")
        content = f.readlines()
        content.insert(line, text)
        f.close()

        #  Write Verilog content.
        f = open(filename, "w")
        f.write("".join(content))
        f.close()

    def add_wrapper_header(self, filename):
        header = []
        header.append("// This file is Copyright (c) 2022 RapidSilicon")
        header.append(f"//{'-'*80}")
        header.append("")
        header = "\n".join(header)
        self.add_wrapper_text(filename, header, 13)


    # JSON template for GUI parsing
    def export_json_template(self, parser, dep_dict, summary):

        # Get "core_fix_param_group" group.
        core_fix_param_group = None
        for group in parser._action_groups:
            if "core fix" in group.title.lower():
                core_fix_param_group = group
                break

        # Get "core_range_param_group" group.
        core_range_param_group = None
        for group in parser._action_groups:
            if "core range" in group.title.lower():
                core_range_param_group = group
                break

        # Get "core_bool_param_group" group.
        core_bool_param_group = None
        for group in parser._action_groups:
            if "core bool" in group.title.lower():
                core_bool_param_group = group
                break

        # Get "core_str_param_group" group.
        core_str_param_group = None
        for group in parser._action_groups:
            if "core string" in group.title.lower():
                core_str_param_group = group
                break

        # Get "core_str_param_group" group.
        core_file_path_group = None
        for group in parser._action_groups:
            if "core file" in group.title.lower():
                core_file_path_group = group
                break

        # Create vars dict of arguments.
        _args = parser.parse_args()
        _vars = vars(_args)

        # Post Processing of Json
        # Add choices/description to Core arguments.

        param_json = {}
        param_list = []
        core_param_list = []
        build_param_list = []
        for name, var in _vars.items():
            if core_fix_param_group is not None:
                for core_action in core_fix_param_group._group_actions:
                    if name == core_action.dest:
                        core_param_list.append(
                        {   "parameter"     : str(name),
                            "title"         : str(name.upper()),
                            "options"       : list(core_action.choices),
                            "default"       : str(core_action.default),
                            "type"          : str("int"),
                            "description"   : str(core_action.help),
                            "disable"       : str("False"),
                        })

            if core_bool_param_group is not None:
                for core_action in core_bool_param_group._group_actions:
                    if name == core_action.dest:
                        core_param_list.append(
                        {   "parameter"     : str(name),
                            "title"         : str(name.upper()),
                            "default"       : str(core_action.default),
                            "type"          : str("bool"),
                            "description"   : str(core_action.help),
                            "disable"       : str("False"),
                        })
            if core_range_param_group is not None:
                for core_action in core_range_param_group._group_actions:
                    if name == core_action.dest:
                        temp_list = list(core_action.choices)
                        core_param_list.append(
                        {   "parameter"     : str(name),
                            "title"         : str(name.upper()),
                            "range"         : [min(temp_list),max(temp_list)],
                            "type"          : str("int"),
                            "default"       : str(core_action.default),
                            "description"   : str(core_action.help),
                            "disable"       : str("False"),
                        })
            if core_str_param_group is not None:
                for core_action in core_str_param_group._group_actions:
                    if name == core_action.dest:
                        core_param_list.append(
                        {   "parameter"     : str(name),
                            "title"         : str(name.upper()),
                            "options"       : list(core_action.choices),
                            "default"       : str(core_action.default),
                            "type"          : str("str"),
                            "description"   : str(core_action.help),
                            "disable"       : str("False"),
                        })

            if core_file_path_group is not None:
                for core_action in core_file_path_group._group_actions:
                    if name == core_action.dest:
                        core_param_list.append(
                        {   "parameter"     : str(name),
                            "title"         : str(name.upper()),
                            "default"       : str(core_action.default),
                            "type"          : str("str"),
                            "description"   : str(core_action.help),
                            "disable"       : str("False"),
                        })

            if name.startswith("build"):
                build_param_list.append({name :  str(_vars[name])})

            if name.startswith("json"):
                build_param_list.append({name : str(_vars[name])})

 
        dep_list= list(dep_dict.keys())
        param_temp = {"parameters": core_param_list}
        param_json.update(param_temp)


    # Append dependencies for dependant paramters

        for i in range(len(core_param_list)):
            if param_json["parameters"][i]['parameter'] in dep_list:
                param_json["parameters"][i].update(disable = dep_dict[param_json["parameters"][i]['parameter']])


    #Append summary in JSON
        summary_temp = {"Summary": summary}
        param_json.update(summary_temp)



    # Append Build and Json params to final json
        for i in range(len(build_param_list)):
            param_json.update(build_param_list[i])

        # Dump vars to JSON.
        print(json.dumps(param_json, indent=4, default=None))


    def import_args_from_json(self, parser, json_filename):
        with open(json_filename, "rt") as f:
            t_args = argparse.Namespace()
            t_args.__dict__.update(json.load(f))
            args = parser.parse_args(namespace=t_args)
        return args
    
    def import_ip_details_json(self, json_filename, details):
        with open(("ip_Details.json"), "w") as f:
            json.dump(details, f, indent=4, default=None,)



    def prepare(self, build_dir, build_name, version):
        # Remove build_name extension when specified.
        build_name = os.path.splitext(build_name)[0]

        # Define paths.
        self.build_name         = build_name
        self.build_path         = os.path.join(build_dir, "rapidsilicon", "ip", self.ip_name, version, build_name)
        self.litex_wrapper_path = os.path.join(self.build_path, "litex_wrapper")
        self.sim_path           = os.path.join(self.build_path, "sim")
        self.src_path           = os.path.join(self.build_path, "src")
        self.synth_path         = os.path.join(self.build_path, "synth")

        # Create paths.
        os.makedirs(self.build_path,         exist_ok=True)
        os.makedirs(self.litex_wrapper_path, exist_ok=True)
        os.makedirs(self.sim_path,           exist_ok=True)
        os.makedirs(self.src_path,           exist_ok=True)
        os.makedirs(self.synth_path,         exist_ok=True)

        self.prepared = True

    def copy_files(self, gen_path):
        assert self.prepared

        # Copy Generator file.
        generator_filename = os.path.join(gen_path, f"{self.ip_name}_gen.py")
        shutil.copy(generator_filename, self.build_path)

        # Copy RTL files.
        rtl_path  = os.path.join(gen_path, "src")
        if os.path.exists(rtl_path):
            rtl_files = os.listdir(rtl_path)
            for file_name in rtl_files:
                full_file_path = os.path.join(rtl_path, file_name)
                if os.path.isfile(full_file_path):
                    shutil.copy(full_file_path, self.src_path)

        # Copy litex_wrapper file.
        litex_path  = os.path.join(gen_path, "litex_wrapper")
        if os.path.exists(litex_path):
            litex_files = os.listdir(litex_path)
            for file_name in litex_files:
                full_file_path = os.path.join(litex_path, file_name)
                if os.path.isfile(full_file_path):
                    shutil.copy(full_file_path, self.litex_wrapper_path)
        
        # Copy sim files.
        simulate_path  = os.path.join(gen_path, "sim")
        if os.path.exists(simulate_path):
            simulate_files = os.listdir(simulate_path)
            for file_name in simulate_files:
                full_file_path = os.path.join(simulate_path, file_name)
                if os.path.isfile(full_file_path):
                    shutil.copy(full_file_path, self.sim_path)
                elif os.path.isdir(full_file_path):
                    shutil.copytree(simulate_path, self.sim_path, ignore=shutil.ignore_patterns('rapidsilicon'), dirs_exist_ok=True)

    def generate_tcl(self):
        assert self.prepared

        # Build .tcl file.
        # ----------------

        tcl = []

        # Create Design.
        tcl.append(f"create_design {self.build_name}")

        # Set Device.
        tcl.append(f"target_device {self.device.upper()}")

        # Add Include Path.
        tcl.append(f"add_include_path ../src")
        tcl.append(f"add_library_path ../src")

        # Add file extension
        tcl.append(f"add_library_ext .v .sv")

        # Add Sources.
        # Verilog vs System Verilog
        if   (self.language == "sverilog"):
            tcl.append(f"add_design_file {os.path.join('../src', self.build_name + '.sv')}")
            
        elif (self.language == "verilog"):
            tcl.append(f"add_design_file {os.path.join('../src', self.build_name + '.v')}")
            
        else:
            tcl.append(f"add_design_file {os.path.join('../src', self.build_name + '.v')}")

        # Set Top Module.
        tcl.append(f"set_top_module {self.build_name}")

        # Add Timings Constraints.
        # tcl.append(f"add_constraint_file {self.build_name}.sdc")

        # Run.
        tcl.append("synthesize")

        # Generate .tcl file.
        # -------------------
        tcl_filename = os.path.join(self.synth_path, "raptor.tcl")
        f = open(tcl_filename, "w")
        f.write("\n".join(tcl))
        f.close()

    def generate_wrapper(self, platform, module):
        assert self.prepared
        build_path     = "litex_build"
        build_filename = os.path.join(build_path, self.build_name) + ".v"

        # Build LiteX module.
        platform.build(module,
            build_dir    = build_path,
            build_name   = self.build_name,
            run          = False,
            regular_comb = False
        )

        # Insert header.
        self.add_wrapper_header(build_filename)

        # Copy file to destination.
        shutil.copy(build_filename, self.src_path)
        
        # Changing File Extension from .v to .sv
        if (self.language == "sverilog"):
            old_wrapper = os.path.join(self.src_path, f'{self.build_name}.v')
            new_wrapper = old_wrapper.replace('.v','.sv')
            os.rename(old_wrapper, new_wrapper)

        # Remove build files.
        shutil.rmtree(build_path)
