import unittest

from liblet.display import Tree


class TestTree(unittest.TestCase):
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
