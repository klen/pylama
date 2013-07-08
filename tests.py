import unittest
from sys import version_info

from pylama.core import run
from pylama.tasks import check_path, async_check_files


class LamaCoreTest(unittest.TestCase):

    def test_filters(self):
        from pylama.core import filter_errors

        self.assertTrue(filter_errors(
            dict(text='E'), select=['E'], ignore=['E101']
        ))

        self.assertFalse(filter_errors(
            dict(text='W'), select=['W100'], ignore=['W']
        ))

    def test_parse_modeline(self):
        from pylama.core import parse_modeline

        code = """
            bla bla bla

            # lint_ignore=W12,E14:lint_select=R
        """

        params = parse_modeline(code)
        self.assertEqual(params, dict(
            lint_ignore='W12,E14', lint_select='R'
        ))

    def test_prepare_params(self):
        from pylama.core import prepare_params

        p1 = dict(lint_ignore='W', select='R01', lint=1)
        p2 = dict(lint=0, lint_ignore='E34,R45', select='E')
        params = prepare_params(p1, p2)

        self.assertEqual(
            params,
            {
                'ignore': set(['R45', 'E34', 'W']), 'skip': [False], 'lint': 0,
                'select': set(['R01', 'E'])})


class LamaTest(unittest.TestCase):

    def test_lama(self):
        errors = run('dummy.py', ignore=set(['M234']), config=dict(lint=1))
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
        from pylama.main import shell, prepare_params, check_files

        errors = shell('-o dummy dummy.py'.split(), error=False)
        self.assertTrue(errors)

        params = prepare_params(dict(lint='0'))
        self.assertFalse(params['lint'])

        errors = check_files(['dummy.py'], error=False)
        self.assertTrue(errors)

    @staticmethod
    def test_git_hook():
        from pylama.hook import git_hook
        try:
            git_hook()
            raise AssertionError('Test failed.')
        except SystemExit:
            pass

    @staticmethod
    def test_hg_hook():
        from pylama.hook import hg_hook
        try:
            hg_hook(None, dict())
            raise AssertionError('Test failed.')
        except SystemExit:
            pass
