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

try:
    import sys
    from src import paths
    import start
    import config
except ImportError as err:
    print("couldn't load module. %s" % (err))
    sys.exit(2)

# INTILIALIZATION
myConfiguration = config.Config_Manager("config.cfg")

FFMM = start.app(myConfiguration.parameters)
# DISPLAY
FFMM.setDisplay()

# GAME RUN!!
FFMM.run()






