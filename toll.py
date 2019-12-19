#!/usr/bin/python3

import random
import time

subscriberlist = []

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
        self.pegs = {"attempt": 0,
                     "complete": 0,
                     "congestion": 0
                     }

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
        self.score_peg("attempt")
        trunk = self.pick_trunk(dest_exchange)
        if trunk is None:
            self.score_peg("congestion")
            return dict(fate="congestion", trunks=[])

        trunk.sleeve = True
        call = dest_exchange.call_term(dest_exchange, numba, trunk)
        call["trunks"].append(trunk)
        return call

    def call_term(self, dest_exchange, numba, inc_trk):
        if dest_exchange == self:
            # terminate
            call = self.subscribers[numba].receive_call(inc_trk)
            call["trunks"] = []
            return call
        else:
            # tandem
            # XXX unimplemented
            return dict(fate="error: not a tandem", trunks=[])

    def addsub(self, numba, sub):
        #print("{} new subscriber {} {}".format(self.name, numba, sub.name))
        self.subscribers[numba] = sub
        subscriberlist.append(sub)

    def score_peg(self, peg):
        self.pegs[peg] += 1
    def print_pegs(self):
        print("hourly report from {}: {}att / {}cpl / {}cong".
              format(self.name,
                     self.pegs["attempt"],
                     self.pegs["complete"],
                     self.pegs["congestion"]))


    def hourly(self):
        self.pegs = {"attempt": 0,
                     "complete": 0,
                     "congestion": 0
                     }
        return [ (60, lambda: self.print_pegs()) ]


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
        result = cur_call["fate"]
        self.cur_call = cur_call
        return "sub {}-{} calls {}-{} and hears \"{}\"".format(self.exchange.name, self.numba, far_exchange.name, numba, result)

    def hangup(self):
        res = "sub {}-{} hangs up releasing {} trunks".format(self.exchange.name, self.numba, len(self.cur_call["trunks"]))
        for trunk in self.cur_call["trunks"]:
            trunk.sleeve = False
        return res

    def receive_call(self, inc_trunk):
        self.sleeve = True
        return dict(term_sub=self, fate="hello this is " + self.name, trunks=[])

    def set_friends(self, friends):
        self.friends = friends

    def hourly(self):
        n = random.randrange(10)
        if n < 1:
            # 10% chance of placing two calls
            Friend = random.sample(self.friends, 2)
            Atime = random.randrange(60)
            Btime = random.randrange(60)
            return [ (Atime, lambda: self.call(Friend[0].exchange, Friend[0].numba)) ,
                     (Atime + 2, lambda: self.hangup()) ,
                     (Btime, lambda: self.call(Friend[1].exchange, Friend[1].numba)),
                     (Btime + 2, lambda: self.hangup())
        ]
        elif n < 4:
            # 30% chance of placing one call
            A = random.sample(self.friends, 1)
            Atime = random.randrange(60)
            return [ (Atime, lambda: self.call(A[0].exchange, A[0].numba)),
                     (Atime + 2, lambda: self.hangup())
            ]
        else:
            return []

wav = Exchange("waverly")
mel = Exchange("melrose")
rai = Exchange("rainier")

exchanges = [wav, mel, rai]

# interoffice
wav.provision(mel, 2)
wav.provision(rai, 2)
mel.provision(wav, 2)
mel.provision(rai, 2)
rai.provision(wav, 2)
rai.provision(mel, 2)

# intraoffice
wav.provision(wav, 6)
mel.provision(mel, 6)
rai.provision(rai, 6)

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
                   "{}-{}".format(kind, i),
                   kind)


populate(wav, 100)
populate(rai, 100)

Joe0 = Subscriber(mel, '0010', 'Joe')
Joe1 = Subscriber(mel, '0011', 'Ted')
Joe2 = Subscriber(mel, '0012', 'Bill')
Joe3 = Subscriber(mel, '0013', 'Marty')
Joe4 = Subscriber(mel, '0014', 'eeeeeeee')
Joe5 = Subscriber(mel, '0015', 'x')
Joe6 = Subscriber(mel, '0016', 'y')
Joe7 = Subscriber(mel, '0017', 'z')
Joe8 = Subscriber(mel, '0018', 'w')
Subscriber(mel, '0019', 'city hall')
Subscriber(mel, '0020', 'u')

#actives = [Joe0, Joe1, Joe2, Joe3, Joe4, Joe5, Joe6, Joe7, Joe8, mel, wav, rai]
actives = subscriberlist

for a in actives:
    a.set_friends(random.sample(subscriberlist, 6))

for N in range(6):
    print("=================== hour", N)
    actions = []
    for subscriber in actives:
        actions.extend(subscriber.hourly())

    for switch in exchanges:
        actions.extend(switch.hourly())

    actions.sort(key = lambda tup: tup[0])
    #actionlist = sorted(actions, key=lambda tup: tup[0])
    last_t = 0
    for action in actions:
        #print(action)
        (t, callback,) = action
        #time.sleep((t - last_t)/60)
        last_t = t
        cbres = callback()
        #print("{}:{:0>2d}".format(N, t), cbres)
