#!/usr/bin/env python3
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

import hashlib
import os
from gettext import gettext as _

class checksum():
    def __init__(self):
        self.hash = _('Calculating, please wait...')
        self.progress = 0.0
        self.done = False

    def computemd5(self, file, CHUNK=2**16):
        self._compute(file, hashlib.md5(), CHUNK)

    def computesha1(self, file, CHUNK=2**16):
        self._compute(file, hashlib.sha1(), CHUNK)

    def _compute(self, file, digest, CHUNK):
        self.hash = _('Calculating, please wait...')
        self.progress = 0.0
        self.done = False
        size = os.stat(file).st_size
        total = 0
        with open(file, 'rb') as file_stream:
            while True:
                chunk = file_stream.read(CHUNK)
                if not chunk:
                    break
                digest.update(chunk)
                total += len(chunk)
                self.progress = float(total) / float(size)
        self.progress = 1.0
        self.hash = digest.hexdigest()
        self.done = True
