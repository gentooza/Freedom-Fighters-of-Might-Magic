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
    import os
    import sys
    import random
    import math
    import getopt
    import pygame
    import main_menu
    import game_engine
    import utils
    import sounds
    import paths
    import gummworld2
    from gummworld2 import Engine, State, BasicMap, SubPixelSurface, View, Vec2d
    from gummworld2 import context, model, spatialhash, toolkit, data
    from socket import *
    from pygame.locals import *
except ImportError as err:
    print("couldn't load module. %s" % (err))
    sys.exit(2)


class app:
    def __init__(self, parameters):
        # sound
        self.gameSounds = sounds.gameSound()
        self.gameSounds.loadTracks()
        pygame.init()
        if(parameters['resolution'] == 'NULL'):
            parameters['resolution'] = (1024, 768)
        if(parameters['strcaption'] == 'NULL'):
            parameters['strcaption'] = 'Freedom Fighters of Might & Magic'
        self.parameters = parameters

    def setDisplay(self):
        os.environ['SDL_VIDEO_FULLSCREEN_HEAD'] = '1'
        # self.screen =
        #     pygame.display.set_mode(self.resolution,pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode(self.parameters['resolution'])
        self.caption = pygame.display.set_caption(
                self.parameters['strcaption'])
        self.parameters['caption'] = self.caption

    def run(self):
        self.gameSounds.playmenu(True, 1.0)
        scr_menu = main_menu.main_menu(self.parameters)
        scr_menu.setScreen(self.screen, 30)
        scr_menu.constructScene()
        ret = 0
        while True:
            if(ret == 0):
                ret = scr_menu.run()
            if(ret == 1):
                self.gameSounds.playmenu(False, 1.0)
                print("LET'S PLAY FMM!!")
                scr_game = game_engine.gameEngine(
                        self.parameters, self.gameSounds)
                print('in game!!')
                gummworld2.run(scr_game)
                print('out of game!!')
                ret = 0
                self.gameSounds.playmenu(True, 1.0)
            else:
                self.gameSounds.playmenu(False, 1.0)
                print("EXITING FMM!!")
                pygame.quit()
                sys.exit()
