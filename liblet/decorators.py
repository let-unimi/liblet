from copy import deepcopy
from functools import wraps


def closure(f):
    @wraps(f)
    def _closure(*args):
        s, *other = args
        while True:
            n = f(deepcopy(s), *other)
            if n == s: return s
            s = n
    return _closure

def show_calls(show_retval = False):
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