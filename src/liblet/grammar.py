from collections import namedtuple
from itertools import chain
from operator import attrgetter

from . import ε
from .utils import letstr


def _letlrhstostr(s):
    return ''.join(map(str, s)) if isinstance(s, tuple) else str(s)

class Production:
    __slots__ = ('lhs', 'rhs')
    def __init__(self, lhs, rhs):
        if isinstance(lhs, str):
            self.lhs = lhs
        elif isinstance(lhs, (list, tuple)) and all(map(lambda _: isinstance(_, str), lhs)): 
            self.lhs = tuple(lhs)
        else:
            raise ValueError('The lhs is not a str, nor a list/tuple of str')
        if isinstance(rhs, (list, tuple)) and all(map(lambda _: isinstance(_, str), rhs)): 
            self.rhs = tuple(rhs)
        else:
            raise ValueError('The rhs must be a list/tuple of str')        
    def __eq__(self, other):
        if not isinstance(other, Production): return False
        return (self.lhs, self.rhs) == (other.lhs, other.rhs)
    def __hash__(self):
        return hash((self.lhs, self.rhs))
    def __iter__(self):
        return iter((self.lhs, self.rhs))
    def __repr__(self):
        return '{} -> {}'.format(_letlrhstostr(self.lhs), _letlrhstostr(self.rhs))
    @classmethod 
    def from_string(cls, prods, context_free = False):
        P = []
        for p in prods.splitlines():
            if not p.strip(): continue
            lh, rha = p.split('->')
            lhs = tuple(lh.split())
            if context_free:
                if len(lhs) != 1: raise ValueError('Production "{}" as more than one symbol as left-hand side'.format(p))
                lhs = lhs[0]
            for rh in rha.split('|'):
                P.append(cls(lhs, tuple(rh.split())))
        return tuple(P)


class Item(Production): # pragma: no cover
    __slots__ = ('pos',)
    def __init__(self, lhs, pos, rhs):
        if isinstance(lhs, (list, tuple)):
            raise ValueError('The lhs must be a str')
        super().__init__(lhs, rhs)
        self.pos = pos
    def __eq__(self, other):
        if not isinstance(other, Item): return False
        return (self.lhs, self.pos, self.rhs) == (other.lhs, other.pos, other.rhs)
    def __hash__(self):
        return hash((self.lhs, self.pos, self.rhs))
    def __iter__(self):
        return iter((self.lhs, self.pos, self.rhs))
    def __repr__(self):
        return '{} -> {}•{}'.format(_letlrhstostr(self.lhs), _letlrhstostr(self.rhs[:self.pos]), _letlrhstostr(self.rhs[self.pos:]))


class EarleyItem(Item):  # pragma: no cover
    __slots__ = ('orig', )
    def __init__(self, lhs, pos, rhs, orig):
        if isinstance(lhs, (list, tuple)):
            raise ValueError('The lhs must be a str')
        super().__init__(lhs, pos, rhs)
        self.orig = orig
    def __eq__(self, other):
        if not isinstance(other, EarleyItem): return False
        return (self.lhs, self.pos, self.rhs, self.orig) == (other.lhs, other.pos, other.rhs, other.orig)
    def __hash__(self):
        return hash((self.lhs, self.pos, self.rhs, self.orig))
    def __iter__(self):
        return iter((self.lhs, self.pos, self.rhs, self.orig))
    def __repr__(self):
        return '{} -> {}•{}@{}'.format(_letlrhstostr(self.lhs), _letlrhstostr(self.rhs[:self.pos]), _letlrhstostr(self.rhs[self.pos:]), self.orig)


class Grammar:
    
    __slots__ = ('N', 'T', 'P', 'S')

    def __init__(self, N, T, P, S):
        self.N = frozenset(N)
        self.T = frozenset(T)
        self.P = tuple(P)
        self.S = S

    @classmethod
    def from_string(cls, prods, context_free = True):
        P = Production.from_string(prods, context_free)
        if context_free:
            S = P[0].lhs
            N = set(map(attrgetter('lhs'), P))
            T = set((chain.from_iterable(map(attrgetter('rhs'), P)))) - N - {ε}
        else:
            S = P[0].lhs[0]
            symbols = set(chain.from_iterable(map(attrgetter('lhs'), P))) | set(chain.from_iterable(map(attrgetter('rhs'), P)))
            N = set(_ for _ in symbols if _[0].isupper())
            T = symbols - N - {ε}
        return cls(N, T, P, S)

    def rhs(self, N): 
        return (P.rhs for P in self.P if P.lhs == N)

    def all_terminal(self, word):
        return all(_ in self.T for _ in word)

    def __repr__ (self):
        return 'Grammar(N={}, T={}, P={}, S={})'.format(letstr(self.N), letstr(self.T), self.P, letstr(self.S))


class Derivation:

    def __init__(self, G):
        self.G = G
        self._sf = [G.S]
        self._repr = G.S
        self._steps = []

    def step(self, prod, pos): # consider adding rightmost/leftmost (with no pos)
        sf = self._sf
        P = self.G.P[prod]
        if tuple(sf[pos: pos + len(P.lhs)]) != P.lhs: raise ValueError('Cannot apply {} at position {} of {}'.format(P, pos, ''.join(sf)))
        copy = Derivation(self.G)
        copy._sf = list(self._sf)
        copy._repr = self._repr
        copy._steps = list(self._steps)
        copy._sf = list(_ for _ in sf[:pos] + list(P.rhs) + sf[pos + len(P.lhs):] if _ != 'ε')
        copy._steps = self._steps + [(prod, pos)]
        copy._repr = self._repr + ' -> ' + ''.join(self._sf)
        return copy

    def matches(self):
        for nprod, prod in enumerate(self.G.P):
            for pos in range(len(self._sf) - len(prod.lhs) + 1):
                if tuple(self._sf[pos: pos + len(prod.lhs)]) == prod.lhs:
                    yield nprod, pos
    
    def steps(self):
        return list(self._steps)
        
    def sentential_form(self):
        return ''.join(self._sf)
    
    def __repr__(self):
        return self._repr
