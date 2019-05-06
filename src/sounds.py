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

'''game sounds'''
'''class to manage music and sounds in game
'''
sounds = {'move' : 'sounds/horse1.ogg'}
music = {'menu' : 'music/menu.mp3','worldmap' : 'music/worldmap1.mp3'}

class gameSound:
   def __init__(self):
      pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag

   def loadTracks(self):
      try:
         pygame.mixer.music.load(os.path.join('data', music['menu']))#load music
         pygame.mixer.music.load(os.path.join('data', music['worldmap']))#load music
         self.move = pygame.mixer.Sound(os.path.join('data',sounds['move']))  #load sound
      except:
         raise(UserWarning, "could not load or play soundfiles in 'data' folder :-(")     

   def playmenu(self,status,volume):
      if status:
         pygame.mixer.music.load(os.path.join('data', music['menu']))#load music
         pygame.mixer.music.set_volume(volume)
         pygame.mixer.music.play(-1)                           # play music non-stop
      else:
         pygame.mixer.music.fadeout(500)                           # fadeout
      return
   #function to know if we can reach a place in world
   def playworld(self,status,volume):
      if status:
         pygame.mixer.music.load(os.path.join('data', music['worldmap']))#load music
         pygame.mixer.music.set_volume(volume)
         pygame.mixer.music.play(-1)                           # play music non-stop
      else:
         pygame.mixer.music.fadeout(500)                           # fadeout
      return
   def playsound(self,sound):
      if sound == 'move':
         self.move.play()
      else:
         return
