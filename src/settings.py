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

''':mod:`settings`
==================

:Synopsis:
 - User configurable settings for ONEDrive.
:Author: DataONE (Dahl)
'''

# Stdlib.
import logging
import os
import sys

# D1.
import d1_common.const


# Create absolute path from path that is relative to the module from which
# the function is called.
def make_absolute(p):
  return os.path.join(os.path.abspath(os.path.dirname(__file__)), p)


################################################################################
# User configurable settings.
################################################################################

# DataONE maintains several instances of the DataONE infrastructure, called
# environments. The production environment is used by the general public. Other
# environments are used by software developers for testing and debugging of new
# components. This setting controls to which environment ONEDrive connects.
#DATAONE_ROOT = d1_common.const.URL_DATAONE_ROOT # (recommended, production)
DATAONE_ROOT = 'https://cn-dev.dataone.org/cn'
#DATAONE_ROOT = 'https://cn-sandbox.dataone.org/cn'
#DATAONE_ROOT = 'https://cn-stage.dataone.org/cn/'


# Select the mountpoint for ONEDrive. The mountpoint is the folder in the local
# filesystem in which the ONEDrive filesystem appears. The default is to mount
# the drive in a folder named "one", in the same folder as the onedrive.py file.
# If the mountpoint is set to a folder that already contains files and folders,
# those files and folders become temporarily invisible while ONEDrive is
# running.
MOUNTPOINT = make_absolute('one') # (default, relative path)
#MOUNTPOINT = '/mnt/onedrive' # (example, absolute path)


# This value determines how many folders that can be held simultaneously
# in the folder cache. The number represents a tradeoff between performance
# and memory footprint. A higher number gives better performance and a larger
# memory footprint. The default is 100. A value below 10 is not recommended.
DIRECTORY_CACHE_SIZE = 100


# This value determines how many science objects that can be held simultaneously
# in the object cache. The default is 10.
OBJECT_CACHE_SIZE = 10


################################################################################
# Settings below this line are not intended to be modified by the user.
################################################################################

# Debug mode.
# True: Turn on verbose logging and various other debugging facilities.
# False: Log only error messages (for normal use, default)
DEBUG = True


# The facet name and value decorates select the characters which denote
# facet names and facet values in filesystem paths where a faceted search
# is supported.
FACET_NAME_DECORATOR = '@' # (default is '@')
FACET_VALUE_DECORATOR = '#' # (default is '#')


# Type of connection to use when connecting to the Solr server.
# True: A persistent connection is maintained (default)
# False: A new connection is created each time a query is sent
SOLR_PERSIST_CONNECTION = True


# Objects that match this query are filtered out of all search results.
# None: No filter (default)
SOLR_QUERY_FILTER = None


# FOREGROUND:
# During normal use, the FUSE driver will go into the background, causing the
# onedrive.py command to return immediately. Setting this value to True
# causes the driver to remain in the foreground.
# True: Run driver in foreground (for debugging)
# False: Run driver in background (for normal use, default)

# NOTHREADS:
# During normal use, the FUSE drive will use multiple threads to improve
# performance. Settings this value to True causes the driver to run everything
# in a single thread.
# True: Do not create multiple threads (for debugging)
# False: Create multiple threads (for normal use)

# LOG_LEVEL:
# Set how serious a log message or error must be before it is logged.
# Choices are: DEBUG, INFO, WARNING, ERROR, CRITICAL and NOTSET.

# SOLR_DEBUG_LEVEL:
# Setting this value to 1 causes the Solr client to output debug information.
# 1: Turn on debug output in the Solr Client (for debugging)
# 0: Turn off debug output (for normal use)

if DEBUG:
  FOREGROUND = True
  NOTHREADS = True
  LOG_LEVEL = 'DEBUG'
  SOLR_DEBUG_LEVEL = 1
else:
  FOREGROUND = False
  NOTHREADS = False
  LOG_LEVEL = 'WARNING'
  SOLR_DEBUG_LEVEL = 0


# Path to the file containing the icon that is displayed for ONEDrive when
# accessing the filesystem through a GUI.
ICON = make_absolute(os.path.join('impl', 'd1.icon'))


# TODO: Describe these.

O_ACCMODE = 3
PATHELEMENT_SAFE_CHARS = ' @$,~*&'
ITERATOR_PER_FETCH = 400
FACET_REFRESH = 20 #seconds between cache refresh for facet values
OSX_SPECIAL = ['._', '.DS_Store', ]
TSTAMP=1280664000.0 #2010-08-01T08:00:00
