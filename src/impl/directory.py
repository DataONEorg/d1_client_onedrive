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

''':mod:`directory`
===================

:Synopsis:
 - Hold the list of files and folders for a directory.
 - Hold the name, size and is_directory flag for each file or folder.
:Author: DataONE (Dahl)
'''

# Stdlib.
import collections
import logging
import os


# Set up logger for this module.
log = logging.getLogger(__name__)


class Directory(collections.MutableSequence):
  def __init__(self):
    self.list = list()


  def __len__(self):
    return len(self.list)


  def __getitem__(self, i):
    return self.list[i]


  def __delitem__(self, i):
    del self.list[i]


  def __setitem__(self, i, v):
    self.list[i] = v


  def __str__(self):
    return str(self.list)


  def insert(self, i, v):
    self.list.insert(i, v)


  def names(self):
    return [d.name() for d in self.list]

#===============================================================================

class DirectoryItem(object):
  def __init__(self, name, size=0, is_dir=False):
    self.name_ = name
    self.size_ = size
    self.is_directory_ = is_dir


  def __eq__(self, other):
    return self.__dict__ == other.__dict__


  def __str__(self):
    return 'DirectoryItem({0}, {1}, {2})'.format(repr(self.name_), self.size_,
                                                 self.is_directory_)


  def __repr__(self):
    return str(self)


  def name(self):
    return self.name_


  def size(self):
    return self.size_


  def is_directory(self):
    return self.is_directory_
