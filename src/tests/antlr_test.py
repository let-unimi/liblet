import unittest

from liblet import generate_and_load, parse_tree, to_let_tree


class TestGenerationAndParsing(unittest.TestCase):

    def test_to_let_tree(self):
        Bad = generate_and_load('Bad', r"""
            grammar Bad ;

            start: expr ;
            expr: ID| expr OP ID ;

            OP: '+' | '-' ;
            ID: [a-z];
        """)
        tree = parse_tree('z-a+a', 'start', Bad)
        T = to_let_tree(tree)
        self.assertEqual(str(T), '(start: (expr: (expr: (expr: (z)), (-), (a)), (+), (a)))')

    def test_to_let_tree_symbolic(self):
        Bad = generate_and_load('Bad', r"""
            grammar Bad ;

            start: expr ;
            expr: ID| expr OP ID ;

            OP: '+' | '-' ;
            ID: [a-z];
        """)
        tree = parse_tree('z-a+a', 'start', Bad)
        T = to_let_tree(tree, True)
        self.assertEqual(str(T), '(start: (expr: (expr: (expr: (ID [z])), (OP [-]), (ID [a])), (OP [+]), (ID [a])))')

    def test_alltogether(self):
        Expr = generate_and_load('Expr', r"""
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
        tree = parse_tree(expr, 'prog', Expr)
        actual = tree.toStringTree(recog = Expr.Parser)
        expected = r'(prog (stat (expr (expr 1) + (expr (expr 2) * (expr 3))) \n) (stat A = (expr 3) \n) (stat (expr (expr 2) * (expr A)) \n))'
        self.assertEqual(actual, expected)
