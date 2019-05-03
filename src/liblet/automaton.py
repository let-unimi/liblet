from collections import namedtuple
from collections.abc import Set
from functools import total_ordering
from operator import attrgetter

from . import DIAMOND, ε
from .utils import letstr
from .grammar import Item

@total_ordering
class Transition:
    """An automaton transition.

        This class represents an automaton transition; it has a `frm` starting
        *state* and a `to` destination *state* and a `label`, the states can be:

        - *nonempty* :obj:`strings <str>`, or
        - *nonempty* :obj:`sets <set>` of *nonempty* strings, or 
        - *nonempty* :obj:`tuples <tuple>` of :obj:`items <liblet.grammar.Item>`, 
        
        whereas the label is a :obj:`str`.  A transition is
        :term:`iterable` and unpacking can be used to obtain its components, so for
        example

        .. doctest::

            >>> frm, label, to = Transition({'A', 'B'}, 'c', {'D'})
            >>> sorted(frm)
            ['A', 'B']
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
            if isinstance(s, tuple) and s and all(map(lambda _: isinstance(_, Item), s)): return True
            return False

        if _cssos(frm):
            self.frm = frm
        else:
            raise ValueError('The frm state is not a nonempty string, or a nonempty set of nonempty strings/items')
        if isinstance(label, str) and label:
            self.label = label
        else:
            raise ValueError('The label is not a nonempty string')
        if _cssos(to):
            self.to = to
        else:
            raise ValueError('The to state is not a nonempty string, or a nonempty set of nonempty strings/items')
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
        """Builds a tuple of *transitions* obtained from the given string.

        Args:
            trasitions (str): a string representing transitions.

        The string must be a sequence of lines of the form::

            frm, label, to
    
        where the parts are strings not containing spaces.s
        """
        res = []
        for t in transitions.splitlines():
            if not t.strip(): continue
            frm, label, to = t.split(',')
            res.append(Transition(frm.strip(), label.strip(), to.strip()))
        return tuple(res)


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
        """Builds an automaton obtained from the given transitions.

        Args:
            transitions (str): a string describing the productions.
            F (set): The set of *final* states.
            q0 (str): The starting state of the automaton (inferred from transitions if ``None``).

        Once the *transitions* are determined via a call to :func:`Transition.from_string`, 
        the starting state (if not specified) is defined as the ``frm`` state of the first transition.
        """
        transitions = Transition.from_string(transitions)
        if F is None: F = set()
        if q0 is None: q0 = transitions[0].frm
        N = set(map(attrgetter('frm'), transitions)) | set(map(attrgetter('to'), transitions))
        T = set(map(attrgetter('label'), transitions)) - {ε}
        return cls(N, T, transitions, q0, F)

    @classmethod
    def from_grammar(cls, G):
        r"""Builds the automaton corresponding to the given *regular grammar*.

        Args:
            G (:obj:`~liblet.Grammar`): the *regular grammar* to derive the automata from.

        The method works under the assumption that the only rules of the 
        grammar are of the form :math:`A\to aB`, :math:`A\to B`, :math:`A\to a`,
        and :math:`A\to ε`.
        """
        res = []
        for P in G.P:
            if len(P.rhs) > 2: raise ValueError('Production {} has more than two symbols on the left-hand side'.format(P))
            if len(P.rhs) == 2:
                A, (a, B) = P
                if not (a in G.T and B in G.N): raise ValueError('Production {} right-hand side is not of the aB form'.format(P))
                res.append(Transition(A, a, B))
            elif P.rhs[0] in G.N:
                res.append(Transition(*((P.lhs, ) + (ε, ) + P.rhs)))
            else:
                res.append(Transition(*((P.lhs, ) + P.rhs + (DIAMOND,))))
        return cls(G.N | {DIAMOND}, G.T, tuple(res), G.S, {DIAMOND})
