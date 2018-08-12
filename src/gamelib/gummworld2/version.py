#!/usr/bin/env python

# This file is part of Gummworld2.
#
# Gummworld2 is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Gummworld2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Gummworld2.  If not, see <http://www.gnu.org/licenses/>.

# Compatible: Python 2.7, Python 3.2

"""toolkit.py - Some helper tools for Gummworld2."""

__version__ = '$Id$'
__author__ = 'Gummbum, (c) 2011-2014'

__all__ = ['version', 'vernum']


version = '1.0.0'
vernum = tuple([int(s) for s in (version.split('.'))])


if __name__ == '__main__':
    print(('Version {0}'.format(version)))
    print(('Vernum {0}'.format(vernum)))
