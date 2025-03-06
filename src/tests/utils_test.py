import unittest
import unittest.mock
from copy import copy

from liblet import AttrDict, Queue, Stack, letstr, suffixes, union_of, warn


class UtilsTest(unittest.TestCase):
  def test_unionof(self):
    self.assertEqual({'a', 'b'}, union_of([{'a'}, {'b'}]))

  def test_str(self):
    self.assertEqual('test', letstr('test'))

  def test_obj(self):
    class AClass:
      def __repr__(self):
        return 'AClass'

    self.assertEqual('AClass', letstr(AClass()))

  def test_emptyset(self):
    self.assertEqual('{}', letstr(set()))

  def test_emptyfrozenset(self):
    self.assertEqual('{}', letstr(frozenset()))

  def test_sefofstr(self):
    self.assertEqual('{a, b, c}', letstr({'a', 'b', 'c'}))

  def test_tupleofesefofstr(self):
    self.assertEqual('(d, {a, b, c})', letstr(({'a', 'b', 'c'}, 'd')))

  def test_listofesefofstr(self):
    self.assertEqual('[(d), e, {a, b, c}]', letstr([{'a', 'b', 'c'}, ('d',), 'e']))

  def test_sefofsetofstr(self):
    self.assertEqual('{{a, b, c}, {d, e}}', letstr({frozenset({'a', 'b', 'c'}), frozenset({'d', 'e'})}))

  def test_stack(self):
    s = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    n = len(s)
    out = s.pop()
    actual = f'{n} {out} {s}'
    expected = '3 3 Stack(1, 2 ↔)'
    self.assertEqual(expected, actual)

  def test_stack_peek(self):
    s = Stack()
    s.push(1)
    s.push(2)
    p = s.peek()
    actual = f'{p} {s}'
    expected = '2 Stack(1, 2 ↔)'
    self.assertEqual(expected, actual)

  def test_stack_copy(self):
    s = Stack([1, 2, 3])
    c = copy(s)
    s.push(4)
    c.push(5)
    actual = f'{s} {c}'
    expected = 'Stack(1, 2, 3, 4 ↔) Stack(1, 2, 3, 5 ↔)'
    self.assertEqual(expected, actual)

  def test_stack_iter(self):
    actual = list(Stack([1, 2, 3]))
    expected = [1, 2, 3]
    self.assertEqual(expected, actual)

  def test_stack_reversed(self):
    actual = list(reversed(Stack([1, 2, 3])))
    expected = [3, 2, 1]
    self.assertEqual(expected, actual)

  def test_empty_stack(self):
    self.assertEqual('Stack()', str(Stack()))

  def test_bounded_stack(self):
    s = Stack(maxlen=2)
    s.push(1)
    s.push(2)
    s.push(3)
    n = len(s)
    out = s.pop()
    actual = f'{n} {out} {s}'
    expected = '2 3 Stack(2 ↔)'
    self.assertEqual(expected, actual)

  def test_queue(self):
    q = Queue()
    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)
    n = len(q)
    out = q.dequeue()
    actual = f'{n} {out} {q}'
    expected = '3 1 Queue(← 2, 3 ←)'
    self.assertEqual(expected, actual)

  def test_queue_copy(self):
    q = Queue([1, 2, 3])
    c = copy(q)
    q.enqueue(4)
    c.enqueue(5)
    actual = f'{q} {c}'
    expected = 'Queue(← 1, 2, 3, 4 ←) Queue(← 1, 2, 3, 5 ←)'
    self.assertEqual(expected, actual)

  def test_queue_iter(self):
    actual = list(Queue([1, 2, 3]))
    expected = [1, 2, 3]
    self.assertEqual(expected, actual)

  def test_queue_reversed(self):
    actual = list(reversed(Queue([1, 2, 3])))
    expected = [3, 2, 1]
    self.assertEqual(expected, actual)

  def test_empty_queue(self):
    self.assertEqual('Queue()', str(Queue()))

  def test_bounded_queue(self):
    q = Queue(maxlen=2)
    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)
    n = len(q)
    out = q.dequeue()
    actual = f'{n} {out} {q}'
    expected = '2 2 Queue(← 3 ←)'
    self.assertEqual(expected, actual)

  def test_warn(self):
    with unittest.mock.patch('liblet.utils.stderr') as stderr_mock:
      warn('this is a test')
      stderr_mock.write.assert_called_with('this is a test\n')

  def test_suffixes(self):
    actual = list(suffixes('atest'))
    expected = ['atest', 'test', 'est', 'st', 't']
    self.assertEqual(expected, actual)

  def test_attrdict_get(self):
    d = {'x': 1}
    ad = AttrDict(d)
    self.assertEqual(d['x'], ad.x)

  def test_attrdict_set(self):
    d = {}
    ad = AttrDict(d)
    ad.x = 1
    self.assertEqual(d['x'], ad.x)

  def test_attrict_rest(self):
    d = {'x': 1, 'y': 2}
    ad = AttrDict(d)
    ad['z'] = 3
    del ad['x']
    self.assertEqual(d['y'], ad['y'])
    self.assertEqual(len(d), len(ad))
    self.assertEqual(list(d), list(ad))


if __name__ == '__main__':
  unittest.main()
