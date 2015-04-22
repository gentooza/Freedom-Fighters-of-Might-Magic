#!/usr/bin/env python

#
#  Freedom Fighters of Might & Magic
#
#  Copyright 2014-2015 by it's authors. 
#
#  Some rights reserved. See COPYING, AUTHORS.
#  This file may be used under the terms of the GNU General Public
#  License version 3.0 as published by the Free Software Foundation
#  and appearing in the file COPYING included in the packaging of
#  this file.
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

"""ffmm_spatialhash.py - Freedom Fighters of Might & Magic derived High performance spatial hash for spatial
partitioning and fast collision detection. from gummworld2
"""



import time
from math import ceil
from weakref  import WeakKeyDictionary

import pygame
from pygame.locals import Rect

import gummworld2
from gummworld2 import *


class game_SpatialHash(SpatialHash):
   
    def get_cell_by_grid(self,col,row):
        cols = self.cols
        cell_id = row + col*cols
        
        return self.get_cell(cell_id)
