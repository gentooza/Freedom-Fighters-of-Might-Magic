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

"""game_engine.py is the gummworld derived engine class for the ffmm

"""
import sys
import cProfile, pstats



import pygame
from pygame.sprite import Sprite
from pygame.locals import *

import paths
import gummworld2
from gummworld2 import context, data, model, geometry, toolkit, ui,Engine, State, TiledMap, BasicMapRenderer, Vec2d, Statf
from gummworld2.geometry import RectGeometry, CircleGeometry, PolyGeometry

import objects
import ffmm_spatialhash
import utils

class gameInterface(object):
    
   def __init__(self, resolution=(1014, 965)):
      
      self.menubar =  utils.load_png("gui/menubar.png")
      self.minimap = utils.load_png("gui/minimap.png")
      self.sidebar = utils.load_png("gui/sidebar.png")
 
      #position
      self.menubar_rect = self.menubar.get_rect()
      self.minimap_rect = self.minimap.get_rect()
      self.sidebar_rect = self.sidebar.get_rect()

      self.menubar_rect = pygame.Rect(0, 0, 833, 27)
      self.minimap_rect = pygame.Rect(833, 0, 181, 265)
      self.sidebar_rect = pygame.Rect(833, 265, 181, 700)

    #def update(self, dt):


    #def update_mouse_movement(self, pos):
       

   # def update_keyboard_movement(self):
      

   def draw(self,screen):
       pygame.draw.rect(self.menubar,(99, 99, 99), self.menubar_rect, 1)
       pygame.draw.rect(self.minimap,(99, 99, 99), self.minimap_rect, 1)
       pygame.draw.rect(self.sidebar,(99, 99, 99), self.sidebar_rect, 1)
       screen.blit(self.menubar,(0,0))
       screen.blit(self.minimap,(833,0))
       screen.blit(self.sidebar,(833,265))
