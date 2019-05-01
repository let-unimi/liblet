from collections import namedtuple
from dataclasses import dataclass
from functools import total_ordering
from itertools import chain
from operator import attrgetter, itemgetter
from typing import Tuple, Union

from . import ε
from .utils import letstr

HAIR_SPACE = '\u200a'

def _letlrhstostr(s):
    return HAIR_SPACE.join(map(str, s)) if isinstance(s, tuple) else str(s)

@dataclass(init = False, repr = False, eq = True, order = True, frozen = True)
class Production:
    """A grammar production.

    This class represents a grammar production, it has a *lefthand* and a
    *righthand* side that can be *nonempty* :obj:`strings <str>`, or 
    :obj:`tuples <tuple>` of *nonempty* strings; the righthand side can 
    contain ε only if is the only symbol it comprises. A production is 
    :term:`iterable` and unpacking can be used to obtain its sides, so 
    for example

    .. doctest::

        >>> lhs, rhs = Production('A', ('B', 'C'))
        >>> lhs
        'A'
        >>> rhs 
        ('B', 'C')

    Args: 
        lhs (:obj:`str` or :obj:`tuple` of :obj:`str`): The left hand side of the production. 
        rhs (:obj:`str` or :obj:`tuple` of :obj:`str`): The right hand side of the production.

    Raises:
        ValueError: in case the lefthand or righthand side are not strings, or tuples of strings.
    """

    lhs: Union[str, Tuple[str, ...]]
    rhs: Tuple[str, ...]
    #__slots__ = ('lhs', 'rhs')

    def __init__(self, lhs, rhs):
        if isinstance(lhs, str) and lhs:
            object.__setattr__(self, 'lhs', lhs)
        elif isinstance(lhs, (list, tuple)) and all(map(lambda _: isinstance(_, str) and _, lhs)): 
            object.__setattr__(self, 'lhs', tuple(lhs))
        else:
            raise ValueError('The lhs is not a nonempty str, nor a tuple (or list) of nonempty str.')
        if isinstance(rhs, (list, tuple)) and rhs and all(map(lambda _: isinstance(_, str) and _, rhs)): 
            object.__setattr__(self, 'rhs', tuple(rhs))
        else:
            raise ValueError('The rhs is not a tuple (or list) of nonempty str.')        
        if ε in self.rhs and len(self.rhs) != 1:
            raise ValueError('The righthand side contains ε but has more than one symbol')

    def __iter__(self):
        return iter((self.lhs, self.rhs))

    def __repr__(self):
        return '{} -> {}'.format(_letlrhstostr(self.lhs), _letlrhstostr(self.rhs))

    @classmethod 
    def from_string(cls, prods, context_free = True):
        """Builds a tuple of *productions* obtained from the given string.

        Args:
            prods (str): a string representing the set of productions.
            context_free (bool): if ``True`` all the *lefthand* sides will be strings (not tuples).

        The string must be a sequence of lines of the form::

            lhs -> alternatives

        where ``alternatives`` is a list of ``rhs`` strings (possibly separated by ``|``)
        and ``lhs`` and ``rhs`` are space separated strings that will be used as *lefthand* and 
        *righthand* of the returned productions; for example::

            S -> ( S ) | x T y
            x T y -> t

        Raises:
            ValueError: in case the productions are declared as ``context_free`` but on of 
                        them has more than one symbol on the righthand side.
        """
        P = []
        for p in prods.splitlines():
            if not p.strip(): continue
            lh, rha = p.split('->')
            lhs = tuple(lh.split())
            if context_free:
                if len(lhs) != 1: raise ValueError('Production "{}" has more than one symbol as lefthand side, that is forbidden in a context-free grammar.'.format(p))
                lhs = lhs[0]
            for rh in rha.split('|'):
                P.append(cls(lhs, tuple(rh.split())))
        return tuple(P)

    @classmethod
    def such_that(cls, **kwargs):
        """Returns a conjunction of predicates specified by its named arguments.

        This method returns a predicate that can be conveniently used with :func:`filter` to 

        Args:
            lhs: returns a predicate that is ``True`` weather the production *lefthand* side is equal to the argument value.            
            rhs: returns a predicate that is ``True`` weather the production *righthand* side is equal to the argument value.
            rhs_len: returns a predicate that is ``True`` weather the length of the production *lefthand* side is equal to the argument value.
            rhs_is_suffix_of: returns a predicate that is ``True`` weather the the argument value ends with the production.
        
        Returns:
            A predicate (that is a one-argument function that retuns ``True`` or ``False``) that is ``True`` weather the production
            given as argument satisfies all the predicates given by the named arguments.

        Example:
            As an example, consider the following productions and the subset of them you can obtaining 
            by filtering them according to different predicates

            .. doctest::

                >>> prods = Production.from_string("A -> B C\\nB -> b\\nC -> D")
                >>> list(filter(Production.such_that(lhs = 'B'), prods))
                [B -> b]
                >>> list(filter(Production.such_that(rhs = ['B', 'C']), prods))
                [A -> B C]
                >>> list(filter(Production.such_that(rhs_len = 1), prods))
                [B -> b, C -> D]
                >>> list(filter(Production.such_that(rhs_is_suffix_of = ('a', 'B', 'C')), prods))
                [A -> B C]
                >>> list(filter(Production.such_that(lhs = 'B', rhs_len = 1), prods))
                [B -> b]

        """
        conditions = []
        if 'lhs' in kwargs:
            conditions.append(lambda P: P.lhs == kwargs['lhs'] if isinstance(kwargs['lhs'], str) else tuple(kwargs['lhs']))
        if 'rhs' in kwargs:
            conditions.append(lambda P: P.rhs == tuple(kwargs['rhs']))
        if 'rhs_len' in kwargs:
            conditions.append(lambda P: len(P.rhs) == kwargs['rhs_len'])
        if 'rhs_is_suffix_of' in kwargs:
            conditions.append(lambda P: tuple(kwargs['rhs_is_suffix_of'][-len(P.rhs):]) == P.rhs)
        return lambda P: all(cond(P) for cond in conditions)

    def as_type0(self):
        if isinstance(self.lhs, tuple): return self
        return Production((self.lhs, ), self.rhs)


class Item(Production): # pragma: no cover
    __slots__ = ('pos',)
    def __init__(self, lhs, pos, rhs):
        if isinstance(lhs, (list, tuple)):
            raise ValueError('The lhs must be a str.')
        super().__init__(lhs, rhs)
        self.pos = pos
    def __eq__(self, other):
        if not isinstance(other, Item): return NotImplemented
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
            raise ValueError('The lhs must be a str.')
        super().__init__(lhs, pos, rhs)
        self.orig = orig
    def __eq__(self, other):
        if not isinstance(other, EarleyItem): return NotImplemented
        return (self.lhs, self.pos, self.rhs, self.orig) == (other.lhs, other.pos, other.rhs, other.orig)
    def __hash__(self):
        return hash((self.lhs, self.pos, self.rhs, self.orig))
    def __iter__(self):
        return iter((self.lhs, self.pos, self.rhs, self.orig))
    def __repr__(self):
        return '{} -> {}•{}@{}'.format(_letlrhstostr(self.lhs), _letlrhstostr(self.rhs[:self.pos]), _letlrhstostr(self.rhs[self.pos:]), self.orig)


class Grammar:
    """A grammar.

    This class represents a formal grammar, that is a tuple :math:`(N, T, P, S)` where
    :math:`N` is the finite set of *nonterminals* or *variables* symbols, :math:`T` is the 
    finite set of *terminals*, :math:`P` are the grammar *productions* or *rules* and, 
    :math:`S \in N` is the *start* symbol.

    Args:
        N (set): the grammar nonterminals.
        T (set): the grammar terminals.
        P (tuple): the grammar :obj:`productions <Production>`.
        S (str): the grammar start symbol.

    """

    __slots__ = ('N', 'T', 'P', 'S', 'is_context_free')

    def __init__(self, N, T, P, S):
        self.N = frozenset(N)
        self.T = frozenset(T)
        self.P = tuple(P)
        self.S = S
        self.is_context_free = all(map(lambda _: isinstance(_.lhs, str), self.P))
        if self.N & self.T: raise ValueError('The set of terminals and nonterminals are not disjoint, but have {} in common.'.format(set(self.N & self.T)))
        if not self.S in self.N: raise ValueError('The start symbol is not a nonterminal.')    
        if self.is_context_free:
            bad_prods = tuple(P for P in self.P if P.lhs not in self.N)
            if bad_prods: raise ValueError('The following productions have a lhs that is not a nonterminal: {}.'.format(bad_prods))
        bad_prods = tuple(P for P in self.P if not (set(P.as_type0().lhs) | set(P.rhs)).issubset(self.N | self.T | {ε}))
        if bad_prods: raise ValueError('The following productions contain symbols that are neither terminals or nonterminals: {}.'.format(bad_prods))        

    def __eq__(self, other):
        if not isinstance(other, Grammar): return NotImplemented
        return (self.N, self.T, tuple(sorted(self.P)), self.S) == (other.N, other.T, tuple(sorted(other.P)), other.S)

    def __hash__(self):
        return hash((self.N, self.T, tuple(sorted(self.P)), self.S))

    def __repr__(self):
        return 'Grammar(N={}, T={}, P={}, S={})'.format(letstr(self.N), letstr(self.T), self.P, letstr(self.S))

    @classmethod
    def from_string(cls, prods, context_free = True):
        """Builds a grammar obtained from the given productions.

        Args:
            prods (str): a string describing the productions.
            context_free (bool): if ``True`` the grammar is expected to be context-free.

        Once the *productions* are determined via a call to :func:`Production.from_string`, 
        the remaining defining elements of the grammar are obtained as follows:
        
        * if the grammar is *not* context-free the *nonterminals* is the set of symbols,
          appearing in (the lefthand, or righthand side of) any production, beginning with 
          an uppercase letter, the *terminals* are the remaining symbols. The *start* symbol
          is the lefthand of the first production;

        * if the grammar is *context-free* the *nonterminals* is the set of symbols appearing
          in a lefthand side of any production, the *terminals* are the remaining symbols. The
          *start* symbol is the lefthand of the first production.           
        """
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
        G = cls(N, T, P, S)
        if context_free: # pragma: no cover
            if not G.is_context_free: raise ValueError('The resulting grammar is not context-free, even if so requested.')
        return G

    def alternatives(self, N):
        """Yields al the righthand sides alternatives matching the given nonterminal.

        Args:
            N (:obj:`str` or :obj:`tuple` of :obj:`str`): the righthand to match.
        Yields:
            the righthand sides of all productions having ``N`` as the lefthand side.
        """
        return (P.rhs for P in self.P if P.lhs == N)

    def restrict_to(self, symbols):
        """Returns a grammar using only the given symbols.

        Args:
            symbols: the only allowed symbols.
        Returns:
             :obj:`Grammar`: a new grammar containing only the given symbols (and hence 
             no production of the original grammar that uses a symbol not in the given 
             set.) 
        """
        return Grammar(self.N & symbols, self.T & symbols, (P for P in self.P if (({P.lhs} | set(P.rhs)) & self.N) <= symbols), self.S)



class Derivation:
    """A derivation.

    This class is *immutable*, derivations can be built invoking
    :func:`~Derivation.step`, :func:`~Derivation.leftmost`, and 
    :func:`~Derivation.rightmost`

    Args:
        G (:class:`~liblet.grammar.Grammar`): the grammar to which the derivations refers to.

    """

    def __init__(self, G):
        self.G = G
        self._steps = tuple()
        # the following attrs are computed
        self._sf = (G.S, )
        self._repr = G.S

    def __eq__(self, other):
        if not isinstance(other, Derivation): return False
        return (self.G, self._steps) == (other.G, other._steps)

    def __hash__(self):
        return hash((self.G, self._steps))
    
    def __repr__(self):
        return self._repr

    def leftmost(self, prod):
        """Performs a *leftmost* derivation step.

        Applies the specified production to the current leftmost nonterminal in the sentential form.

        Args:
            prod (int): the production to apply, that is ``G.P[prod]``.

        Returns:
            :obj:`Derivation`: A derivation obtained applying the specified production to the present production.

        Raises:
            ValueError: in case the leftmost nonterminal isn't the lefthand side of the given production.
        """
        if not self.G.is_context_free: raise ValueError('Cannot perform a leftmost derivation on a non context-free grammar')
        for pos, symbol in enumerate(self._sf):
            if symbol in self.G.N:
                if self.G.P[prod].lhs == symbol:
                    return self.step(prod, pos)
                else:
                    raise ValueError('Cannot apply {}: the leftmost nonterminal of {} is {}.'.format(self.G.P[prod], HAIR_SPACE.join(self._sf), symbol))
        else:
            raise ValueError('Cannot apply {}: there are no nonterminals in {}.'.format(self.G.P[prod], HAIR_SPACE.join(self._sf,)))

    def rightmost(self, prod):
        """Performs a *rightmost* derivation step.

        Applies the specified production to the current rightmost nonterminal in the sentential form.

        Args:
            prod (int): the production to apply, that is ``G.P[prod]``.

        Returns:
            :obj:`Derivation`: A derivation obtained applying the specified production to the present production.

        Raises:
            ValueError: in case the rightmost nonterminal isn't the lefthand side of the given production.
        """
        if not self.G.is_context_free: raise ValueError('Cannot perform a rightmost derivation on a non context-free grammar')
        for pos, symbol in list(enumerate(self._sf))[::-1]:
            if symbol in self.G.N:
                if self.G.P[prod].lhs == symbol:
                    return self.step(prod, pos)
                else:
                    raise ValueError('Cannot apply {}: the rightmost nonterminal of {} is {}.'.format(self.G.P[prod], HAIR_SPACE.join(self._sf), symbol))
        else:
            raise ValueError('Cannot apply {}: there are no nonterminals in {}.'.format(self.G.P[prod], HAIR_SPACE.join(self._sf,)))

    def step(self, prod, pos): 
        """Performs a derivation step, returning a new derivation.

        Applies the specified production to the given position in the sentential form.

        Args:
            prod (int): the production to apply, that is ``G.P[prod]``.
            pos (int): the position (in the current *sentential form*) where to apply the production.

        Returns:
            :obj:`Derivation`: A derivation obtained applying the specified production to the present production.

        Raises:
            ValueError: in case the production can't be applied at the specified position.
        """

        sf = self._sf
        P = self.G.P[prod].as_type0()
        if sf[pos: pos + len(P.lhs)] != P.lhs: raise ValueError('Cannot apply {} at position {} of {}.'.format(P, pos, HAIR_SPACE.join(sf)))
        copy = Derivation(self.G)
        copy._sf = tuple(_ for _ in sf[:pos] + P.rhs + sf[pos + len(P.lhs):] if _ != 'ε')
        copy._steps = self._steps + ((prod, pos), )
        copy._repr = self._repr + ' -> ' + HAIR_SPACE.join(copy._sf)
        return copy

    def possible_steps(self, prod = None, pos = None):
        """Yields all the possible steps that can be performed given the grammar and current *sentential form*.

        Determines all the position of the *sentential form* that correspond to the lefthand side of 
        one of the production in the grammar, returning the position and production number. If a 
        production is specified, it yields only the pairs referring to it; similarly, if a position
        is specified, it yields only the pairs referring to it.

        Args:
            prod (int): the production whose lefthand is to be searched (that is `G.P[prod].lhs``) in the *sentential form*.
            pos (int): the position where to look for grammar productions that have a matching lefthand side.

        Yields:
            Pairs of ``(pord, pos)`` that can be used as :func:`step` argument.
        """
        type0_prods = tuple(map(lambda _: _.as_type0(), self.G.P))
        for n, P in enumerate(type0_prods) if prod is None else ((prod, type0_prods[prod]), ):
            for p in range(len(self._sf) - len(P.lhs) + 1) if pos is None else (pos, ):
                if self._sf[p: p + len(P.lhs)] == P.lhs:
                    yield n, p
    
    def steps(self):
        """Returns the steps of the derivation.

        Returns: a :obj:`tuple` of ``(prod, pos)`` pairs corresponding to this derivation steps.
        """
        return tuple(self._steps)
        
    def sentential_form(self):
        """Returns the *sentential form* of the derivation.

        Returns: a :obj:`tuple` of (strings representing) grammar symbols corresponding to the *sentential form* of this derivation steps.
        """
        return tuple(self._sf)
