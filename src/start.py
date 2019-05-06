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
