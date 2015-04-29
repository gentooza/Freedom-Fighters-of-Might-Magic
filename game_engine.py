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


class gameEngine(Engine):
    
    def __init__(self, resolution=(1014, 965),strcaption = "no caption"):
        #setting resolution
        resolution = Vec2d(resolution)
        #creating instance of our avatar in screen
        self.avatar = objects.ourHero("horseman","horseman",(30, 30), (0,0))

        #self.map is our map created with tile editor
        worldmap = TiledMap(data.filepath('map', 'test.tmx'))
        #heores layer of the map edited with Tiled
        self.avatar_group = worldmap.layers[1]
        ## Tell the renderer this layer needs to be sorted, and how to.
        self.avatar_group.objects.sort_key = lambda o: o.rect.bottom

        #engine initialization
        #   camera target: our avatar
        Engine.__init__(self, caption=strcaption,
                        camera_target= self.avatar,resolution=resolution,map =worldmap, frame_speed=0,camera_view_rect=pygame.Rect(0, 27, 833, 938))

        # Conserve CPU.
        State.clock.use_wait = True

        ## Insert avatar into the Fringe layer.
        self.avatar_group.add(self.avatar)

        ## The renderer.
        self.renderer = BasicMapRenderer(
            worldmap, max_scroll_speed=State.speed)
        ## New requirement. When renderer draws dynamic layers (e.g. Fringe)
        ## we need to tell it to redraw the changed tiles. This also is done
        ## in the draw cycle; see self.draw_renderer().
        self.dirty_rect = Rect(self.avatar.rect)
        self.renderer.set_dirty(self.dirty_rect)

        # I like huds.
        ui.text_color = Color('black')
        toolkit.make_hud()
        State.hud.add('Max FPS',
                      Statf(State.hud.next_pos(), 'Max FPS {:.0f}',
                            callback=lambda: (State.clock.max_fps,), interval=1.0))
        State.hud.add('Use Wait',
                      Statf(State.hud.next_pos(), 'Use Wait {}',
                            callback=lambda: (State.clock.use_wait,), interval=1.0))
        State.hud.add('Tile Size',
                      Statf(State.hud.next_pos(), 'Tile Size {} pixels (key={})',
                            callback=lambda: (self.renderer.tile_size, State.camera.rect.w // self.renderer.tile_size),
                            interval=1.0))


        #create world with map size and the cell size
        self.cell_size = 60
        self.world = ffmm_spatialhash.game_SpatialHash(worldmap.rect, self.cell_size)
        #  no idea
        #self.set_state()
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
        self.final_cell_id = None
        self.step = []
        self.path = 'stop'

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
     
        #game interface!
        self.interface = game_interface.gameInterface(State.screen)
    
    #def setScreen(self, screen):
    #    self.screen = screen

    def update(self, dt):
        """overrides Engine.update"""
        # If mouse button is held down update for continuous walking.
        if self.mouse_down:
            self.update_mouse_movement(pygame.mouse.get_pos())
        if self.key_down:
            self.update_keyboard_movement()     
        self.update_camera_position()
        State.camera.update()
        self.anim_avatar()
        State.hud.update(dt)
        #steps

    def update_mouse_movement(self, pos):
        # Final destination.
        self.move_to = None
        # we need tl paint arrows to destination
        #if we have no destination we prepare the path!
        if (self.final_cell_id == None):
           #destination
           pos = State.camera.screen_to_world(pos)
           self.final_cell_id = self.world.index_at(pos[0],pos[1])
           if(self.final_cell_id == None):
              return;
           row,col = self.world.get_cell_grid(self.final_cell_id)
           #origin
           camera = State.camera
           wx, wy = camera.target.position
           cell_id = self.world.index_at(wx,wy)
           orig_row,orig_col = self.world.get_cell_grid(cell_id)
           print("avatar position: ",wx,wy," destination position: ",pos)
           if(orig_row == row and orig_col == col):
              return;
           #steps
           if(orig_row >= row):
              for i in range(row,orig_row):
                 print("x,y : ",self.world.get_cell_pos(self.world.index(self.world.get_cell_by_grid(orig_col,i)))) 
                 self.step.append(self.world.index(self.world.get_cell_by_grid(orig_col,i)))
           else:
               for i in range(orig_row,row):
                 print("x,y : ",self.world.get_cell_pos(self.world.index(self.world.get_cell_by_grid(orig_col,i))))
                 self.step.append(self.world.index(self.world.get_cell_by_grid(orig_col,i)))
           if(orig_col >= col):
              for i in range(col,orig_col):
                 print("x,y : ",self.world.get_cell_pos(self.world.index(self.world.get_cell_by_grid(i,row)))) 
                 self.step.append(self.world.index(self.world.get_cell_by_grid(i,row)))
           else:
               for i in range(orig_col,col):
                 print("x,y : ",self.world.get_cell_pos(self.world.index(self.world.get_cell_by_grid(i,row)))) 
                 self.step.append(self.world.index(self.world.get_cell_by_grid(i,row)))
        else:
           pos = State.camera.screen_to_world(pos)
           cell = self.world.index_at(pos[0],pos[1])
           #if clicked the same destination again
           #movement starts!!
           if(cell == self.final_cell_id):
              pos = self.world.get_cell_pos(self.step.pop(0))
              self.move_to = pos[0]+self.cell_size/2,pos[1]+self.cell_size/2
           else:
              self.step.clear()
              self.final_cell_id = cell
              if(self.final_cell_id == None):
                 return;
              row,col = self.world.get_cell_grid(self.final_cell_id)
              #origin
              camera = State.camera
              wx, wy = camera.target.position

              cell_id = self.world.index_at(wx,wy)
              orig_row,orig_col = self.world.get_cell_grid(cell_id)
              print("avatar position: ",wx,wy," destination position: ",pos)
              if(orig_row == row and orig_col == col):
                 return;
              #steps
              if(orig_row >= row):
                 for i in range(row,orig_row):
                    print("x,y : ",self.world.get_cell_pos(self.world.index(self.world.get_cell_by_grid(orig_col,i))))
                    self.step.append(self.world.index(self.world.get_cell_by_grid(orig_col,i)))
              else:
                 for i in range(orig_row,row):
                    print("x,y : ",self.world.get_cell_pos(self.world.index(self.world.get_cell_by_grid(orig_col,i))))
                    self.step.append(self.world.index(self.world.get_cell_by_grid(orig_col,i)))
              if(orig_col >= col):
                 for i in range(col,orig_col):
                    print("x,y : ",self.world.get_cell_pos(self.world.index(self.world.get_cell_by_grid(i,row))))
                    self.step.append(self.world.index(self.world.get_cell_by_grid(i,row)))
              else:
                 for i in range(orig_col,col):
                    print("x,y : ",self.world.get_cell_pos(self.world.index(self.world.get_cell_by_grid(i,row))))
                    self.step.append(self.world.index(self.world.get_cell_by_grid(i,row)))

    #keyboard movement between cells
    def update_keyboard_movement(self):
        # Current position.
        camera = State.camera
        wx, wy = camera.target.position
        cell_id = self.world.index_at(wx,wy)
        row,col = self.world.get_cell_grid(cell_id)
        #print("actual position: ",wx,wy," inside the cell: ",cell_id," row and col: ",row,col) 
        #new situation of new cell
        if(row == 0 and self.move_y < 0):
           new_row = row
        else:
           new_row = row + self.move_y
        if(col == 0 and self.move_x < 0):
           new_col = col
        else:
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
           #print("a la position: ",self.new_x,self.new_y," inside the cell: ",cell_id," row and col: ",row,col)
        self.step.clear()
 
        
    def update_camera_position(self):
        camera = State.camera
        """Step the camera's position if self.move_to contains a value.
        """
        #print("mover a",self.move_to)
    #    if (self.final_cell_id != None and self.move_to != None):
            # Current position.
    #        camera = State.camera
    #        wx, wy = camera.position
    #        self.new_x = self.move_to[0]
    #        self.new_y = self.move_to[1]
            #print("coordenadas",wx,wy)
            #set dir to avatar
    #        direction = Vec2d(self.move_to[0]-wx,self.move_to[1]-wy)
            #print("DIRECCION!:",direction)
    #        self.avatar.move(direction)
    #        newx, newy = self.new_x,self.new_y

            #new step
    #        pos = self.world.get_cell_pos(self.step.pop(0))
    #        if(pos == None):
    #           #finished
    #           self.final_cell_id = None
    #           self.move_to = None
    #        else:
    #           self.move_to = pos[0]+self.cell_size/2,pos[1]+self.cell_size/2
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

     #   if self.move_to is not None or self.move_x != 0 or self.move_y != 0:  
        if(self.move_x != 0 or self.move_y != 0):
            # Check world collisions.

            world = State.world
            camera_target = camera.target
            dummy = self.faux_avatar
            dummy.position = camera_target.position
            dummy.rect = dummy.getRect()
            #gentooza
            #true collisions should be edited here, in can_step, taking care of the sprite rect
            #COLLISIONS WITH LAYER
            #def can_step(step):
            #    dummy.position = step
                #print("AVATAR POSITION!!",step)
                #print("AVATAR POSITION 2!!",dummy.getposition())
            #    return not world.collideany(dummy)

            # Remove camera target so it's not a factor in collisions.
            #world.remove(camera_target)
            #move_ok = can_step((newx, newy)) #we can trick can_step to aproach, or get far away a sprite from bounds,gentooza

            # We hit something. Try side-stepping.
            #if not move_ok:
            #    newx = wx + pygame_utils.sign(newx - wx) * speed
            #    newy = wy + pygame_utils.sign(newy - wy) * speed
            #    
            #    for side_step in ((newx, wy),(wx, newy)):
            #        move_ok = can_step(side_step)
            #        if move_ok:
            #            newx, newy = side_step
                        # End move_to if side-stepping backward from previous.
                        # This happens if we're trying to get through an
                        # obstacle with no valid path to take.
            #            newstep = newx - wx, newy - wy
            #            self.side_steps.append(newstep)
            #            self.side_steps = self.side_steps[-2:]
            #            for step in self.side_steps[:1]:
            #                if step != newstep:
            #                    self.move_to = None
            #                    self.move_x = self.move_y = self.new_x = self.new_y = 0
            #                     break
            #            break
            #else:
            #    del self.side_steps[:]
            
            # Either we can move, or not.
            #if not move_ok:
                # Reset camera position.
            #    self.move_to = None
            #    self.move_x = self.move_y = self.new_x = self.new_y =  0
            #else:
                # Keep avatar inside map bounds.
            rect = State.world.rect
                #avatar_topleft,avatar_topright,avatar_bottomright,avatar_bottomleft = dummy.getpoints()
                #print("coordinates: ",newx,newy,"map limits: ",rect.left,rect.right,rect.top,rect.bottom,"sprite size: ",avatar_topright,avatar_topleft,avatar_bottomleft,avatar_bottomright)
            if newx < rect.left:
                newx = rect.left 
            elif newx  >= rect.right:
                newx = rect.right - self.cell_size/2
            if newy  < rect.top:
                newy = rect.top 
            elif newy  >= rect.bottom:
                newy = rect.bottom - self.cell_size/2
            camera.position = newx, newy
            print(newx,newy)
            self.avatar.position = camera.target.position
            #self.avatar_group.add(self.avatar)
        else:
            self.avatar.stopMove(Vec2d(0,0))
            self.avatar.position = camera.target.position
            #self.avatar_group.add(self.avatar)
        
    def draw(self, interp):
        """overrides Engine.draw"""
        # Draw stuff.
        State.screen.clear()
        #self.anim_avatar()
        self.draw_renderer()
        if False:
           self.draw_debug()
        State.hud.draw()
        self.draw_steps()
        self.interface.draw(State.screen,self.avatar_group)
        State.screen.flip()


    def draw_renderer(self):
        """renderer draws map layers"""
        
        renderer = self.renderer
        
        # If panning, mark the renderer's tiles dirty where avatar is.
        panning = False
        camera = State.camera
        camera_rect = camera.rect
        dirty_rect = self.dirty_rect
        camera_center = camera_rect.center
        if camera.target.rect.center != camera_center:
            dirty_rect.center = camera_center
            renderer.set_dirty(dirty_rect)
            panning = True
        
        # Set render's rect and draw the screen.
        renderer.set_rect(center=camera_center)
        renderer.draw_tiles()
        
        # Must mark dirty rect before next call to draw(), otherwise avatar
        # leaves little artifacts behind.
        if panning:
            renderer.set_dirty(dirty_rect)

    def draw_steps(self):
        self.arrows = None
        
        if(self.step == []):
          return;
    
        camera = State.camera
        for element in self.step:
           x,y  = self.world.get_cell_pos(element)
           x += self.cell_size/2
           y += self.cell_size/2
           arrow = objects.arrow_step("arrow.png","misc",(x,y))
           #drawing arrow!
           #print("drawing arrow") 
           #self.avatar_group.add(arrow)
           camera.surface.blit(arrow.image, camera.world_to_screen(arrow.position))

    
    def draw_debug(self):
        # draw the hitbox and speed box
        camera = State.camera
        cx, cy = camera.rect.topleft
        rect = self.avatar.hitbox
        pygame.draw.rect(camera.surface, Color('red'), rect.move(-cx, -cy))
        pygame.draw.polygon(camera.surface, Color('white'), self.speed_box.corners, 1)      
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
    
    def anim_avatar(self):
        #self.avatar.update()
        #camera = State.camera
        #avatar = camera.target
        #camera.surface.blit(avatar.image, camera.world_to_screen(avatar.position))
        self.avatar.update()
        self.avatar_group.add(self.avatar)
        
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

