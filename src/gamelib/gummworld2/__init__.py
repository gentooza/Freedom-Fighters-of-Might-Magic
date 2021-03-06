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

"""
Gummworld2 is designed as a pygame framework for a scrolling game, where
the map is larger than the display. It emphasizes performance.
"""

"""__init__.py - Package initializer for Gummworld2."""

import os
import sys


__version__ = '$Id: __init__.py 407 2013-08-12 15:11:30Z stabbingfinger@gmail.com $'
__author__ = 'Gummbum, (c) 2011-2014'


# Unbuffered IO for Python 2.6, 2.7, and 3.x
try:
    buf_arg = 0
    if sys.version_info[0] == 3:
        buf_arg = 1
        os.environ['PYTHONUNBUFFERED'] = '1'
    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'a', buf_arg)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'a', buf_arg)
except Exception as e:
    print('gummworld2.__init__: {}'.format(e))
    print('gummworld2.__init__: non-fatal: could not enable unbuffered stdio')

del os, sys


import pygame
pygame.init()

del pygame

__all__ = [
    'context',
    'model',
    'data',
    'hudlight',
    'geometry',
    'pygametext',
    'pygame_utils',
    'popup_menu',
    'state',
    'toolkit',
    'basicmap',
    'tiledmap',
    'supermap',
    'version',
    'Vec2d',
    'State',
    'Context',
    'SpatialHash',
    'Screen', 'View',
    'BasicMap', 'BasicLayer',
    'BasicMapRenderer',
    'TiledMap',
    'SuperMap', 'MapHandler',
    'Camera',
    'GameClock',
    'SubPixelSurface',
    'PopupMenu',
    # 'HUD', 'Stat', 'Statf',
    'HUD', 'HUDBadArgs', 'HUDNameNotFound', 'HUDNameExists', 'set_font_template',
    'run', 'Engine', 'NO_WORLD', 'SIMPLE_WORLD',
]

from gummworld2 import version
if __debug__:
    print('gummworld2 v{0} loading...'.format(version.version))

# Classes
from .vec2d import Vec2d
from .state import State
from .context import Context
from .spatialhash import SpatialHash

# the following creates a separate namespace, don't do it.
#from tiledtmxloader.tiledtmxloader import TileMap, TileMapParser
#from tiledtmxloader.helperspygame import ResourceLoaderPygame, RendererPygame

from .screen import Screen, View
from .basicmap import BasicMap, BasicLayer
from .basicmaprenderer import BasicMapRenderer
from .tiledmap import TiledMap
from .supermap import SuperMap, MapHandler
from .camera import Camera
from .gameclock import GameClock
from .hudlight import HUD, set_font_template
from .subpixel import SubPixelSurface
from .popup_menu import PopupMenu

from .engine import run, Engine, NO_WORLD, SIMPLE_WORLD

if __debug__:
    print('gummworld2 v{0} loaded'.format(version.version))
