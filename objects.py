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
	from gummworld2 import context, model, spatialhash, toolkit
	from socket import *
	from pygame.locals import *
except ImportError, err:
	print "couldn't load module. %s" % (err)
	sys.exit(2)


# define some constants
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

WALKRATE = 4
RUNRATE = 12

class ourHero(object):

 def __init__(self,image,path,screen_position):
	 self.movement = 0
	 self.x = screen_position[0]
	 self.y = screen_position[1]
	 self._position = Vec2d(0,0) # x e y? funciones de gummworld2
	 self.direction = DOWN
	 self.dir = Vec2d(0.0, 5.0)
	 #images loading
	 front_image = path + '/' + image + '-se-bob1.png'
	 self.front_standing = utils.load_png(front_image)
	 self.right_standing = utils.load_png(front_image)
	 self.rect = self.front_standing.get_rect(center=self.position)

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

	 self.image = self.animObjs['-se-run'].getCurrentFrame()

	 #move conductor
	 self.moveConductor = pyganim.PygConductor(self.animObjs)
	 #start direction
	 self.direction = DOWN


 @property
 def position(self):
	 return self._position.x,self._position.y

 def getxyposition(self):
	return self.x, self.y

 @position.setter
 def position(self, val):
	 p = self._position
	 p.x, p.y = val
	 #self.x,self.y = val
	 self.rect.center = round(p.x), round(p.y)

 def setxyposition(self,val):
        self.x,self.y = val

 def moveLimits(self,width,height):
	 self.limitRight = width
	 self.limitDown = height

 def move(self,direction):
	 self.direction = direction
	 self.movement = 1
	 #if(self.direction == DOWN):
		 #self.y = self.y + WALKRATE
		 #self._position = Vec2d(self.x,self.y)
		 #self.dir = Vec2d(0.0, 5.0)
	 #elif self.direction == UP:
		 #self.y = self.y - WALKRATE
		 #self._position = Vec2d(self.x,self.y)
		 #self.dir = Vec2d(0.0, -5.0)
	 #elif(self.direction == LEFT):
		 #self.x = self.x - WALKRATE
		 #self._position = Vec2d(self.x,self.y)
		 #self.dir = Vec2d(-5.0, 0.0)
	 #elif self.direction == RIGHT:
		 #self.x = self.x + WALKRATE
		 #self._position = Vec2d(self.x,self.y)
		 #self.dir = Vec2d(5.0, 0.0)		 
 

 def stopMove(self,direction):
	 self.direction = direction
	 self.movement = 0

 def update(self,screen):
	 if self.movement:
                 newx,newy = self.position + self.dir
                 world_rect = State.world.rect
		 # draw the correct walking/running sprite from the animation object
		 self.moveConductor.play() # calling play() while the animation objects are already playing is okay; in that case play() is a no-op
		 # walking
                 if newy < 28:
                        self.position = (self.position[0],28)
                 if newy >= world_rect.bottom:
                        self.position = (self.position[0],world_rect.bottom)
                 if newx < 64:
                        self.position = (64,self.position[1])
                 if newx >= world_rect.right:
                        self.position = (world_rect.right,self.position[1])
		 if self.direction == UP:
 			 self.dir.y = -4
			 #self._position = Vec2d(self.x,self.y)
			 self.animObjs['-n-run'].blit(screen, (self.x, self.y))
			 self.image = self.animObjs['-n-run'].getCurrentFrame()
		 elif self.direction == DOWN:
                         self.dir.y = 4
			 #self.y = self.y + WALKRATE
			 #self._position = Vec2d(self.x,self.y)
			 self.animObjs['-s-run'].blit(screen, (self.x, self.y))
			 self.image = self.animObjs['-s-run'].getCurrentFrame()
		 elif self.direction == LEFT:
                         self.dir.x = -4
			 #self.x = self.x - WALKRATE
			 #self._position = Vec2d(self.x,self.y)
			 self.animObjs['-sw-run'].blit(screen, (self.x, self.y))
			 self.image = self.animObjs['-sw-run'].getCurrentFrame()
		 elif self.direction == RIGHT:
                         self.dir.x = 4
			 #self.x = self.x + WALKRATE
			 #self._position = Vec2d(self.x,self.y)
			 self.animObjs['-se-run'].blit(screen, (self.x, self.y))
			 self.image = self.animObjs['-se-run'].getCurrentFrame()
	 else:
		 # standing still
		 self.moveConductor.stop() # calling stop() while the animation objects are already stopped is okay; in that case stop() is a no-op
                 self.dir.x = self.dir.y = 0
		 if self.direction == UP:
			 screen.blit(self.back_standing, (self.x, self.y))
			 self.image = self.back_standing
		 elif self.direction == DOWN:
			 screen.blit(self.front_standing, (self.x, self.y))
			 self.image = self.front_standing
		 elif self.direction == LEFT:
			 screen.blit(self.left_standing, (self.x, self.y))
			 self.image = self.left_standing
		 elif self.direction == RIGHT:
			 screen.blit(self.right_standing, (self.x, self.y))
			 self.image = self.right_standing
		 else:
			 screen.blit(self.front_standing, (self.x, self.y))
			 self.image = self.front_standing



	 self.position +=  self.dir
	 print self.position


	
