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

''':mod:`resolver.resource_map`
===============================

:Synopsis:
 - Resolve a filesystem path pointing to a resource map.
:Author:
  DataONE (Dahl)
'''

# Stdlib.
import httplib
import logging
import os
import pprint
import sys

# D1.
import d1_client.data_package
from ..onedrive_exceptions import ONEDriveException

# App.
from d1_client_onedrive.impl import attributes
from d1_client_onedrive.impl import cache_memory as cache
from d1_client_onedrive.impl import directory
from d1_client_onedrive.impl import onedrive_exceptions
from d1_client_onedrive.impl import util
import d1_object
import resolver_base


log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)


class Resolver(resolver_base.Resolver):
  def __init__(self, options, object_tree):
    super(Resolver, self).__init__(options, object_tree)
    self._d1_object_resolver = d1_object.Resolver(options, object_tree)

  # The resource map resolver handles only one hierarchy level, so anything that
  # has more levels is handed to the d1_object resolver. If the object is not a
  # resource map, control is also handed to the d1_object resolver.

  def get_attributes(self, object_tree_root, path):
    log.debug(u'get_attributes: {0}'.format(util.string_from_path_elements(path)))
    if self._is_readme_file(path):
      return self._get_readme_file_attributes()
    is_resource_map = self._is_resource_map(path[0])
    if not is_resource_map:
      return self._d1_object_resolver.get_attributes(object_tree_root, path)
    if len(path) > 1:
      if is_resource_map:
        return self._d1_object_resolver.get_attributes(object_tree_root, path[1:])
      else:
        return self._d1_object_resolver.get_attributes(object_tree_root, path)
    return self._get_attributes(object_tree_root, path)


  def get_directory(self, object_tree_root, path):
    log.debug(u'get_directory: {0}'.format(util.string_from_path_elements(path)))
    is_resource_map = self._is_resource_map(path[0])
    if not is_resource_map:
      return self._d1_object_resolver.get_directory(object_tree_root, path)
    if len(path) > 1:
      if is_resource_map:
        return self._d1_object_resolver.get_directory(object_tree_root, path[1:])
      else:
        return self._d1_object_resolver.get_directory(object_tree_root, path)
    return self._get_directory(object_tree_root, path)


  def read_file(self, object_tree_root, path, size, offset):
    log.debug(u'read_file: {0}, {1}, {2}'.format(util.string_from_path_elements(
      path), size, offset))
    if self._is_readme_file(path):
      return self._get_readme_text(size, offset)
    if len(path) > 1 and self._is_resource_map(path[0]):
      return self._d1_object_resolver.read_file(object_tree_root, path[1:], size, offset)
    return self._d1_object_resolver.read_file(object_tree_root, path, size, offset)


  # Private.

  def _get_attributes(self, object_tree_root, path):
    return attributes.Attributes(self._get_resource_map_size(path[0]),
                                 is_dir=True)


  def _get_directory(self, object_tree_root, path):
    resource_map = self._object_tree.get_science_object(path[0])
    pids = self._deserialize_resource_map(resource_map)
    return pids


  def _get_resource_map_size(self, pid):
    return {
      'total': self._get_total_size_of_objects_in_resource_map,
      'number': self._get_number_of_objects_in_resource_map,
      'zero': self._get_zero,
    }[self._options.folder_size_for_resource_maps](pid)


  def _is_resource_map(self, pid):
    try:
      record = self._object_tree.get_object_record(pid)
    except ONEDriveException:
      self._raise_invalid_pid(pid)
    return record['formatId'] == d1_client.data_package.RDFXML_FORMATID


  def _deserialize_resource_map(self, resource_map):
    package = d1_client.data_package.ResourceMapParser(resource_map)
    return package.get_aggregated_pids()


  def _get_total_size_of_objects_in_resource_map(self, resource_map_pid):
    resource_map = self._object_tree.get_science_object_through_cache(
      resource_map_pid)
    pids = self._deserialize_resource_map(resource_map)
    total = 0
    for pid in pids:
      o = self._object_tree.get_solr_record(pid)
      total += o['size']
    return total


  def _get_number_of_objects_in_resource_map(self, resource_map_pid):
    resource_map = self._object_tree.get_science_object_through_cache(
      resource_map_pid)
    return len(self._deserialize_resource_map(resource_map))


  def _get_zero(self, pid):
    return 0;


if __name__ == '__main__':
  r = Resolver()
  r.deserialize_resource_map()
