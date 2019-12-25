#!/usr/bin/python3

import random
import time
from configparser import ConfigParser
import re

subscriberlist = []
service = {
    "OK": 0,
    "NC": 0,
    "BY": 0,
    "EQ": 0,
}

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
                     "congestion": 0,
                     }
        # randomly drop 0.1% of calls
        self.shittiness = 0.001

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
        # first route
        group = self.trunkgroups[dest_exchange.name]
        for t in group:
            if t.sleeve == False:
                return t
        # second route
        return None

    def call_orig(self, dest_exchange, numba):
        # originate a call
        self.score_peg("attempt")
        trunk = self.pick_trunk(dest_exchange)
        if trunk is None:
            self.score_peg("congestion")
            print('{}: congestion towards {}'.format(self.name, dest_exchange.name))
            return dict(fate="congestion", service="NC", trunks=[])

        trunk.sleeve = True
        call = dest_exchange.call_term(dest_exchange, numba, trunk)
        call["trunks"].append(trunk)
        return call

    def call_term(self, dest_exchange, numba, inc_trk):
        if random.uniform(0,1) < self.shittiness:
            return dict(fate="equipment trouble", service="EQ", trunks=[])
        if dest_exchange == self:
            # terminate
            call = self.subscribers[numba].receive_call(inc_trk)
            call["trunks"] = []
            return call
        else:
            # tandem
            # XXX unimplemented
            return dict(fate="error: not a tandem", service="ER", trunks=[])

    def addsub(self, numba, sub):
        #print("{} new subscriber {} {}".format(self.name, numba, sub.name))
        self.subscribers[numba] = sub
        subscriberlist.append(sub)

    def score_peg(self, peg):
        self.pegs[peg] += 1
    def print_pegs(self):
        print("hourly report from {}: {}att / {}ok / {}nc {}by".
              format(self.name,
                     self.pegs["attempt"],
                     self.pegs["congestion"],
                     self.pegs["OK"],
                     self.pegs["NC"],
                     self.pegs["BY"]))


    def hourly(self):
        self.pegs = {"attempt": 0,
                     "congestion": 0,
                     "OK": 0,
                     "NC": 0,
                     "BY": 0,
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
        service[cur_call["service"]] += 1
        self.cur_call = cur_call
        return "sub {}-{} calls {}-{} and hears \"{}\"".format(
            self.exchange.name, self.numba, far_exchange.name, numba, result)

    def hangup(self):
        if self.cur_call == None:
            return "nothing"
        res = "sub {}-{} hangs up releasing {} trunks".format(
            self.exchange.name, self.numba, len(self.cur_call["trunks"]))
        if "term_sub" in self.cur_call:
            self.cur_call["term_sub"].sleeve = False
        for trunk in self.cur_call["trunks"]:
            trunk.sleeve = False
        self.cur_call = None
        return res

    def receive_call(self, inc_trunk):
        if self.sleeve == True:
            return dict(fate="busy",
                        service="BY",
                        trunks=[])

        self.sleeve = True
        return dict(term_sub=self,
                    fate="hello this is " + self.name,
                    service="OK",
                    trunks=[])

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

def populate(exchange, quantity):
    for i in range(quantity):
        n = random.randrange(10)
        if (n < 1):
            # 10% are businesses
            kind = "bus"
        else:
            # 90% are resi
            kind = "resi"
        print("populating", kind, exchange.name)
        Subscriber(exchange,
                   "{:0>4d}".format(i),
                   "{}-{}".format(kind, i),
                   kind)

config = ConfigParser()
config.read_file(open('smalltown.ini'))

exchanges = dict()
for sect in config.sections():
    e = Exchange(sect)
    exchanges[sect] = e
    print("made new exchange", sect)

pattern = re.compile("tg\.(.*)")
for name in exchanges:
    e = exchanges[name]
    for k, v in config.items(name):
        m = pattern.match(k)
        if m:
            towards = m.group(1)
            count = config.getint(name, k)
            e.provision(exchanges[towards], count)
            print("added N trunks from X to Y", count, name, towards)
        elif k == "subs":
            subs = config.getint(name, "subs")
            populate(e, subs)
            print("added N subs to", name, subs)

actives = subscriberlist

for a in actives:
    a.set_friends(random.sample(subscriberlist, 15))

for N in range(24):
    print("=================== hour", N)
    actions = []
    for subscriber in actives:
        actions.extend(subscriber.hourly())

    for switch in exchanges:
        actions.extend(exchanges[switch].hourly())

    print("{} actions to do".format(len(actions)))

    actions.sort(key = lambda tup: tup[0])
    #actionlist = sorted(actions, key=lambda tup: tup[0])
    last_t = 0
    for action in actions:
        #print(action)
        (t, callback,) = action
        #time.sleep((t - last_t)/60)
        last_t = t
        cbres = callback()
        print("{}:{:0>2d}".format(N, t), cbres)

    print("service summary:", service)
