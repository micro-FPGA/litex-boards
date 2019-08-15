# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, VivadoProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("user_led", 0, Pins("M16"), IOStandard("LVCMOS33")), # LED4
#    ("user_led", 1, Pins("E26"), IOStandard("LVCMOS33")),

# P17
    ("clk100", 0, Pins("P17"), IOStandard("LVCMOS33")),
# 
    ("cpu_reset", 0, Pins("V10"), IOStandard("LVCMOS33")),
#
    ("serial", 0,
        Subsignal("tx", Pins("M18")),
        Subsignal("rx", Pins("L18")),
        IOStandard("LVCMOS33")
    ),

    ("hyperram", 0,
        Subsignal("clk", Pins("A13")),
        Subsignal("clk_n", Pins("A14")),
        Subsignal("rstn", Pins("J17")),
        Subsignal("dq", Pins("E17 B17 F18 F16 G17 D18 B18 A16")),
        Subsignal("cs0", Pins("D17")),
        Subsignal("rwds", Pins("E18")),
        IOStandard("LVCMOS18")
    ),

    ("spiflash_4x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("L13")),
        Subsignal("dq", Pins("K17", "K18", "L14", "M14")),
        IOStandard("LVCMOS33")
    ),
    ("spiflash_1x", 0,  # clock needs to be accessed through STARTUPE2
        Subsignal("cs_n", Pins("L13")),
        Subsignal("mosi", Pins("K17")),
        Subsignal("miso", Pins("K18")),
        Subsignal("wp", Pins("L14")),
        Subsignal("hold", Pins("M14")),
        IOStandard("LVCMOS33")
    ),

]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    ("porta", "*"),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    default_clk_name = "clk100"
    default_clk_period = 10.0

    def __init__(self, variant="a7-35-2c"):
        device = {
            "a7-35-2c": "xc7a35tcsg324-2",
            "a7-35-2i": "xc7a35tcsg324-2"
        }[variant]
        XilinxPlatform.__init__(self, device, _io, _connectors, toolchain="vivado")
        self.add_platform_command("""
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
""")
        self.toolchain.bitstream_commands = \
            ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        self.toolchain.additional_commands = \
            ["write_cfgmem -force -format bin -interface spix4 -size 16 "
             "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
#fixme change spi flash type
    def create_programmer(self):
        return VivadoProgrammer(flash_part="n25q128-3.3v-spi-x1_x2_x4")
