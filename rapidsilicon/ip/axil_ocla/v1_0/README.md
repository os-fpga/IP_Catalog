# On-Chip Logic Analyzer IP Core  
## Introduction
The On Chip Logic Analyzer (OCLA)
core is a AXI compliant configurable embedded logic analyzer that is designed to be used in applications that requires verification or debugging by monitoring the internal signals of a design on FPGAs

## Contents
```
.
├── axil_ocla_gen.py
├── LICENSE
├── litex_wrapper
│   ├── axil_ocla_litex_wrapper.py
│   └── README.md
├── README.md
├── sdc
│   └── README.md
├── sim
│   └── README.md
└── src
    ├── axi_slv_lite.sv
    ├── defines.sv
    ├── dual_port_ram.sv
    ├── gray2binary.sv
    ├── ocla_controller.sv
    ├── ocla_mem_controller.sv
    ├── ocla.sv
    ├── README
    ├── sampler_buffer.sv
    ├── stream_out_buffer.sv
    ├── synchronizer.sv
    ├── trigger_control_unit.sv
    └── trigger_unit.sv

```

## Parameters
User can configure OCLA IP CORE using following parameters:

| Sr.No.|     Parameter               |      Keyword             |    Value                     |
|-------|-----------------------------|--------------------------|------------------------------|
|   1.  |   MEMORY DEPTH              |   mem_depth              |  32, 64, 128, 256, 512,1024  |
|   2.  |   NUMBER OF PROBES          |  no_of_probes            |  1-1024                      |
|   3.  |   NUMBER OF INPUT TRIGGERS  |  no_of_trigger_inputs    |  1-32                        |
|   4.  |   PROBE WIDTH               |   probe_width            |  1-32                        |

## Macros
User can enable different OCLA IP Core features using the following Macros:
| Sr.No.|     Feature                 |      Macro                     |    Description                   |
|-------|-----------------------------|--------------------------------|----------------------------------|
|   1.  |   Value Compare Feature     |   value_compare                | To enable Value Compare feature  |
|   2.  |   Advance Trigger Mode      |   advance_trigger              | To enable Advance Trigger Mode   |
|   3.  |   Enable Trigger Inputs     |   trigger_inputs_en            | To enable Trigger inputs         |

To generate RTL with above parameters, run the following command:
```
python3 axil_ocla_gen.py --build-name=crossbar_wrapper --build
```


