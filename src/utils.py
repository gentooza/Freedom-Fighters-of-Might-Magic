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
    import os
    import pygame
    
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