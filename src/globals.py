#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This file is part of PyFuriusIsoMount. Copyright 2008 Dean Harris (marcus_furius@hotmail.com)
#
#    PyFuriusIsoMount is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyFuriusIsoMount is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyFuriusIsoMount.  If not, see <http://www.gnu.org/licenses/>.

import os.path

# Directories
home_directory = os.path.expanduser('~')
source_directory = os.path.join(os.path.dirname(__file__))
resource_directory = os.path.join(source_directory, '..', 'res')
image_directory = os.path.join(source_directory, '..', 'pix')
document_directory = os.path.join(source_directory, '..', 'doc')

#files
application_interface = os.path.join(resource_directory, 'main_window.glade')