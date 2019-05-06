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
import ai



#to improve, mix the for loop with the factions __init__ 
class creatures(object):
    def __init__(self,objects_layer):
        self.group = []
        for element in objects_layer:
            faction_num = int(element.properties['team'])
            if faction_num == 0:
                stype = element.properties['type']
                qty = element.properties['qty']
                x,y = element.rect.x,element.rect.y
                self.group.append(group(stype,qty,(x,y)))



#to improve, add attributes, moral, luck modifiers, etc.
class group(object):
    def __init__(self,stype,qty,coordinates):
        #cell size
        newcoordinates = (coordinates[0]+30,coordinates[1]+30)
        self.creature = objects.creature("peasant","peasant",newcoordinates,(0, 0))

class factions(object):
 def __init__(self,objects_layer):
    self.n_factions = 0
    self.team = []
    for element in objects_layer:
       faction_num = int(element.properties['team'])
       if faction_num != 0:
          faction_hero = element.properties['heroe']
          player = element.properties['player']
          #simple error parameter input check
          if(player != 'computer' and player != 'human'):
             player = 'computer'
          x,y = element.rect.x,element.rect.y
          self.team.append(team(faction_num,faction_hero,(x,y),player))



'''faction class, with it's heroes, places, resources, etc.'''
class team(object):
 def __init__(self, num, hero_name,coordinates,player):
   #cell size
   newcoordinates = (coordinates[0]+30,coordinates[1]+30)
   self.num = num
   self.color = num #color code by team number? 1 = red, etc.?
   self.heroes = []
   hero = objects.ourHero("horseman","horseman",newcoordinates,(0, 0),num)
   hero.attr = game_engine.heroes[hero_name]
   self.heroes.append(hero)
   self.player = player
   #computer team?
   if player != 'human':
      self.AI = ai.computerPlayer(None)
   self.end_turn = 0
   
 def move_hero(self,computer_hero,world,avatar_layer,terrain_layer,collision_layer,objects_layer):
    #stablish objectives
    self.AI.prepare(computer_hero,world,avatar_layer,terrain_layer,collision_layer,objects_layer)
    #if objectives move
    #objectives achieved? && endturn    
    move_x,move_y = self.AI.move(computer_hero)
  
                    
    if self.AI.turnFinished(computer_hero,world,avatar_layer,terrain_layer,collision_layer,objects_layer):
        self.end_turn = True
    return move_x,move_y

	

