from os import environ
from urllib import request, parse
from urllib.error import URLError
from uuid import getnode

__version__ = '0.11.1-alpha'

ε = 'ε'
DIAMOND = '◇'

from .decorators import closure, show_calls
from .display import Tree, Graph, StateTransitionGraph, ProductionGraph, side_by_side, dod2table, iter2table, cyk2table, prods2table, dict2table, ff2table, warn
from .grammar import Production, Item, Grammar, Derivation
from .automaton import Transition, Automaton
from .utils import peek, union_of, letstr, Stack, Queue
from .antlr import ANTLR

if 'LIBLET_NOBEACON' not in environ and 'READTHEDOCS' not in environ:
    try:
        if 'playground' in environ.get('PYTHONPATH', ''):
            ea = 'playground'
        elif 'handouts' in environ.get('PYTHONPATH', ''):
            ea = 'handouts'
        else:
            ea = 'direct'
        request.urlopen('https://www.google-analytics.com/collect', data = parse.urlencode({
            'v': 1,
            'tid': 'UA-377250-25',
            'aip': 1,
            'ds': 'lib',
            'cid': getnode(),
            't': 'event',
            'ec': 'liblet',
            'ea': ea,
            'el': __version__,
            'ev': 1
        }).encode()).read()
    except URLError:
        pass