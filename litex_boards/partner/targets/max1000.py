#!/usr/bin/env python3

# This file is Copyright (c) 2019 msloniewski <marcin.sloniewski@gmail.com>
# License: BSD

import argparse

from migen import *

from litex_boards.partner.platforms import max1000

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *

from litex.soc.integration.builder import *

from litedram.modules import MT48LC4M16
from litedram.phy import GENSDRPHY

from litex.soc.cores import gpio


class ClassicLed(gpio.GPIOOut):
    def __init__(self, pads):
        gpio.GPIOOut.__init__(self, pads)

# CRG ----------------------------------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        # # #

        self.cd_sys.clk.attr.add("keep")
        self.cd_sys_ps.clk.attr.add("keep")
        self.cd_por.clk.attr.add("keep")

        # clock input always available
        clk12 = platform.request("clk12")

        # power on rst
        rst_n = Signal()
        self.sync.por += rst_n.eq(1)
        self.comb += [
            self.cd_por.clk.eq(clk12),
            self.cd_sys.rst.eq(~rst_n),
            self.cd_sys_ps.rst.eq(~rst_n)
        ]

        clk_outs = Signal(5)

        self.comb += self.cd_sys.clk.eq(clk_outs[0]) # C0
        self.comb += self.cd_sys_ps.clk.eq(clk_outs[1]) # C1

        #
        # PLL we need 2 clocks one system one for SDRAM phase shifter
        # 

        self.specials += \
            Instance("ALTPLL",
                p_BANDWIDTH_TYPE="AUTO",
                p_CLK0_DIVIDE_BY=6,
                p_CLK0_DUTY_CYCLE=50,
                p_CLK0_MULTIPLY_BY=25,
                p_CLK0_PHASE_SHIFT="0",
                p_CLK1_DIVIDE_BY=6,
                p_CLK1_DUTY_CYCLE=50,
                p_CLK1_MULTIPLY_BY=25, 
                p_CLK1_PHASE_SHIFT="-10000",
                p_COMPENSATE_CLOCK="CLK0",
                p_INCLK0_INPUT_FREQUENCY=83000,
                p_INTENDED_DEVICE_FAMILY="MAX 10",
                p_LPM_TYPE = "altpll",
                p_OPERATION_MODE = "NORMAL",
                i_INCLK=clk12,
                o_CLK=clk_outs, # we have total max 5 Cx clocks
                i_ARESET=~rst_n,
                i_CLKENA=0x3f,
                i_EXTCLKENA=0xf,
                i_FBIN=1,
                i_PFDENA=1,
                i_PLLENA=1,
            )
        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCSDRAM):
#class BaseSoC(SoCCore):
    csr_peripherals = (
        "leds",
    )
#    csr_map.update(SoCCore.csr_map, csr_peripherals)

    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        assert sys_clk_freq == int(50e6)

        platform = max1000.Platform()

#        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq,
#                          integrated_rom_size=0x8000,
#                          **kwargs)


#    csr_map_update(SoCSDRAM.csr_map, csr_peripherals)

        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq,
            integrated_rom_size=0x6000,
#            integrated_main_ram_size=0x4000,
            **kwargs)
 

        self.submodules.crg = _CRG(platform)
 
#        self.submodules.leds = ClassicLed(Cat(platform.request("user_led", i) for i in range(7)))
        self.add_csr("leds", allow_user_defined=True)
        self.submodules.leds = ClassicLed(platform.request("user_led", 0))

#        self.add_csr("gpio_leds", allow_user_defined=True)
        self.add_csr("gpio_leds", allow_user_defined=True)
        self.submodules.gpio_leds = gpio.GPIOOut(platform.request("gpio_leds"))


# use micron device as winbond and ISSI not available

        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            sdram_module = MT48LC4M16(self.clk_freq, "1:1")
            self.register_sdram(self.sdrphy,
                                sdram_module.geom_settings,
                                sdram_module.timing_settings)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on MAX1000")
    builder_args(parser)

    soc_sdram_args(parser)
#    soc_core_args(parser)

    args = parser.parse_args()

    soc = BaseSoC(**soc_sdram_argdict(args))

#    cls = BaseSoC
#    soc = cls(**soc_core_argdict(args))


    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
