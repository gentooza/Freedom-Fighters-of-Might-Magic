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
	import main_menu
	import game_engine
	import utils
#	import objects
	import paths
	import gummworld2
	from gummworld2 import Engine, State, BasicMap, SubPixelSurface, View, Vec2d
	from gummworld2 import context, model, spatialhash, toolkit

	from socket import *
	from pygame.locals import *
except ImportError as err:
	print("couldn't load module. %s" % (err))
	sys.exit(2)

class app:

 def __init__(self,parameters):
    pygame.init();
    if(parameters['resolution'] != 'NULL'):
       self.resolution = parameters['resolution']
    else:
       self.resolution = (320,240)
    if(parameters['strcaption'] != 'NULL'):
       self.strCaption = parameters['strcaption']
    else:
       self.strCaption = 'Freedom Fighters of Might & Magic'
    self.parameters = parameters


 def setDisplay(self):
    self.screen =  pygame.display.set_mode(self.resolution)
    self.caption = pygame.display.set_caption(self.strCaption)
    self.parameters['caption'] = self.caption

 def run(self):
    scr_menu = main_menu.main_menu(parameters)
    scr_menu.setScreen(self.screen,30)
    scr_menu.constructScene()
    ret = 0
    while True:
       if(ret == 0):
          ret = scr_menu.run()
       if(ret == 1):
          print("LET'S PLAY FMM!!")
          #scr_game = game.gameScene(self.parameters)
          #scr_game.constructScene()
          scr_game = game_engine.gameEngine(self.resolution,self.strCaption)
          #scr_game.setScreen(self.screen)
          print('in game!!')
          gummworld2.run(scr_game)
          print('out of game!!')
          ret = 0

       else:
          print("EXITING FMM!!")
          pygame.quit()
          sys.exit()		
	
		
	



#INTILIALIZATION
#old 1014,965
resolution = (1024,768)
version = '0.0.5 ALPHA'
strCaption = 'FFMM ' + version
tile_size=(30, 30) 
map_size=(100, 100)
minimap_pos = (600,100)
minimap_size = (120,120)
FPS = 50
NULL = 'NULL'

parameters = {'resolution' : resolution,'strcaption' : strCaption,'caption' : NULL,'tile_size' : tile_size,'map_size' : map_size, 'minimap_pos' : minimap_pos, 'minimap_size' : minimap_size, 'FPS' : FPS, 'version' : version}
FFMM = app(parameters)

#DISPLAY
FFMM.setDisplay()

#GAME RUN!!
FFMM.run()

	





