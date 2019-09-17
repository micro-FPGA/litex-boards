# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2016-2019 Florent Kermarrec <florent@enjoy-digital.fr>

# License: BSD

from migen import *
from migen.genlib.misc import timeline

from litex.gen import *

from litex.soc.interconnect import wishbone
#from litex.soc.interconnect.csr import *

# We need this as migen only has 1-bit oe on tristate signals
class mfioSinglePin(Module):
    def __init__(self, pads, pin, i, o, oe):
        self.pads = pads
        io = TSTriple(1)
        self.specials.io = io.get_tristate(pads[pin])
        self.comb += [
            i.eq(io.i),
            io.o.eq(o),
            io.oe.eq(oe)     
        ]

class mfioCommon(Module):
    def __init__(self, pads):
        self.pads = pads

class mfioBasic(mfioCommon):
    def __init__(self, pads):
        """
        MFIO simple core for LiteX
        
        """
        mfioCommon.__init__(self, pads)

        mfio_width = len(pads)
        #
        mfio_o  = Signal(mfio_width)
        mfio_oe = Signal(mfio_width)
        mfio_i  = Signal(mfio_width)
        # create single pin tristate buffers
        for b in range(mfio_width):
            self.submodules += mfioSinglePin(pads, b, mfio_i[b], mfio_o[b],  mfio_oe[b]) 	

        # Wishbone 
        self.bus = bus = wishbone.Interface()

        #
        sel     = Signal(mfio_width)
        inbit   = Signal(1)

        # todo: dynamic address width calc to optimize the decode logic
        addr_width = 12
        # 1024 IO max
        seladr  = Signal(10)

        # 10 bits of address = 1024 pins max
        self.comb += seladr.eq(self.bus.adr[:10]) 
      
        # address decoder
        for b in range(mfio_width):
            self.comb += sel[b].eq(seladr == b)

        self.comb += inbit.eq( (mfio_i & sel) != 0 )

        # Read bit
        rdbus = Signal(32)
        self.comb += [
            rdbus[0].eq(inbit),
            bus.dat_r.eq(rdbus)
        ]	

        # process output 
        outbit  = Signal(1)
        oebit   = Signal(1)
        wren    = Signal(1)

        self.comb += outbit.eq( bus.dat_w[0] )
        self.comb += oebit.eq ( bus.dat_w[1] )

        # write enable
        self.comb += wren.eq(self.bus.stb & self.bus.cyc & self.bus.we) 

        for b in range(mfio_width):
            self.sync += If(wren & sel[b], mfio_o[b].eq(outbit), mfio_oe[b].eq(oebit) )

        seq = [
            (1,        [bus.ack.eq(1)]), #
            (1,        [bus.ack.eq(0)]), #
            (0,        []),
        ]
 
        t, tseq = 0, []
        for dt, a in seq:
            tseq.append((t, a))
            t += dt

        self.sync += timeline(bus.cyc & bus.stb, tseq)

