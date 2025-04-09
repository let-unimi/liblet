import unittest

from liblet.display import Tree


class TestTree(unittest.TestCase):
  def test_child(self):
    t = Tree('root', ['child'])
    self.assertEqual(t.child, 'child')

  def test_two_children_raises_value_error(self):
    with self.assertRaises(ValueError):
      _ = Tree('root', ['child1', 'child2']).child

  def test_no_children_raises_value_error(self):
    with self.assertRaises(ValueError):
      _ = Tree('root').child

  def test_from_lol(self):
    lol = (1, (11,), (12, (121,), (122,)))
    t = Tree.from_lol(lol)
    self.assertEqual(str(t), '(1: (11), (12: (121), (122)))')

  def test_to_lol(self):
    lol = (1, (11,), (12, (121,), (122,)))
    t = Tree.from_lol(lol)
    self.assertEqual(t.to_lol(), lol)

  def test_equals(self):
    lol = (1, (11,), (12, (121,), (122,)))
    t1 = Tree.from_lol(lol)
    t2 = Tree.from_lol(lol)
    self.assertEqual(t1, t2)
