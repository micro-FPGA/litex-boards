#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# License: BSD

import argparse

from migen import *

from litex_boards.partner.platforms import sockit

#from litex.soc.integration.soc_sdram import *
from litex.soc.integration.soc_core import *

from litex.soc.integration.builder import *

#from litedram.modules import IS42S16320
#from litedram.phy import GENSDRPHY

# CRG ------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        # # #

        self.cd_sys.clk.attr.add("keep")
        self.cd_sys_ps.clk.attr.add("keep")
        self.cd_por.clk.attr.add("keep")

        # power on rst
        rst_n = Signal()
        self.sync.por += rst_n.eq(1)
        self.comb += [
            self.cd_por.clk.eq(self.cd_sys.clk),
            self.cd_sys.rst.eq(~rst_n),
            self.cd_sys_ps.rst.eq(~rst_n)
        ]

        # sys clk / sdram clk
        clk50 = platform.request("clk50")
        self.comb += self.cd_sys.clk.eq(clk50)
        self.specials += \
            Instance("ALTPLL",
                p_BANDWIDTH_TYPE="AUTO",
                p_CLK0_DIVIDE_BY=1,
                p_CLK0_DUTY_CYCLE=50,
                p_CLK0_MULTIPLY_BY=1,
                p_CLK0_PHASE_SHIFT="-3000",
                p_COMPENSATE_CLOCK="CLK0",
                p_INCLK0_INPUT_FREQUENCY=20000,
                p_OPERATION_MODE="ZERO_DELAY_BUFFER",
                i_INCLK=clk50,
                o_CLK=self.cd_sys_ps.clk,
                i_ARESET=~rst_n,
                i_CLKENA=0x3f,
                i_EXTCLKENA=0xf,
                i_FBIN=1,
                i_PFDENA=1,
                i_PLLENA=1,
            )
#        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

# BaseSoC --------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), **kwargs):
        assert sys_clk_freq == int(50e6)
        platform = sockit.Platform()
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
                          integrated_rom_size=0x8000,
                          integrated_main_ram_size=0x8000,
                          **kwargs)

        self.submodules.crg = _CRG(platform)



        self.counter = counter = Signal(32)
        self.sync += counter.eq(counter + 1)
 
        led_red = platform.request("user_led", 0)
        self.comb += led_red.eq(counter[23])


#        if not self.integrated_main_ram_size:
#            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
#            # ISSI IS42S16320D-7TL
#            sdram_module = IS42S16320(self.clk_freq, "1:1")
#            self.register_sdram(self.sdrphy,
#                                sdram_module.geom_settings,
#                                sdram_module.timing_settings)

# Build ----------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on SoCKit")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
