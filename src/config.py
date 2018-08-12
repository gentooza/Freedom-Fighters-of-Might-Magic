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

class Config_Manager:
    def __init__(self,config_file):
        try:
            myConfig_file = open(config_file,"r")
            self.load_parameters(myConfig_file)
            myConfig_file.close()
        except Exception as myError:
            print(myError)
            self.create_basic(config_file)
    
    def load_parameters(self,config_file):
        resolution = (1024,768)
        fullscreen = False
        for line in config_file:
            param_value = line.split('=')
            if(param_value[0] == "resolution"):
                coordinates = param_value[1].split('x')
                resolution = (int(coordinates[0]),int(coordinates[1]))
            if(param_value[0] == "fullscreen"):
                fullscreen = self.str2bool(param_value[1])
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
        
        txtResolution = "resolution=1024x768\n"
        myConfig_file.write(txtResolution)
        
        txtFullscreen = "fullscreen=False\n"
        myConfig_file.write(txtFullscreen)
        
        resolution = (1024,768)
        version = '0.0.6 ALPHA'
        strCaption = 'FFMM ' + version
        tile_size=(30, 30) 
        map_size=(100, 100)
        minimap_pos = (600,100)
        minimap_size = (120,120)
        FPS = 50
        NULL = 'NULL'

        self.parameters = {'resolution' : resolution,'strcaption' : strCaption,'caption' : NULL,'tile_size' : tile_size,'map_size' : map_size, 'minimap_pos' : minimap_pos, 'minimap_size' : minimap_size, 'FPS' : FPS, 'version' : version , 'fullscreen' : False }
        myConfig_file.close()
        
    def str2bool(self,v):
        return v.lower() in ("yes", "true", "t", "1")
        