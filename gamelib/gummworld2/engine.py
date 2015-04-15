#!/usr/bin/env python

# This file is part of Gummworld2.
#
# Gummworld2 is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Gummworld2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Gummworld2.  If not, see <http://www.gnu.org/licenses/>.

# Compatible: Python 2.7, Python 3.2


"""engine.py - A sample engine for Gummworld2.

This module provides an Engine class that can be subclassed for an application
framework that's easy to use.

The run loop keeps time via the game clock. update() and event handlers are
called every time an update cycle is ready. draw() is called every time a frame
cycle is ready.

The subclass should override update() and draw() for its own purposes. If the
subclass wants to get events for a particular type, all it needs to do is
override the event handler for that type.

If you want to write your own framework instead of using this one, then in
general you will still want to initialize yours in the same order as this class,
though not everything created in the constructor is required. See
Engine.__init__(), Engine.run(), and examples/00_minimum.py for helpful clues.
"""

__version__ = '$Id: engine.py 407 2013-08-12 15:11:30Z stabbingfinger@gmail.com $'
__author__ = 'Gummbum, (c) 2011-2014'


__all__ = ['NO_WORLD', 'SIMPLE_WORLD', 'Engine', 'run']


import pygame
from pygame.locals import *

if __name__ == '__main__':
    from . import paths

from gummworld2 import (
    State, Context, Screen, View, BasicMap, Camera, GameClock,
    context, model, pygame_utils,
)


NO_WORLD = 0
SIMPLE_WORLD = 1


class Engine(Context):
    
    NO_WORLD = NO_WORLD
    SIMPLE_WORLD = SIMPLE_WORLD
    
    def __init__(self, screen_surface=None, resolution=None, display_flags=0, caption=None, camera_target=None,
                 camera_view=None, camera_view_rect=None, map=None, tile_size=None, map_size=None, update_speed=30,
                 frame_speed=30, world_type=NO_WORLD, set_state=True):
        """Construct an instance of Engine.
        
        This constructor does the following:
            
            The pygame display is initialized with an optional caption, and the
            resulting screen.Screen object is placed in State.screen.
            
            An empty map.BasicMap object is created and placed in State.map.
            
            An empty model.World* object is created and placed in State.world.
            
            State.world_type is set to one of the engine.*_WORLD values
            corresponding to the world object in State.world.
            
            A camera.Camera object is created and placed in State.camera. The
            camera target is either taken from the camera_target argument, or an
            appropriate target for world type is created. The target is *NOT*
            added to the world, as the target does not need to be an object
            subject to game rules. If target happens to be an avatar-type object
            then add it manually to world with the rest of the world entities.
            
            A game_clock.GameClock object is created and placed in State.clock.
            
            Joystick objects are created for connected controllers.
        
        The following arguments are used to initialize a Screen object:
            
            The screen_surface argument specifies the pygame top level surface
            to use for creating the State.screen object. The presence of this
            argument overrides initialization of the pygame display, and
            resolution and display_flags arguments are ignored. Use this if
            the pygame display has already been initialized in the calling
            program.
            
            The resolution argument specifies the width and height of the
            display.
            
            The display_flags argument specifies the pygame display flags to
            pass to the display initializer.
            
            The caption argument is a string to use as the window caption.
        
        The following arguments are used to initialize a Camera object:
            
            The camera_target argument is the target that the camera will track.
            If camera_target is None, Engine will create a default target
            appropriate for the world type.
            
            The camera_view argument is a screen.View object to use as the
            camera's view.
            
            The camera_view_rect argument specifies the pygame Rect from which
            to create a screen.View object for the camera's view.
            State.screen.surface is used as the source surface. This argument is
            ignored if camera_view is not None.
        
        The following arguments are used to initialize a BasicMap object:
            
            The tile_size and map_size arguments specify the width and height of
            a map tile, and width and height of a map in tiles, respectively.
        
        The following arguments are used to initialize a model.World* object:
            
            The world_type argument specifies which of the world classes to
            create. It must be one of engine.NO_WORLD, or engine.SIMPLE_WORLD.
            
        The following arguments are used to initialize a Clock object:
            
            update_speed specifies the maximum updates that can occur per
            second.
            
            frame_speed specifies the maximum frames that can occur per second.
        
        The clock sacrifices frames per second in order to achieve the desired
        updates per second. If frame_speed is 0 the frame rate is uncapped.
        
        Engine.update() and Engine.draw() are registered as callbacks in the
        clock.
        """
        
        if __debug__:
            print('Engine: -- new engine --')
        
        Context.__init__(self)
        
        ## If you don't use this engine, then in general you will still want
        ## to initialize your State objects in the same order you see here.
        
        self.world_type = world_type
        self.screen = None
        self.caption = caption
        self.map = None
        self.world = None
        self.camera = None
        self.camera_target = camera_target
        self.clock = None
        
        ## Screen.
        if screen_surface:
            if __debug__:
                print('Engine: Screen(surface=screen_surface)')
            self.screen = Screen(surface=screen_surface)
        elif resolution:
            if __debug__:
                print('Engine: Screen(resolution, display_flags)')
            self.screen = Screen(resolution, display_flags)
        elif State.screen:
            if __debug__:
                print('Engine: using State.screen')
                self.screen = State.screen
        else:
            if __debug__:
                print('Engine: falling back on pygame.display.get_surface()')
            self.screen = Screen(surface=pygame.display.get_surface())
        
        ## BasicMap.
        if map:
            if __debug__:
                print('Engine: using pre-made map')
            self.map = map
        elif tile_size and map_size:
            if __debug__:
                print('Engine: BasicMap(map_size, tile_size)')
            self.map = BasicMap(map_size[0], map_size[1], tile_size[0], tile_size[1])
        else:
            if __debug__:
                print(('Engine: SKIPPING map creation:' +
                      ' no map, tile_size, or map_size'))
        
        ## If you want to use the camera target as a world entity, you have to
        ## use the right object type. Type checking and exception handling are
        ## not done. This is to allow flexible initialization of the Engine
        ## context.
        if __debug__ and self.camera_target:
            print('Engine: using pre-made camera target')
        if not self.map:
            if __debug__:
                print('Engine: SKIPPING world creation: no map')
            pass
        elif world_type == NO_WORLD:
            if __debug__:
                print('Engine: NoWorld(self.map.rect)')
            self.world = model.NoWorld(self.map.rect)
            if camera_target is None:
                if __debug__:
                    print('Engine: making camera target Object()')
                self.camera_target = model.Object()
        elif world_type == SIMPLE_WORLD:
            if __debug__:
                print('Engine: World(self.map.rect)')
            self.world = model.World(self.map.rect)
            if camera_target is None:
                if __debug__:
                    print('Engine: making camera target Object()')
                self.camera_target = model.Object()
        
        ## Create the camera.
        if any((self.camera_target, camera_view, camera_view_rect)):
            if camera_view:
                if __debug__:
                    print('Engine: using pre-made camera view')
            else:
                if camera_view_rect:
                    if __debug__:
                        print('Engine: making camera view from rect')
                    camera_view = View((self.screen or State.screen).surface, camera_view_rect)
                else:
                    if __debug__:
                        print('Engine: making camera view from screen')
                    camera_view = self.screen
            if __debug__:
                print('Engine: making camera')
            self.camera = Camera(self.camera_target, camera_view)
        else:
            if __debug__:
                print(('Engine: SKIPPING camera creation:' +
                      ' no camera target, view, or view rect'))
        
        ## Create the clock, specifying callbacks for update() and draw().
        if __debug__:
            print('Engine: creating GameClock')
        self.clock = GameClock(
            update_speed, frame_speed,
            update_callback=self._update, frame_callback=self._draw)
        
        ## Init joysticks.
        if not pygame.joystick.get_init():
            if __debug__:
                print('Engine: initializing joysticks')
            self._joysticks = pygame_utils.init_joystick()
        self._get_pygame_events = pygame.event.get
        
        ## Initialize State.
        if set_state:
            if __debug__:
                print('Engine: copying my objects to State')
            self.set_state()
 
    def enter(self):
        """Called when the context is entered.
        
        If you override this, make sure you call the super.
        """
        self.set_state()
    
    def resume(self):
        """Called when the context is resumed.
        
        If you override this, make sure you call the super.
        """
        self.set_state()
    
    def set_state(self):
        if self.world_type is not None:
            State.world_type = self.world_type
        if self.screen is not None:
            State.screen = self.screen
        if self.caption is not None:
            pygame.display.set_caption(self.caption)
        if self.map is not None:
            State.map = self.map
        if self.world is not None:
            State.world = self.world
        if self.camera is not None:
            State.camera = self.camera
        if self.camera_target is not None:
            State.camera_target = self.camera_target
        if self.clock is not None:
            State.clock = self.clock
    
    def _update(self, dt):
        """The clock's update_callback, which in turn calls
        Engine._get_events and Engine.update.
        """
        self._get_events()
        self.update(dt)
    
    def _draw(self, interp):
        """The clock's draw_callback, which in turn calls
        Camera.interpolate and Engine.draw.
        """
        if State.camera:
            State.camera.interpolate()
        self.draw(interp)
    
    def update(self, dt):
        """Override this method. Called by run() when the clock signals an
        update cycle is ready.
        
        Suggestion:
            move_camera()
            State.camera.update()
            ... custom update the rest of the game ...
        """
        pass
    
    def draw(self, interp):
        """Override this method. Called by run() when the clock signals a
        frame cycle is ready.
        
        Suggestion:
            State.screen.clear()
            ... custom draw the screen ...
            State.screen.flip()
        """
        pass
    
    @property
    def joysticks(self):
        """List of initialized joysticks.
        """
        return list(self._joysticks)
    
    def _get_events(self):
        """Get events and call the handler. Called automatically by run() each
        time the clock indicates an update cycle is ready.
        """
        for e in self._get_pygame_events():
            typ = e.type
            if typ == KEYDOWN:
                #removed e.str python3 doesn't like it
		#by gentooza 2015-04-14
                self.on_key_down(e.key, e.mod)
            elif typ == KEYUP:
                self.on_key_up(e.key, e.mod)
            elif typ == MOUSEMOTION:
                self.on_mouse_motion(e.pos, e.rel, e.buttons)
            elif typ == MOUSEBUTTONUP:
                self.on_mouse_button_up(e.pos, e.button)
            elif typ == MOUSEBUTTONDOWN:
                self.on_mouse_button_down(e.pos, e.button)
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
    
    ## Override an event handler to get specific events.
    def on_active_event(self, gain, state): pass
    def on_joy_axis_motion(self, joy, axis, value): pass
    def on_joy_ball_motion(self, joy, ball, rel): pass
    def on_joy_button_down(self, joy, button): pass
    def on_joy_button_up(self, joy, button): pass
    def on_joy_hat_motion(self, joy, hat, value): pass
    def on_key_down(self, key, mod): pass
    def on_key_up(self, key, mod): pass
    def on_mouse_button_down(self, pos, button): pass
    def on_mouse_button_up(self, pos, button): pass
    def on_mouse_motion(self, pos, rel, buttons): pass
    def on_quit(self): pass
    def on_user_event(self, e): pass
    def on_video_expose(self): pass
    def on_video_resize(self, size, w, h): pass


def run(app):
    """Push app onto the context stack and start the run loop.
    
    To exit the run loop gracefully, call context.pop().
    """
    context.push(app)
    while context.top():
        State.clock.tick()


if __name__ == '__main__':
    ## Multiple "apps", (aka engines, aka levels) and other settings
    from pygame.locals import *
    from gamelib import Vec2d, View, toolkit
    
    class App(Engine):

        def __init__(self, **kwargs):
            super(App, self).__init__(**kwargs)
            toolkit.make_tiles2()
            self.speed = 3
            self.movex = 0
            self.movey = 0

        def update(self):
            if self.movex or self.movey:
                State.camera.position += self.movex,self.movey
            State.camera.update()

        def draw(self):
            State.camera.interpolate()
            State.screen.surface.fill(Color('black'))
            toolkit.draw_tiles()
            if State.camera.view is not State.screen:
                pygame.draw.rect(State.screen.surface, (99,99,99),
                    State.camera.view.parent_rect, 1)
            pygame.display.flip()

        def on_key_down(self, str, key, mod):
            if key == K_DOWN:
                self.movey += self.speed
            elif key == K_UP:
                self.movey += -self.speed
            elif key == K_RIGHT:
                self.movex += self.speed
            elif key == K_LEFT:
                self.movex += -self.speed
            elif key == K_SPACE:
                State.running = False
            elif key == K_ESCAPE:
                quit()

        def on_key_up(self, key, mod):
            if key == K_DOWN:
                self.movey -= self.speed
            elif key == K_UP:
                self.movey -= -self.speed
            elif key == K_RIGHT:
                self.movex -= self.speed
            elif key == K_LEFT:
                self.movex -= -self.speed
    
    def make_app(num, **kwargs):
        name = 'app' + str(num)
        if name in state.states:
            State.restore(name)
            pygame.display.set_caption(State.caption + ' (restored)')
        else:
            State.app = App(**kwargs)
            if num % 2:
                toolkit.make_tiles()
            else:
                toolkit.make_tiles2()
            State.camera.position = State.camera.screen_center
            State.caption = kwargs['caption']
            State.save(name)
    
    def make_app1():
        screen = pygame.display.set_mode(resolution)
        make_app(1, screen_surface=screen, tile_size=tile_size, map_size=map_size, caption='1:Screen')
    
    def make_app2():
        tile_size = Vec2d(32, 32)
        view = View(State.screen.surface, Rect(16, 16, *(tile_size * 6)))
        make_app(2, tile_size=tile_size, map_size=map_size, camera_view=view, caption='2:View+Tilesize')
    
    def make_app3():
        make_app(3, tile_size=tile_size, map_size=map_size, camera_view_rect=Rect(16, 16, *(tile_size * 3)),
                 caption='3:Viewrect')
    
    tile_size = Vec2d(64, 64)
    map_size = Vec2d(10, 10)
    resolution = tile_size * 4
    
    State.default_attrs.extend(('app', 'caption'))
    app_num = 0
    
    while 1:
        app_num += 1
        if app_num > 3:
            app_num = 1
        if app_num == 1:
            make_app1()
        elif app_num == 2:
            make_app2()
        elif app_num == 3:
            make_app3()
        State.app.run()
