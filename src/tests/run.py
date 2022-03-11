import unittest

import unittest
loader = unittest.TestLoader()
tests = loader.discover('src/tests', '*_test.py')
testRunner = unittest.runner.TextTestRunner()
testRunner.run(tests)
