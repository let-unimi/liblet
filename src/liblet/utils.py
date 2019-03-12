from collections import deque
from collections.abc import Set, Iterable
from itertools import chain

from IPython.display import HTML


def peek(s):
    return next(iter(s)) if s else None

def union(s):
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
    
def iter2table(it):
    return HTML('<table>' + '\n'.join(f'<tr><th>{n}<td style="text-align:left"><pre>{e}</pre>' for n, e in enumerate(it)) + '</table>')

def dod2html(dod):
    def fmt(r, c):
        if not c in dod[r]: return '&nbsp;'
        elem = dod[r][c]
        if elem is None: return '&nbsp;'
        if isinstance(elem, list) or isinstance(elem, tuple) or isinstance(elem, set):
            return ', '.join(map(str, elem))
        else:
            return str(elem)
    rows = sorted(dod.keys())
    cols = sorted(set(chain.from_iterable(dod[x].keys() for x in dod)))
    head = '<tr><td>&nbsp;<th>' + '<th>'.join(cols)
    body = '\n'.join('<tr><th>{}<td>{}'.format(r, '<td>'.join(fmt(r, c) for c in cols))for r in rows)
    return HTML('<table class="table table-bordered">\n{}\n{}\n</table>'.format(head, body))

class StatesQueueMap(object):

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

