# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform
from litex.build.altera.programmer import USBBlaster

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk12", 0, Pins("M2"), IOStandard("3.3-V LVTTL")),     # 12MHz clock
    ("user_led", 0, Pins("M6"), IOStandard("3.3-V LVTTL")),  # LED1

    ("sw", 0, Pins("N6"), IOStandard("3.3-V LVTTL")), # user

    ("serial", 0,
        Subsignal("tx", Pins("T7"), IOStandard("3.3-V LVTTL")),
        Subsignal("rx", Pins("R7"), IOStandard("3.3-V LVTTL"))
    ),

    ("spiflash", 0,
        Subsignal("cs_n", Pins("D2")),
        Subsignal("clk",  Pins("H1")),
        Subsignal("mosi", Pins("C1")),
        Subsignal("miso", Pins("H2")),
        IOStandard("3.3-V LVTTL"),
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


    ("gpio_leds", 0,
        Pins("M6 T4 T3 R3 T2 R4 N5 N3"),
        IOStandard("3.3-V LVTTL")
    ),

    # all IO not connected to peripherals mapped to MFIO
    #                 <-        LEDS       -> <-             PMOD          -> <-           D0..D14, D11R, D12R                -> <-        AIN0..AIN7, AIN        -> [C O  I  S  i1 i2]
    ("bbio", 0, Pins("M6 T4 T3 R3 T2 R4 N5 N3 F13 F15 F16 D16 D15 C15 B16 C16 N16 L15 L16 K15 K16 J14 N2 N1 P2 J1 J2 K2 L2 K1 L1 R12 T13 R13 T14 P14 R14 T15 R11 T12 F3 G2 G1 D1 B1 C2"),
        IOStandard("3.3-V LVTTL")),


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

        self.add_platform_command('set_global_assignment -name CYCLONEII_RESERVE_NCEO_AFTER_CONFIGURATION "USE AS REGULAR IO"')
        self.add_platform_command('set_global_assignment -name RESERVE_DATA0_AFTER_CONFIGURATION "USE AS REGULAR IO"')
        self.add_platform_command('set_global_assignment -name RESERVE_DATA1_AFTER_CONFIGURATION "USE AS REGULAR IO"')
        self.add_platform_command('set_global_assignment -name RESERVE_FLASH_NCE_AFTER_CONFIGURATION "USE AS REGULAR IO"')
        self.add_platform_command('set_global_assignment -name RESERVE_DCLK_AFTER_CONFIGURATION "USE AS REGULAR IO"')





    def create_programmer(self):
        return USBBlaster()
