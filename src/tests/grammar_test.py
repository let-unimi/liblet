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

    def test_production_totalorder(self):
        self.assertTrue(Production('a', ('b', )) > Production('a', ('a', )))

    def test_grammar_eq(self):
        G0 = Grammar.from_string('S -> A B | B\nA -> a\nB -> b')
        G1 = Grammar.from_string('S -> B | A B\nB -> b\nA -> a')
        self.assertEqual(G0, G1)

    def test_grammar_hash(self):
        S = {
            Grammar.from_string('S -> A B | B\nA -> a\nB -> b'): 1,
            Grammar.from_string('S -> B | A B\nB -> b\nA -> a'): 2
        }
        self.assertEqual(1, len(S))

    def test_grammar_nondisjoint(self):
        with self.assertRaisesRegex(ValueError, "not disjoint.*\{'A'\}"):
            Grammar({'S', 'A'},{'A', 'a'}, (), 'S')

    def test_grammar_wrongstart(self):
        with self.assertRaisesRegex(ValueError, 'start symbol.*not a nonterminal'):
            Grammar({'T', 'A'},{'a'}, (), 'S')

    def test_grammar_cf(self):
        G = Grammar.from_string('S -> T U\nT -> t\nU -> u')
        self.assertTrue(G.context_free)

    def test_grammar_not_cf(self):
        G = Grammar.from_string('S -> T U\nT x -> t\nT U -> u', False)
        self.assertFalse(G.context_free)

    def test_grammar_wrong_cf(self):
        with self.assertRaisesRegex(ValueError, 'not a nonterminal.*\(T -> s,\)'):
            Grammar(
                {'S'}, {'s'}, (
                    Production('S', ('s', )),
                    Production('T', ('s', ))
                ), 'S'
            )

    def test_grammar_extrasymbol(self):
        with self.assertRaisesRegex(ValueError, 'neither terminals or nonterminals.*\(S -> s t,\)'):
            Grammar(
                {'S'}, {'s'}, (
                    Production('S', ('s', )),
                    Production(('S',), ('s', 't' ))
                ), 'S'
            )

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

    def test_all_terminals(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        self.assertTrue(G.all_terminals('babba'))

    def test_derivation_repr(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        d = Derivation(G)
        for prod, pos in [(0, 0), (1, 0), (2, 1)]: d = d.step(prod, pos)
        self.assertEqual('S -> A B -> a B -> a b', str(d))

    def test_derivation_sf(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        d = Derivation(G)
        for prod, pos in [(0, 0), (1, 0), (2, 1)]: d = d.step(prod, pos)
        self.assertEqual(('a', 'b'), d.sentential_form())

    def test_derivation_eq(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        d0 = Derivation(G)
        for prod, pos in [(0, 0), (1, 0), (2, 1)]: d0 = d0.step(prod, pos)
        d1 = Derivation(G)
        for prod, pos in [(0, 0), (1, 0), (2, 1)]: d1 = d1.step(prod, pos)
        self.assertEqual(d0, d1)
        
    def test_derivation_hash(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        d0 = Derivation(G)
        for prod, pos in [(0, 0), (1, 0), (2, 1)]: d0 = d0.step(prod, pos)
        d1 = Derivation(G)
        for prod, pos in [(0, 0), (1, 0), (2, 1)]: d1 = d1.step(prod, pos)
        S = {d0: 1, d1: 2}
        self.assertEqual(1, len(S))
        
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

    def test_derivation_possible_steps(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        expected = [(1, 0), (2, 1)]
        actual = list(Derivation(G).step(0,0).possible_steps())
        self.assertEqual(expected, actual)

    def test_derivation_possible_steps_prod(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        expected = [(1, 0)]
        actual = list(Derivation(G).step(0,0).possible_steps(prod = 1))
        self.assertEqual(expected, actual)

    def test_derivation_possible_steps_pos(self):
        G = Grammar.from_string("""
            S -> A B
            A -> a 
            B -> b
        """, False)
        expected = [(2, 1)]
        actual = list(Derivation(G).step(0,0).possible_steps(pos = 1))
        self.assertEqual(expected, actual)

if __name__ == '__main__': unittest.main()
