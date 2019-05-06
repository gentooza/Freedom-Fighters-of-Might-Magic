#!/usr/bin/env python3
#
# This file is part of Freedom Fighters of Might & Magic
#
# Copyright 2014-2019, Joaquín Cuéllar <joa.cuellar (at) riseup (dot) net>
#
# Freedom Fighters of Might & Magic is free software:
# you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Freedom Fighters of Might & Magic is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Freedom Fighters of Might & Magic.
# If not, see <https://www.gnu.org/licenses/>.

"""paths.py - Path setup for FFMM.

Import this at the start of your program to augment the python library path.
"""


import os
import sys

progname = sys.argv[0]
progdir = os.path.dirname(progname)
sys.path.insert(0, os.path.normpath(os.path.join(progdir,'src')))
sys.path.insert(0, os.path.normpath(os.path.join(progdir,'src','gamelib')))
sys.path.insert(0, os.path.normpath(os.path.join(progdir,'src','pgu')))
sys.path.insert(0, os.path.normpath(os.path.join(progdir,'src','AI')))

from gummworld2 import data

data.set_data_dir(os.path.normpath(os.path.join(progdir,'data')))