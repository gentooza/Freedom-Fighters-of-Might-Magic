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
from gummworld2 import context, data, model, geometry, toolkit, ui,Engine, State, TiledMap, BasicMapRenderer, Vec2d, Statf, View
from gummworld2.geometry import RectGeometry, CircleGeometry, PolyGeometry

import objects
import ffmm_spatialhash
import utils

class gameInterface(object):
    
   def __init__(self, screen):

      #loading images
      self.menubar =  utils.load_png("gui/menubar.png")
      self.minimap = utils.load_png("gui/minimap.png")
      self.sidebar = utils.load_png("gui/sidebar.png")
 
      #position, not positioned yet
      self.menubar_rect = self.menubar.get_rect()
      self.minimap_rect = self.minimap.get_rect()
      self.sidebar_rect = self.sidebar.get_rect()
      #setting rectangles
      self.menubar_rect = pygame.Rect(0, 0, 833, 27)
      self.minimap_rect = pygame.Rect(833, 0, 181, 265)
      self.sidebar_rect = pygame.Rect(833, 265, 181, 700)
      #creating mini screens from state screen, method obtained from example 10_minimap.py of gummlib2
      self.menubar_screen = View(screen.surface, self.menubar_rect)
      self.minimap_screen = View(screen.surface, self.menubar_rect)
      self.sidebar_screen = View(screen.surface, self.menubar_rect)

    #def update(self, dt):


    #def update_mouse_movement(self, pos):
       

   # def update_keyboard_movement(self):
      

   def draw(self,screen):
       #clearing
       self.menubar_screen.clear()
       self.minimap_screen.clear()
       self.sidebar_screen.clear()
       #drawing
       pygame.draw.rect(screen.surface,(99, 99, 99), self.menubar_rect, 1)
       pygame.draw.rect(screen.surface,(99, 99, 99), self.minimap_rect, 1)
       pygame.draw.rect(screen.surface,(99, 99, 99), self.sidebar_rect, 1)
       #blitting panels
       self.menubar_screen.surface.blit(self.menubar,(0,0))
       self.minimap_screen.surface.blit(self.minimap,(833,0))
       self.sidebar_screen.surface.blit(self.sidebar,(833,265))
       #screen.blit(self.menubar,(0,0))
       #screen.blit(self.minimap,(833,0))
       #screen.blit(self.sidebar,(833,265))
       print("drawing panels!")
