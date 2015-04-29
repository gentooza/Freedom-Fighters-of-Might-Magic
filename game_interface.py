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
from gummworld2 import context, data, model, geometry, toolkit, ui,Engine, State, TiledMap, BasicMapRenderer, Vec2d, Statf, View,SubPixelSurface
from gummworld2.geometry import RectGeometry, CircleGeometry, PolyGeometry

import objects
import ffmm_spatialhash
import utils

class gameInterface(object):
    
   def __init__(self, screen):

      #loading images
      self.menubar =  utils.load_png("gui/menubar_.png")
      self.minimap = utils.load_png("gui/minimap.png")
      self.sidebar = utils.load_png("gui/sidebar_.png")
 
      #position, not positioned yet
      self.menubar_rect = self.menubar.get_rect()
      self.minimap_rect = self.minimap.get_rect()
      self.sidebar_rect = self.sidebar.get_rect()
      #setting rectangles
      self.menubar_rect = pygame.Rect(0, 0, 833, 27)
      self.minimap_rect = pygame.Rect(833, 0, 181, 265)
      self.minimap_map_rect = pygame.Rect(850, 8, 152, 205)
      self.sidebar_rect = pygame.Rect(833, 265, 181, 700)
      #creating mini screens from state screen, method obtained from example 10_minimap.py of gummlib2
      self.menubar_screen = View(screen.surface, self.menubar_rect)
      self.minimap_screen = View(screen.surface, self.minimap_rect)
      self.sidebar_screen = View(screen.surface, self.sidebar_rect)

      #minimap
      self.minimap_map = Minimap( self.minimap_map_rect)

    #def update(self, dt):


    #def update_mouse_movement(self, pos):
       

   # def update_keyboard_movement(self):
      

   def draw(self,screen,items):
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
       self.minimap_screen.surface.blit(self.minimap,(0,0))
       self.sidebar_screen.surface.blit(self.sidebar,(0,0))
       #screen.blit(self.menubar,(0,0))
       #screen.blit(self.minimap,(833,0))
       #screen.blit(self.sidebar,(833,265))
       #print("drawing panels!")
       self.minimap_map.draw(items)

class Minimap(object):
    
    def __init__(self, minimap_rect):
        
        # The minimap is a subsurface upon which the whole world is projected.
        self.mini_screen = View(
            State.screen.surface, minimap_rect)
        
        # tiny_rect will be drawn on the minimap to indicate the visible area of
        # the world (the screen, aka camera).
        self.tiny_rect = self.mini_screen.rect.copy()
        size = Vec2d(State.screen.size)
        size.x = float(size.x)
        size.y = float(size.y)
        size = size / State.world.rect.size * self.mini_screen.rect.size
        self.tiny_rect.size = round(size.x), round(size.y)
        
        # A dot represents a full sprite on the minimap. SubPixelSurface is a
        # generated set of antialiased images that give the illusion of movement
        # smaller than one pixel. If we did not do this the dots would have an
        # annoying jerky movement.
        dot = pygame.surface.Surface((1, 1))
        dot.fill(Color('white'))
        self.dot = SubPixelSurface(dot)
        
        # Pre-compute some reusable values.
        mini_screen = self.mini_screen
        mini_surf = mini_screen.surface
        mini_size = mini_screen.rect.size
        self.mini_size = mini_size
        
        full_size = Vec2d(State.world.rect.size)
        full_size.x = float(full_size.x)
        full_size.y = float(full_size.y)
        self.full_size = full_size

    def draw(self, sprite_group):
        mini_screen = self.mini_screen
        mini_surf = mini_screen.surface
        
        # Position the "visible area" tiny_rect, aka camera, within the minimap
        # so we can draw it as a filled rect.
        full_size = self.full_size
        mini_size = self.mini_size
        tiny_pos = State.camera.rect.topleft / full_size * mini_size
        self.tiny_rect.topleft = round(tiny_pos.x), round(tiny_pos.y)
        
        # Draw the minimap...
        mini_screen.clear()
        # Draw the camera area as a filled rect.
        pygame.draw.rect(mini_surf, Color(200, 0, 255), self.tiny_rect)
        # Draw sprites as dots.
        for s in sprite_group:
            pos = s.rect.topleft / full_size * mini_size
            dot = self.dot.at(pos.x, pos.y)
            mini_surf.blit(dot, pos, None, BLEND_RGBA_ADD)
        
        # Draw a border.
        pygame.draw.rect(State.screen.surface, (99, 99, 99), mini_screen.parent_rect.inflate(2, 2), 1)
