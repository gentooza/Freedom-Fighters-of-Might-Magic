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


from random import randrange, choice

import pygame, math, sys
import objects
import pygbutton
import utils

from pygame.locals import *

import paths
import gummworld2
from gummworld2 import Engine, State, BasicMap, SubPixelSurface, View, Vec2d
from gummworld2 import context, model, spatialhash, toolkit

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BACKGROUND = (20,20,20)

# define some constants
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


class Minimap(object):
    
    def __init__(self,(coordinate_x, coordinate_y), (size_x, size_y)):
        
        # The minimap is a subsurface upon which the whole world is projected.
        self.mini_screen = View(
            State.screen.surface, pygame.Rect(coordinate_x, coordinate_y, size_x, size_y))
        
        # tiny_rect will be drawn on the minimap to indicate the visible area of
        # the world (the screen, aka camera).
        self.tiny_rect = self.mini_screen.rect.copy()
        size = Vec2d(State.screen.size)
        size.x = float(size.x)
        size.y = float(size.y)
        size = size / State.world.rect.size * self.mini_screen.rect.size
        self.tiny_rect.size = round(size.x), round(size.y)
        
        # A dot represents a full sprite on the minimap. SubPixelSurface is a
        # generated set of antialiased images that give the illusion of movement
        # smaller than one pixel. If we did not do this the dots would have an
        # annoying jerky movement.
        dot = pygame.surface.Surface((1, 1))
        dot.fill(Color('white'))
        self.dot = SubPixelSurface(dot)
        
        # Pre-compute some reusable values.
        mini_screen = self.mini_screen
        mini_surf = mini_screen.surface
        mini_size = mini_screen.rect.size
        self.mini_size = mini_size
        
        full_size = Vec2d(State.world.rect.size)
        full_size.x = float(full_size.x)
        full_size.y = float(full_size.y)
        self.full_size = full_size

    def draw(self, sprite_group):
        mini_screen = self.mini_screen
        mini_surf = mini_screen.surface
        
        # Position the "visible area" tiny_rect, aka camera, within the minimap
        # so we can draw it as a filled rect.
        full_size = self.full_size
        mini_size = self.mini_size
        tiny_pos = State.camera.rect.topleft / full_size * mini_size
        self.tiny_rect.topleft = round(tiny_pos.x), round(tiny_pos.y)
        
        # Draw the minimap...
        mini_screen.clear()
        # Draw the camera area as a filled rect.
        pygame.draw.rect(mini_surf, Color(200, 0, 255), self.tiny_rect)
        # Draw sprites as dots.
        for s in sprite_group:
            pos = s.rect.topleft / full_size * mini_size
            dot = self.dot.at(pos.x, pos.y)
            mini_surf.blit(dot, pos, None, BLEND_RGBA_ADD)
        
        # Draw a border.
        pygame.draw.rect(State.screen.surface, (99, 99, 99), mini_screen.parent_rect.inflate(2, 2), 1)


class gameScene(Engine):
    id=1
    def __init__(self,features):
        self.features = features
        #gunworld2 engine
        print features['resolution']
        self.movement = 0
 
    def setScreen(self,screen):
        self.screen = screen
        
    def constructScene(self):
        Engine.__init__(self,self.screen,self.features['resolution'],0,self.features['strcaption'],None,None,None,None, self.features['tile_size'], self.features['map_size'],self.features['FPS'])
      
        self.minimap = Minimap(self.features['minimap_pos'],self.features['minimap_size'])

        toolkit.make_tiles()
        for tile in self.map.layers[0].objects.objects:
            tile.image = utils.load_png('dirt_1.png')
        map_ = State.map
        self.things = spatialhash.SpatialHash(map_.rect, 30)
        self.things.add(objects.ourHero('horseman','horseman',(320,240)))

        self.visible_objects = []
        
        State.clock.schedule_interval(self.set_caption, 2.)
        
        self.incx = self.x = 0
        self.incy = self.y = 0
        State.camera.init_position(State.camera.rect.center - Vec2d(self.x, self.y))
   
    def update(self, dt):
        """overrides Engine.update"""
        self.update_camera_position()
        State.camera.update(dt)
        for thing in list(self.things):
            thing.update(self.screen)
            self.things.add(thing)
        self.visible_objects = self.things.intersect_objects(State.camera.rect)

    def update_camera_position(self):
        """update the camera's position if star has moved
        """
        #for thing in list(self.things):
        #    position = thing.xyposition()
        if(self.movement):
            self.x = self.x + self.incx
            self.y = self.y + self.incy
    
        camera = State.camera
        wx, wy = self.x,self.y
        rect = State.world.rect
        wx = max(min(wx, rect.right), rect.left)
        wy = max(min(wy, rect.bottom), rect.top)
        camera.position = wx, wy
        print 'camera',camera.position


    def set_caption(self, dt):
        pygame.display.set_caption(self.caption + ' - {:.0f} fps'.format(round(State.clock.fps)))
    
    def draw(self, interp):
        """overrides Engine.draw"""
        # Draw stuff.
        State.screen.clear()
        toolkit.draw_tiles()
        self.draw_things()
        self.minimap.draw(self.things)
        State.screen.flip()
        
    def draw_things(self):
        # Balls move pretty fast, so we'll interpolate their movement to smooth
        # out the motion.
        camera = State.camera
        camera_pos = Vec2d(camera.rect.topleft)
        interp = State.camera.interp
        blit = camera.view.blit
        interpolated_step = toolkit.interpolated_step
        # Draw visible sprites...
        for s in self.visible_objects:
            x,y = interpolated_step(s.rect.topleft - camera_pos, s.dir, interp)
            #x,y = s.getxyposition()
            blit(s.image, (round(x), round(y)))
    
    def on_key_down(self, unicode, key, mod):
        # Turn on key-presses.
        camera = State.camera
        rect = State.world.rect
        if key == K_DOWN:
            camera_pos = Vec2d(camera.rect.bottomleft)
            #print KEYDOWN
            self.movement = 1
            for thing in list(self.things):
                thing.move(DOWN)
                #self.incx = 0
                if(camera_pos.y >= rect.bottom ):
                    self.incy = 0
                else:
                    self.incy = 4


        if key == K_UP:
            camera_pos = Vec2d(camera.rect.topleft)
            self.movement = 1
            for thing in list(self.things):
                thing.move(UP)
                #self.incx = 0
                if(camera_pos.y <= 0):
                    self.incy = 0
                else:
                    self.incy = -4

        if key == K_RIGHT:
            camera_pos = Vec2d(camera.rect.topright)
            self.movement = 1
            for thing in list(self.things):
                thing.move(RIGHT)
                if(camera_pos.x >= rect.right):
                    self.incx = 0
                else:
                    self.incx = 4
                #self.incy = 0
        if key == K_LEFT:
            camera_pos = Vec2d(camera.rect.topleft)
            self.movement = 1
            for thing in list(self.things):
                thing.move(LEFT)
                if(camera_pos.x <= rect.left):
                    self.incx = 0
                else:
                    self.incx = -4
                #self.incy = 0
        elif key == K_ESCAPE:
            context.pop()
        
    def on_key_up(self, key, mod):
        # Turn off key-presses.
        if key == K_DOWN:
            self.movement = 0
            for thing in list(self.things):
                thing.stopMove(DOWN)
        if key == K_UP:
            self.movement = 0
            for thing in list(self.things):
                thing.stopMove(UP)
        if key == K_RIGHT:
            self.movement = 0
            for thing in list(self.things):
                thing.stopMove(RIGHT)
        if key == K_LEFT:
            self.movement = 0
            for thing in list(self.things):
                thing.stopMove(LEFT)
        self.incx = self.incy = 0

        
    def on_quit(self):
        context.pop()
                     
            
            
        


	

