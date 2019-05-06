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
  import random
  import math
  import os
  import getopt
  import pygame
  import pyganim
  import utils
  import paths
  from gummworld2 import Vec2d
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

 def __init__(self,image,path,map_pos, screen_pos,team_num):
   self._position = Vec2d(0,0) # x e y? funciones de gummworld2
   self.movement = 0
   #self.direction = DOWN
   self.dir = Vec2d(0.0, 0.0)
   #images loading
   front_image = path + '/' + image + '-se-bob1.png'
   self.front_standing = utils.load_png(front_image)
   self.right_standing = utils.load_png(front_image)
   #team flag
   self.flag,flag_colour = utils.load_flag(team_num)
   
   #self.rect = self.front_standing.get_rect()

   self.back_standing = pygame.transform.flip(self.front_standing, True, False) 
   self.left_standing = pygame.transform.flip(self.right_standing, True, False) 
   self.playerWidth, self.playerHeight = self.front_standing.get_size()

   ##animation loading
   self.animTypes = '-se-run -n-run -s-run -sw-run'
   self.animObjs = {}
   self.imagesAndDurations = [('data/horseman/horseman-se-run%s.png' % (str(num)), 0.1) for num in range(1,8)]
   self.animObjs['-se-run'] = pyganim.PygAnimation(self.imagesAndDurations)
   #flag
   self.flagsID = [("data/flags/%s-%s.png" % (flag_colour,str(num)), 0.1) for num in range(1,4)] 
   self.animFlags  = pyganim.PygAnimation(self.flagsID)
   # create the right-facing sprites by copying and flipping the left-facing sprites
   self.animObjs['-n-run'] = self.animObjs['-se-run'].getCopy()
   self.animObjs['-s-run'] = self.animObjs['-se-run'].getCopy()
   self.animObjs['-s-run'].flip(True, False)
   self.animObjs['-s-run'].makeTransformsPermanent()
   self.animObjs['-sw-run'] = self.animObjs['-se-run'].getCopy()
   self.animObjs['-sw-run'].flip(True, False)
   self.animObjs['-sw-run'].makeTransformsPermanent()

   #self.image = self.animObjs['-se-run'].getCurrentFrame()
   self.hero_image = self.image_stand = self.front_standing
   self.rect = self.hero_image.get_rect()
   self.image = pygame.Surface((72,72))
   self.image.set_colorkey(0)

   self.image.blit(self.flag,(2,-10))
   self.image.blit(self.hero_image,(-5,-5))

   #move conductor
   self.moveConductor = pyganim.PygConductor(self.animObjs)
   self.moveFlags = pyganim.PygConductor(self.animFlags)
   self.moveFlags.play()
   #start direction
   #self.direction = DOWN
   self.x = screen_pos[0]
   self.y = screen_pos[1]
   self.screen_position = screen_pos
   self.position = map_pos

   #game attributes
   self.team = team_num
   self.attr = 0
   self.saved_path = None
   self.move_points = 1
   self.remaining_movement = 0
   self.strength = 1
   
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
   self.moveFlags.play()
   self.dir = direction
   self.movement = 1

 def stopMove(self,direction):
   self.moveConductor.stop() # calling stop() while the animation objects are already stopped is okay; in that case stop() is a no-op
   self.moveFlags.play()
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
         self.hero_image = self.animObjs['-se-run'].getCurrentFrame()
         self.image_stand = self.right_standing
      else:
         #self.animObjs['-s-run'].blit(screen, (self.x, self.y))
         self.hero_image = self.animObjs['-sw-run'].getCurrentFrame()
         self.image_stand = self.left_standing
   else:
         self.hero_image = self.image_stand
         #screen.blit(self.image, (self.x, self.y))
 
   self.rect = self.image.get_rect()
   self.rect.center=self.x, self.y
   self.flag = self.animFlags.getCurrentFrame()
   #print('animating flag')
   self.image = pygame.Surface((72,72))
   self.image.set_colorkey(0)
   self.image.blit(self.flag,(2,-10))
   self.image.blit(self.hero_image,(-5,-5))
   
#game dynamics procedures
 def setStrength(self,value):
     self.strength = value
   #self.flag =utils.load_png('flags/red-1.png')# self.animFlags.getCurrentFrame()
  
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
   
class creature(object):

 def __init__(self,image,path,map_pos, screen_pos):
   self._position = Vec2d(0,0) # x e y? funciones de gummworld2

   #self.direction = DOWN
   self.dir = Vec2d(0.0, 0.0)
   #images loading
   front_image = path + '/' + image + '-idle-1.png'
   self.front_standing = utils.load_png(front_image)
   self.right_standing = utils.load_png(front_image)
   
   

   self.back_standing = pygame.transform.flip(self.front_standing, True, False) 
   self.left_standing = pygame.transform.flip(self.right_standing, True, False) 
   self.playerWidth, self.playerHeight = self.front_standing.get_size()

   ##animation loading
   self.imagesAndDurations = [('data/peasant/peasant-idle-%s.png' % (str(num)), 0.1) for num in range(1,7)]
   self.animObjs = pyganim.PygAnimation(self.imagesAndDurations,False)
   self.movement = 0
   # to improve the path and left and right animations

   # create the right-facing sprites by copying and flipping the left-facing sprites
   #self.animObjs['-n-run'] = self.animObjs['-se-run'].getCopy()
   #self.animObjs['-s-run'] = self.animObjs['-se-run'].getCopy()
   #self.animObjs['-s-run'].flip(True, False)
   #self.animObjs['-s-run'].makeTransformsPermanent()
   #self.animObjs['-sw-run'] = self.animObjs['-se-run'].getCopy()
   #self.animObjs['-sw-run'].flip(True, False)
   #self.animObjs['-sw-run'].makeTransformsPermanent()

   #self.image = self.animObjs['-se-run'].getCurrentFrame()
   self.image = self.front_standing
   self.rect = self.image.get_rect()


   #move conductor
   self.moveConductor = pyganim.PygConductor(self.animObjs)

##voy por aqui modificando!!
   #start direction
   #self.direction = DOWN
   self.x = screen_pos[0]
   self.y = screen_pos[1]
   self.screen_position = screen_pos
   self.position = map_pos

   #game attributes
   self.strength = 1
   
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


 def move(self):
   self.moveConductor.play() # calling play() while the animation objects are already playing is okay; in that case play() is a no-op
   self.movement = 1

 def stopMove(self):
   self.moveConductor.stop() # calling stop() while the animation objects are already stopped is okay; in that case stop() is a no-op
   self.movement = 0
		 
 def getRect(self):
   return self.rect

 def update(self): #no screen
   self.x = self.position[0]
   self.y = self.position[1]
   if self.movement:
       self.image = self.animObjs.getCurrentFrame()
       if(self.animObjs.isFinished()):
           print('creature animation finished!')
           self.image = self.front_standing
           self.stopMove()

   else:
       self.image = self.front_standing

   self.rect = self.image.get_rect()
   self.rect.center = self.x, self.y
   #print('animating flag')

   
#game dynamics procedures
 def setStrength(self,value):
     self.strength = value
   #self.flag =utils.load_png('flags/red-1.png')# self.animFlags.getCurrentFrame()
  
     


	

