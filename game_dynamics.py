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

import objects
import game_engine

class factions(object):
 def __init__(self,objects_layer):
    self.n_factions = 0
    self.team = []
    for element in objects_layer:
       faction_num = int(element.properties['team'])
       faction_hero = element.properties['heroe']
       x,y = element.rect.x,element.rect.y
       self.team.append(team(faction_num,faction_hero,(x,y)))



'''faction class, with it's heroes, places, resources, etc.'''
class team(object):
 def __init__(self, num, hero_name,coordinates):
   self.num = num
   self.color = num #color code by team number? 1 = red, etc.?
   self.heroes = []
   hero = objects.ourHero("horseman","horseman",coordinates,(0, 0))
   hero.team = num
   hero.attr = game_engine.heroes[hero_name]
   self.heroes.append(hero)


	

