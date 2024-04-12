import unittest
import unittest.mock
from contextlib import redirect_stdout
from io import StringIO
from textwrap import dedent

from liblet import ANTLR, AnnotatedTreeWalker, Tree


class TestGenerationAndParsing(unittest.TestCase):
  def test_noname(self):
    with self.assertRaisesRegex(ValueError, 'name not found'):
      ANTLR("a: 'rule'")

  def test_invalid_grammar(self):
    with unittest.mock.patch('liblet.antlr.warn') as mock_warn:
      ANTLR('grammar A; a: rule;')
      args, kwargs = mock_warn.call_args
    self.assertTrue('reference to undefined rule' in args[0])

  def test_tokens(self):
    Tk = ANTLR(
      r"""
      grammar Tk ;
      start: ID+ ;
      ID: [a-z]+;
      WS : [ \t]+ -> skip ;
    """
    )
    tks = ' '.join(list(map(str, Tk.tokens('tic gulp boom'))))
    self.assertEqual(
      tks, "[@0,0:2='tic',<1>,1:0] [@1,4:7='gulp',<1>,1:4] [@2,9:12='boom',<1>,1:9] [@3,13:12='<EOF>',<-1>,1:13]"
    )

  def test_tree_str(self):
    Bad = ANTLR(
      r"""
      grammar Bad ;

      start: expr ;
      expr: ID | expr OP ID | expr '*' ID;

      OP: '+' | '-' ;
      ID: [a-z];
    """
    )
    tree = Bad.context(
      'z-a+a*x',
      'start',
      as_string=True,
    )
    self.assertEqual(tree, '(start (expr (expr (expr (expr z) - a) + a) * x))')

  def test_tree_simple(self):
    Bad = ANTLR(
      r"""
      grammar Bad ;

      start: expr ;
      expr: ID | expr OP ID | expr '*' ID;

      OP: '+' | '-' ;
      ID: [a-z];
    """
    )
    tree = str(Bad.tree('z-a+a*x', 'start', simple=True))
    self.assertEqual(tree, '(start: (expr: (expr: (expr: (expr: (z)), (-), (a)), (+), (a)), (*), (x)))')

  def test_tree(self):
    Bad = ANTLR(
      r"""
      grammar Bad ;

      start: expr ;
      expr: ID | expr OP ID | expr '*' ID;

      OP: '+' | '-' ;
      ID: [a-z];
    """
    )
    tree = str(Bad.tree('z-a+a*x', 'start'))
    self.assertEqual(
      tree,
      r"({'type': 'rule', 'name': 'start', 'rule': 'start', 'src': (0, 6), 'line': 1}: ({'type': 'rule', 'name': 'expr', 'rule': 'expr', 'src': (0, 6), 'line': 1}: ({'type': 'rule', 'name': 'expr', 'rule': 'expr', 'src': (0, 4), 'line': 1}: ({'type': 'rule', 'name': 'expr', 'rule': 'expr', 'src': (0, 2), 'line': 1}: ({'type': 'rule', 'name': 'expr', 'rule': 'expr', 'src': (0, 0), 'line': 1}: ({'type': 'token', 'name': 'ID', 'value': 'z', 'src': 0, 'line': 1})), ({'type': 'token', 'name': 'OP', 'value': '-', 'src': 1, 'line': 1}), ({'type': 'token', 'name': 'ID', 'value': 'a', 'src': 2, 'line': 1})), ({'type': 'token', 'name': 'OP', 'value': '+', 'src': 3, 'line': 1}), ({'type': 'token', 'name': 'ID', 'value': 'a', 'src': 4, 'line': 1})), ({'type': 'token', 'name': '*', 'value': '*', 'src': 5, 'line': 1}), ({'type': 'token', 'name': 'ID', 'value': 'x', 'src': 6, 'line': 1})))",
    )

  def test_nolexersym(self):
    NoSym = ANTLR(
      r"""
      grammar NoSym ;

      start: expr * ;
      expr: 'a';
    """
    )
    tree = str(NoSym.tree('aa', 'start'))
    self.assertEqual(
      tree,
      r"({'type': 'rule', 'name': 'start', 'rule': 'start', 'src': (0, 1), 'line': 1}: ({'type': 'rule', 'name': 'expr', 'rule': 'expr', 'src': (0, 0), 'line': 1}: ({'type': 'token', 'name': 'a', 'value': 'a', 'src': 0, 'line': 1})), ({'type': 'rule', 'name': 'expr', 'rule': 'expr', 'src': (1, 1), 'line': 1}: ({'type': 'token', 'name': 'a', 'value': 'a', 'src': 1, 'line': 1})))",
    )

  def test_eof(self):
    NoSym = ANTLR(
      r"""
      grammar NoSym ;

      start: expr * EOF;
      expr: 'a';
    """
    )
    tree = str(NoSym.tree('aa', 'start'))
    self.assertEqual(
      tree,
      r"({'type': 'rule', 'name': 'start', 'rule': 'start', 'src': (0, 1), 'line': 1}: ({'type': 'rule', 'name': 'expr', 'rule': 'expr', 'src': (0, 0), 'line': 1}: ({'type': 'token', 'name': 'a', 'value': 'a', 'src': 0, 'line': 1})), ({'type': 'rule', 'name': 'expr', 'rule': 'expr', 'src': (1, 1), 'line': 1}: ({'type': 'token', 'name': 'a', 'value': 'a', 'src': 1, 'line': 1})))",
    )

  def test_diag(self):
    with unittest.mock.patch('liblet.antlr.warn') as mock_warn:
      Ambig = ANTLR(
        r"""
        grammar Ambig;
        stat: expr ';' | ID '(' ')' ';' ;
        expr: ID '(' ')' | INT ;
        INT :  [0-9]+ ;
        ID :  [a-zA-Z]+ ;
        WS :  [ \t\r\n]+ -> skip ;
        """
      )
      text = 'f();'
      Ambig.context(text, 'stat', diag=True)
      args, kwargs = mock_warn.call_args
    errs = "line 1:3 reportAttemptingFullContext d=0 (stat), input='f();'\nline 1:3 reportAmbiguity d=0 (stat): ambigAlts={1, 2}, input='f();'"
    self.assertEqual(args[0], errs)

  def test_trace(self):
    buf = StringIO()
    with redirect_stdout(buf):
      Ambig = ANTLR(
        r"""
        grammar Ambig;
        stat: expr ';' | ID '(' ')' ';' ;
        expr: ID '(' ')' | INT ;
        INT :  [0-9]+ ;
        ID :  [a-zA-Z]+ ;
        WS :  [ \t\r\n]+ -> skip ;
        """
      )
      text = 'f();'
      Ambig.context(text, 'stat', trace=True)
    trace = dedent(
      """
      enter   stat, LT(1)=f
      enter   expr, LT(1)=f
      consume [@0,0:0='f',<5>,1:0] rule expr
      consume [@1,1:1='(',<2>,1:1] rule expr
      consume [@2,2:2=')',<3>,1:2] rule expr
      exit    expr, LT(1)=;
      consume [@3,3:3=';',<1>,1:3] rule stat
      exit    stat, LT(1)=<EOF>
    """
    )[1:]  # remove first blank line
    self.assertEqual(buf.getvalue(), trace)

  def test_atw_tree_ca(self):
    at = Tree({'key': 'a'}, [Tree({'key': 'b'}), Tree({'key': 'c'})])
    w = AnnotatedTreeWalker('key')
    with unittest.mock.patch('liblet.antlr.warn') as mock_warn:
      res = w(at)
    self.assertEqual(str(res), "({'key': 'a'}: ({'key': 'b'}), ({'key': 'c'}))")

  def test_atw_text_ca(self):
    at = Tree({'key': 'a'}, [Tree({'key': 'b'}), Tree({'key': 'c'})])
    w = AnnotatedTreeWalker('key', AnnotatedTreeWalker.TEXT_CATCHALL)
    with unittest.mock.patch('liblet.antlr.warn') as mock_warn:
      res = w(at)
    self.assertEqual(res, "{'key': 'a'}\n\t{'key': 'b'}\n\t{'key': 'c'}")

  def test_atw_rc_ca(self):
    at = Tree({'key': 'a'}, [Tree({'key': 'b'}), Tree({'key': 'c'})])
    w = AnnotatedTreeWalker('key', AnnotatedTreeWalker.RECOURSE_CHILDREN)
    SEEN = False

    @w.register
    def c(visit, tree):
      nonlocal SEEN
      SEEN = True

    w(at)
    self.assertTrue(SEEN)

  def test_atw_user_ca(self):
    at = Tree({'key': 'a'}, [Tree({'key': 'b'}), Tree({'key': 'c'})])
    w = AnnotatedTreeWalker('key')

    @w.catchall
    def catchall(visit, tree):
      nonlocal SEEN
      SEEN = True

    SEEN = False
    w(at)
    self.assertTrue(SEEN)

  def test_atw_register(self):
    at = Tree({'key': 'a'}, [Tree({'key': 'b'}, [Tree({'key': 'x'})]), Tree({'key': 'c'})])
    w = AnnotatedTreeWalker('key')

    @w.register
    def a(visit, tree):
      return visit(tree.children[0])

    @w.register
    def x(visit, tree):
      return Tree('X')

    with unittest.mock.patch('liblet.antlr.warn') as mock_warn:
      res = w(at)
    self.assertEqual(str(res), "({'key': 'b'}: (X))")


if __name__ == '__main__':
  unittest.main()
