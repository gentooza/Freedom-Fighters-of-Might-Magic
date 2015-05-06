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
#from pygame.sprite import Sprite
from pygame.locals import *

import paths
import gummworld2
from gummworld2 import context, data, model, geometry, toolkit, ui,Engine, State, TiledMap, BasicMapRenderer, Vec2d, Statf
from gummworld2.geometry import RectGeometry, CircleGeometry, PolyGeometry

import objects
import game_interface
import ffmm_spatialhash
import path_finding
import game_dynamics

katrin =  {'name':'katrin','faction' : 'human','portrait': 'katrin','attack':2,'deffense':2,'magic_p':1,'magic_k':1}
sandro =  {'name':'sandro','faction' : 'undead','portrait': 'sandro','attack':1,'deffense':0,'magic_p':2,'magic_k':2}
heroes = {'katrin':katrin,'sandro':sandro}

class gameEngine(Engine):
    
    def __init__(self, resolution=(1014, 965),strcaption = "no caption"):
        #setting resolution
        resolution = Vec2d(resolution)
        #creating instance of our avatar in screen
        #self.avatar = objects.ourHero("horseman","horseman",(30, 30), (0,0))
        #self.avatar.team = 1
        #self.avatar.attr = katrin

        #self.map is our map created with tile editor
        #we load all information from map
        worldmap = TiledMap(data.filepath('map', 'test.tmx'))
        #heores layer of the map edited with Tiled
        self.avatar_group = worldmap.layers[2]
        self.terrain_layer = worldmap.layers[0]
        self.collision_layer = worldmap.layers[1]
        self.objects_layer = worldmap.layers[3]

        self.factions = game_dynamics.factions(self.objects_layer)

        self.actual_team = self.factions.team.pop(0)
        self.avatar = self.actual_team.heroes.pop(0)

        #for element in  self.terrain_layer.objects:
        #   print(element.properties)
       
        ## Tell the renderer this layer needs to be sorted, and how to.
        self.avatar_group.objects.sort_key = lambda o: o.rect.bottom

        #engine initialization
        #   camera target: our avatar
        Engine.__init__(self, caption=strcaption,
                        camera_target= self.avatar,resolution=resolution,display_flags=pygame.FULLSCREEN,map =worldmap, frame_speed=0,camera_view_rect=pygame.Rect(0, 27, 833, 741))

        # Conserve CPU.
        State.clock.use_wait = True

        ## Insert avatars into the Fringe layer.
        self.avatar_group.add(self.avatar)
        #others avatars in actual team
        for avatars in self.actual_team.heroes:
           self.avatar_group.add(avatars)
        #others avatars in others teams
        for teams in self.factions.team:
           for avatars in teams.heroes:
              self.avatar_group.add(avatars)
        ##################
        #Game dynamics
        self.endturn = False
        ###################
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
        self.mouse_down = False #left click
        self.mouse_down2 = False  #right click
        self.side_steps = []
        self.faux_avatar = objects.ourHero("horseman","horseman",self.camera.target.position, (10,0))
        self.final_cell_id = None
        self.path = []
        self.mouse_reponse = 3
        self.iterator = 0
        self.pathstep = None
        self.lastpathstep = None 
        self.cellstep = None
        self.lastcellstep = None 
        #self.path = 'stop'

        #keyboard managment
        self.key_down = False
        self.move_x = 0
        self.move_y = 0
        self.new_x = 0
        self.new_y = 0
        self.step = Vec2d(0,0)


        self.laststepx = 0
        self.laststepy = 0
        
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
        if self.endturn:
           self.endturn_fun()
        # If mouse button is held down update for continuous walking.
        self.iterator+=1
        if self.iterator >= self.mouse_reponse:
           if self.mouse_down:
               self.update_mouse_movement(pygame.mouse.get_pos())
           self.iterator = 0
        if self.mouse_down2:
           self.popup(pygame.mouse.get_pos())
        if self.key_down:
            self.update_keyboard_movement()     
        self.update_camera_position()
        State.camera.update()
        self.anim_avatar()
        State.hud.update(dt)
        #steps
        

    def update_mouse_movement(self, pos):
        #checking map edges
        rect = State.world.rect
        world_pos = State.camera.screen_to_world(pos)
        #if mouse click is outside the map we do nothing!
        if world_pos[0] < rect.left:
           return;
        elif world_pos[0]  >= rect.right:
           return;
        if world_pos[1]  < rect.top:
           return;
        elif world_pos[1]  >= rect.bottom:
           return;

        # Final destination reset.
        self.move_to = None
        ##
        #if we have no destination we prepare the path to the cell of coordinates given by mouse click!
        if (self.final_cell_id == None):
           self.path,self.final_cell_id = path_finding.pos2steps(pos,self.world,self.terrain_layer,self.collision_layer)
        #if we already have a destination
        else:
           world_pos = State.camera.screen_to_world(pos)
           cell = self.world.index_at(world_pos[0],world_pos[1])
           #if clicked the same destination again
           #movement starts!!
           if(cell == self.final_cell_id and self.path and self.avatar.movement == 0):
              self.getStepFromPath()
              #print(self.step)
              
           #else, new path
           else:
              self.interruptpath()
              self.path.clear()
              self.lastpathstep = None
              self.pathstep = None
              self.path,self.final_cell_id = path_finding.pos2steps(pos,self.world,self.terrain_layer,self.collision_layer)

    #keyboard movement between cells
    def update_keyboard_movement(self):
        # Gummchange
        if self.move_x == 0 and self.move_y == 0:
            return
        # print('CALCULATING MOVE_TO')
        # end Gummchange
        #if we are moving, interrupt!
        self.interruptpath()
        ############################
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
           #collisions
           if(self.collision_layer.get_objects_in_rect(pygame.Rect(self.new_x,self.new_y,self.cell_size,self.cell_size))):
              self.new_x = 0
              self.new_y = 0
              return; 
           row,col = self.world.get_cell_grid(cell_id)
           self.new_x += self.cell_size/2
           self.new_y += self.cell_size/2
           
           # Gummchange
           self.move_to = Vec2d(self.new_x, self.new_y)
           self.step = Vec2d(self.move_x, self.move_y)
           #print("to position: ",self.new_x,self.new_y," inside the cell: ",cell_id," row and col: ",row,col)
        self.path.clear()
        self.lastpathstep = None
        self.pathstep = None
 
    def update_camera_position(self):
        # if move_to, then the camera needs to keep stepping towards the destination tile.
        if self.move_to:
            #print('STEP pos{} -> dest{} by step{}'.format(
            #    tuple(self.camera.position), tuple(self.move_to), tuple(self.step)))
            camx, camy = self.camera.position
            stepx, stepy = self.step
            #pay attention, if we are in a mouse movement we take next step
            # Check if camx has arrived at the move_to point. If it has set stepx to 0.
            if camx == self.move_to[0]:
                stepx = 0
            # Check if camy has arrived at the move_to point. If it has set stepy to 0.
            if camy == self.move_to[1]:
                stepy = 0
            #if arrived
            if(camx == self.move_to[0] and camy == self.move_to[1]):
            #if it was only one step of the whole path, we take the next 
               if(self.final_cell_id and self.path):
                  self.getStepFromPath() 
                  stepx, stepy = self.step
            #checking map edges
            rect = State.world.rect
            if self.move_to[0] < rect.left:
                stepx=0
                stepy=0 
            elif self.move_to[0]  >= rect.right:
                stepx=0
                stepy=0 
            if self.move_to[1]  < rect.top:
                stepx=0
                stepy=0
            elif self.move_to[1]  >= rect.bottom:
                stepx=0
                stepy=0
            # If steps remain on the x or y axis, update the camera position. Else, the
            # camera/avatar is done moving, so set self.move_to = None.
            if stepx or stepy:
                self.laststepx = stepx
                self.laststepy = stepy
                self.camera.position += stepx, stepy
                #avatar animation
                self.avatar.move(Vec2d(stepx,stepy))
            else:
                #print("stop moving {},{}".format(int(self.laststepx),int(self.laststepy)))
                self.move_to = None
                #avatar animation
                self.avatar.stopMove(Vec2d(self.laststepx,self.laststepy))
                self.laststepx = self.laststepy = 0
                
       
        
#LEGACY    def update_camera_position(self):
#        camera = State.camera
# 
#        if(self.move_x != 0 or self.move_y !=0):
#            # Current position.
#            camera = State.camera
#            wx, wy = camera.position
#            #set dir to avatar
#            direction = Vec2d(self.move_x,self.move_y)
#            #print("DIRECCION!:",direction)
#            self.avatar.move(direction)
#
#            newx, newy = self.new_x,self.new_y
#
#     #   if self.move_to is not None or self.move_x != 0 or self.move_y != 0:  
#        if(self.move_x != 0 or self.move_y != 0):
#            # Check world collisions.
#
#            world = State.world
#            camera_target = camera.target
#            dummy = self.faux_avatar
#            dummy.position = camera_target.position
#            dummy.rect = dummy.getRect()
#            #gentooza
#            #true collisions should be edited here, in can_step, taking care of the sprite rect
#            #COLLISIONS WITH LAYER
#            #def can_step(step):
#            #    dummy.position = step
#                #print("AVATAR POSITION!!",step)
#                #print("AVATAR POSITION 2!!",dummy.getposition())
#            #    return not world.collideany(dummy)
#
#            # Remove camera target so it's not a factor in collisions.
#            #world.remove(camera_target)
#            #move_ok = can_step((newx, newy)) #we can trick can_step to aproach, or get far away a sprite from bounds,gentooza
#
#            # We hit something. Try side-stepping.
#            #if not move_ok:
#            #    newx = wx + pygame_utils.sign(newx - wx) * speed
#            #    newy = wy + pygame_utils.sign(newy - wy) * speed
#            #    
#            #    for side_step in ((newx, wy),(wx, newy)):
#            #        move_ok = can_step(side_step)
#            #        if move_ok:
#            #            newx, newy = side_step
#                        # End move_to if side-stepping backward from previous.
#                        # This happens if we're trying to get through an
#                        # obstacle with no valid path to take.
#            #            newstep = newx - wx, newy - wy
#            #            self.side_steps.append(newstep)
#            #            self.side_steps = self.side_steps[-2:]
#            #            for step in self.side_steps[:1]:
#            #                if step != newstep:
#            #                    self.move_to = None
#            #                    self.move_x = self.move_y = self.new_x = self.new_y = 0
#            #                     break
#            #            break
#            #else:
#            #    del self.side_steps[:]
#            
#            # Either we can move, or not.
#            #if not move_ok:
#                # Reset camera position.
#            #    self.move_to = None
#            #    self.move_x = self.move_y = self.new_x = self.new_y =  0
#            #else:
#                # Keep avatar inside map bounds.
#            rect = State.world.rect
#                #avatar_topleft,avatar_topright,avatar_bottomright,avatar_bottomleft = dummy.getpoints()
#                #print("coordinates: ",newx,newy,"map limits: ",rect.left,rect.right,rect.top,rect.bottom,"sprite size: ",avatar_topright,avatar_topleft,avatar_bottomleft,avatar_bottomright)
#            if newx < rect.left:
#                newx = rect.left 
#            elif newx  >= rect.right:
#                newx = rect.right - self.cell_size/2
#            if newy  < rect.top:
#                newy = rect.top 
#            elif newy  >= rect.bottom:
#                newy = rect.bottom - self.cell_size/2
#            camera.position = newx, newy
#            print(newx,newy)
#            self.avatar.position = camera.target.position
#            #self.avatar_group.add(self.avatar)
#        else:
#            self.avatar.stopMove(Vec2d(0,0))
#            self.avatar.position = camera.target.position
#            #self.avatar_group.add(self.avatar)
        
    def draw(self, interp):
        """overrides Engine.draw"""
        # Draw stuff.
        State.screen.clear()
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
        
        if(not self.path):
          return;
    
        camera = State.camera
        for element in self.path:
           y,x  = self.world.get_cell_pos(element)
           x += self.cell_size/2
           y += self.cell_size/2
           arrow = objects.arrow_step("dot-white.png","misc",(x,y))
           camera.surface.blit(arrow.image, camera.world_to_screen(arrow.position))

    
    def draw_debug(self):
        # draw the hitbox and speed box
        camera = State.camera
        cx, cy = camera.rect.topleft
        rect = self.avatar.hitbox
        pygame.draw.rect(camera.surface, Color('red'), rect.move(-cx, -cy))
        pygame.draw.polygon(camera.surface, Color('white'), self.speed_box.corners, 1)   
   
  
    
    def anim_avatar(self):
        #self.avatar.update()
        #camera = State.camera
        #avatar = camera.target
        #camera.surface.blit(avatar.image, camera.world_to_screen(avatar.position))
        self.avatar.update()
        self.avatar_group.add(self.avatar)
        
    def on_mouse_button_down(self, pos, button):
       if(button == 1): 
          self.mouse_down = True
          self.interface.erasehpopup()
       else:
          self.mouse_down2 = True
        
    def on_mouse_button_up(self, pos, button):
        if(button == 1):
           self.mouse_down = False
        else:
           self.mouse_down2 = False
        
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
        if key == K_SPACE:
            self.endturn = True
        if key == K_ESCAPE:
            context.pop()
        self.interface.erasehpopup()

        
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
#####GAME DYNAMICS
    def interruptpath(self):
       if self.lastpathstep:
          print(self.lastpathstep)
          stepx,stepy = self.lastpathstep
          self.move_to = None
          #avatar animation
          self.camera.position = stepx,stepy
          self.avatar.stopMove(Vec2d(stepx,stepy))
          

    def endturn_fun(self):

        print('endturn function!')
        self.interruptpath()
        self.avatar.stopMove(Vec2d(0,0))
        #path saving
        self.avatar.saved_path = self.path.copy()
        ############
        self.actual_team.heroes.append(self.avatar)     
        self.factions.team.append(self.actual_team)
       
        self.actual_team = None
        self.avatar = None

        self.actual_team = self.factions.team.pop(0)
        self.avatar = self.actual_team.heroes.pop(0)
        
        ## Insert avatars into the Fringe layer.
        self.avatar_group.add(self.avatar)
        #others avatars in actual team
        for avatars in self.actual_team.heroes:
           self.avatar_group.add(avatars)
        #others avatars in others teams
        for teams in self.factions.team:
           for avatars in teams.heroes:
              self.avatar_group.add(avatars)
        #path saving an restoring
        self.lastpathstep = self.pathstep = None
        if self.avatar.saved_path:
           self.path.clear()
           self.path = self.avatar.saved_path.copy()
           self.move_to = None
           self.step = None

        camx, camy = self.camera.position  
        self.move_to = Vec2d(camx,camy)
        self.step = Vec2d(0,0)
        self.camera.target = self.avatar
        self.endturn = False


#####INTERFACE
    def popup(self,pos):
       rect = State.world.rect
       world_pos = State.camera.screen_to_world(pos)
       cell_position = self.world.index_at(world_pos[0],world_pos[1])
       
       #on avatar click?
       wx,wy = State.camera.target.position
       cell_avatar = self.world.index_at(wx,wy)
       if(cell_avatar == cell_position): #show avatar popup!
           popup_pos = pos[0],pos[1]
           self.interface.createhpopup(State.screen,popup_pos,self.avatar)
       else:
           self.interface.erasehpopup()

#####UTILS
    '''it returns self.move_to and self.step from path'''
    def getStepFromPath(self):
        self.lastcellstep = self.cellstep
        if(self.lastcellstep):
           pos = self.world.get_cell_pos(self.lastcellstep)
           self.laststeppath = Vec2d(pos[1]+self.cell_size/2,pos[0]+self.cell_size/2)
        cell_id =  self.path.pop(0)
        self.cellstep = cell_id
        #if cell 0 is origin we take the next
        camera = State.camera
        wx, wy = camera.target.position
        cell_avatar = self.world.index_at(wx,wy)
        if(cell_id == cell_avatar and self.path): 
            cell_id =  self.path.pop(0) 
        ##
        #DEBUG 
        #print('to cell id: ',cell_id)
        pos = self.world.get_cell_pos(cell_id)
           
        self.move_to = Vec2d(pos[1]+self.cell_size/2,pos[0]+self.cell_size/2)
        self.new_x = self.move_to[0]# + self.cell_size/2
        self.new_y = self.move_to[1]# + self.cell_size/2
        #step calculation
        o_col,o_row = self.world.get_cell_grid(cell_avatar)
        d_col,d_row = self.world.get_cell_grid(cell_id)
              
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
        self.step = Vec2d( row,col)        
    # App.on_quit

