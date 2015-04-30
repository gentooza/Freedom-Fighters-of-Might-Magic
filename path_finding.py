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



def pos2steps(pos,world):
   """ get a path from a mouse pos"""
   #path
   path = []
   #destination
   pos = State.camera.screen_to_world(pos)
   final_cell_id = world.index_at(pos[0],pos[1])
   if(final_cell_id == None):
      return;
   row,col = world.get_cell_grid(final_cell_id)
   #origin
   camera = State.camera
   wx, wy = camera.target.position
   cell_id = world.index_at(wx,wy)
   orig_row,orig_col = world.get_cell_grid(cell_id)
   print("avatar position: ",wx,wy," destination position: ",pos)
   if(orig_row == row and orig_col == col):
      return;
   #steps
   if(orig_row >= row):
      for i in range(row,orig_row):
         print("x,y : ",world.get_cell_pos(world.index(world.get_cell_by_grid(orig_col,i)))) 
         path.append(world.index(world.get_cell_by_grid(orig_col,i)))
   else:
      for i in range(orig_row,row):
         print("x,y : ",world.get_cell_pos(world.index(world.get_cell_by_grid(orig_col,i))))
         path.append(world.index(world.get_cell_by_grid(orig_col,i)))
   if(orig_col >= col):
      for i in range(col,orig_col):
         print("x,y : ",world.get_cell_pos(world.index(world.get_cell_by_grid(i,row)))) 
         path.append(world.index(world.get_cell_by_grid(i,row)))
   else:
      for i in range(orig_col,col):
         print("x,y : ",world.get_cell_pos(world.index(world.get_cell_by_grid(i,row)))) 
         path.append(world.index(world.get_cell_by_grid(i,row)))
   return path,final_cell_id




