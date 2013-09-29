#!/usr/bin/env python
# Copyright 2007 The Closure Linter Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Checks JavaScript files for common style guide violations.

gjslint.py is designed to be used as a PRESUBMIT script to check for javascript
style guide violations.  As of now, it checks for the following violations:

  * Missing and extra spaces
  * Lines longer than 80 characters
  * Missing newline at end of file
  * Missing semicolon after function declaration
  * Valid JsDoc including parameter matching

Someday it will validate to the best of its ability against the entirety of the
JavaScript style guide.

This file is a front end that parses arguments and flags.  The core of the code
is in tokenizer.py and checker.py.
"""

__author__ = ('robbyw@google.com (Robert Walker)',
              'ajp@google.com (Andy Perelson)',
              'nnaze@google.com (Nathan Naze)',)

import errno
import itertools
import platform
import sys
import time

import gflags as flags

from . import errorrecord
from . import runner
from .common import erroraccumulator
from .common import simplefileflags as fileflags

# Attempt import of multiprocessing (should be available in Python 2.6 and up).
try:
  # pylint: disable=g-import-not-at-top
  import multiprocessing
except ImportError:
  multiprocessing = None

FLAGS = flags.FLAGS
flags.DEFINE_boolean('unix_mode', False,
                     'Whether to emit warnings in standard unix format.')
flags.DEFINE_boolean('beep', True, 'Whether to beep when errors are found.')
flags.DEFINE_boolean('time', False, 'Whether to emit timing statistics.')
flags.DEFINE_boolean('check_html', False,
                     'Whether to check javascript in html files.')
flags.DEFINE_boolean('summary', False,
                     'Whether to show an error count summary.')
flags.DEFINE_list('additional_extensions', None, 'List of additional file '
                  'extensions (not js) that should be treated as '
                  'JavaScript files.')
flags.DEFINE_boolean('multiprocess',
                     platform.system() is 'Linux' and bool(multiprocessing),
                     'Whether to attempt parallelized linting using the '
                     'multiprocessing module.  Enabled by default on Linux '
                     'if the multiprocessing module is present (Python 2.6+). '
                     'Otherwise disabled by default. '
                     'Disabling may make debugging easier.')


GJSLINT_ONLY_FLAGS = ['--unix_mode', '--beep', '--nobeep', '--time',
                      '--check_html', '--summary']


def _MultiprocessCheckPaths(paths):
  """Run _CheckPath over mutltiple processes.

  Tokenization, passes, and checks are expensive operations.  Running in a
  single process, they can only run on one CPU/core.  Instead,
  shard out linting over all CPUs with multiprocessing to parallelize.

  Args:
    paths: paths to check.

  Yields:
    errorrecord.ErrorRecords for any found errors.
  """

  pool = multiprocessing.Pool()

  path_results = pool.imap(_CheckPath, paths)
  for results in path_results:
    for result in results:
      yield result

  # Force destruct before returning, as this can sometimes raise spurious
  # "interrupted system call" (EINTR), which we can ignore.
  try:
    pool.close()
    pool.join()
    del pool
  except OSError as err:
    if err.errno is not errno.EINTR:
      raise err


def _CheckPaths(paths):
  """Run _CheckPath on all paths in one thread.

  Args:
    paths: paths to check.

  Yields:
    errorrecord.ErrorRecords for any found errors.
  """

  for path in paths:
    results = _CheckPath(path)
    for record in results:
      yield record


def _CheckPath(path):
  """Check a path and return any errors.

  Args:
    path: paths to check.

  Returns:
    A list of errorrecord.ErrorRecords for any found errors.
  """

  error_handler = erroraccumulator.ErrorAccumulator()
  runner.Run(path, error_handler)

  make_error_record = lambda err: errorrecord.MakeErrorRecord(path, err)
  return map(make_error_record, error_handler.GetErrors())


def main(argv = None):
  """Main function.

  Args:
    argv: Sequence of command line arguments.

  Returns:
    Generator (iterator) to any found errors records.
  """
  if argv is None:
    argv = flags.FLAGS(sys.argv)

  if FLAGS.time:
    start_time = time.time()

  suffixes = ['.js']
  if FLAGS.additional_extensions:
    suffixes += ['.%s' % ext for ext in FLAGS.additional_extensions]
  if FLAGS.check_html:
    suffixes += ['.html', '.htm']
  paths = fileflags.GetFileList(argv, 'JavaScript', suffixes)

  if FLAGS.multiprocess:
    records_iter = _MultiprocessCheckPaths(paths)
  else:
    records_iter = _CheckPaths(paths)

  return records_iter

if __name__ == '__main__':
  main()
