#! /usr/bin/env python

'''
Copyright 2014-2018 by it's authors (see file AUTHORS)

This file is part of .Freedom Fighters of Might & Magic

Freedom Fighters of Might & Magic is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Freedom Fighters of Might & Magic is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Freedom Fighters of Might & Magic.  If not, see <https://www.gnu.org/licenses/>.
'''
import pygame
import subprocess


class Config_Manager:
    def __init__(self,config_file):
        try:
            myConfig_file = open(config_file,"r")
            self.load_parameters(myConfig_file)
            myConfig_file.close()
        except Exception as myError:
            print(myError)
            print("INFO: creating basic config.cfg")
            self.create_basic(config_file)
    
    def load_parameters(self,config_file):
        '''loading from text config file'''
        for line in config_file:
            param_value = line.split('=')
            if(param_value[0] == "resolution"):
                coordinates = param_value[1].split('x')
                cfg_resolution = (int(coordinates[0]),int(coordinates[1]))
            if(param_value[0] == "fullscreen"):
                cfg_fullscreen = self.str2bool(param_value[1])
        '''checking configurations not in config file'''
        try:
            resolution = cfg_resolution
        except:
            resolution = self.initResolution(config_file)
        try:
            fullscreen = cfg_fullscreen
        except:
            fullscreen = self.initFullscreen(config_file)
        '''------'''
        version = '0.0.6 ALPHA'
        strCaption = 'FFMM ' + version
        tile_size=(30, 30) 
        map_size=(100, 100)
        minimap_pos = (600,100)
        minimap_size = (120,120)
        FPS = 50
        NULL = 'NULL'

        self.parameters = {'resolution' : resolution,'strcaption' : strCaption,'caption' : NULL,'tile_size' : tile_size,'map_size' : map_size, 'minimap_pos' : minimap_pos, 'minimap_size' : minimap_size, 'FPS' : FPS, 'version' : version , 'fullscreen' : fullscreen }
        
            
    def create_basic(self,config_file):
        myConfig_file = open(config_file,"w")
        '''resolution'''
        resolution = self.initResolution(myConfig_file)
        '''fullscreen'''
        fullscreen = self.initFullscreen(myConfig_file)

        version = '0.0.6 ALPHA'
        strCaption = 'FFMM ' + version
        tile_size=(30, 30) 
        map_size=(100, 100)
        minimap_pos = (600,100)
        minimap_size = (120,120)
        FPS = 50
        NULL = 'NULL'

        self.parameters = {'resolution' : resolution,'strcaption' : strCaption,'caption' : NULL,'tile_size' : tile_size,'map_size' : map_size, 'minimap_pos' : minimap_pos, 'minimap_size' : minimap_size, 'FPS' : FPS, 'version' : version , 'fullscreen' : fullscreen }
        myConfig_file.close()
        
    def initResolution(self,config_file):
        res = subprocess.run("./src/tools/activescreen", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if(res.returncode == 0):
          wh = res.stdout.split(b' ')
          width = int(wh[0])
          height = int(wh[1])
        else:
          infoObject = pygame.display.Info()
          width = infoObject.current_w
          height = infoObject.current_h
        txtResolution = "resolution={}x{}\n".format(width,height)
        config_file.write(txtResolution)
        resolution = (width,height)
        
        return resolution
    
    def initFullscreen(self,config_file): 
        txtFullscreen = "fullscreen=False\n"
        config_file.write(txtFullscreen)
        
        return False

    '''tools'''
        
    def str2bool(self,v):
        return v.lower() in ("yes", "true", "t", "1")
        