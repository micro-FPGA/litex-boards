# This file is Copyright (c) 2019 Antony Pavlov <antonynpavlov@gmail.com>
# License: BSD

from litex.build.generic_platform import *
from litex.build.altera import AlteraPlatform

# IOs ------------------------------------------------------------------

_io = [
    ("clk50", 0, Pins("AF14"), IOStandard("1.5-V")),

    ("user_led", 0, Pins("AF10"), IOStandard("3.3-V LVTTL")), # LED0
    ("user_led", 1, Pins("AD10"), IOStandard("3.3-V LVTTL")), # LED1
    ("user_led", 2, Pins("AE11"), IOStandard("3.3-V LVTTL")), # LED2
    ("user_led", 3, Pins("AD7" ), IOStandard("3.3-V LVTTL")),  # LED3

    ("serial", 0,
        Subsignal("tx", Pins("C9"), IOStandard("3.3-V LVTTL")), # fake
        Subsignal("rx", Pins("C10"), IOStandard("3.3-V LVTTL"))   # fake
    ),

]

# Platform -------------------------------------------------------------

class Platform(AlteraPlatform):
    default_clk_name = "clk50"
    default_clk_period = 20

    def __init__(self):
        AlteraPlatform.__init__(self, "5CSXFC6D6F31C8", _io)
