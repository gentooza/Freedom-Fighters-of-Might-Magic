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
  import game_engine
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
      self.path = path_finding.path()
      self.objective = None
      self.possible_objective = None
      return
      
   '''function to rpepare path, after studying enemy heroes, local situation, mines, resources, etc.'''
   '''v1 if enemy hero is weaker, attack, if is stronger flee, if is equal simply go idle over the map exploring'''
   def prepare(self,computer_hero,world,avatar_layer,terrain_layer,collision_layer,objects_layer):
       #analyse map seeking objectives:
       #for the instance only one hero   as objective 
       for hero in avatar_layer:
           if(hero != computer_hero):
               if not self.objective:
                   self.possible_objective = hero
                   
       if self.possible_objective != self.objective:
            #new objective, new decission, new path
            self.objective = self.possible_objective
            self.possible_objective = None
            self.flee_attack(computer_hero,hero,world,terrain_layer,collision_layer,avatar_layer)
       #already with same objective   
       else:
           if not self.path.route:
               self.flee_attack(computer_hero,hero,world,terrain_layer,collision_layer,avatar_layer)
           else:
               return

   '''to move hero we needs our situation
   the enemy situation, his strength, our strength'''
   def flee_attack(self,hero,enemy_hero,world,terrain_layer,collision_layer,avatar_layer):
       #print('computer hero position:',hero.position,' human hero position:',enemy_hero.position)
       row,col = world.get_grid_by_worldcoordinates(hero.position[0],hero.position[1])
       print('computer hero position:',row,col)
       row,col = world.get_grid_by_worldcoordinates(enemy_hero.position[0],enemy_hero.position[1])
       print('human hero position:',row,col)   
       final_cell_id = self.path.pos2steps(hero.position,enemy_hero.position,world,terrain_layer,collision_layer,avatar_layer)
       print('distance:')
       print(len(self.path.route))
       print('complete path:')
       for element_id,element_G in self.path.route:
           print('col and row (y,x):',world.get_cell_grid(element_id))
       if len(self.path.route) <= self.attackRatius and hero.strength > enemy_hero.strength:
          #attack
          print('attack!')
          final_cell_id = self.path.pos2steps(hero.position,enemy_hero.position,world,terrain_layer,collision_layer,avatar_layer)
       elif len(self.path.route) <= self.safeRatius and hero.strength < enemy_hero.strength:
          #flee
          print('flee')
          if self.path.route:
              self.path.route.clear()
       else:
          #idle
          print('idle')
          if self.path.route:             
              self.path.route.clear()
       return
       
   def move(self,hero):
       if self.path.route:
          cell_id,cell_G =  self.path.route.pop(0)
          wx, wy = hero.position
          cell_avatar = State.world.index_at(wx,wy)
          o_row,o_col = State.world.get_cell_grid(cell_avatar)
          d_row,d_col = State.world.get_cell_grid(cell_id)
          
          print('computer origin:(',o_row,',',o_col,')')
          print('computer destination:(',d_row ,',',d_col,')')
          move_x = d_col-o_col
          move_y = d_row-o_row
       else:
          move_x = random.randint(-1, 1)
          move_y = random.randint(-1, 1)
       return move_x,move_y
       
   def turnFinished(self,hero,world,avatar_layer,terrain_layer,collision_layer,objects_layer):
       if not self.objective:
           return True
       elif hero.remaining_movement < 1:
           return True
       else:
           return False
