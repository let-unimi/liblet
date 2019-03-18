from abc import ABC, abstractmethod
from itertools import chain

from IPython.display import HTML
from graphviz import Digraph as gvDigraph

from .utils import letstr

# graphviz stuff

class BaseGraph(ABC):

    @abstractmethod
    def _gvgraph_(self):
        pass

    # letstr(node) is always used as node_label 
    # node_id is str(x) where x is id (if not None) or hash(node_label)
    def node(self, G, node, id = None, sep = None, gv_args = None):
        if gv_args is None: gv_args = {}
        if not hasattr(self, '_nodes'): self._nodes = set()
        node_label = letstr(node, sep)
        node_id = str(hash(node_label) if id is None else id)
        if node_id in self._nodes: return node_id
        G.node(node_id, node_label, **gv_args)
        self._nodes.add(node_id)
        return node_id

    # src and dst as str()-ed and used as ids
    def edge(self, G, src, dst, label = None, large_label = False, gv_args = None):
        if gv_args is None: gv_args = {}
        label_param = {} if label is None else {'xlabel' if large_label else 'label': label}
        label_param.update(gv_args)
        G.edge(str(src), str(dst), **label_param)

    def _repr_svg_(self):
        return self._gvgraph_()._repr_svg_()

    def _repr_png_(self):
        return self._gvgraph_().pipe(format='png')


class Tree(BaseGraph):
    
    def __init__(self, root, children = None):
        self.root = root
        self.children = children if children else []

    @classmethod
    def from_lol(cls, nl):
        def _to_tree(lst):
            return cls(str(lst[0]), [_to_tree(sl) for sl in lst[1:]])
        return _to_tree(nl)

    def __repr__(self):
        def walk(T):
            return '({}: {})'.format(T.root, ', '.join(map(walk, T.children))) if T.children else T.root
        return walk(self)

    def _gvgraph_(self):
        def walk(T, parent):
            if parent: 
                self.node(G, T.root, id(T))
                self.edge(G, id(parent), id(T))
            with G.subgraph(edge_attr = {'style': 'invis'}, graph_attr = {'rank': 'same'}) as S:
                for f, t in zip(T.children, T.children[1:]): self.edge(S, id(f), id(t))
            for child in T.children: walk(child, T)
        G = gvDigraph(
            graph_attr = {
                'nodesep': '.25',
                'ranksep': '.25'    
            },
            node_attr = {
                'shape': 'box',
                'margin': '.05',
                'width': '0',
                'height': '0',
                'style': 'rounded, setlinewidth(.25)'
             },
             edge_attr = {
                'dir': 'none'
             }
        )
        G.node(str(id(self)), self.root)
        walk(self, None)
        return G


class Graph(BaseGraph):

    def __init__(self, arcs, sep = None):
        self.G = gvDigraph(graph_attr = {'size': '8', 'rankdir': 'LR'})
        for src, dst in arcs: self.G.edge(letstr(src, sep = sep), letstr(dst, sep = sep))

    @classmethod
    def from_adjdict(cls, adjdict):
        return cls((src, dst) for src, dsts in adjdict.items() for dst in dsts)

    def _gvgraph_(self):
        return self.G


class ProductionGraph(BaseGraph):

    def __init__(self, derivation):
        self.derivation = derivation
        self.G = None

    def __repr__(self):
        return 'ProductionGraph({})'.format(self.derivation)

    def _gvgraph_(self):
        if self.G is not None: return self.G
        derivation = self.derivation
        G = gvDigraph(
            graph_attr = {
                'nodesep': '.25',
                'ranksep': '.25'
            },
            node_attr = {
                'size': '8',
                'shape': 'box',
                'margin': '.05',
                'width': '0',
                'height': '0',
                'style': 'rounded, setlinewidth(.25)'
            },
            edge_attr = {
                'dir': 'none',
                'penwidth': '.5',
                'arrowsize': '.5'
            }
        )

        def remove_ε(sentence):
            return tuple(_ for _ in sentence if _[0] != 'ε')

        sentence = ((derivation.G.S, 0, 0), )
        for step, (rule, pos) in enumerate(derivation.steps(), 1):
            lhs, rhs = derivation.G.P[rule].as_type0()
            rhsn = tuple((X, step, p) for p, X in enumerate(rhs))
            sentence = remove_ε(sentence[:pos] + rhsn + sentence[pos + len(lhs):])
        last_sentence = set(sentence)

        sentence = ((derivation.G.S, 0, 0), )
        with G.subgraph(graph_attr = {'rank': 'same'}) as S:
            prev_level = self.node(S, ('LevelNode', 0), gv_args = {'style': 'invis'})
            self.node(S, sentence[0][0], hash(sentence[0]))

        for step, (rule, pos) in enumerate(derivation.steps(), 1):
            
            lhs, rhs = derivation.G.P[rule].as_type0()
            rhsn = tuple((X, step, p) for p, X in enumerate(rhs))
            
            with G.subgraph(graph_attr = {'rank': 'same'}) as S:
                new_level = self.node(S, ('LevelNode', step), gv_args = {'style': 'invis'})
                for node in rhsn: self.node(S, node[0], hash(node), gv_args = {'style': 'rounded, setlinewidth(1.25)' if node in last_sentence else 'rounded, setlinewidth(.25)'})
            self.edge(G, prev_level, new_level, gv_args = {'style': 'invis'})
            prev_level = new_level 
            
            if len(lhs) == 1:                
                frm = sentence[pos]
                for to in rhsn: self.edge(G, hash(frm), hash(to))
            else:
                id_dot = self.node(G, (step, rule), gv_args = {'shape': 'point', 'width': '.07', 'height': '.07'})
                for frm in sentence[pos:pos + len(lhs)]: self.edge(G, hash(frm), id_dot)
                for to in rhsn: self.edge(G, id_dot, hash(to))
            
            if len(rhs) > 1:
                with G.subgraph(edge_attr = {'style': 'invis'}, graph_attr = {'rank': 'same'}) as S:
                    for f, t in zip(rhsn, rhsn[1:]): self.edge(S, hash(f), hash(t))

            sentence = remove_ε(sentence[:pos] + rhsn + sentence[pos + len(lhs):])
        
        self.G = G
        return G


class StateTransitionGraph(BaseGraph):

    def __init__(self, transitions, S = None, F = None, large_labels = False):
        self.transitions = transitions
        self.S = S
        self.F = set() if F is None else F
        self.large_labels = large_labels
        self.G = None

    @classmethod
    def from_automaton(cls, A):
        return cls(A.transitions, A.q0, A.F)

    @classmethod
    def from_lr(cls, STATES, GOTO):
        transitions = [(STATES[s], X, STATES[t]) for s in GOTO for X, t in GOTO[s].items() if t]
        return cls(transitions, STATES[0], [s for s in STATES if any(item.pos == len(item.rhs) for item in s)], True)

    def _gvgraph_(self):
        if self.G: return self.G
        sep = '\n' if self.large_labels else None
        G = gvDigraph(
                graph_attr = {
                    'rankdir': 'LR',
                    'size': '8'
                },
                node_attr = {'margin': '.05'} if self.large_labels else {},
                engine = 'dot'
            )
        if self.S is not None:
            self.edge(G, 
                self.node(G, '#START#', '#START#', sep = sep, gv_args = {'shape': 'none'}), 
                self.node(G, self.S, sep = sep, gv_args = {'peripheries': '2' if self.S in self.F else '1'})
            )
        for X, x, Y in self.transitions:
            self.edge(G, 
                self.node(G, X, sep = sep, gv_args = {'peripheries': '2' if X in self.F else '1'}), 
                self.node(G, Y, sep = sep, gv_args = {'peripheries': '2' if Y in self.F else '1'}), 
                x, self.large_labels
            )
        self.G = G
        return G


# HTML stuff

def side_by_side(*iterable):
    return HTML('<div>{}</div>'.format(' '.join(item._repr_svg_() for item in iterable)))

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