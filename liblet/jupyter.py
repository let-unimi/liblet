from IPython import get_ipython
from IPython.display import HTML


_is2t = lambda x: isinstance(x, tuple) and len(x) == 2
_isalt = lambda x: isinstance(x, tuple) and all(isinstance(_, str) for _ in x)
_isdottedalt = lambda x: _is2t(x) and isinstance(x[0], int) and _isalt(x[1])
_isprod = lambda x: _is2t(x) and isinstance(x[0], str) and _isalt(x[1])
_isdottedprod = lambda x: _is2t(x) and isinstance(x[0], str) and _isdottedalt(x[1])

def _let_tuple_repr(x):
    if _isdottedalt(x):
        b, a = x
        return _let_tuple_repr(a[:b] + ('•', ) + a[b:])
    if _isalt(x): return ' '.join(x)
    if _isprod(x) or _isdottedprod(x):
        return '{} -> {}'.format(x[0], _let_tuple_repr(x[1]))
    return None

def set_tuple_formatter():
    def _let_tuple_fmt(x, p, cycle):
        r = _let_tuple_repr(x)
        if r: return p.text(r)
        else: return _tuple_fmt(x, p, cycle)
    plain = get_ipython().display_formatter.formatters['text/plain']
    _tuple_fmt = plain.for_type(tuple)
    plain.for_type(tuple, _let_tuple_fmt)

def side_by_side(*iterable):
    return HTML('<div>{}</div>'.format(' '.join(item._repr_svg_() for item in iterable)))

