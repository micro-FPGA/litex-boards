# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>

# This file is Copyright (c) 2014 Yann Sionneau <ys@m-labs.hk>
# This file is Copyright (c) 2015-2018 Florent Kermarrec <florent@enjoy-digital.fr>
# This file is Copyright (c) 2015 Sebastien Bourdeauducq <sb@m-labs.hk>
# This file is Copyright (c) 2018 Tim 'mithro' Ansell <me@mith.ro>
# License: BSD

from migen import *
from migen.genlib.record import Record

from litex.soc.interconnect.csr import *
from litex.soc.interconnect.csr_eventmanager import *

class JTAG_atlantic(Module):
    def __init__(self):
        #      
        self.rst_n     = Signal(reset=1)

        self.tx_valid = Signal()
        self.tx_ready = Signal()
        self.tx_data  = Signal(8)

        self.rx_valid = Signal()
        self.rx_ready = Signal()
        self.rx_pause = Signal()
        self.rx_data  = Signal(8)

        self.specials += Instance("alt_jtag_atlantic",
            p_INSTANCE_ID             =  0,
            p_LOG2_RXFIFO_DEPTH       = "0", # should be 0, but not recognized by migen?
            p_LOG2_TXFIFO_DEPTH       = "0", #
            p_SLD_AUTO_INSTANCE_INDEX = "YES",
            i_clk     = ClockSignal("sys"), 
            i_rst_n   = self.rst_n,
            #
            i_r_dat   = self.tx_data,
            i_r_val   = self.tx_valid,
            o_r_ena   = self.tx_ready,
            # transmit part of uart - our RX
            o_t_dat   = self.rx_data,
            i_t_dav   = self.rx_ready,
            o_t_ena   = self.rx_valid,
            o_t_pause = self.rx_pause
        )


# Altera Atlantic JTAG UART ----------------------------------------------------------------------------------------

class UART_atlantic(Module, AutoCSR):
    def __init__(self,
                 tx_fifo_depth=16,
                 rx_fifo_depth=16):
        self._rxtx = CSR(8)
        self._txfull = CSRStatus()
        self._rxempty = CSRStatus()

        self.submodules.ev = EventManager()
        self.ev.tx = EventSourceProcess()
        self.ev.rx = EventSourceProcess()
        self.ev.finalize()

        # # #
        jtag = JTAG_atlantic()
        self.submodules += jtag

        # TX
        self.comb += [
            jtag.tx_valid.eq(self._rxtx.re),
            jtag.tx_data.eq(self._rxtx.r),
            self._txfull.status.eq(~jtag.tx_ready),
            # Generate TX IRQ when tx_fifo becomes non-full
            self.ev.tx.trigger.eq(~jtag.tx_ready)
        ]

        # RX
        self.comb += [
            self._rxempty.status.eq(~jtag.rx_valid),
            self._rxtx.w.eq(jtag.rx_data),
            jtag.rx_ready.eq(self.ev.rx.clear),
            # Generate RX IRQ when rx_fifo becomes non-empty
            self.ev.rx.trigger.eq(~jtag.rx_valid)
        ]

