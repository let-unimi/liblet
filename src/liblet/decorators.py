from copy import deepcopy
from functools import wraps


def closure(f):
    """Wraps a function in a closure computation.

    This decorator takes a function ``f(S, O)`` and returns a function ``F(S, O)`` that repeatedly calls
    ``f`` on its own returned value and ``O`` until it doesn't change.

    Args:
        f: the function to wrap in the closure computation.

    Example:
        
        Consider the following example where the function ``f`` given a set ``S`` of integers and 
        an integer ``m`` as input, returns the set obtained adding to ``S`` all the values
        ``s - 1`` for all its elements greater than some lower limit ``m``.

        .. doctest::

            >>> @closure
            ... def reduce_up_to(S, m):
            ...     return S | {s - 1 for s in S if s > m}
            ... 
            >>> reduce_up_to({7,5}, 3)
            {3, 4, 5, 6, 7}

        It is evident that its closure will return the set of values from ``m`` to the largest element in ``S``.

    Notes:

        More formally, consider a function :math:`f : \mathfrak{D}\\times \mathfrak{X} \\to \mathfrak{D}` 
        where :math:`\mathfrak{D}` is a domain of interest and  :math:`\mathfrak{X}` is the (possibly 
        empty) domain of extra parameters. Define as usual the iterated application of :math:`f` as
        :math:`f^{(n + 1)}(D, X) = f(f^{(n)}(D, X), X)`, where :math:`f^{(0)}(D, X) = f(D, X)`. Then
        :math:`F = \\textit{closure}(f)` is the function 
        :math:`F: \mathfrak{D}\\times \mathfrak{X} \\to \mathfrak{D}`  defined as 
        :math:`F(D, X) = f^{(\hat{n})}(D, X)` where :math:`\hat{n}` is the minimum
        :math:`n` (depending on :math:`D` and :math:`X`) such that 
        :math:`f^{(\hat{n} + 1)}(D, X) = f^{(\hat{n})}(D, X)`.  

    """
    @wraps(f)
    def _closure(*args):
        s, *other = args
        while True:
            n = f(deepcopy(s), *other)
            if n == s: return s
            s = n
    return _closure

def show_calls(show_retval = False):
    """Wraps a function so that it calls (and return values) are printed when invoked.

    This decorator takes a function a decorated function that prints every invocation 
    (with the value of the parameters and optionally the returned value).

    Args:
        f: the function to wrap in the closure computation.
        show_retval: wether to show also the return values.

    Example:

        This is how to use the decorator with the classic recursive implementation of 
        the Fibonacci numbers computation.
        
        .. doctest::

            >>> @show_calls(True)
            ... def fib(n):
            ...     if n == 0 or n == 1: return 1
            ...     return fib(n - 1) + fib(n - 2)
            ... 
            >>> _ = fib(3)
            ┌fib(3)
            │┌fib(2)
            ││┌fib(1)
            ││└─ 1
            ││┌fib(0)
            ││└─ 1
            │└─ 2
            │┌fib(1)
            │└─ 1
            └─ 3
    """
    def _show_calls(f):
        f.depth = 0
        @wraps(f)
        def wrapper(*args, **kwds):
            f.depth += 1
            fargs = ', '.join(['{!r}'.format(a) for a in args] + ['{} = {!r}'.format(k, v) for k, v in kwds.items()])
            if show_retval: print('{}┌{}({})'.format('│' * (f.depth - 1), f.__name__, fargs))
            else: print('{}{}({})'.format(' ' * (f.depth - 1), f.__name__, fargs))
            ret = f(*args, **kwds)
            if show_retval: print('{}└─ {}'.format('│' * (f.depth - 1), ret))
            f.depth -= 1
            return ret
        return wrapper
    return _show_calls