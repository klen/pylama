import unittest
from sys import version_info


class LamaTest(unittest.TestCase):

    def test_lama(self):
        from pylama.main import run
        errors = run('dummy.py')
        self.assertEqual(len(errors), 4)

        errors = run('dummy.py', linters=['pyflakes'])
        self.assertFalse(errors)

        errors = run('dummy.py', ignore=['E301'])
        self.assertEqual(len(errors), 3)

        errors = run('dummy.py', ignore=['E3'])
        self.assertEqual(len(errors), 2)

        errors = run(
            'dummy.py', ignore=['E3'], select=['E301'])
        self.assertEqual(len(errors), 3)
        self.assertTrue(errors[0]['col'])

        # test pylint
        if version_info < (3, 0):
            errors = run('pylama/pylint/utils.py', linters=['pylint'])
            self.assertEqual(len(errors), 14)
