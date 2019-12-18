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
    def __init__(self, exchange, numba, name):
        self.exchange = exchange
        self.numba = numba
        self.name = name
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

Joe0 = Subscriber(mel, '10', 'Joe')
Joe1 = Subscriber(mel, '11', 'Ted')
Joe2 = Subscriber(mel, '12', 'Bill')
Joe3 = Subscriber(mel, '13', 'Marty')
Joe4 = Subscriber(mel, '14', 'eeeeeeee')
Joe5 = Subscriber(mel, '15', 'x')
Joe6 = Subscriber(mel, '16', 'x')
Joe7 = Subscriber(mel, '17', 'x')
Joe8 = Subscriber(mel, '18', 'x')
Subscriber(mel, '19', 'x')
Subscriber(mel, '20', 'x')

Subscriber(wav, '10', 'operator')
Subscriber(wav, '11', 'the library')
Subscriber(wav, '12', 'city hall')
Subscriber(wav, '13', 'transit')
Subscriber(wav, '14', 'tax bureau')
Subscriber(wav, '15', 'dogcatcher')
Subscriber(wav, '16', 'the other library')
Subscriber(wav, '17', 'x')
Subscriber(wav, '18', 'x')
Subscriber(wav, '19', 'x')
Subscriber(wav, '20', 'x')

print(Joe0.call(wav, '10'))
print(Joe1.call(wav, '11'))
Joe0.hangup()
print(Joe2.call(wav, '12'))
print(Joe3.call(wav, '13'))
print(Joe4.call(wav, '14'))
Joe1.hangup()
Joe2.hangup()
print(Joe5.call(wav, '15'))
print(Joe6.call(wav, '16'))
print(Joe7.call(wav, '17'))
print(Joe8.call(wav, '18'))
