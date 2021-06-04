from os import environ
from urllib import request, parse
from urllib.error import URLError
from uuid import getnode

__version__ = '1.4.1-alpha'

ε = 'ε'
DIAMOND = '◇'
HASH = '♯'

from .decorators import closure, show_calls
from .display import Tree, Graph, StateTransitionGraph, ProductionGraph, side_by_side, dod2table, iter2table, cyk2table, prods2table, dict2table, ff2table, animate_derivation, pyast2tree
from .grammar import Production, Item, Grammar, Derivation
from .automaton import Transition, Automaton, TopDownInstantaneousDescription, BottomUpInstantaneousDescription
from .utils import first, peek, union_of, letstr, Stack, Queue, Table, warn, uc, suffixes
from .antlr import ANTLR, AnnotatedTreeWalker
from .llvm import LLVM