#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2012 DataONE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''':mod:`test_command_processor`
================================

:Synopsis:
 - Test the CommandProcessor class.
:Author: DataONE (Dahl)
'''

# Stdlib.
#import os
import sys
import unittest

# D1.
sys.path.append('../fuse')
import cache


class TestCache(unittest.TestCase):
  def setUp(self):
    pass


  def test_100_cache(self):
    c = cache.Cache(10)
    c['a'] = 1
    self.assertEqual(len(c), 1)
    self.assertEqual(c['a'], 1)
    #self.assertEqual(len(c), 1)


  def test_110_cache(self):
    c = cache.Cache(2)
    c['a'] = 1
    c['b'] = 2
    c['c'] = 3
    self.assertEqual(len(c), 2)
    self.assertRaises(KeyError, c.__getitem__, 'a')
    self.assertEqual(c['b'], 2)
    self.assertEqual(c['c'], 3)


  def test_120_cache(self):
    c = cache.Cache(2)
    c['a'] = 1
    c['b'] = 2
    c['c'] = 3
    c['a'] = 4
    self.assertEqual(len(c), 2)
    self.assertRaises(KeyError, c.__getitem__, 'b')
    self.assertEqual(c['a'], 4)
    self.assertEqual(c['c'], 3)


#===============================================================================

def log_setup():
  formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                                '%y/%m/%d %H:%M:%S')
  console_logger = logging.StreamHandler(sys.stdout)
  console_logger.setFormatter(formatter)
  logging.getLogger('').addHandler(console_logger)


def main():
  import optparse

  log_setup()

  # Command line opts.
  parser = optparse.OptionParser()
  parser.add_option('--debug', action='store_true', default=False, dest='debug')
  parser.add_option('--test', action='store', default='', dest='test',
                    help='run a single test')

  (options, arguments) = parser.parse_args()

  if options.debug:
    logging.getLogger('').setLevel(logging.DEBUG)
  else:
    logging.getLogger('').setLevel(logging.ERROR)

  s = TestCache
  s.options = options

  if options.test != '':
    suite = unittest.TestSuite(map(s, [options.test]))
  else:
    suite = unittest.TestLoader().loadTestsFromTestCase(s)

  unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
  main()
