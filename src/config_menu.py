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


import pygame, math, sys
import pygbutton
import utils

from pygame.locals import *


WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BACKGROUND = (20,20,20)

class config_menu:
    id=1
    def __init__(self,parameters):
        self.clock = pygame.time.Clock()
        #it depends of resolution
        self.image_background = utils.load_png('gui/main_menu.png')
        #it depends of resolution
        self.main_title = utils.load_png('gui/title.png')

        self.title_font = pygame.font.SysFont('verdana',22)
        self.title_font.set_bold(True)
        self.title = 'CONFIGURATION'
 
        self.option_font = pygame.font.SysFont('verdana',16)
        self.option_font.set_bold(True)
        self.option_video = 'VIDEO OPTIONS:'  

        self.parameters = parameters       
 
    def setScreen(self,screen,FPS):
        self.screen = screen
        self.FPS = FPS
        
    def constructScene(self):
        myResolution=self.parameters["resolution"]
        self.toggleFull = pygbutton.PygButton((60, 380, 200, 40), 'TOGGLE FULLSCREEN')
        self.buttQuit = pygbutton.PygButton((myResolution[0]-190, myResolution[1]-80, 150, 40), 'OK')
        
        self.objects = (self.toggleFull,self.buttQuit);
        for b in self.objects:
            b.bgcolor = WHITE
            b.fgcolor = RED

        self.title_str = self.title_font.render(self.title,True,(220,0,0))
        self.option_str = self.option_font.render(self.option_video,True,(220,0,0))
        
    def run(self):
        while True:
            for event in pygame.event.get(): # event handling loop
            #if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                
                #   pygame.quit()
                #  sys.exit()
                if 'click' in self.toggleFull.handleEvent(event):
                    if not self.parameters['fullscreen']:
                       self.parameters['fullscreen'] = True
                       pygame.display.toggle_fullscreen()
                    else:
                       self.parameters['fullscreen'] = False
                       pygame.display.toggle_fullscreen()
                if 'click' in self.buttQuit.handleEvent(event):
                    return 1
            #background theme
            self.screen.blit(self.image_background,(0,2))
            self.screen.blit(self.main_title,(175,0))
            self.screen.blit(self.title_str,(10,300))
            self.screen.blit(self.option_str,(30,350))
            #buttons
            for b in self.objects:
                b.draw(self.screen)

            pygame.display.update()
            self.clock.tick(self.FPS)
            
        


	

