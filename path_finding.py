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
      self.H = 0
      self.G = 0

terrain_costs = {1 : 1.2 , 2 : 1}

def  getting_adjacent(orig_cell,dest_cell, world,terrain_layer,collision_layer,avatars_layer):

   y,x =  world.get_cell_pos(orig_cell.id)
   collide_rect = Rect(x-10,y-10,80,80)
   adjacents = set()

   objects = avatars_layer.get_objects_in_rect(collide_rect)
   cells = world.intersect_indices(collide_rect)
   #print("adjacents!")
   for element in cells:
      cell_tmp = cell(element,orig_cell)
      col,row = world.get_cell_grid(element)
      o_col,o_row = world.get_cell_grid(orig_cell.id)
      if((col != o_col or row != o_row) and (row < terrain_layer.layer.width and col < terrain_layer.layer.height)): #neither we don't want to add the origin nor seek outside the map layers
         #fixed cost
         cell_tmp.G = terrain_costs[terrain_layer.layer.content2D[row][col]]
         
         if(cell_tmp.G!=0): #if it's walkable      
            #heuristic cost
            o_col,o_row = world.get_cell_grid(orig_cell.id)
            d_col,d_row = world.get_cell_grid(dest_cell.id)
            #we don't want discrimine diagonals, they are kind, good people, and the most important, they have no more cost movement
            row_difference = d_row-row
            if(abs(row_difference) == 1):
               row_difference = 0.1
            col_difference = d_col-col
            if(abs(col_difference) == 1):
               col_difference = 0.1
            ####
            cell_tmp.H = (abs(row_difference)+abs(col_difference))*2
            #if there is no collision
            if(collision_layer.layer.content2D[row][col] == 0):
            #and if 
               adjacents.add(cell_tmp)

            #print('added in heuristics the cell id: ',cell_tmp.id)
         #col,row = world.get_cell_grid(element)
         #print(row,col,cell_tmp.G,cell_tmp.H)
   #print("end adj")
   return adjacents

def a_algorithm(orig_cell,final_cell,world,terrain_layer,collision_layer,avatars_layer):
   #A* method
   path = []
   closedList = set()
   openList = set()

   current = orig_cell
   def retracePath(c):
        #(x,y) = world.get_cell_pos(c.id)
        #cell size!
        #path.insert(0,(x+30,y+30))
        path.insert(0,(c.id,c.G))
        if c.parent == None:
            return
        retracePath(c.parent)

   #adding adjacent cells
   openList.add(current)
   while len(openList) is not 0:
       #print('elements in openlist:')
       #for element in openList:
       #   print('element id: ',element.id, ' ,element H+G: ',element.H+element.G)
       current = min(openList, key=lambda inst:inst.H+inst.G)       
       #print('the minor is: ',current.id,'  ,with H+G = ',current.H+current.G)
       if current.id == final_cell.id: #finished
          retracePath(current)
          return path
       openList.remove(current)
       closedList.add(current)
       for tile in getting_adjacent(current,final_cell,world,terrain_layer,collision_layer, avatars_layer):
          #print(tile.id,tile.H)
          if tile not in closedList:            
            #print('not in closedlist')
            if tile not in openList:
               #print('added to openlist')
               openList.add(tile)
            tile.parent = current
       #input("Press Enter to continue...")
   
   return path
   


def pos2steps(orig_pos,pos,world,terrain_layer,collision_layer, avatars_layer):
   """ get a path from a mouse pos"""
   #path
   path = []

   #destination
   #pos = State.camera.screen_to_world(pos)
   final_cell = cell(world.index_at(pos[0],pos[1]),None)
   if(final_cell.id == None):
      return;
   col,row = world.get_cell_grid(final_cell.id)
   if(collision_layer.layer.content2D[row][col] != 0):
      return None,None
   #origin
   orig_cell = cell(world.index_at(orig_pos[0],orig_pos[1]),None)
   print('setting path from:(',orig_pos[0],',',orig_pos[1],') to (',pos[0],',',pos[1],')')
   #if destination is the same as origin, then, no path and return
   if(orig_cell.id == final_cell.id):
      final_cell.id = None
      return path,None;
   orig_col,orig_row = world.get_cell_grid(orig_cell.id)
   idx= terrain_layer.layer.content2D[orig_row][orig_col]
   orig_cell.G = idx
   final_cell.G = terrain_layer.layer.content2D[row][col]
   
   #print(orig_col,orig_row,idx)
   #print(terrain_costs[idx])
   #steps
   
   path =  a_algorithm(orig_cell,final_cell,world,terrain_layer,collision_layer, avatars_layer)
   #removing origin from path   
   if path:
       path.pop(0)
   #print('to go from cell_id: ', orig_cell.id,'  to cell_id: ',final_cell.id)
   #for element in path:
   #   print(element)
    
   #what if we erase the first step, the origin?
   #################################path.pop(0)
   return path,final_cell.id




