import ast

from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from collections.abc import Set, MutableMapping
from html import escape
from itertools import chain, groupby
from re import sub
from warnings import warn as wwarn

from IPython.display import HTML, display
from attr import frozen
from graphviz import Digraph as gvDigraph
from ipywidgets import interactive, IntSlider

from . import ε
from .utils import letstr, AttrDict
from .grammar import Productions, HAIR_SPACE, Derivation

# graphviz stuff

def _escape(label):
  return sub('\]', '&#93;', sub('\[', '&#91;', escape(str(label))))

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
    return self._gvgraph_()._repr_image_svg_xml()

class Tree(BaseGraph):
  """A *n-ary tree* with ordered children.

  The tree stores its :attr:`root` and :attr:`children` in two fields of the same name.

  If the tree root is a :obj:`dict` the tree is an *annotated* tree. Such kind
  of trees arise from parsing, for example using the
  :meth:`~liblet.antlr.ANTLR.tree` method of the :class:`~liblet.antlr.ANTLR`
  class; these trees are automatically endowed with an :attr:`attr` attribute
  defined as an :class:`~liblet.utils.AttrDict` wrapping the :attr:`root`, so
  that, for an annotated tree ``t``, it is completely equivalent to write
  ``t.root['key']`` or ``t.attr.key`` (both for reading, and writing).

  A tree is represented as a string as a ``(<root>: <children>)`` where ``<root>``
  is the string representation of the root node content and ``<children>`` is the
  recursively obtained string representation of its children.

  It also has a representation as a graph; in such case, if the tree is annotated it
  will be rendered by Graphviz using `HTML-Like Labels <https://www.graphviz.org/doc/info/shapes.html#html>`__
  built as a table where each dictionary item corresponds to a row with two columns containing the
  key and value pair of such item.

  Args:
    root: the root node content (can be of any type).
    children: an :term:`iterable` of trees to become the current tree children.
  """

  def __init__(self, root, children = None):
    self.root = root
    self.children = list(children) if children else []
    if isinstance(root, MutableMapping): self.attr = AttrDict(root)

  def __iter__(self):
    return iter([self.root] + self.children)

  @classmethod
  def from_lol(cls, lol):
    """Builds a tree from a *list of lists*.

    A list of lists (lol) is a list recursively defined such that the first element of a lol
    is the tree node content and the following elements are lols.

    Args:
      lol (list): a list representing a tree.

    Examples:
      The following code

    .. code:: ipython3

      Tree.from_lol([{'this': 'is', 'an': 2},[3, ['example']], [5]])

    produces the following tree

    .. image:: tree.svg

    """
    def _to_tree(lst):
      root, *children = lst
      return cls(root, [_to_tree(child) for child in children])
    return _to_tree(lol)

  def __repr__(self):
    def walk(T):
      return '({}: {})'.format(T.root, ', '.join(map(walk, T.children))) if T.children else '({})'.format(T.root)
    return walk(self)

  def _gvgraph_(self):
    def _gv_args(node):
      is_dict = isinstance(node, dict)
      return {
        'shape': 'none' if is_dict else 'box',
        'margin': '0' if is_dict else '.05'
      }
    def _tostr(node):
      if isinstance(node, dict):
        return ''.join(
          ['<<FONT POINT-SIZE="12"><TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">'] +
          ['<TR><TD>{}</TD><TD>{}</TD></TR>'.format(k, _escape(v)) for k, v in node.items() if not k.startswith('_thread_')] +
          ['</TABLE></FONT>>'])
      return str(node)
    def walk(T):
      curr = self.node(G, _tostr(T.root), id(T), gv_args = _gv_args(T.root))
      if T.children:
        for child in T.children:
          self.node(G, _tostr(child.root), id(child), gv_args = _gv_args(child.root))
          self.edge(G, curr, id(child ))
        with G.subgraph(edge_attr = {'style': 'invis'}, graph_attr = {'rank': 'same'}) as S:
          for f, t in zip(T.children, T.children[1:]):
            self.edge(S, id(f), id(t))
        for child in T.children: walk(child)
    G = gvDigraph(
      graph_attr = {
        'nodesep': '.25',
        'ranksep': '.25'
      },
      node_attr = {
        'width': '0',
        'height': '0',
        'style': 'rounded, setlinewidth(.25)'
       },
       edge_attr = {
        'dir': 'none'
       }
    )
    self._nodes = set()
    walk(self)
    return G

  def with_threads(self, threads):
    """Draws a *threaded* and *annotated* tree (as a graph).

    Tree *threads* are arcs among tree nodes (or special nodes), more
    precisely, a :obj:`dict` mapping annotated tree *source* nodes to a
    :obj:`dict` whose values are *destinations* tree nodes; arcs are
    represented as dotted arrows. Special nodes are: the *start* tree (an
    annotated tree whose root contains the ``(type, <START>)`` item), the
    *join* trees (annotated trees whose root contains the ``(type, <JOIN>)``
    item) and the ``None`` value; such special nodes are represented as red
    dots.


    Args: threads (dict): a dictionary representing the threads.
    """

    G = self._gvgraph_()
    del G.edge_attr['dir']
    G.edge_attr['arrowsize'] = '.5'

    depths = defaultdict(list)
    def _depth(tree, d):
      depths[d].append(tree)
      for child in tree.children: _depth(child, d + 1)
    _depth(self, 0)
    for d in sorted(depths.keys()):
      with G.subgraph(graph_attr = {'rank': 'same'}) as S:
        for n in depths[d]: S.node(str(id(n)))

    node_args = {'shape': 'point', 'width': '.07', 'height': '.07', 'color': 'red'}
    edge_args = {'dir': 'forward', 'arrowhead': 'vee', 'arrowsize': '.5', 'style': 'dashed', 'color': 'red'}

    for node in threads:
      if 'type' in node.root and node.root['type'] in ('<START>', '<JOIN>'):
        self.node(G, node.root['type'], id(node), gv_args = node_args)
    self.node(G, None, id(None), gv_args = node_args)

    for node, info in threads.items():
      for nxt in info.keys():
        self.edge(G, id(node), id(info[nxt]), gv_args = edge_args)

    return G

class Graph(BaseGraph):

  def __init__(self, arcs, sep = None):
    self.G = gvDigraph(graph_attr = {'size': '8', 'rankdir': 'LR'})
    self.adj = dict()
    for src, dst in arcs:
     self.adj[src] = self.adj.get(src, set()) | {dst}
     self.adj[dst] = self.adj.get(dst, set())
     self.G.edge(letstr(src, sep = sep), letstr(dst, sep = sep))

  def neighbors(self, src):
    """Returns (a set containing) the neighbors of the given node.

    Args:
      src: the node.
    """
    return frozenset(self.adj[src])

  @classmethod
  def from_adjdict(cls, adjdict):
    """Builds a graph given its adjacency structure.

    Args:
      adjdict (dict): a dictionary where keys are source nodes and values are an iterable of destination nodes.
    """
    return cls((src, dst) for src, dsts in adjdict.items() for dst in dsts)

  def _gvgraph_(self):
    return self.G


class ProductionGraph(BaseGraph):

  def __init__(self, derivation, compact = None):
    self.derivation = derivation
    if compact is None:
      self.compact = True if derivation.G.is_context_free else False
    else:
      self.compact = compact
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
      return tuple(_ for _ in sentence if _[0] != ε)

    sentence = ((derivation.start, 0, 0), )
    for step, (rule, pos) in enumerate(derivation.steps(), 1):
      lhs, rhs = derivation.G.P[rule].as_type0()
      rhsn = tuple((X, step, p) for p, X in enumerate(rhs))
      sentence = remove_ε(sentence[:pos] + rhsn + sentence[pos + len(lhs):])
    last_sentence = set(sentence)

    use_levels = not self.compact

    sentence = ((derivation.start, 0, 0), )
    with G.subgraph(graph_attr = {'rank': 'same'}) as S:
      if use_levels: prev_level = self.node(S, ('LevelNode', 0), gv_args = {'style': 'invis'})
      self.node(S, sentence[0][0], hash(sentence[0]))

    for step, (rule, pos) in enumerate(derivation.steps(), 1):

      lhs, rhs = derivation.G.P[rule].as_type0()
      rhsn = tuple((X, step, p) for p, X in enumerate(rhs))

      with G.subgraph(graph_attr = {'rank': 'same'}) as S:
        if use_levels: new_level = self.node(S, ('LevelNode', step), gv_args = {'style': 'invis'})
        for node in rhsn: self.node(S, node[0], hash(node), gv_args = {'style': 'rounded, setlinewidth(1.25)' if node in last_sentence else 'rounded, setlinewidth(.25)'})
      if use_levels:
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
  """A directed graph with labelled nodes and arcs.

  Args:
   transitions: an :term:`iterable` of triples :math:`(f, l, t)` of three strings representing the :math:`(f, t)` edge of the graph with label :math:`l`.
   S (str): the *starting node*.
   F (set): the set of *final nodes*.
   large_labels (bool): whether the string labelling nodes are long and require pre-formatting before being drawn or not.

  Examples:
   The following code

   .. code:: ipython3

    StateTransitionGraph([
       ('node a','arc (a,b)','node b'),
       ('node a', 'arc (a,c)', 'node c'),
       ('node b', 'arc (b, c)', 'node c')],
     'node a', {'node b'})

   gives the following graph

   .. image:: stg.svg

   where nodes and edges are labeled as implied by the first parameter, the *staring* node has an (unlabelled)
   edge entering into it, whereas the *final nodes* are doubly circled.
  """

  def __init__(self, transitions, S = None, F = None, large_labels = False):
    self.transitions = tuple(transitions)
    self.S = S
    self.F = set() if F is None else F
    self.large_labels = large_labels
    self.G = None

  @classmethod
  def from_automaton(cls, A, coalesce_sets = True, large_labels = False):
    """A factory method to build a :class:`StateTransitionGraph` starting from an :class:`~liblet.automaton.Automaton`.

    Args:
      A (:class:`~liblet.automaton.Automaton`): the automaton.
      coalesce_sets (bool): whether the automata states are sets and the corresponding labels must be obtained joining the strings in the sets.
    """
    def tostr(N):
      if coalesce_sets and not large_labels and isinstance(N, Set):
        return HAIR_SPACE.join(sorted(map(str, N)))
      return N
    transitions = tuple((tostr(frm), label, tostr(to)) for frm, label, to in A.transitions)
    F = set(map(tostr, A.F))
    q0 = tostr(A.q0)
    return cls(transitions, q0, F, large_labels = large_labels)

  def _gvgraph_(self):
    if self.G: return self.G
    sep = '\n' if self.large_labels else None
    G = gvDigraph(
        graph_attr = {
          'rankdir': 'LR',
          'size': '32'
        },
        node_attr = {'margin': '.05'} if self.large_labels else {},
        engine = 'dot'
      )
    if self.S is not None:
      self.edge(G,
        self.node(G, '', id(self.S), gv_args = {'shape': 'none'}),
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

# Python AST stuff

def pyast2tree(node):
  if not isinstance(node, ast.AST):
    return Tree({'type': 'token', 'value': node})
  else:
    return Tree({'type': 'ast', 'name': node.__class__.__name__},
      [ Tree(name, [pyast2tree(v) for v in (value if isinstance(value, list) else [value])])
        for name, value in ast.iter_fields(node) if not name in {'type_ignores', 'type_comment'}
      ]
    )

# Jupyter Widgets sfuff

def animate_derivation(d, height = '300px'):
  steps = d.steps()
  d = Derivation(d.G)
  ui = interactive(
    lambda n: display(ProductionGraph(d.step(steps[:n]))),
    n = IntSlider(min = 0, max = len(steps), value = 0)
  )
  ui.children[-1].layout.height = height
  return ui

# HTML stuff

def __bordered_table__(content):
  return HTML('<style>td, th {border: 1pt solid lightgray !important ;}</style><table>'+ content + '</table>')


def side_by_side(*iterable):
  if len(iterable) == 1: iterable = iterable[0]
  return HTML('<div>{}</div>'.format(' '.join(item._repr_svg_() for item in iterable)))

def iter2table(it):
  return __bordered_table__('\n'.join(f'<tr><th style="text-align:left">{n}<td style="text-align:left"><pre>{_escape(e)}</pre>' for n, e in enumerate(it)))

def dict2table(it):
  return __bordered_table__('\n'.join(f'<tr><th style="text-align:left">{k}<td style="text-align:left"><pre>{_escape(v)}</pre>' for k, v in it.items()))

def dod2table(dod, sort = False, sep = None):
  def fmt(r, c):
    if not c in dod[r]: return '&nbsp;'
    elem = dod[r][c]
    if elem is None: return '&nbsp;'
    return '<pre>{}</pre>'.format(letstr(elem, sep))
  rows = list(dod.keys())
  if sort: rows = sorted(rows)
  cols = list(OrderedDict.fromkeys(chain.from_iterable(dod[x].keys() for x in dod)))
  if sort: cols = sorted(cols)
  head = '<tr><td>&nbsp;<th style="text-align:left">' + '<th style="text-align:left">'.join(cols)
  body = '\n'.join('<tr><th style="text-align:left"><pre>{}</pre><td style="text-align:left">{}'.format(letstr(r, sep), '<td style="text-align:left">'.join(fmt(r, c) for c in cols)) for r in rows)
  return __bordered_table__('{}\n{}\n'.format(head, body))

def cyk2table(TABLE):
  I, L = max(TABLE.keys())
  # when the nullable row (-, 0) is present the maximum key is (N + 1, 0)
  # (otherwise i <= N); in any case the lengths range in [N, L - 1)
  N = I - 1 if L == 0 else I
  return __bordered_table__('<tr>' +
    '<tr>'.join('<td style="text-align:left"><pre>' + '</pre></td><td style="text-align:left"><pre>'.join(
        (letstr(TABLE[(i, l)], sep = '\n') if TABLE[(i, l)] else '&nbsp;') for i in range(1, N - l + 2)
      ) + '</pre></td>' for l in range(N, L - 1, -1))
    )

def prods2table(G):
  """Deprecated. Use Productions instead"""
  wwarn('The function "prods2table" has been absorbed in Productions.', DeprecationWarning)
  return HTML(Productions(G.P)._repr_html_())

def ff2table(G, FIRST, FOLLOW):
  return dod2table({N: {'First': ' '.join(FIRST[(N, )]), 'Follow': ' '.join(FOLLOW[N])} for N in G.N})
