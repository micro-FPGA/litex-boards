#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.partner.platforms import te0725

from litex.soc.interconnect import wishbone

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from litex.soc.cores.spi_flash import SpiFlash

from hyper_memory import *

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()

        # # #
        self.cd_sys.clk.attr.add("keep")
        self.submodules.pll = pll = S7PLL(speedgrade=-2)
        self.comb += pll.reset.eq(platform.request("cpu_reset"))

        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)


# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
#    csr_map = (
#        "spiflash",
#    )
#    csr_map.update(SoCCore.csr_map, csr_map)

    mem_map = {
        "spiflash": 0x20000000,
        "hyperram": 0x40000000,
    }
    mem_map.update(SoCCore.mem_map)


    def __init__(self, sys_clk_freq=int(100e6), spiflash="spiflash_4x", **kwargs):

        platform = te0725.Platform()

        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
            ident="TE0725", ident_version=True,
            integrated_rom_size=0x8000,
#            integrated_main_ram_size=0x8000,
            **kwargs)

	# can we just use the clock without PLL ?

        self.submodules.crg = _CRG(platform, sys_clk_freq)

        self.add_csr("spiflash", allow_user_defined=True)

        spiflash_dummy = {
            "spiflash_1x": 9, # not tested - need change
            "spiflash_4x": 6, # works but why?
        }

        spiflash_pads = platform.request(spiflash)
        self.submodules.spiflash = SpiFlash(
                spiflash_pads,
                dummy=spiflash_dummy[spiflash],
                div=4,
                endianness=self.cpu.endianness)

        self.spiflash.add_clk_primitive("xc7");	

        #32 Mbyte spansion flash, note there is no pullup on D2, but spi flah ic has internal one?
        self.add_constant("SPIFLASH_PAGE_SIZE", 256)
        self.add_constant("SPIFLASH_SECTOR_SIZE", 0x10000)

        # spi_flah.py supports max 16MB linear space
        self.add_wb_slave(mem_decoder(self.mem_map["spiflash"]), self.spiflash.bus)
        self.add_memory_region(
            "spiflash", self.mem_map["spiflash"] | self.shadow_base, 16*1024*1024)

        hyperram_pads = platform.request("hyperram")
        self.submodules.hyperram = HyperRAM(
                hyperram_pads)

        self.add_wb_slave(mem_decoder(self.mem_map["hyperram"]), self.hyperram.bus)
        self.add_memory_region(
            "hyperram", self.mem_map["hyperram"] | self.shadow_base, 8*1024*1024)


        self.counter = counter = Signal(32)
        self.sync += counter.eq(counter + 1)
 
	#
        led_red = platform.request("user_led", 0)
        self.comb += led_red.eq(counter[23])

#        led_green = platform.request("user_led_green")
#        self.comb += led_green.eq(counter[25])


# ila
##        platform.add_source("ila_0/ila_0.xci")
##        probe0 = Signal(40)
#        self.comb += probe0.eq(Cat(spi_pads.clk, spi_pads.cs_n, spi_pads.wp, spi_pads.hold, spi_pads.miso, spi_pads.mosi))

##        self.comb += probe0.eq(Cat(counter))
##        self.specials += [
##            Instance("ila_0", i_clk=self.crg.cd_sys.clk, i_probe0=probe0),
##            ]
#        platform.toolchain.additional_commands +=  [
#            "write_debug_probes -force {build_name}.ltx",
#        ]


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX on TE0725")
    builder_args(parser)
#    soc_sdram_args(parser)
    soc_core_args(parser)

    args = parser.parse_args()

    cls = BaseSoC

    soc = cls(**soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
