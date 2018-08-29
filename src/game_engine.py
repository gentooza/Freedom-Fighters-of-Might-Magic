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

import gummworld2
from gummworld2 import Engine, Vec2d, TiledMap, data, State, BasicMapRenderer, toolkit, geometry, SpatialHash

from AI import path_finding

import utils
import objects
import game_interface
import game_dynamics
import pygbutton
import sounds
import random

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BACKGROUND = (20,20,20)

katrin =  {'name':'katrin','faction' : 'human','portrait': 'katrin','attack':2,'deffense':2,'magic_p':1,'magic_k':1}
sandro =  {'name':'sandro','faction' : 'undead','portrait': 'sandro','attack':1,'deffense':0,'magic_p':2,'magic_k':2}
heroes = {'katrin':katrin,'sandro':sandro}


class gameEngine(Engine):
    
    def __init__(self, parameters,gameSounds):
        #playing sounds
        self.gameSounds = gameSounds
        self.gameSounds.playworld(True,0.6)
        #setting parameters
        resolution = Vec2d(parameters['resolution'])
        
        self.parameters = parameters
        if(parameters['fullscreen']):
           flags = pygame.FULLSCREEN
        else:
           flags = 0
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
        #loading factions
        self.factions = game_dynamics.factions(self.objects_layer)

        self.actual_team = self.factions.team.pop(0)
        self.avatar = self.actual_team.heroes.pop(0)
        self.avatar.remaining_movement = self.avatar.move_points
        
        #loading creatures
        self.creatures = game_dynamics.creatures(self.objects_layer)
        #for element in  self.terrain_layer.objects:
        #   print(element.properties)
       
        ## Tell the renderer this layer needs to be sorted, and how to.
        self.avatar_group.objects.sort_key = lambda o: o.rect.bottom

        #engine initialization
        #   camera target: our avatar
        #Engine.__init__(self, caption=strcaption,camera_target= self.avatar,resolution=resolution,display_flags=pygame.FULLSCREEN,map =worldmap, frame_speed=0,camera_view_rect=pygame.Rect(0, 27, 833, 741))
        Engine.__init__(self, caption=parameters['strcaption'],camera_target= self.avatar,resolution=resolution, display_flags=flags,map =worldmap, frame_speed=0,camera_view_rect=pygame.Rect(0, 27, self.parameters["resolution"][0]-183, self.parameters["resolution"][1]-27))
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
        for group in self.creatures.group:
            self.avatar_group.add(group.creature)
       
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

        # Make the hud.
        self.hud = toolkit.make_default_hud(theme='vera')
        # I like huds.
        #toolkit.make_hud()
        #State.hud.add('Max FPS',
        #              Statf(State.hud.next_pos(), 'Max FPS {:.0f}',
        #                    callback=lambda: (State.clock.max_fps,), interval=1.0))
        #State.hud.add('Use Wait',
        #              Statf(State.hud.next_pos(), 'Use Wait {}',
        #                    callback=lambda: (State.clock.use_wait,), interval=1.0))
        #State.hud.add('Tile Size',
        #              Statf(State.hud.next_pos(), 'Tile Size {} pixels (key={})',
        #                    callback=lambda: (self.renderer.tile_size, State.camera.rect.w // self.renderer.tile_size),
        #                    interval=1.0))


        #create world with map size and the cell size
        self.cell_size = 60
        self.world = SpatialHash(self.cell_size)
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
        self.move_to_G = 0
        self.speed = None
        self.mouse_down = False #left click
        self.mouse_down2 = False  #right click
        self.side_steps = []
        self.faux_avatar = objects.ourHero("horseman","horseman",self.camera.target.position, (10,0),0)
        self.final_cell_id = None
        self.path = path_finding.path()

        self.mouse_reponse = 4
        self.iterator = 0
        
        self.pathstep = None
        self.laststeppath = None 
        self.cellstep = None
        self.lastcellstep = None
        self.lastcellG = 0
        self.cellG = 0


        #keyboard managment
        self.key_down = False
        self.move_x = 0
        self.move_y = 0
        self.new_x = 0
        self.new_y = 0
        self.step = Vec2d(0,0)
        
        #computer movement
        self.pc_mov_cost = 0


        self.laststepx = 0
        self.laststepy = 0
        
        State.show_world = False
        State.speed = 5


        # Use the renderer.
        self.renderer = BasicMapRenderer(self.map, max_scroll_speed=State.speed)
             
        #game interface!
        self.interface = game_interface.gameInterface(State.screen, self.parameters)
        #populating game interface
        self.populating_interface()
    
    #def setScreen(self, screen):
    #    self.screen = screen

    def update(self, dt):
        """overrides Engine.update"""
        #endturn
        if self.actual_team.player == 'human':
           if self.endturn and not self.avatar.movement:
              self.endturn_fun()
        else:
           #print('computer turn!')
           if self.actual_team.end_turn and not self.avatar.movement:
              self.actual_team.end_turn = 0
              self.endturn_fun()
        ###
        #mouse and movement
        # If mouse button is held down update for continuous walking.
        if self.actual_team.player == 'human':
            if self.mouse_down:
                self.update_mouse_movement_path(pygame.mouse.get_pos())
            if self.mouse_down2:
                self.popup(pygame.mouse.get_pos())
            self.update_mouse_movement()
        #computer movements
        else:
            if(not self.avatar.movement):
                move_x,move_y = self.actual_team.move_hero(self.avatar,State.world,self.avatar_group,self.terrain_layer,self.collision_layer,self.objects_layer)
                print(move_x,move_y)
                self.update_computer_movement(move_x,move_y)
            if self.mouse_down2:
                self.popup(pygame.mouse.get_pos())
        ####### 
        #if self.key_down:
        #    self.update_keyboard_movement()     
        #update camera
        self.update_camera_position()
        State.camera.update()
        ####
        #animate actors
        self.anim_avatar()
        self.anim_creatures()
        ###
        #hud
        self.hud.update()
        ###
        #steps
        
    '''update mouse movement function
    it takes a step from a path if exists and is confirmed
    '''        
    def update_mouse_movement(self):

        #if already moving quit
        if(self.avatar.movement):
            return
        #
        #if path is not confirmed or even the path doesn't exist
        if(not self.path.confirmed):
            return
        if(not self.path.route):
            return
        #
        #taking step from path            
        self.move_to, self.step, cell_id, move_G, cell_type = self.path.getStepFromPath(self.world)
        #
        #if can't move
        if self.avatar.remaining_movement < move_G:
            self.path.retStepToPath(cell_id,move_G,cell_type)
            self.move_to = None
            self.move_to_G = 0
        self.move_x = self.step[0]
        self.move_y = self.step[1]
        self.move_to_G = move_G
        #debug
        #print('avatar position: (',State.camera.position[0],',',State.camera.position[1],')   and moving to: ',self.move_to)
        #ok
        return
        
    '''update mouse movement path function
    it takes mouse position and:
    if click in new destination we get a new path
    if click in same destination we confirm path
    '''
    def update_mouse_movement_path(self, pos):

        if(not utils.is_screen_pos_inside_map(pos)):
           return

        #in which cell are we clicking?
        world_pos = State.camera.screen_to_world(pos)
        cell = self.world.index_at(world_pos[0],world_pos[1])
        #1 case:if we have no destination, or destination is different to previous destination we prepare the path to the cell of coordinates given by mouse click!
        if (cell != self.final_cell_id):
           if not self.move_to:
              camera = State.camera
              orig_pos = camera.target.position
           else:
              orig_pos = self.move_to
           self.path.confirmed = False
           self.final_cell_id = self.path.pos2steps(orig_pos,world_pos,self.world,self.terrain_layer,self.collision_layer,self.avatar_group)
        #2 if we already have a destination
        else:
           #if clicked the same destination again
           #movement starts!!
           if(not self.avatar.movement):
              self.path.confirmed = True
        
    #keyboard movement between cells
    def update_keyboard_movement(self):
        # Gummchange
        if self.move_x == 0 and self.move_y == 0:
            return
        # print('CALCULATING MOVE_TO')
        # end Gummchange
        #if we are moving, interrupt!
        ############################
        # Current position.
        camera = State.camera
        wx, wy = camera.target.position
        cell_id = self.world.index_at(wx,wy)
        x,y =self.world.get_cell_pos(cell_id)
        camera.target.position = y+self.cell_size/2,x+self.cell_size/2
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
           #row,col = self.world.get_cell_grid(cell_id)
           self.new_x += self.cell_size/2
           self.new_y += self.cell_size/2
                   
           #gummchange
           self.move_to = Vec2d(self.new_x, self.new_y)
           self.step = Vec2d(self.move_x, self.move_y)
           #print("to position: ",self.new_x,self.new_y," inside the cell: ",cell_id," row and col: ",row,col)
           

    #keyboard movement between cells
    def update_computer_movement(self,move_x,move_y):
        # Gummchange
        if move_x == 0 and move_y == 0:
            return
        # print('CALCULATING MOVE_TO')
        # end Gummchange
        #if we are moving, interrupt!
        ############################
        # Current position.
        camera = State.camera
        wx, wy = camera.target.position
        cell_id = self.world.get_cell_id(wx,wy)
        x,y =self.world.get_cell_pos(cell_id)
        camera.target.position = y+self.cell_size/2,x+self.cell_size/2
        col = cell_id[0]
        row = cell_id[1]
        #print("actual position: ",wx,wy," inside the cell: ",cell_id," row and col: ",row,col) 
        #new situation of new cell
        if(row == 0 and move_y < 0):
           new_row = row
        else:
           new_row = row + move_y
        if(col == 0 and move_x < 0):
           new_col = col
        else:
           new_col = col + move_x
        #does it exist?
        cell_id = self.world.get_cell_id(int((new_col*self.cell_size)-1),int((new_row*self.cell_size)-1))
        self.new_x,self.new_y = self.world.get_cell_pos(cell_id)
        #collisions
        if(self.collision_layer.get_objects_in_rect(pygame.Rect(self.new_x,self.new_y,self.cell_size,self.cell_size))):
          self.new_x = 0
          self.new_y = 0
          return;
        self.new_x += self.cell_size/2
        self.new_y += self.cell_size/2
        #movement cost
        col = cell_id[0]
        row = cell_id[1]
        self.pc_mov_cost = path_finding.terrain_costs[self.terrain_layer.layer.content2D[row][col]]
        #print(self.avatar.remaining_movement,self.pc_mov_cost)
        self.avatar.remaining_movement -= self.pc_mov_cost
        #print(self.avatar.remaining_movement)
           
        #gummchange
        self.move_to = Vec2d(self.new_x, self.new_y)
        self.step = Vec2d(move_x, move_y)
        #print("to position: ",self.new_x,self.new_y," inside the cell: ",cell_id," row and col: ",row,col)

    def update_camera_position(self):
        ##debug
        #print('moving: ',self.move_to,'   , step: ',self.step)
        #
        # if move_to, then the camera needs to keep stepping towards the destination tile.
        if self.move_to:
            #print('STEP pos{} -> dest{} by step{}'.format(
            #    tuple(self.camera.position), tuple(self.move_to), tuple(self.step)))
            camx, camy = self.camera.position
            #print('current camera position: ',camx,camy)
            stepx, stepy = self.step
            #pay attention, if we are in a mouse movement we take next step
            # Check if camx has arrived at the move_to point. If it has set stepx to 0.
            if camx == self.move_to[0]:
                stepx = 0
            # Check if camy has arrived at the move_to point. If it has set stepy to 0.
            if camy == self.move_to[1]:
                stepy = 0
            # If steps remain on the x or y axis, update the camera position. Else, the
            # camera/avatar is done moving, so set self.move_to = None.
            if stepx or stepy:
                self.camera.position += stepx, stepy
                self.laststepx = stepx
                self.laststepy = stepy
                #avatar animation
                #print('avatar animation!')
                self.avatar.move(Vec2d(stepx,stepy))
                self.gameSounds.playsound('move')
            else:
                print("stop moving {},{}".format(int(self.laststepx),int(self.laststepy)))
                self.move_to = None
                #avatar animation
                self.avatar.stopMove(Vec2d(self.laststepx,self.laststepy))
                self.pc_mov_cost = 0
                self.avatar.remaining_movement -= self.move_to_G
                self.move_to_G = 0
                
        
    def draw(self, interp):
        """overrides Engine.draw"""
        # Draw stuff.
        State.screen.clear()
        self.draw_renderer()
        if False:
           self.draw_debug()
        self.draw_steps()
        self.draw_interface()
        # Draw the hud.
        self.hud.draw(State.screen.surface)
        State.screen.flip()

    def draw_interface(self):
       #buttons
       #for b in self.objects:
       #   b.draw(self.sidebar_screen)
       self.interface.draw(State.screen,self.avatar_group)
       self.buttEndTurn.draw(State.screen)
    def draw_renderer(self):
        """renderer draws map layers"""
        
        renderer = self.renderer
        
        # If panning, mark the renderer's tiles dirty where avatar is.
        panning = False
        camera = State.camera
        camera_rect = camera.rect
        dirty_rect = self.dirty_rect
        camera_center = camera_rect.center
        #changed this to have the renderer refreshing all the camera surface ALWAYS
        # TO HAVE animated objects always
        #set dirty to refresh all objects in camera rectangle
        dirty_rect.center = camera_center
        renderer.set_dirty(camera_rect)
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
        
        if(not self.path.route):
          return;
    
        camera = State.camera
        total_movement = self.avatar.remaining_movement
        for element in self.path.route:
           y,x  = self.world.get_cell_pos(element[0])
           x += self.cell_size/2
           y += self.cell_size/2
           if(total_movement >= element[1]):
               if(element[2] == 2):
                  sprite = "new-battle2.png"
               else:
                  sprite = "dot-white.png"  
               arrow = objects.arrow_step(sprite,"misc",(x,y))
               total_movement -= element[1]
           else:
               if(element[2] == 2):
                  sprite = "new-battle.png"
               else:
                  sprite = "new-journey.png"
               arrow = objects.arrow_step(sprite,"misc",(x,y))
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
        #others avatars in others teams
        for teams in self.factions.team:
           for avatars in teams.heroes:
              avatars.update()
              self.avatar_group.add(avatars)

        self.avatar.update()
        self.avatar_group.add(self.avatar)

    def anim_creatures(self):
        #self.avatar.update()
        #camera = State.camera
        #avatar = camera.target
        #others avatars in others teams
        for group in self.creatures.group:
           print('movement creature:',group.creature.movement)
           if(not group.creature.movement):
               i = random.randint(1, 50)
               print('random:',i)
               if(i == 1):
                   print('animating creature!')
                   group.creature.move()
           group.creature.update()
           self.avatar_group.add(group.creature)
        
    def on_mouse_button_down(self,event, pos, button):
       if(button == 1): 
          if 'click' in self.buttEndTurn.handleEvent(event):
             return 
          if(pos[0] <= 833 and pos[1] <= 741 and pos[1] >= 27): #to improve, if we are clicking on map
             self.mouse_down = True
             self.interface.erasehpopup()
             #print(pos)
       else:
          self.mouse_down2 = True
        
    def on_mouse_button_up(self,event, pos, button):
        if(button == 1):
           if 'click' in self.buttEndTurn.handleEvent(event):
             self.endturn = True   
           self.mouse_down = False
        else:
           self.mouse_down2 = False

    def on_mouse_motion(self,event, pos,rel, button):
        return
        
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
            self.avatar.setStrength(self.avatar.strength+1)
        if key == K_SPACE:
            self.endturn = True
        if key == K_ESCAPE:
            self.gameSounds.playworld(False,0.6)
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
    #we need to override original fucntion from parent class, to take also the event
    def _get_events(self):
        """Get events and call the handler. Called automatically by run() each
        time the clock indicates an update cycle is ready.
        """
        for e in self._get_pygame_events():
            typ = e.type
            if typ == KEYDOWN:
                #removed e.str python3 doesn't like it
		#by gentooza 2015-04-14
                self.on_key_down(e.unicode,e.key, e.mod)
            elif typ == KEYUP:
                self.on_key_up(e.key, e.mod)
            elif typ == MOUSEMOTION:
                self.on_mouse_motion(e,e.pos, e.rel, e.buttons)
            elif typ == MOUSEBUTTONUP:
                self.on_mouse_button_up(e,e.pos, e.button)
            elif typ == MOUSEBUTTONDOWN:
                self.on_mouse_button_down(e,e.pos, e.button)
            elif typ == JOYAXISMOTION:
                self.on_joy_axis_motion(e.joy, e.axis, e.value)
            elif typ == JOYBALLMOTION:
                self.on_joy_ball_motion(e.joy, e.ball, e.rel)
            elif typ == JOYHATMOTION:
                self.on_joy_hat_motion(e.joy, e.hat, e.value)
            elif typ == JOYBUTTONUP:
                self.on_joy_button_up(e.joy, e.button)
            elif typ == JOYBUTTONDOWN:
                self.on_joy_button_down(e.joy, e.button)
            elif typ == VIDEORESIZE:
                self.on_video_resize(e.size, e.w, e.h)
            elif typ == VIDEOEXPOSE:
                self.on_video_expose()
            elif typ == USEREVENT:
                    self.on_user_event(e)
            elif typ == QUIT:
                    self.on_quit()
            elif typ == ACTIVEEVENT:
                self.on_active_event(e.gain, e.state)


#####GAME DYNAMICS
    def cleanMovement(self):
        self.pathstep = None
        self.laststeppath = None 
        self.cellstep = None
        self.lastcellstep = None
        self.lastcellG = 0
        self.cellG = 0
        self.final_cell_id = None

    def endturn_fun(self):

        #print('endturn function!')
        #path saving
        self.cleanMovement()
        self.avatar.saved_path = self.path

        ############
        self.actual_team.heroes.append(self.avatar)     
        self.factions.team.append(self.actual_team)

        self.actual_team = None
        self.avatar = None
        self.actual_team = self.factions.team.pop(0)
        self.avatar = self.actual_team.heroes.pop(0)
        #refreshing avatar movement points
        self.avatar.remaining_movement = self.avatar.move_points
 
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
           self.path = self.avatar.saved_path

        self.move_to = None
        self.step = Vec2d(0,0)
        self.camera.target = self.avatar
        self.endturn = False



#####INTERFACE
    def populating_interface(self):
        #buttons position depends of game resolution
        self.buttEndTurn  = pygbutton.PygButton((870, 720, 120, 30), 'End Turn')

        #self.buttons = (self.buttEndTurn,..);
        #for b in self.buttons:
        #   b.bgcolor = WHITE
        #   b.fgcolor = RED
        self.buttEndTurn.bgcolor = WHITE
        self.buttEndTurn.fgcolor = RED

    def popup(self,pos):
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




