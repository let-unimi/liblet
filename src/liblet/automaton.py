from collections import namedtuple
from operator import attrgetter

from . import DIAMOND, ε
from .utils import letstr

Transition = namedtuple('Transition', 'frm label to')
"""An automaton transition.

    This class represents an automaton transition; it has a `frm` starting
    *state* and a `to` destination *state* and a `label`, the states can be
    *nonempty* :obj:`strings <str>` or *nonempty* :obj:`sets <set>` of
    *nonempty* strings, whereas the label is usually a string.  A transition is
    :term:`iterable` and unpacking can be used to obtain its components, so for
    example

    .. doctest::

        >>> frm, label, to = Transition({'A', 'B'}, 'c', {'D'})
        >>> frm
        {'B', 'A'}
        >>> label
        'c'
        >>> to
        {'D'}

    Args: 
        frm (:obj:`str` or :obj:`set` of :obj:`str`): The starting state(s) of the transition. 
        label (:obj:`str`): The label of the transition.
        to (:obj:`str` or :obj:`set` of :obj:`str`): The destination state(s) of the transition.

"""

Transition.__repr__ = lambda self: '{}-{}->{}'.format(letstr(self.frm), self.label, letstr(self.to))

class Automaton(object):
    """An automaton.

        This class represents a (*nondeterministic*) *finite automaton*.

        Args: 
            N (:obj:`set`): The states of the automaton. 
            T (:obj:`set`): The transition labels.
            transitions (:obj:`set` of :obj:`Transition`): The transition of the automata.
            F (:obj:`set`): The set of *final* states.
            q0: The starting state of the automaton.
    """
    
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
