# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>

# License: BSD

from migen import *


# Frequency (max) 80MHz

class onchip_osc_c10lp(Module):
    def __init__(self):

        self.clkout = Signal()

        self.specials += Instance("cyclone10lp_oscillator",
            i_oscena  = Constant(1), 
            o_clkout  = self.clkout
        )

# max 100MHz
class onchip_osc_c5(Module):
    def __init__(self):

        self.clkout = Signal()

        self.specials += Instance("cyclonev_oscillator",
            i_oscena  = Constant(1), 
            o_clkout  = self.clkout
        )


# Frequency 82 (116 max)
# 55 MAX40, MAX50
#
class onchip_osc_max10(Module):
    def __init__(self):

        self.clkout = Signal()

        self.specials += Instance("fiftyfivenm_oscillator",
            p_device_id = "08",
            p_clock_frequency = "116",
            i_oscena  = Constant(1), 
            o_clkout  = self.clkout
        )



class onchip_osc(Module):
    def __init__(self, osc=None, device=None, clock_domain="sys"):

        # assign clock automatically?

        self.clkout = Signal()
       
        if osc is None:
            if device[:4] == "10CL":
                osc = onchip_osc_c10lp()
            elif device[:3] == "EP5":
                osc = onchip_osc_c5()
            elif device[:3] == "10M":
                osc = onchip_osc_max10()
            else:
                raise NotImplementedError

        self.submodules += osc

        self.comb += self.clkout.eq(osc.clkout)