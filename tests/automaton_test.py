import unittest

from liblet import Automaton, Grammar


class TestAutomaton(unittest.TestCase):

    def test_automaton_from_grammar(self):
        # fig 5.6, pag 142
        A = Automaton.from_grammar(Grammar.from_string("""
            S -> a A
            S -> a B
            A -> b B
            A -> b C
            B -> c A
            B -> c C
            C -> a
        """))
        s = 'Automaton(N={A, B, C, S, ◇}, T={a, b, c}, transitions=(S-a->A, S-a->B, A-b->B, A-b->C, B-c->A, B-c->C, C-a->◇), F={◇}, q0=S)'
        self.assertEqual(s, str(A))

    def test_automaton_from_ε_grammar(self):
        # fig 5.14 pag 147
        A = Automaton.from_grammar(Grammar.from_string("""
            S -> A
            S -> a B
            A -> a A
            A -> ε
            B -> b B
            B -> b
        """))
        s = "Automaton(N={A, B, S, ◇}, T={a, b}, transitions=(S-ε->A, S-a->B, A-a->A, A-ε->◇, B-b->B, B-b->◇), F={◇}, q0=S)"
        self.assertEqual(s, str(A))

    def test_automaton_from_string(self):
        # HMU, fig 4.8, pag 147
        A = Automaton.from_string("""
                A, 0, B
                A, 1, F
                B, 0, G
                B, 1, C
                C, 1, C
                D, 0, C
                D, 1, G
                E, 0, H
                E, 1, F
                F, 0, C
                F, 1, G
                G, 0, G
                H, 0, G
                H, 1, C
            """, {'C'})
        s = 'Automaton(N={A, B, C, D, E, F, G, H}, T={0, 1}, transitions=(A-0->B, A-1->F, B-0->G, B-1->C, C-1->C, D-0->C, D-1->G, E-0->H, E-1->F, F-0->C, F-1->G, G-0->G, H-0->G, H-1->C), F={C}, q0=A)'
        self.assertEqual(s, str(A))

if __name__ == '__main__': unittest.main()
