from collections import OrderedDict, defaultdict, deque
from collections.abc import MutableMapping, Set  #  noqa: PYI025
from functools import partial, reduce
from html import escape
from itertools import chain
from sys import stderr
from warnings import warn as wwarn

from liblet.const import HTML_FONT_NAME


def suffixes(α):
  for i in range(len(α)):
    yield α[i:]


def warn(msg):
  """Emits a string on the *standard error*."""
  stderr.write(msg + '\n')


def first(s):
  """Deprecated. Use set.pop"""
  wwarn('The function "first" is now deprecated, please use "pop" instead.', DeprecationWarning, stacklevel=2)
  return next(iter(s)) if s else None


def peek(s):  # pragma: nocover
  """Deprecated. Use first"""
  wwarn('The function "peek" is now deprecated, please use "first" instead.', DeprecationWarning, stacklevel=2)
  return first(s)


def union_of(s):
  """Return the set union of its arguments."""
  return set().union(*s)


def compose(*funcs):
  return reduce(lambda f, g: lambda x: f(g(x)), funcs)


def letstr(obj, sep=None, sort=True, remove_outer=False):
  if sep is None:
    sep = ', '

  def _ls(obj):
    if isinstance(obj, str):
      return obj
    fs = None
    if isinstance(obj, Set):
      fs = '{{{}}}'
    elif isinstance(obj, list):
      fs = '[{}]'
    elif isinstance(obj, tuple):
      fs = '({})'
    if fs is None:
      return str(obj)
    if sep == '\n' or remove_outer:
      fs = '{}'
    return fs.format(sep.join(sorted(map(_ls, obj)) if sort else list(map(_ls, obj))))

  return _ls(obj)


class Queue:
  """A convenience implementation of a *queue* providing the usual ``enqueue``, ``dequeue`` methods."""

  def __init__(self, iterable=None, maxlen=None):
    self.Q = deque(iterable, maxlen) if iterable is not None else deque(maxlen=maxlen)

  def enqueue(self, item):
    self.Q.append(item)

  def dequeue(self):
    return self.Q.popleft()

  def copy(self):  # pragma: nocover
    wwarn('The copy method is deprecated, use the copy module.', DeprecationWarning, stacklevel=2)
    return self.__copy__()

  def __copy__(self):
    return Queue(self.Q, self.Q.maxlen)

  def __iter__(self):
    return iter(self.Q)

  def __reversed__(self):
    return reversed(self.Q)

  def __repr__(self):
    el = ', '.join(map(repr, self.Q))
    return 'Queue({})'.format(f'← {el} ←' if el else '')

  def __len__(self):
    return len(self.Q)

  def __hash__(self):
    return hash(tuple(self.Q))

  def __eq__(self, other):
    if not isinstance(other, Queue):
      return False
    return self.Q == other.Q


class Stack:
  """A convenience implementation of a *stack* providing the usual ``push``, ``pop``, ``peek``, methods."""

  def __init__(self, iterable=None, maxlen=None):
    self.S = deque(iterable, maxlen) if iterable is not None else deque(maxlen=maxlen)

  def push(self, item):
    self.S.append(item)

  def peek(self):
    return self.S[-1]

  def pop(self):
    return self.S.pop()

  def copy(self):  # pragma: nocover
    wwarn('The copy method is deprecated, use the copy module.', DeprecationWarning, stacklevel=2)
    return self.__copy__()

  def __copy__(self):
    return Stack(self.S, self.S.maxlen)

  def __iter__(self):
    return iter(self.S)

  def __reversed__(self):
    return reversed(self.S)

  def __repr__(self):
    el = ', '.join(map(repr, self.S))
    return 'Stack({})'.format(f'{el} ↔' if el else '')

  def __len__(self):
    return len(self.S)
  
  def __hash__(self):
    return hash(tuple(self.S))
  
  def __eq__(self, other):
    if not isinstance(other, Stack):
      return False
    return self.S == other.S


class AttrDict(MutableMapping):
  """A :class:`~collections.abc.MutableMapping` implementation that wraps
  a given mapping ``d`` so that if ``ad = AttrDict(d)`` it will then
  become completely equivalent to write ``d['key']``, ``ad['key']``
  or ``ad.key``.
  """

  def __init__(self, mapping):
    object.__setattr__(self, '_AttrDict__store', mapping)

  def __getattr__(self, key):
    return self.__store[key]

  def __setattr__(self, key, val):
    self.__store[key] = val

  def __getitem__(self, key):
    return self.__store[key]

  def __setitem__(self, key, value):
    self.__store[key] = value

  def __delitem__(self, key):
    del self.__store[key]

  def __iter__(self):
    return iter(self.__store)

  def __len__(self):
    return len(self.__store)

  def __repr__(self):
    return f'AttrDict({self.__store})'


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
      raise ValueError('The ndim must be 1, or 2.')
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
    def _table(content):
      return (
        f'<style>td, th {{border: 1pt solid lightgray !important; text-align: left !important;}} table * {{font-family: "{HTML_FONT_NAME}";}}</style><table>'
        + content
        + '</table>'
      )

    def _fmt(r, c):
      if c not in self.data[r]:
        return '&nbsp;'
      elem = self.data[r][c]
      if elem is None:
        return '&nbsp;'
      return '<pre>{}</pre>'.format(
        escape(letstr(elem, self.fmt['elem_sep'], sort=self.fmt['letstr_sort'], remove_outer=True)),
      )

    if self.ndim == 2:  # noqa: PLR2004
      rows = list(self.data.keys())
      if self.fmt['rows_sort']:
        rows = sorted(rows)
      cols = list(OrderedDict.fromkeys(chain.from_iterable(self.data[x].keys() for x in rows)))
      if self.fmt['cols_sort']:
        cols = sorted(cols)
      head = (
        '<tr><td>&nbsp;<th><pre>'
        + '</pre><th><pre>'.join(
          letstr(col, self.fmt['cols_sep'], sort=self.fmt['letstr_sort'], remove_outer=True) for col in cols
        )
        + '</pre>'
      )
      body = '\n'.join(
        '<tr><th><pre>{}<pre><td>'.format(
          letstr(r, self.fmt['rows_sep'], sort=self.fmt['letstr_sort'], remove_outer=True)
        )
        + '<td>'.join(_fmt(r, c) for c in cols)
        for r in rows
      )
      return _table(f'{head}\n{body}\n')
    rows = list(self.data.keys())
    if self.fmt['rows_sort']:
      rows = sorted(rows)
    return _table(
      '\n'.join(
        '<tr><th><pre>{}</pre><td><pre>{}</pre>'.format(
          letstr(r, self.fmt['rows_sep'], sort=self.fmt['letstr_sort'], remove_outer=True),
          letstr(self.data[r], self.fmt['elem_sep'], sort=self.fmt['letstr_sort'], remove_outer=True),
        )
        for r in rows
      )
    )


class CYKTable(Table):
  def __init__(self):
    super().__init__(ndim=2, element=set)

  def _repr_html_(self):
    TABLE = {(i, l): v for i, row in self.data.items() for l, v in row.items()}  # noqa: E741
    I, L = max(TABLE.keys())  # noqa: E741
    # when the nullable row (-, 0) is present the maximum key is (N + 1, 0)
    # (otherwise i <= N); in any case the lengths range in [N, L - 1)
    N = I - 1 if L == 0 else I
    return (
      '<style>td, th {border: 1pt solid lightgray !important ;}</style><table>'
      + (
        '<tr>'
        + '<tr>'.join(
          '<td style="text-align:left"><pre>'
          + '</pre></td><td style="text-align:left"><pre>'.join(
            (letstr(TABLE[(i, l)], sep='\n') if TABLE[(i, l)] else '&nbsp;') for i in range(1, N - l + 2)
          )
          + '</pre></td>'
          for l in range(N, L - 1, -1)  # noqa: E741
        )
      )
      + '</table>'
    )


def uc(s, c=''):  # pragma: nocover
  return ''.join(_ + c for _ in s)


uc.dot = partial(uc, c='\u0307')
uc.overline = partial(uc, c='\u0305')
uc.prime = partial(uc, c='\u031b')
