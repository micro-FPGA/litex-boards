# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk12", 0, Pins("M2"), IOStandard("3.3-V LVTTL")),    # 12MHz clock
    ("user_led", 0, Pins("M6"), IOStandard("3.3-V LVTTL")), # 

    ("sw", 0, Pins("N6"), IOStandard("3.3-V LVTTL")), # user

    ("serial", 0,
        Subsignal("tx", Pins("T7"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("R7"), IOStandard("3.3-V LVTTL"))
    ),

    ("sdram_clock", 0, Pins("B14"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins("A3 B5 B4 B3 C3 D3 E6 E7 D6 D8 A5 E8")), #0, 1, ...
        Subsignal("ba", Pins("A4 B6")),
        Subsignal("cs_n", Pins("A6")),
        Subsignal("cke", Pins("F8")),
        Subsignal("ras_n", Pins("B7")),
        Subsignal("cas_n", Pins("C8")),
        Subsignal("we_n", Pins("A7")),
        Subsignal("dq", Pins("B10 A10 B11 A11 A12 D9 B12 C9 D11 E11 A15 E9 D14 F9 C14 A14")),
        Subsignal("dm", Pins("B13 D12")),
        IOStandard("3.3-V LVTTL")
    ),

#    ("epcs", 0,
#        Subsignal("data0", Pins("H2")),
#        Subsignal("dclk", Pins("A3")),
#        Subsignal("ncs0", Pins("B3")),
#        Subsignal("asd0", Pins("C1")),
#        IOStandard("3.3-V LVTTL")
#    ),

#    ("i2c", 0,
#        Subsignal("sclk", Pins("F2")),
#        Subsignal("sdat", Pins("F1")),
#        IOStandard("3.3-V LVTTL")
#    ),

#    ("g_sensor", 0,
#        Subsignal("cs_n", Pins("G5")),
#        Subsignal("int", Pins("M2")),
#        IOStandard("3.3-V LVTTL")
#    ),

    ("gpio_leds", 0,
        Pins("M6 T4 T3 R3 T2 R4 N5 N3"),
        IOStandard("3.3-V LVTTL")
    ),

]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name = "clk12"
    default_clk_period = 83

    def __init__(self):
        AlteraPlatform.__init__(self, "10CL025YU256C8G", _io)
        self.add_platform_command("set_global_assignment -name FAMILY \"Cyclone 10 LP\"")
#        self.add_platform_command("set_global_assignment -name ENABLE_CONFIGURATION_PINS OFF")
        self.add_platform_command("set_global_assignment -name INTERNAL_FLASH_UPDATE_MODE \"SINGLE IMAGE WITH ERAM\"")

    def create_programmer(self):
        return USBBlaster()
