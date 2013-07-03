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

''':mod:`resolver.workspace`
============================

:Synopsis:
 - Resolve a filesystem path that points to a directory to the contents
   of the directory by querying the query engine.
:Author: DataONE (Dahl)
'''

# Stdlib.
import pprint
import logging
import os
from StringIO import StringIO

# D1.

# App.
from impl import attributes
from impl import cache_memory as cache
from impl import command_processor
from impl import directory
from impl import directory_item
from impl import path_exception
from .    import resolver_abc
from .    import resource_map
#from impl #import settings
from impl import util
from impl.resolver import author
from impl.resolver import taxa
from impl.resolver import region
from impl.resolver import time_period
from impl.resolver import single

from d1_workspace.types.generated import generateFolderHelpText
import d1_workspace.types.generated.workspace_types as workspace_types

# Set up logger for this module.
log = logging.getLogger(__name__)
#Set level specific for this module if specified
try:
  log.setLevel(logging.getLevelName( \
               getattr(logging,'ONEDRIVE_MODULES')[__name__]) )
except:
  pass

README="readme.txt"

class WorkspaceFolderObjects(object):
  '''A workspace folder contains queries (that resolve to any number of matching
  PIDs) and PIDs that are specified directly. This class iteraterates over the
  queries and PIDs and issues Solr queries to get the records for each PID. This
  object then holds those records. Because the same object can be returned by
  any number of queries as well as be specified directly, the results are stored
  in a dictionary, keyed on the PID'''
  def __init__(self, command_processor, workspace_folder):
    self._command_processor = command_processor
    self._workspace_folder = workspace_folder
    self._records = self._get_records_for_identifiers()
    self._records.update(self._get_records_for_queries())
    self.helpText = "Workspace Folder Object help text"


  def get_records(self):
    return self._records.values()


  def _get_records_for_identifiers(self):
    records = {}
    for pid in self._workspace_folder.identifier:
      try:
        records[pid] = self._command_processor.get_solr_record(pid)
      except path_exception.PathException:
        pass
    return records


  def _get_records_for_queries(self):
    records = {}
    for q in self._workspace_folder.query:
      response = self._command_processor.solr_query(q)
      for sci_obj in response['response']['docs']:
        records[sci_obj['id']] = sci_obj
        #log.debug("solr response doc: %s" % str(sci_obj))
    return records


  def helpSize(self):
    return len(self.helpText)

  
  def getHelp(self, offset=0, size=None):
    return self.helpText[offset:size]

  

class Resolver(resolver_abc.Resolver):
  def __init__(self, options, command_processor):
    super(Resolver, self).__init__(options, command_processor)
    self.resource_map_resolver = resource_map.Resolver(options, command_processor)
    self.load_workspace(options.WORKSPACE_XML)
    self.resolvers = {
      'Authors': author.Resolver(self._options, self.command_processor),
      'Regions': region.Resolver(self._options, self.command_processor),
      'Taxa': taxa.Resolver(self._options, self.command_processor),
      'TimePeriods': time_period.Resolver(self._options, self.command_processor),
      'All': single.Resolver(self._options, self.command_processor),
    }
    #self.facet_value_cache = cache.Cache(self._options.MAX_FACET_NAME_CACHE_SIZE)
    self._generateHelp()


  def get_attributes(self, path, fs_path=''):
    log.debug('get_attributes: {0}'.format(util.string_from_path_elements(
      path)))

    # All items rendered by the Workspace Resolver are folders. Anything else
    # is deferred to one of the child resolvers.
    try:
      return super(Resolver, self).get_attributes(path, fs_path)
    except path_exception.NoResultException:
      pass
      
    log.debug('get_attributes2: {0}'.format(util.string_from_path_elements(
      path)))
    # To determine where the path transitions from the workspace to the
    # controlled hierarchy, we check for the controlled hierarchy root names.
    # This means that those names are reserved. They can not be used as
    # workspace folder names by the user.
    workspace_folder = self._get_workspace_folder(path)

    log.debug('get_attributes3: {0}'.format(util.string_from_path_elements(
      path)))

    # All workspace items are folders.
    if workspace_folder is not None:
      if len(path) > 0:
        if path[-1] == self.helpName():
          return attributes.Attributes(size=self.folderHelpSize(workspace_folder),
                                       is_dir=False)
      return attributes.Attributes(is_dir=True)

    log.debug('get_attributes4: {0}'.format(util.string_from_path_elements(
      path)))

    # If the path is not to a workspace folder root, a valid path must go to a
    # controlled hierarchy root or subfolder THROUGH a workspace folder root. In
    # that case, the first path element that matches the reserved name of one of
    # the controlled hierarchy roots becomes the separator between the two
    # sections and determines which resolver to use for the tail section of the
    # path.
    workspace_path, resolver, controlled_path = \
      self._split_path_by_reserved_name(path)

    log.debug('get_attributes5: {0}'.format(util.string_from_path_elements(
      path)))


    # If the workspace_path is not valid now, then the path is invalid.
    workspace_folder = self._get_workspace_folder(workspace_path)
    if workspace_folder is None:
      raise path_exception.PathException('Invalid folder')
    
    if resolver == self.helpName():
      return attributes.Attributes(size=self.folderHelpSize(workspace_folder),
                                   is_dir=False)


    # Now have all information required for gathering information about all the
    # objects in the workspace folder and dispatching to a controlled hierarchy
    # resolver.
    return self.resolvers[resolver].get_attributes(controlled_path)



#    # The facet path parser split method validates the path to make sure it can
#    # be cleanly split to a valid facet and/or object section. If the path is
#    # not syntactically valid, the parser raises an exception.
#    facet_section, object_section = self.facet_path_parser \
#      .split_path_to_facet_and_object_sections(path)
#
#    # If object_section is not empty, the path references something outside of
#    # the faceted search area, so the facet section is stripped off the path,
#    # and the remainder is passed to the package resolver.
#    if len(object_section):
#      return self.resource_map_resolver.get_attributes(object_section)
#
#    # Handle faceted path that is syntactically valid but uses a non-existing
#    # facet name or value.
#    path_facets = self.facet_path_parser.facets_from_path(facet_section)
#    self._raise_if_any_invalid_facet(path_facets)
#
#    # It is not necessary to check if the path points to a file because an
#    # earlier step determined that path if a valid facet_section, and all
#    # elements in a facet_section path are folders.
#
#    # The path can reference either the root, a facet name or a facet value.
#    if self._is_root(path_facets):
#      return self._get_root_attribute()
#    elif self._is_path_to_undefined_facet(path_facets):
#      return self._get_facet_name_attribute(path_facets)
#    else:
#      return self._get_facet_value_attribute(path_facets)
#
#
  def get_directory(self, path, preconfigured_query=None, fs_path=''):
    # the directory will typically be in the cache. already retrieved by
    # get_attributes, since get_attributes() needs to know how many items
    # there are in the directory, in order to return that count.
    log.debug('get_directory: {0}'.format(util.string_from_path_elements(path)))

    # To determine where the path transitions from the workspace to the
    # controlled hierarchy, we check for the controlled hierarchy root names.
    # This means that those names are reserved. They can not be used as
    # workspace folder names by the user.

    workspace_folder = self._get_workspace_folder(path)

    # If the path is to a workspace folder root, render the roots of the
    # controlled hierarchies and workspace subfolders. No need to get the object
    # metadata from solr at this point, as it is not yet known if the user will
    # actually enter one of the controlled hierarchies.
    if workspace_folder is not None:
      res = self._resolve_workspace_folder(workspace_folder)
      if self.folderHelpSize(workspace_folder) > 0:
        res.append(self.getHelpDirectoryItem())
      return res

    # If the path is not to a workspace folder root, a valid path must go to a
    # controlled hierarchy root or subfolder THROUGH a workspace folder root. In
    # that case, the first path element that matches the reserved name of one of
    # the controlled hierarchy roots becomes the separator between the two
    # sections and determines which resolver to use for the tail section of the
    # path.
    workspace_path, resolver, controlled_path = \
      self._split_path_by_reserved_name(path)

    # If the workspace_path is not valid now, then the path is invalid.
    workspace_folder = self._get_workspace_folder(workspace_path)
    if workspace_folder is None:
      raise path_exception.PathException('Invalid folder')

    # Now have all information required for gathering information about all the
    # objects in the workspace folder and dispatching to a controlled hierarchy
    # resolver.
    workspace_folder_objects = WorkspaceFolderObjects(self.command_processor,
                                                      workspace_folder)
    return self.resolvers[resolver].get_directory(controlled_path,
                                           workspace_folder_objects)


    #d = directory.Directory()
    #self.append_parent_and_self_references(d)
    #
    #d.append(directory_item.DirectoryItem('Authors'))
    #
    #
    ## Each workspace folder corresponds to a specific set of objects, which is
    ## determined here. Thee objects are rendered by the child resolvers.
    #
    #
    #self.resolvers
    #
    ##self.append_folders(d, f)
    ## Add contents of folder.
    #for o in workspace_folder_objects.get_records():
    #  d.append(directory_item.DirectoryItem(o['id'] + ' ' + o.get('author', '')))
    ##pprint.pprint(w.objects)
    #
    ##self.append_folders(d, f)
    ##self.append_pids(d, f)
    ##self.append_queries(d, f)
    #return d


  def read_file(self, path, size, offset, fs_path=''):
    log.debug('read_file: {0}, {1}, {2}'.format(util.string_from_path_elements(
      path), size, offset))
    try:
      return super(Resolver, self).read_file(path, size, offset, fs_path=fs_path)
    except path_exception.NoResultException:
      pass

    # The workspace resolver exposes no readable files.
    workspace_folder = self._get_workspace_folder(path)

    if workspace_folder is not None:
      if len(path) > 0:
        if path[-1] == workspace_folder.helpName():
          return self.getFolderHelp(workspace_folder, offset, size)
          #return workspace_folder.getHelp(offset, size)
      raise path_exception.PathException('Invalid file')


    workspace_path, resolver, controlled_path = \
      self._split_path_by_reserved_name(path)

    workspace_folder = self._get_workspace_folder(workspace_path)
    if workspace_folder is None:
      raise path_exception.PathException('Invalid file')

    if resolver == self.helpName():
      res = self.getFolderHelp(workspace_folder, offset, size)
      log.debug(res)
      return res
    #print self.resolvers[resolver]
    return self.resolvers[resolver].read_file(controlled_path, size, offset)


  def load_workspace(self, workspace_xml):
    '''Loads the workspace XML document
    '''
    self._workspace = self._create_workspace_from_xml_doc(workspace_xml)
    #Additional processing to flush cache etc


  def folderHelpSize(self, folder):
    '''Return the size of the help text for a folder
    '''
    try:
      return len(folder._helpText)
    except AttributeError:
      #Generate help text for folder
      self.getFolderHelp(folder)
      return len(folder._helpText)
    pass
  
  
  def getFolderHelp(self, folder, offset=0, size=None):
    '''Return help text for specific folder. If not available, then the 
    help text is generated by reviewing the folder attributes. The help text
    is then attached to the folder object for future use.
    #TODO: consider thread safety for this.
    '''
    try:
      test = folder._helpText
    except AttributeError:
      #Need to generate the help text
      folder._helpText = generateFolderHelpText(folder)
      #folder._helpText = "This is some folder help text"
    res = folder._helpText[offset:size]
    log.debug(res)
    return res
    

  #
  # Private.
  #
  def _generateHelp(self):
    res = StringIO()
    t = u"ONEDrive Workspace Overview"
    res.write(t)
    res.write(u"\n")
    res.write(u"%s\n" % u"="*len(t))
    res.write(u"\n")
    res.write(u"""
The ONEDrive Workspace folder contains objects that match queries specified
in the workspace configuration and individual identifiers 
    """)
    
    return res.getvalue().encode('utf8')
  

  def _create_workspace_from_xml_doc(self, xml_doc_path):
    xml_doc = open(xml_doc_path, 'rb').read()
    return workspace_types.CreateFromDocument(xml_doc)


  def _split_path_by_reserved_name(self, path):
    '''Return: workspace_path, resolver, controlled_path
    '''
    for i, e in enumerate(path):
      if e in self.resolvers:
        return path[:i], path[i], path[i + 1:]
      elif e == self.helpName():
        return path[:i], path[i], path[i + 1:]
    raise path_exception.PathException('Invalid folder: %s' % str(path))


  #def _resolve_controlled_roots(self, workspace_folder):
  #  dir = directory.Directory()
  #  dir.append(directory_item.DirectoryItem('Authors'))
  #  dir.append(directory_item.DirectoryItem('Regions'))
  #  dir.append(directory_item.DirectoryItem('ScienceDiscipline'))
  #  dir.append(directory_item.DirectoryItem('Taxa'))
  #  dir.append(directory_item.DirectoryItem('TimePeriods'))
  #  return dir


  def _resolve_workspace_folder(self, workspace_folder):
    dir = directory.Directory()
    self.append_parent_and_self_references(dir)
    self.append_folders(dir, workspace_folder)
    #if self.helpSize() > 0:
    #  dir.append(self.getHelpDirectoryItem())
    dir.extend([directory_item.DirectoryItem(name) for name in
               sorted(self.resolvers)])
    return dir


  def append_folders(self, d, workspace_folder):
    for f in workspace_folder.folder:
      d.append(directory_item.DirectoryItem(f.name))
    return d
  #
  #
  #def append_pids(self, d, workspace_folder):
  #  for pid in workspace_folder.identifier:
  #    d.append(directory_item.DirectoryItem(pid))
  #  return d
  #
  #
  #def append_queries(self, d, workspace_folder):
  #  for q in workspace_folder.query:
  #    sci_objs = self.command_processor.solr_query_raw(q)
  #    for s in sci_objs:
  #      d.append(directory_item.DirectoryItem(s['id']))
  #  return d



  # A workspace folder can contain other folders, identifiers or queries.

  # Identifiers and queries are rendered directly into a folder.

  #def is_workspace_folder(self, path):
  #  return self._get_workspace_folder(path) is not None

  # workspace = root Folder
  # To iterate over
  #  folders in Folder: Folder.folder
  #  PIDs in Folder: Folder.identifier
  #  SOLR queries in Folder: Folder.query

  def _get_workspace_folder(self, path):
    '''Given a path, return the members of that path from the workspace.
    '''
    return self._get_workspace_folder_recursive(self._workspace, path, 0)


  def _get_workspace_folder_recursive(self, folder, path, c):
    if len(path) == c:
      return folder
    for f in folder.folder:
      if f.name == path[c]:
        return self._get_workspace_folder_recursive(f, path, c + 1)


#    # If the path references something outside of the faceted search area, the
#    # facet section is stripped off the path, and the remainder is passed to the
#    # next resolver.
#    facet_section, object_section = self.facet_path_parser \
#      .split_path_to_facet_and_object_sections(path)
#
#    if len(object_section):
#      return self.resource_map_resolver.get_directory(object_section)
#
#    return self._get_directory(path, preconfigured_query)
#
#
#
#
#  def _read_file(self, path, size, offset):
#    facet_section, object_section = self.facet_path_parser \
#      .split_path_to_facet_and_object_sections(path)
#
#    if len(object_section):
#      return self.resource_map_resolver.read_file(object_section, size, offset)
#
#    self._raise_invalid_path()
#
#
#  def _get_facet_name_attribute(self, path_facets):
#    applied_facets = self._get_applied_facets(path_facets)
#    # solr_query finds the pid and size of all science objects that match
#    # the applied facets. And it finds the names of the facets that are not
#    # yet applied, together with their matching object counts.
#    unapplied_facet_counts, sci_objs = self.command_processor.solr_query(
#      applied_facets=[])
#    n = self._get_last_element_facet_name(path_facets)
#    return attributes.Attributes(is_dir=True,
#                                 size=unapplied_facet_counts[n]['count'])
#
#
#  def _get_facet_value_attribute(self, path_facets):
#    applied_facets = self._get_applied_facets(path_facets)[:-1]
#    unapplied_facet_counts, sci_objs = self.command_processor.solr_query(
#      applied_facets=applied_facets)
#
#    self._raise_if_invalid_facet_value(unapplied_facet_counts, path_facets[-1])
#
#    last_facet_name = self._get_last_element_facet_name(path_facets)
#    last_facet_value = self._get_last_element_facet_value(path_facets)
#    n_matches = self._get_match_count_for_facet_value(unapplied_facet_counts,
#                                                      last_facet_name,
#                                                      last_facet_value)
#    return attributes.Attributes(is_dir=True, size=n_matches)
#
#
#  def _get_match_count_for_facet_value(self, unapplied_facet_counts, facet_name,
#                                       facet_value):
#    for value in unapplied_facet_counts[facet_name]['values']:
#      if facet_value == value[0]:
#        return value[1]
#
#
#  def _get_root_attribute(self):
#    return attributes.Attributes(is_dir=True,
#                                 size=self._get_match_count_for_root())
#
#
#  def _get_match_count_for_root(self):
#    sci_objs = self.command_processor.solr_query()[1]
#    return len(sci_objs)
#
#
#  def _get_directory(self, path, preconfigured_query):
#    dir = directory.Directory()
#    self.append_parent_and_self_references(dir)
#
#    path_facets = self.facet_path_parser.facets_from_path(path)
#    applied_facets = self._get_applied_facets(path_facets)
#
#    unapplied_facet_counts, sci_objs = self.command_processor.solr_query(
#      applied_facets=applied_facets, filter_queries=preconfigured_query)
#
#    if self._is_path_to_undefined_facet(path_facets):
#      dir.extend(self._get_facet_values(unapplied_facet_counts,
#        self._get_last_element_facet_name(path_facets)))
#    else:
#      dir.extend(self._get_unapplied_facets(unapplied_facet_counts))
#
#    dir.extend(self._directory_items_from_science_objects(sci_objs))
#
#    return dir
#
#
#  # This was the initial implementation of error file detection in the faceted
#  # search. It is very resource intensive as it causes Solr queries to be
#  # performed for each folder touched by get_attributes(). Leaving it in, in
#  # case the new implementation does not work out.
#  def _raise_if_any_invalid_facet(self, path_facets):
#    for facet in path_facets:
#      self._raise_if_invalid_facet(facet)
#
#
#  def _raise_if_invalid_facet(self, facet):
#    self._raise_if_invalid_facet_name(facet)
#    #self._raise_if_invalid_facet_value(facet)
#
#
#  def _raise_if_invalid_facet_name(self, facet):
#    if facet[0] not in \
#      self.command_processor.get_all_field_names_good_for_faceting():
#        raise path_exception.PathException(
#          'Invalid facet name: {0}'.format(facet[0]))
#
#
#  def _raise_if_invalid_facet_value(self, unapplied_facet_counts, facet):
#    for facet_value in unapplied_facet_counts[facet[0]]['values']:
#      if facet_value[0] == facet[1]:
#        return
#    raise path_exception.PathException(
#      'Invalid facet value: {0}'.format(facet[1]))
#
#
#  def _is_error_file_alternative(self, path):
#    if len(path) <= 1:
#      return False
#    try:
#      self.get_directory(path[:-1])
#    except path_exception.PathException as e:
#      return True
#    return False
#
#
#  def _get_applied_facets(self, path_facets):
#    if self._is_path_to_undefined_facet(path_facets):
#      return path_facets[:-1]
#    else:
#      return path_facets
#
#
#  def _is_path_to_undefined_facet(self, path_facets):
#    return len(path_facets) and path_facets[-1][1] is None
#
#
#  def _get_last_element_facet_name(self, path_facets):
#    return path_facets[-1][0]
#
#
#  def _get_last_element_facet_value(self, path_facets):
#    return path_facets[-1][1]
#
#
#  def _get_facet_values(self, unapplied_facet_counts, facet_name):
#    try:
#      return [directory_item.DirectoryItem(self.facet_path_formatter
#        .decorate_facet_value(u[0]))
#          for u in unapplied_facet_counts[facet_name]['values']]
#    except KeyError:
#      raise path_exception.PathException(
#        'Invalid facet name: {0}'.format(facet_name))
#
#
#  def _get_unapplied_facets(self, unapplied_facet_counts):
#    return [directory_item.DirectoryItem(self.facet_path_formatter.
#      decorate_facet_name(f))
#        for f in sorted(unapplied_facet_counts)]
#
#
#  def _directory_items_from_science_objects(self, sci_obj):
#    return [directory_item.DirectoryItem(s['pid'])
#            for s in sci_obj]
#
#
##    facet_counts = self.query_engine.unapplied_facet_names_with_value_counts(facets)
##    for facet_count in facet_counts:
##      facet_name = self.facet_path_parser.decorate_facet_name(facet_count[0])
##      dir.append(directory_item.DirectoryItem(facet_name, facet_count[1], True))
##
##    # def append_facet_value_selection_directories(self, dir, objects, facets, facet_name):
##    facet_value_counts = self.query_engine.count_matches_for_unapplied_facet(objects, facets, facet_name)
##    for facet_value_count in facet_value_counts:
##      facet_value = self.facet_path_parser.decorate_facet_value(facet_value_count[0])
##      dir.append(directory_item.DirectoryItem(facet_value, facet_value_count[1], True))
##
##    # def append_objects_matching_facets(self, dir, facets):
##    objects = self.query_engine.search_and(facets)
##    dir.extend([directory_item.DirectoryItem(o[0], 123) for o in objects])
#
#    #facets = self.facet_path_parser.undecorate_facets(path)
#    #if self.facet_path_parser.dir_contains_facet_names(path):
#    #  return self.resolve_dir_containing_facet_names(path, facets)
#    #if self.facet_path_parser.dir_contains_facet_values(path):
#    #  return self.resolve_dir_containing_facet_values(path, facets)
#    #if self.n_path_components_after_facets(path) == 1:
#    #  return self.resolve_package_dir(path)
#    #return self.invalid_directory_error()
#
#
#  def _is_undefined_facet(self, facet):
#    return self._is_facet_name_or_value(facet[0]) and facet[1] is None
#
#
##  def append_facet_directories(dir, facet_section):
##    facets = self.facet_path_parser.undecorate_facets(facet_section)
##
##
##  def append_dir_containing_facet_names(self, dir, path, facets):
##    self.append_facet_name_selection_directories(dir, facets)
##    self.append_objects_matching_facets(dir, facets)
##
##
##  def append_dir_containing_facet_values(self, dir, path, facets):
##    dir = directory.Directory()
##    facet_name = self.facet_path_parser.undecorated_tail(path)
##    objects = self.query_engine.search_and(facets)
##    self.append_facet_value_selection_directories(dir, objects, facets,
##                                                  facet_name)
##    dir.extend([directory_item.DirectoryItem(o[0], 123) for o in objects])
#
#
##  def append_facet_name_selection_directories(self, dir, facets):
##    facet_counts = self.query_engine.unapplied_facet_names_with_value_counts(facets)
##    for facet_count in facet_counts:
##      facet_name = self.facet_path_parser.decorate_facet_name(facet_count[0])
##      dir.append(directory_item.DirectoryItem(facet_name, facet_count[1], True))
##
##
##  def append_facet_value_selection_directories(self, dir, objects, facets, facet_name):
##    facet_value_counts = self.query_engine.count_matches_for_unapplied_facet(objects, facets, facet_name)
##    for facet_value_count in facet_value_counts:
##      facet_value = self.facet_path_parser.decorate_facet_value(facet_value_count[0])
##      dir.append(directory_item.DirectoryItem(facet_value, facet_value_count[1], True))
##
##
##  def append_objects_matching_facets(self, dir, facets):
##    objects = self.query_engine.search_and(facets)
##    dir.extend([directory_item.DirectoryItem(o[0], 123) for o in objects])
#
#
##  def is_valid_facet_value_for_facet_name(self, facet_name):
##    pass
