import unittest

from liblet import ANTLR


class TestGenerationAndParsing(unittest.TestCase):

    def test_to_let_tree(self):
        Bad = ANTLR(r"""
            grammar Bad ;

            start: expr ;
            expr: ID| expr OP ID ;

            OP: '+' | '-' ;
            ID: [a-z];
        """)
        tree = Bad.tree('z-a+a', 'start')
        lol = Bad.as_lol(tree)
        self.assertEqual(lol, ['start', ['expr', ['expr', ['expr', ['z']], ['-'], ['a']], ['+'], ['a']]])

    def test_to_let_tree_symbolic(self):
        Bad = ANTLR(r"""
            grammar Bad ;

            start: expr ;
            expr: ID| expr OP ID ;

            OP: '+' | '-' ;
            ID: [a-z];
        """)
        tree = Bad.tree('z-a+a', 'start')
        lol = Bad.as_lol(tree, True)
        self.assertEqual(lol, ['start', ['expr', ['expr', ['expr', ['ID [z]']], ['OP [-]'], ['ID [a]']], ['OP [+]'], ['ID [a]'] ]])

    def test_alltogether(self):
        Expr = ANTLR(r"""
            grammar Expr;

            prog: stat+ ;

            stat: expr NEWLINE        # print
                | ID '=' expr NEWLINE # assign
                | NEWLINE             # empty
                ;

            expr: left=expr op=('*'|'/') right=expr # muldiv
                | left=expr op=('+'|'-') right=expr # sumsub
                | INT                               # int
                | ID                                # id
                | '(' expr ')'                      # paren
                ;

            ID : [a-zA-Z]+ ;
            INT : [0-9]+ ;
            NEWLINE :'\r'? '\n' ;
            WS : [ \t]+ -> skip ;
        """)
        expr = '1 + 2 * 3\nA = 3\n2 * A\n'
        tree = Expr.tree(expr, 'prog')
        actual = Expr.as_str(tree)
        expected = r'(prog (stat (expr (expr 1) + (expr (expr 2) * (expr 3))) \n) (stat A = (expr 3) \n) (stat (expr (expr 2) * (expr A)) \n))'
        self.assertEqual(actual, expected)
