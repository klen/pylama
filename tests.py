import unittest


class LamaTest(unittest.TestCase):

    def test_lama(self):
        from pylama.main import run
        errors = run('pylama/pyflakes/messages.py')
        self.assertEqual(len(errors), 4)

        errors = run('pylama/pyflakes/messages.py', linters=['pyflakes'])
        self.assertFalse(errors)

        errors = run('pylama/pyflakes/messages.py', ignore=['E301'])
        self.assertEqual(len(errors), 3)

        errors = run('pylama/pyflakes/messages.py', ignore=['E3'])
        self.assertEqual(len(errors), 2)

        errors = run(
            'pylama/pyflakes/messages.py', ignore=['E3'], select=['E301'])
        self.assertEqual(len(errors), 3)
        self.assertTrue(errors[0]['col'])

        # test pylint
        errors = run('pylama/pylint/utils.py', linters=['pylint'])
        self.assertEqual(len(errors), 12)
