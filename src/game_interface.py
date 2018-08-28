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
from gummworld2 import context, data, model, geometry, toolkit,Engine, State, TiledMap, BasicMapRenderer, Vec2d, View,SubPixelSurface
from gummworld2.geometry import RectGeometry, CircleGeometry, PolyGeometry

import objects
import ffmm_spatialhash
import utils


class gameInterface(object):
    
   def __init__(self, screen, parameters):
      self.parameters =parameters
      #loading images
      self.menubar =  utils.load_png("gui/menubar.png")
      #self.minimap = utils.load_png("gui/minimap.png")
      self.sidebar = utils.load_png("gui/sidebar.png")
      self.sidebar_bott = utils.load_png("gui/sidebar_top.png")

      #hero popup
      self.hpopup = utils.load_png("gui/heropopup.png")
      self.hpopup_screen = None
      self.shownhpoup = False
      
      #standar popup
      self.popup =  None 
      self.popup_screen = None
      self.shownpopup = False
 
      #position, not positioned yet
      self.menubar_rect = self.menubar.get_rect()
      #self.minimap_rect = self.minimap.get_rect()
      self.sidebar_rect = self.sidebar.get_rect()
      #setting rectangles
      screen_resolution = self.parameters["resolution"]
      self.menubar_rect = pygame.Rect(2, 0, screen_resolution[0]-183, 27)
      self.minimap_rect = pygame.Rect(screen_resolution[0]-183, 0, 183, 265)
      self.minimap_map_rect = pygame.Rect(screen_resolution[0]-160, 10, 150, 205)
      self.sidebar_rect = pygame.Rect(screen_resolution[0]-179, 0, 179, screen_resolution[1])
      #creating mini screens from state screen, method obtained from example 10_minimap.py of gummlib2
      self.menubar_screen = View(screen.surface, self.menubar_rect)
      #self.minimap_screen = View(screen.surface, self.minimap_rect)
      self.sidebar_screen = View(screen.surface, self.sidebar_rect)
      
      #minimap
      self.minimap_map = Minimap( self.minimap_map_rect)

      #hero popup
      self.name_font = pygame.font.SysFont('verdana',16)
      self.name_font.set_bold(True)
      self.atributes_font = pygame.font.SysFont('verdana',14)      

   def draw(self,screen,items):
       #clearing
       self.menubar_screen.clear()
       #self.minimap_screen.clear()
       self.sidebar_screen.clear()
       #drawing
       pygame.draw.rect(screen.surface,(99, 99, 99), self.menubar_rect, 1)
       #pygame.draw.rect(screen.surface,(99, 99, 99), self.minimap_rect, 1)
       pygame.draw.rect(screen.surface,(99, 99, 99), self.sidebar_rect, 1)
       #blitting panels
       self.menubar_screen.surface.blit(self.menubar,(0,0))
       #self.minimap_screen.surface.blit(self.minimap,(0,0))
       self.sidebar_screen.surface.blit(self.sidebar,(0,0))
       self.sidebar_screen.surface.blit(self.sidebar_bott,(0,self.parameters["resolution"][1]-300))
       #screen.blit(self.menubar,(0,0))
       #screen.blit(self.minimap,(833,0))
       #screen.blit(self.sidebar,(833,265))
       #print("drawing panels!")
       self.minimap_map.draw(items)
       #do we draw the hero popup?? 
       if(self.shownhpoup):
           if(self.hpopup_screen):
              self.hpopup_screen.clear()
              self.himage_screen.clear()
           pygame.draw.rect(screen.surface,(99, 99, 99), self.hpopup_rect, 1)
           self.hpopup_screen.surface.blit(self.hpopup,(0,0))
           pygame.draw.rect(screen.surface,(99, 99, 99), self.himage_rect, 1)
           self.himage_screen.surface.blit(self.himage,(0,0))
           #pygame.draw.rect(screen.surface,(0, 0, 0), self.hname_rect, 0)
           self.hname_screen.surface.blit(self.hname,(0,0))
           self.hattack_screen.surface.blit(self.hattack,(0,0))
           self.hdef_screen.surface.blit(self.hdef,(0,0))
           self.hpower_screen.surface.blit(self.hpower,(0,0))
           self.hknow_screen.surface.blit(self.hknow,(0,0))

   def createhpopup(self,screen,pos,hero):
       self.shownhpoup = True
       if (self.hpopup_screen):
          self.hpopup_screen.clear()

       self.hpopup_x = pos[0]
       self.hpopup_y = pos[1]
       self.hpopup_rect = pygame.Rect(self.hpopup_x,self.hpopup_y, 181, 68)
       pygame.draw.rect(screen.surface,(99, 99, 99), self.hpopup_rect, 1)
       self.hpopup_screen = View(screen.surface, self.hpopup_rect)
       self.hpopup_screen.surface.blit(self.hpopup,(0,0))

       #content & hero attributes!
       attributes = hero.attr
       ##portrait
       image =  utils.load_png("portraits/" + attributes['portrait']+'.png')
       self.himage = utils.load_png('portraits/no_portrait.png')
       self.himage = pygame.transform.scale(image,(66,66))
       self.himage_rect = pygame.Rect(self.hpopup_x+6,self.hpopup_y+1, 66, 66)
       pygame.draw.rect(self.hpopup_screen.surface,(99, 99, 99), self.himage_rect, 1)
       self.himage_screen = View(screen.surface, self.himage_rect)
       self.himage_screen.surface.blit(self.himage,(0,0))
       ##Name
       self.hname = self.name_font.render(attributes['name'],True,(230,230,230))
       self.hname_rect = pygame.Rect(self.hpopup_x+80,self.hpopup_y+1, 90, 20)
       self.hname_screen = View(screen.surface, self.hname_rect)
       self.hname_screen.surface.blit(self.hname,(0,0))
       ##attributes
       self.hattack = self.atributes_font.render("A: " + str(attributes['attack']),True,(220,220,220))
       self.hattack_rect = pygame.Rect(self.hpopup_x+85,self.hpopup_y+22, 40, 15)
       self.hattack_screen = View(screen.surface, self.hattack_rect)
       self.hattack_screen.surface.blit(self.hattack,(0,0))

       self.hdef = self.atributes_font.render("D: " + str(attributes['deffense']),True,(220,220,220))
       self.hdef_rect = pygame.Rect(self.hpopup_x+125,self.hpopup_y+22, 40, 15)
       self.hdef_screen = View(screen.surface, self.hdef_rect)
       self.hdef_screen.surface.blit(self.hdef,(0,0))

       self.hpower = self.atributes_font.render("P: " + str(attributes['magic_p']),True,(220,220,220))
       self.hpower_rect = pygame.Rect(self.hpopup_x+85,self.hpopup_y+40, 40, 15)
       self.hpower_screen = View(screen.surface, self.hpower_rect)
       self.hpower_screen.surface.blit(self.hpower,(0,0))

       self.hknow = self.atributes_font.render("K: " + str(attributes['magic_k']),True,(220,220,220))
       self.hknow_rect = pygame.Rect(self.hpopup_x+125,self.hpopup_y+40, 40, 15)
       self.hknow_screen = View(screen.surface, self.hknow_rect)
       self.hknow_screen.surface.blit(self.hknow,(0,0))

   def erasehpopup(self):
       self.shownhpoup = False
       if(self.hpopup_screen):  
          self.hpopup_screen.clear()
          self.himage_screen.clear() 
          
   def createpopup(self,screen,pos,message,itype):
       self.shownpopup = True
       if (self.popup_screen):
          self.popup_screen.clear()

       self.popup = popup(self.popup_screen,screen,pos,message,itype)
       

       self.popup_rect = pygame.Rect(pos[0],pos[1], self.popup.width, self.popup.height)
       pygame.draw.rect(screen.surface,(99, 99, 99), self.popup_rect, 1)
       self.popup_screen = View(screen.surface, self.popup_rect)
       #construction
       self.popup_screen.surface.blit(self.popup,(0,0))

       #content & hero attributes!
       attributes = hero.attr
       ##portrait
       image =  utils.load_png("portraits/" + attributes['portrait']+'.png')
       self.himage = utils.load_png('portraits/no_portrait.png')
       self.himage = pygame.transform.scale(image,(66,66))
       self.himage_rect = pygame.Rect(self.hpopup_x+6,self.hpopup_y+1, 66, 66)
       pygame.draw.rect(self.hpopup_screen.surface,(99, 99, 99), self.himage_rect, 1)
       self.himage_screen = View(screen.surface, self.himage_rect)
       self.himage_screen.surface.blit(self.himage,(0,0))
       ##Name
       self.hname = self.name_font.render(attributes['name'],True,(230,230,230))
       self.hname_rect = pygame.Rect(self.hpopup_x+80,self.hpopup_y+1, 90, 20)
       self.hname_screen = View(screen.surface, self.hname_rect)
       self.hname_screen.surface.blit(self.hname,(0,0))
       ##attributes
       self.hattack = self.atributes_font.render("A: " + str(attributes['attack']),True,(220,220,220))
       self.hattack_rect = pygame.Rect(self.hpopup_x+85,self.hpopup_y+22, 40, 15)
       self.hattack_screen = View(screen.surface, self.hattack_rect)
       self.hattack_screen.surface.blit(self.hattack,(0,0))

       self.hdef = self.atributes_font.render("D: " + str(attributes['deffense']),True,(220,220,220))
       self.hdef_rect = pygame.Rect(self.hpopup_x+125,self.hpopup_y+22, 40, 15)
       self.hdef_screen = View(screen.surface, self.hdef_rect)
       self.hdef_screen.surface.blit(self.hdef,(0,0))

       self.hpower = self.atributes_font.render("P: " + str(attributes['magic_p']),True,(220,220,220))
       self.hpower_rect = pygame.Rect(self.hpopup_x+85,self.hpopup_y+40, 40, 15)
       self.hpower_screen = View(screen.surface, self.hpower_rect)
       self.hpower_screen.surface.blit(self.hpower,(0,0))

       self.hknow = self.atributes_font.render("K: " + str(attributes['magic_k']),True,(220,220,220))
       self.hknow_rect = pygame.Rect(self.hpopup_x+125,self.hpopup_y+40, 40, 15)
       self.hknow_screen = View(screen.surface, self.hknow_rect)
       self.hknow_screen.surface.blit(self.hknow,(0,0))

   def erasepopup(self):
       self.shownpopup = False
       if(self.popup_screen):  
          self.popup_screen.clear()
       if(self.popup):
           popup.destroy()

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

'''generic popup class, giving size for resolutionc hanges,
the message text,
and the popup type:
0 -> ok popup
1 -> ok,cancel popup'''

class popup(object):
    def __init__(self,pos,smessage,itype):
        self.shownhpoup = False
        self.background = utils.load_png("gui/wood_popup.png") #orig resolution: 181x63
        self.side = utils.load_png("gui/popup_side_medium.png") #orig resolution: 10x250
        self.top = utils.load_png("gui/popup_top.png") #orig resolution: 352x10
        
        self.width = 352
        self.height = 250
        