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

#    i_jtag_uart : component alt_jtag_atlantic
#        generic map
#        (
#            INSTANCE_ID                 => 0,
#            LOG2_RXFIFO_DEPTH           => LOG2_RXFIFO_DEPTH,
#            LOG2_TXFIFO_DEPTH           => LOG2_TXFIFO_DEPTH,
#            SLD_AUTO_INSTANCE_INDEX     => "YES"
#        )
#        port map
#        (
#            clk                         => clk,
#            rst_n                       => reset_n,
#
#            -- alt_jtag_atlantic ports have _very_ strange (kind of backwards) names...
#            
#            -- this is the receiving part of alt_jtag_atlantic, the ports
#            -- we actually *send* data to
#            r_dat                       => tx_data,
#            r_val                       => tx_start,
#            r_ena                       => tx_idle,
#
#            -- this is the sending part of alt_jtag_atlantic, i.e. the ports
#            -- we receive data from
#            t_dat                       => rx_data,
#            t_dav                       => rx_data_req,
#            t_ena                       => rx_ready,
#            t_pause                     => rx_paused
#        );


        self.specials += Instance("alt_jtag_atlantic",
            #p_INSTANCE_ID             =  0, # should be 0, can not be "0"
            p_LOG2_RXFIFO_DEPTH       = "0", # should be 0, but not recognized by migen?
            p_LOG2_TXFIFO_DEPTH       = "0", # "0" is OK, can not be left out
            p_SLD_AUTO_INSTANCE_INDEX = "YES",
            i_clk     = ClockSignal("sys"), 
            i_rst_n   = ~ResetSignal("sys"), #self.rst_n,
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

        #
        self.submodules.jtag = JTAG_atlantic()
        # latch jtag data
        rx_data = Signal(8)
        tx_data = Signal(8)
        tx_valid = Signal()
        tx_pending = Signal()
        tx_busy = Signal()

        self.sync += [
            If(self.jtag.rx_valid,
                rx_data.eq(self.jtag.rx_data)
            ),
            If(self._rxtx.re,
                tx_data.eq(self._rxtx.r), # latch tx data
                tx_pending.eq(1),         # 
                tx_busy.eq(1),         # 
            ),

            If(tx_pending & self.jtag.tx_ready,
                tx_valid.eq(1),           # 
                tx_pending.eq(0)
            ),

            If(tx_valid & ~self.jtag.tx_ready,
                tx_valid.eq(0),            # clear valid
                tx_busy.eq(0),         # 
            ),


        ]


        # TX
        self.comb += [
            self.jtag.tx_valid.eq(tx_valid),
            self.jtag.tx_data.eq(tx_data),
            self._txfull.status.eq(~self.jtag.tx_ready | tx_busy),
            # Generate TX IRQ when tx_fifo becomes non-full
            self.ev.tx.trigger.eq(~self.jtag.tx_ready | tx_busy)
        ]

        # RX
        self.comb += [
            self._rxempty.status.eq(~self.jtag.rx_valid),
#            self._rxtx.w.eq(self.jtag.rx_data),
            self._rxtx.w.eq(rx_data),
            self.jtag.rx_ready.eq(self.ev.rx.clear),
            # Generate RX IRQ when rx_fifo becomes non-empty
            self.ev.rx.trigger.eq(~self.jtag.rx_valid)
        ]

