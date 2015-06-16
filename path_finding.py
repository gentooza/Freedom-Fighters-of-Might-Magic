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

terrain_costs = {1 : 0.2 , 2 : 0.1, 3 : 0.5 , 4 : 0.1 , 5 : 0.2 , 6 : 1.0}

class cell(object):
   def __init__(self,ident,parent):
      self.id = ident
      self.parent = parent
      self.H = 0
      self.G = 0
      self.type = 0
class path():
    def __init__(self):
        self.route = None
        self.confirmed = False
        
    def  getting_adjacent(self,orig_cell,dest_cell, world,terrain_layer,collision_layer,avatars_layer):
        y,x =  world.get_cell_pos(orig_cell.id)
        collide_rect = Rect(x-10,y-10,80,80)
        adjacents = set()
        #objects = avatars_layer.get_objects_in_rect(collide_rect) THIS WORKS? PERHAPS IS FASTER THAN DE FOR LOOP AT THE BOTTOM
        cells = world.intersect_indices(collide_rect)
        #print("adjacents!")
        for element in cells:
            cell_tmp = cell(element,orig_cell)
            col,row = world.get_cell_grid(element)
            o_col,o_row = world.get_cell_grid(orig_cell.id)
            if((col != o_col or row != o_row) and (row < terrain_layer.layer.width and col < terrain_layer.layer.height)): #neither we don't want to add the origin nor seek outside the map layers
                #fixed cost
                cell_tmp.G = terrain_costs[terrain_layer.layer.content2D[row][col]]
                print("terrain layer:",terrain_layer.layer.content2D[row][col])
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
                    cell_tmp.type = 0
                    #if there is no collision
                    if(collision_layer.layer.content2D[row][col] == 0):
                        #and if there is no other avatar or creature
                        occuped = False
                        for creature in avatars_layer:
                            if cell_tmp.id == world.index_at(creature.position[0],creature.position[1]):
                                occuped = True
                        if not occuped:
                            adjacents.add(cell_tmp)
                        if occuped and cell_tmp.id == dest_cell.id: #attack!
                            cell_tmp.type = 2
                            adjacents.add(cell_tmp)
                            

        return adjacents

    def a_algorithm(self,orig_cell,final_cell,world,terrain_layer,collision_layer,avatars_layer):
        #A* method
        path = []
        closedList = set()
        openList = set()

        current = orig_cell
        def retracePath(c):
            #(x,y) = world.get_cell_pos(c.id)
            #cell size!
            #path.insert(0,(x+30,y+30))
            path.insert(0,(c.id,c.G,c.type))
            if c.parent == None:
                return
            retracePath(c.parent)

        #adding origin
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
            for tile in self.getting_adjacent(current,final_cell,world,terrain_layer,collision_layer, avatars_layer):
                #print(tile.id,tile.H)
                if tile not in closedList:            
                    #print('not in closedlist')
                    if tile not in openList:
                        #print('added to openlist')
                        openList.add(tile)
                    tile.parent = current
                    #input("Press Enter to continue...")
   
        return path
   


    def pos2steps(self,orig_pos,pos,world,terrain_layer,collision_layer, avatars_layer):
       """ get a path from a mouse pos"""
       #path
       path = []
    
       #destination
       #pos = State.camera.screen_to_world(pos)
       final_cell = cell(world.index_at(pos[0],pos[1]),None)
       #last step is attack?
       #attack = False
       #for creature in avatars_layer:
       #    if final_cell == world.index_at(creature.position[0],creature.position[1]):
       #        attack = True
       #last step is action?
       #NOT IMPLEMENTED        
       if(final_cell.id == None):
          return;
       row,col = world.get_cell_grid(final_cell.id)
       if(collision_layer.layer.content2D[row][col] != 0):
          return None,None
       #origin
       orig_cell = cell(world.index_at(orig_pos[0],orig_pos[1]),None)
       print('setting path from:(',orig_pos[0],',',orig_pos[1],') to (',pos[0],',',pos[1],')')
       #if destination is the same as origin, then, no path and return
       if(orig_cell.id == final_cell.id):
          final_cell.id = None
          return path,None;
       orig_row,orig_col = world.get_cell_grid(orig_cell.id)
       x = orig_col
       y = orig_row
       idx= terrain_layer.layer.content2D[x][y]
       orig_cell.G = idx
       x = col
       y = row
       #check for errors?
       final_cell.G = terrain_layer.layer.content2D[x][y]
       #################
     
       path =  self.a_algorithm(orig_cell,final_cell,world,terrain_layer,collision_layer, avatars_layer)
       #removing origin from path   
       if path:
           path.pop(0)
    
       #debug
       print('path:')
       #for element in path:
       #    pos = world.get_cell_pos(element[0])
       #    print('(',pos[1]+world.cell_size/2,',',pos[0]+world.cell_size/2,') , cost =',element[1])
       self.route = path
       return final_cell.id


    '''it get a step from path
    returning:
    self.move_to: Vec2d to final coordinates
    self.step: Vec2d with the grid step to walk (one step left, diagonal upperleft, up, etc.) 
    cell_id: the destination cell id
    move_G: the movement cost to take this step
    '''
    def getStepFromPath(self,world):
        
        #debug:
        #print('remaining path:')
        #for element in path:
        #    pos = world.get_cell_pos(element[0])
        #    print('(',pos[1]+world.cell_size/2,',',pos[0]+world.cell_size/2,')')
        #
        orig_x,orig_y = State.camera.position
        o_row,o_col = world.get_grid_by_worldcoordinates(orig_x,orig_y)
        #taking step
        if(not self.route):
            return #ERROR
        cell_id,cell_G,cell_type =  self.route.pop(0)
        pos = world.get_cell_pos(cell_id)
             
        move_to = Vec2d(pos[1]+world.cell_size/2,pos[0]+world.cell_size/2)
    
        d_row,d_col = world.get_cell_grid(cell_id)
        col = row = 0
        if(o_row -d_row > 0):
            row = -1
        elif(o_row - d_row < 0):
            row = 1
        else:
            row = 0
        if(o_col - d_col > 0):
            col = -1
        elif(o_col - d_col < 0):
            col=1
        else:
            col = 0  
        step = Vec2d( col,row)
        return move_to,step,cell_id,cell_G,cell_type
            
    '''it returns a step to path'''
    def retStepToPath(self,cell_id,cell_G,cell_type):
        self.route.insert(0,(cell_id,cell_G,cell_type))
 


