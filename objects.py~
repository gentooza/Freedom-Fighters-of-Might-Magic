#! /usr/bin/env python

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
#


try:
  import sys
  import random
  import math
  import os
  import getopt
  import pygame
  import pyganim
  import utils
  import paths
  import gummworld2
  from gummworld2 import Engine, State, BasicMap, SubPixelSurface, View, Vec2d
  from gummworld2.geometry import RectGeometry, CircleGeometry, PolyGeometry
  from gummworld2 import context, model, spatialhash, toolkit
  from socket import *
  from pygame.locals import *
except ImportError as err:
  print("couldn't load module. %s" % (err))
  sys.exit(2)


# define some constants
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

WALKRATE = 4
RUNRATE = 12

#attributes = {'faction' :None,'portrait':None,'attack':None,'deffense':None,'magic_p':None,'magic_k':None}
katrin =  {'faction' : 'human','portrait': 'katrin','attack':2,'deffense':2,'magic_p':1,'magic_k':1}

class ourHero(object):

 def __init__(self,image,path,map_pos, screen_pos):
   self._position = Vec2d(0,0) # x e y? funciones de gummworld2
   self.movement = 0
   #self.direction = DOWN
   self.dir = Vec2d(0.0, 0.0)
   #images loading
   front_image = path + '/' + image + '-se-bob1.png'
   self.front_standing = utils.load_png(front_image)
   self.right_standing = utils.load_png(front_image)
   #self.rect = self.front_standing.get_rect()

   self.back_standing = pygame.transform.flip(self.front_standing, True, False) 
   self.left_standing = pygame.transform.flip(self.right_standing, True, False) 
   self.playerWidth, self.playerHeight = self.front_standing.get_size()

   #animation loading
   self.animTypes = '-se-run -n-run -s-run -sw-run'
   self.animObjs = {}
   self.imagesAndDurations = [('data/horseman/horseman-se-run%s.png' % (str(num)), 0.1) for num in range(1,8)]
   self.animObjs['-se-run'] = pyganim.PygAnimation(self.imagesAndDurations)

   # create the right-facing sprites by copying and flipping the left-facing sprites
   self.animObjs['-n-run'] = self.animObjs['-se-run'].getCopy()
   self.animObjs['-s-run'] = self.animObjs['-se-run'].getCopy()
   self.animObjs['-s-run'].flip(True, False)
   self.animObjs['-s-run'].makeTransformsPermanent()
   self.animObjs['-sw-run'] = self.animObjs['-se-run'].getCopy()
   self.animObjs['-sw-run'].flip(True, False)
   self.animObjs['-sw-run'].makeTransformsPermanent()

   #self.image = self.animObjs['-se-run'].getCurrentFrame()
   self.image = self.image_stand = self.front_standing
   self.rect = self.image.get_rect()

   #move conductor
   self.moveConductor = pyganim.PygConductor(self.animObjs)
   #start direction
   #self.direction = DOWN
   self.x = screen_pos[0]
   self.y = screen_pos[1]
   self.screen_position = screen_pos
   self.position = map_pos

   #game attributes
   self.team = 0
   self.attr = 0

 def getpoints(self):
    r = self.rect
    return r.topleft, r.topright, r.bottomright, r.bottomleft
 points = property(getpoints)

 def getposition(self):
    """GOTCHA: Something like "rect_geom.position.x += 1" will not do what
    you expect. That operation does not update the rect instance variable.
    Instead use "rect_geom.position += (1,0)".
    """
    return self._position

 def setposition(self, val):
    p = self._position
    p.x, p.y = val
    self.rect.center = round(p.x), round(p.y)
 position = property(getposition, setposition)


 def move(self,direction):
   self.moveConductor.play() # calling play() while the animation objects are already playing is okay; in that case play() is a no-op
   self.dir = direction
   self.movement = 1

 def stopMove(self,direction):
   self.moveConductor.stop() # calling stop() while the animation objects are already stopped is okay; in that case stop() is a no-op
   self.dir = direction
   self.movement = 0
		 
 def getRect(self):
   return self.rect

 def update(self): #no screen
   self.x = self.position[0]
   self.y = self.position[1]
   if self.movement:
      #self.moveConductor.play() # calling play() while the animation objects are already playing is okay; in that case play() is a no-op
      if self.dir.x > 0:
         #self.animObjs['-n-run'].blit(screen, (self.x, self.y))
         self.image = self.animObjs['-se-run'].getCurrentFrame()
         self.image_stand = self.right_standing
      else:
         #self.animObjs['-s-run'].blit(screen, (self.x, self.y))
         self.image = self.animObjs['-sw-run'].getCurrentFrame()
         self.image_stand = self.left_standing
   else:
         self.image = self.image_stand
         #screen.blit(self.image, (self.x, self.y))
 
   self.rect = self.image.get_rect()
   self.rect.center=self.x, self.y

'''faction class, with it's heroes, places, resources, etc.'''
class faction(object):
 def __init__(self, faction,color):
   self.color = color
   self.faction = faction
  
class arrow_step(object):

 def __init__(self,image,path,map_pos):
   self._position = Vec2d(0,0) # x e y? funciones de gummworld2
   self.movement = 0
   #self.direction = DOWN
   self.dir = Vec2d(0.0, 0.0)
   #images loading
   arrow_image = path + '/'+ image
   self.right_arrow = utils.load_png(arrow_image)
   self.image = self.right_arrow

   self.rect = self.right_arrow.get_rect()

   #start direction
   #self.direction = DOWN
   self.x = map_pos[0]
   self.y = map_pos[1]
   self.position = map_pos

 def getpoints(self):
    r = self.rect
    return r.topleft, r.topright, r.bottomright, r.bottomleft
 points = property(getpoints)

 def getposition(self):
    """GOTCHA: Something like "rect_geom.position.x += 1" will not do what
    you expect. That operation does not update the rect instance variable.
    Instead use "rect_geom.position += (1,0)".
    """
    return self._position

 def setposition(self, val):
    p = self._position
    p.x, p.y = val
    self.rect.center = round(p.x), round(p.y)
 position = property(getposition, setposition)
		 
 def getRect(self):
   return self.rect

 def stopMove(self,direction):
   self.dir = direction
   self.movement = 0


	

