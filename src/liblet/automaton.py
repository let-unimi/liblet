from collections import namedtuple
from collections.abc import Set
from functools import total_ordering
from operator import attrgetter

from . import DIAMOND, ε
from .utils import letstr



@total_ordering
class Transition:
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
            label (str): The label of the transition.
            to (:obj:`str` or :obj:`set` of :obj:`str`): The destination state(s) of the transition.

        Raises:
            ValueError: in case the frm or to states are not nonempty strings, or nonempty set 
                        of nonempty strings, or the label is not a nonempty string.
    """

    __slots__ = ('frm', 'label', 'to')

    def __init__(self, frm, label, to):

        def _cssos(s):
            if isinstance(s, str) and s: return True
            if isinstance(s, Set) and s and all(map(lambda _: isinstance(_, str) and _, s)): return True
            return False

        if _cssos(frm):
            self.frm = frm
        else:
            raise ValueError('The frm state is not a nonempty string, or a nonempty set of nonempty strings')
        if isinstance(label, str) and label:
            self.label = label
        else:
            raise ValueError('The label is not a nonempty string')
        if _cssos(to):
            self.to = to
        else:
            raise ValueError('The to state is not a nonempty string, or a nonempty set of nonempty strings')
        self.to = to

    def __lt__(self, other):
        if not isinstance(other, Transition): return NotImplemented
        return (self.frm, self.label, self.to) < (other.frm, other.label, other.to)
        
    def __eq__(self, other):
        if not isinstance(other, Transition): return False
        return (self.frm, self.label, self.to) == (other.frm, other.label, other.to)

    def __hash__(self):
        return hash((self.frm, self.label, self.to))

    def __iter__(self):
        return iter((self.frm, self.label, self.to))

    def __repr__(self):
        return '{}-{}->{}'.format(letstr(self.frm), self.label, letstr(self.to))

    @classmethod
    def from_string(cls, transitions):
        res = []
        for t in transitions.splitlines():
            if not t.strip(): continue
            frm, label, to = t.split(',')
            res.append(Transition(frm.strip(), label.strip(), to.strip()))
        return res


class Automaton(object):
    """An automaton.

        This class represents a (*nondeterministic*) *finite automaton*.

        Args: 
            N (set): The states of the automaton. 
            T (set): The transition labels.
            transitions (:obj:`set` of :obj:`Transition`): The transition of the automata.
            q0: The starting state of the automaton.
            F (set): The set of *final* states.
    """

    __slots__ = ('N', 'T', 'transitions', 'q0', 'F')
    
    def __init__(self, N, T, transitions, q0, F):
        self.N = set(N)
        self.T = set(T)
        self.transitions = tuple(transitions)
        self.q0 = q0
        self.F = set(F)
        if self.N & self.T: raise ValueError('The set of states and input symbols are not disjoint, but have {} in common.'.format(letstr(set(self.N & self.T))))
        if not self.q0 in self.N: raise ValueError('The specified q0 ({}) is not a state.'.format(letstr(q0)))    
        if not self.F <= self.N: raise ValueError('The accepting states {} in F are not states.'.format(letstr(self.F - self.N)))        
        bad_trans = tuple(t for t in transitions if not t.frm in self.N or not t.to in self.N or not t.label in (self.T | {ε}))
        if bad_trans: raise ValueError('The following transitions contain states or symbols that are neither states nor input symbols: {}.'.format(bad_trans))

    def δ(self, X, x):
        """The transition function.

        This function returns the set of states reachable from the given state and input symbol.

        Args:
            X: the state.
            x: the input symbol.
        Returns:
            The set of next states of the automaton.
        """
        return {Z for Y, y, Z in self.transitions if Y == X and y == x}

    def __repr__(self):
        return 'Automaton(N={}, T={}, transitions={}, F={}, q0={})'.format(letstr(self.N), letstr(self.T), self.transitions, letstr(self.F), letstr(self.q0))
   
    @classmethod
    def from_string(cls, transitions, F = None, q0 = None):
        transitions = Transition.from_string(transitions)
        if F is None: F = set()
        if q0 is None: q0 = transitions[0].frm
        N = set(map(attrgetter('frm'), transitions)) | set(map(attrgetter('to'), transitions))
        T = set(map(attrgetter('label'), transitions)) - {ε}
        return cls(N, T, transitions, q0, F)

    @classmethod
    def from_grammar(cls, G):
        res = []
        for P in G.P:
            if len(P.rhs) > 2: raise ValueError('Production {} has more than two symbols on the lefthand side'.format(P))
            if len(P.rhs) == 2:
                A, (a, B) = P
                if not (a in G.T and B in G.N): raise ValueError('Production {} right hand side is not of the aB form'.format(P))
                res.append(Transition(A, a, B))
            elif P.rhs[0] in G.N:
                res.append(Transition(*((P.lhs, ) + (ε, ) + P.rhs)))
            else:
                res.append(Transition(*((P.lhs, ) + P.rhs + (DIAMOND,))))
        return cls(G.N | {DIAMOND}, G.T, tuple(res), G.S, {DIAMOND})
