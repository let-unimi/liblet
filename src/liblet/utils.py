from collections import deque
from collections.abc import Set, Iterable
from itertools import chain

from IPython.display import HTML


def peek(s):
    return next(iter(s)) if s else None

def union_of(s):
    return set().union(*s)

def letstr(obj, sep = None, sort = True):
    if sep is None: sep = ', '
    def _ls(obj):
        if isinstance(obj, str): return obj
        fs = None
        if isinstance(obj, Set):
            fs = '{{{}}}'
        elif isinstance(obj, list):
            fs = '[{}]'
        elif isinstance(obj, tuple):
            fs = '({})'
        if fs is None:
            return str(obj)
        else:
            if sep == '\n': fs = '{}'
            return fs.format(sep.join(sorted(map(_ls, obj)) if sorted else list(map(_ls, obj))))
    return _ls(obj)
    

class StatesQueueMap(object): # pragma: nocover

    def __init__(self, S0):
        self.queue = [S0]
        self.num = 0
        self.map = {frozenset(S0): 0, frozenset(): None}

    def getorput(self, IS):
        f = frozenset(IS)
        try:
            return self.map[f]
        except KeyError:
            self.num += 1
            self.map[f] = self.num
            self.queue.append(IS)
            return self.num

    def empty(self):
        return len(self.queue) == 0

    def pop(self):
        return self.queue.pop()

    def states(self):
        res = [None] * (1 + self.num)
        for IS, n in self.map.items():
            if n is not None: res[n] = set(IS)
        return res

class Queue(object):
    def __init__(self, iterable = None, maxlen = None):
        self.Q = deque(iterable, maxlen) if iterable is not None else deque(maxlen = maxlen)
    def enqueue(self, item):
        self.Q.append(item)
    def dequeue(self):
        return self.Q.popleft()
    def __repr__(self):
        return 'Queue({})'.format(', '.join(map(repr, self.Q)))
    def __len__(self):
        return len(self.Q)

class Stack(object):
    def __init__(self, iterable = None, maxlen = None):
        self.S = deque(iterable, maxlen) if iterable is not None else deque(maxlen = maxlen)
    def push(self, item):
        self.S.append(item)
    def pop(self):
        return self.S.pop()
    def __repr__(self):
        return 'Stack({})'.format(', '.join(map(repr, self.S)))
    def __len__(self):
        return len(self.S)

