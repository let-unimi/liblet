import unittest

from liblet import Production, Grammar, Derivation


class TestGrammar(unittest.TestCase):

    def test_production_wrong_lhs(self):
        with self.assertRaises(ValueError):
            Production(1,['a'])
 
    def test_production_wrong_rhs(self):
        with self.assertRaises(ValueError):
            Production('a',[1])
 
    def test_production_inset(self):
        P = Production('a',['b','c'])
        Q = Production('a',('b','c'))
        s = set()
        s.add(P)
        s.add(Q)
        self.assertEqual(len(s), 1)

    def test_production_unpack(self):
        lhs, rhs = Production('a',['b'])
        self.assertEqual(('a', ('b',)), (lhs, rhs))

    def test_grammar_from_to_string(self):
        G = Grammar.from_string("""
            Z -> E $
            E -> T | E + T
            T -> i | ( E )
        """)
        s = "Grammar(N={E, T, Z}, T={$, (, ), +, i}, P=(Z -> E $, E -> T, E -> E + T, T -> i, T -> ( E )), S=Z)"
        self.assertEqual(s, str(G))

    def test_rhs(self):
        actual = set(Grammar.from_string("""
            Z -> E $
            E -> T | E + T
            T -> i | ( E )
        """).rhs('E'))
        expected = set([('T',), ('E', '+', 'T')])
        self.assertEqual(expected, actual)

    def test_all_terminal(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        self.assertTrue(G.all_terminal('babba'))

    def test_derivation_repr(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        d = Derivation(G)
        for prod, pos in [(0, 0), (1, 0), (2, 1)]: d = d.step(prod, pos)
        self.assertEqual('S -> A B -> a B -> a b', str(d))

    def test_derivation_steps(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        d = Derivation(G)
        steps = ((0, 0), (1, 0), (2, 1))
        for prod, pos in steps: d = d.step(prod, pos)
        self.assertEqual(steps, d.steps())

    def test_derivation_leftmost(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        d = Derivation(G).leftmost(0).leftmost(1).leftmost(2)
        steps = ((0, 0), (1, 0), (2, 1))
        self.assertEqual(steps, d.steps())

    def test_derivation_rightmost(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        d = Derivation(G).rightmost(0).rightmost(2).rightmost(1)
        steps = ((0, 0), (2, 1), (1, 0))
        self.assertEqual(steps, d.steps())

    def test_derivation_matches(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        expected = [(1, 0), (2, 1)]
        actual = list(Derivation(G).step(0,0).matches())
        self.assertEqual(expected, actual)

    def test_derivation_matches_prod(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        expected = [(1, 0)]
        actual = list(Derivation(G).step(0,0).matches(prod = 1))
        self.assertEqual(expected, actual)

    def test_derivation_matches_pos(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        expected = [(2, 1)]
        actual = list(Derivation(G).step(0,0).matches(pos = 1))
        self.assertEqual(expected, actual)

if __name__ == '__main__': unittest.main()
