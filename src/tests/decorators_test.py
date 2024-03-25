import unittest
from contextlib import redirect_stdout
from io import StringIO

from liblet import closure, show_calls


class TestClosure(unittest.TestCase):
  def test_closure_func(self):
    @closure
    def dec(s):
      return s | {x - 1 for x in s if x > 0}

    self.assertEqual({0, 1, 2, 3, 4}, dec({4}))

  def test_closure_lambda(self):
    dec = closure(lambda s: s | {x - 1 for x in s if x > 0})
    self.assertEqual({0, 1, 2, 3, 4}, dec({4}))

  def test_closure_towargs(self):
    @closure
    def dec(s, d):
      return s | {x - d for x in s if x >= d}

    self.assertEqual({0, 2, 4}, dec({4}, 2))

  def test_show_calls_true(self):
    buf = StringIO()

    @show_calls(True)
    def fib(n):
      if n in (0, 1):
        return 1
      return fib(n - 1) + fib(n - 2)

    with redirect_stdout(buf):
      fib(4)
    expected = '┌fib(4)\n│┌fib(3)\n││┌fib(2)\n│││┌fib(1)\n│││└─ 1\n│││┌fib(0)\n│││└─ 1\n││└─ 2\n││┌fib(1)\n││└─ 1\n│└─ 3\n│┌fib(2)\n││┌fib(1)\n││└─ 1\n││┌fib(0)\n││└─ 1\n│└─ 2\n└─ 5\n'
    self.assertEqual(expected, buf.getvalue())

  def test_show_calls_false(self):
    buf = StringIO()

    @show_calls(False)
    def fac(n):
      if n == 0:
        return 1
      return n * fac(n - 1)

    with redirect_stdout(buf):
      fac(4)
      expected = 'fac(4)\n fac(3)\n  fac(2)\n   fac(1)\n    fac(0)\n'
      self.assertEqual(expected, buf.getvalue())

  def test_show_calls_args(self):
    buf = StringIO()

    @show_calls(False)
    def f(a, b, c):
      pass

    with redirect_stdout(buf):
      f(4, ['b'], c={'c': 1})
    expected = "f(4, ['b'], c = {'c': 1})\n"
    self.assertEqual(expected, buf.getvalue())


if __name__ == '__main__':
  unittest.main()
