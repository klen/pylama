#!/usr/bin/env python
from os import path as op

from setuptools import setup, find_packages

from pylama import version, __project__, __license__


def read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''


META_DATA = dict(
    name=__project__,
    version=version,
    license=__license__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    platforms=('Any'),

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    url=' http://github.com/klen/adrest',

    packages=find_packages(),

    test_suite = 'tests.__main__',
)


if __name__ == "__main__":
    setup(**META_DATA)
