#!/usr/bin/env python

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

"""game_engine.py is the gummworld derived engine class for the ffmm

"""



import pygame
from pygame.sprite import Sprite
from pygame.locals import *

import paths
import gummworld2
from gummworld2 import *
from gummworld2.geometry import RectGeometry, CircleGeometry, PolyGeometry

import objects
import ffmm_spatialhash


class gameEngine(Engine):
    
    def __init__(self, resolution=(800, 600),strcaption = "no caption"):
        #setting resolution
        resolution = Vec2d(resolution)
        #creating instance of our avatar in screen
        self.avatar = objects.ourHero("horseman","horseman",(500, 770), resolution // 2)
        #engine initialization
        #   camera target: our avatar
        Engine.__init__(self, caption=strcaption,
                        camera_target= self.avatar,resolution=resolution, frame_speed=0)
        #self.map is our map created with tile editor
        self.map = TiledMap(data.filepath('map', 'test.tmx'))
        #create world with map size and the cell size
        self.cell_size = 50
        self.world = ffmm_spatialhash.game_SpatialHash(self.map.rect, self.cell_size)
        #  no idea
        self.set_state()
        #load entities from map, I think here we see collision rects, i.e.
        #removed temporally
        #entities, tilesheets = toolkit.load_entities(data.filepath('map', 'mini2.entities'))
        #for e in entities:
        #    State.world.add(e)
        
        # Create a speed box for converting mouse position to destination
        # and scroll speed. 800x600 has aspect ratio 8:6.
        self.speed_box = geometry.Diamond(0, 0, 8, 6)
        self.speed_box.center = Vec2d(State.camera.rect.size) // 2
        self.max_speed_box = float(self.speed_box.width) / 2.0
        
        # Mouse and movement state. move_to is in world coordinates.
        self.move_to = None
        self.speed = None
        self.mouse_down = False
        self.side_steps = []
        self.faux_avatar = objects.ourHero("horseman","horseman",self.camera.target.position, (10,0))

        #keyboard managment
        self.key_down = False
        self.move_x = 0
        self.move_y = 0
        self.new_x = 0
        self.new_y = 0
        
        State.show_world = False
        State.speed = 5


        # Use the renderer.
        self.renderer = BasicMapRenderer(self.map, max_scroll_speed=State.speed)
        
        # I like huds.
        toolkit.make_hud()
        State.clock.schedule_interval(State.hud.update, 1.0)
    
    #def setScreen(self, screen):
    #    self.screen = screen

    def update(self, dt):
        """overrides Engine.update"""
        # If mouse button is held down update for continuous walking.
        #if self.mouse_down:
        #    self.update_mouse_movement(pygame.mouse.get_pos())
        if self.key_down:
            self.update_keyboard_movement()     
        self.update_camera_position()
        self.renderer.set_rect(center=State.camera.rect.center)
        State.camera.update()
        self.avatar.update(State.screen)
  

    def update_mouse_movement(self, pos):
        # Final destination.
        self.move_to = None
        for edge in self.speed_box.edges:
            # line_intersects_line() returns False or (True,(x,y)).
            cross = geometry.line_intersects_line(edge, (self.speed_box.center, pos))
            if cross:
                x, y = cross[0]
                self.move_to = State.camera.screen_to_world(pos)
                self.speed = geometry.distance(
                    self.speed_box.center, (x, y)) / self.max_speed_box
                break
    #keyboard movement between cells
    def update_keyboard_movement(self):
        # Current position.
        camera = State.camera
        wx, wy = camera.position
        cell_id = self.world.index_at(wx,wy)
        row,col = self.world.get_cell_grid(cell_id)
        print("actual position: ",wx,wy," inside the cell: ",cell_id," row and col: ",row,col) 
        #new situation of new cell
        new_row = row + self.move_y
        new_col = col + self.move_x
        #does it exist?
        cell = self.world.get_cell_by_grid(new_col,new_row)
        if(cell == None):
           #doesnt exist
           return
        else:
           cell_id = self.world.index(cell)
           self.new_x,self.new_y = self.world.get_cell_pos(cell_id)
           row,col = self.world.get_cell_grid(cell_id)
           self.new_x += self.cell_size/2
           self.new_y += self.cell_size/2
           print("a la position: ",self.new_x,self.new_y," inside the cell: ",cell_id," row and col: ",row,col)
 
        
    def update_camera_position(self):
        """Step the camera's position if self.move_to contains a value.
        """
        #print("mover a",self.move_to)
        if self.move_to is not None:
            # Current position.
            camera = State.camera
            wx, wy = camera.position
            #print("coordenadas",wx,wy)
            #set dir to avatar
            direction = Vec2d(self.move_to[0]-wx,self.move_to[1]-wy)
            #print("DIRECCION!:",direction)
            self.avatar.move(direction)
            # Speed formula.
            speed = self.speed * State.speed
            # newx,newy is the new vector, which will be adjusted to avoid
            # collisions...

            if geometry.distance((wx, wy), self.move_to) < speed:
                # If within spitting distance, a full step would overshoot the
                # destination. Therefore, jump right to it.
                newx, newy = self.move_to
                self.move_to = None
            else:
                # Otherwise, calculate the full step.
                angle = geometry.angle_of((wx, wy), self.move_to)
                newx, newy = geometry.point_on_circumference((wx, wy), speed, angle)
        #by keyboard
        if(self.move_x != 0 or self.move_y !=0):
            # Current position.
            camera = State.camera
            wx, wy = camera.position
            #set dir to avatar
            direction = Vec2d(self.move_x,self.move_y)
            #print("DIRECCION!:",direction)
            self.avatar.move(direction)

            # Speed formula. 
            #gentooza, set to 3 to test
            #speed = 3
            # newx,newy is the new vector, which will be adjusted to avoid
            # collisions...
            # GENTOOZA
            #"*5" is the step length
            # we need to know the tile size to move one tile here!
            #this is only a test
            newx, newy = self.new_x,self.new_y

        if self.move_to is not None or self.move_x != 0 or self.move_y != 0:   
            # Check world collisions.

            world = State.world
            camera_target = camera.target
            dummy = self.faux_avatar
            dummy.position = camera_target.position
            dummy.rect = dummy.getRect()
            #gentooza
            #true collisions should be edited here, in can_step, taking care of the sprite rect
            def can_step(step):
                dummy.position = step
                #print("AVATAR POSITION!!",step)
                #print("AVATAR POSITION 2!!",dummy.getposition())
                return not world.collideany(dummy)

            # Remove camera target so it's not a factor in collisions.
            world.remove(camera_target)
            move_ok = can_step((newx, newy)) #we can trick can_step to aproach, or get far away a sprite from bounds,gentooza

            # We hit something. Try side-stepping.
            if not move_ok:
                newx = wx + pygame_utils.sign(newx - wx) * speed
                newy = wy + pygame_utils.sign(newy - wy) * speed
                
                for side_step in ((newx, wy),(wx, newy)):
                    move_ok = can_step(side_step)
                    if move_ok:
                        newx, newy = side_step
                        # End move_to if side-stepping backward from previous.
                        # This happens if we're trying to get through an
                        # obstacle with no valid path to take.
                        newstep = newx - wx, newy - wy
                        self.side_steps.append(newstep)
                        self.side_steps = self.side_steps[-2:]
                        for step in self.side_steps[:1]:
                            if step != newstep:
                                self.move_to = None
                                self.move_x = self.move_y = self.new_x = self.new_y = 0
                                break
                        break
            else:
                del self.side_steps[:]
            
            # Either we can move, or not.
            if not move_ok:
                # Reset camera position.
                self.move_to = None
                self.move_x = self.move_y = self.new_x = self.new_y =  0
            else:
                # Keep avatar inside map bounds.
                rect = State.world.rect
                #avatar_topleft,avatar_topright,avatar_bottomright,avatar_bottomleft = dummy.getpoints()
                #print("coordinates: ",newx,newy,"map limits: ",rect.left,rect.right,rect.top,rect.bottom,"sprite size: ",avatar_topright,avatar_topleft,avatar_bottomleft,avatar_bottomright)
                if newx < rect.left:
                    newx = rect.left 
                elif newx  > rect.right:
                    newx = rect.right
                if newy  < rect.top:
                    newy = rect.top 
                elif newy  > rect.bottom:
                    newy = rect.bottom 
                camera.position = newx, newy
        else:
            self.avatar.stopMove(Vec2d(0,0))
        
    def draw(self, interp):
        """overrides Engine.draw"""
        # Draw stuff.
        State.screen.clear()
        self.renderer.draw_tiles()
        self.draw_world()
        State.hud.draw()
        self.draw_avatar()
        State.screen.flip()
        
    def draw_world(self):
        """Draw the on-screen shapes in the world.
        """
        if not State.show_world:
            return
        
        camera = State.camera
        camera_target = camera.target
        things = State.world.intersect_objects(camera.rect)
        display = camera.view.surface
        world_to_screen = camera.world_to_screen
        color = Color('white')
        
        draw_rect = pygame.draw.rect
        draw_circle = pygame.draw.circle
        draw_poly = pygame.draw.lines
        
        for thing in things:
            if thing is not camera_target:
                if isinstance(thing, RectGeometry):
                    r = thing.rect.copy()
                    r.center = world_to_screen(thing.position)
                    draw_rect(display, color, r, 1)
                elif isinstance(thing, CircleGeometry):
                    draw_circle(display, color, world_to_screen(thing.position), thing.radius, 1)
                elif isinstance(thing, PolyGeometry):
                    points = [world_to_screen(p) for p in thing.points]
                    draw_poly(display, color, True, points)
    
    def draw_avatar(self):
        camera = State.camera
        avatar = camera.target
        camera.surface.blit(avatar.image, avatar.screen_position)
        #self.avatar.draw(self.screen)
        
    def on_mouse_button_down(self, pos, button):
        self.mouse_down = True
        
    def on_mouse_button_up(self, pos, button):
        self.mouse_down = False
        
    def on_key_down(self, unicode, key, mod):
        # Turn on key-presses.
        if key == K_DOWN:
            self.key_down = True
            self.move_y = 1    
        if key == K_UP:
            self.key_down = True
            self.move_y = -1 
        if key == K_RIGHT:
            self.key_down = True
            self.move_x = 1
        if key == K_LEFT:
            self.key_down = True
            self.move_x = -1 
        if key == K_TAB:
            State.show_world = not State.show_world
        if key == K_ESCAPE:
            context.pop()

        
    def on_key_up(self, key, mod):
        # Turn off key-presses.
        if key in (K_DOWN, K_UP):
            self.key_down = False
            self.move_y = 0
        elif key in (K_RIGHT, K_LEFT):
            self.key_down = False
            self.move_x = 0

        
    def on_quit(self):
        context.pop()
        
    # App.on_quit

