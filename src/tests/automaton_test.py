import unittest

from liblet import Automaton, Transition, Grammar


class TestAutomaton(unittest.TestCase):

    def test_transition_unpack(self):
        f, l, t = Transition('a', 'b', 'c')
        self.assertEqual(('a', 'b', 'c'), (f, l, t))

    def test_transition_totalorder(self):
        self.assertTrue(Transition('a', 'b', 'c') > Transition('a', 'b', 'b'))

    def test_transition_eqo(self):
        self.assertFalse(Transition('a', 'b', 'c') == object())

    def test_transition_lto(self):
        self.assertIs(Transition('a', 'b', 'c').__lt__(object()), NotImplemented)

    def test_transition_hash(self):
        S = {
            Transition('a', 'b', 'c'): 1,
            Transition('a', 'b', 'c'): 2
        }
        self.assertEqual(1, len(S))

    def test_transition_str(self):
        self.assertEqual('frm-label->to', str(Transition('frm', 'label', 'to')))

    def test_transition_lt(self):
        self.assertEqual('frm-label->to', str(Transition('frm', 'label', 'to')))

    def test_transition_set(self):
        self.assertEqual('{frm}-label->{to}', str(Transition({'frm'}, 'label', {'to'})))

    def test_transition_wrong_label1(self):
        with self.assertRaisesRegex(ValueError, 'The label is not'):
            Transition('frm', 1, 'to')

    def test_transition_wrong_label2(self):
        with self.assertRaisesRegex(ValueError, 'The label is not'):
            Transition('frm', '', 'to')

    def test_transition_wrong_from1(self):
        with self.assertRaisesRegex(ValueError, 'The frm state is not'):
            Transition(1, 'label', 'to')

    def test_transition_wrong_from2(self):
        with self.assertRaisesRegex(ValueError, 'The frm state is not'):
            Transition('', 'label', 'to')

    def test_transition_wrong_from3(self):
        with self.assertRaisesRegex(ValueError, 'The frm state is not'):
            Transition(set(), 'label', 'to')

    def test_transition_wrong_from4(self):
        with self.assertRaisesRegex(ValueError, 'The frm state is not'):
            Transition({''}, 'label', 'to')

    def test_transition_wrong_to1(self):
        with self.assertRaisesRegex(ValueError, 'The to state is not'):
            Transition('frm', 'label', 1)

    def test_transition_wrong_to2(self):
        with self.assertRaisesRegex(ValueError, 'The to state is not'):
            Transition('frm', 'label', '')

    def test_transition_wrong_to3(self):
        with self.assertRaisesRegex(ValueError, 'The to state is not'):
            Transition('frm', 'label', set())

    def test_transition_wrong_to4(self):
        with self.assertRaisesRegex(ValueError, 'The to state is not'):
            Transition('frm', 'label', {''})

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

    def test_automaton_δ(self):
        # fig 5.6, pag 142
        states = Automaton.from_grammar(Grammar.from_string("""
            S -> a A
            S -> a B
            A -> b B
            A -> b C
            B -> c A
            B -> c C
            C -> a
        """)).δ('S', 'a')
        self.assertEqual({'A', 'B'}, states)

    def test_automaton_from_grammar_fail3(self):
        with self.assertRaisesRegex(ValueError, 'has more than two symbols'):
            Automaton.from_grammar(Grammar.from_string('S -> a b c'))

    def test_automaton_from_grammar_fail2a(self):
        with self.assertRaisesRegex(ValueError, 'not of the aB form'):
            Automaton.from_grammar(Grammar.from_string('S -> a b'))

    def test_automaton_from_grammar_fail2b(self):
        with self.assertRaisesRegex(ValueError, 'not of the aB form'):
            Automaton.from_grammar(Grammar.from_string('S -> B B'))

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

    def test_automaton_overlapTN(self):
        with self.assertRaisesRegex(ValueError, "but have {B} in common"):
            Automaton({'A', 'B'}, {'B', 'C'}, tuple(), set(), 'A')

    def test_automaton_q0N(self):
        with self.assertRaisesRegex(ValueError, r'\(X\) is not a state'):
            Automaton({'A', 'B'}, {'b', 'c'}, tuple(), 'X', set())

    def test_automaton_FN(self):
        with self.assertRaisesRegex(ValueError, r'states {C} in F are not states'):
            Automaton({'A', 'B'}, {'b', 'c'}, tuple(), 'A', {'B', 'C'})

if __name__ == '__main__': unittest.main()
