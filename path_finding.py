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
import sys
import cProfile, pstats



import pygame
from pygame.sprite import Sprite
from pygame.locals import *

import paths
import gummworld2
from gummworld2 import context, data, model, geometry, toolkit, ui,Engine, State, TiledMap, BasicMapRenderer, Vec2d, Statf
from gummworld2.geometry import RectGeometry, CircleGeometry, PolyGeometry

import objects
import game_interface
import ffmm_spatialhash

class cell(object):
   def __init__(self,ident,parent):
      self.id = ident
      self.parent = parent
      self.H = None




terrain_costs = {1 : 1.2 , 2 : 1}
def  getting_adjacent(cell,dest_cell):
   
   for 


def a_algorithm(orig_cell_id,final_cell_id,world,terrain_layer):
   #A* method
   path = []
   openlist = set()
   closedlist = set()

   current = orig_cell_id
   def retracePath(c):
        (x,y) = world.get_cell_pos(c.id)
        #cell size!
        path.insert(0,(x+30,y+30))
        if c.parent == None:
            return
        retracePath(c.parent)

   #adding adjacent tiles
   getting_adjacent(current,final_cell_id)
    world.get_cell_grid(orig_cell.id)

   openList.append(current)
   while len(openList) is not 0:
      current = min(openList, key=lambda inst:inst.H)
      if current == end:
         return retracePath(current)
      openList.remove(current)
      closedList.append(current)
      for tile in graph[current]:
         if tile not in closedList:
            tile.H = (abs(end.x-tile.x)+abs(end.y-tile.y))*10 
            if tile not in openList:
               openList.append(tile)
            tile.parent = current
   return path
   


def pos2steps(pos,world,terrain_layer):
   """ get a path from a mouse pos"""
   #path
   path = []

   #destination
   pos = State.camera.screen_to_world(pos)
   final_cell = cell(world.index_at(pos[0],pos[1]),None)
   if(final_cell.id == None):
      return;
   col,row = world.get_cell_grid(final_cell.id)
   #origin
   camera = State.camera
   wx, wy = camera.target.position
   orig_cell = cell(world.index_at(wx,wy),None)

   #if destination is the same as origin, then, no path and return
   if(orig_cell.id == final_cell.id):
      final_cell.id = None
      return path,None;
   orig_col,orig_row = world.get_cell_grid(orig_cell.id)
   idx= terrain_layer.layer.content2D[orig_row][orig_col]
   #print(orig_col,orig_row,idx)
   #print(terrain_costs[idx])
   #steps
   #path =  a_algorithm(orig_cell_id,final_cell_id,world,terrain_layer)
  

   return path,final_cell.id




