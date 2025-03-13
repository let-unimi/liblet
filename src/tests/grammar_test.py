import unittest

from liblet import Derivation, Grammar, Item, Production, Productions, ε


class TestGrammar(unittest.TestCase):
  def test_production_wrong_lhs(self):
    with self.assertRaises(ValueError):
      Production(1, ['a'])

  def test_production_nonempty_lhs(self):
    with self.assertRaisesRegex(ValueError, 'nonempty'):
      Production('', ['a'])

  def test_production_wrong_rhs(self):
    with self.assertRaises(ValueError):
      Production('a', [1])

  def test_production_nonemptystr_rhs(self):
    with self.assertRaisesRegex(ValueError, 'nonempty'):
      Production('a', ['a', '', 'c'])

  def test_production_empty_rhs(self):
    P = Production('a', [])
    self.assertEqual(P.rhs, (ε,))

  def test_production_inset(self):
    P = Production('a', ['b', 'c'])
    Q = Production('a', ('b', 'c'))
    s = set()
    s.add(P)
    s.add(Q)
    self.assertEqual(len(s), 1)

  def test_production_aε(self):
    with self.assertRaisesRegex(ValueError, 'contains ε but has more than one symbol'):
      Production('A', ('a', ε))

  def test_production_unpack(self):
    lhs, rhs = Production('a', ['b'])
    self.assertEqual(('a', ('b',)), (lhs, rhs))

  def test_production_totalorder(self):
    self.assertTrue(Production('a', ('b',)) > Production('a', ('a',)))

  def test_production_eqo(self):
    self.assertFalse(Production('a', ('b',)) == object())

  def test_production_lto(self):
    self.assertIs(Production('a', ('b',)).__lt__(object()), NotImplemented)

  def test_production_from_string_cf(self):
    with self.assertRaisesRegex(ValueError, 'forbidden in a context-free'):
      Productions.from_string('A B -> c', True)

  def test_production_such_that_lhs(self):
    self.assertTrue(Production.such_that(lhs='X')(Production('X', ('x',))))

  def test_production_such_that_rhs(self):
    self.assertTrue(Production.such_that(rhs='x')(Production('X', ('x',))))

  def test_production_such_that_rhs_len(self):
    self.assertTrue(Production.such_that(rhs_len=2)(Production('X', ('x', 'y'))))

  def test_production_such_that_rhs_is_suffix_of(self):
    self.assertTrue(Production.such_that(rhs_is_suffix_of=('a', 'x'))(Production('X', ('x',))))

  def test_item_wrong_lhs(self):
    with self.assertRaises(ValueError):
      Item(1, ['a'])

  def test_item_neg_pos(self):
    with self.assertRaises(ValueError):
      Item('A', ('B',), -1)

  def test_item_wrong_pos(self):
    with self.assertRaises(ValueError):
      Item('A', ('B',), 2)

  def test_item_inset(self):
    P = Item('a', ['b', 'c'])
    Q = Item('a', ('b', 'c'))
    s = set()
    s.add(P)
    s.add(Q)
    self.assertEqual(len(s), 1)

  def test_item_totalorder(self):
    self.assertTrue(Item('a', ('b', 'c'), 2) > Item('a', ('b', 'c'), 1))

  def test_item_eqo(self):
    self.assertFalse(Item('a', ('b',)) == object())

  def test_item_lto(self):
    self.assertIs(Item('a', ('b',)).__lt__(object()), NotImplemented)

  def test_item_unpack(self):
    lhs, rhs, pos = Item('a', ['b', 'c'], 1)
    self.assertEqual(('a', ('b', 'c'), 1), (lhs, rhs, pos))

  def test_item_advance(self):
    self.assertEqual(Item('A', ('x', 'B'), 1), Item('A', ('x', 'B')).advance('x'))

  def test_item_notadvance(self):
    self.assertIsNone(Item('A', ('B', 'C')).advance('x'))

  def test_item_symbol_after_dot(self):
    self.assertEqual('B', Item('A', ('x', 'B'), 1).symbol_after_dot())

  def test_item_nosymbol_after_dot(self):
    self.assertIsNone(Item('A', ('B', 'C'), 2).symbol_after_dot())

  def test_grammar_eq(self):
    G0 = Grammar.from_string('S -> A B | B\nA -> a\nB -> b')
    G1 = Grammar.from_string('S -> B | A B\nB -> b\nA -> a')
    self.assertEqual(G0, G1)

  def test_grammar_eqo(self):
    G = Grammar.from_string('S -> A B | B\nA -> a\nB -> b')
    self.assertFalse(object() == G)

  def test_grammar_lto(self):
    self.assertIs(Grammar.from_string('S -> s').__lt__(object()), NotImplemented)

  def test_grammar_hash(self):
    S = {
      Grammar.from_string('S -> A B | B\nA -> a\nB -> b'): 1,
      Grammar.from_string('S -> B | A B\nB -> b\nA -> a'): 2,
    }
    self.assertEqual(1, len(S))

  def test_grammar_nondisjoint(self):
    with self.assertRaisesRegex(ValueError, r"not disjoint.*\{'A'\}"):
      Grammar({'S', 'A'}, {'A', 'a'}, (), 'S')

  def test_grammar_wrongstart(self):
    with self.assertRaisesRegex(ValueError, 'start symbol.*not a nonterminal'):
      Grammar({'T', 'A'}, {'a'}, (), 'S')

  def test_grammar_cf(self):
    G = Grammar.from_string('S -> T U\nT -> t\nU -> u')
    self.assertTrue(G.is_context_free)

  def test_grammar_not_cf(self):
    G = Grammar.from_string('S -> T U\nT x -> t\nT U -> u', False)
    self.assertFalse(G.is_context_free)

  def test_grammar_wrong_cf(self):
    with self.assertRaisesRegex(ValueError, r'not a nonterminal.*\(T -> s,\)'):
      Grammar({'S'}, {'s'}, (Production('S', ('s',)), Production('T', ('s',))), 'S')

  def test_grammar_extrasymbol(self):
    with self.assertRaisesRegex(ValueError, r'neither terminals or nonterminals.*\(S -> s t,\)'):
      Grammar({'S'}, {'s'}, (Production('S', ('s',)), Production(('S',), ('s', 't'))), 'S')

  def test_grammar_from_to_string(self):
    G = Grammar.from_string(
      """
      Z -> E $
      E -> T | E + T
      T -> i | ( E )
    """
    )
    s = 'Grammar(N={E, T, Z}, T={$, (, ), +, i}, P=(Z -> E $, E -> T, E -> E + T, T -> i, T -> ( E )), S=Z)'
    self.assertEqual(s, str(G))

  def test_grammar_restrict_to(self):
    G = Grammar.from_string(
      """
      Z -> E $
      E -> T | E + T | X
      X -> x
      T -> i | ( E )
    """
    )
    Gr = Grammar.from_string(
      """
      Z -> E $
      E -> T | E + T
      T -> i | ( E )
    """
    )
    self.assertEqual(G.restrict_to((G.T | G.N) - {'X', 'x'}), Gr)

  def test_grammar_restrict_to_no_start(self):
    G = Grammar.from_string(
      """
      Z -> E $
      E -> T | E + T | X
      X -> x
      T -> i | ( E )
    """
    )
    with self.assertRaisesRegex(ValueError, 'start symbol'):
      G.restrict_to((G.T | G.N) - {'Z'})

  def test_alternatives(self):
    actual = set(
      Grammar.from_string(
        """
      Z -> E $
      E -> T | E + T
      T -> i | ( E )
    """
      ).alternatives('E')
    )
    expected = {('T',), ('E', '+', 'T')}
    self.assertEqual(expected, actual)

  def test_derivation_repr(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    d = Derivation(G)
    for prod, pos in [(0, 0), (1, 0), (2, 1)]:
      d = d.step(prod, pos)
    self.assertEqual('S -> A B -> a B -> a b', str(d))

  def test_derivation_sf(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    d = Derivation(G)
    for prod, pos in [(0, 0), (1, 0), (2, 1)]:
      d = d.step(prod, pos)
    self.assertEqual(('a', 'b'), d.sentential_form())

  def test_derivation_eqo(self):
    self.assertFalse(Derivation(Grammar.from_string('S -> s')) == object())

  def test_derivation_eq(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    d0 = Derivation(G)
    for prod, pos in [(0, 0), (1, 0), (2, 1)]:
      d0 = d0.step(prod, pos)
    d1 = Derivation(G)
    for prod, pos in [(0, 0), (1, 0), (2, 1)]:
      d1 = d1.step(prod, pos)
    self.assertEqual(d0, d1)

  def test_derivation_hash(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    d0 = Derivation(G)
    for prod, pos in [(0, 0), (1, 0), (2, 1)]:
      d0 = d0.step(prod, pos)
    d1 = Derivation(G)
    for prod, pos in [(0, 0), (1, 0), (2, 1)]:
      d1 = d1.step(prod, pos)
    S = {d0: 1, d1: 2}
    self.assertEqual(1, len(S))

  def test_derivation_steps(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    d = Derivation(G)
    steps = ((0, 0), (1, 0), (2, 1))
    for prod, pos in steps:
      d = d.step(prod, pos)
    self.assertEqual(steps, d.steps())

  def test_derivation_byprods(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """
    )
    d = Derivation(G)
    p = Production('S', ('A', 'B')), Production('A', ('a',))
    self.assertEqual(d.leftmost(p).sentential_form(), ('a', 'B'))

  def test_derivation_byprod(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """
    )
    d = Derivation(G)
    p = Production('S', ('A', 'B'))
    self.assertEqual(d.leftmost(p).sentential_form(), ('A', 'B'))

  def test_derivation_steps_list(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    steps = ((0, 0), (1, 0), (2, 1))
    d = Derivation(G).step(steps)
    self.assertEqual(steps, d.steps())

  def test_derivation_wrong_step(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    d = Derivation(G)
    steps = ((0, 0), (1, 1))
    with self.assertRaisesRegex(ValueError, 'at position'):
      for prod, pos in steps:
        d = d.step(prod, pos)

  def test_derivation_leftmost(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """
    )
    d = Derivation(G).leftmost(0).leftmost(1).leftmost(2)
    steps = ((0, 0), (1, 0), (2, 1))
    self.assertEqual(steps, d.steps())

  def test_derivation_leftmost_list(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """
    )
    d = Derivation(G).leftmost([0, 1, 2])
    steps = ((0, 0), (1, 0), (2, 1))
    self.assertEqual(steps, d.steps())

  def test_derivation_leftmost_ncf(self):
    with self.assertRaisesRegex(ValueError, 'derivation on a non context-free grammar'):
      Derivation(Grammar.from_string('S -> s\nT U ->s', False)).leftmost(0)

  def test_derivation_leftmost_allterminals(self):
    G = Grammar.from_string(
      """
    E -> M | A | n
    M -> E * E
    A -> E + E
    """
    )
    d = Derivation(G).leftmost(1).leftmost(4).leftmost(0).leftmost(3).leftmost(2).leftmost(2).leftmost(2)
    with self.assertRaisesRegex(ValueError, 'there are no nonterminals'):
      d.leftmost(2)

  def test_derivation_leftmost_wrongsymbol(self):
    G = Grammar.from_string(
      """
    E -> M | A | n
    M -> E * E
    A -> E + E
    """
    )
    d = Derivation(G).leftmost(1).leftmost(4).leftmost(0).leftmost(3).leftmost(2)
    with self.assertRaisesRegex(ValueError, 'Cannot apply M'):
      d.leftmost(3)

  def test_derivation_rightmost(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """
    )
    d = Derivation(G).rightmost(0).rightmost(2).rightmost(1)
    steps = ((0, 0), (2, 1), (1, 0))
    self.assertEqual(steps, d.steps())

  def test_derivation_rightmost_list(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """
    )
    d = Derivation(G).rightmost([0, 2, 1])
    steps = ((0, 0), (2, 1), (1, 0))
    self.assertEqual(steps, d.steps())

  def test_derivation_rightmost_ncf(self):
    with self.assertRaisesRegex(ValueError, 'derivation on a non context-free grammar'):
      Derivation(Grammar.from_string('S -> s\nT U ->s', False)).rightmost(0)

  def test_derivation_rightmost_allterminals(self):
    G = Grammar.from_string(
      """
    E -> M | A | n
    M -> E * E
    A -> E + E
    """
    )
    d = Derivation(G).rightmost(0).rightmost(3).rightmost(2).rightmost(2)
    with self.assertRaisesRegex(ValueError, 'there are no nonterminals'):
      d.rightmost(2)

  def test_derivation_rightmost_wrongsymbol(self):
    G = Grammar.from_string(
      """
    E -> M | A | n
    M -> E * E
    A -> E + E
    """
    )
    d = Derivation(G).rightmost(0).rightmost(3)
    with self.assertRaisesRegex(ValueError, 'Cannot apply M'):
      d.rightmost(3)

  def test_derivation_possible_steps(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    expected = [(1, 0), (2, 1)]
    actual = list(Derivation(G).step(0, 0).possible_steps())
    self.assertEqual(expected, actual)

  def test_derivation_possible_steps_prod(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    expected = [(1, 0)]
    actual = list(Derivation(G).step(0, 0).possible_steps(prod=1))
    self.assertEqual(expected, actual)

  def test_derivation_possible_steps_pos(self):
    G = Grammar.from_string(
      """
      S -> A B
      A -> a
      B -> b
    """,
      False,
    )
    expected = [(2, 1)]
    actual = list(Derivation(G).step(0, 0).possible_steps(pos=1))
    self.assertEqual(expected, actual)


if __name__ == '__main__':
  unittest.main()
