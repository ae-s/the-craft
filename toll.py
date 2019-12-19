#!/usr/bin/python3

import random

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

    def pick_trunk(self, dest_exchange):
        group = self.trunkgroups[dest_exchange.name]
        for t in group:
            if t.sleeve == False:
                return t

    def call_orig(self, dest_exchange, numba):
        # originate a call
        trunk = self.pick_trunk(dest_exchange)
        if trunk is None:
            return ["congestion"]
        trunk.sleeve = True
        result = dest_exchange.call_term(dest_exchange, numba, trunk)
        result.append(trunk)
        return result

    def call_term(self, dest_exchange, numba, inc_trk):
        if dest_exchange == self:
            # terminate
            return self.subscribers[numba].receive_call(inc_trk)
        else:
            # tandem
            # XXX unimplemented
            None

    def addsub(self, numba, sub):
        self.subscribers[numba] = sub

class Subscriber():
    def __init__(self, exchange, numba, name, kind = "resi"):
        self.exchange = exchange
        self.numba = numba
        self.name = name
        self.kind = kind
        exchange.addsub(numba, self)
        self.sleeve = False
        self.cur_call = None

    def call(self, far_exchange, numba):
        cur_call = self.exchange.call_orig(far_exchange, numba)
        result = cur_call.pop(0)
        self.cur_call = cur_call
        return result

    def hangup(self):
        for trunk in self.cur_call:
            trunk.sleeve = False

    def receive_call(self, inc_trunk):
        self.sleeve = True
        return(["hello this is " + self.name, self])

wav = Exchange("waverly")
mel = Exchange("melrose")

# interoffice
wav.provision(mel, 2)
mel.provision(wav, 2)

# intraoffice
wav.provision(wav, 6)
mel.provision(mel, 6)

def populate(exchange, quantity):
    for i in range(quantity):
        n = random.randrange(10)
        if (n < 1):
            # 10% are businesses
            kind = "bus"
        else:
            # 90% are resi
            kind = "resi"
        Subscriber(exchange,
                   "{:0>4d}".format(i),
                   "{} {}".format(kind, n),
                   kind)


populate(wav, 100)

Joe0 = Subscriber(mel, '0010', 'Joe')
Joe1 = Subscriber(mel, '0011', 'Ted')
Joe2 = Subscriber(mel, '0012', 'Bill')
Joe3 = Subscriber(mel, '0013', 'Marty')
Joe4 = Subscriber(mel, '0014', 'eeeeeeee')
Joe5 = Subscriber(mel, '0015', 'x')
Joe6 = Subscriber(mel, '0016', 'x')
Joe7 = Subscriber(mel, '0017', 'x')
Joe8 = Subscriber(mel, '0018', 'x')
Subscriber(mel, '0019', 'x')
Subscriber(mel, '0020', 'x')

print(Joe0.call(wav, '0010'))
print(Joe1.call(wav, '0011'))
Joe0.hangup()
print(Joe2.call(wav, '0012'))
print(Joe3.call(wav, '0013'))
print(Joe4.call(wav, '0014'))
Joe1.hangup()
Joe2.hangup()
print(Joe5.call(wav, '0015'))
print(Joe6.call(wav, '0016'))
print(Joe7.call(wav, '0017'))
print(Joe8.call(wav, '0018'))
