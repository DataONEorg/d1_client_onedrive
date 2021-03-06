#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2014 DataONE
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

'''
:mod:`conf`
===========

:Synopsis:
  Sphinx documentation building system configuration.

:Author:
  DataONE (Vieglais, Dahl)
'''

import sys
import os

project = u'DataONE ONEDrive'
copyright = u'2010,2013 Participating institutions in DataONE'

autosummary_generate = True

extensions = [
  'sphinx.ext.autodoc',
  'sphinx.ext.doctest',
  'sphinx.ext.todo',
  'sphinx.ext.graphviz',
  'sphinx.ext.autosummary',
  'sphinx.ext.pngmath',
  'sphinx.ext.ifconfig',
  'sphinx.ext.inheritance_diagram',
  'sphinx.ext.extlinks',
]

source_suffix = '.rst'
master_doc = 'index'
version = None
release = None
exclude_trees = ['_build', '_templates']
pygments_style = 'sphinx'
today_fmt = '%Y-%m-%d'

html_theme = 'dataone'
html_theme_options = {'collapsiblesidebar':'true', 'render_epad_comments':'false'}
html_theme_path = ['../docutils/sphinx_themes', ]
html_logo = '_static/dataone_logo.png'
