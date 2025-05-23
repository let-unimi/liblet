import ast
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from collections.abc import Iterable, Mapping, Set  # noqa: PYI025
from functools import partial
from html import escape
from itertools import chain, count, pairwise
from operator import itemgetter
from re import sub
from textwrap import indent

import svgutils.transform as svg_ttransform
from graphviz import Digraph
from IPython.display import HTML, SVG, display
from ipywidgets import IntSlider, interactive

from liblet.const import CUSTOM_CSS, GV_FONT_NAME, GV_FONT_SIZE, ε
from liblet.grammar import HAIR_SPACE, Derivation, Productions
from liblet.utils import AttrDict, compose, deprecation_warning, letstr, warn


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

  def edge(self, objsrc, objdst, G=None, gv_args=None, srcport=None, dstport=None):
    if G is None:
      G = self.G
    src = self.node(objsrc).gid()
    if srcport is not None:
      src = f'{src}:{srcport}'
    dst = self.node(objdst).gid()
    if dstport is not None:
      dst = f'{dst}:{dstport}'
    G.edge(src, dst, **(gv_args or {}))

  def __repr__(self):
    return 'GVWrapper[\n' + indent(str(self.G), '\t') + ']'

  def _repr_svg_(self):
    return self.G._repr_image_svg_xml()


class BaseGraph(ABC):
  def __init__(self):
    deprecation_warning('Inheriting from BaseGraph is deprecated, use GVWrapper instead')

  @abstractmethod
  def _gvgraph_(self):
    pass

  # letstr(node) is always used as node_label
  # node_id is str(x) where x is id (if not None) or hash(node_label)
  def node(self, G, node, id=None, sep=None, gv_args=None):  # noqa: A002
    deprecation_warning('The method "node" is deprecated, use GVWrapper instead of BaseGraph')
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
    deprecation_warning('The method "edge" is deprecated, use GVWrapper instead of BaseGraph')
    if gv_args is None:
      gv_args = {}
    label_param = {} if label is None else {'xlabel' if large_label else 'label': label}
    label_param.update(gv_args)
    G.edge(str(src), str(dst), **label_param)

  def _repr_svg_(self):
    deprecation_warning('The method "_repr_svg_" is deprecated, use GVWrapper instead of BaseGraph')
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

  __INSTANCE_COUNT = 0

  def __init__(self, root, children=None):
    self.root = root
    self.children = list(children) if children else []
    if isinstance(root, Mapping):
      self.attr = AttrDict(root)
    Tree.__INSTANCE_COUNT += 1
    self.__instance_count = Tree.__INSTANCE_COUNT

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

  @property
  def child(self):
    """Returns the only child of the tree, or raises an exception.

    Returns:
      The first child of the tree.
    Raises:
      ValueError: if the tree has no children or more than one child.
    """
    if len(self.children) == 1:
      return self.children[0]
    if len(self.children) == 0:
      raise ValueError('No children available')
    raise ValueError('More than one child present')

  def to_lol(self, undict=False):
    """
    Converts the tree to a *list of lists*.

    Args:
      undict (bool): if True and the root is a Mapping, it will be converted to a sorted tuple of key-value pairs.

    Returns:
      A list of lists representing the tree.
    """

    def walk(T):
      if undict and isinstance(T.root, Mapping):
        root = tuple((k, v) for k, v in sorted(T.root.items()) if not k.startswith('_thread_'))
      else:
        root = T.root
      return (root, *tuple(walk(child) for child in T.children))

    return walk(self)

  def __repr__(self):
    def walk(T):
      return '({}: {})'.format(T.root, ', '.join(map(walk, T.children))) if T.children else f'({T.root})'

    return walk(self)

  def __eq__(self, other):
    return isinstance(other, Tree) and self.to_lol() == other.to_lol()

  def __hash__(self):
    return hash(self.to_lol(True))

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
      curr = (T.root, T.__instance_count)
      G.node(curr)
      for child in T.children:
        G.edge(curr, (child.root, child.__instance_count))
      if len(T.children) > 1:
        with G.subgraph(edge_attr={'style': 'invis'}, graph_attr={'rank': 'same'}) as S:
          for f, t in pairwise(T.children):
            G.edge((f.root, f.__instance_count), (t.root, t.__instance_count), S)
      for child in T.children:
        walk(child)

    walk(self)
    return G

  def _repr_svg_(self):
    return self._gv_graph_()._repr_svg_()

  def with_threads(self, threads):
    """Draws a *threaded* and *annotated* tree (as a graph).

    Tree *threads* are arcs among tree nodes (or special nodes).

    Such threads can be represented in a compact way as a :obj:`dict` mapping
    annotated tree *source* nodes to a :obj:`dict` whose values are *destinations*
    tree nodes; arcs are represented as dotted arrows.

    A more verbose is also possible: a :obj:`list` of annotated tree nodes where
    some attributes begin with ``'_thread_'`` and contain the *destination*
    tree nodes.

    Special nodes are: the *begin* tree (an annotated tree whose root contains
    the ``(type, <BEGIN>)`` item), the *join* trees (annotated trees whose root
    contains the ``(type, <JOIN>)`` item) and the *end* node  (annotated trees
    whose root contains the ``(type, <END>)`` item); such special nodes are
    represented as red dots.

    Args: threads (dict|list): a compact, or verbose, representation of the threads.
    """

    if isinstance(threads, list):
      threads = {
        source: {
          name.removeprefix('_thread_'): dest for name, dest in source.root.items() if name.startswith('_thread_')
        }
        for source in threads
      }

    G = self._gv_graph_()
    del G.wrapped_graph().edge_attr['dir']
    G.wrapped_graph().edge_attr['arrowsize'] = '.5'

    node_args = {'shape': 'point', 'width': '.07', 'height': '.07', 'color': 'red'}
    edge_args = {'dir': 'forward', 'arrowhead': 'vee', 'arrowsize': '.5', 'style': 'dashed', 'color': 'red'}

    for node in threads:
      if 'type' in node.root and node.root['type'] in ('<BEGIN>', '<JOIN>', '<END>'):
        G.node((node.root, node.__instance_count), gv_args=node_args)

    for node, info in threads.items():
      for nxt in info:
        if nxt == 'next':
          G.edge((node.root, node.__instance_count), (info[nxt].root, info[nxt].__instance_count), gv_args=edge_args)
        else:
          G.node(
            (nxt, (1, node.__instance_count)),
            gv_args={'color': 'red', 'fontcolor': 'red', 'fontsize': '10', 'width': '.04', 'height': '.04'},
          )
          G.edge(
            (node.root, node.__instance_count),
            (nxt, (1, node.__instance_count)),
            gv_args=edge_args | {'arrowhead': 'none'},
          )
          G.edge((nxt, (1, node.__instance_count)), (info[nxt].root, info[nxt].__instance_count), gv_args=edge_args)

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
  """A production graph representing a derivation as a dag (or tree, if the grammar is context-free)."""

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


class ComputationGraph:
  """A class to represent a computation (nodes usually are :class:`~liblet.automaton.InstantaneousDescription`)."""

  def __init__(self, node2color=None, node2label=None, width=800, height=600):
    self.width = width
    self.height = height
    self.counted = {}
    self.counter = count()
    if node2color is None:
      node2color = lambda _: 'black'
    if node2label is None:
      node2label = (
        lambda node: f"""
        <<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
        <TR><TD PORT="in">{node._stack_str_()}</TD></TR>
        <TR><TD PORT="out">{node._tape_str_()}</TD><TD BORDER="0"><I>&nbsp;{self.counted[node]}</I></TD></TR>
        </TABLE>>
      """.strip()
      )
    self.G = GVWrapper(
      gv_graph_args={'node_attr': {'shape': 'none'}},
      node_wrapper=make_node_wrapper(node_label=node2label, node_gv_args=node2color),
    )

  def seen(self, node):
    return node in self.counted

  def step(self, src, dst, label=''):
    def count(node):
      if node not in self.counted:
        self.counted[node] = next(self.counter)
      return self.counted[node]

    count(src)
    count(dst)
    self.G.edge(src, dst, gv_args={'label': label}, srcport='out', dstport='in')

  def __repr__(self):
    return self.G.__repr__()

  def _repr_svg_(self):
    return resized_svg_repr(self.G, width=self.width, height=self.height, as_str=True)

  def resized_svg(self, height, width):
    return resized_svg_repr(self.G, width, height)


class Table:
  """A one or two-dimensional *table* able to detect conflicts and with a nice HTML representation, based on :obj:`~collections.defaultdict`."""

  DEFAULT_FORMAT = {  # noqa: RUF012
    'cols_sort': False,
    'rows_sort': False,
    'letstr_sort': False,
    'cols_sep': ', ',
    'rows_sep': ', ',
    'elem_sep': ', ',
  }

  def __init__(self, ndim=1, element=lambda: None, no_reassign=False, fmt=None):
    if ndim not in {1, 2}:
      raise ValueError('The ndim must be 1, or 2')
    self.ndim = ndim
    if ndim == 1:
      self.data = defaultdict(element)
    else:
      self.data = defaultdict(lambda: defaultdict(element))
    self.element = element
    self.no_reassign = no_reassign
    self.fmt = dict(Table.DEFAULT_FORMAT)
    if fmt is not None:
      self.fmt.update(fmt)

  @staticmethod
  def _make_hashable(idx):
    if isinstance(idx, list):
      return tuple(idx)
    if isinstance(idx, set):
      return frozenset(idx)
    return idx

  def __getitem__(self, key):
    if self.ndim == 2:  # noqa: PLR2004
      if not (isinstance(key, tuple) and len(key) == 2):  # noqa: PLR2004
        raise ValueError('Index is not a pair of values')
      r, c = Table._make_hashable(key[0]), Table._make_hashable(key[1])
      return self.data[r][c]
    r = Table._make_hashable(key)
    return self.data[r]

  def __setitem__(self, key, value):
    if self.ndim == 2:  # noqa: PLR2004
      if not (isinstance(key, tuple) and len(key) == 2):  # noqa: PLR2004
        raise ValueError('Index is not a pair of values')
      r, c = Table._make_hashable(key[0]), Table._make_hashable(key[1])
      if self.no_reassign and c in self.data[r]:
        warn(f'Table already contains value {self.data[r][c]} for ({r}, {c}), cannot store {value}')
      else:
        self.data[r][c] = value
    else:
      r = Table._make_hashable(key)
      if self.no_reassign and r in self.data:
        warn(f'Table already contains value {self.data[r]} for {r}, cannot store {value}')
      else:
        self.data[r] = value

  def __eq__(self, other):
    if not isinstance(other, Table):
      return False
    return self.data == other.data

  def __hash__(self):
    return hash(self.data)

  def restrict_to(self, rows=None, cols=None):
    if rows is None:
      rows = list(self.data.keys())
    R = Table(self.ndim, self.element, self.no_reassign, self.fmt)
    if self.ndim == 1:
      if cols is not None:
        raise ValueError('Columns cannot be specified, since the dimension is 1')
      for r in rows:
        if r in self.data:
          R.data[r] = self.data[r]
    else:
      if cols is None and self.ndim == 2:  # noqa: PLR2004
        cols = list(OrderedDict.fromkeys(chain.from_iterable(self.data[x].keys() for x in rows)))
      for r in rows:
        if r not in self.data:
          continue
        for c in cols:
          if c in self.data[r]:
            R.data[r][c] = self.data[r][c]
    return R

  def _repr_html_(self):
    def _pre(s):
      return (
        '<pre>' + escape(letstr(s, self.fmt['elem_sep'], sort=self.fmt['letstr_sort'], remove_outer=True)) + '</pre>'
      )

    def _fmt(r, c):
      if c not in self.data[r]:
        return '&nbsp;'
      elem = self.data[r][c]
      if elem is None:
        return '&nbsp;'
      return _pre(elem)

    if self.ndim == 2:  # noqa: PLR2004
      rows = list(self.data.keys())
      if self.fmt['rows_sort']:
        rows = sorted(rows)
      cols = list(OrderedDict.fromkeys(chain.from_iterable(self.data[x].keys() for x in rows)))
      if self.fmt['cols_sort']:
        cols = sorted(cols)
      return liblet_table(
        ['<tr><th>&nbsp;</th><th>' + '</th><th>'.join(_pre(col) for col in cols) + '</th></tr>']
        + [f'<tr><th>{_pre(r)}</th><td>' + '</td><td>'.join(_fmt(r, c) for c in cols) + '</td></tr>' for r in rows],
        True,
      )
    rows = list(self.data.keys())
    if self.fmt['rows_sort']:
      rows = sorted(rows)
    return liblet_table((f'<tr><th>{_pre(r)}</th><td>{_pre(self.data[r])}</td></tr>' for r in rows), True)


class CYKTable(Table):
  def __init__(self):
    super().__init__(ndim=2, element=set)

  def _repr_html_(self):
    TABLE = {(i, l): v for i, row in self.data.items() for l, v in row.items()}  # noqa: E741
    I, L = max(TABLE.keys())  # noqa: E741
    # when the nullable row (-, 0) is present the maximum key is (N + 1, 0)
    # (otherwise i <= N); in any case the lengths range in [N, L - 1)
    N = I - 1 if L == 0 else I
    return liblet_table(
      '<tr>'
      + '<tr>'.join(
        '<td><pre>'
        + '</pre></td><td><pre>'.join(
          (letstr(TABLE[(i, l)], sep='\n') if TABLE[(i, l)] else '&nbsp;') for i in range(1, N - l + 2)
        )
        + '</pre></td>'
        for l in range(N, L - 1, -1)  # noqa: E741
      ),
      True,
    )


# Python AST stuff


def pyast2tree(node):
  """Deprecated. Use Tree.from_pyast instead."""
  deprecation_warning('The function "pyast2tree" has been absorbed in Tree (as from_pyast factory method)')
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


def embed_css(custom_css=CUSTOM_CSS):
  return HTML(f'<style>{custom_css}</style>')


def liblet_table(content, as_str=False):
  if not isinstance(content, str) and isinstance(content, Iterable):
    content = '\n'.join(str(line) for line in content)
  html = f'<table class="liblet" data-quarto-disable-processing="true">{content}</table>'
  return html if as_str else HTML(html)


def resized_svg_repr(obj, width=800, height=600, as_str=False):
  if hasattr(obj, '_repr_image_svg_xml'):
    svg_str = obj._repr_image_svg_xml()
  elif hasattr(obj, '_repr_svg_'):
    svg_str = obj._repr_svg_()
  else:
    raise TypeError('The given object has no svg representation')
  svg_figure = svg_ttransform.fromstring(svg_str)
  svg_figure.set_size((str(width), str(height)))
  return svg_figure.to_str().decode('utf-8') if as_str else SVG(svg_figure.to_str())


def side_by_side(*iterable):
  if len(iterable) == 1:
    iterable = iterable[0]
  return HTML('<div>{}</div>'.format(' '.join(item._repr_svg_() for item in iterable)))


def iter2table(it):
  return liblet_table(f'<tr><th>{n}</th><td><pre>{_escape(e)}</pre></td></tr>' for n, e in enumerate(it))


def dict2table(it):
  return liblet_table(f'<tr><th>{k}</th><td><pre>{_escape(v)}</pre></td></tr>' for k, v in it.items())


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
  return liblet_table(
    ['<tr><th>&nbsp;</th><th>' + '</th><th>'.join(cols) + '</th></tr>']
    + [
      f'<tr><th><pre>{letstr(r, sep)}</pre></th><td>' + '</td><td>'.join(fmt(r, c) for c in cols) + '</td></tr>'
      for r in rows
    ]
  )


def cyk2table(TABLE):
  """Deprecated. Use CYKTable instead."""
  deprecation_warning('The function "cyk2table" has been absorbed in CYKTable')
  t = CYKTable()
  for il, v in TABLE.items():
    t[il] = v
  return HTML(t._repr_html_())


def prods2table(G):
  """Deprecated. Use Productions instead"""
  deprecation_warning('The function "prods2table" has been absorbed in Productions')
  return HTML(Productions(G.P)._repr_html_())


def ff2table(G, FIRST, FOLLOW):
  return dod2table({N: {'First': ' '.join(FIRST[(N,)]), 'Follow': ' '.join(FOLLOW[N])} for N in G.N})
