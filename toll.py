#!/usr/bin/python3

class Trunk():
    def __init__(self):
        self.dest = None
        self.sleeve = False

    def connect(self, other):
        self.dest = other

class Exchange():
    def __init__(self, name):
        self.name = name
        self.subscribers = dict()
        self.trunkgroups = dict()

    def provision(self, to_office, count):
        far_name = to_office.name
        group = []
        for _ in range(count):
            t = Trunk()
            t.connect(to_office)
            to_office.provision_incoming(t, self)
            group.append(t)
        self.trunkgroups[far_name] = group

    def provision_incoming(self, trunk, from_office):
        None

    def pick_trunk(self, far_exchange):
        group = self.trunkgroups[far_exchange.name]
        for t in group:
            if t.sleeve == False:
                return t

    def call(self, far_exchange, numba, inc_trk):
        if inc_trk is None:
            # originate a call
            trunk = self.pick_trunk(far_exchange)
            if trunk is None:
                return "congestion"
            trunk.sleeve = True
            return far_exchange.call(far_exchange, numba, trunk)
        else:
            # terminate or tandem a call
            if far_exchange == self:
                # terminate
                return self.subscribers[numba].receive_call(inc_trk)
            else:
                # tandem
                # XXX unimplemented
                None

    def addsub(self, numba, sub):
        self.subscribers[numba] = sub

class Subscriber():
    def __init__(self, exchange, numba, name):
        self.exchange = exchange
        self.numba = numba
        self.name = name
        exchange.addsub(numba, self)

    def call(self, far_exchange, numba):
        return self.exchange.call(far_exchange, numba, None)

    def receive_call(self, trunk):
        return("hello this is " + self.name)

wav = Exchange("waverly")
mel = Exchange("melrose")

# interoffice
wav.provision(mel, 2)
mel.provision(wav, 2)

# intraoffice
wav.provision(wav, 6)
mel.provision(mel, 6)

Joe0 = Subscriber(mel, '10', 'x')
Joe1 = Subscriber(mel, '11', 'x')
Joe2 = Subscriber(mel, '12', 'x')
Joe3 = Subscriber(mel, '13', 'x')
Joe4 = Subscriber(mel, '14', 'x')
Joe5 = Subscriber(mel, '15', 'x')
Joe6 = Subscriber(mel, '16', 'x')
Joe7 = Subscriber(mel, '17', 'x')
Joe8 = Subscriber(mel, '18', 'x')
Subscriber(mel, '19', 'x')
Subscriber(mel, '20', 'x')

Subscriber(wav, '10', 'x')
Subscriber(wav, '11', 'x')
Subscriber(wav, '12', 'x')
Subscriber(wav, '13', 'x')
Subscriber(wav, '14', 'x')
Subscriber(wav, '15', 'x')
Subscriber(wav, '16', 'x')
Subscriber(wav, '17', 'x')
Subscriber(wav, '18', 'x')
Subscriber(wav, '19', 'x')
Subscriber(wav, '20', 'x')

print(Joe0.call(wav, '10'))
print(Joe1.call(wav, '10'))
print(Joe2.call(wav, '10'))
print(Joe3.call(wav, '10'))
print(Joe4.call(wav, '10'))
print(Joe5.call(wav, '10'))
print(Joe6.call(wav, '10'))
print(Joe7.call(wav, '10'))
print(Joe8.call(wav, '10'))
