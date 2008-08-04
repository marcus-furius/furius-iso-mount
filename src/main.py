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

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import pango
    import gtk
    import gtk.glade
except:
    sys.exit(1)

import globals

class main_window:
    def __init__(self):
        #Set the Glade file
        self.wTree = gtk.glade.XML(globals.application_interface, 'main_window')

if __name__ == "__main__":
    app = main_window()
    gtk.main()