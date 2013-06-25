import unittest
from sys import version_info

from pylama.core import run
from pylama.tasks import check_path, async_check_files
from pylama.main import shell


class LamaTest(unittest.TestCase):

    def test_lama(self):

        errors = run('dummy.py')
        self.assertEqual(len(errors), 3)

    def test_pyflakes(self):
        errors = run('dummy.py', linters=['pyflakes'])
        self.assertFalse(errors)

    def test_pep257(self):
        errors = run('dummy.py', linters=['pep257'])
        self.assertTrue(errors)

    def test_ignore_select(self):
        errors = run('dummy.py', ignore=['E301'])
        self.assertEqual(len(errors), 2)

        errors = run('dummy.py', ignore=['E3'])
        self.assertEqual(len(errors), 2)

        errors = run(
            'dummy.py', ignore=['E3'], select=['E301'])
        self.assertEqual(len(errors), 3)
        self.assertTrue(errors[0]['col'])

    def test_pylint(self):
        # test pylint
        if version_info < (3, 0):
            errors = run('pylama/checkers/pylint/utils.py', linters=['pylint'])
            self.assertEqual(len(errors), 14)

    def test_checkpath(self):
        errors = check_path('dummy.py', linters=['pep8'])
        self.assertTrue(errors)
        self.assertEqual(errors[0]['rel'], 'dummy.py')

    def test_async(self):
        errors = async_check_files(['dummy.py'], async=True, linters=['pep8'])
        self.assertTrue(errors)

    def test_shell(self):
        errors = shell('-o dummy dummy.py'.split(), error=False)
        self.assertTrue(errors)

    @staticmethod
    def test_git_hook():
        from pylama.hook import git_hook
        try:
            git_hook()
            raise AssertionError('Test failed.')
        except SystemExit:
            pass

# lint_ignore=C0110
