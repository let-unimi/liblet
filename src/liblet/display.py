import ast
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Mapping, Set  # noqa: PYI025
from functools import partial
from html import escape
from itertools import chain, pairwise
from operator import itemgetter
from re import sub
from textwrap import indent
from warnings import warn as wwarn

import svgutils.transform as svg_ttransform
from graphviz import Digraph
from IPython.display import HTML, SVG, display
from ipywidgets import IntSlider, interactive

from liblet.const import GV_FONT_NAME, GV_FONT_SIZE, HTML_FONT_NAME, ε
from liblet.grammar import HAIR_SPACE, Derivation, Productions
from liblet.utils import AttrDict, CYKTable, compose, letstr


def _escape(label):
  return sub(r'\]', '&#93;', sub(r'\[', '&#91;', escape(str(label))))


def make_mapping_aware_label(
  other_str=letstr,  # in mapping_aware_label, how to represent non-mapping objects
  key_str=str,  # in mapping_aware_label, how to represent keys
  value_str=_escape,  # in mapping_aware_label, how to represent values
  key_filter=lambda k: not k.startswith('_thread_'),  # in mapping_aware_label, which keys to show
):
  def mapping_aware_label(obj):
    if obj is None:
      return None
    if isinstance(obj, Mapping):
      return ''.join(
        ['<<FONT POINT-SIZE="12"><TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">']
        + [f'<TR><TD>{key_str(k)}</TD><TD>{value_str(obj[k])}</TD></TR>' for k in filter(key_filter, obj)]
        + ['</TABLE></FONT>>']
      )
    return other_str(obj)

  return mapping_aware_label


def mapping_aware_gv_args(obj):
  return (
    {'shape': 'none', 'margin': '0', 'height': '0', 'width': '0'} if isinstance(obj, Mapping) else {'margin': '.05'}
  )


def make_node_wrapper(
  node_label=None,  # how to produce the node label from the node object
  node_eq='obj',  # how to decide equality between nodes
  node_gv_args=None,  # how to produce the default gv args from the node object
):
  if node_label is None:
    node_label = make_mapping_aware_label()
  elif not callable(node_label):
    raise ValueError('node_label must be either None or a callable')

  if node_eq == 'obj':
    node_eq = lambda x, y: x == y
  elif node_eq == 'label':
    node_eq = lambda x, y: node_label(x) == node_label(y)
  elif not callable(node_eq):
    raise ValueError('node_eq must be either "obj", "label" or a callable')

  if node_gv_args is None:
    node_gv_args = mapping_aware_gv_args
  elif not callable(node_gv_args):
    raise ValueError('node_gv_args must be either None or a callable')

  class EHW:
    def __init__(self, obj):
      self.obj = obj

    def __eq__(self, other):
      if not isinstance(other, EHW):
        return False
      return node_eq(self.obj, other.obj)

    def __hash__(self):
      return hash(node_label(self.obj))

  class NodeWrapper(EHW):
    _wn2gid = {}  # noqa: RUF012

    def __new__(cls, obj):
      ehw = EHW(obj)
      if ehw not in cls._wn2gid:
        intsance = cls._wn2gid[ehw] = super().__new__(cls)
        intsance._gid = f'N{len(cls._wn2gid)}'
      return cls._wn2gid[ehw]

    def gid(self):
      return self._gid

    def label(self):
      return node_label(self.obj)

    def gv_args(self):
      return node_gv_args(self.obj)

    def __repr__(self):
      return f'NodeWrapper[obj = {self.obj}, label = {self.label()}, hash = {hash(self)}]'

  return NodeWrapper


class GVWrapper:
  def __init__(self, gv_graph_args=None, node_wrapper=None):
    gv_graph_args = gv_graph_args or {}
    gv_graph_args['node_attr'] = {'fontname': GV_FONT_NAME, 'fontsize': GV_FONT_SIZE} | (
      gv_graph_args['node_attr'] if 'node_attr' in gv_graph_args else {}
    )
    gv_graph_args['edge_attr'] = {'fontname': GV_FONT_NAME, 'fontsize': GV_FONT_SIZE} | (
      gv_graph_args['edge_attr'] if 'edge_attr' in gv_graph_args else {}
    )
    node_wrapper = node_wrapper or make_node_wrapper()
    self.G = Digraph(**gv_graph_args)
    self.node_wrapper = node_wrapper
    self.nodes = set()

  def wrapped_graph(self):
    return self.G

  def subgraph(self, **args):
    return self.G.subgraph(**args)

  def node(self, obj, G=None, gv_args=None):
    if G is None:
      G = self.G
    wn = self.node_wrapper(obj)
    if wn.gid() not in self.nodes:
      G.node(wn.gid(), wn.label(), **(wn.gv_args() | (gv_args or {})))
      self.nodes.add(wn.gid())
    return wn

  def edge(self, objsrc, objdst, G=None, gv_args=None):
    if G is None:
      G = self.G
    G.edge(self.node(objsrc).gid(), self.node(objdst).gid(), **(gv_args or {}))

  def __repr__(self):
    return 'GVWrapper[\n' + indent(str(self.G), '\t') + ']'

  def _repr_svg_(self):
    return self.G._repr_image_svg_xml()


class BaseGraph(ABC):
  def __init__(self):
    wwarn('Inheriting from BaseGraph is deprecated, use GVWrapper instead', DeprecationWarning, stacklevel=2)

  @abstractmethod
  def _gvgraph_(self):
    pass

  # letstr(node) is always used as node_label
  # node_id is str(x) where x is id (if not None) or hash(node_label)
  def node(self, G, node, id=None, sep=None, gv_args=None):  # noqa: A002
    wwarn('The method "node" is deprecated, use GVWrapper instead of BaseGraph', DeprecationWarning, stacklevel=2)
    if gv_args is None:
      gv_args = {}
    if not hasattr(self, '_nodes'):
      self._nodes = set()
    node_label = letstr(node, sep)
    node_id = str(hash(node_label) if id is None else id)
    if node_id in self._nodes:
      return node_id
    G.node(node_id, node_label, **gv_args)
    self._nodes.add(node_id)
    return node_id

  # src and dst as str()-ed and used as ids
  def edge(self, G, src, dst, label=None, large_label=False, gv_args=None):
    wwarn('The method "edge" is deprecated, use GVWrapper instead of BaseGraph', DeprecationWarning, stacklevel=2)
    if gv_args is None:
      gv_args = {}
    label_param = {} if label is None else {'xlabel' if large_label else 'label': label}
    label_param.update(gv_args)
    G.edge(str(src), str(dst), **label_param)

  def _repr_svg_(self):
    wwarn(
      'The method "_repr_svg_" is deprecated, use GVWrapper instead of BaseGraph',
      DeprecationWarning,
      stacklevel=2,
    )
    return self._gvgraph_()._repr_image_svg_xml()


class Tree:
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

  def __init__(self, root, children=None):
    self.root = root
    self.children = list(children) if children else []
    if isinstance(root, Mapping):
      self.attr = AttrDict(root)

  def __iter__(self):
    return iter([self.root, *self.children])

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

  @classmethod
  def from_pyast(cls, node):
    """Builds a tree from a Python AST node.
    
    Args:
      node (ast.AST): the AST node.
    
    Example:
    
      The following code
    
    .. code:: ipython3
    
      import ast
      
      node = ast.parse('1 + 2', mode = 'eval')
      Tree.from_pyast(node)
      
    produces the following tree
    
    .. image:: ast.svg
      
    
    """

    def _to_tree(ast_node):
      return (
        cls(
          {'type': 'ast', 'name': ast_node.__class__.__name__},
          [
            cls(name, [_to_tree(v) for v in (value if isinstance(value, list) else [value])])
            for name, value in ast.iter_fields(ast_node)
            if name not in {'type_ignores', 'type_comment'}
          ],
        )
        if isinstance(ast_node, ast.AST)
        else cls({'type': 'token', 'value': ast_node})
      )

    return _to_tree(node)

  def __repr__(self):
    def walk(T):
      return '({}: {})'.format(T.root, ', '.join(map(walk, T.children))) if T.children else f'({T.root})'

    return walk(self)

  def _gv_graph_(self):
    G = GVWrapper(
      dict(  # noqa: C408
        graph_attr={'nodesep': '.25', 'ranksep': '.25'},
        node_attr={'shape': 'box', 'width': '0', 'height': '0', 'style': 'rounded, setlinewidth(.25)'},
        edge_attr={'dir': 'none'},
      ),
      make_node_wrapper(
        node_label=compose(make_mapping_aware_label(), itemgetter(0)),
        node_gv_args=compose(mapping_aware_gv_args, itemgetter(0)),
      ),
    )

    def walk(T):
      curr = (T.root, T)
      G.node(curr)
      for child in T.children:
        G.edge(curr, (child.root, child))
      if len(T.children) > 1:
        with G.subgraph(edge_attr={'style': 'invis'}, graph_attr={'rank': 'same'}) as S:
          for f, t in pairwise(T.children):
            G.edge((f.root, f), (t.root, t), S)
      for child in T.children:
        walk(child)

    walk(self)
    return G

  def _repr_svg_(self):
    return self._gv_graph_()._repr_svg_()

  def with_threads(self, threads):
    """Draws a *threaded* and *annotated* tree (as a graph).

    Tree *threads* are arcs among tree nodes (or special nodes), more precisely,
    a :obj:`dict` mapping annotated tree *source* nodes to a :obj:`dict` whose
    values are *destinations* tree nodes; arcs are represented as dotted arrows.
    Special nodes are: the *begin* tree (an annotated tree whose root contains
    the ``(type, <BEGIN>)`` item), the *join* trees (annotated trees whose root
    contains the ``(type, <JOIN>)`` item) and the *end* node  (annotated trees
    whose root contains the ``(type, <END>)`` item); such special nodes are
    represented as red dots.


    Args: threads (dict): a dictionary representing the threads.
    """

    G = self._gv_graph_()
    del G.wrapped_graph().edge_attr['dir']
    G.wrapped_graph().edge_attr['arrowsize'] = '.5'

    node_args = {'shape': 'point', 'width': '.07', 'height': '.07', 'color': 'red'}
    edge_args = {'dir': 'forward', 'arrowhead': 'vee', 'arrowsize': '.5', 'style': 'dashed', 'color': 'red'}

    for node in threads:
      if 'type' in node.root and node.root['type'] in ('<BEGIN>', '<JOIN>', '<END>'):
        G.node((node.root, node), gv_args=node_args)

    for node, info in threads.items():
      for nxt in info:
        if nxt == 'next':
          G.edge((node.root, node), (info[nxt].root, info[nxt]), gv_args=edge_args)
        else:
          G.node(
            (nxt, (1, node)),
            gv_args={'color': 'red', 'fontcolor': 'red', 'fontsize': '10', 'width': '.04', 'height': '.04'},
          )
          G.edge((node.root, node), (nxt, (1, node)), gv_args=edge_args | {'arrowhead': 'none'})
          G.edge((nxt, (1, node)), (info[nxt].root, info[nxt]), gv_args=edge_args)

    return G


class Graph:
  def __init__(self, arcs, sep=None):
    self.G = GVWrapper(
      dict(graph_attr={'size': '8', 'rankdir': 'LR'}, node_attr={'shape': 'oval'}),  # noqa: C408
      make_node_wrapper(node_label=make_mapping_aware_label(other_str=partial(letstr, sep=sep))),
    )
    self.adj = {}
    for src, dst in arcs:
      self.adj[src] = self.adj.get(src, set()) | {dst}
      self.adj[dst] = self.adj.get(dst, set())
      self.G.edge(src, dst)

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

  def _gv_graph_(self):
    return self.G

  def _repr_svg_(self):
    return self._gv_graph_()._repr_svg_()


class ProductionGraph:
  def __init__(self, derivation, compact=None):
    self.derivation = derivation
    if compact is None:
      self.compact = derivation.G.is_context_free
    else:
      self.compact = compact
    self.G = None

  def __repr__(self):
    return f'ProductionGraph({self.derivation})'

  def _gv_graph_(self):
    if self.G is not None:
      return self.G
    derivation = self.derivation
    G = GVWrapper(
      dict(  # noqa: C408
        graph_attr={'nodesep': '.25', 'ranksep': '.25'},
        node_attr={
          'shape': 'box',
          'margin': '.05',
          'width': '0',
          'height': '0',
          'style': 'rounded, setlinewidth(.25)',
        },
        edge_attr={'dir': 'none', 'penwidth': '.5', 'arrowsize': '.5'},
      ),
      make_node_wrapper(node_label=compose(make_mapping_aware_label(), itemgetter(0))),
    )

    def remove_ε(sentence):
      return tuple(_ for _ in sentence if _[0] != ε)

    sentence = ((derivation.start, 0, 0),)
    for step, (rule, pos) in enumerate(derivation.steps(), 1):
      lhs, rhs = derivation.G.P[rule].as_type0()
      rhsn = tuple((X, step, p) for p, X in enumerate(rhs))
      sentence = remove_ε(sentence[:pos] + rhsn + sentence[pos + len(lhs) :])
    last_sentence = set(sentence)

    use_levels = not self.compact

    sentence = ((derivation.start, 0, 0),)
    with G.subgraph(graph_attr={'rank': 'same'}) as S:
      if use_levels:
        prev_level = ('level', 0)
        G.node(prev_level, S, gv_args={'style': 'invis'})
      G.node(sentence[0], S)

    for step, (rule, pos) in enumerate(derivation.steps(), 1):
      lhs, rhs = derivation.G.P[rule].as_type0()
      rhsn = tuple((X, step, p) for p, X in enumerate(rhs))

      with G.subgraph(graph_attr={'rank': 'same'}, edge_attr={'style': 'invis'}) as S:
        if use_levels:
          new_level = ('level', step)
          G.node(new_level, S, gv_args={'style': 'invis'})
          G.edge(prev_level, new_level, gv_args={'style': 'invis'})
          prev_level = new_level

        for node in rhsn:
          G.node(
            node,
            S,
            gv_args={'style': 'rounded, setlinewidth(1.25)' if node in last_sentence else 'rounded, setlinewidth(.25)'},
          )

        for f, t in pairwise(rhsn):
          G.edge(f, t, S)

      if len(lhs) == 1:
        frm = sentence[pos]
        for to in rhsn:
          G.edge(frm, to)
      else:
        dot = ('dot', step)
        G.node(dot, gv_args={'shape': 'point', 'width': '.07', 'height': '.07'})
        for frm in sentence[pos : pos + len(lhs)]:
          G.edge(frm, dot)
        for to in rhsn:
          G.edge(dot, to)

      sentence = remove_ε(sentence[:pos] + rhsn + sentence[pos + len(lhs) :])

    self.G = G
    return G

  def _repr_svg_(self):
    return self._gv_graph_()._repr_svg_()


class StateTransitionGraph:
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

  def __init__(self, transitions, S=None, F=None, large_labels=False):
    self.transitions = tuple(transitions)
    self.S = S
    self.F = set() if F is None else F
    self.large_labels = large_labels
    self.G = None

  @classmethod
  def from_automaton(cls, A, coalesce_sets=True, large_labels=False):
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
    return cls(transitions, q0, F, large_labels=large_labels)

  def _gv_graph_(self):
    if self.G:
      return self.G
    sep = '\n' if self.large_labels else None
    G = GVWrapper(
      dict(  # noqa: C408
        graph_attr={'rankdir': 'LR', 'size': '32'},
        node_attr={'margin': '.05'} if self.large_labels else {},
        engine='dot',
      ),
      make_node_wrapper(
        node_label=make_mapping_aware_label(other_str=partial(letstr, sep=sep)),
        node_gv_args=lambda X: {'peripheries': '2' if X in self.F else '1'},
      ),
    )
    if self.S is not None:
      G.node('', gv_args={'shape': 'point'})
      G.edge('', self.S)
    for X, x, Y in self.transitions:
      G.edge(X, Y, gv_args={'xlabel' if self.large_labels else 'label': x})
    self.G = G
    return G

  def _repr_svg_(self):
    return self._gv_graph_()._repr_svg_()


# Python AST stuff


def pyast2tree(node):
  """Deprecated. Use Tree.from_pyast instead."""
  wwarn(
    'The function "pyast2tree" has been absorbed in Tree (as from_pyast factory method).',
    DeprecationWarning,
    stacklevel=2,
  )
  return (
    Tree(
      {'type': 'ast', 'name': node.__class__.__name__},
      [
        Tree(name, [pyast2tree(v) for v in (value if isinstance(value, list) else [value])])
        for name, value in ast.iter_fields(node)
        if name not in {'type_ignores', 'type_comment'}
      ],
    )
    if isinstance(node, ast.AST)
    else Tree({'type': 'token', 'value': node})
  )


# Jupyter Widgets sfuff


def animate_derivation(d, height='300px'):
  steps = d.steps()
  d = Derivation(d.G)
  ui = interactive(lambda n: display(ProductionGraph(d.step(steps[:n]))), n=IntSlider(min=0, max=len(steps), value=0))
  ui.children[-1].layout.height = height
  return ui


# HTML/SVG stuff


def __bordered_table__(content):  # noqa: N807
  return HTML(
    f'<style>td, th {{border: 1pt solid lightgray !important;}} table * {{font-family: "{HTML_FONT_NAME}";}}</style><table>'
    + content
    + '</table>'
  )


def resized_svg_repr(obj, width=800, height=600):
  if hasattr(obj, '_repr_image_svg_xml'):
    svg_str = obj._repr_image_svg_xml()
  elif hasattr(obj, '_repr_svg_'):
    svg_str = obj._repr_svg_()
  else:
    raise TypeError('The given object has no svg representation')
  svg_figure = svg_ttransform.fromstring(svg_str)
  svg_figure.set_size((str(width), str(height)))
  return SVG(svg_figure.to_str())


def side_by_side(*iterable):
  if len(iterable) == 1:
    iterable = iterable[0]
  return HTML('<div>{}</div>'.format(' '.join(item._repr_svg_() for item in iterable)))


def iter2table(it):
  return __bordered_table__(
    '\n'.join(
      f'<tr><th style="text-align:left">{n}<td style="text-align:left"><pre>{_escape(e)}</pre>'
      for n, e in enumerate(it)
    )
  )


def dict2table(it):
  return __bordered_table__(
    '\n'.join(
      f'<tr><th style="text-align:left">{k}<td style="text-align:left"><pre>{_escape(v)}</pre>' for k, v in it.items()
    )
  )


def dod2table(dod, sort=False, sep=None):
  def fmt(r, c):
    if c not in dod[r]:
      return '&nbsp;'
    elem = dod[r][c]
    if elem is None:
      return '&nbsp;'
    return f'<pre>{letstr(elem, sep)}</pre>'

  rows = list(dod.keys())
  if sort:
    rows = sorted(rows)
  cols = list(OrderedDict.fromkeys(chain.from_iterable(dod[x].keys() for x in dod)))
  if sort:
    cols = sorted(cols)
  head = '<tr><td>&nbsp;<th style="text-align:left">' + '<th style="text-align:left">'.join(cols)
  body = '\n'.join(
    '<tr><th style="text-align:left"><pre>{}</pre><td style="text-align:left">{}'.format(
      letstr(r, sep), '<td style="text-align:left">'.join(fmt(r, c) for c in cols)
    )
    for r in rows
  )
  return __bordered_table__(f'{head}\n{body}\n')


def cyk2table(TABLE):
  """Deprecated. Use CYKTable instead."""
  wwarn('The function "cyk2table" has been absorbed in CYKTable.', DeprecationWarning, stacklevel=2)
  t = CYKTable()
  for il, v in TABLE.items():
    t[il] = v
  return HTML(t._repr_html_())


def prods2table(G):
  """Deprecated. Use Productions instead"""
  wwarn('The function "prods2table" has been absorbed in Productions.', DeprecationWarning, stacklevel=2)
  return HTML(Productions(G.P)._repr_html_())


def ff2table(G, FIRST, FOLLOW):
  return dod2table({N: {'First': ' '.join(FIRST[(N,)]), 'Follow': ' '.join(FOLLOW[N])} for N in G.N})
