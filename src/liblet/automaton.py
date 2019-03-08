from collections import namedtuple
from operator import attrgetter

from . import DIAMOND, ε
from .utils import letstr


Transition = namedtuple('Transition', 'frm label to')
Transition.__repr__ = lambda self: '{}-{}->{}'.format(letstr(self.frm), self.label, letstr(self.to))

class Automaton(object):
    
    def __init__(self, N, T, transitions, F, q0):
        self.N = set(N)
        self.T = set(T)
        self.transitions = tuple(transitions)
        self.F = set(F)
        self.q0 = q0

    def δ(self, X, x):
        return {Z for Y, y, Z in self.transitions if Y == X and y == x}

    def __repr__(self):
        return 'Automaton(N={}, T={}, transitions={}, F={}, q0={})'.format(letstr(self.N), letstr(self.T), self.transitions, letstr(self.F), letstr(self.q0))
   
    def coalesce(self):
        return Automaton(
            {''.join(sorted(_)) for _ in self.N}, 
            self.T, 
            tuple(Transition(''.join(sorted(frm)), label, ''.join(sorted(to))) for frm, label, to in self.transitions), 
            {''.join(sorted(_)) for _ in self.F}, 
            ''.join(sorted(self.q0))
        )

    @classmethod
    def from_transitions(cls, transitions, F = None, q0 = None):
        transitions = tuple(map(lambda _: Transition(*_), transitions))
        if q0 is None: q0 = transitions[0].frm
        if F is None:  F = set()
        N = set(map(attrgetter('frm'), transitions)) | set(map(attrgetter('to'), transitions))
        T = set(map(attrgetter('label'), transitions)) - {ε}
        return cls(N, T, transitions, F, q0)

    @classmethod
    def from_grammar(cls, G):
        res = []
        for P in G.P:
            if len(P.rhs) == 2:
                res.append(Transition(*((P.lhs, ) + P.rhs)))
            elif P.rhs[0] in G.N:
                res.append(Transition(*((P.lhs, ) + (ε, ) + P.rhs)))
            else:
                res.append(Transition(*((P.lhs, ) + P.rhs + (DIAMOND,))))
        return cls(G.N | {DIAMOND}, G.T, tuple(res), {DIAMOND}, G.S)

    @classmethod
    def from_string(cls, trans, F = None):
        transitions = []
        for t in trans.splitlines():
            if not t.strip(): continue
            frm, label, to = t.split(',')
            transitions.append(Transition(frm.strip(), label.strip(), to.strip()))
        return Automaton.from_transitions(transitions, set() if F is None else F)
