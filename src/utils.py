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
    import os
    import pygame
    from gummworld2 import State
    
except ImportError as err:
	print("couldn't load module. %s" % (err))
	sys.exit(2)


def load_png(name):
   """ Load image and return image object"""
   fullname = os.path.join('data', name)
   try:
      image = pygame.image.load(fullname)
      if image.get_alpha() is None:
         image = image.convert()
      else:
         image = image.convert_alpha()
   except pygame.error as message:
      print('Cannot load image:', fullname)
      raise SystemExit(message)
   return image

def load_flag(num):
   if(num == 1): #red
      image =  load_png('flags/red-1.png')
      colour = 'red'
   elif(num == 2): #green
      image =  load_png('flags/green-1.png')
      colour = 'green' 
   else: #red?
      image =  load_png('flags/red-1.png')
      colour = 'red'
   return image,colour              

def is_screen_pos_inside_map(screen_pos):
   #checking map edges
   rect = State.world.rect
   world_pos = State.camera.screen_to_world(screen_pos)
   #if mouse click is outside the map we do nothing!
   if world_pos[0] < rect.left:
      return False;
   elif world_pos[0]  >= rect.right:
      return False;
   if world_pos[1]  < rect.top:
      return False;
   elif world_pos[1]  >= rect.bottom:
      return False;
   return True;