from contextlib import redirect_stdout
from io import StringIO
from textwrap import dedent
import unittest
import unittest.mock

from liblet import ANTLR


class TestGenerationAndParsing(unittest.TestCase):

    def test_noname(self):
        with self.assertRaisesRegex(ValueError, 'name not found'):
            ANTLR("a: 'rule'")

    def test_invalid_grammar(self):
        with unittest.mock.patch('liblet.antlr.warn') as mock_warn:
            ANTLR("grammar A; a: rule;")
            args, kwargs = mock_warn.call_args
        self.assertTrue('reference to undefined rule' in args[0])

    def test_tokens(self): 
        Tk = ANTLR(r"""
            grammar Tk ;
            start: ID+ ;
            ID: [a-z]+;
            WS : [ \t]+ -> skip ;
        """)
        tks = ' '.join(list(map(str,Tk.tokens('tic gulp boom'))))
        self.assertEqual(tks, "[@0,0:2='tic',<1>,1:0] [@1,4:7='gulp',<1>,1:4] [@2,9:12='boom',<1>,1:9] [@3,13:12='<EOF>',<-1>,1:13]")

    def test_tree_str(self):
        Bad = ANTLR(r"""
            grammar Bad ;

            start: expr ;
            expr: ID | expr OP ID | expr '*' ID;

            OP: '+' | '-' ;
            ID: [a-z];
        """)
        tree = Bad.context('z-a+a*x', 'start', as_string = True,)
        self.assertEqual(tree, "(start (expr (expr (expr (expr z) - a) + a) * x))")

    def test_tree_simple(self):
        Bad = ANTLR(r"""
            grammar Bad ;

            start: expr ;
            expr: ID | expr OP ID | expr '*' ID;

            OP: '+' | '-' ;
            ID: [a-z];
        """)
        tree = str(Bad.tree('z-a+a*x', 'start', simple = True))
        self.assertEqual(tree, "(start: (expr: (expr: (expr: (expr: (z)), (-), (a)), (+), (a)), (*), (x)))")

    def test_tree(self):
        Bad = ANTLR(r"""
            grammar Bad ;

            start: expr ;
            expr: ID | expr OP ID | expr '*' ID;

            OP: '+' | '-' ;
            ID: [a-z];
        """)
        tree = str(Bad.tree('z-a+a*x', 'start'))
        self.assertEqual(tree, r"({'type': 'rule', 'name': 'start', 'label': 'start'}: ({'type': 'rule', 'name': 'expr', 'label': 'expr'}: ({'type': 'rule', 'name': 'expr', 'label': 'expr'}: ({'type': 'rule', 'name': 'expr', 'label': 'expr'}: ({'type': 'rule', 'name': 'expr', 'label': 'expr'}: ({'type': 'token', 'name': 'ID', 'value': 'z'})), ({'type': 'token', 'name': 'OP', 'value': '-'}), ({'type': 'token', 'name': 'ID', 'value': 'a'})), ({'type': 'token', 'name': 'OP', 'value': '+'}), ({'type': 'token', 'name': 'ID', 'value': 'a'})), ({'type': 'token', 'name': '*'}), ({'type': 'token', 'name': 'ID', 'value': 'x'})))")

    def test_diag(self):
        with unittest.mock.patch('liblet.antlr.warn') as mock_warn:
            Ambig = ANTLR(r"""
                grammar Ambig;
                stat: expr ';' | ID '(' ')' ';' ;
                expr: ID '(' ')' | INT ;
                INT :   [0-9]+ ;
                ID  :   [a-zA-Z]+ ;
                WS  :   [ \t\r\n]+ -> skip ;
                """)
            text = 'f();'
            Ambig.context(text, 'stat', diag = True)
            args, kwargs = mock_warn.call_args
        errs = "line 1:3 reportAttemptingFullContext d=0 (stat), input='f();'\nline 1:3 reportAmbiguity d=0 (stat): ambigAlts={1, 2}, input='f();'"
        self.assertEqual(args[0], errs)

    def test_trace(self):
        buf = StringIO()
        with redirect_stdout(buf):
            Ambig = ANTLR(r"""
                grammar Ambig;
                stat: expr ';' | ID '(' ')' ';' ;
                expr: ID '(' ')' | INT ;
                INT :   [0-9]+ ;
                ID  :   [a-zA-Z]+ ;
                WS  :   [ \t\r\n]+ -> skip ;
                """)
            text = 'f();'
            Ambig.context(text, 'stat', trace = True)
        trace = dedent("""
            enter   stat, LT(1)=f
            enter   expr, LT(1)=f
            consume [@0,0:0='f',<5>,1:0] rule expr
            consume [@1,1:1='(',<2>,1:1] rule expr
            consume [@2,2:2=')',<3>,1:2] rule expr
            exit    expr, LT(1)=;
            consume [@3,3:3=';',<1>,1:3] rule stat
            exit    stat, LT(1)=<EOF>
        """)[1:] # remove first blank line
        self.assertEqual(buf.getvalue(), trace)

if __name__ == '__main__': unittest.main()