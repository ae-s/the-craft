#!/usr/bin/python3

class Port():
    def __init__(self, ship):
        # whatever
        self.peer = None
        self.ship = ship
        self.sleeve = False

    def connect(self, peer):
        self.peer = peer

    def connect2(self, peer):
        self.peer = peer
        peer.connect(self)

    def receive(self):
        self.ship.receive(self)
        self.sleeve = True

    def sleeve(self):
        return self.sleeve

class Subscriber():
    def __init__(self, numba, switchport):
        self.numba = numba
        self.port = Port(self)
        self.port.connect2(switchport)

    def receive(self):
        None

class Switch():
    def __init__(self):
        self.inports = []
        self.outports = []

    def mark(self, inports, outports):
        return [inp.sleeve() and outp.sleeve()
                for inp in inports
                for outp in outports]

    def reachable_inports(self, peerports):
        return [inp.peer == peerp
                for inp in self.inports
                for peerp in peerports]

    def reachable_outports(self, peerports):
        return [outp.peer == peerp
                for outp in self.outports
                for peerp in peerports]

class Strowger(Switch):
    def __init__(self):
        self.inports = [None]
        self.outports = [None, None, None, None, None]


Sa0 = Strowger()
Sb0 = Strowger()
Sb1 = Strowger()


Sa0.inports[0] = Port(Sa0)
Sub = Subscriber('20', Sa0.inports[0])

Sa0.outports[0] = Port(Sa0)
Sb0.inports[0] = Port(Sb0)
Sb0.inports[0].connect2(Sa0.outports[0])

Sa0.outports[1] = Port(Sa0)
Sb1.inports[0] = Port(Sb1)
Sb1.inports[0].connect2(Sa0.outports[1])


Sb0.outports[0] = Port(Sb0)
Sub = Subscriber('30', Sb0.outports[0])
Sb0.outports[1] = Port(Sb0)
Sub = Subscriber('31', Sb0.outports[1])

Sb1.outports[0] = Port(Sb1)
Sub = Subscriber('32', Sb1.outports[0])
Sb1.outports[1] = Port(Sb1)
Sub = Subscriber('33', Sb1.outports[1])

print 
