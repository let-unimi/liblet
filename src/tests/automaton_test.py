import unittest
from copy import copy

from liblet import (
  Automaton,
  BottomUpInstantaneousDescription,
  Grammar,
  InstantaneousDescription,
  Item,
  Production,
  TopDownInstantaneousDescription,
  Transition,
)


#
class TestAutomaton(unittest.TestCase):
  def test_transition_unpack(self):
    frm, lbl, to = Transition('a', 'b', 'c')
    self.assertEqual(('a', 'b', 'c'), (frm, lbl, to))

  def test_transition_totalorder(self):
    self.assertTrue(Transition('a', 'b', 'c') > Transition('a', 'b', 'b'))

  def test_transition_eqo(self):
    self.assertFalse(Transition('a', 'b', 'c') == object())

  def test_transition_lto(self):
    self.assertIs(Transition('a', 'b', 'c').__lt__(object()), NotImplemented)

  def test_transition_hash(self):
    S = {Transition('a', 'b', 'c'): 1, Transition('a', 'b', 'c'): 2}
    self.assertEqual(1, len(S))

  def test_transition_str(self):
    self.assertEqual('frm-label->to', str(Transition('frm', 'label', 'to')))

  def test_transition_set(self):
    self.assertEqual('{frm}-label->{to}', str(Transition({'frm'}, 'label', {'to'})))

  def test_transition_setofitems(self):
    self.assertEqual('{A -> •B}-label->{C -> •D}', str(Transition({Item('A', ('B',))}, 'label', {Item('C', ('D',))})))

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
    A = Automaton.from_grammar(
      Grammar.from_string(
        """
      S -> a A
      S -> a B
      A -> b B
      A -> b C
      B -> c A
      B -> c C
      C -> a
    """
      )
    )
    s = 'Automaton(N={A, B, C, S, ◇}, T={a, b, c}, transitions=(S-a->A, S-a->B, A-b->B, A-b->C, B-c->A, B-c->C, C-a->◇), F={◇}, q0=S)'
    self.assertEqual(s, str(A))

  def test_automaton_δ(self):
    # fig 5.6, pag 142
    states = Automaton.from_grammar(
      Grammar.from_string(
        """
      S -> a A
      S -> a B
      A -> b B
      A -> b C
      B -> c A
      B -> c C
      C -> a
    """
      )
    ).δ('S', 'a')
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
    A = Automaton.from_grammar(
      Grammar.from_string(
        """
      S -> A
      S -> a B
      A -> a A
      A -> ε
      B -> b B
      B -> b
    """
      )
    )
    s = 'Automaton(N={A, B, S, ◇}, T={a, b}, transitions=(S-ε->A, S-a->B, A-a->A, A-ε->◇, B-b->B, B-b->◇), F={◇}, q0=S)'
    self.assertEqual(s, str(A))

  def test_automaton_from_string(self):
    # HMU, fig 4.8, pag 147
    A = Automaton.from_string(
      """
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
      """,
      {'C'},
    )
    s = 'Automaton(N={A, B, C, D, E, F, G, H}, T={0, 1}, transitions=(A-0->B, A-1->F, B-0->G, B-1->C, C-1->C, D-0->C, D-1->G, E-0->H, E-1->F, F-0->C, F-1->G, G-0->G, H-0->G, H-1->C), F={C}, q0=A)'
    self.assertEqual(s, str(A))

  def test_automaton_overlapTN(self):
    with self.assertRaisesRegex(ValueError, 'but have {B} in common'):
      Automaton({'A', 'B'}, {'B', 'C'}, (), set(), 'A')

  def test_automaton_q0N(self):
    with self.assertRaisesRegex(ValueError, r'\(X\) is not a state'):
      Automaton({'A', 'B'}, {'b', 'c'}, (), 'X', set())

  def test_automaton_FN(self):
    with self.assertRaisesRegex(ValueError, r'states {C} in F are not states'):
      Automaton({'A', 'B'}, {'b', 'c'}, (), 'A', {'B', 'C'})

  def test_ID_done(self):
    self.assertFalse(InstantaneousDescription(Grammar.from_string('S -> s')).is_done())

  def test_TDID_copy(self):
    i = TopDownInstantaneousDescription(Grammar.from_string('S -> s'))
    c = copy(i)
    i.stack.push(1)
    c.stack.push(2)
    self.assertEqual(i.stack.pop(), 1)

  def test_BUID_copy(self):
    i = BottomUpInstantaneousDescription(Grammar.from_string('S -> s'))
    c = copy(i)
    i.stack.push(1)
    c.stack.push(2)
    self.assertEqual(i.stack.pop(), 1)

  def test_TDID_init(self):
    G = Grammar.from_string(
      """
      S -> a B C
      B -> a B | b
      C -> a
    """
    )
    i = TopDownInstantaneousDescription(G, 'aaba')
    self.assertEqual('(), S♯, ｜aaba♯', str(i))

  def test_BUID_init(self):
    G = Grammar.from_string(
      """
      S -> A C
      A -> a b
      C -> c
    """
    )
    i = BottomUpInstantaneousDescription(G, 'abc')
    self.assertEqual('(), , ｜abc', str(i))

  def test_TDID_init_exception(self):
    G = Grammar.from_string('S -> ♯')
    with self.assertRaisesRegex(ValueError, r'.*♯.*belong to terminal'):
      TopDownInstantaneousDescription(G, 'aaba')

  def test_TDID_predict(self):
    G = Grammar.from_string(
      """
      S -> a B C
      B -> a B | b
      C -> a
    """
    )
    i = TopDownInstantaneousDescription(G, 'aaba')
    i = i.predict(G.P[0])
    self.assertEqual('(S -> a\u200aB\u200aC,), aBC♯, ｜aaba♯', str(i))

  def test_TDID_predict_exception0(self):
    G = Grammar.from_string(
      """
      S -> a B C
      B -> a B | b
      C -> a
    """
    )
    i = TopDownInstantaneousDescription(G, 'aaba')
    with self.assertRaisesRegex(ValueError, r'.*top of the stack.*production'):
      i = i.predict(Production('X', ('Y',)))

  def test_TDID_predict_exception1(self):
    G = Grammar.from_string(
      """
      S -> a B C
      B -> a B | b
      C -> a
    """
    )
    i = TopDownInstantaneousDescription(G, 'aaba')
    with self.assertRaisesRegex(ValueError, r'.*top of the stack.*production'):
      i = i.predict(G.P[1])

  def test_BUID_reduce(self):
    G = Grammar.from_string(
      """
      S -> A C
      A -> a b
      C -> c
    """
    )
    i = BottomUpInstantaneousDescription(G, 'abc')
    i = i.shift().shift().reduce(G.P[1])
    self.assertEqual('(A -> a\u200ab,), (A: (a), (b)), ab｜c', str(i))

  def test_BUID_reduce_exception0(self):
    G = Grammar.from_string(
      """
      S -> A C
      A -> a b
      C -> c
    """
    )
    i = BottomUpInstantaneousDescription(G, 'abc')
    with self.assertRaisesRegex(ValueError, r'rhs does not correspond to the symbols on the stack'):
      i.shift().shift().reduce(G.P[0])

  def test_BUID_reduce_exception1(self):
    G = Grammar.from_string(
      """
      S -> A C
      A -> a b
      C -> c
    """
    )
    i = BottomUpInstantaneousDescription(G, 'abc')
    with self.assertRaisesRegex(ValueError, r'production does not belong to the grammar'):
      i.reduce(Production('X', ('y',)))

  def test_TDID_match(self):
    G = Grammar.from_string(
      """
      S -> a B C
      B -> a B | b
      C -> a
    """
    )
    i = TopDownInstantaneousDescription(G, 'aaba')
    i = i.predict(G.P[0]).match()
    self.assertEqual('(S -> a\u200aB\u200aC,), BC♯, a｜aba♯', str(i))

  def test_TDID_match_exception(self):
    G = Grammar.from_string(
      """
      S -> a B C
      B -> a B | b
      C -> a
    """
    )
    i = TopDownInstantaneousDescription(G, 'aaba')
    with self.assertRaisesRegex(ValueError, r'.*top of the stack.*head symbol'):
      i = i.match()

  def test_BUID_shift(self):
    G = Grammar.from_string(
      """
      S -> A C
      A -> a b
      C -> c
    """
    )
    i = BottomUpInstantaneousDescription(G, 'abc')
    i = i.shift()
    self.assertEqual('(), (a), a｜bc', str(i))

  def test_TDID_done(self):
    G = Grammar.from_string(
      """
      S -> a B C
      B -> a B | b
      C -> a
    """
    )
    i = TopDownInstantaneousDescription(G, 'aaba')
    i = i.predict(G.P[0]).match().predict(G.P[1]).match().predict(G.P[2]).match().predict(G.P[3]).match()
    self.assertTrue(i.is_done())

  def test_BUID_done(self):
    G = Grammar.from_string(
      """
      S -> A C
      A -> a b
      C -> c
    """
    )
    i = BottomUpInstantaneousDescription(G, 'abc')
    i = i.shift().shift().reduce(G.P[1]).shift().reduce(G.P[2]).reduce(G.P[0])
    self.assertTrue(i.is_done())


if __name__ == '__main__':
  unittest.main()
