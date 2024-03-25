import unittest

loader = unittest.TestLoader()
tests = loader.discover('src/tests', '*_test.py')
test_runner = unittest.runner.TextTestRunner()
test_runner.run(tests)
