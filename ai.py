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

import path_finding
'''computer AI'''
'''we have the AI for the world map
the economics AI
and the combat AI
   - for V0.0.6 we are gonna attack, or flee from hero
'''

class computerPlayer:
   def __init__(self,aiparameters):
      self.safeRatius = 10
      self.attackRatius = 14
      self.path = None
      return
      
   '''to move hero we needs our situation
   the enemy situation, his strength, our strength'''
   def flee_attack(self,hero,enemy_hero,world,terrain_layer,collision_layer,avatar_layer):
      
      self.path,final_cell_id = path_finding.pos2steps(hero.position,enemy_hero.position,world,terrain_layer,collision_layer,avatar_layer)
      print('distance:')
      print(len(self.path))
      if len(self.path) <= self.attackRatius and hero.strength > enemy_hero.strength:
          #attack
          print('attack!')
          move_x = 0
          move_y = 0
      elif len(self.path) <= self.safeRatius and hero.strength < enemy_hero.strength:
          #flee
          print('flee')
          move_x = 0
          move_y = 0
      else:
          #idle
          print('idle')
          move_x = random.randint(-1, 1)
          move_y = random.randint(-1, 1)
      return move_x,move_y
      
