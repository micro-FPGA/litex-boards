# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk12", 0, Pins("G21"), IOStandard("3.3-V LVTTL")),

#    ("user_led", 0, Pins("C10"), IOStandard("3.3-V LVTTL")),
#    ("user_led", 1, Pins("A"), IOStandard("3.3-V LVTTL")),
#    ("user_led", 2, Pins("B"), IOStandard("3.3-V LVTTL")),
#    ("user_led", 3, Pins("A"), IOStandard("3.3-V LVTTL")),
#    ("user_led", 4, Pins("D"), IOStandard("3.3-V LVTTL")),
#    ("user_led", 5, Pins("F"), IOStandard("3.3-V LVTTL")),
#    ("user_led", 6, Pins("B"), IOStandard("3.3-V LVTTL")),
#    ("user_led", 7, Pins("C1"), IOStandard("3.3-V LVTTL")),


    ("sw", 0, Pins("U10"), IOStandard("3.3-V LVTTL")),
    ("sw", 1, Pins("U11"), IOStandard("3.3-V LVTTL")),
    ("sw", 2, Pins("V11"), IOStandard("3.3-V LVTTL")),
    ("sw", 3, Pins("T10"), IOStandard("3.3-V LVTTL")),
    ("sw", 4, Pins("T11"), IOStandard("3.3-V LVTTL")),

    ("serial", 0,
        Subsignal("tx", Pins("B21"), IOStandard("3.3-V LVTTL")), # BDBUS 1
        Subsignal("rx", Pins("C20"), IOStandard("3.3-V LVTTL"))  # BDBUS 0
    ),

    ("sdram_clock", 0, Pins("AA3"), IOStandard("3.3-V LVTTL")),
    ("sdram", 0,
        Subsignal("a", Pins("V5 Y3 W6 Y4 AB5 AB6 AA6 AA7 AB7 AA5 V6 AA8 AB8")), 
        Subsignal("ba", Pins("Y6 V7")),
        Subsignal("cs_n", Pins("W7")),
        Subsignal("cke", Pins("AA4")),
        Subsignal("ras_n", Pins("V8")),
        Subsignal("cas_n", Pins("Y7")),
        Subsignal("we_n", Pins("W8")),
        Subsignal("dq", Pins("AB16 Y17 AA16 AA19 AB18 AA20 AB19 AB20 Y13 Y15 AA13 AB15 AB13 AA15 AA14")),
        Subsignal("dm", Pins("Y14 W13")),
        IOStandard("3.3-V LVTTL")
    ),

    ("epcs", 0,
        Subsignal("data0", Pins("K1")),
        Subsignal("dclk", Pins("K2")),
        Subsignal("ncs0", Pins("E2")),
        Subsignal("asd0", Pins("D1")),
        IOStandard("3.3-V LVTTL")
    ),

#    ("i2c", 0,
#        Subsignal("sclk", Pins("F2")),
#        Subsignal("sdat", Pins("F1")),
#        IOStandard("3.3-V LVTTL")
#    ),


    ("gpio_leds", 0,
        Pins("AB10 AA10 AA9 Y10 W10 U9 U8 U7"),
        IOStandard("3.3-V LVTTL")
    ),

#    ("gpio_0", 0,
#        Pins("D3 C3 A2 A3 B3 B4 A4 B5 A5 D5 B6 A6 B7 D6 A7 C6",
#            "C8 E6 E7 D8 E8 F8 F9 E9 C9 D9 E11 E10 C11 B11 A12 D11",
#            "D12 B12"),
#        IOStandard("3.3-V LVTTL")
#    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name = "clk12"
    default_clk_period = 83

    def __init__(self):
        AlteraPlatform.__init__(self, "10CL055YU484A7G", _io)
        self.add_platform_command("set_global_assignment -name FAMILY \"Cyclone 10 LP\"")

    def create_programmer(self):
        return USBBlaster()
