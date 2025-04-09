from collections import deque
from collections.abc import MutableMapping, Set  #  noqa: PYI025
from functools import partial, reduce
from sys import stderr
from warnings import warn as _warn


def suffixes(α):
  """Yields all the suffixes of the given sentential form."""
  for i in range(len(α)):
    yield α[i:]


def deprecation_warning(msg):
  """Emits a *deprecation* warning."""
  _warn(msg, DeprecationWarning, stacklevel=2)


def warn(msg):
  """Emits a string on the *standard error*."""
  stderr.write(msg + '\n')


def first(s):
  """Returns the first element of the iterable  or `None` if empty."""
  return next(iter(s)) if s else None


def peek(s):  # pragma: nocover
  """Deprecated. Use first"""
  deprecation_warning('The function "peek" is now deprecated, please use "first" instead')
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
  """A convenience implementation of a *queue* providing the usual ``enqueue``, ``dequeue`` methods.

  An instance of this class can be created with an iterable and the final result will be
  the as if the elements of the iterable were added to an empty queue. Similarly, iterating
  a queue, returns (without consuming) the elements in the order they could be obtained by
  dequeuing them.

  Example:

    .. doctest::

      >>> from liblet.utils import Queue
      >>> q0 = Queue([1, 2, 3])
      >>> q1 = Queue()
      >>> for i in 1, 2, 3:
      ...   q1.enqueue(i)
      >>> q0 == q1
      True
      >>> list(q0)
      [1, 2, 3]
      >>> while q0:
      ...   print(q0.dequeue())
      1
      2
      3

  """

  def __init__(self, iterable=None, maxlen=None):
    self.Q = deque(iterable, maxlen) if iterable is not None else deque(maxlen=maxlen)

  def enqueue(self, item):
    self.Q.append(item)

  def dequeue(self):
    return self.Q.popleft()

  def copy(self):  # pragma: nocover
    deprecation_warning('The copy method is deprecated, use the copy module')
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
  """A convenience implementation of a *stack* providing the usual ``push``, ``pop``, ``peek``, methods.

  An instance of this class can be created with an iterable and the final result will be
  the as if the elements of the iterable were added to an empty stack. Similarly, iterating
  a stack, returns (without consuming) the elements in the order they could be obtained by
  popping them.

  Warnings:

    The iteration order has changed in version 1.12, before it was reversed!


  Example:

    .. doctest::

      >>> from liblet.utils import Stack
      >>> s0 = Stack([1, 2, 3])
      >>> s1 = Stack()
      >>> for i in 1, 2, 3:
      ...   s1.push(i)
      >>> s0 == s1
      True
      >>> list(s0)
      [3, 2, 1]
      >>> while s0:
      ...   print(s0.pop())
      3
      2
      1

  """

  def __init__(self, iterable=None, maxlen=None):
    self.S = deque(iterable, maxlen) if iterable is not None else deque(maxlen=maxlen)

  def push(self, item):
    self.S.append(item)

  def peek(self):
    return self.S[-1]

  def pop(self):
    return self.S.pop()

  def copy(self):  # pragma: nocover
    deprecation_warning('The copy method is deprecated, use the copy module')
    return self.__copy__()

  def __copy__(self):
    return Stack(self.S, self.S.maxlen)

  def __iter__(self):
    return reversed(self.S)

  def __reversed__(self):
    return iter(self.S)

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


def uc(s, c=''):  # pragma: nocover
  return ''.join(_ + c for _ in s)


uc.dot = partial(uc, c='\u0307')
uc.overline = partial(uc, c='\u0305')
uc.prime = partial(uc, c='\u031b')
