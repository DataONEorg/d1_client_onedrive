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

''':mod:`resolver.single`
=========================

:Synopsis:
 - This resolver simply renders all objects into a single folder.
:Author: DataONE (Dahl)
'''

# Stdlib.
import httplib
import logging
import os
import pprint
import sys

# D1.

# App.
sys.path.append('.')
from impl import attributes
from impl import cache_memory as cache
from impl import command_processor
from impl import directory
from impl import directory_item
from impl import path_exception
import resolver_abc
#from impl #import settings
from impl import util

import resource_map


# Set up logger for this module.
log = logging.getLogger(__name__)
try:
  if __name__ in logging.DEBUG_MODULES:
    __level = logging.getLevelName("DEBUG")
    log.setLevel(__level)
except:
  pass  


class Resolver(resolver_abc.Resolver):
  def __init__(self, options, command_processor):
    self._options = options
    self.command_processor = command_processor
    self.resource_map_resolver = resource_map.Resolver(options, command_processor)


  def get_attributes(self, path):
    log.debug('get_attributes: {0}'.format(util.string_from_path_elements(
      path)))

    if len(path) >= 1:
      return self.resource_map_resolver.get_attributes(path[0:])

    return self._get_attribute(path)


  def get_directory(self, path, workspace_folder_objects):
    log.debug('get_directory: {0}'.format(util.string_from_path_elements(
      path)))

    if len(path) >= 1:
      return self.resource_map_resolver.get_directory(path[0:])

    return self._get_directory(path, workspace_folder_objects)


  def read_file(self, path, size, offset):
    log.debug('read_file: {0}, {1}, {2}'
      .format(util.string_from_path_elements(path), size, offset))

    if len(path) >= 1:
      return self.resource_map_resolver.read_file(path[0:], size, offset)

    raise path_exception.PathException('Invalid file')

  # Private.

  def _get_attribute(self, path):
    return attributes.Attributes(0, is_dir=True)


  def _get_directory(self, path, workspace_folder_objects):
    dir = directory.Directory()
    self.append_parent_and_self_references(dir)
    for r in workspace_folder_objects.get_records():
      dir.append(directory_item.DirectoryItem(r['id']))
    return dir
