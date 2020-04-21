from functools import partial
from collections import deque
from collections.abc import Set, Iterable
from itertools import chain
from sys import stderr

from IPython.display import HTML

def warn(msg):
    """Emits a string on the *standard error*."""
    stderr.write(msg + '\n')

def peek(s):
    """Returns the fist element of the given :obj:`set`."""
    return next(iter(s)) if s else None

def union_of(s):
    """Return the set union of its arguments."""
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
            return fs.format(sep.join(sorted(map(_ls, obj)) if sort else list(map(_ls, obj))))
    return _ls(obj)

class Queue(object):
    """A convenience implementation of a *queue* providing the usual ``enqueue``, ``dequeue``, and ``copy`` methods."""
    def __init__(self, iterable = None, maxlen = None):
        self.Q = deque(iterable, maxlen) if iterable is not None else deque(maxlen = maxlen)
    def enqueue(self, item):
        self.Q.append(item)
    def dequeue(self):
        return self.Q.popleft()
    def copy(self):
        return Queue(self.Q, self.Q.maxlen)
    def __iter__(self):
        return iter(self.Q)
    def __repr__(self):
        el = ', '.join(map(repr, self.Q))
        return 'Queue({})'.format('← {} ←'.format(el) if el else '')
    def __len__(self):
        return len(self.Q)

class Stack(object):
    """A convenience implementation of a *stack* providing the usual ``push``, ``pop``, ``peek``, and ``copy`` methods."""
    def __init__(self, iterable = None, maxlen = None):
        self.S = deque(iterable, maxlen) if iterable is not None else deque(maxlen = maxlen)
    def push(self, item):
        self.S.append(item)
    def peek(self):
        return self.S[-1]
    def pop(self):
        return self.S.pop()
    def copy(self):
        return Stack(self.S, self.S.maxlen)
    def __iter__(self):
        return iter(self.S)
    def __repr__(self):
        el = ', '.join(map(repr, self.S))
        return 'Stack({})'.format('{} ↔'.format(el) if el else '')
    def __len__(self):
        return len(self.S)

def uc(s, c = ''):
    return ''.join(map(lambda _: _ + c, s))

uc.dot = partial(uc, c = '\u0307')
uc.overline = partial(uc, c = '\u0305')
uc.prime = partial(uc, c = '\u031b')