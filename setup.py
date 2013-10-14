""" Setup pylama installation. """
#!/usr/bin/env python
from os import path as op
from sys import version_info

from setuptools import setup, find_packages

from pylama import version, __project__, __license__


read = lambda f: open(
    op.join(op.dirname(__file__), f)).read() if op.exists(f) else ''


install_requires = []
if version_info < (2, 7):
    install_requires += ['argparse']


meta = dict(
    name=__project__,
    version=version,
    license=__license__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    platforms=('Any'),
    keywords='pylint pep8 pyflakes mccabe linter qa pep257'.split(),

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    url=' http://github.com/klen/pylama',

    package_data = {"pylama": ['pylint.rc']},
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'pylama = pylama.main:shell',
        ]
    },

    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)', # noqa
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Code Generators',
    ],

    install_requires=install_requires,
    test_suite = 'tests',
)


if __name__ == "__main__":
    setup(**meta)
